import os
import struct
import zlib
import json

ROM_DIR = r"c:\PokeDinner-Eglantine-2.0.0\PPP ROM"
IDX_PATH = os.path.join(ROM_DIR, r"updates\655360\romfs\LI_C0_R.IDX")
BIN_PATH = os.path.join(ROM_DIR, r"updates\655360\romfs\LD_C0_R.BIN")
OUTPUT_DIR = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\texts"
MANIFEST_PATH = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\manifest.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(IDX_PATH, "rb") as f_idx:
    idx_data = f_idx.read()

num_entries = len(idx_data) // 32
print(f"Lendo {num_entries} entradas de {IDX_PATH}...")

manifest = {
    "game": "Pokemon Pokopia",
    "title_id": "0400A3A01EE4C000",
    "version": "10.0.0 (655360)",
    "language": "pt_BR",
    "target_language_slot": "English",
    "total_files": 0,
    "total_strings": 0,
    "files": []
}

total_strings_count = 0
file_count = 0

with open(BIN_PATH, "rb") as f_bin:
    for i in range(num_entries):
        id_val, offset, size, flag = struct.unpack("<4Q", idx_data[i*32:(i+1)*32])
        if id_val == 0 and offset == 0:
            continue
        
        f_bin.seek(id_val + 0x80)
        c_hdr = f_bin.read(6)
        if len(c_hdr) == 6 and c_hdr[4:6] in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
            c_size = struct.unpack("<I", c_hdr[:4])[0]
            try:
                f_bin.seek(id_val + 0x84)
                decomp = zlib.decompress(f_bin.read(c_size))
                
                # Check for dialogue / text tags
                first_tag = decomp.find(b"<$")
                if first_tag == -1:
                    first_tag = decomp.find(b"<oneline>")
                
                if first_tag != -1:
                    raw_chunks = decomp[first_tag:].split(b"\x00")
                    valid_strings = []
                    for rs in raw_chunks:
                        if len(rs) >= 3:
                            try:
                                s = rs.decode('utf-8')
                                if any(c.isalpha() for c in s):
                                    valid_strings.append(s)
                            except:
                                pass
                    
                    if len(valid_strings) > 0:
                        sample = " ".join(valid_strings[:10])
                        # Detect if this is English slot
                        is_en = any(w in sample for w in [" the ", " you ", " to ", " and ", " is ", " I ", " in ", " of "])
                        if is_en:
                            file_count += 1
                            total_strings_count += len(valid_strings)
                            
                            filename = f"text_{i:05d}_{id_val:#010x}.json"
                            file_data = {
                                "entry_index": i,
                                "bin_id": hex(id_val),
                                "decompressed_size": len(decomp),
                                "first_tag_offset": first_tag,
                                "total_strings": len(valid_strings),
                                "dialogues": [
                                    {
                                        "id": s_idx,
                                        "en": s,
                                        "pt_br": ""
                                    }
                                    for s_idx, s in enumerate(valid_strings)
                                ]
                            }
                            
                            with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as out_f:
                                json.dump(file_data, out_f, ensure_ascii=False, indent=2)
                            
                            manifest["files"].append({
                                "entry_index": i,
                                "bin_id": hex(id_val),
                                "file_name": filename,
                                "string_count": len(valid_strings)
                            })
            except Exception as e:
                pass

manifest["total_files"] = file_count
manifest["total_strings"] = total_strings_count

with open(MANIFEST_PATH, "w", encoding="utf-8") as m_f:
    json.dump(manifest, m_f, ensure_ascii=False, indent=2)

print(f"\n[SUCESSO] Extração concluída!")
print(f"Total de arquivos JSON gerados: {file_count}")
print(f"Total de linhas/textos extraídos: {total_strings_count}")
print(f"Diretório de saída: {OUTPUT_DIR}")
print(f"Manifesto salvo em: {MANIFEST_PATH}")
