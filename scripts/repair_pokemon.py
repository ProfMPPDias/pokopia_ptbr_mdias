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

print(f"Total Pokémon list count: {len(all_pokes)}")

# 1. Carregar missing_pokes.json
with open(r"C:\Users\mppdi\.gemini\antigravity\scratch\pokopia-ptbr\missing_pokes.json", "r", encoding="utf-8") as f:
    missing_items = json.load(f)

# Ordenar por tamanho decrescente
sorted_pokes = sorted(list(all_pokes), key=len, reverse=True)
poke_pattern = re.compile(r'\b(' + '|'.join(re.escape(p) for p in sorted_pokes) + r')\b')

# Mapeamento de correções específicas encontradas
known_replacements = {
    # Standalone
    "Happiny": "Happiny", "Noctowl": "Noctowl", "Tinkmaster": "Tinkmaster",
    "Carkol": "Carkol", "Typhlosion": "Typhlosion", "Vespiquen": "Vespiquen",
    "Ditto": "Ditto", "Cacturne": "Cacturne", "Gastly": "Gastly",
    "Torchic": "Torchic", "Illumise": "Illumise", "Tangrowth": "Tangrowth",
    "Weezing": "Weezing", "Whiscash": "Whiscash", "Applin": "Applin",
    "Chewtle": "Chewtle", "Oddish": "Oddish", "Excadrill": "Excadrill",
    "Magneton": "Magneton", "Moltres": "Moltres", "Rolycoly": "Rolycoly",
    "Bruxish": "Bruxish", "Fore-Wyrm": "Fore-Wyrm", "Core-Wyrm": "Core-Wyrm",
    "Aurorus": "Aurorus", "Milotic": "Milotic", "Fidough": "Fidough",
    "Porygon": "Porygon", "Golisopod": "Golisopod", "Porygon-Z": "Porygon-Z",
    "Totodile": "Totodile", "Squirtle": "Squirtle", "Scyther": "Scyther",
    "Slowbro": "Slowbro", "Slowking": "Slowking", "Haunter": "Haunter",
    "Flareon": "Flareon", "Umbreon": "Umbreon", "Magnezone": "Magnezone",
    "Leafeon": "Leafeon", "Conkeldurr": "Conkeldurr", "Persian": "Persian",
    "Empoleon": "Empoleon", "Toxel": "Toxel", "Toxtricity": "Toxtricity",
    "Gloom": "Gloom", "Vileplume": "Vileplume", "Lampent": "Lampent",
    "Mareep": "Mareep", "Electrode": "Electrode", "Cinderace": "Cinderace",
    "Arbok": "Arbok", "Arcanine": "Arcanine",
    
    # Gifts
    "Volcanion’s gifts": "Presentes de Volcanion",
    "Volcanion’s gift": "Presente de Volcanion",
    "Vileplume’s gifts": "Presentes de Vileplume",
    "Vileplume’s gift": "Presente de Vileplume",
    "Happiny’s gift": "Presente de Happiny",
    "Happiny’s gifts": "Presentes de Happiny",
    "Vespiquen’s gift": "Presente de Vespiquen",
    "Vespiquen’s gifts": "Presentes de Vespiquen",
    "Illumise’s gifts": "Presentes de Illumise",
    "Illumise’s gift": "Presente de Illumise",
    "Flaaffy’s gift": "Presente de Flaaffy",
    "Flaaffy’s gifts": "Presentes de Flaaffy",
    "Gloom’s gift": "Presente de Gloom",
    "Gloom’s gifts": "Presentes de Gloom",
    "Scyther’s gift": "Presente de Scyther",
    "Scyther’s gifts": "Presentes de Scyther",
    "Empoleon’s gifts": "Presentes de Empoleon",
    "Empoleon’s gift": "Presente de Empoleon",
    "Ampharos’s gift": "Presente de Ampharos",
    "Ampharos’s gifts": "Presentes de Ampharos",
    "Scizor’s gift": "Presente de Scizor",
    "Dusknoir’s gifts": "Presentes de Dusknoir",
    "Dusknoir’s gift": "Presente de Dusknoir",
    "Tyrantrum’s gifts": "Presentes de Tyrantrum",
    "Victreebel’s gift": "Presente de Victreebel",
    "Victreebel’s gifts": "Presentes de Victreebel",
    "Mr. Mime’s gift": "Presente de Mr. Mime",
    "Mr. Mime’s gifts": "Presentes de Mr. Mime",
    "Cinderace’s gifts": "Presentes de Cinderace",
    "Cinderace’s gift": "Presente de Cinderace",
    "Leafeon’s gifts": "Presentes de Leafeon",
    "Excadrill’s gifts": "Presentes de Excadrill",
    "Electrode’s gift": "Presente de Electrode",
    "Electrode’s gifts": "Presentes de Electrode",
    "Persian’s gifts": "Presentes de Persian",
    "Persian’s gift": "Presente de Persian",
    "Typhlosion’s gifts": "Presentes de Typhlosion",
    "Typhlosion’s gift": "Presente de Typhlosion",
    "Jolteon’s gift": "Presente de Jolteon",
    "Toxtricity’s gifts": "Presentes de Toxtricity",
    "Toxtricity’s gift": "Presente de Toxtricity",
    "Coalossal’s gift": "Presente de Coalossal",
    "Coalossal’s gifts": "Presentes de Coalossal",
    "Haunter’s gifts": "Presentes de Haunter",
    "Haunter’s gift": "Presente de Haunter",
    "Ninetales’s gifts": "Presentes de Ninetales",
    "Ninetales’s gift": "Presente de Ninetales",
    "Meowth’s gift": "Presente de Meowth",
    "Sableye’s gift": "Presente de Sableye",
    "Sableye’s gifts": "Presentes de Sableye",
    "Tyranitar’s gifts": "Presentes de Tyranitar",
    "Ditto’s gift": "Presente de Ditto",
    "Ditto’s gifts": "Presentes de Ditto",
    "Ditto’s Home": "Lar do Ditto",
    "Tinkmaster’s tower": "Torre do Tinkmaster",
    "Starmie dolls": "Bonecas Starmie",
    "Starmie doll": "Boneca Starmie",
    "Primarina statues": "Estátuas de Primarina",
    "Swampert squad rugs": "Tapetes do Esquadrão Swampert",
    "Jumpluff pattern!": "Padrão de Jumpluff!",
    "dynamic Ditto print": "Estampa dinâmica de Ditto",
    "dynamic Ditto prints": "Estampas dinâmicas de Ditto",
    "fanned-out Ditto print": "Estampa aberta de Ditto",
    "fanned-out Ditto prints": "Estampas abertas de Ditto",
    "Yep, I’m a Ditto": "Sim, eu sou um Ditto",
    "Small, white tufts of cotton. Bring them to Hoppip!": "Pequenos tufos brancos de algodão. Leve-os para Hoppip!",
    "An apple full of syrup. Bring it to Applin!": "Uma maçã cheia de xarope. Leve-a para Applin!",
    "A piece of broken red crystal. Bring it to Sableye!": "Um pedaço de cristal vermelho quebrado. Leve-o para Sableye!",
    "A pumpkin-flavored lollipop. Bring it to Pumpkaboo!": "Um pirulito com sabor de abóbora. Leve-o para Pumpkaboo!",
    "Allow the camera to avoid objects between itself and Ditto.": "Permitir que a câmera evite objetos entre ela e o Ditto.",
    "Choose whether the camera automatically follows Ditto.": "Escolha se a câmera segue o Ditto automaticamente.",
    "You can’t change your hair color when you’re Ditto color.": "Você não pode mudar a cor do seu cabelo quando está com a cor do Ditto.",
    "When you’re Ditto color, other bag and clothing colors will not display.": "Quando você estiver com a cor do Ditto, outras cores de bolsa e roupas não serão exibidas.",
    "Ditto can’t stay in deep water too long...": "O Ditto não pode ficar em águas profundas por muito tempo...",
    "Ditto looks totally adorable with its broad smile.": "O Ditto fica totalmente adorável com seu sorriso largo.",
    "A pattern of three Ditto in a row. The way they’re": "Um padrão de três Ditto em fileira. A forma como eles estão",
    "A flag that marks Ditto’s house. Place it on a house": "Uma bandeira que marca a casa do Ditto. Coloque-a em uma casa",
    "will make that Pokémon squeaky clean. This will also make Ditto": "vai deixar aquele Pokémon limpíssimo. Isso também deixará o Ditto",
    "Only its face still looked like Ditto. Unfortunately,": "Apenas o seu rosto ainda parecia o do Ditto. Infelizmente,",
    "Page 20 – Leafeon Aroma for Relaxation": "Página 20 – Aroma de Leafeon para Relaxamento",
    "Clefairy dancing under a full moon.": "Clefairy dançando sob a lua cheia.",
    "A gift from Low Key Form Toxtricity. What’ll happen if": "Um presente da Forma Baixa de Toxtricity. O que acontecerá se",
    "Dusknoir. And when night falls...": "Dusknoir. E quando a noite cai...",
    "Sableye collects their broken fragments.": "Sableye coleta seus fragmentos quebrados.",
    "This issue’s feature article is all about Vespiquen!": "O artigo principal desta edição é todinho sobre Vespiquen!",
    "Floatzel carries people as if it were a rubber raft.": "Floatzel carrega pessoas como se fosse um bote inflável.",
    "Lampent appears at the moment of death and promptly absorbs": "Lampent aparece no momento da morte e prontamente absorve",
    "It loves the sweet aroma given off by Illumise.": "Ele adora o doce aroma exalado por Illumise.",
    "If the vines grow long, Tangrowth shortens them by tearing parts": "Se os cipós crescerem muito, Tangrowth os encurta arrancando partes",
    "Is this a time capsule? Professor Tangrowth might": "Isto é uma cápsula do tempo? O Professor Tangrowth pode",
    "A wall clock shaped like a small house. Rowlet will": "Um relógio de parede em forma de casinha. Rowlet vai",
    "over brought their best Corphish to participate, and": "trouxeram seus melhores Corphish para participar, e",
    "a coating to protect it from dust. Cinccino won’t tolerate even a": "uma camada para protegê-lo da poeira. Cinccino não tolera nem um",
    "Horsea. There are just so many to catch—I’m having": "Horsea. Há tantos para pegar—estou tendo",
    "Vulcan the Ninetales of the Vermilion City Pokémon": "Vulcan, o Ninetales do Pokémon de Vermilion City",
    "It has no problem drinking dirty water. An organ inside Toxel’s": "Não tem problemas para beber água suja. Um órgão dentro de Toxel",
    "This Pokémon is three Magnemite that have linked": "Este Pokémon é formado por três Magnemite que se uniram",
    "You got <$cdef(27)><fqty(1)><$ifull(111)></color> from <$cdef(27)>Mareep</color>!": "Você obteve <$cdef(27)><fqty(1)><$ifull(111)></color> de <$cdef(27)>Mareep</color>!",
    "<oneline><$comeff(1,10)><$motion(1,664)><$voicel(1,9)>Come, <$cdef(27)><pname;0></color>! Let’s follow <$cdef(27)>Tinkmaster</color>!": "<oneline><$comeff(1,10)><$motion(1,664)><$voicel(1,9)>Venha, <$cdef(27)><pname;0></color>! Vamos seguir o <$cdef(27)>Tinkmaster</color>!",
    "<$comeff(1,10)><$facial(1,4)><$motion(1,801)><$voicel(1,9)>I look forward to seeing this building completed,<br><$cdef(27)><pname;0></color> and <$cdef(27)>Tinkmaster</color>!": "<$comeff(1,10)><$facial(1,4)><$motion(1,801)><$voicel(1,9)>Estou ansioso para ver este edifício concluído,<br><$cdef(27)><pname;0></color> e <$cdef(27)>Tinkmaster</color>!",
    "Go show the <$cdef(27)><fqty(1)><$ifull(435)> </color>to <$cdef(27)>Mareanie</color>!": "Vá mostrar o <$cdef(27)><fqty(1)><$ifull(435)> </color>para <$cdef(27)>Mareanie</color>!",
    "<$voicel(2,5)><$comeff(2,14)><$motion(2,666)>I always get all dried out whenever I chat with <$cdef(27)>Lampent</color>...<br><$voicel(2,4)><$emotion(2,29)>Could I ask you to splash me with <$cdef(27)><$sklfull(3)></color>?": "<$voicel(2,5)><$comeff(2,14)><$motion(2,666)>Eu sempre fico todo seco quando converso com <$cdef(27)>Lampent</color>...<br><$voicel(2,4)><$emotion(2,29)>Poderia me molhar com <$cdef(27)><$sklfull(3)></color>?",
    "Cacnea": "Cacnea",
    "Serperior": "Serperior",
    "Porygon2": "Porygon2",
    "Mareanie": "Mareanie",
    "Greedent": "Greedent",
    "Mr. Mime": "Mr. Mime",
    "d-out Ditto print": "estampa recortada de Ditto",
    "<$comeff(1,10)><$motion(1,814)><$voicel(1,5)>*bzzzt bzzzt* Greetings.<clear><br><$comeff(1,6)><$motion(1,827)><$voicel(1,7)>I do look like just three Magnemite sticking together,<br>yes?<clear><br><$comeff(1,9)><$motion(1,803)><$voicel(1,8)>Well, we are just sticking together. Yes.<clear><br><$comeff(1,10)><$motion(1,802)><$voicel(1,7)>Actually, it requires much skill to work together as three.<clear><br><$comeff(1,13)><$facial(1,4)><$motion(1,801)><$voicel(1,10)>So I think we too can be good friends. We and you.": "<$comeff(1,10)><$motion(1,814)><$voicel(1,5)>*bzzzt bzzzt* Saudações.<clear><br><$comeff(1,6)><$motion(1,827)><$voicel(1,7)>Eu pareço apenas três Magnemite grudados,<br>não é?<clear><br><$comeff(1,9)><$motion(1,803)><$voicel(1,8)>Bem, nós estamos apenas grudados. Sim.<clear><br><$comeff(1,10)><$motion(1,802)><$voicel(1,7)>Na verdade, requer muita habilidade trabalhar juntos em três.<clear><br><$comeff(1,13)><$facial(1,4)><$motion(1,801)><$voicel(1,10)>Então acho que nós também podemos ser bons amigos. Nós e você.",
    "Plug it in and switch on the screen. DJ Ditto in": "Conecte-o e ligue a tela. DJ Ditto em",
}

# Aplicar correções conhecidas
for en_k, pt_v in known_replacements.items():
    tr[en_k] = pt_v

# Função de correção inteligente para cdef e frases com nomes de Pokémon
cdef_en_pattern = re.compile(r'<\$cdef\(27\)>(\s*)([A-Za-z0-9\-\’\.\s]+?)(\s*)(</color>|<slide>|<br>|<clear>)')
cdef_pt_pattern = re.compile(r'<\$cdef\(27\)>(\s*)(.*?)(\s*)(</color>|<slide>|<br>|<clear>)')

def fix_pokemon_in_string(en, pt):
    # Se já tem o Pokémon no pt, não precisa mexer em cdef
    # Alinhamento de tags cdef(27)
    m_en = list(cdef_en_pattern.finditer(en))
    m_pt = list(cdef_pt_pattern.finditer(pt))
    if m_en and len(m_en) == len(m_pt):
        # Mapear e substituir cada tag cdef
        res_pt = pt
        for me, mp in zip(m_en, m_pt):
            content_en = me.group(2).strip()
            # Checar se content_en é ou contém um nome de pokemon
            for p in sorted_pokes:
                if p == content_en or content_en.startswith(p):
                    old_tag = mp.group(0)
                    lead_sp = mp.group(1)
                    trail_sp = mp.group(3)
                    close_tag = mp.group(4)
                    new_tag = f"<$cdef(27)>{lead_sp}{content_en}{trail_sp}{close_tag}"
                    res_pt = res_pt.replace(old_tag, new_tag, 1)
                    break
        pt = res_pt

    # Correções de palavras residuais
    # Ditto
    if "Ditto" in en:
        pt = re.sub(r'\b[Ii]dem\b', 'Ditto', pt)
        pt = re.sub(r'\bItto\b', 'Ditto', pt)
        pt = re.sub(r'\bda mesma cor\b', 'da cor do Ditto', pt)
        pt = re.sub(r'\bcor Idem\b', 'cor do Ditto', pt)
        pt = re.sub(r'\bO mesmo\b', 'O Ditto', pt)
        pt = re.sub(r'\bo mesmo\b', 'o Ditto', pt)

    # Slowpoke
    if "Slowpoke" in en and "Slowpoke" not in pt:
        pt = re.sub(r'\bbocejos lentos\b', 'bocejos de um Slowpoke', pt)
        pt = re.sub(r'\blentos\b', 'Slowpoke', pt)

    # Scyther
    if "Scyther" in en and "Scyther" not in pt:
        pt = re.sub(r'\bCíter\b', 'Scyther', pt)
        pt = re.sub(r'\bCitera\b', 'Scyther', pt)
        pt = re.sub(r'\bCitro\b', 'Scyther', pt)

    # Squirtle
    if "Squirtle" in en and "Squirtle" not in pt:
        pt = re.sub(r'\bEsguicho\b', 'Squirtle', pt)

    # Haunter
    if "Haunter" in en and "Haunter" not in pt:
        pt = re.sub(r'\bAssombrador\b', 'Haunter', pt)

    # Happiny
    if "Happiny" in en and "Happiny" not in pt:
        pt = re.sub(r'\bFeliz\b', 'Happiny', pt)
        pt = re.sub(r'\bHappyy\b', 'Happiny', pt)

    # Tinkmaster
    if "Tinkmaster" in en and "Tinkmaster" not in pt:
        pt = re.sub(r'\bSincronia:\b', 'Tinkmaster', pt)
        pt = re.sub(r'\bSinkmaster\b', 'Tinkmaster', pt)

    # Toxtricity
    if "Toxtricity" in en and "Toxtricity" not in pt:
        pt = re.sub(r'\bToxtricidade\b', 'Toxtricity', pt)

    # Toxel
    if "Toxel" in en and "Toxel" not in pt:
        pt = re.sub(r'\bToxil\b', 'Toxel', pt)

    # Illumise
    if "Illumise" in en and "Illumise" not in pt:
        pt = re.sub(r'\bIluminar\b', 'Illumise', pt)
        pt = re.sub(r'\bIlluminar\b', 'Illumise', pt)
        pt = re.sub(r'\bIlluminase\b', 'Illumise', pt)

    # Empoleon
    if "Empoleon" in en and "Empoleon" not in pt:
        pt = re.sub(r'\bEmpoleão\b', 'Empoleon', pt)

    # Flareon
    if "Flareon" in en and "Flareon" not in pt:
        pt = re.sub(r'\bFlareão\b', 'Flareon', pt)

    # Umbreon
    if "Umbreon" in en and "Umbreon" not in pt:
        pt = re.sub(r'\bUmbreão\b', 'Umbreon', pt)

    # Torchic
    if "Torchic" in en and "Torchic" not in pt:
        pt = re.sub(r'\bTórquico\b', 'Torchic', pt)

    # Electrode
    if "Electrode" in en and "Electrode" not in pt:
        pt = re.sub(r'\bEletrodo\b', 'Electrode', pt)
        pt = re.sub(r'\beletrodo\b', 'Electrode', pt)

    # Tangrowth
    if "Tangrowth" in en and "Tangrowth" not in pt:
        pt = re.sub(r'\bcrescimento do bronzeado\b', 'Tangrowth', pt)
        pt = re.sub(r'\bCrescimento de bronzeamento\b', 'Tangrowth', pt)

    # Cinderace
    if "Cinderace" in en and "Cinderace" not in pt:
        pt = re.sub(r'\bCinderela\b', 'Cinderace', pt)

    # Gloom
    if "Gloom" in en and "Gloom" not in pt:
        pt = re.sub(r'\bAlumínio\b', 'Gloom', pt)
        pt = re.sub(r'\bObscenidade\b', 'Gloom', pt)
        pt = re.sub(r'\bobscenidade\b', 'Gloom', pt)

    # Weezing
    if "Weezing" in en and "Weezing" not in pt:
        pt = re.sub(r'\bTrituração\b', 'Weezing', pt)

    # Whiscash
    if "Whiscash" in en and "Whiscash" not in pt:
        pt = re.sub(r'\bSushi\b', 'Whiscash', pt)

    # Applin
    if "Applin" in en and "Applin" not in pt:
        pt = re.sub(r'\bAplicativo\b', 'Applin', pt)

    # Chewtle
    if "Chewtle" in en and "Chewtle" not in pt:
        pt = re.sub(r'\bMastigar\b', 'Chewtle', pt)

    # Oddish
    if "Oddish" in en and "Oddish" not in pt:
        pt = re.sub(r'\bEstranha\b', 'Oddish', pt)

    # Dusknoir
    if "Dusknoir" in en and "Dusknoir" not in pt:
        pt = re.sub(r'\bCrepúsculo\b', 'Dusknoir', pt)
        pt = re.sub(r'\bcrepúsculo\b', 'Dusknoir', pt)

    # Sableye
    if "Sableye" in en and "Sableye" not in pt:
        pt = re.sub(r'\bSabley\b', 'Sableye', pt)

    # Ampharos
    if "Ampharos" in en and "Ampharos" not in pt:
        pt = re.sub(r'\bAmfaros\b', 'Ampharos', pt)

    # Arbok
    if "Arbok" in en and "Arbok" not in pt:
        pt = re.sub(r'\bArboque\b', 'Arbok', pt)

    # Leafeon
    if "Leafeon" in en and "Leafeon" not in pt:
        pt = re.sub(r'\bFolha-de-cavalo\b', 'Leafeon', pt)
        pt = re.sub(r'\bFolha\b', 'Leafeon', pt)

    # Persian
    if "Persian" in en and "Persian" not in pt:
        pt = re.sub(r'\bPersa\b', 'Persian', pt)
        pt = re.sub(r'\bpersa\b', 'Persian', pt)
        pt = re.sub(r'\bpersas\b', 'Persian', pt)

    # Slowbro
    if "Slowbro" in en and "Slowbro" not in pt:
        pt = re.sub(r'\bBro lento\b', 'Slowbro', pt)

    # Slowking
    if "Slowking" in en and "Slowking" not in pt:
        pt = re.sub(r'\bAtraso\b', 'Slowking', pt)

    # Magneton / Magnezone
    if "Magneton" in en and "Magneton" not in pt:
        pt = re.sub(r'\bMagnetão\b', 'Magneton', pt)
    if "Magnezone" in en and "Magnezone" not in pt:
        pt = re.sub(r'\bMagnezona\b', 'Magnezone', pt)

    # Conkeldurr
    if "Conkeldurr" in en and "Conkeldurr" not in pt:
        pt = re.sub(r'\bConkeldur\b', 'Conkeldurr', pt)

    # Vespiquen
    if "Vespiquen" in en and "Vespiquen" not in pt:
        pt = re.sub(r'\bVespiken\b', 'Vespiquen', pt)
        pt = re.sub(r'\bVespiqueno\b', 'Vespiquen', pt)

    # Flaaffy
    if "Flaaffy" in en and "Flaaffy" not in pt:
        pt = re.sub(r'\bFlafy\b', 'Flaaffy', pt)

    # Victreebel
    if "Victreebel" in en and "Victreebel" not in pt:
        pt = re.sub(r'\bVitreebel\b', 'Victreebel', pt)
        pt = re.sub(r'\bVistrebel\b', 'Victreebel', pt)

    # Typhlosion
    if "Typhlosion" in en and "Typhlosion" not in pt:
        pt = re.sub(r'\bticlosão\b', 'Typhlosion', pt)
        pt = re.sub(r'\bTiflosão\b', 'Typhlosion', pt)

    # Jolteon
    if "Jolteon" in en and "Jolteon" not in pt:
        pt = re.sub(r'\bJôlteo\b', 'Jolteon', pt)

    # Coalossal
    if "Coalossal" in en and "Coalossal" not in pt:
        pt = re.sub(r'\bColossal\b', 'Coalossal', pt)

    # Ninetales
    if "Ninetales" in en and "Ninetales" not in pt:
        pt = re.sub(r'\bNinotales\b', 'Ninetales', pt)
        pt = re.sub(r'\bNinales\b', 'Ninetales', pt)

    # Meowth
    if "Meowth" in en and "Meowth" not in pt:
        pt = re.sub(r'\bMiau\b', 'Meowth', pt)

    # Volcanion
    if "Volcanion" in en and "Volcanion" not in pt:
        pt = re.sub(r'\bVulcão\b', 'Volcanion', pt)

    # Tyrantrum
    if "Tyrantrum" in en and "Tyrantrum" not in pt:
        pt = re.sub(r'\btirano\b', 'Tyrantrum', pt)
        pt = re.sub(r'\bTirantro\b', 'Tyrantrum', pt)

    # Frillish
    if "Frillish" in en and "Frillish" not in pt:
        pt = re.sub(r'\bFrílis\b', 'Frillish', pt)

    # Carkol
    if "Carkol" in en and "Carkol" not in pt:
        pt = re.sub(r'\bCarcol\b', 'Carkol', pt)

    # Cacturne
    if "Cacturne" in en and "Cacturne" not in pt:
        pt = re.sub(r'\bCaturno\b', 'Cacturne', pt)

    # Noctowl
    if "Noctowl" in en and "Noctowl" not in pt:
        pt = re.sub(r'\bNocturna\b', 'Noctowl', pt)

    # Moltres
    if "Moltres" in en and "Moltres" not in pt:
        pt = re.sub(r'\bMoltros\b', 'Moltres', pt)

    # Rolycoly
    if "Rolycoly" in en and "Rolycoly" not in pt:
        pt = re.sub(r'\bRolicoli\b', 'Rolycoly', pt)

    # Bruxish
    if "Bruxish" in en and "Bruxish" not in pt:
        pt = re.sub(r'\bBruxos\b', 'Bruxish', pt)

    # Aurorus
    if "Aurorus" in en and "Aurorus" not in pt:
        pt = re.sub(r'\bAuroro\b', 'Aurorus', pt)

    # Fidough
    if "Fidough" in en and "Fidough" not in pt:
        pt = re.sub(r'\bFido\b', 'Fidough', pt)

    # Corphish
    if "Corphish" in en and "Corphish" not in pt:
        pt = re.sub(r'\bCorfis\b', 'Corphish', pt)

    # Horsea
    if "Horsea" in en and "Horsea" not in pt:
        pt = re.sub(r'\bHorya\b', 'Horsea', pt)

    # Porygon
    if "Porygon" in en and "Porygon" not in pt:
        pt = re.sub(r'\bPorígono\b', 'Porygon', pt)

    # Totodile
    if "Totodile" in en and "Totodile" not in pt:
        pt = re.sub(r'\bTotódilo\b', 'Totodile', pt)

    # Floatzel
    if "Floatzel" in en and "Floatzel" not in pt:
        pt = re.sub(r'\bA Flutuante\b', 'Floatzel', pt)

    # Jumpluff
    if "Jumpluff" in en and "Jumpluff" not in pt:
        pt = re.sub(r'\bpulgas\b', 'Jumpluff', pt)

    return pt

# Aplicar em todo o mapa de tradução
total_fixed = 0
for en, pt in list(tr.items()):
    new_pt = fix_pokemon_in_string(en, pt)
    if new_pt != pt:
        tr[en] = new_pt
        total_fixed += 1

print(f"Total de frases com nomes de Pokémon corrigidos no master map: {total_fixed}")

# Salvar o translations_master.json atualizado
with open(MASTER_MAP_PATH, "w", encoding="utf-8") as f:
    json.dump(tr, f, ensure_ascii=False, indent=2)

print("translations_master.json salvo com sucesso!")

# Agora verificar quantos ainda estão pendentes
missing_after = []
for en, pt in tr.items():
    pokes_in_en = set(poke_pattern.findall(en))
    for p in pokes_in_en:
        if not re.search(r'\b' + re.escape(p) + r'\b', pt, re.IGNORECASE):
            missing_after.append((p, en, pt))

print(f"Pendentes após correção: {len(missing_after)}")
if missing_after:
    for p, en, pt in missing_after[:15]:
        print(f"  [{p}] EN: {repr(en)} -> PT: {repr(pt)}")
