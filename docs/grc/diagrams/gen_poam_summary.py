#!/usr/bin/env python3
"""Generate POA&M Status donut chart."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Config ---
BG = '#0d1117'
TEXT = '#ffffff'
GREEN = '#00FF41'
FONT = 'JetBrains Mono'
DPI = 300
OUT = './diagrams/poam_summary.png'

plt.rcParams.update({
    'font.family': FONT,
    'text.color': TEXT,
    'axes.labelcolor': TEXT,
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'savefig.facecolor': BG,
})

# Data
labels = ['Accepted Risk', 'Open', 'Closed']
sizes = [16, 10, 1]
colors = ['#d4a017', '#e63946', '#2ea043']
explode = (0.03, 0.03, 0.03)
total = sum(sizes)

fig, ax = plt.subplots(figsize=(8, 8))

wedges, texts, autotexts = ax.pie(
    sizes, labels=None, autopct=lambda pct: f'{int(round(pct * total / 100))}',
    startangle=90, colors=colors, explode=explode,
    pctdistance=0.78,
    wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=2),
    textprops=dict(color=TEXT, fontsize=14, fontweight='bold')
)

# Style the percentage text
for autotext in autotexts:
    autotext.set_fontsize(16)
    autotext.set_fontweight('bold')

# Center text
ax.text(0, 0.05, str(total), fontsize=48, fontweight='bold', ha='center', va='center', color=TEXT)
ax.text(0, -0.12, 'FINDINGS', fontsize=11, fontweight='bold', ha='center', va='center', color='#888888')

# Legend with counts
legend_labels = [f'{l} ({s})' for l, s in zip(labels, sizes)]
leg = ax.legend(wedges, legend_labels, loc='lower center',
                fontsize=11, facecolor='#1a1a2e', edgecolor='#444',
                labelcolor=TEXT, framealpha=0.9, ncol=3,
                bbox_to_anchor=(0.5, -0.05), borderpad=1)

ax.set_title('POA&M STATUS BREAKDOWN\nPlan of Action & Milestones',
             fontsize=14, fontweight='bold', pad=20, color=TEXT)

# Add percentage labels outside
for i, (wedge, label, size) in enumerate(zip(wedges, labels, sizes)):
    angle = (wedge.theta2 + wedge.theta1) / 2
    import numpy as np
    x = 0.65 * np.cos(np.radians(angle))
    y = 0.65 * np.sin(np.radians(angle))
    pct = size / total * 100
    # Place percentage text on the wedge outer edge
    x2 = 1.15 * np.cos(np.radians(angle))
    y2 = 1.15 * np.sin(np.radians(angle))
    ha = 'left' if x2 > 0 else 'right'
    ax.text(x2, y2, f'{label}\n{pct:.0f}%', fontsize=9,
            ha=ha, va='center', color=colors[i], fontweight='bold')

plt.tight_layout()
plt.savefig(OUT, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
