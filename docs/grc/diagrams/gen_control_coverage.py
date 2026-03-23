#!/usr/bin/env python3
"""Generate NIST 800-53 Control Coverage horizontal stacked bar chart."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# --- Config ---
BG = '#0d1117'
TEXT = '#ffffff'
GREEN = '#00FF41'
FONT = 'JetBrains Mono'
DPI = 300
OUT = './diagrams/control_coverage.png'

plt.rcParams.update({
    'font.family': FONT,
    'text.color': TEXT,
    'axes.labelcolor': TEXT,
    'xtick.color': TEXT,
    'ytick.color': TEXT,
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'savefig.facecolor': BG,
})

# Data: family, implemented, partial, planned, na, inherited
data = [
    ('AC',  8,  3, 1, 0, 0),
    ('AU', 10,  2, 0, 0, 0),
    ('CA',  5,  1, 0, 0, 0),
    ('CM',  8,  0, 0, 0, 0),
    ('CP',  3,  5, 0, 0, 0),
    ('IA',  7,  2, 0, 1, 0),
    ('IR',  5,  3, 0, 0, 0),
    ('MA',  4,  2, 0, 0, 0),
    ('MP',  3,  1, 0, 0, 2),
    ('PE',  0,  0, 0, 0, 1),
    ('PL',  2,  0, 1, 0, 0),
    ('PS',  0,  2, 1, 5, 0),
    ('RA',  4,  0, 0, 0, 0),
    ('SA',  8,  1, 0, 0, 0),
    ('SC', 13,  2, 0, 3, 3),
    ('SI',  7,  3, 0, 1, 0),
]

families = [d[0] for d in data]
implemented = [d[1] for d in data]
partial     = [d[2] for d in data]
planned     = [d[3] for d in data]
na          = [d[4] for d in data]
inherited   = [d[5] for d in data]
totals      = [sum(d[1:]) for d in data]

# Colors
c_impl     = '#2ea043'  # green
c_partial  = '#d4a017'  # yellow/gold
c_planned  = '#da6d28'  # orange
c_na       = '#555555'  # gray
c_inher    = '#3b82f6'  # blue

fig, ax = plt.subplots(figsize=(14, 8))

y = np.arange(len(families))
bar_height = 0.65

# Stack the bars
b1 = ax.barh(y, implemented, bar_height, label='Implemented', color=c_impl, edgecolor='none')
b2 = ax.barh(y, partial,     bar_height, left=np.array(implemented), label='Partial', color=c_partial, edgecolor='none')
left2 = np.array(implemented) + np.array(partial)
b3 = ax.barh(y, planned,     bar_height, left=left2, label='Planned', color=c_planned, edgecolor='none')
left3 = left2 + np.array(planned)
b4 = ax.barh(y, na,          bar_height, left=left3, label='N/A', color=c_na, edgecolor='none')
left4 = left3 + np.array(na)
b5 = ax.barh(y, inherited,   bar_height, left=left4, label='Inherited', color=c_inher, edgecolor='none')

# Total count label on each bar
for i, total in enumerate(totals):
    ax.text(total + 0.3, i, str(total), va='center', ha='left',
            fontsize=9, color=TEXT, fontweight='bold')

# Add count labels inside bar segments (only if segment > 0)
for bars, values in [(b1, implemented), (b2, partial), (b3, planned), (b4, na), (b5, inherited)]:
    for bar, val in zip(bars, values):
        if val > 0:
            cx = bar.get_x() + bar.get_width() / 2
            cy = bar.get_y() + bar.get_height() / 2
            ax.text(cx, cy, str(val), va='center', ha='center',
                    fontsize=7, color='#000000' if val > 1 else '#ffffff', fontweight='bold')

ax.set_yticks(y)
ax.set_yticklabels(families, fontsize=10, fontweight='bold')
ax.invert_yaxis()
ax.set_xlabel('Number of Controls', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('NIST 800-53 Control Implementation by Family\n16 Control Families - Organization Security Stack',
             fontsize=13, fontweight='bold', pad=20, color=TEXT)

# Spines
for spine in ax.spines.values():
    spine.set_color('#333333')
ax.tick_params(axis='both', colors=TEXT)
ax.set_xlim(0, max(totals) + 2.5)

# Legend
leg = ax.legend(loc='lower right', fontsize=9, facecolor='#1a1a2e',
                edgecolor='#444', labelcolor=TEXT, framealpha=0.9,
                ncol=5, borderpad=0.8)

# Summary stats
total_controls = sum(totals)
total_impl = sum(implemented)
total_partial = sum(partial)
pct = (total_impl / total_controls) * 100 if total_controls else 0
pct_with_partial = ((total_impl + total_partial) / total_controls) * 100 if total_controls else 0

summary = f'Total Controls: {total_controls}  |  Fully Implemented: {total_impl} ({pct:.0f}%)  |  Impl+Partial: {total_impl+total_partial} ({pct_with_partial:.0f}%)'
ax.text(0.5, -0.08, summary, transform=ax.transAxes, fontsize=8.5,
        ha='center', va='top', color=GREEN, fontweight='bold')

plt.tight_layout()
plt.savefig(OUT, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
