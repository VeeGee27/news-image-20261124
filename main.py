#!/usr/bin/env python3
"""news-image-20261124 v1 — draws the 1024x1024 newspaper image.

Written fresh in-session for the make.fun bounty news-image-20261124
("Sum up 24 November's world news in one image"). Every story below was
verified against its original source on 2026-11-25; stories that failed
the Tuesday 24 Nov 2026 test were replaced (see REPORT.md).
Stdlib + Pillow only; deterministic (no randomness, no timestamps).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or HERE
OUT = os.path.join(OUT_DIR, "entry.png")

# ---------------------------------------------------------------- colours
PAPER = (246, 239, 220)
PAPER_DK = (238, 228, 200)
INK = (28, 26, 22)
INK_SOFT = (74, 68, 58)
RED = (163, 18, 18)
RED_DK = (125, 13, 13)
BLUE = (31, 78, 121)
RULE = (180, 168, 138)
CARD_BG = (252, 248, 236)
SEA = (214, 228, 230)
LAND = (196, 178, 128)
LAND_LINE = (138, 122, 77)
PIN_BG = (163, 18, 18)
PIN_TX = (255, 255, 255)

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"
def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

f_title = F(SERIF_B, 38)
f_date = F(SANS, 12)
f_stat = F(SERIF_B, 13)
f_hero_h = F(SERIF_B, 16)
f_hero_d = F(SERIF, 11)
f_mid_h = F(SERIF_B, 14)
f_mid_d = F(SERIF, 11)
f_tag = F(SANS_B, 8)
f_brief = F(SERIF, 11)
f_brief_n = F(SANS_B, 10)
f_sect = F(SERIF_B, 12)
f_dc = F(SERIF, 11)
f_dc_b = F(SERIF_B, 11)
f_foot = F(SANS, 9)
f_pin = F(SANS_B, 8)
f_art = F(SERIF_B, 13)
f_art_s = F(SANS_B, 9)

# ---------------------------------------------------------------- helpers
def wrap(d, text, font, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_w(d, s, font):
    return d.textlength(s, font=font)

# ---------------------------------------------------------------- stories
# heroes: (num, headline, deck, tag, region, pin_lon, pin_lat, art)
HEROES = [
    (1, "HUANG ADMITS MISTAKES AS SHARES SLIP",
     "Huang told staff Tue he broke Nvidia's code of conduct; shares fell 5.9% to $155.38 after Mon's 31.5% surge added ~$950bn.",
     "REPORTED", "North America", -122, 37, "chip"),
    (2, "THREE TANKERS HIT BY MINES IN HORMUZ",
     "IRGC says three tankers hit mines in the Strait \u2014 claims unverified, no ships named; Tehran: no talks until the US meets its 7 conditions.",
     "REPORTED", "Middle East", 56, 26, "tanker"),
    (3, "SENEGAL \u2014 AFCON TITLE RESTORED",
     "CAS reinstated Senegal as 2025 AFCON winners after their 1\u20130 extra-time win over Morocco in the 18 Jan final in Rabat.",
     "CONFIRMED", "Africa", -17, 14, "trophy"),
]

# mids: (num, headline, deck, tag, region, pin_lon, pin_lat)
MIDS = [
    (4, "LIBYA \u2014 2 OFFICERS DIE IN SUNDAY ATTACK",
     "Two Libyan naval officers died Tue of wounds from Sun's drone attack on the Russian corvette Merkury at Benghazi; Kyiv calls it self-defence under Article 51.",
     "REPORTED", "Africa", 20, 32),
    (5, "CHINA \u2014 FIRST FOREIGNER FOR TIANGONG",
     "China named the Shenzhou-24 crew \u2014 Tang Hongbo, Wu Yi and Pakistani Muhammad Zeeshan Ali, 40, first Pakistani in orbit \u2014 launch Wed 08:18 Beijing.",
     "OFFICIAL", "East Asia", 100, 40),
    (6, "N. KOREA \u2014 THREAT TO SHUT SWISS OFFICE",
     "Kim Yo Jong said the North would consider shutting Switzerland's new office in Pyongyang after Bern sanctioned a youth camp linked to the Russia war.",
     "REPORTED", "East Asia", 127, 39),
    (7, "SOLOMONS \u2014 SCRAP CHINA SECURITY PACT",
     "The Solomons ended its 2022 security pact with China \u2014 the deal that raised fears of a Chinese naval foothold \u2014 clearing the way for an Australian treaty.",
     "REPORTED", "Oceania", 160, -9),
    (8, "MARKETS \u2014 ASIA SURGES, US SLIPS",
     "Kospi +6.3%, Nikkei +3.91% to 58,645 on Huang's return; Wall St slipped \u2014 Nasdaq -1.5%, S&P -0.5%; Brent settled $91.40, up 2.3%.",
     "REPORTED", "Global", 127, 37),
    (9, "YEMEN \u2014 HOUTHIS CLOSE IN ON ADEN",
     "Houthis are ~60 km from Aden as Yemeni forces prepare its defences; a strike on buses and trucks killed 26, with Houthis blaming Saudi jets.",
     "REPORTED", "Middle East", 45, 13),
    (10, "BANGLADESH \u2014 HASINA PLANS DEC 16 RETURN",
     "Ousted leader Sheikh Hasina plans to return from exile on 16 Dec despite a death sentence in absentia for the Aug 2024 crackdown; her party is banned.",
     "REPORTED", "South Asia", 90, 24),
    (11, "UKRAINE \u2014 STRIKE KILLS 2, WOUNDS 48",
     "A Russian strike on Zaporizhzhia killed 2 and wounded 48, including four children; a glide bomb destroyed a house and part of a five-storey block.",
     "REPORTED", "Europe", 35, 48),
    (12, "USA \u2014 CONSUMER CONFIDENCE HITS 103.3",
     "The Conference Board index rose 11.4 points to 103.3 in November, up from 91.9 in October \u2014 its highest level since January 2025.",
     "OFFICIAL", "North America", -77, 39),
    (13, "VIETNAM \u2014 HOT-POT BLAST KILLS 6 IN HANOI",
     "A gas blast at a hot-pot eatery on Nguyen Van Tuyet Street in Dong Da killed 6 and injured more than a dozen at ~8:30 a.m. Tue.",
     "REPORTED", "Southeast Asia", 106, 21),
    (14, "MALAYSIA \u2014 6,803 SENT BACK TO MYANMAR",
     "PM Anwar told parliament Malaysia will return 6,803 Myanmar nationals in Dec \u2014 1,500 by navy ships on 6\u20137 Dec, 5,303 by air \u2014 days after the ICJ ruling.",
     "REPORTED", "Southeast Asia", 101, 3),
    (15, "GAZA \u2014 STRIKES KILL 7 DESPITE CEASEFIRE",
     "Israeli strikes killed 7 Palestinians, including a child and police officers; meningitis cases surged to 272 in Oct, eight times the normal monthly rate.",
     "REPORTED", "Middle East", 34, 31),
    (16, "USA \u2014 TARIFFS READIED ON CHINA AND EU",
     "The US is preparing tariffs on China, the EU and 14 other economies under a Section 301 probe into subsidised production; rates are not yet fixed.",
     "REPORTED", "North America", -82, 36),
]

# briefs: (num, text, region, pin_lon, pin_lat)
BRIEFS = [
    (17, "Zelensky confirms Ukraine hit Russian ship Sparta II in the Gulf of Finland.", "Europe", 24, 60),
    (18, "Trump to meet NATO chief Rutte on Wednesday in Palm Beach, Florida.", "North America", -80, 27),
    (19, "Alibaba calls the US blacklisting of its Singapore unit Apex 'erroneous'.", "North America", 104, 1),
    (20, "DNC's 2028 dark-money pledge draws pushback a day after its unveiling.", "North America", -77, 39),
    (21, "Norway pledges at least $7bn in 2027 aid to Ukraine; DESNA defence to expand.", "Europe", 10, 60),
    (22, "Timms review calls for a PIP overhaul; no plan to cut the \u00a325bn welfare bill.", "Europe", -1, 52),
    (23, "Two men arrested over a suspected burglary at Prince William's Anmer Hall.", "Europe", 1, 53),
    (24, "UK's MI5 warns defence firms of a Russian sabotage threat.", "Europe", -1, 52),
    (25, "Russia's 2026 troop losses hit a record 432,519, Kyiv's General Staff says.", "Europe", 37, 56),
    (26, "Poland reports a Russian surveillance drone briefly entered its airspace.", "Europe", 19, 52),
    (27, "South Korea scrambles jets as Russian aircraft near Ulleungdo island.", "East Asia", 130, 38),
    (28, "China extends its pause on US mineral export curbs by 2 months, to 27 Jan.", "East Asia", 116, 40),
    (29, "Japan to pay its full 2027 ICC contribution early, by year-end.", "East Asia", 140, 38),
    (30, "Singapore will keep investigating Megaspeed, PM Wong says.", "Southeast Asia", 104, 1),
    (31, "Poland renews its push for a permanent US military base after two incursions.", "Europe", 19, 52),
    (32, "Gunmen take ~30 hostages in a Cartagena supermarket; 10 freed by nightfall.", "South America", -74, 10),
    (33, "Iraq orders federal control of Kurdish oilfields in 4 provinces.", "Middle East", 44, 33),
    (34, "Erdogan and Aliyev back the US-backed TRIPP route through Armenia.", "Europe", 45, 40),
    (35, "Huawei guilty on 10 of 12 counts in a US trial \u2014 trade secrets, fraud.", "North America", -74, 41),
    (36, "Zambia's Mundubile committed to the High Court for a treason trial.", "Africa", 28, -15),
    (37, "Houthis threaten to strike Saudi Red Sea ports in retaliation.", "Middle East", 45, 20),
    (38, "Gavi signs deal to secure 1.5m doses of a potential Ebola vaccine for Congo.", "Africa", 25, -2),
    (39, "Lahore again tops the world's most-polluted list, AQI 538.", "South Asia", 74, 31),
]

STATS = [
    "KOSPI +6.3% TUESDAY",
    "NIKKEI +3.91% TO 58,645",
    "BRENT $91.40, UP 2.3%",
    "3 TANKERS HIT NEAR HORMUZ",
]

DATE_CHECK = [
    ("Merkury sinking", "attack was Sun 22 Nov (only Tue angles count)"),
    ("Shenzhou-24 launch", "Wed 25 Nov, 08:18 Beijing (crew named Tue)"),
    ("COP31 ended", "Sun 22 Nov"),
    ("Guterres AI framework", "called for Mon 23 Nov"),
    ("Huang reinstatement", "board acted Mon 23 Nov (Tue angles count)"),
    ("Taiex rebound 779 pts", "Mon 23 Nov"),
]

REGIONS = ["North America", "South America", "Europe", "Middle East",
           "Africa", "South Asia", "Southeast Asia", "East Asia", "Oceania"]

# ---------------------------------------------------------------- world map
# Coarse continent outlines as (lon, lat) points, equirectangular.
# Drawn on a box-sized layer and pasted in, so nothing can leak outside.
N_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
    (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
    (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12),
    (-83, 9), (-80, 8), (-77, 8), (-80, 13), (-83, 15), (-87, 16),
    (-88, 18), (-90, 21), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
    (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
    (-65, 44), (-60, 47), (-55, 47), (-60, 50), (-65, 50), (-60, 52),
    (-55, 52), (-60, 55), (-65, 60), (-68, 58), (-75, 62), (-80, 66),
    (-85, 66), (-90, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
    (-155, 71), (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68),
    (-22, 70), (-20, 74), (-25, 78), (-35, 80), (-50, 80), (-58, 76),
    (-58, 70)]
S_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
    (-72, -18), (-70, -23), (-70, -30), (-73, -37), (-73, -44), (-70, -50),
    (-68, -55), (-65, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -35),
    (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6),
    (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9),
    (-68, 11), (-72, 12), (-75, 10)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
    (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, 0), (12, -2),
    (13, -6), (12, -12), (13, -17), (12, -22), (14, -28), (17, -33),
    (20, -35), (26, -34), (32, -29), (35, -24), (40, -16), (40, -10),
    (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (44, 11), (40, 15),
    (38, 18), (37, 22), (34, 27), (32, 31), (30, 31), (25, 32), (20, 32),
    (15, 32), (11, 34), (10, 37), (5, 37), (-1, 35)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25),
    (44, -25), (43, -20)]
EUROPE = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 52), (7, 55),
    (8, 58), (10, 62), (15, 68), (25, 71), (32, 70), (40, 67), (48, 68),
    (55, 68), (60, 66), (55, 60), (48, 58), (42, 56), (35, 54), (30, 52),
    (28, 55), (24, 58), (20, 60), (18, 58), (15, 55), (12, 54), (8, 54),
    (5, 53), (2, 51), (-2, 50), (-5, 48), (-2, 44), (-5, 43), (-9, 43),
    (-10, 38)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
    (-3, 50)]
ICELAND = [(-22, 64), (-18, 63), (-15, 64), (-18, 66), (-22, 66), (-24, 65)]
ASIA = [(30, 36), (34, 36), (36, 33), (40, 31), (43, 29), (48, 30),
    (50, 29), (54, 27), (57, 26), (60, 25), (64, 25), (66, 25), (70, 22),
    (72, 20), (75, 18), (77, 15), (80, 13), (80, 10), (77, 8), (80, 6),
    (84, 8), (88, 10), (91, 12), (92, 15), (94, 17), (97, 16), (98, 14),
    (100, 12), (103, 10), (105, 9), (107, 11), (109, 13), (108, 16),
    (106, 20), (108, 22), (110, 20), (113, 22), (116, 23), (119, 25),
    (121, 28), (120, 32), (122, 35), (120, 38), (122, 40), (126, 40),
    (128, 38), (130, 42), (132, 43), (135, 44), (138, 46), (140, 48),
    (142, 50), (142, 54), (140, 58), (142, 62), (150, 60), (156, 59),
    (160, 60), (162, 58), (160, 55), (156, 52), (150, 59), (142, 55),
    (141, 50), (140, 45), (138, 42), (135, 38), (130, 35), (127, 35),
    (126, 38), (124, 40), (122, 38), (120, 35), (122, 32), (120, 28),
    (118, 25), (116, 22), (113, 21), (110, 20), (108, 18), (106, 20),
    (105, 15), (103, 10), (101, 8), (99, 10), (98, 12), (97, 15),
    (94, 17), (92, 16), (91, 14), (89, 12), (87, 10), (85, 12), (83, 15),
    (80, 15), (78, 10), (76, 8), (74, 12), (72, 18), (70, 20), (68, 22),
    (66, 25), (62, 25), (60, 25), (58, 26), (56, 27), (54, 27), (52, 28),
    (50, 29), (48, 30), (46, 29), (44, 29), (42, 30), (40, 31), (38, 32),
    (36, 34), (34, 36), (32, 36)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
    (141, 40), (142, 42), (144, 44), (143, 42), (141, 40), (139, 37),
    (137, 35), (135, 33), (132, 32)]
INDONESIA = [(95, 5), (98, 3), (100, 0), (102, -2), (104, -4), (106, -6),
    (108, -7), (110, -7), (112, -7), (114, -8), (116, -9), (118, -9),
    (120, -10), (122, -10), (124, -10), (126, -9), (128, -8), (130, -7),
    (132, -5), (134, -4), (136, -2), (138, -2), (140, -3), (141, -5),
    (140, -8), (138, -8), (136, -6), (134, -5), (132, -4), (130, -2),
    (128, 0), (126, 1), (124, 2), (122, 1), (120, 0), (118, 1), (116, 2),
    (114, 1), (112, 0), (110, -1), (108, -2), (106, -3), (104, -4),
    (102, -3), (100, 0), (98, 3)]
PHILIPPINES = [(120, 18), (122, 18), (122, 16), (124, 14), (122, 12),
    (121, 10), (120, 12), (119, 15)]
NEW_GUINEA = [(131, -1), (134, -2), (137, -3), (140, -4), (142, -6),
    (145, -7), (147, -8), (150, -9), (148, -10), (146, -8), (144, -6),
    (142, -5), (140, -3), (137, -2), (134, -1)]
AUSTRALIA = [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38),
    (150, -37), (153, -32), (153, -27), (151, -24), (149, -20), (146, -19),
    (143, -15), (142, -11), (141, -13), (142, -15), (141, -18), (140, -20),
    (139, -17), (137, -15), (136, -12), (135, -12), (133, -12), (132, -11),
    (130, -13), (128, -15), (126, -14), (124, -16), (122, -17), (120, -20),
    (118, -20), (115, -21)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
    (175, -40), (173, -42), (170, -44), (166, -45)]
LAND_POLYS = [N_AMERICA, GREENLAND, S_AMERICA, AFRICA, MADAGASCAR, EUROPE,
              UK, ICELAND, ASIA, JAPAN, INDONESIA, PHILIPPINES, NEW_GUINEA,
              AUSTRALIA, NEW_ZEALAND]

ALL_STORIES = []
for _h in HEROES:
    ALL_STORIES.append((_h[0], _h[5], _h[6]))
for _m in MIDS:
    ALL_STORIES.append((_m[0], _m[5], _m[6]))
for _b in BRIEFS:
    ALL_STORIES.append((_b[0], _b[3], _b[4]))

# ---------------------------------------------------------------- layout
M = 12                      # outer margin
CW = W - 2 * M              # 1000 content width

def badge(d, x, y, s, num, size=18):
    """Red number badge; returns its width."""
    d.rounded_rectangle([x, y, x + size, y + size], radius=3, fill=RED)
    t = str(num)
    f = F(SANS_B, 10 if size >= 18 else 9)
    tw = d.textlength(t, font=f)
    d.text((x + (size - tw) / 2, y + (size - 10) / 2 - 1), t, font=f, fill=PIN_TX)
    return size

def draw_tag(d, x_right, y, tag):
    col = RED if tag == "REPORTED" else (BLUE if tag == "OFFICIAL" else RED_DK)
    d.text((x_right - d.textlength(tag, font=f_tag), y), tag, font=f_tag, fill=col)

def draw_hero_art(d, x0, y0, w, kind, tag):
    """Simple geometric art panel for a hero card; tag chip top-right."""
    if kind == "chip":
        d.rectangle([x0, y0, x0 + w, y0 + 48], fill=(15, 61, 30))
        cx, cy = x0 + 52, y0 + 24
        d.rectangle([cx - 22, cy - 13, cx + 22, cy + 13], outline=(120, 200, 140), width=2)
        d.rectangle([cx - 13, cy - 7, cx + 13, cy + 7], fill=(46, 160, 90))
        for i in range(5):
            px = cx - 16 + i * 8
            d.line([px, cy - 13, px, cy - 19], fill=(120, 200, 140), width=2)
            d.line([px, cy + 13, px, cy + 19], fill=(120, 200, 140), width=2)
        d.text((x0 + 92, y0 + 12), "NVIDIA", font=f_art, fill=(255, 255, 255))
        d.text((x0 + 92, y0 + 30), "SANTA CLARA HQ", font=f_art_s, fill=(170, 220, 180))
    elif kind == "tanker":
        d.rectangle([x0, y0, x0 + w, y0 + 48], fill=(18, 50, 74))
        d.rectangle([x0 + 30, y0 + 26, x0 + 200, y0 + 38], fill=(200, 90, 40))
        for bx in (46, 86, 126, 166):
            d.rectangle([x0 + bx, y0 + 14, x0 + bx + 32, y0 + 26], outline=(220, 220, 220), width=1)
        d.rectangle([x0 + 204, y0 + 18, x0 + 224, y0 + 38], fill=(240, 240, 240))
        for wx in range(0, w, 26):
            d.arc([x0 + wx, y0 + 40, x0 + wx + 24, y0 + 50], 0, 180, fill=(140, 190, 210), width=2)
    else:  # trophy
        d.rectangle([x0, y0, x0 + w, y0 + 48], fill=(20, 90, 60))
        cx, cy = x0 + 52, y0 + 24
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 2], fill=(240, 200, 60))
        d.rectangle([cx - 14, cy - 12, cx + 14, cy - 2], fill=(240, 200, 60))
        d.arc([cx - 22, cy - 14, cx - 8, cy + 2], 90, 270, fill=(240, 200, 60), width=3)
        d.arc([cx + 8, cy - 14, cx + 22, cy + 2], -90, 90, fill=(240, 200, 60), width=3)
        d.rectangle([cx - 3, cy + 2, cx + 3, cy + 12], fill=(240, 200, 60))
        d.rectangle([cx - 10, cy + 12, cx + 10, cy + 16], fill=(240, 200, 60))
        d.text((x0 + 92, y0 + 12), "AFCON 2025", font=f_art, fill=(255, 255, 255))
        d.text((x0 + 92, y0 + 30), "CHAMPIONS", font=f_art_s, fill=(220, 240, 210))
    # verification tag chip, top-right of the art panel
    tw = d.textlength(tag, font=f_tag)
    d.rounded_rectangle([x0 + w - 8 - tw - 8, y0 + 5, x0 + w - 8, y0 + 18], radius=3, fill=RED_DK)
    d.text((x0 + w - 8 - tw - 4, y0 + 7), tag, font=f_tag, fill=(255, 255, 255))

def draw_heroes(d, report):
    y0, h = 96, 142
    xs = [M, M + 326 + 11, M + 2 * (326 + 11)]
    for (num, head, deck, tag, _reg, _lo, _la, art), x0 in zip(HEROES, xs):
        d.rectangle([x0, y0, x0 + 326, y0 + h], fill=CARD_BG, outline=RULE, width=1)
        draw_hero_art(d, x0, y0, 326, art, tag)
        tx = x0 + 32
        ty = y0 + 54
        badge(d, x0 + 6, ty, "", num, size=20)
        hl = wrap(d, head, f_hero_h, 326 - 38)
        for i, ln in enumerate(hl[:2]):
            d.text((tx, ty + i * 19), ln, font=f_hero_h, fill=INK)
            report["hero_head_right"].append((num, tx + text_w(d, ln, f_hero_h), x0 + 326 - 6))
        dy = ty + len(hl[:2]) * 19 + 3
        dl = wrap(d, deck, f_hero_d, 326 - 38)
        for i, ln in enumerate(dl[:3]):
            d.text((tx, dy + i * 13), ln, font=f_hero_d, fill=INK_SOFT)
        report["hero_deck_lines"].append((num, len(dl)))

def draw_mids(d, report):
    y0, max_h = 242, 346
    cols = [(M, MIDS[:7]), (M + 494 + 12, MIDS[7:])]
    for x0, stories in cols:
        y = y0
        for (num, head, deck, tag, _reg, _lo, _la) in stories:
            tx = x0 + 30
            hl = wrap(d, head, f_mid_h, 494 - 38 - 56)
            dl = wrap(d, deck, f_mid_d, 494 - 38)
            ch = 3 + len(hl) * 16 + 1 + len(dl) * 12 + 2
            d.rectangle([x0, y, x0 + 494, y + ch], fill=CARD_BG, outline=RULE, width=1)
            badge(d, x0 + 6, y + 4, "", num, size=18)
            for i, ln in enumerate(hl):
                d.text((tx, y + 4 + i * 16), ln, font=f_mid_h, fill=INK)
                report["mid_head_right"].append((num, tx + text_w(d, ln, f_mid_h), x0 + 494 - 6))
            dy = y + 4 + len(hl) * 16 + 1
            for i, ln in enumerate(dl):
                d.text((tx, dy + i * 12), ln, font=f_mid_d, fill=INK_SOFT)
            report["mid_deck_lines"].append((num, len(dl)))
            draw_tag(d, x0 + 494 - 6, y + 5, tag)
            y += ch + 1
        if len(stories) == 6:
            # filler box so the right column ends level with the left
            fh = y0 + max_h - y
            if fh > 20:
                d.rectangle([x0, y, x0 + 494, y0 + max_h], fill=PAPER_DK, outline=RULE, width=1)
                note = "39 STORIES \u00b7 9 REGIONS \u2014 every story is numbered and pinned on the world map below."
                nl = wrap(d, note, f_mid_d, 494 - 24)
                for i, ln in enumerate(nl):
                    d.text((x0 + 12, y + 8 + i * 13), ln, font=f_mid_d, fill=INK_SOFT)
        report["mid_col_bottom"].append(y)

# ---------------------------------------------------------------- map
def project(lon, lat, mw, mh):
    x = (lon + 180.0) / 360.0 * mw
    y = (85.0 - lat) / 145.0 * mh
    return [x, y]

def spread_pins(pts, mw, mh, min_d=15.0):
    """Deterministic repulsion so clustered pins do not overlap."""
    pts = [p[:] for p in pts]
    for _ in range(60):
        moved = False
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx = pts[j][0] - pts[i][0]
                dy = pts[j][1] - pts[i][1]
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < min_d and dist > 0.01:
                    push = (min_d - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    pts[i][0] -= ux * push
                    pts[i][1] -= uy * push
                    pts[j][0] += ux * push
                    pts[j][1] += uy * push
                    moved = True
                elif dist <= 0.01:
                    pts[j][0] += 2.0
                    pts[j][1] += 2.0
                    moved = True
        for p in pts:
            p[0] = max(8.0, min(mw - 8.0, p[0]))
            p[1] = max(8.0, min(mh - 8.0, p[1]))
        if not moved:
            break
    return pts

def draw_map(d, img, report):
    mx, my, mw, mh = M, 606, 486, 190
    # land/sea on a box-sized layer, then paste (paste clips exactly)
    layer = Image.new("RGB", (mw, mh), SEA)
    ld = ImageDraw.Draw(layer)
    for poly in LAND_POLYS:
        pts = [tuple(project(lo, la, mw, mh)) for lo, la in poly]
        ld.polygon(pts, fill=LAND, outline=LAND_LINE)
    img.paste(layer, (mx, my))
    d.rectangle([mx, my, mx + mw, my + mh], outline=INK, width=2)
    # pins
    true_pts = [project(lo, la, mw, mh) for (_n, lo, la) in ALL_STORIES]
    disp_pts = spread_pins(true_pts, mw, mh)
    for (num, _lo, _la), tp, dp in zip(ALL_STORIES, true_pts, disp_pts):
        dx, dy = dp[0] - tp[0], dp[1] - tp[1]
        if (dx * dx + dy * dy) ** 0.5 > 6:
            d.line([mx + tp[0], my + tp[1], mx + dp[0], my + dp[1]], fill=INK_SOFT, width=1)
            d.ellipse([mx + tp[0] - 1.5, my + tp[1] - 1.5, mx + tp[0] + 1.5, my + tp[1] + 1.5], fill=INK_SOFT)
        px, py = mx + dp[0], my + dp[1]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=PIN_BG, outline=(255, 255, 255), width=1)
        t = str(num)
        tw = d.textlength(t, font=f_pin)
        d.text((px - tw / 2, py - 5), t, font=f_pin, fill=PIN_TX)
    report["map_box"] = (mx, my, mw, mh)

def draw_briefs(d, report):
    x0, y0 = 510, 606
    w = W - M - x0  # 502
    y = y0
    for (num, text, _reg, _lo, _la) in BRIEFS:
        lines = wrap(d, text, f_brief, w - 38)
        report["brief_lines"].append((num, len(lines)))
        badge(d, x0 + 6, y, "", num, size=16)
        d.text((x0 + 30, y + 2), lines[0], font=f_brief, fill=INK)
        if len(lines) > 1:
            d.text((x0 + 30, y + 15), lines[1], font=f_brief, fill=INK)
        y += 17 if len(lines) == 1 else 30
    report["briefs_bottom"] = y

def draw_date_check(d):
    x0, y0, w, h = M, 816, 486, 184
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(253, 244, 230), outline=RED, width=2)
    d.text((x0 + 10, y0 + 8), "DATE CHECK \u2014 NOT TUESDAY, LEFT OUT", font=f_sect, fill=RED)
    y = y0 + 30
    for name, note in DATE_CHECK:
        d.text((x0 + 10, y), name, font=f_dc_b, fill=INK)
        nw = d.textlength(name, font=f_dc_b)
        d.text((x0 + 10 + nw + 4, y), "\u2014 " + note, font=f_dc, fill=INK_SOFT)
        y += 16
    y += 4
    d.text((x0 + 10, y), "Every story above happened or was first reported", font=f_dc, fill=INK)
    y += 14
    d.text((x0 + 10, y), "on Tue 24 Nov 2026. Tags: CONFIRMED = official record;", font=f_dc, fill=INK)
    y += 14
    d.text((x0 + 10, y), "OFFICIAL = named authority; REPORTED = multiple outlets.", font=f_dc, fill=INK)

def main():
    report = {"hero_head_right": [], "mid_head_right": [], "hero_deck_lines": [],
              "mid_deck_lines": [], "brief_lines": [], "mid_col_bottom": [],
              "briefs_bottom": 0, "map_box": None}
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 10), title, font=f_title, fill=INK)
    date_line = "TUESDAY 24 NOVEMBER 2026  \u00b7  39 STORIES  \u00b7  9 REGIONS  \u00b7  ALL STORIES VERIFIED"
    dw = d.textlength(date_line, font=f_date)
    d.text(((W - dw) / 2, 54), date_line, font=f_date, fill=INK_SOFT)
    d.line([M, 68, W - M, 68], fill=INK, width=2)
    # stat strip
    sw = (CW - 3 * 8) // 4
    for i, s in enumerate(STATS):
        x0 = M + i * (sw + 8)
        d.rectangle([x0, 72, x0 + sw, 96], fill=CARD_BG, outline=RULE, width=1)
        tw = d.textlength(s, font=f_stat)
        d.text((x0 + (sw - tw) / 2, 79), s, font=f_stat, fill=RED_DK)
    draw_heroes(d, report)
    draw_mids(d, report)
    # section titles over map and briefs
    d.text((M, 592), "WORLD MAP \u2014 EVERY STORY PINNED", font=f_sect, fill=INK)
    d.text((510, 592), "THE REST OF THE DAY \u2014 23 BRIEFS", font=f_sect, fill=INK)
    draw_map(d, img, report)
    draw_briefs(d, report)
    d.text((M, 800), "39 stories pinned \u2014 numbers match the list.", font=f_foot, fill=INK_SOFT)
    draw_date_check(d)
    foot = "Compiled from Reuters \u00b7 AP \u00b7 WSJ \u00b7 Bloomberg \u00b7 Conference Board \u00b7 CMSA \u00b7 Al Jazeera \u2014 all stories verified against original sources \u00b7 Tue 24 Nov 2026"
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 1006), foot, font=f_foot, fill=INK_SOFT)
    img.save(OUT, format="PNG", optimize=True)

    # ---- checks ------------------------------------------------------
    problems = []
    for num, right, limit in report["hero_head_right"] + report["mid_head_right"]:
        if right > limit:
            problems.append(f"headline #{num} right edge {right:.1f} > card limit {limit}")
    for num, n in report["hero_deck_lines"]:
        if n > 3:
            problems.append(f"hero #{num} deck wraps to {n} lines (max 3)")
    for num, n in report["mid_deck_lines"]:
        if n > 2:
            problems.append(f"mid #{num} deck wraps to {n} lines (max 2)")
    for num, n in report["brief_lines"]:
        if n > 1:
            problems.append(f"brief #{num} wraps to {n} lines (max 1)")
    if report["briefs_bottom"] > 1000:
        problems.append(f"briefs bottom {report['briefs_bottom']} > 1000")
    mx, my, mw, mh = report["map_box"]
    px = img.load()
    outside = 0
    for yy in range(H):
        for xx in range(W):
            if not (mx <= xx < mx + mw and my <= yy < my + mh):
                if px[xx, yy] == LAND:
                    outside += 1
    if outside:
        problems.append(f"map: {outside} land-coloured pixels outside the box")
    print("mid column bottoms:", report["mid_col_bottom"], " briefs bottom:", report["briefs_bottom"])
    print("PROBLEMS:" if problems else "ALL CHECKS PASSED")
    for p in problems:
        print(" -", p)
    print("saved", OUT)

if __name__ == "__main__":
    main()
