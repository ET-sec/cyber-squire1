#!/usr/bin/env python3
"""Generate 2x2 Risk Summary Dashboard."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- Config ---
BG = '#0d1117'
PANEL_BG = '#161b22'
TEXT = '#ffffff'
GREEN = '#00FF41'
FONT = 'JetBrains Mono'
DPI = 300
OUT = '/Users/et/cyber-squire-ops/docs/grc/diagrams/risk_summary_dashboard.png'

plt.rcParams.update({
    'font.family': FONT,
    'text.color': TEXT,
    'axes.labelcolor': TEXT,
    'xtick.color': TEXT,
    'ytick.color': TEXT,
    'figure.facecolor': BG,
    'axes.facecolor': PANEL_BG,
    'savefig.facecolor': BG,
})

fig = plt.figure(figsize=(20, 14))
fig.suptitle('RISK SUMMARY DASHBOARD — Organization Security Posture',
             fontsize=16, fontweight='bold', color=TEXT, y=0.97)

# ============================================================
# TOP-LEFT: Risk Distribution Pie by Category
# ============================================================
ax1 = fig.add_subplot(2, 2, 1)
ax1.set_facecolor(PANEL_BG)

categories = ['External', 'Internal', 'Environmental', 'Compliance']
cat_sizes = [6, 5, 3, 3]
cat_colors = ['#e63946', '#d4a017', '#3b82f6', '#8b5cf6']
explode = (0.04, 0.04, 0.04, 0.04)

wedges, texts, autotexts = ax1.pie(
    cat_sizes, labels=None, autopct='%1.0f%%',
    startangle=140, colors=cat_colors, explode=explode,
    pctdistance=0.75,
    wedgeprops=dict(width=0.5, edgecolor=BG, linewidth=2),
    textprops=dict(color=TEXT, fontsize=10, fontweight='bold')
)

for at in autotexts:
    at.set_fontsize(11)
    at.set_fontweight('bold')

# Center text
ax1.text(0, 0.05, '17', fontsize=32, fontweight='bold', ha='center', va='center', color=TEXT)
ax1.text(0, -0.1, 'RISKS', fontsize=9, ha='center', va='center', color='#888888', fontweight='bold')

# Legend
legend_labels = [f'{c} ({s})' for c, s in zip(categories, cat_sizes)]
ax1.legend(wedges, legend_labels, loc='lower center',
           fontsize=8.5, facecolor='#1a1a2e', edgecolor='#444',
           labelcolor=TEXT, framealpha=0.9, ncol=2,
           bbox_to_anchor=(0.5, -0.08), borderpad=0.8)

ax1.set_title('Risk Distribution by Category', fontsize=11, fontweight='bold', pad=12, color=TEXT)

# ============================================================
# TOP-RIGHT: Inherent vs Residual Risk Score Comparison
# ============================================================
ax2 = fig.add_subplot(2, 2, 2)
ax2.set_facecolor(PANEL_BG)

risk_ids = [f'R-{i:02d}' for i in range(1, 18)]
inherent_scores = [9, 12, 10, 12, 8, 5, 9, 10, 5, 15, 8, 8, 4, 10, 6, 9, 5]
residual_scores = [6,  6,  5,  8, 4, 5, 6,  5, 4, 10, 4, 6, 3,  8, 4, 6, 4]

x = np.arange(len(risk_ids))
width = 0.35

bars1 = ax2.bar(x - width/2, inherent_scores, width, label='Inherent',
                color='#e63946', edgecolor='none', alpha=0.85)
bars2 = ax2.bar(x + width/2, residual_scores, width, label='Residual',
                color=GREEN, edgecolor='none', alpha=0.85)

ax2.set_xticks(x)
ax2.set_xticklabels(risk_ids, fontsize=6.5, rotation=45, ha='right')
ax2.set_ylabel('Risk Score (L x I)', fontsize=9, fontweight='bold')
ax2.set_title('Inherent vs Residual Risk Scores', fontsize=11, fontweight='bold', pad=12, color=TEXT)

# Add value labels on bars
for bar in bars1:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.2, str(int(h)),
             ha='center', va='bottom', fontsize=6, color='#ff6b6b', fontweight='bold')
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., h + 0.2, str(int(h)),
             ha='center', va='bottom', fontsize=6, color=GREEN, fontweight='bold')

ax2.set_ylim(0, max(inherent_scores) + 2.5)
ax2.legend(loc='upper right', fontsize=9, facecolor='#1a1a2e',
           edgecolor='#444', labelcolor=TEXT, framealpha=0.9)

for spine in ax2.spines.values():
    spine.set_color('#333333')
ax2.tick_params(axis='both', colors=TEXT)
ax2.grid(axis='y', alpha=0.15, color='#555555')

# Summary stat
avg_inh = np.mean(inherent_scores)
avg_res = np.mean(residual_scores)
reduction = ((avg_inh - avg_res) / avg_inh) * 100
ax2.text(0.5, -0.18, f'Avg Inherent: {avg_inh:.1f}  |  Avg Residual: {avg_res:.1f}  |  Reduction: {reduction:.0f}%',
         transform=ax2.transAxes, fontsize=8, ha='center', color=GREEN, fontweight='bold')

# ============================================================
# BOTTOM-LEFT: FIPS 199 Categorization
# ============================================================
ax3 = fig.add_subplot(2, 2, 3)
ax3.set_facecolor(PANEL_BG)
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.axis('off')

ax3.set_title('FIPS 199 Security Categorization', fontsize=11, fontweight='bold', pad=12, color=TEXT)

# Draw badge-style display
badge_color = '#d4a017'  # amber for MODERATE

# Main badge
badge = mpatches.FancyBboxPatch((2.5, 4.5), 5, 2.5, boxstyle="round,pad=0.3",
                                 facecolor='none', edgecolor=badge_color, linewidth=3)
ax3.add_patch(badge)
ax3.text(5, 6.2, 'OVERALL', fontsize=10, ha='center', va='center', color='#888888', fontweight='bold')
ax3.text(5, 5.2, 'MODERATE', fontsize=22, ha='center', va='center', color=badge_color, fontweight='bold')

# Three category boxes
cats = [
    ('Confidentiality', 'MODERATE', 1.0),
    ('Integrity', 'MODERATE', 4.0),
    ('Availability', 'MODERATE', 7.0),
]

for label, level, xpos in cats:
    box = mpatches.FancyBboxPatch((xpos, 1.2), 2.5, 2.5, boxstyle="round,pad=0.2",
                                   facecolor='#1a1a2e', edgecolor='#444', linewidth=1.5)
    ax3.add_patch(box)
    ax3.text(xpos + 1.25, 3.0, label, fontsize=7.5, ha='center', va='center',
             color='#aaaaaa', fontweight='bold')
    ax3.text(xpos + 1.25, 2.0, level, fontsize=11, ha='center', va='center',
             color=badge_color, fontweight='bold')

# FIPS formula
ax3.text(5, 0.5, 'SC = {(confidentiality, MODERATE), (integrity, MODERATE), (availability, MODERATE)}',
         fontsize=7, ha='center', va='center', color='#666666', style='italic')

# ============================================================
# BOTTOM-RIGHT: Finding Severity Breakdown by Source
# ============================================================
ax4 = fig.add_subplot(2, 2, 4)
ax4.set_facecolor(PANEL_BG)

# Sources and severities
sources = ['CIS Docker\nBench', 'Checkov\nIaC Scan', 'Risk Assessment\nMitigations']
critical = [0, 0, 0]
high =     [0, 0, 0]
medium =   [2, 0, 5]
low =      [27, 3, 0]
totals =   [29, 3, 5]

x = np.arange(len(sources))
width = 0.5

# Stacked bars
b_low = ax4.bar(x, low, width, label='Low', color='#2ea043', edgecolor='none')
b_med = ax4.bar(x, medium, width, bottom=low, label='Medium', color='#d4a017', edgecolor='none')
b_high = ax4.bar(x, high, width, bottom=np.array(low)+np.array(medium), label='High', color='#da6d28', edgecolor='none')
b_crit = ax4.bar(x, critical, width, bottom=np.array(low)+np.array(medium)+np.array(high), label='Critical', color='#e63946', edgecolor='none')

# Total labels
for i, total in enumerate(totals):
    ax4.text(i, total + 0.5, str(total), ha='center', va='bottom',
             fontsize=12, color=TEXT, fontweight='bold')

# Value labels inside segments
for bars_list, vals in [(b_low, low), (b_med, medium)]:
    for bar, val in zip(bars_list, vals):
        if val > 0:
            cx = bar.get_x() + bar.get_width() / 2
            cy = bar.get_y() + bar.get_height() / 2
            ax4.text(cx, cy, str(val), ha='center', va='center',
                     fontsize=9, color='#000000', fontweight='bold')

ax4.set_xticks(x)
ax4.set_xticklabels(sources, fontsize=8.5)
ax4.set_ylabel('Number of Findings', fontsize=9, fontweight='bold')
ax4.set_title('Finding Severity by Source', fontsize=11, fontweight='bold', pad=12, color=TEXT)
ax4.set_ylim(0, max(totals) + 4)

for spine in ax4.spines.values():
    spine.set_color('#333333')
ax4.tick_params(axis='both', colors=TEXT)
ax4.grid(axis='y', alpha=0.15, color='#555555')

ax4.legend(loc='upper right', fontsize=8.5, facecolor='#1a1a2e',
           edgecolor='#444', labelcolor=TEXT, framealpha=0.9, ncol=2)

# Summary
total_findings = sum(totals)
ax4.text(0.5, -0.15,
         f'Total Findings: {total_findings}  |  Critical: 0  |  High: 0  |  Medium: {sum(medium)}  |  Low: {sum(low)}',
         transform=ax4.transAxes, fontsize=8, ha='center', color=GREEN, fontweight='bold')

# ============================================================
plt.subplots_adjust(hspace=0.35, wspace=0.3, top=0.92, bottom=0.06)
plt.savefig(OUT, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'Saved: {OUT}')
