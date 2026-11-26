#!/usr/bin/env python3
"""Render the News 25 front page (Wednesday 25 November 2026).

Draws a 1024x1024 front page with PIL: navy header naming the day,
three illustrated hero cards for the biggest stories, a dotted world
map with numbered pins, a row of flag cards, a UTC timeline strip, a
numbered list of all 29 verified stories, and a DATE CHECK box.
Run: python3 render.py  ->  writes entry.png next to this file.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
NAVY = (11, 42, 91)
NAVY_DARK = (8, 30, 66)
GOLD = (212, 160, 32)
RED = (198, 32, 32)
RED_DARK = (160, 20, 20)
INK = (24, 28, 36)
GREY = (90, 100, 115)
LIGHT = (234, 240, 247)
MAP_DOT = (150, 175, 205)
WHITE = (255, 255, 255)
GREEN = (18, 130, 70)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap_text(d, text, fnt, max_w):
    """Split text into lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centered(d, cx, y, text, fnt, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ---- continent outlines (lon, lat), simplified but recognisable ----
NORTH_AMERICA = [(-168, 66), (-155, 71), (-140, 70), (-130, 71), (-120, 72),
    (-110, 73), (-100, 73), (-95, 80), (-85, 80), (-80, 73), (-75, 72),
    (-65, 62), (-60, 55), (-55, 47), (-60, 45), (-65, 44), (-70, 42),
    (-75, 35), (-80, 32), (-81, 26), (-85, 29), (-90, 21), (-95, 19),
    (-97, 16), (-100, 20), (-105, 20), (-110, 23), (-115, 29), (-120, 34),
    (-125, 40), (-125, 49), (-130, 55), (-140, 60), (-150, 59), (-160, 58),
    (-165, 60), (-168, 66)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-25, 70),
    (-35, 74), (-50, 76), (-60, 76), (-65, 70), (-58, 64)]
SOUTH_AMERICA = [(-79, 9), (-77, 7), (-72, 11), (-64, 10), (-60, 8),
    (-52, 5), (-50, 0), (-44, -3), (-35, -6), (-35, -10), (-38, -15),
    (-40, -22), (-48, -27), (-52, -32), (-58, -35), (-62, -40),
    (-65, -45), (-68, -50), (-70, -54), (-74, -52), (-73, -44),
    (-73, -36), (-72, -28), (-70, -20), (-77, -12), (-80, -5),
    (-81, 0), (-80, 5), (-79, 9)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (0, 46),
    (0, 49), (3, 51), (5, 53), (8, 55), (8, 57), (10, 59), (12, 56),
    (18, 56), (21, 55), (24, 58), (26, 59), (28, 60), (30, 62), (30, 66),
    (25, 70), (20, 70), (18, 69), (15, 68), (12, 65), (10, 62), (5, 60),
    (5, 58), (0, 55), (-3, 53), (-5, 50), (-5, 48), (-10, 43), (-10, 36)]
AFRICA = [(-17, 15), (-16, 20), (-15, 25), (-13, 28), (-10, 31), (-6, 33),
    (-5, 35), (0, 36), (5, 37), (10, 37), (15, 32), (20, 32), (25, 31),
    (30, 31), (32, 31), (35, 28), (35, 23), (37, 18), (39, 15), (43, 12),
    (48, 11), (51, 11), (48, 5), (44, 0), (41, -5), (40, -10), (37, -15),
    (35, -20), (33, -25), (31, -29), (28, -33), (25, -34), (20, -35),
    (17, -32), (15, -27), (13, -22), (12, -17), (13, -12), (12, -6),
    (9, -1), (9, 4), (4, 6), (-2, 5), (-8, 4), (-13, 8), (-17, 12),
    (-17, 15)]
ASIA = [(28, 70), (35, 68), (40, 68), (45, 68), (50, 69), (55, 69),
    (60, 69), (65, 70), (70, 71), (75, 72), (80, 73), (85, 74), (90, 75),
    (95, 76), (100, 76), (105, 77), (110, 76), (115, 74), (120, 73),
    (125, 72), (130, 72), (135, 71), (140, 72), (145, 72), (150, 70),
    (155, 70), (160, 69), (165, 67), (170, 66), (178, 65), (175, 62),
    (170, 60), (165, 60), (160, 55), (158, 52), (155, 55), (150, 59),
    (145, 59), (142, 55), (140, 50), (138, 45), (135, 43), (132, 43),
    (130, 42), (128, 40), (126, 38), (124, 40), (122, 38), (120, 35),
    (118, 32), (115, 28), (112, 22), (110, 20), (108, 18), (106, 10),
    (104, 8), (102, 8), (100, 10), (98, 12), (97, 16), (95, 16),
    (93, 18), (91, 22), (89, 22), (87, 22), (85, 20), (83, 18), (80, 15),
    (78, 10), (76, 8), (75, 10), (73, 16), (72, 20), (70, 22), (68, 23),
    (66, 25), (64, 25), (62, 25), (60, 25), (58, 26), (56, 26), (54, 26),
    (52, 27), (50, 29), (48, 30), (46, 29), (44, 29), (42, 30), (40, 32),
    (38, 35), (36, 36), (34, 36), (32, 36), (30, 36), (28, 38), (27, 40),
    (28, 44), (30, 46), (32, 50), (35, 55), (38, 60), (40, 65), (35, 68),
    (30, 70), (28, 70)]
AUSTRALIA = [(113, -22), (114, -28), (115, -32), (115, -35), (118, -35),
    (122, -34), (126, -32), (129, -32), (132, -32), (135, -35), (138, -35),
    (140, -38), (144, -38), (147, -39), (150, -37), (153, -32), (153, -27),
    (150, -23), (147, -19), (144, -15), (142, -11), (141, -13), (139, -15),
    (136, -15), (135, -12), (133, -12), (131, -12), (129, -14), (127, -14),
    (125, -14), (122, -17), (120, -20), (117, -20), (114, -21), (113, -22)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
    (141, 38), (141, 41), (142, 43), (143, 44), (144, 44), (142, 42),
    (140, 40), (139, 38), (137, 37), (135, 35), (133, 34), (131, 33),
    (130, 31)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 54), (1, 51),
    (-2, 50), (-5, 50)]
INDONESIA = [(95, 5), (98, 5), (100, 0), (102, -3), (104, -4), (106, -6),
    (108, -7), (110, -7), (112, -7), (114, -8), (116, -9), (118, -9),
    (120, -10), (122, -9), (124, -10), (126, -9), (128, -8), (130, -7),
    (132, -4), (134, -3), (136, -2), (138, -2), (140, -3), (141, -4),
    (140, -6), (138, -8), (136, -8), (134, -6), (132, -5), (130, -3),
    (128, -2), (126, 0), (124, 1), (122, 1), (120, 0), (118, 1), (116, 0),
    (114, 0), (112, 0), (110, 0), (108, 1), (106, 2), (104, 3), (102, 4),
    (100, 5), (98, 5), (95, 5)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EUROPE, AFRICA,
              ASIA, AUSTRALIA, JAPAN, UK, INDONESIA]

# story pins: (story no, lat, lon, nudge dx, nudge dy)
PINS = [
    (1, 38.9, -77.0, 0, 0),      # Washington — tariffs
    (3, 37.5, 127.0, 0, 0),      # Seoul — Kospi
    (5, 39.8, 98.5, 0, 0),       # Jiuquan — Shenzhou
    (6, 51.5, -0.1, 0, 0),       # London — energy cap
    (7, 30.0, 31.2, 0, 0),       # Cairo — tanker fire
    (8, -6.6, 106.8, 0, 0),      # Bogor — mine flood
    (9, 26.5, 56.3, -2, -13),    # Hormuz — tankers hit mines
    (10, 26.6, 50.2, 0, 13),     # Ras Tanura — refinery strike
    (11, 11.8, 34.4, 0, 0),      # Damazin — Sudan strikes
    (14, 23.8, 90.4, 0, 0),      # Dhaka — garment wage
    (15, 41.9, 12.5, 0, 0),      # Vatican — Pope on COP31
    (16, -9.6, 160.2, 0, 0),     # Solomon Islands — treaty
    (20, 55.8, 37.6, 0, 0),      # Moscow — Lukoil sale
]

STORIES = [
    "US tariffs on 14 partners — China up to 20%",
    "US hits Brazil: 10% duty on Embraer jets",
    "Kospi -6.2% to 4,697 as AI doubts return",
    "Taiex -4.8%, Nikkei -2.8% in chip rout",
    "Shenzhou-24 docks; first Pakistani in orbit",
    "UK energy cap +26% to £2,166 from Jan",
    "Cairo tanker fire kills 31, injures 21",
    "West Java mine: 9 bodies found, 17 trapped",
    "Two tankers hit mines in Hormuz, explode",
    "Houthis claim Ras Tanura strike; oil $93",
    "Sudan RSF drone strikes kill 19",
    "US GDP revised to 4.3%; PCE inflation 3.8%",
    "Nvidia -3.9%; Nasdaq slides in AI selloff",
    "Bangladesh garment wage +36% to $139",
    "Pope decries COP31 climate talks failure",
    "Solomon Islands–Australia treaty bars bases",
    "Macy's 100th parade postponed to Saturday",
    "Second judge blocks birthright order",
    "US famine monitor halts reporting",
    "Lukoil assets sold to Boehly-led group",
    "Nigeria seizes $200m meth; 5 Mexicans held",
    "UN evacuates Ebola workers in E. Congo",
    "Venice Biennale prizes: Nick Cave, India",
    "BBC: 490,334 Russian soldiers killed",
    "Eurostar disrupted by union strikes",
    "BBC journalists vote to strike over cuts",
    "Poland plans no-fly zone on east border",
    "US tells citizens to leave Iran at once",
    "CIA and ODNI hit by cyber breach",
]

TIMELINE = [
    ("00:18", "Shenzhou-24 launches"),
    ("03:56", "Docks at Tiangong"),
    ("06:30", "Kospi closes -6.2%"),
    ("09:46", "Tankers hit mines"),
    ("13:30", "US GDP 4.3%, PCE 3.8%"),
    ("23:08", "Macy's parade postponed"),
]


def draw_ship(d, x, y, w, h):
    # sea + sky
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 245))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(46, 110, 180))
    # hull
    d.polygon([(x + 18, y + h - 52), (x + w - 18, y + h - 52),
               (x + w - 42, y + h - 26), (x + 42, y + h - 26)],
              fill=(30, 60, 110))
    # containers
    cols = [(198, 32, 32), (212, 160, 32), (18, 130, 70), (198, 32, 32),
            (30, 90, 160)]
    cw = (w - 90) // 5
    for i, c in enumerate(cols):
        d.rectangle([x + 48 + i * cw, y + h - 78, x + 48 + (i + 1) * cw - 3,
                     y + h - 52], fill=c)
    # bridge + funnel
    d.rectangle([x + w - 58, y + h - 96, x + w - 34, y + h - 78],
                fill=(240, 240, 240))
    d.rectangle([x + 30, y + h - 92, x + 52, y + h - 78], fill=(198, 32, 32))
    # gold 20% badge
    bx, by, br = x + w - 52, y + 30, 30
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=GOLD,
              outline=WHITE, width=3)
    d.text((bx - d.textlength("20%", font=font(20, True)) / 2, by - 13),
           "20%", font=font(20, True), fill=NAVY_DARK)


def draw_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 16, 44))
    # stars
    for sx, sy, r in [(14, 12, 2), (52, 26, 1), (96, 10, 2), (140, 30, 1),
                      (180, 14, 2), (220, 26, 1), (260, 12, 2), (300, 34, 1),
                      (30, 52, 1), (250, 52, 2), (120, 44, 1), (200, 48, 1)]:
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=WHITE)
    # station: core + panels
    d.rectangle([x + 196, y + 22, x + 296, y + 42], fill=(150, 160, 175))
    d.rectangle([x + 176, y + 26, x + 196, y + 38], fill=(40, 90, 180))
    d.rectangle([x + 296, y + 26, x + 316, y + 38], fill=(40, 90, 180))
    d.ellipse([x + 238, y + 18, x + 254, y + 34], fill=GOLD)
    # rocket body
    rx, ry = x + 78, y + 30
    d.polygon([(rx + 12, ry), (rx + 28, ry), (rx + 28, ry + 58),
               (rx + 12, ry + 58)], fill=(240, 240, 240))
    d.polygon([(rx + 12, ry), (rx + 20, ry - 16), (rx + 28, ry)],
              fill=RED)
    d.polygon([(rx + 12, ry + 44), (rx, ry + 66), (rx + 12, ry + 58)],
              fill=RED)
    d.polygon([(rx + 28, ry + 44), (rx + 40, ry + 66), (rx + 28, ry + 58)],
              fill=RED)
    d.ellipse([rx + 14, ry + 16, rx + 26, ry + 28], fill=(40, 120, 200))
    # flame
    d.polygon([(rx + 12, ry + 58), (rx + 28, ry + 58), (rx + 20, ry + 88)],
              fill=(255, 170, 30))
    d.polygon([(rx + 15, ry + 58), (rx + 25, ry + 58), (rx + 20, ry + 76)],
              fill=(255, 220, 80))


def draw_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 244, 244))
    # grid
    for gy in range(y + 16, y + h - 8, 18):
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(225, 200, 200), width=1)
    # falling line
    pts = [(x + 14, y + 18), (x + 60, y + 26), (x + 110, y + 22),
           (x + 160, y + 44), (x + 210, y + 58), (x + 260, y + 52),
           (x + 306, y + 88)]
    d.line(pts, fill=RED, width=5, joint="curve")
    # arrow head
    d.polygon([(x + 306, y + 88), (x + 292, y + 82), (x + 300, y + 96)],
              fill=RED)
    # big -6.2% label
    txt = "-6.2%"
    f = font(30, True)
    d.text((x + w - d.textlength(txt, font=f) - 14, y + h - 44), txt,
           font=f, fill=RED_DARK)


def draw_flag(d, x, y, w, h, kind):
    d.rectangle([x, y, x + w, y + h], outline=(120, 130, 145), width=1)
    if kind == "USA":
        for i in range(7):
            d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7],
                        fill=(178, 34, 52) if i % 2 == 0 else WHITE)
        d.rectangle([x, y, x + w * 2 // 5, y + h * 4 // 7], fill=(30, 50, 110))
        for sy in range(3):
            for sx in range(4):
                d.ellipse([x + 6 + sx * 12, y + 5 + sy * 9,
                           x + 10 + sx * 12, y + 9 + sy * 9], fill=WHITE)
    elif kind == "CHN":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.polygon(star_points(x + 16, y + 14, 9, 4), fill=(255, 220, 60))
    elif kind == "KOR":
        d.rectangle([x, y, x + w, y + h], fill=WHITE)
        d.ellipse([x + w // 2 - 13, y + h // 2 - 13, x + w // 2 + 13,
                   y + h // 2 + 13], fill=(205, 46, 58))
        d.pieslice([x + w // 2 - 13, y + h // 2 - 13, x + w // 2 + 13,
                    y + h // 2 + 13], start=180, end=360, fill=(205, 46, 58))
        d.pieslice([x + w // 2 - 13, y + h // 2 - 13, x + w // 2 + 13,
                    y + h // 2 + 13], start=0, end=180, fill=(0, 71, 160))
        d.rectangle([x + 5, y + 5, x + 18, y + 8], fill=INK)
        d.rectangle([x + w - 18, y + 5, x + w - 5, y + 8], fill=INK)
        d.rectangle([x + 5, y + h - 8, x + 18, y + h - 5], fill=INK)
        d.rectangle([x + w - 18, y + h - 8, x + w - 5, y + h - 5], fill=INK)
    elif kind == "GBR":
        d.rectangle([x, y, x + w, y + h], fill=(0, 36, 125))
        d.line([(x, y), (x + w, y + h)], fill=WHITE, width=7)
        d.line([(x + w, y), (x, y + h)], fill=WHITE, width=7)
        d.line([(x + w // 2, y), (x + w // 2, y + h)], fill=WHITE, width=11)
        d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=WHITE, width=11)
        d.line([(x + w // 2, y), (x + w // 2, y + h)], fill=(200, 16, 46),
               width=5)
        d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(200, 16, 46),
               width=5)
    elif kind == "PAK":
        d.rectangle([x, y, x + w, y + h], fill=(0, 66, 37))
        d.rectangle([x, y, x + w // 4, y + h], fill=WHITE)
        d.ellipse([x + w // 2 - 2, y + h // 2 - 12, x + w // 2 + 22,
                   y + h // 2 + 12], fill=WHITE)
        d.ellipse([x + w // 2 + 3, y + h // 2 - 10, x + w // 2 + 23,
                   y + h // 2 + 10], fill=(0, 66, 37))
        d.polygon(star_points(x + w // 2 + 26, y + h // 2 - 2, 5, 2),
                  fill=WHITE)
    elif kind == "EGY":
        d.rectangle([x, y, x + w, y + h // 3], fill=(206, 17, 38))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=WHITE)
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=INK)
    elif kind == "IDN":
        d.rectangle([x, y, x + w, y + h // 2], fill=(215, 0, 0))
        d.rectangle([x, y + h // 2, x + w, y + h], fill=WHITE)
    elif kind == "SAU":
        d.rectangle([x, y, x + w, y + h], fill=(0, 106, 78))
        d.rectangle([x + 12, y + h // 2 - 7, x + w - 12, y + h // 2 - 3],
                    fill=WHITE)
        d.rectangle([x + 16, y + h // 2 + 5, x + w - 16, y + h // 2 + 8],
                    fill=WHITE)
    elif kind == "SDN":
        d.rectangle([x, y, x + w, y + h // 3], fill=(210, 16, 52))
        d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=WHITE)
        d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=INK)
        d.polygon([(x, y), (x + w // 3, y + h // 2), (x, y + h)],
                  fill=(0, 114, 41))
    elif kind == "BGD":
        d.rectangle([x, y, x + w, y + h], fill=(0, 106, 78))
        d.ellipse([x + w // 2 - 16, y + h // 2 - 13, x + w // 2 + 8,
                   y + h // 2 + 13], fill=(244, 42, 65))


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=4)

    # ---------- header ----------
    d.rectangle([4, 4, W - 5, 88], fill=NAVY)
    centered(d, W // 2, 12, "WEDNESDAY 25 NOVEMBER 2026",
             font(38, True), WHITE)
    d.rectangle([W // 2 - 150, 62, W // 2 + 150, 64], fill=GOLD)
    centered(d, W // 2, 68, "THE WORLD IN ONE DAY  •  29 STORIES",
             font(15, True), (255, 214, 90))

    # ---------- hero cards ----------
    heroes = [
        ("US HITS 14 NATIONS WITH NEW TARIFFS",
         "China up to 20% — 40% if the trade truce fails. Brazil jets hit too.",
         draw_ship),
        ("FIRST PAKISTANI ASTRONAUT DOCKS AT TIANGONG",
         "Shenzhou-24 docks 03:56 UTC; Zeeshan Ali is the first foreign visitor.",
         draw_rocket),
        ("KOSPI PLUNGES 6.2% AS AI DOUBTS RETURN",
         "Samsung -9.9%, SK Hynix -11.1%. Taiex -4.8%, Nikkei -2.8%.",
         draw_chart),
    ]
    card_y, card_h, card_w, gap = 96, 200, 322, 8
    for i, (title, body, art) in enumerate(heroes):
        cx = 8 + i * (card_w + gap)
        d.rectangle([cx, card_y, cx + card_w, card_y + card_h],
                    fill=(248, 250, 253), outline=(180, 195, 215), width=2)
        art(d, cx + 2, card_y + 2, card_w - 4, 108)
        ty = card_y + 116
        for line in wrap_text(d, title, font(16, True), card_w - 16):
            d.text((cx + 8, ty), line, font=font(16, True), fill=NAVY_DARK)
            ty += 19
        for line in wrap_text(d, body, font(12), card_w - 16):
            d.text((cx + 8, ty), line, font=font(12), fill=INK)
            ty += 15

    # ---------- dotted world map ----------
    map_x0, map_y0, map_x1, map_y1 = 24, 330, 1000, 536
    d.text((map_x0, 304), "WHERE IT HAPPENED", font=font(14, True),
           fill=NAVY_DARK)
    d.text((W - 24 - d.textlength("RED PINS = STORY NUMBERS BELOW",
                                  font=font(12, True)), 306),
           "RED PINS = STORY NUMBERS BELOW", font=font(12, True), fill=RED)
    d.rectangle([map_x0, map_y0, map_x1, map_y1], fill=(245, 248, 252),
                outline=(180, 195, 215), width=1)

    def project(lon, lat):
        x = map_x0 + (lon + 170) / 360.0 * (map_x1 - map_x0)
        y = map_y0 + (78 - lat) / 136.0 * (map_y1 - map_y0)
        return x, y

    step = 7
    gx = map_x0 + 4
    while gx < map_x1 - 2:
        gy = map_y0 + 4
        while gy < map_y1 - 2:
            lon = -170 + (gx - map_x0) / (map_x1 - map_x0) * 360.0
            lat = 78 - (gy - map_y0) / (map_y1 - map_y0) * 136.0
            if any(point_in_polygon(lon, lat, poly) for poly in CONTINENTS):
                d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=MAP_DOT)
            gy += step
        gx += step

    for no, lat, lon, ndx, ndy in PINS:
        px, py = project(lon, lat)
        px += ndx
        py += ndy
        r = 10
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=WHITE, width=2)
        t = str(no)
        f = font(11, True) if len(t) == 1 else font(9, True)
        d.text((px - d.textlength(t, font=f) / 2,
                py - 8 if len(t) == 1 else py - 7), t, font=f, fill=WHITE)

    # ---------- flag cards ----------
    flags = [("USA", "USA"), ("CHN", "CHINA"), ("KOR", "S. KOREA"),
             ("GBR", "BRITAIN"), ("PAK", "PAKISTAN"), ("EGY", "EGYPT"),
             ("IDN", "INDONESIA"), ("SAU", "S. ARABIA"), ("SDN", "SUDAN"),
             ("BGD", "BANGLADESH")]
    fy = 552
    for i, (kind, label) in enumerate(flags):
        fx = 24 + i * 98
        draw_flag(d, fx, fy, 88, 50, kind)
        centered(d, fx + 44, fy + 54, label, font(10, True), INK)

    # ---------- UTC timeline ----------
    d.text((24, 636), "THE DAY IN UTC", font=font(14, True), fill=NAVY_DARK)
    line_y = 668
    d.line([(130, line_y), (996, line_y)], fill=NAVY, width=3)
    slot_w = (996 - 130) / 6
    for i, (t, label) in enumerate(TIMELINE):
        cx = 130 + slot_w * (i + 0.5)
        d.ellipse([cx - 6, line_y - 6, cx + 6, line_y + 6], fill=RED,
                  outline=WHITE, width=2)
        centered(d, cx, 640, t, font(13, True), RED_DARK)
        ly = line_y + 10
        for ln in wrap_text(d, label, font(10), 130):
            centered(d, cx, ly, ln, font(10), INK)
            ly += 12

    # ---------- story list ----------
    d.rectangle([8, 700, W - 9, 724], fill=LIGHT)
    centered(d, W // 2, 704, "ALL 29 STORIES — WEDNESDAY 25 NOVEMBER 2026",
             font(14, True), NAVY_DARK)
    col_x = [24, 528]
    col_w = [480, 472]
    ly = 732
    f_num, f_txt = font(13, True), font(13)
    for i, story in enumerate(STORIES):
        col = 0 if i < 17 else 1
        row = i if i < 17 else i - 17
        x = col_x[col]
        y = ly + row * 14
        num = f"{i + 1}."
        d.text((x, y), num, font=f_num, fill=NAVY)
        d.text((x + 26, y), story, font=f_txt, fill=INK)

    # ---------- DATE CHECK footer ----------
    d.rectangle([4, 970, W - 5, 1019], fill=NAVY)
    check = ("DATE CHECK — Every story above happened or was first reported "
             "on Wednesday 25 November 2026. No story from another day.")
    f_check = font(13, True)
    if d.textlength(check, font=f_check) <= W - 32:
        centered(d, W // 2, 988, check, f_check, WHITE)
    else:
        lines = wrap_text(d, check, f_check, W - 32)
        yy = 976
        for ln in lines:
            centered(d, W // 2, yy, ln, f_check, WHITE)
            yy += 17

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {os.path.getsize(OUT)} bytes {img.size}")


if __name__ == "__main__":
    main()
