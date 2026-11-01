import json
import re
import sys
import struct
import zlib

sys.stdout.reconfigure(encoding='utf-8')

MASTER_MAP_PATH = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\translations_master.json"
with open(MASTER_MAP_PATH, "r", encoding="utf-8") as f:
    tr = json.load(f)

ORIG_IDX = r"c:\PokeDinner-Eglantine-2.0.0\PPP ROM\updates\655360\romfs\LI_C0_R.IDX"
ORIG_BIN = r"c:\PokeDinner-Eglantine-2.0.0\PPP ROM\updates\655360\romfs\LD_C0_R.BIN"
with open(ORIG_IDX, "rb") as f: idx_data = f.read()
bin_f = open(ORIG_BIN, "rb")

def get_entry(idx):
    off, uncomp, block, flag = struct.unpack('<4Q', idx_data[idx*32:(idx+1)*32])
    bin_f.seek(off)
    hdr = bin_f.read(0x80)
    c_sz, n_c, tot = struct.unpack('<3I', hdr[:12])
    if c_sz != 65536 or n_c == 0 or n_c > 32: return None
    sizes = struct.unpack(f'<{n_c}I', hdr[12:12+n_c*4])
    curr = 0x80
    decomp = bytearray()
    for sz in sizes:
        bin_f.seek(off + curr)
        act_c = struct.unpack('<I', bin_f.read(4))[0]
        decomp += zlib.decompress(bin_f.read(act_c))
        curr += ((sz + 0x7f) // 0x80) * 0x80
    return decomp

all_pokes = set()
for e_idx in [2261, 4934]:
    decomp = get_entry(e_idx)
    count = struct.unpack('<I', decomp[:4])[0]
    for i in range(count):
        rel, flag = struct.unpack('<2I', decomp[0x40+i*8:0x48+i*8])
        if rel > 0 and 0x40+i*8+rel < len(decomp):
            addr = 0x40+i*8+rel
            s = decomp[addr:decomp.find(b'\x00', addr)].decode('utf-8', 'ignore').strip()
            base_s = re.sub(r'\s*\([^\)]*\)', '', s).strip()
            base_s = re.sub(r'\s+[A-E]$', '', base_s).strip()
            if base_s and len(base_s) > 2 and base_s not in ['All', 'Both', '???']:
                all_pokes.add(base_s)

all_pokes.update(['Pikachu', 'Charmander', 'Charizard', 'Squirtle', 'Bulbasaur', 'Ditto', 'Mew', 'Mewtwo', 'Eevee', 'Snorlax', 'Gengar'])

sorted_pokes = sorted(list(all_pokes), key=len, reverse=True)
combined_pattern = re.compile(r'\b(' + '|'.join(re.escape(p) for p in sorted_pokes) + r')\b')

missing = []
for en, pt in tr.items():
    pokes_in_en = set(combined_pattern.findall(en))
    for p in pokes_in_en:
        if not re.search(r'\b' + re.escape(p) + r'\b', pt, re.IGNORECASE):
            missing.append((p, en, pt))

with open(r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\missing_pokes.json", "w", encoding="utf-8") as f_out:
    json.dump(missing, f_out, ensure_ascii=False, indent=2)

print(f"Dumped {len(missing)} missing pokemon entries to missing_pokes.json")
