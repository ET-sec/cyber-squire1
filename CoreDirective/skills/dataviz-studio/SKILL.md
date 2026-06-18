---
name: dataviz-studio
description: Data visualization with Python (matplotlib, seaborn, plotly) and chart selection guidance
---

# DataViz Studio

## When to Use
User asks to create charts, graphs, dashboards, visualize data, or needs help choosing chart types.

## Chart Selection Guide

| Question | Chart Type | Library |
|----------|-----------|---------|
| Compare categories | Bar (vertical/horizontal) | matplotlib/seaborn |
| Show trend over time | Line | matplotlib/plotly |
| Show correlation | Scatter | seaborn/plotly |
| Part of whole | Pie (max 6) or Treemap | matplotlib/plotly |
| Distribution | Histogram or Box plot | seaborn |
| Compare distributions | Violin plot | seaborn |
| Heat/intensity | Heatmap | seaborn |
| Geographic | Choropleth map | plotly |
| Interactive dashboard | Multi-chart layout | plotly/dash |

## Quick Templates

**Bar chart (matplotlib):**
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(categories, values, color="#2196F3")
ax.set_title("Title", fontsize=16, fontweight="bold")
ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("chart.png", dpi=150, bbox_inches="tight")
```

**Line chart with seaborn:**
```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=df, x="date", y="value", hue="category", ax=ax)
ax.set_title("Trend Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("trend.png", dpi=150)
```

**Interactive plotly:**
```python
import plotly.express as px

fig = px.scatter(df, x="col_x", y="col_y", color="category",
                 size="magnitude", hover_data=["detail"],
                 title="Interactive Scatter")
fig.update_layout(template="plotly_white")
fig.write_html("chart.html")
fig.write_image("chart.png", scale=2)
```

**Multi-panel dashboard:**
```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes[0,0].bar(...)    # Top-left: bar
axes[0,1].plot(...)   # Top-right: line
axes[1,0].scatter(...) # Bottom-left: scatter
axes[1,1].pie(...)    # Bottom-right: pie
fig.suptitle("Dashboard Title", fontsize=18)
plt.tight_layout()
plt.savefig("dashboard.png", dpi=150)
```

## Color Palettes (Accessible)

```python
# Colorblind-safe (default to these)
colors_cb = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]

# Sequential (for heatmaps, intensity)
cmap = "viridis"  # or "plasma", "cividis"

# Diverging (for +/- values)
cmap = "RdBu_r"  # red=negative, blue=positive
```

## Export Formats
- **PNG:** `dpi=150` for screen, `dpi=300` for print
- **SVG:** `plt.savefig("chart.svg")` -- scalable, good for web
- **PDF:** `plt.savefig("chart.pdf")` -- print-ready
- **HTML:** plotly `fig.write_html()` -- interactive, shareable

## Presentation Tips
- Title: 16-18pt bold, describes the insight (not just the data)
- Labels: Always label axes with units
- Legend: Only when 2+ series; place outside plot if crowded
- Gridlines: Light gray, horizontal only for bar/line
- Annotations: Call out key data points with `ax.annotate()`
- White space: Use `plt.tight_layout()` always
