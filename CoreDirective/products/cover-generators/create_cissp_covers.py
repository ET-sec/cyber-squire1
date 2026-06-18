#!/usr/bin/env python3
"""CISSP GREEN theme covers - matches CCNA gold / Sec+ red / Net+ blue design language.
Metrics verified against 6-agent audit report (2026-03-13)."""
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

# GREEN theme colors - electric green (brand: Directed Signal)
BG = '#0D1117'
BG2 = '#161B22'
ACCENT = '#00E676'       # CISSP ELECTRIC GREEN
ACCENT_LIGHT = '#69F0AE'
WHITE = '#E6EDF3'
GRAY = '#8B949E'
DIM = '#21262D'
BORDER = '#30363D'


def create_cover():
    """1280x1280 square cover."""
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

    # "CISSP" massive centered
    f_title = font('BigShoulders-Bold', 200)
    bbox = d.textbbox((0, 0), 'CISSP', font=f_title)
    tw = bbox[2] - bbox[0]
    title_x = (W - tw) // 2
    title_y = 100 * S
    d.text((title_x, title_y), 'CISSP', fill=WHITE, font=f_title)

    # Divider directly under CISSP (no ISC2 line)
    div_y = title_y + (bbox[3] - bbox[1]) + 40 * S
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

    # Verified metrics from 6-agent audit (2026-03-13)
    features = [
        ("10", "Databases"),
        ("40+", "Custom Views"),
        ("8", "Exam Domains"),
        ("62", "ISC2 Objectives"),
        ("13", "Security Models"),
        ("4", "DoK Levels"),
        ("30+", "Crypto Entries"),
        ("13", "Scenario Labs"),
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
    path = os.path.join(OUT_DIR, 'cissp-cover-green-1280x1280.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Cover: {path}")


def create_thumbnail():
    """600x600 thumbnail."""
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

    # "CERTIFICATION EXAM" top label (no ISC2)
    f_top = tfont('JetBrainsMono', 11)
    text_top = 'CERTIFICATION EXAM'
    bbox = d.textbbox((0,0), text_top, font=f_top)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, 42*T), text_top, fill=GRAY, font=f_top)

    # "CISSP" large
    f_title = tfont('BigShoulders-Bold', 140)
    bbox = d.textbbox((0,0), 'CISSP', font=f_title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text(((W-tw)//2, H//2 - th - 20*T), 'CISSP', fill=WHITE, font=f_title)

    # Divider (no exam code line)
    d.line([(160*T, H//2 + 30*T), (W-160*T, H//2 + 30*T)], fill=BORDER, width=T)

    # "STUDY SYSTEM"
    f_sub = tfont('Outfit-Bold', 24)
    bbox = d.textbbox((0,0), 'STUDY SYSTEM', font=f_sub)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H//2 + 45*T), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    f_feat = tfont('JetBrainsMono', 10)
    feat_text = '10 DBs  |  40+ Views  |  DoK Framework'
    bbox = d.textbbox((0,0), feat_text, font=f_feat)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 100*T), feat_text, fill=WHITE, font=f_feat)

    f_tag = tfont('JetBrainsMono', 12)
    tag_text = '// NOTION TEMPLATE'
    bbox = d.textbbox((0,0), tag_text, font=f_tag)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 68*T), tag_text, fill=ACCENT, font=f_tag)

    final = img.resize((600, 600), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'cissp-thumb-green-600x600.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Thumb: {path}")


def create_banner():
    """1280x720 social/header banner."""
    T = 6
    W, H = 1280 * T, 720 * T
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    def bfont(name, size):
        paths = {
            'BigShoulders-Bold': 'BigShoulders-Bold.ttf',
            'GeistMono-Bold': 'GeistMono-Bold.ttf',
            'GeistMono': 'GeistMono-Regular.ttf',
            'JetBrainsMono': 'JetBrainsMono-Regular.ttf',
            'JetBrainsMono-Bold': 'JetBrainsMono-Bold.ttf',
            'Outfit': 'Outfit-Regular.ttf',
            'Outfit-Bold': 'Outfit-Bold.ttf',
        }
        return ImageFont.truetype(os.path.join(FONT_DIR, paths[name]), size * T)

    # Dot grid
    for x in range(40*T, W, 40*T):
        for y in range(40*T, H, 40*T):
            r = int(1.5 * T)
            d.ellipse([x-r, y-r, x+r, y+r], fill=DIM)

    # Left accent bar
    d.rectangle([0, 0, 5*T, H], fill=ACCENT)

    # Corner brackets
    lw = int(2.5 * T)
    d.line([(28*T, 28*T), (28*T, 100*T)], fill=ACCENT, width=lw)
    d.line([(28*T, 28*T), (100*T, 28*T)], fill=ACCENT, width=lw)
    d.line([(W-28*T, H-28*T), (W-28*T, H-100*T)], fill=ACCENT, width=lw)
    d.line([(W-28*T, H-28*T), (W-100*T, H-28*T)], fill=ACCENT, width=lw)
    lw2 = int(1.5 * T)
    d.line([(W-28*T, 28*T), (W-28*T, 68*T)], fill=BORDER, width=lw2)
    d.line([(W-28*T, 28*T), (W-68*T, 28*T)], fill=BORDER, width=lw2)
    d.line([(28*T, H-28*T), (28*T, H-68*T)], fill=BORDER, width=lw2)
    d.line([(28*T, H-28*T), (68*T, H-28*T)], fill=BORDER, width=lw2)

    # LEFT SIDE: "CISSP" + subtitle stack (no ISC2)
    left_x = 100 * T

    f_title = bfont('BigShoulders-Bold', 200)
    title_y = 80 * T
    d.text((left_x, title_y), 'CISSP', fill=WHITE, font=f_title)
    bbox = d.textbbox((left_x, title_y), 'CISSP', font=f_title)

    # Divider directly under CISSP
    div_y = bbox[3] + 30 * T
    d.line([(left_x, div_y), (left_x + 300*T, div_y)], fill=BORDER, width=T)

    f_sub = bfont('Outfit-Bold', 30)
    sub_y = div_y + 20 * T
    d.text((left_x, sub_y), 'STUDY SYSTEM', fill=WHITE, font=f_sub)
    bbox3 = d.textbbox((left_x, sub_y), 'STUDY SYSTEM', font=f_sub)

    f_tag = bfont('JetBrainsMono', 14)
    tag_y = bbox3[3] + 16 * T
    d.text((left_x, tag_y), '// NOTION TEMPLATE', fill=ACCENT, font=f_tag)

    # RIGHT SIDE: Feature card (compact)
    card_x = W // 2 + 40 * T
    card_y = 60 * T
    card_w = W - card_x - 60 * T
    card_h = H - 120 * T

    d.rounded_rectangle([card_x+4*T, card_y+4*T, card_x+card_w+4*T, card_y+card_h+4*T],
                        radius=10*T, fill='#080B10')
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                        radius=10*T, fill=BG2)
    d.rounded_rectangle([card_x, card_y, card_x+card_w, card_y+card_h],
                        radius=10*T, outline=BORDER, width=T)
    d.rectangle([card_x+5*T, card_y, card_x+card_w-5*T, card_y+3*T], fill=ACCENT)

    f_header = bfont('JetBrainsMono', 10)
    d.text((card_x+25*T, card_y+16*T), 'SYSTEM COMPONENTS', fill=WHITE, font=f_header)
    d.line([(card_x+25*T, card_y+36*T), (card_x+card_w-25*T, card_y+36*T)], fill=BORDER, width=T)

    features = [
        ("10", "Databases"),
        ("40+", "Views"),
        ("8", "Domains"),
        ("62", "Objectives"),
        ("13", "Models"),
        ("4", "DoK"),
    ]

    col_w = (card_w - 60*T) // 3
    row_h = (card_h - 100*T) // 2
    start_x = card_x + 35 * T
    start_y = card_y + 48 * T
    f_num = bfont('BigShoulders-Bold', 44)
    f_label = bfont('Outfit', 12)

    for i, (num, label) in enumerate(features):
        col = i % 3
        row = i // 3
        fx = start_x + col * col_w
        fy = start_y + row * row_h
        d.text((fx, fy), num, fill=ACCENT, font=f_num)
        bbox_n = d.textbbox((fx, fy), num, font=f_num)
        d.text((fx, bbox_n[3] + 3*T), label, fill=WHITE, font=f_label)

    # Bottom selling points
    bottom_y = H - 55 * T
    f_pts = bfont('Outfit', 12)
    points = ["ADHD-Friendly", "Lifetime Updates", "7-Day Guarantee"]
    point_spacing = W // 3
    for i, pt in enumerate(points):
        px = point_spacing * i + point_spacing // 2
        bbox_pt = d.textbbox((0, 0), pt, font=f_pts)
        ptw = bbox_pt[2] - bbox_pt[0]
        r = 3 * T
        dot_x = px - ptw // 2 - 12 * T
        d.ellipse([dot_x-r, bottom_y+6*T-r, dot_x+r, bottom_y+6*T+r], fill=ACCENT)
        d.text((dot_x + 10*T, bottom_y), pt, fill=WHITE, font=f_pts)

    final = img.resize((1280, 720), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'cissp-banner-green-1280x720.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Banner: {path}")


if __name__ == '__main__':
    print("Generating CISSP GREEN covers (v2 - verified metrics, no ISC2)...")
    create_cover()
    create_thumbnail()
    create_banner()

    for f in ['cissp-cover-green-1280x1280.png', 'cissp-thumb-green-600x600.png', 'cissp-banner-green-1280x720.png']:
        p = os.path.join(OUT_DIR, f)
        img = Image.open(p)
        kb = os.path.getsize(p) / 1024
        print(f"  {f}: {img.size[0]}x{img.size[1]}, {kb:.0f}KB")
    print("Done.")
