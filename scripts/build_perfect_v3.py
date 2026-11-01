import os
import sys
import struct
import zlib
import json
import re
import time
import shutil

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

ROM_DIR = r"c:\PokeDinner-Eglantine-2.0.0\PPP ROM"
ORIG_IDX = os.path.join(ROM_DIR, r"updates\655360\romfs\LI_C0_R.IDX")
ORIG_BIN = os.path.join(ROM_DIR, r"updates\655360\romfs\LD_C0_R.BIN")
MASTER_MAP_PATH = r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\translations_master.json"
MOD_ROMFS_DIR = r"C:\Users\mppdi\AppData\Roaming\eden\load\0400A3A01EE4C000\Traducao_PTBR\romfs"
TARGET_IDX = os.path.join(MOD_ROMFS_DIR, "LI_C0_R.IDX")
TARGET_BIN = os.path.join(MOD_ROMFS_DIR, "LD_C0_R.BIN")

print("=" * 70)
print("  BUILDER MASTER V3.2 - POKÉMON POKOPIA (100% PT-BR + NOMES ORIGINAIS)")
print("=" * 70)

t_start = time.time()

# 1. Carregar mapa mestre de traduções
print("[1/5] Carregando mapa de traduções...")
with open(MASTER_MAP_PATH, "r", encoding="utf-8") as f:
    tr_map = json.load(f)

# Substituições exatas por índice de entrada para garantia absoluta
ENTRY_EXACT_OVERRIDES = {
    3305: {
        0: "Acorde e brilhe! Você certamente parece bem descansado!",
        1: "Hm? Você está procurando por algo?",
        2: "Oho! Uma <$cdef(27)>Pokédex</color>—e este modelo vem com uma câmera!",
        3: "Esta é a cidade onde você morava? É tão linda!",
        4: "Ah, que foto linda! É o seu Treinador fazendo carinho em você?<br>Você parece tão feliz!<clear><br>Você se lembra de como o seu Treinador era?",
        5: "Interessante! Então o seu Treinador era assim?",
        6: "Entendo... O que mais você pode me dizer sobre o seu Treinador?",
        7: "Uau! Você tem um talento natural para se <$cdef(27)>transformar</color>! Pronto para começar sua<br>aventura com o seu visual atual?",
        8: "Entendo... Você precisa de mais tempo para se lembrar de como o seu<br>Treinador era?",
        9: "Puxa vida... Parece que ALGUÉM precisa de mais um tempinho de sono!",
    },
    2324: {
        71: "Deseja começar com o idioma selecionado?",
        72: "O jogo precisa reiniciar para alterar as configurações de idioma.<br>Deseja reiniciar o jogo?",
        75: "Tem certeza de que deseja jogar em Português (Brasil)?",
        394: "Você está prestes a abrir a tela de <$cdef(27)>Configurações de Idioma</color>.<br>Deseja salvar suas alterações anteriores?",
    },
    2351: {
        4: "<$voicel(1,9)><$motionoff(1,804)><$comeff(1,5)><$facial(1,13)>Caramba! O que raios um humano está fazendo aqui?!<br><$voicel(1,5)><$comeff(1,21)><$motion(1,801)><$facial(1,5)>Pensei que não restasse mais nenhum!",
        5: "<$voicel(1,5)><$comeff(1,6)>Hm? Há algo curioso em você... <$voicel(1,2)>Você é<br>REALMENTE um humano?",
        6: "<$voicel(1,3)>Esses olhos simples... Essa boquinha boba... <$voicel(1,8)>Hrm?! Espere um<br>pouco...<clear><br><$voicel(1,9)>Você é um <$cdef(27)>Ditto</color>?! Puxa, que transformação impressionante!",
        7: "<$voicel(1,9)>Oho! Então você é um <$cdef(27)>Ditto</color>, hein? <$voicel(1,10)>Que transformação<br>impressionante!",
        10: "*beep-beep!*<clear><br><$cdef(27)>Proprietário</color> detectado. Iniciando bateria de backup.",
        13: "Você encontrou uma <$cdef(27)>Pokédex</color>! Ela vem até equipada com uma câmera<br>que pode tirar selfies!",
        14: "<$voicel(1,7)><$emotion(1,32)>Oho! Essa é uma <$cdef(27)>Pokédex</color> que encontrei há muito tempo!",
        15: "<$voicel(1,5)><$emotion(1,14)>É mesmo? Eu pensei que essa Pokédex não tivesse conserto,<br><$voicel(1,8)>mas ela começou a funcionar assim que você apareceu...",
        16: "<$voicel(1,7)><$facial(1,4)><$emotion(1,9)>Pode ficar com ela.<clear><br><$voicel(1,3)>Não faço a menor ideia de como usar essa coisa.",
        17: "<$voicel(1,5)><$emotion(1,9)>Sim, já estava em péssimo estado quando a encontrei.<clear><br><$voicel(1,7)><$emotion(1,13)>Pensei que essa engenhoca estivesse quebrada, mas voltou<br>a funcionar bem na hora em que você chegou...",
        18: "<$voicel(1,7)><$facial(1,4)><$emotion(1,9)>Pode ficar com essa Pokédex.<clear><br><$voicel(1,5)>Não faço a menor ideia de como usá-la.",
        19: "<$voicel(1,7)><$comeff(1,3)><$motion(1,803)>A sua transformação humana é realmente impressionante,<br>sabe?<clear><br><$voicel(1,5)><$emotion(1,38)>E agora que você está segurando uma Pokédex, parece até<br>um Treinador Pokémon!<clear><br><$voicel(1,3)><$comeff(1,6)><$facial(1,2)><$motion(1,666)>Será que você baseou essa sua aparência no seu<br>próprio Treinador?",
        20: "<$voicel(1,7)><$motion(1,801)><$comeff(1,10)><$facial(1,4)>Hohoho! Tenho certeza de que você e seu Treinador devem ter sido<br><$voicel(1,8)>parceiros esplêndidos.",
        21: "<$voicel(1,5)><$motion(1,827)><$facial(1,1)><$comeff(1,6)>A propósito, aquele Treinador te deu um nome?",
        28: "<$voicel(1,7)><$emotion(1,9)>Nesse caso, creio que também tomarei a liberdade de te chamar<br>de “<$cdef(27)><pname;0></color>.”",
        29: "<$voicel(1,9)><$emotion(1,1)>Entendo, entendo. <$voicel(1,6)>Tenho certeza de que você era um <$cdef(27)>Ditto<br></color>muito especial para o seu Treinador.",
        30: "<$voicel(1,7)><$emotion(1,23)>Nesse caso, creio que também tomarei a liberdade de te chamar<br>de <$cdef(27)><pname;0></color>.",
        33: "<$voicel(1,3)><$emotion(1,31)>Já faz um bom tempo desde a última vez que vi<br>um humano ou um Pokémon...<clear><br><$voicel(1,5)>E aí, do nada, me deparo com um Pokémon com<br>forma de humano! Que curioso.",
        34: "<$voicel(1,4)><$comeff(1,6)><$motion(1,827)>Hrm?<clear><br><$voicel(1,5)>Quer dizer que... você não sabe o que aconteceu por aqui?<br><$voicel(1,8)><$comeff(1,3)><$motion(1,839)>Muito bem, então. Venha comigo.",
        35: "<$voicel(1,1)>Este lugar já foi o lar de muitos humanos...<clear><br><$voicel(1,2)><$comeff(1,17)><$facial(1,9)><$motion(1,806)>Mas agora está... bem, como você pode ver.",
        36: "<$voicel(1,3)>A grama e as árvores estão secas e murchas. E todos os<br>humanos e Pokémon que viviam aqui... <wait(1.5)><$voicel(1,2)>se foram.",
        37: "<$voicel(1,3)>Mas a minha pergunta é: onde VOCÊ esteve durante todo esse—",
        38: "<$voicel(1,6)>Hm?!",
        39: "<$voicel(1,9)>O que é aquilo no chão ali na frente? Poderia ser<br>um Pokémon?!",
        43: "<$voicel(2,2)>Nnngh...<clear><br>Á... água...",
        44: "<$voicel(1,9)><$motion(1,803)><$comeff(1,5)>Nossa, não acredito! É um <$cdef(27)>Squirtle</color>! E ele está<br>quase todo ressecado!",
        45: "<$voicel(1,5)><$motion(1,827)>E eu achando que <$cdef(27)>Squirtle</color> tinha total domínio<br>sobre a água...",
        46: "<$voicel(1,4)><$motion(1,654)><$emotion(1,31)>Será que não podemos fazer nada para ajudar?!",
        47: "Você reparou no <$cdef(27)>balão de fala</color> que apareceu sobre a<br>cabeça do <$cdef(27)>Squirtle</color>?<clear><br>Quando um Pokémon quer dizer algo a você, um <$cdef(27)>balão<br>de fala</color> aparecerá acima dele.<clear><br>Parece que o <$cdef(27)>Squirtle</color> está com um problema bem sério...<br>tente falar com ele!",
        48: "<$voicel(2,2)>Nnngh...<clear><br>Á... água...",
        49: "<$voicel(1,3)><$comeff(1,7)><$motion(1,667)><$facial(1,9)>Será que há algo que possamos fazer para ajudar o <$cdef(27)>Squirtle</color>?",
        50: "Se um Pokémon parecer que quer dizer algo a você,<br>tente falar com ele!",
        51: "<$voicel(2,3)>Uggghhh... Que lugar é esse? Onde está... a água...",
        52: "<$voicel(2,1)>Rrrgh... Normalmente eu posso lançar quanta água eu quiser...",
        53: "<$voicel(2,3)>Ahhh... Se ao menos houvesse... outro Squirtle saudável por perto<br>para me ajudar...",
        55: "<$voicel(1,5)><$comeff(1,7)><$facial(1,9)>Devo dizer, já vi transformações melhores...<br><$facial(1,1)>mas parece que você consegue usar o movimento do <$cdef(27)>Squirtle</color>!",
        56: "<$voicel(1,7)><$motion(1,801)>Você consegue usar esse movimento para <$cdef(27)>salvar o Squirtle</color>?",
        57: "<$voicel(1,7)><$motion(1,801)>Você consegue usar esse movimento para <$cdef(27)>salvar o Squirtle</color>?",
        59: "<$voicel(1,9)><$facial(1,9)>Nossa vida! Por que você foi esguichar água<br>em MIM?!",
        60: "<$voicel(1,5)><$motion(1,824)>Não sou eu quem precisa de água. <$cdef(27)>Jogue no Squirtle,<br>pelo amor de Deus!</color>",
        64: "<$voicel(2,8)>Estou salvo!!!",
        65: "<$voicel(2,9)><$motion(2,801)><$facial(2,4)>Muito obrigado! Achei mesmo que tinha chegado ao meu fim!",
        66: "<$voicel(2,8)>Devo minha vida a você...",
        70: "<$voicel(2,9)><$emotion(2,1)>Obrigado de novo por me molhar! Isso realmente me salvou.",
        72: "<$voicel(2,7)><$motion(2,803)>Mas parece que o lugar se anima todo quando<br>você molha as coisas com <$cdef(27)><$sklfull(3)></color>!",
        74: "<$voicel(2,10)><$motionoff(2,804)><$facial(2,4)><$comeff(2,9)>Quem sabe você não possa <$cdef(27)>regar mais esta área para ajudar a grama a crescer</color>!"
    },
    5069: {
        202: "Á... água...",
        204: "Vá em frente — jogue água nele!"
    }
}

# Nos menus de idioma (4663 a 4671), a opção 1 é sempre 'English' -> 'Português (Brasil)'
for lang_idx in range(4663, 4672):
    ENTRY_EXACT_OVERRIDES.setdefault(lang_idx, {})[1] = "Português (Brasil)"

# Frases adicionais para o dicionário global
extra_dialogues = {
    "Wa...water...": "Á... água...",
    "<$voicel(2,2)>Nnngh...<clear><br>Wa...water...": "<$voicel(2,2)>Nnngh...<clear><br>Á... água...",
    "Rise and shine! You certainly look well rested!": "Acorde e brilhe! Você certamente parece bem descansado!",
    "Hm? Are you looking for something?": "Hm? Você está procurando por algo?",
    "Is this the town where you used to live? It’s so pretty!": "Esta é a cidade onde você morava? É tão linda!",
    "Are you sure you want to play in English?": "Tem certeza de que deseja jogar em Português (Brasil)?",
    "Which language will you play in?": "Em qual idioma você deseja jogar?",
    "Select the display language.": "Selecione o idioma de exibição.",
    "Language": "Idioma",
}
for k, v in extra_dialogues.items():
    tr_map[k] = v

print(f"Total de pares no mapa de tradução: {len(tr_map)}")

# 2. Ler o índice original e mapear os 368 arquivos do Slot 1 + menus de idiomas
print("[2/5] Lendo índice original e identificando arquivos a modificar...")
with open(ORIG_IDX, "rb") as f_idx:
    orig_idx_data = f_idx.read()

num_idx_entries = len(orig_idx_data) // 32
orig_bin_f = open(ORIG_BIN, "rb")

def read_full_entry(bin_f, bin_offset):
    bin_f.seek(bin_offset)
    hdr = bin_f.read(0x80)
    if len(hdr) < 0x80:
        return None, None
    chunk_size, num_chunks, total_uncomp = struct.unpack('<3I', hdr[:12])
    if chunk_size != 65536 or num_chunks == 0 or num_chunks > 32:
        return None, None
    c_sizes = struct.unpack(f'<{num_chunks}I', hdr[12:12+num_chunks*4])
    
    full_decomp = bytearray()
    curr_off = 0x80
    for c_sz in c_sizes:
        bin_f.seek(bin_offset + curr_off)
        act_c_bytes = bin_f.read(4)
        if len(act_c_bytes) < 4:
            return None, None
        act_c = struct.unpack('<I', act_c_bytes)[0]
        comp_data = bin_f.read(act_c)
        try:
            full_decomp += zlib.decompress(comp_data)
        except:
            return None, None
        curr_off += ((c_sz + 0x7f) // 0x80) * 0x80
        
    return hdr, full_decomp

# Extrair todos os nomes de Pokémon das tabelas originais 2261 e 4934 para proteção absoluta
all_pokes = set()
for e_idx in [2261, 4934]:
    orig_id_val, orig_uncomp, orig_block, orig_flag = struct.unpack('<4Q', orig_idx_data[e_idx*32:(e_idx+1)*32])
    _, decomp_p = read_full_entry(orig_bin_f, orig_id_val)
    if decomp_p:
        cnt = struct.unpack('<I', decomp_p[:4])[0]
        for i in range(cnt):
            rel, flag = struct.unpack('<2I', decomp_p[0x40+i*8:0x48+i*8])
            if rel > 0 and 0x40+i*8+rel < len(decomp_p):
                addr = 0x40+i*8+rel
                s_name = decomp_p[addr:decomp_p.find(b'\x00', addr)].decode('utf-8', 'ignore').strip()
                base_name = re.sub(r'\s*\([^\)]*\)', '', s_name).strip()
                base_name = re.sub(r'\s+[A-E]$', '', base_name).strip()
                if base_name and len(base_name) > 2 and base_name not in ['All', 'Both', '???']:
                    all_pokes.add(base_name)

all_pokes.update([
    'Pikachu', 'Raichu', 'Charmander', 'Charmeleon', 'Charizard',
    'Squirtle', 'Wartortle', 'Blastoise', 'Bulbasaur', 'Ivysaur', 'Venusaur',
    'Ditto', 'Mew', 'Mewtwo', 'Eevee', 'Vaporeon', 'Jolteon', 'Flareon',
    'Espeon', 'Umbreon', 'Leafeon', 'Glaceon', 'Sylveon',
    'Snorlax', 'Munchlax', 'Gengar', 'Gastly', 'Haunter', 'Scyther', 'Scizor',
    'Tangela', 'Tangrowth', 'Professor Tangrowth',
    'Tinkmaster', 'Tinkatink', 'Tinkatuff', 'Tinkaton',
    'Toxel', 'Toxtricity', 'Slowpoke', 'Slowbro', 'Slowking',
    'Oddish', 'Gloom', 'Vileplume', 'Bellossom',
    'Weezing', 'Koffing', 'Electrode', 'Voltorb',
    'Cinderace', 'Raboot', 'Scorbunny',
    'Happiny', 'Chansey', 'Blissey',
    'Empoleon', 'Prinplup', 'Piplup',
    'Duskull', 'Dusclops', 'Dusknoir',
    'Illumise', 'Volbeat', 'Sableye',
    'Conkeldurr', 'Gurdurr', 'Timburr',
    'Persian', 'Meowth', 'Torchic', 'Combusken', 'Blaziken',
    'Ampharos', 'Flaaffy', 'Mareep',
    'Arbok', 'Ekans', 'Frillish', 'Jellicent',
    'Greedent', 'Skwovet', 'Lampent', 'Litwick', 'Chandelure',
    'Mr. Mime', 'Mime Jr.', 'Whiscash', 'Barboach',
    'Applin', 'Flapple', 'Appletun', 'Dipplin', 'Hydrapple',
    'Chewtle', 'Drednaw', 'Rowlet', 'Dartrix', 'Decidueye',
    'Fidough', 'Dachsbun', 'Milotic', 'Feebas',
    'Floatzel', 'Buizel', 'Starmie', 'Staryu',
    'Primarina', 'Brionne', 'Popplio',
    'Swampert', 'Marshtomp', 'Mudkip',
    'Jumpluff', 'Skiploom', 'Hoppip',
    'Typhlosion', 'Quilava', 'Cyndaquil',
    'Tyranitar', 'Pupitar', 'Larvitar',
    'Vespiquen', 'Combee', 'Volcanion',
    'Coalossal', 'Carkol', 'Rolycoly',
    'Ninetales', 'Vulpix', 'Cacturne', 'Cacnea',
    'Excadrill', 'Drilbur', 'Totodile', 'Croconaw', 'Feraligatr',
    'Porygon', 'Porygon2', 'Porygon-Z',
    'Corphish', 'Crawdaunt', 'Cinccino', 'Minccino',
    'Horsea', 'Seadra', 'Kingdra', 'Aurorus', 'Amaura',
    'Tyrantrum', 'Tyrunt', 'Victreebel', 'Weepinbell', 'Bellsprout',
    'Bruxish', 'Golisopod', 'Wimpod', 'Pumpkaboo', 'Gourgeist',
    'Peakychu', 'Mosslax', 'DJ Rotom', 'Chef Dente', 'Smearguru'
])

print(f"Lista de proteção de Pokémon: {len(all_pokes)} espécies registradas.")

# Conjunto de entradas a reconstruir:
# 1. Todas as entradas com passo 9 de 1910 a 5213 (todos os 368 arquivos de texto do Slot 1)
# 2. Entradas 4663 a 4671 (menu de seleção de idiomas)
target_entry_indices = set()
for i in range(1910, 5214):
    if (i - 1910) % 9 == 0:
        target_entry_indices.add(i)

for i in range(4663, 4672):
    target_entry_indices.add(i)

print(f"Total de entradas selecionadas para reconstrução precisa: {len(target_entry_indices)}")

# 3. Preparar contêiner base limpo
print("[3/5] Restaurando contêiner base limpo na pasta do emulador...")
os.makedirs(MOD_ROMFS_DIR, exist_ok=True)
shutil.copyfile(ORIG_BIN, TARGET_BIN)
shutil.copyfile(ORIG_IDX, TARGET_IDX)

with open(TARGET_IDX, "rb") as f_idx:
    mod_idx_data = bytearray(f_idx.read())

def translate_full_string(text, is_lang_menu=False):
    if is_lang_menu:
        if text == "English":
            return "Português (Brasil)"
        return text
    if text.strip() in all_pokes:
        return text  # Mantém o nome exato original do Pokémon!
    if text in tr_map:
        return tr_map[text]
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
            m = re.match(r'^(\s*)(.*?)(\s*)$', p, re.DOTALL)
            if m:
                lead, core, trail = m.groups()
                core_clean = core.strip()
                if core_clean in all_pokes:
                    tr_core = core_clean  # Nome de Pokémon protegido
                else:
                    tr_core = tr_map.get(core_clean, core)
                new_parts.append(lead + tr_core + trail)
            else:
                p_clean = p.strip()
                if p_clean in all_pokes:
                    tr_p = p_clean
                else:
                    tr_p = tr_map.get(p_clean, p)
                new_parts.append(tr_p)
    return "".join(new_parts)

# 4. Reconstruir e injetar cada entrada
print("[4/5] Reconstruindo tabelas com ponteiros relativos matematicamente exatos...")
total_strings_modified = 0

with open(TARGET_BIN, "r+b") as target_bin_f:
    target_bin_f.seek(0, os.SEEK_END)
    
    for counter, entry_idx in enumerate(sorted(target_entry_indices)):
        orig_id_val, orig_uncomp, orig_block, orig_flag = struct.unpack('<4Q', mod_idx_data[entry_idx*32:(entry_idx+1)*32])
        if orig_id_val == 0 or orig_block == 0:
            continue
            
        hdr, full_decomp = read_full_entry(orig_bin_f, orig_id_val)
        if not full_decomp or len(full_decomp) < 0x48:
            continue
            
        count, val2 = struct.unpack('<2I', full_decomp[:8])
        if count == 0 or len(full_decomp) < 0x40 + count * 8:
            continue
            
        is_lang_menu = (4663 <= entry_idx <= 4671)
        is_poke_table = (entry_idx in (2261, 4934))
        
        # Mapeia todas as entradas originais
        file_strings = []
        for ei in range(count):
            e_addr = 0x40 + ei * 8
            rel_off, flag = struct.unpack('<2I', full_decomp[e_addr : e_addr + 8])
            if rel_off > 0 and (e_addr + rel_off) < len(full_decomp):
                t_addr = e_addr + rel_off
                end = full_decomp.find(b'\x00', t_addr)
                s = full_decomp[t_addr:end].decode('utf-8', 'ignore')
                file_strings.append((ei, s, flag))
            else:
                file_strings.append((ei, '', flag))
                
        # Constrói novo buffer com cabeçalho idêntico
        table_size = 0x40 + count * 8
        new_decomp = bytearray(full_decomp[:table_size])
        pad_size = (16 - (table_size % 16)) % 16
        new_decomp += b'\x00' * pad_size
        
        # Insere as strings traduzidas e recalcula os ponteiros relativos
        string_cache = {}
        for ei, orig_s, flag in file_strings:
            e_addr = 0x40 + ei * 8
            if not orig_s and flag == 0:
                new_s = ''
            elif is_poke_table:
                # Nas listas de espécies 2261 e 4934, mantemos os nomes de Pokémon 100% originais!
                if orig_s == 'All':
                    new_s = 'Todos'
                elif orig_s == 'Both':
                    new_s = 'Ambos'
                else:
                    new_s = orig_s  # Nome original oficial sem alteração!
                if new_s != orig_s:
                    total_strings_modified += 1
            elif entry_idx in ENTRY_EXACT_OVERRIDES and ei in ENTRY_EXACT_OVERRIDES[entry_idx]:
                new_s = ENTRY_EXACT_OVERRIDES[entry_idx][ei]
                if new_s != orig_s:
                    total_strings_modified += 1
            else:
                new_s = translate_full_string(orig_s, is_lang_menu)
                if new_s != orig_s:
                    total_strings_modified += 1
                
            if new_s not in string_cache:
                target_pos = len(new_decomp)
                new_decomp += new_s.encode('utf-8') + b'\x00'
                string_cache[new_s] = target_pos
            else:
                target_pos = string_cache[new_s]
                
            new_rel_off = target_pos - e_addr
            struct.pack_into('<2I', new_decomp, e_addr, new_rel_off, flag)
            
        # Fraciona em chunks de 65536 bytes
        CHUNK_SIZE = 65536
        raw_chunks = []
        for offset in range(0, len(new_decomp), CHUNK_SIZE):
            raw_chunks.append(new_decomp[offset:offset+CHUNK_SIZE])
            
        num_chunks = len(raw_chunks)
        compressed_chunks = [zlib.compress(c, level=6) for c in raw_chunks]
        c_sizes = [len(c) + 4 for c in compressed_chunks]
        
        # Cabeçalho 0x80 bytes
        new_hdr = bytearray(0x80)
        struct.pack_into('<3I', new_hdr, 0, CHUNK_SIZE, num_chunks, len(new_decomp))
        for c_i, c_sz in enumerate(c_sizes):
            struct.pack_into('<I', new_hdr, 12 + c_i * 4, c_sz)
            
        # Grava no LD_C0_R.BIN com alinhamento a 0x80
        target_bin_f.seek(0, os.SEEK_END)
        pad_bin = (0x80 - (target_bin_f.tell() % 0x80)) % 0x80
        target_bin_f.write(b'\x00' * pad_bin)
        new_bin_offset = target_bin_f.tell()
        
        target_bin_f.write(new_hdr)
        for comp_c in compressed_chunks:
            target_bin_f.write(struct.pack('<I', len(comp_c)))
            target_bin_f.write(comp_c)
            pad_c = (0x80 - (target_bin_f.tell() % 0x80)) % 0x80
            target_bin_f.write(b'\x00' * pad_c)
            
        new_block_size = target_bin_f.tell() - new_bin_offset
        
        # Atualiza o índice LI_C0_R.IDX
        struct.pack_into('<4Q', mod_idx_data, entry_idx * 32, new_bin_offset, len(new_decomp), new_block_size, orig_flag)
        
        if (counter + 1) % 50 == 0 or (counter + 1) == len(target_entry_indices):
            print(f"  Progresso: [{counter+1}/{len(target_entry_indices)}] Entrada {entry_idx:05d}: {orig_id_val:#x} -> {new_bin_offset:#x} (chunks: {num_chunks})")

# 5. Salvar o índice LI_C0_R.IDX
print("[5/5] Salvando índice LI_C0_R.IDX...")
with open(TARGET_IDX, "wb") as f_idx:
    f_idx.write(mod_idx_data)

final_bin_size = os.path.getsize(TARGET_BIN)
total_time = time.time() - t_start

print("\n" + "=" * 70)
print(f"  CONCLUÍDO COM SUCESSO TOTAL EM {total_time:.2f}s!")
print(f"  Total de entradas reconstruídas: {len(target_entry_indices)}")
print(f"  Total de frases traduzidas aplicadas: {total_strings_modified}")
print(f"  Tamanho final LD_C0_R.BIN: {final_bin_size / (1024*1024):.2f} MB")
print(f"  Destino: {MOD_ROMFS_DIR}")
print("=" * 70)
