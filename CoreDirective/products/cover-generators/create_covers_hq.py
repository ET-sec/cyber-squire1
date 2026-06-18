#!/usr/bin/env python3
"""
High-quality PNG generation for Gumroad covers.
Renders at 3x resolution directly to PIL, then downscales with Lanczos.
No PDF intermediate — pixel-perfect output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/Users/et/cyber-squire-ops/.claude/skills/canvas-design/canvas-fonts"
OUT_DIR = "/Users/et/cyber-squire-ops/builds/gumroad-assets"
os.makedirs(OUT_DIR, exist_ok=True)

# Scale factor for supersampling
S = 6

def font(name, size):
    """Load font at scaled size."""
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

# Colors
BG = '#0D1117'
BG2 = '#161B22'
ACCENT = '#F5A623'
ACCENT_LIGHT = '#FFD060'
WHITE = '#E6EDF3'
GRAY = '#8B949E'
DIM = '#21262D'
BORDER = '#30363D'
DARK_GRAY = '#484F58'


def create_cover():
    """1280x1280 square cover rendered at 3x (3840x3840) then downscaled."""
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

    # Top-left corner bracket
    lw = int(2.5 * S)
    d.line([(28*S, 28*S), (28*S, 100*S)], fill=ACCENT, width=lw)
    d.line([(28*S, 28*S), (100*S, 28*S)], fill=ACCENT, width=lw)

    # Bottom-right corner bracket
    d.line([(W-28*S, H-28*S), (W-28*S, H-100*S)], fill=ACCENT, width=lw)
    d.line([(W-28*S, H-28*S), (W-100*S, H-28*S)], fill=ACCENT, width=lw)

    # Top-right small bracket
    lw2 = int(1.5 * S)
    d.line([(W-28*S, 28*S), (W-28*S, 68*S)], fill=BORDER, width=lw2)
    d.line([(W-28*S, 28*S), (W-68*S, 28*S)], fill=BORDER, width=lw2)

    # Bottom-left small bracket
    d.line([(28*S, H-28*S), (28*S, H-68*S)], fill=BORDER, width=lw2)
    d.line([(28*S, H-28*S), (68*S, H-28*S)], fill=BORDER, width=lw2)

    # === TOP SECTION: Title block (centered) ===
    # "CCNA" massive centered
    f_ccna = font('BigShoulders-Bold', 200)
    bbox = d.textbbox((0, 0), 'CCNA', font=f_ccna)
    tw = bbox[2] - bbox[0]
    ccna_x = (W - tw) // 2
    ccna_y = 80 * S
    d.text((ccna_x, ccna_y), 'CCNA', fill=WHITE, font=f_ccna)

    # "200-301" centered below
    f_code = font('GeistMono-Bold', 64)
    bbox2 = d.textbbox((0, 0), '200-301', font=f_code)
    tw2 = bbox2[2] - bbox2[0]
    code_y = ccna_y + (bbox[3] - bbox[1]) + 40 * S
    d.text(((W - tw2) // 2, code_y), '200-301', fill=ACCENT, font=f_code)

    # Divider line
    div_y = code_y + (bbox2[3] - bbox2[1]) + 28 * S
    d.line([(W//2 - 200*S, div_y), (W//2 + 200*S, div_y)], fill=BORDER, width=S)

    # "STUDY SYSTEM" centered (extra spacing from divider)
    f_sub = font('Outfit-Bold', 36)
    bbox3 = d.textbbox((0, 0), 'STUDY SYSTEM', font=f_sub)
    tw3 = bbox3[2] - bbox3[0]
    sub_y = div_y + 24 * S
    d.text(((W - tw3) // 2, sub_y), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    # "// NOTION TEMPLATE" (extra spacing from STUDY SYSTEM)
    f_tag = font('JetBrainsMono', 16)
    tag_text = '// NOTION TEMPLATE'
    bbox4 = d.textbbox((0, 0), tag_text, font=f_tag)
    tw4 = bbox4[2] - bbox4[0]
    tag_y = sub_y + (bbox3[3] - bbox3[1]) + 20 * S
    d.text(((W - tw4) // 2, tag_y), tag_text, fill=ACCENT, font=f_tag)

    # === MIDDLE: Feature card (full width, centered) ===
    card_margin = 60 * S
    cx = card_margin
    cw = W - 2 * card_margin
    ch = 520 * S
    cy = tag_y + 60 * S

    # Card shadow
    d.rounded_rectangle(
        [cx+5*S, cy+5*S, cx+cw+5*S, cy+ch+5*S],
        radius=12*S, fill='#080B10'
    )
    # Card background
    d.rounded_rectangle(
        [cx, cy, cx+cw, cy+ch],
        radius=12*S, fill=BG2
    )
    # Card border
    d.rounded_rectangle(
        [cx, cy, cx+cw, cy+ch],
        radius=12*S, outline=BORDER, width=S
    )
    # Top accent line
    d.rectangle([cx+6*S, cy, cx+cw-6*S, cy+3*S], fill=ACCENT)

    # Card header
    f_header = font('JetBrainsMono', 12)
    d.text((cx+35*S, cy+20*S), 'SYSTEM COMPONENTS', fill=WHITE, font=f_header)

    # Divider under header
    d.line([(cx+35*S, cy+45*S), (cx+cw-35*S, cy+45*S)], fill=BORDER, width=S)

    # Feature grid 3x3
    features = [
        ("10", "Databases"),
        ("30+", "Custom Views"),
        ("6", "Exam Domains"),
        ("300+", "Acronyms"),
        ("35+", "Port Refs"),
        ("4", "DoK Levels"),
        ("100+", "CLI Commands"),
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
        d.line([(fx, bbox_l[3] + 8*S), (bbox_l[2] + 20*S, bbox_l[3] + 8*S)],
               fill=DIM, width=S)

    # Card bottom tagline
    bot_y = cy + ch - 50 * S
    d.line([(cx+35*S, bot_y), (cx+cw-35*S, bot_y)], fill=BORDER, width=S)

    f_tagline = font('JetBrainsMono', 11)
    tagline = 'Auto-Linked Mistakes  //  Study Analytics  //  Mobile Optimized'
    bbox_t = d.textbbox((0, 0), tagline, font=f_tagline)
    ttw = bbox_t[2] - bbox_t[0]
    d.text((cx + (cw - ttw)//2, bot_y + 16*S), tagline, fill=WHITE, font=f_tagline)

    # === BOTTOM SECTION: Selling points + price ===
    bottom_y = cy + ch + 40 * S

    # Three selling points in a row
    f_pts = font('Outfit', 15)
    points = [
        "ADHD-Friendly Design",
        "Lifetime Updates",
        "7-Day Money Back Guarantee",
    ]
    point_spacing = W // 3
    for i, pt in enumerate(points):
        px = point_spacing * i + point_spacing // 2
        bbox_pt = d.textbbox((0, 0), pt, font=f_pts)
        ptw = bbox_pt[2] - bbox_pt[0]
        # Gold dot
        r = 4 * S
        dot_x = px - ptw // 2 - 16 * S
        d.ellipse([dot_x-r, bottom_y+8*S-r, dot_x+r, bottom_y+8*S+r], fill=ACCENT)
        d.text((dot_x + 12*S, bottom_y), pt, fill=WHITE, font=f_pts)

    # Downscale to final 1280x1280 with Lanczos
    final = img.resize((1280, 1280), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'ccna-cover-gold-1280x1280.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Cover: {path} (1280x1280, {S}x supersampled)")


def create_thumbnail():
    """600x600 thumbnail rendered at 6x (3600x3600) then downscaled for max sharpness."""
    T = 6  # Higher scale for small image
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

    # Subtle dot grid
    for x in range(25*T, W, 25*T):
        for y in range(25*T, H, 25*T):
            r = T
            d.ellipse([x-r, y-r, x+r, y+r], fill=DIM)

    # Border with accent
    d.rounded_rectangle(
        [12*T, 12*T, W-12*T, H-12*T],
        radius=6*T, outline=ACCENT, width=3*T
    )

    # Corner accent fills
    cl = 50 * T
    # Top-left
    d.rectangle([12*T, 12*T, 12*T+cl, 12*T+3*T], fill=ACCENT)
    d.rectangle([12*T, 12*T, 12*T+3*T, 12*T+cl], fill=ACCENT)
    # Bottom-right
    d.rectangle([W-12*T-cl, H-12*T-3*T, W-12*T, H-12*T], fill=ACCENT)
    d.rectangle([W-12*T-3*T, H-12*T-cl, W-12*T, H-12*T], fill=ACCENT)

    # "CISCO CERTIFICATION" top
    f_top = tfont('JetBrainsMono', 11)
    text_top = 'CISCO CERTIFICATION'
    bbox = d.textbbox((0,0), text_top, font=f_top)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, 42*T), text_top, fill=WHITE, font=f_top)

    # "CCNA" centered large
    f_ccna = tfont('BigShoulders-Bold', 140)
    bbox = d.textbbox((0,0), 'CCNA', font=f_ccna)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text(((W-tw)//2, H//2 - th - 30*T), 'CCNA', fill=WHITE, font=f_ccna)

    # "200-301"
    f_code = tfont('GeistMono-Bold', 44)
    bbox = d.textbbox((0,0), '200-301', font=f_code)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H//2 + 10*T), '200-301', fill=ACCENT, font=f_code)

    # Divider
    d.line([(160*T, H//2 + 65*T), (W-160*T, H//2 + 65*T)], fill=BORDER, width=T)

    # "STUDY SYSTEM"
    f_sub = tfont('Outfit-Bold', 24)
    bbox = d.textbbox((0,0), 'STUDY SYSTEM', font=f_sub)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H//2 + 80*T), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    # Feature count
    f_feat = tfont('JetBrainsMono', 10)
    feat_text = '10 DBs  |  30+ Views  |  DoK Framework'
    bbox = d.textbbox((0,0), feat_text, font=f_feat)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 100*T), feat_text, fill=WHITE, font=f_feat)

    # "// NOTION TEMPLATE"
    f_tag = tfont('JetBrainsMono', 12)
    tag_text = '// NOTION TEMPLATE'
    bbox = d.textbbox((0,0), tag_text, font=f_tag)
    tw = bbox[2] - bbox[0]
    d.text(((W-tw)//2, H - 68*T), tag_text, fill=ACCENT, font=f_tag)

    # Downscale 6x to 600x600
    final = img.resize((600, 600), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'ccna-thumb-gold-600x600.png')
    final.save(path, 'PNG', optimize=True)
    print(f"[OK] Thumb: {path} (600x600, {T}x supersampled)")


if __name__ == '__main__':
    print("Generating high-quality PNGs...")
    create_cover()
    create_thumbnail()

    # Verify
    for f in ['ccna-cover-gold-1280x1280.png', 'ccna-thumb-gold-600x600.png']:
        p = os.path.join(OUT_DIR, f)
        img = Image.open(p)
        kb = os.path.getsize(p) / 1024
        print(f"  {f}: {img.size[0]}x{img.size[1]}, {kb:.0f}KB")
    print("Done.")
