#!/usr/bin/env python3
"""Generate 5x5 Risk Heat Map with inherent→residual arrows."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# --- Config ---
BG = '#0d1117'
TEXT = '#ffffff'
GREEN = '#00FF41'
FONT = 'JetBrains Mono'
DPI = 300
OUT = './diagrams/risk_heat_map.png'

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

# Risk data: (ID, label, inh_likelihood, inh_impact, res_likelihood, res_impact)
risks = [
    ('R-01', 'DDoS',                3, 3, 2, 3),
    ('R-02', 'Brute Force',         4, 3, 2, 3),
    ('R-03', 'Supply Chain',        2, 5, 1, 5),
    ('R-04', 'Webhook Exploit',     3, 4, 2, 4),
    ('R-05', 'Credential Phishing', 2, 4, 1, 4),
    ('R-06', 'Zero-Day',            1, 5, 1, 5),
    ('R-07', 'Container Misconfig', 3, 3, 2, 3),
    ('R-08', 'Privilege Escalation',2, 5, 1, 5),
    ('R-09', 'Insider Threat',      1, 5, 1, 4),
    ('R-10', 'Secret Exposure',     3, 5, 2, 5),
    ('R-11', 'Unauth Config Change',2, 4, 1, 4),
    ('R-12', 'DO Outage',           2, 4, 2, 3),
    ('R-13', 'Hardware Failure',    1, 4, 1, 3),
    ('R-14', 'Data Loss',           2, 5, 2, 4),
    ('R-15', 'Regulatory Changes',  2, 3, 2, 2),
    ('R-16', 'POAM Remed. Failure', 3, 3, 2, 3),
    ('R-17', 'Breach Notification', 1, 5, 1, 4),
]

# Build 5x5 score matrix for background colors
score_matrix = np.zeros((5, 5))
for row in range(5):
    for col in range(5):
        score_matrix[row, col] = (row + 1) * (col + 1)

# Color thresholds: 1-6 green, 7-14 yellow, 15-19 orange, 20-25 red
def score_color(s):
    if s <= 6:
        return '#1a5c2a'   # dark green
    elif s <= 14:
        return '#7a6c00'   # dark yellow
    elif s <= 19:
        return '#8a4500'   # dark orange
    else:
        return '#8a1515'   # dark red

fig, ax = plt.subplots(figsize=(12, 10))

# Draw grid cells with colors
for row in range(5):
    for col in range(5):
        score = (row + 1) * (col + 1)
        color = score_color(score)
        rect = mpatches.FancyBboxPatch(
            (col, row), 1, 1,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor='#333333', linewidth=0.5, alpha=0.85
        )
        ax.add_patch(rect)
        # Score number in corner
        ax.text(col + 0.92, row + 0.08, str(score),
                fontsize=7, color='#888888', ha='right', va='bottom', alpha=0.6)

# Plot risk positions - need to handle overlapping points with jitter
def jitter_positions(points, jitter_amount=0.12):
    """Add jitter to overlapping positions."""
    from collections import Counter
    counts = Counter([(p[0], p[1]) for p in points])
    position_index = {}
    result = []
    for px, py, rid in points:
        key = (px, py)
        if key not in position_index:
            position_index[key] = 0
        idx = position_index[key]
        total = counts[key]
        if total == 1:
            dx, dy = 0, 0
        else:
            angle = (2 * np.pi * idx) / total
            dx = jitter_amount * np.cos(angle)
            dy = jitter_amount * np.sin(angle)
        result.append((px + dx, py + dy, rid))
        position_index[key] += 1
    return result

# Inherent positions (impact=x, likelihood=y), centered in cell
inh_points = [(r[3] - 0.5, r[2] - 0.5, r[0]) for r in risks]  # impact-1+0.5, likelihood-1+0.5
res_points = [(r[5] - 0.5, r[4] - 0.5, r[0]) for r in risks]

inh_jittered = jitter_positions(inh_points)
res_jittered = jitter_positions(res_points)

# Draw arrows from inherent to residual
for i in range(len(risks)):
    ix, iy = inh_jittered[i][0], inh_jittered[i][1]
    rx, ry = res_jittered[i][0], res_jittered[i][1]
    if abs(ix - rx) > 0.01 or abs(iy - ry) > 0.01:  # Only draw if positions differ
        ax.annotate('', xy=(rx, ry), xytext=(ix, iy),
                    arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.2, alpha=0.5,
                                   connectionstyle='arc3,rad=0.1'))

# Plot inherent positions (hollow circles)
for x, y, rid in inh_jittered:
    ax.plot(x, y, 'o', markersize=10, markerfacecolor='none',
            markeredgecolor='#ff6b6b', markeredgewidth=2, zorder=5)
    ax.text(x, y + 0.18, rid, fontsize=5.5, color='#ff6b6b',
            ha='center', va='bottom', fontweight='bold', zorder=6)

# Plot residual positions (filled circles)
for x, y, rid in res_jittered:
    ax.plot(x, y, 'o', markersize=10, markerfacecolor=GREEN,
            markeredgecolor=GREEN, markeredgewidth=1.5, alpha=0.85, zorder=5)
    ax.text(x, y - 0.18, rid, fontsize=5.5, color=GREEN,
            ha='center', va='top', fontweight='bold', zorder=6)

# Axes
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
ax.set_xticklabels(['Very Low\n(1)', 'Low\n(2)', 'Moderate\n(3)', 'High\n(4)', 'Very High\n(5)'], fontsize=9)
ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5])
ax.set_yticklabels(['Very Low\n(1)', 'Low\n(2)', 'Moderate\n(3)', 'High\n(4)', 'Very High\n(5)'], fontsize=9)
ax.set_xlabel('IMPACT', fontsize=12, fontweight='bold', labelpad=10)
ax.set_ylabel('LIKELIHOOD', fontsize=12, fontweight='bold', labelpad=10)

# Grid lines
for i in range(6):
    ax.axhline(y=i, color='#333333', linewidth=0.5)
    ax.axvline(x=i, color='#333333', linewidth=0.5)

# Title
ax.set_title('RISK HEAT MAP - Inherent vs Residual Positions\n17 Identified Risks',
             fontsize=14, fontweight='bold', pad=20, color=TEXT)

# Legend
legend_elements = [
    mpatches.Patch(facecolor='none', edgecolor='#ff6b6b', linewidth=2, label='Inherent Risk'),
    mpatches.Patch(facecolor=GREEN, edgecolor=GREEN, label='Residual Risk'),
    mpatches.FancyArrowPatch((0, 0), (1, 0), arrowstyle='->', color=GREEN, label='Risk Reduction'),
    mpatches.Patch(facecolor='#1a5c2a', label='Low (1-6)'),
    mpatches.Patch(facecolor='#7a6c00', label='Moderate (7-14)'),
    mpatches.Patch(facecolor='#8a4500', label='High (15-19)'),
    mpatches.Patch(facecolor='#8a1515', label='Critical (20-25)'),
]
from matplotlib.lines import Line2D
legend_elements_v2 = [
    Line2D([0], [0], marker='o', color='none', markerfacecolor='none',
           markeredgecolor='#ff6b6b', markeredgewidth=2, markersize=10, label='Inherent Risk'),
    Line2D([0], [0], marker='o', color='none', markerfacecolor=GREEN,
           markeredgecolor=GREEN, markersize=10, label='Residual Risk'),
    Line2D([0], [0], color=GREEN, linewidth=1.5, label='Risk Reduction →'),
    mpatches.Patch(facecolor='#1a5c2a', edgecolor='#555', label='Low (1-6)'),
    mpatches.Patch(facecolor='#7a6c00', edgecolor='#555', label='Moderate (7-14)'),
    mpatches.Patch(facecolor='#8a4500', edgecolor='#555', label='High (15-19)'),
    mpatches.Patch(facecolor='#8a1515', edgecolor='#555', label='Critical (20-25)'),
]
leg = ax.legend(handles=legend_elements_v2, loc='upper left', fontsize=7.5,
                facecolor='#1a1a2e', edgecolor='#444', labelcolor=TEXT,
                framealpha=0.9, borderpad=1)

ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(OUT, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
