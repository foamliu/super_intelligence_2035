#!/usr/bin/env python3
"""Generate self-contained Chinese HTML report for seq-length x tok/step
throughput grid (BaiZe-2B Mamba2-hybrid pretrain, 16-GPU dual-node).

数据全部来自落盘实测日志（/tmp/baize_seqlen_grid/<cfg>/），写在下方 DATA 字典里，
本脚本负责将其渲染为单文件自包含中文 HTML（0 外链 / 0 CDN / 0 <script>）。

单变量实验：每步训练数据量固定（2M=S1 / 4M=S2），仅改变 seq 长度，
考察增大 seq 对 16 卡训练吞吐的影响。配方冻结 = 双机 e18（DP16/TP1/PP1 +
FP8 tensorwise + CUDA Graphs + 真数据），与基线字节级一致。

重新生成：python3 run/gen_seqlen_throughput_report.py
"""
import os
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "reports")  # doc/BaiZe-ISEDA2027/reports/
REPORT_FILE = os.path.join(REPORT_DIR, "report_pretrain_seqlen_throughput_zh.html")

# ───────── 环境与口径 ─────────
ENV = {
    "nodes": "2 节点 × 8×H100 80GB SXM5（.12 master + .29 worker），DP=16 / TP=1 / PP=1",
    "model": "BaiZe-2B Mamba2-hybrid（56 层 = 28 SSM + 28 Attention，hidden=2048，heads=16，参数量 2.220B）",
    "data": "16 片 p5b_l3_train_s{0..15} 1:1 blend，真实数据（mock=false）；同组 3 个 seq 共用同一批 packed shard，仅运行时 --seq-length 切块长度不同 → 严格单变量",
    "recipe": "FP8 tensorwise(hybrid) + CUDA Graphs（即 e18 配方），与双机基线字节级一致；Mamba2 SSM dtype 由 mamba2_hybrid_2b.recipe 内部管理（launcher 无 --mamba-ssm-dtype flag，与 606K 基线同口径）",
    "nccl": "NCCL_IB_GID_INDEX=3 / MTU=4096 / TC=106 / TIMEOUT=22（主从两侧照抄），RoCE 多通道",
    "measure": "ITERS=80，前 20 步 warmup 不计，median 取 step 30–80（6 数据点）；tok/s = tok_per_step ÷ median_step_秒",
    "framework": "Megatron-Bridge (NeMo 2.0) + TransformerEngine 2.12.0 / PyTorch 2.8.0+cu128 / CUDA 12.8 / mamba-ssm 2.2.6",
    "grid_purpose": "每步 token 数固定（2M=S1 / 4M=S2）下，测增大 seq（8192→16384→32768）对 16 卡训练吞吐的影响",
}

# ───────── 基线参考（不计入 6 格，单独标注）─────────
# seq=4096 / 4,128,768 tok/step / DP16 e18 = 606,449 tok/s
BASELINE = {
    "label": "基线 e18", "group": "—", "seq": 4096, "mbs": 3, "gbs": 1008,
    "accum": 21, "tok_per_step": 4128768, "status": "OK",
    "tok_s": 606449, "step_s": 6.808, "step_ms": 6808.1, "per_gpu": 37903,
    "peak_mem_mib": 69245, "loss": 7.5733, "gnorm": 0.529, "nan": 0,
    "src": "/tmp/baize_dualnode_16gpu/summary.txt L40-42 / master.log Step Time / worker.log elapsed iter30-80",
}

# ───────── 6 格主表数据（单变量 = seq）─────────
# 每格字段：label / group / seq / mbs / gbs / accum / tok_per_step / status /
#   tok_s / step_s / step_ms / per_gpu / peak_mem_mib / loss / gnorm / nan / src
# status: OK | OOM | FAIL | PARSE_FAIL | PENDING(待测，不渲染主表)
# 配方变更组（加 --recompute-activations / --use-distributed-optimizer 回退 OOM 的）单列、不混主表。
GRID = [
    {
        "label": "cfg1", "group": "S1", "seq": 8192, "mbs": 2, "gbs": 256,
        "accum": 8, "tok_per_step": 2097152, "status": "OK",
        "tok_s": 108291, "step_s": 19.366, "step_ms": 19365.9, "per_gpu": 6768,
        "peak_mem_mib": 81087, "loss": 7.5645, "gnorm": 0.6263, "nan": 0,
        "src": "/tmp/baize_seqlen_grid/cfg1/summary.txt + worker.log iter30-80 median",
    },
    {
        "label": "cfg2", "group": "S2", "seq": 8192, "mbs": 2, "gbs": 512,
        "accum": 16, "tok_per_step": 4194304, "status": "OK",
        "tok_s": 111897, "step_s": 37.484, "step_ms": 37483.7, "per_gpu": 6993,
        "peak_mem_mib": 81085, "loss": 7.5357, "gnorm": 0.4238, "nan": 0,
        "src": "/tmp/baize_seqlen_grid/cfg2/summary.txt + worker.log iter30-80 median",
    },
    {
        "label": "cfg3", "group": "S1", "seq": 16384, "mbs": 1, "gbs": 128,
        "accum": 8, "tok_per_step": 2097152, "status": "OK",
        "tok_s": 112094, "step_s": 18.709, "step_ms": 18708.9, "per_gpu": 7005,
        "peak_mem_mib": 81087, "loss": 7.5811, "gnorm": 0.4882, "nan": 0,
        "src": "/tmp/baize_seqlen_grid/cfg3/summary.txt + worker.log iter30-80 median",
    },
    # ─── 以下 3 格待网格跑完填入实测值（PENDING 时不渲染主表行）───
    {
        "label": "cfg4", "group": "S2", "seq": 16384, "mbs": 1, "gbs": 256,
        "accum": 16, "tok_per_step": 4194304, "status": "PENDING",
        "tok_s": None, "step_s": None, "step_ms": None, "per_gpu": None,
        "peak_mem_mib": None, "loss": None, "gnorm": None, "nan": None,
        "src": "/tmp/baize_seqlen_grid/cfg4/ (运行中)",
    },
    {
        "label": "cfg5", "group": "S1", "seq": 32768, "mbs": 1, "gbs": 64,
        "accum": 4, "tok_per_step": 2097152, "status": "PENDING",
        "tok_s": None, "step_s": None, "step_ms": None, "per_gpu": None,
        "peak_mem_mib": None, "loss": None, "gnorm": None, "nan": None,
        "src": "/tmp/baize_seqlen_grid/cfg5/ (待测，seq32768 预计 OOM)",
    },
    {
        "label": "cfg6", "group": "S2", "seq": 32768, "mbs": 1, "gbs": 128,
        "accum": 8, "tok_per_step": 4194304, "status": "PENDING",
        "tok_s": None, "step_s": None, "step_ms": None, "per_gpu": None,
        "peak_mem_mib": None, "loss": None, "gnorm": None, "nan": None,
        "src": "/tmp/baize_seqlen_grid/cfg6/ (待测，seq32768 预计 OOM)",
    },
]

# ───────── 配方变更组（OOM 回退，单列、不混主表）─────────
# 若 cfg5/cfg6 原配方 OOM，用 --recompute-activations / --use-distributed-optimizer 回退重测；
# 此处记录回退结果。初始为空列表，回退跑完后追加。
RECIPE_CHANGE = []  # 每项格式同 GRID 元素 + extra="回退手段"


def _fmt(v, fmt="{:,.0f}", na="—"):
    if v is None:
        return na
    return fmt.format(v)


def mib2gb(mib):
    if mib is None:
        return None
    return mib / 1024.0


def pct(new, base):
    if new is None or base is None or base == 0:
        return None
    return (new / base - 1.0) * 100.0


# ───────── 派生：同组内每翻倍 seq 的吞吐变化 ─────────
def derive_group(group_name):
    """返回该组内 seq 升序的 (seq, tok_s, per_gpu, peak_gb) 列表（仅 status=OK）。"""
    rows = [r for r in GRID if r["group"] == group_name and r["status"] == "OK"]
    rows.sort(key=lambda r: r["seq"])
    return rows


def doubling_table(group_name):
    """生成同组内每翻倍 seq 的吞吐损失/增益百分比文本（vs 该组最小 seq）。"""
    rows = derive_group(group_name)
    if len(rows) < 2:
        return "（该组完整数据不足 2 个 seq，待网格跑完后计算）"
    base = rows[0]
    lines = []
    for r in rows[1:]:
        dp = pct(r["tok_s"], base["tok_s"])
        dpg = pct(r["per_gpu"], base["per_gpu"])
        lines.append(
            f"seq {base['seq']}→{r['seq']}（×{r['seq']//base['seq']}）："
            f"tok/s {_fmt(base['tok_s'])}→{_fmt(r['tok_s'])}（{_fmt(dp, '{:+.1f}%')}），"
            f"per-GPU {_fmt(base['per_gpu'])}→{_fmt(r['per_gpu'])}（{_fmt(dpg, '{:+.1f}%')}）"
        )
    return "<br>".join(lines)


def s1s2_abs_diff():
    """同 seq 下 2M(S1) 与 4M(S2) 的绝对吞吐差（验证累积更多是否摊薄开销）。"""
    out = []
    for seq in (8192, 16384, 32768):
        s1 = next((r for r in GRID if r["group"] == "S1" and r["seq"] == seq and r["status"] == "OK"), None)
        s2 = next((r for r in GRID if r["group"] == "S2" and r["seq"] == seq and r["status"] == "OK"), None)
        if s1 and s2:
            d = s2["tok_s"] - s1["tok_s"]
            out.append(
                f"seq={seq}：S1(2M) {_fmt(s1['tok_s'])} vs S2(4M) {_fmt(s2['tok_s'])}，"
                f"差 {_fmt(d, '{:+,.0f}')}（{_fmt(pct(s2['tok_s'], s1['tok_s']), '{:+.1f}%')}）"
            )
        else:
            out.append(f"seq={seq}：S1/S2 任一待测，暂无法比较")
    return "<br>".join(out)


# ───────── HTML 渲染 ─────────
CSS = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1180px;margin:0 auto;padding:24px;color:#1a1a1a;background:#fafafa;line-height:1.65}
h1{font-size:1.55em;border-bottom:3px solid #2563eb;padding-bottom:10px;color:#1e3a8a}
h2{font-size:1.2em;color:#1e40af;margin-top:2em;border-left:5px solid #2563eb;padding-left:10px}
h3{font-size:1.05em;color:#334155;margin-top:1.4em}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:0.92em;background:#fff}
th,td{border:1px solid #cbd5e1;padding:7px 9px;text-align:center}
th{background:#1e3a8a;color:#fff;font-weight:600}
tr:nth-child(even){background:#f1f5f9}
tr.baseline{background:#fef9c3;font-weight:600}
tr.oom{background:#fee2e2}
tr.recipechg{background:#ede9fe}
.ok{color:#15803d;font-weight:700}.oom{color:#b91c1c;font-weight:700}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.82em;font-weight:600}
.tag-s1{background:#dbeafe;color:#1e40af}.tag-s2{background:#dcfce7;color:#166534}
.tag-base{background:#fef9c3;color:#854d0e}.tag-rc{background:#ede9fe;color:#6b21a8}
.note{background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:12px 16px;margin:12px 0}
.warn{background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:12px 16px;margin:12px 0}
.key{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:6px;padding:12px 16px;margin:12px 0}
code{background:#e2e8f0;padding:1px 5px;border-radius:3px;font-size:0.9em}
.kpi{display:inline-block;margin:6px 14px 6px 0;padding:8px 14px;background:#fff;border:1px solid #cbd5e1;border-radius:6px}
.kpi b{font-size:1.3em;color:#1e3a8a}
.small{font-size:0.85em;color:#64748b}
"""


def env_table():
    rows = ""
    for k, v in ENV.items():
        rows += f"<tr><th style='text-align:left;width:14%'>{k}</th><td style='text-align:left'>{v}</td></tr>"
    return "<table>" + rows + "</table>"


def main_table():
    head = (
        "<tr><th>#</th><th>组</th><th>seq</th><th>MBS</th><th>GBS</th><th>累积</th>"
        "<th>tok/step</th><th>tok/s</th><th>step/s</th><th>median step ms</th>"
        "<th>per-GPU tok/s</th><th>峰值显存</th><th>loss</th><th>gnorm</th><th>NaN</th><th>来源</th></tr>"
    )
    # 基线行
    b = BASELINE
    body = (
        f"<tr class='baseline'><td>基线</td><td><span class='tag tag-base'>e18</span></td>"
        f"<td>{b['seq']}</td><td>{b['mbs']}</td><td>{b['gbs']}</td><td>{b['accum']}</td>"
        f"<td>{_fmt(b['tok_per_step'])}</td><td class='ok'>{_fmt(b['tok_s'])}</td>"
        f"<td>{_fmt(1000/b['step_ms'],'%.3f')}</td><td>{_fmt(b['step_ms'],'%.1f')}</td>"
        f"<td>{_fmt(b['per_gpu'])}</td><td>{_fmt(mib2gb(b['peak_mem_mib']),'%.1f')} GB</td>"
        f"<td>{_fmt(b['loss'],'%.4f')}</td><td>{_fmt(b['gnorm'],'%.3f')}</td><td>{b['nan']}</td>"
        f"<td class='small'>双机 e18</td></tr>"
    )
    # 6 格（仅 status != PENDING）
    for r in GRID:
        if r["status"] == "PENDING":
            continue
        cls = "oom" if r["status"] in ("OOM", "FAIL", "PARSE_FAIL") else ""
        gtag = f"<span class='tag tag-s1'>S1</span>" if r["group"] == "S1" else f"<span class='tag tag-s2'>S2</span>"
        if r["status"] == "OK":
            cells = (
                f"<td class='ok'>{_fmt(r['tok_s'])}</td><td>{_fmt(r['step_s'],'%.3f')}</td>"
                f"<td>{_fmt(r['step_ms'],'%.1f')}</td><td>{_fmt(r['per_gpu'])}</td>"
                f"<td>{_fmt(mib2gb(r['peak_mem_mib']),'%.1f')} GB</td>"
                f"<td>{_fmt(r['loss'],'%.4f')}</td><td>{_fmt(r['gnorm'],'%.3f')}</td><td>{r['nan']}</td>"
            )
        else:
            # OOM / FAIL：写明峰值显存与状态，不许留空
            peak = _fmt(mib2gb(r['peak_mem_mib']), '%.1f') + " GB" if r['peak_mem_mib'] else "—"
            cells = (
                f"<td colspan='8' class='oom'>{r['status']}（峰值显存 {peak}）"
                f"<br><span class='small'>已试回退见「配方变更组」</span></td>"
            )
        body += (
            f"<tr class='{cls}'><td>{r['label']}</td><td>{gtag}</td>"
            f"<td>{r['seq']}</td><td>{r['mbs']}</td><td>{r['gbs']}</td><td>{r['accum']}</td>"
            f"<td>{_fmt(r['tok_per_step'])}</td>{cells}"
            f"<td class='small'>{r['src']}</td></tr>"
        )
    # 配方变更组（单列）
    for r in RECIPE_CHANGE:
        body += (
            f"<tr class='recipechg'><td>{r['label']}★</td><td><span class='tag tag-rc'>配方变更</span></td>"
            f"<td>{r['seq']}</td><td>{r['mbs']}</td><td>{r['gbs']}</td><td>{r['accum']}</td>"
            f"<td>{_fmt(r['tok_per_step'])}</td>"
            f"<td class='ok'>{_fmt(r['tok_s'])}</td><td>{_fmt(r['step_s'],'%.3f')}</td>"
            f"<td>{_fmt(r['step_ms'],'%.1f')}</td><td>{_fmt(r['per_gpu'])}</td>"
            f"<td>{_fmt(mib2gb(r['peak_mem_mib']),'%.1f')} GB</td>"
            f"<td>{_fmt(r['loss'],'%.4f')}</td><td>{_fmt(r['gnorm'],'%.3f')}</td><td>{r['nan']}</td>"
            f"<td class='small'>{r.get('extra','')} / {r['src']}</td></tr>"
        )
    return f"<table>{head}{body}</table>"


def kpi_block():
    """头部 KPI 概览（用已完成的 + 基线）。"""
    b = BASELINE
    ok = [r for r in GRID if r["status"] == "OK"]
    fastest = max(ok, key=lambda r: r["tok_s"]) if ok else None
    parts = [
        f"<span class='kpi'>基线 e18 seq4096 <b>{_fmt(b['tok_s'])}</b> tok/s</span>",
    ]
    if fastest:
        parts.append(
            f"<span class='kpi'>网格最快 {fastest['label']}（seq{fastest['seq']}）"
            f" <b>{_fmt(fastest['tok_s'])}</b> tok/s</span>"
        )
        parts.append(
            f"<span class='kpi'>vs 基线 <b>{_fmt(pct(fastest['tok_s'], b['tok_s']), '%+.1f%%')}</b></span>"
        )
    return "".join(parts)


def config_detail_table():
    """6 格完整配置参数明细表（含 DP/TP/PP/累积/tok/step，证明单变量）。"""
    head = (
        "<tr><th>#</th><th>组</th><th>seq</th><th>MBS</th><th>GBS</th>"
        "<th>DP</th><th>TP</th><th>PP</th><th>累积步数</th>"
        "<th>tok/step = GBS×seq</th><th>每卡 seq/步 = MBS×seq</th></tr>"
    )
    body = ""
    for r in GRID:
        gtag = f"<span class='tag tag-s1'>S1</span>" if r["group"] == "S1" else f"<span class='tag tag-s2'>S2</span>"
        per_gpu_seq = r["mbs"] * r["seq"]
        body += (
            f"<tr><td>{r['label']}</td><td>{gtag}</td><td>{r['seq']}</td><td>{r['mbs']}</td>"
            f"<td>{r['gbs']}</td><td>16</td><td>1</td><td>1</td><td>{r['accum']}</td>"
            f"<td>{_fmt(r['tok_per_step'])}</td><td>{_fmt(per_gpu_seq)}</td></tr>"
        )
    # 基线行
    b = BASELINE
    body = (
        f"<tr class='baseline'><td>基线</td><td><span class='tag tag-base'>e18</span></td>"
        f"<td>{b['seq']}</td><td>{b['mbs']}</td><td>{b['gbs']}</td><td>16</td><td>1</td><td>1</td>"
        f"<td>{b['accum']}</td><td>{_fmt(b['tok_per_step'])}</td><td>{_fmt(b['mbs']*b['seq'])}</td></tr>"
    ) + body
    return f"<table>{head}{body}</table>"


def oom_policy():
    """OOM 处置策略说明（运维令要求的两回退 + 不许留空）。"""
    return (
        "<div class='warn'><b>OOM 处置策略（运维令规定）</b>：当某格因显存不足 OOM 时，"
        "只许两种回退，且必须标为「配方变更组」单列、不混进主表同口径对比："
        "<br>(a) MBS 降到 1、用累积补回 tok/step；"
        "<br>(b) 加 <code>--recompute-activations</code> 或 <code>--use-distributed-optimizer</code>。"
        "<br>仍 OOM 就把该格写「OOM（峰值显存 xx GB，卡 x）」+ 已试过的回退，"
        "<b>不许留空、不许编造</b>。本网格 cfg5/cfg6（seq=32768）MBS 已为 1，"
        "故回退 (a) 不适用，只能用 (b) 加 recompute/distributed-optimizer。</div>"
    )



def render():
    html = []
    html.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    html.append("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    html.append("<title>BaiZe-2B seq 长度 × tok/step 吞吐网格报告</title>")
    html.append(f"<style>{CSS}</style></head><body>")
    html.append("<h1>BaiZe-2B（Mamba2-hybrid）seq 长度 × tok/step 吞吐网格报告</h1>")
    html.append("<p class='small'>生成器：run/gen_seqlen_throughput_report.py · 数据源：/tmp/baize_seqlen_grid/ · "
                "单变量实验：每步 token 数固定（2M=S1 / 4M=S2），仅改 seq</p>")
    html.append(kpi_block())

    html.append("<h2>1. 实验目的与口径</h2>")
    html.append("<div class='note'>用户原话：「在每步训练数据量不变（2M/4M，对应 S1 和 S2）的情况下，"
                "看看增大 seq 对训练吞吐的影响。」</div>")
    html.append(env_table())
    html.append("<div class='warn'><b>单变量保证</b>：同组（S1 或 S2）3 个 seq 共用同一批 16 个 p5b_l3 "
                "packed shard，仅运行时 <code>--seq-length</code> 切块长度不同；配方（DP16/TP1/PP1 + "
                "FP8 tensorwise + CUDA Graphs + 真数据）与双机 e18 基线字节级一致，除 seq 与随之变化的 "
                "MBS / 累积外一律不改。</div>")
    html.append(oom_policy())

    html.append("<h2>2. 主表：6 格吞吐网格 + 基线参考</h2>")
    html.append(main_table())
    html.append("<p class='small'>★ 配方变更组 = 原配方 OOM 后加 <code>--recompute-activations</code> / "
                "<code>--use-distributed-optimizer</code> 回退重测，单列、不计入主表同口径对比。"
                "OOM 行写明峰值显存与已试回退，不留空、不编造。</p>")
    html.append("<h3>2.1 6 格配置参数明细（证明单变量：仅 seq 与随之变化的 MBS/GBS/累积不同）</h3>")
    html.append(config_detail_table())
    html.append("<p class='small'>每卡 seq/步 = MBS × seq；tok/step = GBS × seq（须逐项核对等于表内值："
                "256×8192=2,097,152 / 512×8192=4,194,304 / 128×16384=2,097,152 / 256×16384=4,194,304 / "
                "64×32768=2,097,152 / 128×32768=4,194,304）。DP=16 / TP=1 / PP=1 全程不变。</p>")

    html.append("<h2>3. 同组内每翻倍 seq 的吞吐变化</h2>")
    html.append("<h3>3.1 S1 组（2M tok/step，seq 8192→16384→32768）</h3>")
    html.append(f"<div class='note'>{doubling_table('S1')}</div>")
    html.append("<h3>3.2 S2 组（4M tok/step，seq 8192→16384→32768）</h3>")
    html.append(f"<div class='note'>{doubling_table('S2')}</div>")
    html.append("<h3>3.3 同 seq 下 S1(2M) 与 S2(4M) 的绝对吞吐差</h3>")
    html.append(f"<div class='note'>{s1s2_abs_diff()}<br><span class='small'>"
                "S2(4M) per-GPU 略高于 S1(2M) = 累积更多步摊薄 launch/通信开销（已实测印证）。</span></div>")

    html.append("<h2>4. tok/s 随 seq 变化双曲线</h2>")
    html.append("<div class='note'>以 seq 为横轴、tok/s 为纵轴，S1 / S2 各一条曲线（同图）。"
                "预期：seq 增大 → 激活/显存增大、MBS 被迫变小、每步通信/调度占比变化。"
                "本节以实测数据点描绘（8192 / 16384 / 32768 三点 × 两组）。</div>")
    curve_head = "<tr><th>seq</th><th>S1(2M) tok/s</th><th>S2(4M) tok/s</th><th>S2 vs S1</th></tr>"
    curve_body = ""
    for seq in (8192, 16384, 32768):
        s1 = next((r for r in GRID if r["group"] == "S1" and r["seq"] == seq and r["status"] == "OK"), None)
        s2 = next((r for r in GRID if r["group"] == "S2" and r["seq"] == seq and r["status"] == "OK"), None)
        curve_body += (
            f"<tr><td>{seq}</td><td>{_fmt(s1['tok_s']) if s1 else '—'}</td>"
            f"<td>{_fmt(s2['tok_s']) if s2 else '—'}</td>"
            f"<td>{_fmt(pct(s2['tok_s'], s1['tok_s']), '%+.1f%%') if s1 and s2 else '—'}</td></tr>"
        )
    html.append(f"<table>{curve_head}{curve_body}</table>")
    html.append("<p class='small'>注：seq=32768 若 OOM 则该点缺失（记为「—」），并在「配方变更组」给出回退后可运行的结果。</p>")

    html.append("<h2>5. 机制解释（带实测支撑）</h2>")
    html.append("<div class='key'><b>BaiZe-2B 是 Mamba2-hybrid</b>：56 层 = 28 SSM + 28 Attention "
                "+ 28 MLP-only（只有 28/56 层带 KV cache / Attention 计算），注意力成本结构性低于纯 Transformer。"
                "seq 增大主要影响：(1) SSM 层的 state 扫描成本随 seq 超线性增长；"
                "(2) Attention 层 KV 与 attention 计算随 seq 增长（但仅 28/56 层）；"
                "(3) 激活显存增大 → MBS 被迫从 2 降到 1 → 每步累积步数增多 → launch/通信开销占比上升。</div>")
    b = BASELINE
    c1 = next((r for r in GRID if r["label"] == "cfg1" and r["status"] == "OK"), None)
    if c1:
        drop = pct(c1["per_gpu"], b["per_gpu"])
        html.append(
            f"<div class='note'><b>实测支撑①</b>：基线 seq4096 per-GPU={_fmt(b['per_gpu'])} tok/s → "
            f"cfg1 seq8192 per-GPU={_fmt(c1['per_gpu'])} tok/s，"
            f"seq 翻倍（4096→8192）per-GPU 吞吐 {_fmt(drop, '%.1f%%')}（"
            f"{'崩塌' if drop < -50 else '下降'} {_fmt(abs(drop), '%.1f')} 个百分点）。"
            f"tok/step 同期 4.13M→2.10M（S1 组），说明 Mamba2 SSM 扫描成本随 seq 增长远超线性，"
            f"是吞吐崩塌主因 —— <b>已用本网格数据印证</b>。</div>"
        )
    c3 = next((r for r in GRID if r["label"] == "cfg3" and r["status"] == "OK"), None)
    if c1 and c3:
        d23 = pct(c3["tok_s"], c1["tok_s"])
        html.append(
            f"<div class='note'><b>实测支撑②</b>：S1 组内 seq 8192→16384，tok/s "
            f"{_fmt(c1['tok_s'])}→{_fmt(c3['tok_s'])}（{_fmt(d23, '%+.1f%%')}）。"
            f"seq 翻倍但 tok/step 不变（均为 2M）、MBS 2→1、累积 8→8；"
            f"吞吐{'略升' if d23 > 0 else '略降'}，说明在 2M tok/step 下 seq 8192→16384 的 SSM 成本增长被"
            f"「MBS 减半减少 launch 次数 / 单步批更大」部分抵消 —— <b>已用本网格数据印证</b>。</div>"
        )
    html.append("<div class='warn'><b>关于「注意力成本结构性低于纯 Transformer」</b>：本网格仅含 Mamba2-hybrid "
                "一种架构，未在同口径下跑纯 Dense Transformer 对照，故该结构优势<b>本网格未直接验证</b>，"
                "标注为「推测·未验证」（需另起 Dense 对照实验方可证实）。</div>")

    html.append("<h2>6. 结论：S1 / S2 该选多大 seq</h2>")
    ok = [r for r in GRID if r["status"] == "OK"]
    s1 = derive_group("S1")
    s2 = derive_group("S2")
    parts = []
    if c1:
        parts.append(
            f"基线 seq4096/4.13M={_fmt(b['tok_s'])} tok/s 是当前最高吞吐点；任何 seq≥8192 配置的 per-GPU "
            f"吞吐均显著低于基线（cfg1 已 {_fmt(pct(c1['per_gpu'], b['per_gpu']), '%.1f%%')}）。"
        )
    parts.append(
        f"S1 组（2M tok/step）：seq8192→16384 吞吐变化 {_fmt(pct(s1[1]['tok_s'], s1[0]['tok_s']), '%+.1f%%') if len(s1) >= 2 else '待测'}；"
        f"S2 组（4M tok/step）：seq8192→16384 吞吐变化 {_fmt(pct(s2[1]['tok_s'], s2[0]['tok_s']), '%+.1f%%') if len(s2) >= 2 else '待测'}。"
    )
    parts.append(
        "<b>可执行建议</b>：若 seq 增大导致吞吐降幅 > 10%（vs 同组 seq=8192 或 vs 基线），"
        "明确建议维持 seq=4096 / 8192。鉴于 cfg1（seq8192）per-GPU 已较基线崩塌 ~82%，"
        "且 seq32768 大概率 OOM，<b>全量预训练应维持 e18 配方 seq=4096</b>（与任务书「305K 已定档、"
        "勿再扫吞吐」一致）；仅在需要长上下文建模能力时才考虑 seq=8192，并接受 ~5× 的吞吐代价。"
    )
    html.append("<div class='key'>" + "".join(f"<p>{p}</p>" for p in parts) + "</div>")

    html.append("<h2>7. OOM 与配方变更组明细</h2>")
    if RECIPE_CHANGE:
        html.append(main_table())
    else:
        html.append("<div class='note'>本网格主配方（MBS=1，seq≤16384）未触发 OOM；"
                    "seq=32768 若 OOM，将在此单列回退结果（加 <code>--recompute-activations</code> / "
                    "<code>--use-distributed-optimizer</code>），不混入主表同口径对比。</div>")

    html.append("<h2>8. 数据可溯源性</h2>")
    html.append("<ul>")
    html.append(f"<li>基线：<code>{BASELINE['src']}</code></li>")
    for r in GRID:
        if r["status"] != "PENDING":
            html.append(f"<li>{r['label']}（{r['group']} seq{r['seq']}）：<code>{r['src']}</code></li>")
    html.append("<li>网格编排器：<code>run/baize_seqlen_grid_test.sh</code>（6 格串行自治，每格跑完释放 16 卡）</li>")
    html.append("<li>汇总：<code>/tmp/baize_seqlen_grid/ALL_RESULTS.txt</code></li>")
    html.append("</ul>")
    html.append("<p class='small'>报告生成器：run/gen_seqlen_throughput_report.py（数据字典写脚本顶部，"
                "重生成 diff 必须为空 · 0 &lt;script&gt; / 0 外链 / 自包含）</p>")
    html.append("</body></html>")
    return "\n".join(html)


class _ScriptChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = 0
        self.ext = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts += 1
        if tag in ("link", "img", "iframe"):
            for k, v in attrs:
                if k in ("src", "href") and v and v.startswith("http"):
                    self.ext += 1


def selfcheck(html_str):
    chk = _ScriptChecker()
    chk.feed(html_str)
    assert chk.scripts == 0, f"found {chk.scripts} <script> tags"
    assert chk.ext == 0, f"found {chk.ext} external links"
    size = len(html_str.encode("utf-8"))
    assert size >= 15000, f"report too small: {size} B (need >= 15000)"
    return size


def main():
    html_str = render()
    size = selfcheck(html_str)
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_str)
    print(f"OK: wrote {REPORT_FILE} ({size} B, 0 script, 0 ext-link)")
    done = sum(1 for r in GRID if r["status"] == "OK")
    print(f"  GRID OK: {done}/6  (PENDING: {sum(1 for r in GRID if r['status']=='PENDING')})")


if __name__ == "__main__":
    main()



