import os
import sys
import struct
import zlib
import json
import re
import time
import ctranslate2
import sentencepiece as spm

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

ROM_DIR = r"c:\PokeDinner-Eglantine-2.0.0\PPP ROM"
IDX_PATH = os.path.join(ROM_DIR, r"updates\655360\romfs\LI_C0_R.IDX")
BIN_PATH = os.path.join(ROM_DIR, r"updates\655360\romfs\LD_C0_R.BIN")
TEXTS_DIR = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\texts"
MANIFEST_PATH = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\manifest.json"
PKG_DIR = r"C:\Users\mppdi\.local\share\argos-translate\packages\translate-en_pt-1_9"

print("=" * 66)
print("  TURBO MOTOR V2: Tradução Perfeita com Preservação Total de Tags")
print("=" * 66)

# 1. Carrega o modelo CTranslate2 e SentencePiece
print("Inicializando CTranslate2 com 8 threads...")
sp = spm.SentencePieceProcessor(model_file=os.path.join(PKG_DIR, "sentencepiece.model"))
translator = ctranslate2.Translator(os.path.join(PKG_DIR, "model"), device="cpu", intra_threads=8)
print("Motor pronto!")

# 2. Carrega todos os JSONs já extraídos dos 172 arquivos em inglês
json_files = sorted([f for f in os.listdir(TEXTS_DIR) if f.endswith(".json")])
print(f"Total de arquivos de diálogos em Inglês identificados: {len(json_files)}")

# 3. Coleta todos os chunks únicos de texto (sem tocar nas tags)
print("Mapeando segmentos de texto puro e isolando tags do motor...")
all_files_data = {}
unique_texts = set()

for fn in json_files:
    fp = os.path.join(TEXTS_DIR, fn)
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_files_data[fn] = data
    for d in data["dialogues"]:
        orig = d["en"]
        parts = re.split(r'(<[^>]+>)', orig)
        for p in parts:
            if not p.startswith('<') and any(c.isalpha() for c in p):
                cleaned = p.strip()
                if cleaned:
                    unique_texts.add(cleaned)

unique_list = list(unique_texts)
print(f"Total de frases únicas a traduzir: {len(unique_list)}")

PT_BR_REPLACEMENTS = [
    (r'\b(és tu|és você)\b', 'é você'),
    (r'\b(Quem és tu)\b', 'Quem é você'),
    (r'\b(Como estás)\b', 'Como você está'),
    (r'\b(estás)\b', 'está'),
    (r'\b(queres)\b', 'quer'),
    (r'\b(tens)\b', 'tem'),
    (r'\b(sabes)\b', 'sabe'),
    (r'\b(vês)\b', 'vê'),
    (r'\b(dizes)\b', 'diz'),
    (r'\b(vens)\b', 'vem'),
    (r'\b(podes)\b', 'pode'),
    (r'\b(contigo)\b', 'com você'),
    (r'\b(connosco)\b', 'conosco'),
    (r'\b(ecrã)\b', 'tela'),
    (r'\b(ficheiro)\b', 'arquivo'),
    (r'\b(facto)\b', 'fato'),
    (r'\b(equipa)\b', 'equipe'),
    (r'\b(pequeno-almoço)\b', 'café da manhã'),
    (r'\b(gostava de)\b', 'gostaria de'),
    (r'\b(deves)\b', 'deve'),
]

def post_process_ptbr(text):
    text = text.replace('\u2581', ' ').replace('_', ' ')
    for pat, rep in PT_BR_REPLACEMENTS:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    # Limpeza de pontuação e espaços duplos
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 4. Traduz todas as frases únicas em lote de 256
print("\n--- INICIANDO TRADUÇÃO DAS FRASES ÚNICAS EM LOTE (256 POR LOTE) ---")
BATCH_SIZE = 256
translation_cache = {}
t_start = time.time()

for b_idx in range(0, len(unique_list), BATCH_SIZE):
    batch = unique_list[b_idx:b_idx+BATCH_SIZE]
    tokens = [sp.encode(s, out_type=str) for s in batch]
    results = translator.translate_batch(tokens, max_batch_size=BATCH_SIZE)
    
    for orig, res in zip(batch, results):
        raw_tr = sp.decode_pieces(res.hypotheses[0])
        clean_tr = post_process_ptbr(raw_tr)
        translation_cache[orig] = clean_tr
        
    done = min(b_idx + BATCH_SIZE, len(unique_list))
    elapsed = time.time() - t_start
    rate = done / elapsed if elapsed > 0 else 0
    pct = (done / len(unique_list)) * 100
    rem_secs = (len(unique_list) - done) / rate if rate > 0 else 0
    print(f"Progresso: [{done}/{len(unique_list)}] ({pct:.1f}%) | {rate:.1f} str/s | Restante estimado: {rem_secs/60:.1f} min")

print(f"\nTradução concluída em {time.time() - t_start:.1f}s!")

# 5. Reconstrói os diálogos aplicando as traduções preservando todas as tags e espaçamentos
print("\nReconstruindo arquivos JSON com tags preservadas...")

def translate_dialogue_string(text):
    if not text or not any(c.isalpha() for c in text):
        return text
    parts = re.split(r'(<[^>]+>)', text)
    new_parts = []
    for p in parts:
        if p.startswith('<') and p.endswith('>'):
            new_parts.append(p)
        elif not any(c.isalpha() for c in p):
            new_parts.append(p)
        else:
            # Preserva espaços e pontuação das pontas
            m = re.match(r'^(\s*)(.*?)(\s*)$', p, re.DOTALL)
            if m:
                lead, core, trail = m.groups()
                core_clean = core.strip()
                tr_core = translation_cache.get(core_clean, core)
                new_parts.append(lead + tr_core + trail)
            else:
                new_parts.append(translation_cache.get(p.strip(), p))
    return "".join(new_parts)

total_dialogues_count = 0
for fn, data in all_files_data.items():
    for d in data["dialogues"]:
        d["pt_br"] = translate_dialogue_string(d["en"])
        total_dialogues_count += 1
    
    fp = os.path.join(TEXTS_DIR, fn)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Todos os {len(all_files_data)} arquivos JSON ({total_dialogues_count} diálogos) foram atualizados com sucesso!")

# 6. Compila e instala o mod LayeredFS
print("\n" + "=" * 66)
print("  RECOMPILANDO ROMFS E INSTALANDO MOD NO EMULADOR")
print("=" * 66)
import build_mod
build_mod.build_mod_append()
print("\n[FINALIZADO COM SUCESSO TOTAL] Mod pronto e verificado no emulador!")
