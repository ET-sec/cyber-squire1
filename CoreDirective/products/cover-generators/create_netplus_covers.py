#!/usr/bin/env python3
"""Network+ N10-009 BLUE theme covers - matches CCNA gold / Sec+ red design language."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/Users/et/cyber-squire-ops/.claude/skills/canvas-design/canvas-fonts"
OUT_DIR = "/Users/et/cyber-squire-ops/builds/gumroad-assets"
os.makedirs(OUT_DIR, exist_ok=True)
S = 6

def font(name, size):
    paths = {
        'BigShoulders-Bold': 'BigShoulders-Bold.ttf',
        'GeistMono-Bold': 'GeistMono-Bold.ttf',
        'GeistMono': 'GeistMono-Regular.ttf',
        'JetBrainsMono': 'JetBrainsMono-Regular.ttf',
        'JetBrainsMono-Bold': 'JetBrainsMono-Bold.ttf',
        'Outfit': 'Outfit-Regular.ttf',
        'Outfit-Bold': 'Outfit-Bold.ttf',
    }
    return ImageFont.truetype(os.path.join(FONT_DIR, paths[name]), size * S)

# BLUE theme colors
BG = '#0D1117'
BG2 = '#161B22'
ACCENT = '#2196F3'       # Network+ BLUE
ACCENT_LIGHT = '#64B5F6'
WHITE = '#E6EDF3'
GRAY = '#8B949E'
DIM = '#21262D'
BORDER = '#30363D'

def create_cover():
    W, H = 1280 * S, 1280 * S
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # Dot grid
    for x in range(40*S, W, 40*S):
        for y in range(40*S, H, 40*S):
            r = int(1.5 * S)
            d.ellipse([x-r, y-r, x+r, y+r], fill=DIM)

    # Left accent bar
    d.rectangle([0, 0, 5*S, H], fill=ACCENT)

    # Corner brackets
    lw = int(2.5 * S)
    d.line([(28*S, 28*S), (28*S, 100*S)], fill=ACCENT, width=lw)
    d.line([(28*S, 28*S), (100*S, 28*S)], fill=ACCENT, width=lw)
    d.line([(W-28*S, H-28*S), (W-28*S, H-100*S)], fill=ACCENT, width=lw)
    d.line([(W-28*S, H-28*S), (W-100*S, H-28*S)], fill=ACCENT, width=lw)
    lw2 = int(1.5 * S)
    d.line([(W-28*S, 28*S), (W-28*S, 68*S)], fill=BORDER, width=lw2)
    d.line([(W-28*S, 28*S), (W-68*S, 28*S)], fill=BORDER, width=lw2)
    d.line([(28*S, H-28*S), (28*S, H-68*S)], fill=BORDER, width=lw2)
    d.line([(28*S, H-28*S), (68*S, H-28*S)], fill=BORDER, width=lw2)

    # "NETWORK+" massive centered
    f_title = font('BigShoulders-Bold', 160)
    bbox = d.textbbox((0, 0), 'NETWORK+', font=f_title)
    tw = bbox[2] - bbox[0]
    title_x = (W - tw) // 2
    title_y = 80 * S
    d.text((title_x, title_y), 'NETWORK+', fill=WHITE, font=f_title)

    # "N10-009" centered
    f_code = font('GeistMono-Bold', 64)
    bbox2 = d.textbbox((0, 0), 'N10-009', font=f_code)
    tw2 = bbox2[2] - bbox2[0]
    code_y = title_y + (bbox[3] - bbox[1]) + 40 * S
    d.text(((W - tw2) // 2, code_y), 'N10-009', fill=ACCENT, font=f_code)

    # Divider
    div_y = code_y + (bbox2[3] - bbox2[1]) + 28 * S
    d.line([(W//2 - 200*S, div_y), (W//2 + 200*S, div_y)], fill=BORDER, width=S)

    # "STUDY SYSTEM"
    f_sub = font('Outfit-Bold', 36)
    bbox3 = d.textbbox((0, 0), 'STUDY SYSTEM', font=f_sub)
    tw3 = bbox3[2] - bbox3[0]
    sub_y = div_y + 24 * S
    d.text(((W - tw3) // 2, sub_y), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    # "// NOTION TEMPLATE"
    f_tag = font('JetBrainsMono', 16)
    tag_text = '// NOTION TEMPLATE'
    bbox4 = d.textbbox((0, 0), tag_text, font=f_tag)
    tw4 = bbox4[2] - bbox4[0]
    tag_y = sub_y + (bbox3[3] - bbox3[1]) + 20 * S
    d.text(((W - tw4) // 2, tag_y), tag_text, fill=ACCENT, font=f_tag)

    # Feature card
    card_margin = 60 * S
    cx = card_margin
    cw = W - 2 * card_margin
    ch = 520 * S
    cy = tag_y + 60 * S

    d.rounded_rectangle([cx+5*S, cy+5*S, cx+cw+5*S, cy+ch+5*S], radius=12*S, fill='#080B10')
    d.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=12*S, fill=BG2)
    d.rounded_rectangle([cx, cy, cx+cw, cy+ch], radius=12*S, outline=BORDER, width=S)
    d.rectangle([cx+6*S, cy, cx+cw-6*S, cy+3*S], fill=ACCENT)

    f_header = font('JetBrainsMono', 12)
    d.text((cx+35*S, cy+20*S), 'SYSTEM COMPONENTS', fill=WHITE, font=f_header)
    d.line([(cx+35*S, cy+45*S), (cx+cw-35*S, cy+45*S)], fill=BORDER, width=S)

    features = [
        ("10", "Databases"),
        ("30+", "Custom Views"),
        ("5", "Exam Domains"),
        ("300+", "Acronyms"),
        ("20+", "Port Refs"),
        ("4", "DoK Levels"),
        ("25+", "CLI Commands"),
        ("Live", "Day Tracker"),
        ("Live", "Dashboard"),
    ]

    col_w = (cw - 80*S) // 3
    row_h = 148 * S
    start_x = cx + 50 * S
    start_y = cy + 58 * S
    f_num = font('BigShoulders-Bold', 50)
    f_label = font('Outfit', 15)

    for i, (num, label) in enumerate(features):
        col = i % 3
        row = i // 3
        fx = start_x + col * col_w
        fy = start_y + row * row_h
        d.text((fx, fy), num, fill=ACCENT, font=f_num)
        bbox_n = d.textbbox((fx, fy), num, font=f_num)
        d.text((fx, bbox_n[3] + 4*S), label, fill=WHITE, font=f_label)
        bbox_l = d.textbbox((fx, bbox_n[3] + 4*S), label, font=f_label)
        d.line([(fx, bbox_l[3] + 8*S), (bbox_l[2] + 20*S, bbox_l[3] + 8*S)], fill=DIM, width=S)

    bot_y = cy + ch - 50 * S
    d.line([(cx+35*S, bot_y), (cx+cw-35*S, bot_y)], fill=BORDER, width=S)
    f_tagline = font('JetBrainsMono', 11)
    tagline = 'Auto-Linked Mistakes  //  Study Analytics  //  Mobile Optimized'
    bbox_t = d.textbbox((0, 0), tagline, font=f_tagline)
    ttw = bbox_t[2] - bbox_t[0]
    d.text((cx + (cw - ttw)//2, bot_y + 16*S), tagline, fill=WHITE, font=f_tagline)

    # Bottom selling points
    bottom_y = cy + ch + 40 * S
    f_pts = font('Outfit', 15)
    points = ["ADHD-Friendly Design", "Lifetime Updates", "7-Day Money Back Guarantee"]
    point_spacing = W // 3
    for i, pt in enumerate(points):
        px = point_spacing * i + point_spacing // 2
        bbox_pt = d.textbbox((0, 0), pt, font=f_pts)
        ptw = bbox_pt[2] - bbox_pt[0]
        r = 4 * S
        dot_x = px - ptw // 2 - 16 * S
        d.ellipse([dot_x-r, bottom_y+8*S-r, dot_x+r, bottom_y+8*S+r], fill=ACCENT)
        d.text((dot_x + 12*S, bottom_y), pt, fill=WHITE, font=f_pts)

    final = img.resize((1280, 1280), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'netplus-cover-blue-1280x1280.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Cover: {path}")


def create_thumbnail():
    T = 6
    W, H = 600 * T, 600 * T
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    def tfont(name, size):
        paths = {
            'BigShoulders-Bold': 'BigShoulders-Bold.ttf',
            'GeistMono-Bold': 'GeistMono-Bold.ttf',
            'JetBrainsMono': 'JetBrainsMono-Regular.ttf',
            'Outfit-Bold': 'Outfit-Bold.ttf',
        }
        return ImageFont.truetype(os.path.join(FONT_DIR, paths[name]), size * T)

    for x in range(25*T, W, 25*T):
        for y in range(25*T, H, 25*T):
            r = T
            d.ellipse([x-r, y-r, x+r, y+r], fill=DIM)

    d.rounded_rectangle([12*T, 12*T, W-12*T, H-12*T], radius=6*T, outline=ACCENT, width=3*T)
    cl = 50 * T
    d.rectangle([12*T, 12*T, 12*T+cl, 12*T+3*T], fill=ACCENT)
    d.rectangle([12*T, 12*T, 12*T+3*T, 12*T+cl], fill=ACCENT)
    d.rectangle([W-12*T-cl, H-12*T-3*T, W-12*T, H-12*T], fill=ACCENT)
    d.rectangle([W-12*T-3*T, H-12*T-cl, W-12*T, H-12*T], fill=ACCENT)

    f_top = tfont('JetBrainsMono', 11)
    text_top = 'COMPTIA CERTIFICATION'
    bbox = d.textbbox((0,0), text_top, font=f_top)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, 42*T), text_top, fill=WHITE, font=f_top)

    # "NET+" large (shorter than NETWORK+ to fit thumbnail)
    f_title = tfont('BigShoulders-Bold', 120)
    bbox = d.textbbox((0,0), 'NET+', font=f_title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text(((W-tw)//2, H//2 - th - 30*T), 'NET+', fill=WHITE, font=f_title)

    f_code = tfont('GeistMono-Bold', 44)
    bbox = d.textbbox((0,0), 'N10-009', font=f_code)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H//2 + 10*T), 'N10-009', fill=ACCENT, font=f_code)

    d.line([(160*T, H//2 + 65*T), (W-160*T, H//2 + 65*T)], fill=BORDER, width=T)

    f_sub = tfont('Outfit-Bold', 24)
    bbox = d.textbbox((0,0), 'STUDY SYSTEM', font=f_sub)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H//2 + 80*T), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    f_feat = tfont('JetBrainsMono', 10)
    feat_text = '10 DBs  |  30+ Views  |  DoK Framework'
    bbox = d.textbbox((0,0), feat_text, font=f_feat)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 100*T), feat_text, fill=WHITE, font=f_feat)

    f_tag = tfont('JetBrainsMono', 12)
    tag_text = '// NOTION TEMPLATE'
    bbox = d.textbbox((0,0), tag_text, font=f_tag)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 68*T), tag_text, fill=ACCENT, font=f_tag)

    final = img.resize((600, 600), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'netplus-thumb-blue-600x600.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Thumb: {path}")


if __name__ == '__main__':
    create_cover()
    create_thumbnail()
    for f in ['netplus-cover-blue-1280x1280.png', 'netplus-thumb-blue-600x600.png']:
        p = os.path.join(OUT_DIR, f)
        img = Image.open(p)
        kb = os.path.getsize(p) / 1024
        print(f"  {f}: {img.size[0]}x{img.size[1]}, {kb:.0f}KB")
