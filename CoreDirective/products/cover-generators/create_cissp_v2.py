#!/usr/bin/env python3
"""CISSP GREEN - Updated thumbnail (600x600) and cover (1280x720).
Stats updated: 57+ Views, added selling points, top label = ISC2 CERTIFICATION."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/Users/et/cyber-squire-ops/.claude/skills/canvas-design/canvas-fonts"
OUT_DIR = "/Users/et/cyber-squire-ops/builds/gumroad-assets"
os.makedirs(OUT_DIR, exist_ok=True)

# Colors — Directed Signal brand
BG     = '#0D1117'
BG2    = '#161B22'
ACCENT = '#00E676'
WHITE  = '#E6EDF3'
GRAY   = '#8B949E'
DIM    = '#21262D'
BORDER = '#30363D'


def F(name, size, scale=1):
    """Load a font at size*scale."""
    paths = {
        'BigShoulders-Bold': 'BigShoulders-Bold.ttf',
        'JetBrainsMono':     'JetBrainsMono-Regular.ttf',
        'JetBrainsMono-Bold':'JetBrainsMono-Bold.ttf',
        'Outfit':            'Outfit-Regular.ttf',
        'Outfit-Bold':       'Outfit-Bold.ttf',
    }
    return ImageFont.truetype(os.path.join(FONT_DIR, paths[name]), int(size * scale))


# ─────────────────────────────────────────────
# THUMBNAIL  600 × 600
# ─────────────────────────────────────────────
def create_thumbnail():
    S = 6                          # render at 3600×3600, downsample to 600×600
    W, H = 600 * S, 600 * S
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # Dot grid
    for x in range(25 * S, W, 25 * S):
        for y in range(25 * S, H, 25 * S):
            r = S
            d.ellipse([x - r, y - r, x + r, y + r], fill=DIM)

    # Rounded border + corner accents
    d.rounded_rectangle([12*S, 12*S, W-12*S, H-12*S],
                        radius=6*S, outline=ACCENT, width=3*S)
    cl = 50 * S
    # top-left
    d.rectangle([12*S,          12*S,          12*S+cl,      12*S+3*S],    fill=ACCENT)
    d.rectangle([12*S,          12*S,          12*S+3*S,     12*S+cl],     fill=ACCENT)
    # bottom-right
    d.rectangle([W-12*S-cl,     H-12*S-3*S,    W-12*S,       H-12*S],      fill=ACCENT)
    d.rectangle([W-12*S-3*S,    H-12*S-cl,     W-12*S,       H-12*S],      fill=ACCENT)

    # ── TOP LABEL: "ISC2 CERTIFICATION" ──
    f_top = F('JetBrainsMono', 11, S)
    top_text = 'ISC2 CERTIFICATION'
    bbox = d.textbbox((0, 0), top_text, font=f_top)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 42 * S), top_text, fill=GRAY, font=f_top)

    # ── "CISSP" huge ──
    f_title = F('BigShoulders-Bold', 140, S)
    bbox = d.textbbox((0, 0), 'CISSP', font=f_title)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    title_y = H // 2 - th - 20 * S
    d.text(((W - tw) // 2, title_y), 'CISSP', fill=WHITE, font=f_title)

    # Divider
    div_y = H // 2 + 28 * S
    d.line([(140 * S, div_y), (W - 140 * S, div_y)], fill=BORDER, width=S)

    # ── "STUDY SYSTEM" ──
    f_sub = F('Outfit-Bold', 24, S)
    bbox = d.textbbox((0, 0), 'STUDY SYSTEM', font=f_sub)
    tw = bbox[2] - bbox[0]
    sub_y = div_y + 14 * S
    d.text(((W - tw) // 2, sub_y), 'STUDY SYSTEM', fill=WHITE, font=f_sub)

    # ── Stats line (UPDATED: 57+ Views) ──
    f_feat = F('JetBrainsMono', 10, S)
    feat_text = '10 DBs  |  57+ Views  |  DoK Framework'
    bbox = d.textbbox((0, 0), feat_text, font=f_feat)
    tw = bbox[2] - bbox[0]
    stats_y = H - 110 * S
    d.text(((W - tw) // 2, stats_y), feat_text, fill=WHITE, font=f_feat)

    # ── "// NOTION TEMPLATE" ──
    f_tag = F('JetBrainsMono', 12, S)
    tag_text = '// NOTION TEMPLATE'
    bbox = d.textbbox((0, 0), tag_text, font=f_tag)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, H - 72 * S), tag_text, fill=ACCENT, font=f_tag)

    out = img.resize((600, 600), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'cissp-thumb-green-600x600.png')
    out.save(path, 'PNG', optimize=True)
    print(f'[OK] Thumb: {path}')


# ─────────────────────────────────────────────
# COVER  1280 × 720
# ─────────────────────────────────────────────
def create_cover():
    S = 6                          # render at 7680×4320, downsample to 1280×720
    W, H = 1280 * S, 720 * S
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # Dot grid
    for x in range(40 * S, W, 40 * S):
        for y in range(40 * S, H, 40 * S):
            r = int(1.5 * S)
            d.ellipse([x - r, y - r, x + r, y + r], fill=DIM)

    # Left accent bar
    d.rectangle([0, 0, 5 * S, H], fill=ACCENT)

    # Corner brackets — TL + BR accent, TR + BL dim
    lw  = int(2.5 * S)
    lw2 = int(1.5 * S)
    blen = 72 * S
    # TL — green
    d.line([(28*S, 28*S), (28*S, 28*S + blen)], fill=ACCENT, width=lw)
    d.line([(28*S, 28*S), (28*S + blen, 28*S)], fill=ACCENT, width=lw)
    # BR — green
    d.line([(W-28*S, H-28*S), (W-28*S, H-28*S - blen)], fill=ACCENT, width=lw)
    d.line([(W-28*S, H-28*S), (W-28*S - blen, H-28*S)], fill=ACCENT, width=lw)
    # TR — dim
    d.line([(W-28*S, 28*S), (W-28*S, 28*S + blen//2)], fill=BORDER, width=lw2)
    d.line([(W-28*S, 28*S), (W-28*S - blen//2, 28*S)], fill=BORDER, width=lw2)
    # BL — dim
    d.line([(28*S, H-28*S), (28*S, H-28*S - blen//2)], fill=BORDER, width=lw2)
    d.line([(28*S, H-28*S), (28*S + blen//2, H-28*S)], fill=BORDER, width=lw2)

    # ══════════════════════════════════
    # LEFT COLUMN  (x 80–620)
    # ══════════════════════════════════
    lx = 80 * S

    # "ISC2 CERTIFICATION" micro-label
    f_micro = F('JetBrainsMono', 11, S)
    d.text((lx, 44 * S), 'ISC2 CERTIFICATION', fill=GRAY, font=f_micro)

    # "CISSP" massive
    f_title = F('BigShoulders-Bold', 196, S)
    title_y = 62 * S
    d.text((lx, title_y), 'CISSP', fill=WHITE, font=f_title)
    bbox_t = d.textbbox((lx, title_y), 'CISSP', font=f_title)

    # Divider
    div_y = bbox_t[3] + 20 * S
    d.line([(lx, div_y), (lx + 280 * S, div_y)], fill=BORDER, width=S)

    # "STUDY SYSTEM"
    f_sub = F('Outfit-Bold', 28, S)
    sub_y = div_y + 18 * S
    d.text((lx, sub_y), 'STUDY SYSTEM', fill=WHITE, font=f_sub)
    bbox_s = d.textbbox((lx, sub_y), 'STUDY SYSTEM', font=f_sub)

    # "// NOTION TEMPLATE"
    f_tag = F('JetBrainsMono', 13, S)
    tag_y = bbox_s[3] + 14 * S
    d.text((lx, tag_y), '// NOTION TEMPLATE', fill=ACCENT, font=f_tag)
    bbox_tag = d.textbbox((lx, tag_y), '// NOTION TEMPLATE', font=f_tag)

    # Selling points (bullet list) — below // NOTION TEMPLATE
    bullets = [
        '62 ISC2 Objectives Mapped',
        '44 Frameworks & Standards',
        '202 Terminology Terms',
        '13 Security Models',
        'Think Like a Manager',
    ]
    f_bullet = F('Outfit', 13, S)
    by = bbox_tag[3] + 28 * S
    br = 4 * S
    row_gap = 30 * S
    for i, pt in enumerate(bullets):
        bx = lx
        cy_dot = by + i * row_gap + 10 * S
        d.ellipse([bx - br, cy_dot - br, bx + br, cy_dot + br], fill=ACCENT)
        d.text((bx + br + 10 * S, by + i * row_gap - 2 * S), pt, fill=WHITE, font=f_bullet)

    # Stats bar near bottom-left
    stats_y = H - 58 * S
    f_stats = F('JetBrainsMono', 10, S)
    stats_text = '10 DBs  |  57+ Views  |  35 Crypto Entries  |  13 Scenarios'
    d.text((lx, stats_y), stats_text, fill=GRAY, font=f_stats)

    # "CoreDirective" branding
    f_brand = F('Outfit-Bold', 11, S)
    brand_text = 'CoreDirective'
    bbox_b = d.textbbox((0, 0), brand_text, font=f_brand)
    d.text((lx, stats_y + (bbox_b[3]-bbox_b[1]) + 10 * S), brand_text, fill=ACCENT, font=f_brand)

    # ══════════════════════════════════
    # RIGHT COLUMN  — Feature card
    # ══════════════════════════════════
    SPLIT = 640 * S        # center divider
    card_x = SPLIT + 30 * S
    card_y = 44 * S
    card_w = W - card_x - 44 * S
    card_h = H - 88 * S

    # Card shadow + body
    d.rounded_rectangle([card_x + 4*S, card_y + 4*S, card_x + card_w + 4*S, card_y + card_h + 4*S],
                        radius=10*S, fill='#080B10')
    d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                        radius=10*S, fill=BG2)
    d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                        radius=10*S, outline=BORDER, width=S)
    # Top green accent strip
    d.rectangle([card_x + 6*S, card_y, card_x + card_w - 6*S, card_y + 3*S], fill=ACCENT)

    # Card header
    f_ch = F('JetBrainsMono', 10, S)
    d.text((card_x + 22*S, card_y + 14*S), 'SYSTEM COMPONENTS', fill=WHITE, font=f_ch)
    d.line([(card_x + 22*S, card_y + 34*S), (card_x + card_w - 22*S, card_y + 34*S)],
           fill=BORDER, width=S)

    features = [
        ('10',   'Databases'),
        ('57+',  'Custom Views'),
        ('8',    'Exam Domains'),
        ('62',   'Objectives'),
        ('13',   'Security Models'),
        ('4',    'DoK Levels'),
        ('35+',  'Crypto Entries'),
        ('13',   'Scenario Labs'),
        ('Live', 'Dashboard'),
    ]

    cols = 3
    col_w  = (card_w - 50 * S) // cols
    row_h  = (card_h - 110 * S) // 3
    sx     = card_x + 26 * S
    sy     = card_y  + 46 * S
    f_num  = F('BigShoulders-Bold', 38, S)
    f_lbl  = F('Outfit', 11, S)

    for i, (num, label) in enumerate(features):
        col = i % cols
        row = i // cols
        fx  = sx + col * col_w
        fy  = sy + row * row_h
        d.text((fx, fy), num, fill=ACCENT, font=f_num)
        nb  = d.textbbox((fx, fy), num, font=f_num)
        d.text((fx, nb[3] + 3*S), label, fill=WHITE, font=f_lbl)

    # Card footer
    bot_y = card_y + card_h - 44 * S
    d.line([(card_x + 22*S, bot_y), (card_x + card_w - 22*S, bot_y)], fill=BORDER, width=S)
    f_ft = F('JetBrainsMono', 9, S)
    footer = 'ADHD-Friendly  //  Lifetime Updates  //  7-Day Guarantee'
    fb = d.textbbox((0, 0), footer, font=f_ft)
    fw = fb[2] - fb[0]
    d.text((card_x + (card_w - fw) // 2, bot_y + 14 * S), footer, fill=GRAY, font=f_ft)

    out = img.resize((1280, 720), Image.LANCZOS)
    path = os.path.join(OUT_DIR, 'cissp-cover-green-1280x720.png')
    out.save(path, 'PNG', optimize=True)
    print(f'[OK] Cover: {path}')


if __name__ == '__main__':
    print('Generating CISSP v2 assets (updated stats, ISC2 label, selling points)...')
    create_thumbnail()
    create_cover()

    for fname in ['cissp-thumb-green-600x600.png', 'cissp-cover-green-1280x720.png']:
        p = os.path.join(OUT_DIR, fname)
        im = Image.open(p)
        kb = os.path.getsize(p) / 1024
        print(f'  {fname}: {im.size[0]}x{im.size[1]}, {kb:.0f} KB')

    print('Done.')
