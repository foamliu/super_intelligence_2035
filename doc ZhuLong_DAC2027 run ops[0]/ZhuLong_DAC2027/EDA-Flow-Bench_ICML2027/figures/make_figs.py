#!/usr/bin/env python3
"""Generate three figures as vector PDF for the ICML paper.

Run from the paper root:  figures/.venv/bin/python figures/make_figs.py

Iterated after VQA review:
- pipeline.pdf: subgraph titles were truncated ("Iso..."); repositioned ABOVE
  each subgraph border and enlarged the canvas so nothing is clipped.
- domain_pie.pdf: small slices (pnr_signoff, pg_layout, characterization) had
  crowded labels at the top; switched to a smarter label-placement that fans
  out small slices vertically and uses shorter callouts.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

OUT = "figures"

# ----------------------------------------------------------------------------
# 1. Evaluation pipeline flowchart  (hand-authored SVG -> PDF via cairosvg)
#    matplotlib-drawn boxes look toy-like; a hand-laid SVG gives clean
#    alignment, crisp text, and proper arrowheads. The SVG source lives in
#    figures/pipeline.svg; this step only re-renders it to PDF.
# ----------------------------------------------------------------------------
import os, subprocess, shutil
svg_path = f"{OUT}/pipeline.svg"
pdf_path = f"{OUT}/pipeline.pdf"
_converters = [
    ("cairosvg", None),
    ("rsvg-convert", f"rsvg-convert -f pdf -o {pdf_path} {svg_path}"),
    ("inkscape", f"inkscape {svg_path} --export-filename={pdf_path}"),
]
_rendered = False
try:
    import cairosvg
    cairosvg.svg2pdf(url=svg_path, write_to=pdf_path)
    print("wrote figures/pipeline.pdf (from SVG via cairosvg)")
    _rendered = True
except Exception as e:
    print(f"cairosvg unavailable ({e}); trying rsvg-convert / inkscape")
for tool, cmd in _converters[1:]:
    if _rendered:
        break
    if shutil.which(tool.split()[0]) is None:
        print(f"  {tool}: not installed, skipping")
        continue
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"wrote figures/pipeline.pdf (via {tool})")
        _rendered = True
    except Exception as e:
        print(f"  {tool} failed: {e}")
if not _rendered:
    # Keeping the committed pipeline.pdf is correct: it is generated from the
    # same pipeline.svg, and silently shipping a stale figure is worse than
    # printing why we skipped.
    print("SKIPPED figures/pipeline.pdf (no SVG converter on this machine; "
          "existing file left untouched)")

# ----------------------------------------------------------------------------
# 2. Domain distribution donut chart
#    2026-11-10: switched to the FROZEN evaluation snapshot used in §4/§5 --
#    696 runs (PASS+FAIL+ERROR+ABSENT) whose per-domain counts are exactly the
#    "Total" column of tab:main-results / tab:full-domain-results.
#    Previous numbers (sum 564) came from an older build and disagreed with both
#    \Ntasks and the evaluated set; keeping one source of truth avoids that.
# ----------------------------------------------------------------------------
domains = [
    ("spice_sim",        104, "SPICE / char"),
    ("schematic_netlist",131, "Schematic / analog"),
    ("physical_verify",   73, "Physical / layout"),
    ("layout_aether",     38, "Physical / layout"),
    ("analog_context",    55, "Schematic / analog"),
    ("digital",           51, "Digital front"),
    ("layout_virtuoso",   40, "Physical / layout"),
    ("verification",      38, "Digital front"),
    ("waveform",          47, "Schematic / analog"),
    ("eda_other",         38, "Digital front"),
    ("characterization",  28, "SPICE / char"),
    ("pg_layout",         28, "Physical / layout"),
    ("pnr_signoff",       25, "Digital front"),
]
labels = [d[0] for d in domains]  # plain underscore, no LaTeX escaping (mpl renders text mode)
sizes  = [d[1] for d in domains]
groups = [d[2] for d in domains]

# 13 distinct colors, organized as 4 hue families (one per area group) with
# lightness variants within each family. Each domain gets a unique color so
# adjacent slices are distinguishable, while the hue family still signals
# the area-group grouping visually.
domain_colors = {
    # Digital front (blue family: dark -> light)
    "digital":           "#08519c",
    "verification":      "#3182bd",
    "pnr_signoff":       "#6baed6",
    "eda_other":         "#9ecae1",
    # SPICE / char (orange/red family)
    "spice_sim":         "#b30000",
    "characterization":  "#ef6548",
    # Physical / layout (green family: dark -> light)
    "physical_verify":   "#006d2c",
    "layout_aether":     "#2ca25c",
    "layout_virtuoso":   "#66c2a4",
    "pg_layout":         "#a8ddb5",
    # Schematic / analog (purple/pink family)
    "schematic_netlist": "#7b3294",
    "analog_context":    "#c2a5cf",
    "waveform":          "#e7d4e8",
}
colors = [domain_colors[d[0]] for d in domains]

fig, ax = plt.subplots(figsize=(7.8, 5.8), dpi=150)
total = sum(sizes)
def autopct(pct):
    return f"{pct:.0f}%" if pct >= 4 else ""

wedges, _, autotexts = ax.pie(
    sizes, labels=None, colors=colors, startangle=90, counterclock=False,
    autopct=autopct, pctdistance=0.78,
    wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.2),
    textprops=dict(fontsize=8, color="white", fontweight="bold"),
)

# Auto-contrast: flip percentage text to dark on light-colored slices.
def _luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    # relative luminance (ITU-R BT.709)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

for autotext, color in zip(autotexts, colors):
    if _luminance(color) > 0.6:
        autotext.set_color("#1a1a1a")

# Smart label placement: pillar/collision algorithm to prevent vertical overlap.
# Compute each label's natural (x,y) at radius r_out; sort by y; enforce a
# minimum vertical gap by pushing labels apart, then connect back to wedge
# with a leader line. (Same idea as D3's pie label "pillar" layout.)
n = len(wedges)
labels_xy = []
for i, w in enumerate(wedges):
    ang = (w.theta2 + w.theta1) / 2.0
    rad = np.deg2rad(ang)
    x, y = np.cos(rad), np.sin(rad)
    ha = "left" if x >= 0 else "right"
    r_out = 1.30
    labels_xy.append({"i": i, "ang": ang, "x": x, "y": y, "ha": ha,
                      "lx": r_out * x, "ly": r_out * y})

# Sort by y (top to bottom) and enforce min vertical gap on each side.
# Process left and right halves independently (labels don't cross the vertical
# axis because ha flips there).
MIN_GAP = 0.26  # min vertical distance between label centers
for side in ("right", "left"):
    group = [d for d in labels_xy if (d["ha"] == "right") == (side == "right")]
    group.sort(key=lambda d: -d["ly"])  # top first
    for k in range(1, len(group)):
        prev_y = group[k - 1]["ly"]
        if group[k]["ly"] > prev_y - MIN_GAP:
            group[k]["ly"] = prev_y - MIN_GAP
    # second pass bottom-up to recover excessive downward drift
    for k in range(len(group) - 2, -1, -1):
        nxt_y = group[k + 1]["ly"]
        if group[k]["ly"] < nxt_y + MIN_GAP:
            group[k]["ly"] = nxt_y + MIN_GAP

for d in labels_xy:
    i = d["i"]
    ax.annotate(
        f"{labels[i]} ({sizes[i]})",
        xy=(0.96 * d["x"], 0.96 * d["y"]),
        xytext=(d["lx"], d["ly"]),
        ha=d["ha"], va="center", fontsize=7.0,
        arrowprops=dict(arrowstyle="-", color="#999", lw=0.5,
                        connectionstyle=f"angle,angleA=0,angleB={d['ang']}"),
    )

# No legend: each slice already has its own color + label with count, so a
# separate 4-entry area-group legend is redundant and collides with the
# bottom slice labels.
ax.set_title(f"Domain distribution of the 696-run evaluation snapshot", fontsize=10, pad=18)
fig.tight_layout()
fig.savefig(f"{OUT}/domain_pie.pdf", bbox_inches="tight")
print("wrote figures/domain_pie.pdf")
plt.close(fig)

# ----------------------------------------------------------------------------
# 3. Grounding depth vs Pass@1  (VQA said this one is fine; keep as-is)
# ----------------------------------------------------------------------------
# Pass@1 values mapped from the 2026-11-09 frozen evaluation (696 runs, 13
# domains, DeepSeek-V4-Pro / Cline v3.0.51), read off tab:main-results. Domains
# are grouped by the minimum number of live EDA tool calls a correct deliverable
# typically requires (tool-chain grounding depth); each plotted value is the
# MEAN Pass@1 of the domains in that bin, so the figure and the table can never
# drift apart:
#   Depth 1-2: pnr_signoff 20.8 + characterization 19.2 + eda_other 18.2 -> 19.4
#   Depth 3  : pg_layout 14.3                                            -> 14.3
#   Depth 4  : schematic_netlist 11.5 + digital 11.1                     -> 11.3
#   Depth 5  : layout_virtuoso 10.3 + analog_context 9.3
#              + verification 9.1 + spice_sim 8.4                        -> 9.3
#   Depth 6  : waveform 5.1                                              -> 5.1
#   Depth 7+ : physical_verify 2.9 + layout_aether 2.9                   -> 2.9
# Depth is an ANNOTATION (design choice), not a measured quantity -- the
# caption says so, and no causal claim is drawn from the monotone ordering.
depth_mid = np.array([1.5, 3.0, 4.0, 5.0, 6.0, 7.0])
pass_rate = np.array([19.4, 14.3, 11.3, 9.3, 5.1, 2.9], dtype=float)
depth_labels = ["1-2\npnr/char/other", "3\npg_layout", "4\nschem/\ndigital",
                "5\nspice/verif\n/layout", "6\nwaveform", "7+\nphys_verify\n/layout"]

fig, ax = plt.subplots(figsize=(6.8, 3.8), dpi=150)
ax.plot(depth_mid, pass_rate, "o-", color="#0072B2", lw=2, ms=7,
        markeredgecolor="white", markeredgewidth=1.2, zorder=3)
ax.axvspan(1.0, 2.5, color="#009E73", alpha=0.10, zorder=1)
ax.axvspan(2.5, 5.5, color="#E69F00", alpha=0.10, zorder=1)
ax.axvspan(5.5, 8.0, color="#D55E00", alpha=0.12, zorder=1)
ax.text(1.5, 23, "text-in/text-out", ha="center", fontsize=7.3, color="#009E73")
ax.text(4.0, 23, "moderate grounding", ha="center", fontsize=7.3, color="#B27800")
ax.text(6.7, 23, "deep tool chaining", ha="center", fontsize=7.3, color="#D55E00")

ax.set_xticks(depth_mid)
ax.set_xticklabels(depth_labels, fontsize=7.3)
ax.set_ylabel("Pass@1 (%)", fontsize=9)
ax.set_xlabel("Tool-chain grounding depth (min. live EDA tool calls)", fontsize=9)
ax.set_ylim(-2, 26); ax.set_xlim(0.8, 7.7)
ax.grid(axis="y", ls=":", color="#ccc", alpha=0.7)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/grounding_depth.pdf", bbox_inches="tight")
print("wrote figures/grounding_depth.pdf")
plt.close(fig)

print("ALL DONE")
