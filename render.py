#!/usr/bin/env python3
"""News 25 front page — Wednesday 25 November 2026.

Renders a single 1024x1024 PNG summarising world news from 25 Nov 2026
only: navy header, 3 illustrated hero cards, dotted world map with
numbered pins, 10 flag cards, a UTC timeline, a numbered list of 29
stories, and a DATE CHECK footer. Every story below happened or was first
reported on 25 November 2026. No story from another day.
"""

import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

NAVY = (11, 42, 91)
NAVY_DARK = (8, 30, 66)
GOLD = (212, 175, 55)
GOLD_DARK = (180, 145, 35)
INK = (22, 30, 44)
MUTED = (70, 82, 100)
RED = (200, 30, 30)
RED_DARK = (160, 20, 20)
LIGHT_BAR = (232, 238, 245)
MAP_BG = (238, 243, 248)
DOT = (178, 196, 216)
BORDER = (196, 210, 226)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    try:
        return ImageFont.truetype(FONT_DIR + name, size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = font("DejaVuSans-Bold.ttf", 34)
F_SUB = font("DejaVuSans-Bold.ttf", 15)
F_SECTION = font("DejaVuSans-Bold.ttf", 14)
F_NOTE = font("DejaVuSans-Bold.ttf", 11)
F_HERO = font("DejaVuSans-Bold.ttf", 16)
F_HERO_SUB = font("DejaVuSans.ttf", 11)
F_FLAG = font("DejaVuSans-Bold.ttf", 11)
F_TIME = font("DejaVuSans-Bold.ttf", 12)
F_EVENT = font("DejaVuSans.ttf", 11)
F_LIST = font("DejaVuSans.ttf", 14)
F_LIST_NUM = font("DejaVuSans-Bold.ttf", 14)
F_FOOT = font("DejaVuSans-Bold.ttf", 13)
F_PIN = font("DejaVuSans-Bold.ttf", 10)
F_BADGE = font("DejaVuSans-Bold.ttf", 20)
F_CHART = font("DejaVuSans-Bold.ttf", 26)

STORIES = [
    "US tariffs on 14 partners — China up to 20%",
    "US hits Brazil too: 10% duty on Embraer jets",
    "Kospi -6.2% to 4,697 as AI doubts return",
    "Taiex -4.8%, Nikkei -2.8% in chip rout",
    "Shenzhou-24 docks; first Pakistani in orbit",
    "UK energy cap +26% to £2,166 from January",
    "Cairo tanker fire kills 31, injures 21",
    "West Java mine: 9 dead, 17 still trapped",
    "Two tankers hit mines in Hormuz, explode",
    "Houthis claim Ras Tanura strike; oil $93",
    "Sudan RSF drone strikes kill 19 in Blue Nile",
    "US GDP revised to 4.3%; PCE inflation 3.8%",
    "Nvidia -3.9%; Nasdaq slides as AI selloff resumes",
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

# Dotted-map landmasses as ellipses (cx, cy, rx, ry) in absolute pixels.
ELLIPSES = [
    (127, 315, 60, 10), (268, 318, 80, 12), (252, 344, 75, 14),
    (257, 362, 28, 8), (390, 304, 30, 10),           # N America, Greenland
    (344, 385, 35, 12), (363, 411, 28, 25),          # S America
    (539, 329, 55, 12), (552, 313, 25, 10), (498, 325, 6, 8),  # Europe, UK
    (660, 320, 70, 11),                              # W Russia
    (544, 360, 60, 12), (580, 399, 45, 28),          # Africa
    (590, 352, 28, 10), (600, 378, 30, 14), (535, 372, 35, 14),  # Egypt, Sudan, W Africa
    (810, 314, 180, 12), (702, 333, 55, 10),         # Siberia, C Asia
    (788, 350, 55, 16), (729, 366, 20, 14),          # China, India
    (788, 370, 20, 12), (645, 356, 42, 14),          # SE Asia, Middle East
    (829, 390, 55, 7), (880, 343, 12, 10),           # Indonesia, Japan
    (872, 417, 50, 14), (978, 435, 10, 8),           # Australia, NZ
]

# Map pins: story number -> (x, y) on the map.
PINS = {
    1: (303, 342), 5: (777, 341), 6: (512, 328), 7: (596, 353),
    8: (802, 395), 9: (668, 350), 10: (640, 366), 11: (605, 374),
    20: (614, 322), 21: (532, 377), 22: (590, 390), 23: (545, 335),
    27: (574, 327),
}

TIMELINE = [
    ("00:18", "Shenzhou-24 launches"),
    ("03:56", "Docks at Tiangong"),
    ("06:30", "Kospi closes -6.2%"),
    ("09:46", "Tankers hit mines"),
    ("13:30", "US GDP 4.3%, PCE 3.8%"),
    ("23:08", "Macy's parade postponed"),
]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def centred(draw, cx, y, s, f, fill):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_header(draw):
    draw.rectangle([0, 0, W, 88], fill=NAVY)
    draw.rectangle([0, 86, W, 88], fill=GOLD)
    centred(draw, W // 2, 14, "WEDNESDAY 25 NOVEMBER 2026", F_TITLE, (255, 255, 255))
    bar_w = 560
    draw.rectangle([(W - bar_w) // 2, 58, (W + bar_w) // 2, 61], fill=GOLD)
    centred(draw, W // 2, 66, "THE WORLD IN ONE DAY  •  29 STORIES", F_SUB, GOLD)


def draw_ship(draw, x0, y0):
    # Sky + sea
    draw.rectangle([x0, y0, x0 + 320, y0 + 98], fill=(207, 232, 245))
    draw.rectangle([x0, y0 + 66, x0 + 320, y0 + 98], fill=(47, 127, 193))
    draw.rectangle([x0, y0 + 66, x0 + 320, y0 + 70], fill=(90, 165, 215))
    # Sun glint
    draw.ellipse([x0 + 20, y0 + 8, x0 + 52, y0 + 40], fill=(255, 236, 160))
    draw.ellipse([x0 + 26, y0 + 14, x0 + 46, y0 + 34], fill=(255, 244, 190))
    # Containers, back row (darker) then front row
    cols = [(178, 52, 40), (232, 176, 10), (38, 140, 80), (38, 96, 168), (200, 60, 45)]
    for i, c in enumerate(cols):
        cx = x0 + 42 + i * 48
        draw.rectangle([cx, y0 + 26, cx + 44, y0 + 52], fill=tuple(v // 2 + 40 for v in c))
    for i, c in enumerate(cols):
        cx = x0 + 42 + i * 48
        draw.rectangle([cx, y0 + 30, cx + 44, y0 + 56], fill=c)
        draw.rectangle([cx, y0 + 30, cx + 44, y0 + 34], fill=(255, 255, 255))
    # Hull with shading
    draw.polygon([(x0 + 18, y0 + 56), (x0 + 302, y0 + 56), (x0 + 288, y0 + 82),
                  (x0 + 34, y0 + 82)], fill=(22, 50, 79))
    draw.polygon([(x0 + 18, y0 + 56), (x0 + 302, y0 + 56), (x0 + 300, y0 + 62),
                  (x0 + 20, y0 + 62)], fill=(60, 105, 150))
    draw.rectangle([x0 + 18, y0 + 76, x0 + 292, y0 + 82], fill=(12, 32, 54))
    # Bridge tower
    draw.rectangle([x0 + 262, y0 + 30, x0 + 288, y0 + 56], fill=(240, 244, 248))
    draw.rectangle([x0 + 264, y0 + 34, x0 + 286, y0 + 42], fill=(22, 50, 79))
    # Waves
    for wx in range(x0 + 10, x0 + 310, 34):
        draw.arc([wx, y0 + 84, wx + 26, y0 + 96], 180, 360, fill=(255, 255, 255), width=2)
    # 20% badge
    bx, by = x0 + 288, y0 + 18
    draw.ellipse([bx - 27, by - 27, bx + 27, by + 27], fill=(0, 0, 0, 0), outline=(150, 115, 20), width=2)
    draw.ellipse([bx - 26, by - 26, bx + 26, by + 26], fill=(240, 200, 60))
    draw.ellipse([bx - 26, by - 26, bx + 26, by + 26], outline=(150, 115, 20), width=2)
    centred(draw, bx, by - 13, "20%", F_BADGE, NAVY)


def draw_space(img, x0, y0):
    # Rendered on its own 320x98 panel so the big Earth arc is clipped
    # to the card and can never spill over the neighbouring hero cards.
    sub = Image.new("RGB", (320, 98), (13, 27, 51))
    d = ImageDraw.Draw(sub)
    rng = random.Random(25)
    for _ in range(46):
        sx = rng.randint(4, 316)
        sy = rng.randint(4, 94)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))
    # Earth arc along the bottom (clipped by the panel edge)
    d.ellipse([-60, 78, 380, 210], fill=(38, 110, 200))
    d.ellipse([-60, 78, 380, 196], fill=(70, 150, 225))
    # Space station (top right)
    d.rectangle([210, 26, 300, 38], fill=(160, 170, 185))
    d.rectangle([210, 26, 300, 30], fill=(200, 210, 225))
    d.rectangle([196, 28, 210, 36], fill=(43, 96, 168))
    d.rectangle([300, 28, 314, 36], fill=(43, 96, 168))
    d.ellipse([248, 22, 262, 42], fill=(220, 228, 238))
    # Rocket (centre left)
    rx, ry = 108, 30
    d.polygon([(rx + 8, ry), (rx + 20, ry + 16), (rx - 4, ry + 16)], fill=(200, 40, 40))
    d.rectangle([rx - 4, ry + 16, rx + 20, ry + 62], fill=(240, 244, 248))
    d.rectangle([rx - 4, ry + 16, rx + 2, ry + 62], fill=(200, 210, 225))
    d.ellipse([rx + 2, ry + 30, rx + 14, ry + 42], fill=(43, 96, 168))
    d.ellipse([rx + 5, ry + 33, rx + 11, ry + 39], fill=(150, 205, 240))
    d.polygon([(rx - 4, ry + 62), (rx - 12, ry + 74), (rx - 4, ry + 70)], fill=(200, 40, 40))
    d.polygon([(rx + 20, ry + 62), (rx + 28, ry + 74), (rx + 20, ry + 70)], fill=(200, 40, 40))
    # Flame
    d.polygon([(rx + 2, ry + 62), (rx + 14, ry + 62), (rx + 8, ry + 88)], fill=(255, 140, 30))
    d.polygon([(rx + 5, ry + 62), (rx + 11, ry + 62), (rx + 8, ry + 78)], fill=(255, 220, 80))
    img.paste(sub, (x0, y0))


def draw_chart(draw, x0, y0):
    draw.rectangle([x0, y0, x0 + 320, y0 + 98], fill=(253, 238, 240))
    # Grid
    for gy in range(y0 + 14, y0 + 92, 18):
        draw.line([x0 + 10, gy, x0 + 310, gy], fill=(235, 205, 210), width=1)
    # Falling line with a small bounce at the end
    pts = [(x0 + 12, y0 + 16), (x0 + 60, y0 + 22), (x0 + 110, y0 + 20),
           (x0 + 150, y0 + 38), (x0 + 200, y0 + 46), (x0 + 240, y0 + 62),
           (x0 + 275, y0 + 58), (x0 + 308, y0 + 74)]
    area = pts + [(x0 + 308, y0 + 94), (x0 + 12, y0 + 94)]
    draw.polygon(area, fill=(250, 205, 210))
    draw.line(pts, fill=RED, width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED_DARK)
    # Down arrow at the end
    draw.polygon([(x0 + 298, y0 + 66), (x0 + 308, y0 + 66), (x0 + 303, y0 + 78)], fill=RED_DARK)
    draw.text((x0 + 14, y0 + 64), "-6.2%", font=F_CHART, fill=RED)


def draw_hero(draw, img, x0, kind, headline, subline):
    draw.rectangle([x0, 96, x0 + 320, 272], outline=BORDER, width=1)
    if kind == "ship":
        draw_ship(draw, x0, 96)
    elif kind == "space":
        draw_space(img, x0, 96)
    else:
        draw_chart(draw, x0, 96)
    lines = wrap(draw, headline, F_HERO, 300)
    y = 202
    for ln in lines[:2]:
        draw.text((x0 + 10, y), ln, font=F_HERO, fill=INK)
        y += 19
    sub = wrap(draw, subline, F_HERO_SUB, 300)
    y = 240
    for ln in sub[:2]:
        draw.text((x0 + 10, y), ln, font=F_HERO_SUB, fill=MUTED)
        y += 14


def draw_map(draw):
    draw.text((24, 282), "WHERE IT HAPPENED", font=F_SECTION, fill=NAVY)
    note = "RED PINS = STORY NUMBERS BELOW"
    draw.text((1000 - text_w(draw, note, F_NOTE), 284), note, font=F_NOTE, fill=RED)
    draw.rectangle([24, 302, 1000, 452], fill=MAP_BG, outline=BORDER, width=1)
    for x in range(28, 998, 8):
        for y in range(306, 450, 8):
            for (cx, cy, rx, ry) in ELLIPSES:
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=DOT)
                    break
    for num, (px, py) in sorted(PINS.items()):
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255), width=2)
        s = str(num)
        tw = text_w(draw, s, F_PIN)
        draw.text((px - tw / 2, py - 7), s, font=F_PIN, fill=(255, 255, 255))


def draw_flag(draw, x0, kind):
    y0, w, h = 460, 90, 52
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=BORDER, width=1)
    if kind == "USA":
        for i in range(7):
            draw.rectangle([x0, y0 + i * 8, x0 + w, y0 + i * 8 + 4],
                           fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        draw.rectangle([x0, y0, x0 + 36, y0 + 28], fill=(30, 50, 110))
        for r in range(4):
            for c in range(5):
                draw.ellipse([x0 + 4 + c * 6, y0 + 4 + r * 6, x0 + 6 + c * 6, y0 + 6 + r * 6],
                             fill=(255, 255, 255))
    elif kind == "CHINA":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 41, 16))
        draw.ellipse([x0 + 8, y0 + 8, x0 + 26, y0 + 26], fill=(255, 222, 0))
        for sx, sy in [(34, 10), (42, 16), (42, 26), (34, 30)]:
            draw.ellipse([x0 + sx, y0 + sy, x0 + sx + 6, y0 + sy + 6], fill=(255, 222, 0))
    elif kind == "S. KOREA":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(255, 255, 255))
        draw.ellipse([x0 + 35, y0 + 14, x0 + 55, y0 + 38], fill=(205, 46, 58))
        draw.pieslice([x0 + 35, y0 + 14, x0 + 55, y0 + 38], 180, 360, fill=(205, 46, 58))
        draw.pieslice([x0 + 35, y0 + 14, x0 + 55, y0 + 38], 0, 180, fill=(0, 71, 160))
        for bx in (8, 68):
            draw.rectangle([x0 + bx, y0 + 8, x0 + bx + 12, y0 + 11], fill=(0, 0, 0))
            draw.rectangle([x0 + bx, y0 + 40, x0 + bx + 12, y0 + 43], fill=(0, 0, 0))
    elif kind == "BRITAIN":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(0, 36, 125))
        draw.line([x0, y0, x0 + w, y0 + h], fill=(255, 255, 255), width=10)
        draw.line([x0 + w, y0, x0, y0 + h], fill=(255, 255, 255), width=10)
        draw.rectangle([x0 + 40, y0, x0 + 50, y0 + h], fill=(255, 255, 255))
        draw.rectangle([x0, y0 + 21, x0 + w, y0 + 31], fill=(255, 255, 255))
        draw.rectangle([x0 + 43, y0, x0 + 47, y0 + h], fill=(200, 16, 46))
        draw.rectangle([x0, y0 + 24, x0 + w, y0 + 28], fill=(200, 16, 46))
    elif kind == "PAKISTAN":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(1, 65, 28))
        draw.rectangle([x0, y0, x0 + 22, y0 + h], fill=(255, 255, 255))
        draw.ellipse([x0 + 44, y0 + 12, x0 + 70, y0 + 40], fill=(255, 255, 255))
        draw.ellipse([x0 + 50, y0 + 14, x0 + 72, y0 + 38], fill=(1, 65, 28))
        draw.ellipse([x0 + 68, y0 + 20, x0 + 74, y0 + 26], fill=(255, 255, 255))
    elif kind == "EGYPT":
        draw.rectangle([x0, y0, x0 + w, y0 + 18], fill=(206, 17, 38))
        draw.rectangle([x0, y0 + 18, x0 + w, y0 + 34], fill=(255, 255, 255))
        draw.rectangle([x0, y0 + 34, x0 + w, y0 + h], fill=(0, 0, 0))
        draw.ellipse([x0 + 42, y0 + 20, x0 + 48, y0 + 32], fill=(200, 160, 40))
    elif kind == "INDONESIA":
        draw.rectangle([x0, y0, x0 + w, y0 + 26], fill=(210, 0, 0))
        draw.rectangle([x0, y0 + 26, x0 + w, y0 + h], fill=(255, 255, 255))
    elif kind == "S. ARABIA":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(0, 122, 61))
        draw.rectangle([x0 + 18, y0 + 18, x0 + 72, y0 + 22], fill=(255, 255, 255))
        draw.rectangle([x0 + 26, y0 + 34, x0 + 64, y0 + 37], fill=(255, 255, 255))
    elif kind == "SUDAN":
        draw.rectangle([x0, y0, x0 + w, y0 + 18], fill=(210, 16, 52))
        draw.rectangle([x0, y0 + 18, x0 + w, y0 + 34], fill=(255, 255, 255))
        draw.rectangle([x0, y0 + 34, x0 + w, y0 + h], fill=(0, 0, 0))
        draw.polygon([(x0, y0), (x0 + 30, y0 + 26), (x0, y0 + h)], fill=(0, 122, 61))
    elif kind == "BANGLADESH":
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(0, 106, 78))
        draw.ellipse([x0 + 32, y0 + 12, x0 + 62, y0 + 40], fill=(244, 42, 65))
    centred(draw, x0 + w / 2, 518, kind, F_FLAG, NAVY)


def draw_timeline(draw):
    draw.text((24, 546), "THE DAY IN UTC", font=F_SECTION, fill=NAVY)
    y_line = 580
    draw.line([70, y_line, 954, y_line], fill=NAVY, width=2)
    xs = [110, 262, 414, 566, 718, 870]
    for (t, ev), cx in zip(TIMELINE, xs):
        draw.ellipse([cx - 5, y_line - 5, cx + 5, y_line + 5], fill=RED, outline=(255, 255, 255), width=2)
        centred(draw, cx, 560, t, F_TIME, RED)
        lines = wrap(draw, ev, F_EVENT, 140)
        y = 590
        for ln in lines[:2]:
            centred(draw, cx, y, ln, F_EVENT, INK)
            y += 13


def draw_list(draw):
    draw.rectangle([24, 628, 1000, 654], fill=LIGHT_BAR)
    centred(draw, W // 2, 634, "ALL 29 STORIES  —  WEDNESDAY 25 NOVEMBER 2026",
            F_SECTION, NAVY)
    row_h = 17.5
    y0 = 664
    for i, story in enumerate(STORIES):
        col = 0 if i < 17 else 1
        row = i if col == 0 else i - 17
        x = 30 if col == 0 else 528
        y = y0 + row * row_h
        num = f"{i + 1}."
        draw.text((x, y), num, font=F_LIST_NUM, fill=NAVY)
        draw.text((x + 30, y), story, font=F_LIST, fill=INK)


def draw_footer(draw):
    draw.rectangle([0, 966, W, H], fill=NAVY)
    centred(draw, W // 2, 978,
            "DATE CHECK — Every story above happened or was first reported on",
            F_FOOT, (255, 255, 255))
    centred(draw, W // 2, 996,
            "Wednesday 25 November 2026. No story from another day.",
            F_FOOT, (255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_hero(draw, img, 24, "ship", "US HITS 14 NATIONS WITH NEW TARIFFS",
              "China up to 20% — 40% if the trade truce fails. Brazil jets hit too.")
    draw_hero(draw, img, 352, "space", "FIRST PAKISTANI ASTRONAUT DOCKS AT TIANGONG",
              "Shenzhou-24 docks 03:56 UTC; Zeeshan Ali is the first foreign visitor.")
    draw_hero(draw, img, 680, "chart", "KOSPI PLUNGES 6.2% AS AI DOUBTS RETURN",
              "Samsung -9.9%, SK Hynix -11.1%, Taiex -4.8%, Nikkei -2.8%.")
    draw_map(draw)
    flags = ["USA", "CHINA", "S. KOREA", "BRITAIN", "PAKISTAN", "EGYPT",
             "INDONESIA", "S. ARABIA", "SUDAN", "BANGLADESH"]
    for i, name in enumerate(flags):
        draw_flag(draw, 26 + i * 98, name)
    draw_timeline(draw)
    draw_list(draw)
    draw_footer(draw)
    img.save(OUT, optimize=True)
    print(f"saved {OUT} {img.size}")


if __name__ == "__main__":
    main()
