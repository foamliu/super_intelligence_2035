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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
import numpy as np

OUT = "figures"

# ----------------------------------------------------------------------------
# 1. Evaluation pipeline flowchart
# ----------------------------------------------------------------------------
def draw_box(ax, x, y, w, h, text, fc, ec, fontsize=8.5, fontweight="normal"):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.08",
                         facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=2)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, zorder=3, color="#1a1a1a")

def draw_subgraph(ax, x, y, w, h, title, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.05",
                 facecolor="none", edgecolor=color, linewidth=1.2,
                 linestyle="--", zorder=1))
    # title ABOVE the border (y + h + small gap), fully visible
    ax.text(x + 0.15, y + h + 0.12, title, fontsize=7.8,
            color=color, fontstyle="italic", zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.9))

def arrow(ax, p1, p2, color="#555", style="-|>", lw=1.3, ls="-", conn=None):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=12,
                        color=color, lw=lw, linestyle=ls,
                        connectionstyle=conn or "arc3,rad=0", zorder=4)
    ax.add_patch(a)

# wider/taller canvas to give subgraph titles room above borders
fig, ax = plt.subplots(figsize=(8.6, 5.6), dpi=150)
ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis("off")

C_BOX  = "#e8f0fe"; E_BOX  = "#2c7be5"
C_AGT  = "#fef3e8"; E_AGT  = "#e88a1a"
C_EDA  = "#e8f5ee"; E_EDA  = "#2ca57a"
C_JDG  = "#f3e8fe"; E_JDG  = "#7a3ec9"
C_OUT  = "#e8eef5"; E_OUT  = "#555555"

# subgraphs (shifted down a bit to leave room for titles at top)
draw_subgraph(ax, 0.3, 3.4, 4.0, 2.5, "Isolated agent workdir", "#e88a1a")
draw_subgraph(ax, 5.2, 3.4, 4.5, 2.5, "Remote EDA server", "#2ca57a")
draw_subgraph(ax, 0.3, 0.5, 4.0, 1.9, "Separate judge dir", "#7a3ec9")

# boxes
draw_box(ax, 0.6, 5.55, 3.4, 0.7, "Task assets\n(prompt.txt, input files)", C_BOX, E_BOX)
draw_box(ax, 0.6, 4.75, 3.4, 0.6, "PreToolUse hook\n(anti-leakage)", C_BOX, E_BOX, fontsize=7.8)
draw_box(ax, 0.7, 4.50, 2.0, 0.55, "Cline agent", C_AGT, E_AGT, fontweight="bold")
draw_box(ax, 2.85, 4.50, 1.3, 0.55, "MCP bridge", C_AGT, E_AGT, fontsize=7.8)
draw_box(ax, 5.5, 4.50, 4.0, 0.85, "EDA tools\n(run_code / run_commands)", C_EDA, E_EDA)
draw_box(ax, 0.6, 3.55, 3.6, 0.7, "outputs/submit.zip\n(deliverable package)", C_OUT, E_OUT)
draw_box(ax, 0.7, 1.65, 3.4, 0.6, "check.py\n(>= 8 assertions)", C_JDG, E_JDG)
draw_box(ax, 0.7, 0.65, 3.4, 0.6, "PASS / FAIL", C_OUT, E_OUT)

# arrows
arrow(ax, (2.3, 5.55), (2.3, 5.05))                     # assets -> hook (down)
arrow(ax, (2.3, 4.75), (2.3, 5.05) if False else (1.7, 4.50))  # hook -> agent area
arrow(ax, (4.15, 4.77), (2.0, 4.50), color="#888", ls=":")  # hook blocks agent
arrow(ax, (2.7, 4.77), (2.85, 4.77))                     # agent -> MCP
arrow(ax, (4.15, 4.77), (5.5, 4.92))                     # MCP -> EDA
arrow(ax, (5.5, 4.50), (4.15, 4.60), color="#2ca57a")    # EDA -> MCP (results)
arrow(ax, (2.3, 4.50), (2.3, 4.25))                      # agent -> outputs
arrow(ax, (2.3, 3.55), (2.3, 2.25), color="#7a3ec9")     # outputs -> judge
arrow(ax, (2.3, 1.65), (2.3, 1.25), color="#555")        # judge -> verdict
ax.text(2.55, 2.85, "agent exits", fontsize=7, color="#7a3ec9", fontstyle="italic")
ax.text(4.55, 5.05, "tool call", fontsize=6.8, color="#888")
ax.text(4.55, 4.25, "results", fontsize=6.8, color="#2ca57a")
ax.text(1.05, 4.62, "blocks", fontsize=6.5, color="#888", fontstyle="italic")

fig.tight_layout()
fig.savefig(f"{OUT}/pipeline.pdf", bbox_inches="tight")
print("wrote figures/pipeline.pdf")
plt.close(fig)

# ----------------------------------------------------------------------------
# 2. Domain distribution donut chart
# ----------------------------------------------------------------------------
domains = [
    ("spice_sim",        177, "SPICE / char"),
    ("schematic_netlist",166, "Schematic / analog"),
    ("physical_verify",  106, "Physical / layout"),
    ("layout_aether",     66, "Physical / layout"),
    ("analog_context",    63, "Schematic / analog"),
    ("digital",           59, "Digital front"),
    ("layout_virtuoso",   57, "Physical / layout"),
    ("verification",      55, "Digital front"),
    ("waveform",          54, "Schematic / analog"),
    ("eda_other",         53, "Digital front"),
    ("characterization",  43, "SPICE / char"),
    ("pg_layout",         38, "Physical / layout"),
    ("pnr_signoff",       27, "Digital front"),
]
labels = [d[0].replace("_", r"\_") for d in domains]
sizes  = [d[1] for d in domains]
groups = [d[2] for d in domains]

group_colors = {
    "Digital front":          "#0072B2",
    "SPICE / char":           "#D55E00",
    "Physical / layout":      "#009E73",
    "Schematic / analog":     "#CC79A7",
}
colors = [group_colors[g] for g in groups]

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

legend_handles = [Patch(facecolor=c, edgecolor="white", label=g)
                  for g, c in group_colors.items()]
ax.legend(handles=legend_handles, loc="center", bbox_to_anchor=(0.5, -0.06),
          ncol=2, fontsize=8, frameon=False, title="Area group", title_fontsize=8.5)
ax.set_title(f"Domain distribution (N={total} tasks, 13 domains)", fontsize=10, pad=18)
fig.tight_layout()
fig.savefig(f"{OUT}/domain_pie.pdf", bbox_inches="tight")
print("wrote figures/domain_pie.pdf")
plt.close(fig)

# ----------------------------------------------------------------------------
# 3. Grounding depth vs Pass@1  (VQA said this one is fine; keep as-is)
# ----------------------------------------------------------------------------
depth_mid = np.array([1.5, 3.0, 4.0, 5.0, 6.0, 7.0])
pass_rate = np.array([80, 55, 29, 19, 8, 0], dtype=float)
depth_labels = ["1-2\nverification", "3\nsimple script", "4\npnr_signoff",
                "5\neda_other", "6\nlayout", "7+\ndigital synth"]

fig, ax = plt.subplots(figsize=(6.8, 3.8), dpi=150)
ax.plot(depth_mid, pass_rate, "o-", color="#0072B2", lw=2, ms=7,
        markeredgecolor="white", markeredgewidth=1.2, zorder=3)
ax.axvspan(1.0, 2.5, color="#009E73", alpha=0.10, zorder=1)
ax.axvspan(2.5, 5.5, color="#E69F00", alpha=0.10, zorder=1)
ax.axvspan(5.5, 8.0, color="#D55E00", alpha=0.12, zorder=1)
ax.text(1.5, 86, "text-in/text-out", ha="center", fontsize=7.3, color="#009E73")
ax.text(4.0, 86, "moderate grounding", ha="center", fontsize=7.3, color="#B27800")
ax.text(6.7, 86, "deep tool chaining", ha="center", fontsize=7.3, color="#D55E00")

ax.set_xticks(depth_mid)
ax.set_xticklabels(depth_labels, fontsize=7.3)
ax.set_ylabel("Pass@1 (%)", fontsize=9)
ax.set_xlabel("Tool-chain grounding depth (min. live EDA tool calls)", fontsize=9)
ax.set_ylim(-5, 95); ax.set_xlim(0.8, 7.7)
ax.grid(axis="y", ls=":", color="#ccc", alpha=0.7)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/grounding_depth.pdf", bbox_inches="tight")
print("wrote figures/grounding_depth.pdf")
plt.close(fig)

print("ALL DONE")
