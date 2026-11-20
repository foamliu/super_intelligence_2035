#!/usr/bin/env python3
"""BaiZe Stage(i) S5-01 长跑 loss 收敛曲线提取 + 绘图。

解析 Megatron `iteration ... lm loss: ...` 日志行，产出：
  1. CSV 曲线数据（iteration, lm_loss, lr, grad_norm）
  2. PNG 收敛曲线图（loss vs step，log-x）

用法：
  python3 plot_s5_curve.py [log] [--out-csv csv] [--out-png png] [--log-y]
默认 log=/tmp/baize_s5_01.log，
     out-csv=<doc>/data/s5_01_loss_curve.csv，
     out-png=<doc>/BaiZe-ISEDA2027/figures/s5_01_loss_curve.png
"""
import csv
import os
import re
import sys

DOC = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027"

# 匹配行形如：  iteration     9430/   20000 | consumed samples: ... | elapsed time per iteration (ms): 301.4 | learning rate: 1.000000E-03 | global batch size:     8 | lm loss: 2.556163E+00 | loss scale: 1.0 | grad norm: 0.241 | number of skipped iterations:   0 | number of nan iterations:   0 |
RE = re.compile(
    r"iteration\s+(\d+)/\s*(\d+).*?"
    r"learning rate:\s*([0-9.Ee+-]+).*?"
    r"lm loss:\s*([0-9.Ee+-]+).*?"
    r"grad norm:\s*([0-9.Ee+-]+)"
)


def parse(path):
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = RE.search(line)
            if not m:
                continue
            it, total, lr, loss, grad = m.groups()
            rows.append((int(it), int(total), float(lr), float(loss), float(grad)))
    # 去重（同 iter 可能多行，取最后一行）
    seen = {}
    for it, total, lr, loss, grad in rows:
        seen[it] = (total, lr, loss, grad)
    out = [(it, t, lr, lo, gr) for it, (t, lr, lo, gr) in sorted(seen.items())]
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    log = args[0] if args else "/tmp/baize_s5_01.log"
    out_csv = os.path.join(DOC, "data", "s5_01_loss_curve.csv")
    out_png = os.path.join(DOC, "BaiZe-ISEDA2027", "figures", "s5_01_loss_curve.png")
    log_y = "--log-y" in sys.argv

    rows = parse(log)
    if not rows:
        print(f"[warn] 未解析到任何 iteration 行，检查日志：{log}", file=sys.stderr)
        sys.exit(2)

    final_it = rows[-1][0]
    final_loss = rows[-1][3]
    print(f"解析到 {len(rows)} 个采样点；最新 iter={final_it}，lm loss={final_loss:.6f}")

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iteration", "lm_loss", "learning_rate", "grad_norm"])
        for it, total, lr, lo, gr in rows:
            w.writerow([it, f"{lo:.6f}", f"{lr:.6e}", f"{gr:.4f}"])
    print(f"[csv] {out_csv}")

    # 绘图
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xs = [r[0] for r in rows]
    ys = [r[3] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    ax.plot(xs, ys, lw=1.1, color="#1f6feb")
    ax.set_xscale("log")
    ax.set_xlabel("training step (log)")
    ax.set_ylabel("lm loss (train)")
    ax.set_title(f"BaiZe Mamba2-hybrid 2B S5-01 long-run convergence (loss@{final_it})")
    ax.grid(True, which="both", alpha=0.25, lw=0.5)
    if log_y:
        ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(out_png)
    print(f"[png] {out_png}")


if __name__ == "__main__":
    main()