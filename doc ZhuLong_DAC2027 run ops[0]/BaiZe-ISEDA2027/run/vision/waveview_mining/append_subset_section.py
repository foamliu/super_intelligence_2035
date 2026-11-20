#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append the EDA-Eval-DesignFlow-WaveView subset section (task §2026-11-17 16:3x)
to reports/report_vision_waveview_selftest_agent_zh.html, in-place overwrite.
Reads: summary_real.json (per-case V0/V1/V2), the WaveView jsonl (subset stats).
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.normpath(os.path.join(HERE, "..", ".."))  # .../run
SUMM = os.path.join(RUN, "vision", "vqa_tool", "waveview_selftest", "summary_real.json")
AUDIT = os.path.join(RUN, "vision", "vqa_tool", "waveview_selftest", "audit_real.json")
JSONL = os.path.join(RUN, "vision", "EDA-Eval-DesignFlow-WaveView.jsonl")
REP = os.path.join(RUN, "reports", "report_vision_waveview_selftest_agent_zh.html")
SHA256 = "623842b5341cc089c530bb7073b76690d2691c3fd36893a81c0b162ec4968bcd"


def esc(s):
    return html.escape(str(s))


def subset_stats():
    cnt = {}
    vr = wf = n_im = 0
    excluded = None
    for line in open(JSONL, encoding="utf-8"):
        d = json.loads(line)
        cnt[d["source"]] = cnt.get(d["source"], 0) + 1
        if d["vqa_runnable"]:
            vr += 1
        if d["waveform_relevant"]:
            wf += 1
        if d.get("image_required"):
            n_im += 1
        if d["source"] == "image_only_non_waveform":
            excluded = d
    return cnt, vr, wf, n_im, excluded


def main():
    summ = json.load(open(SUMM, encoding="utf-8"))
    aud = json.load(open(AUDIT, encoding="utf-8"))
    cnt, vr, wf, n_im, excluded = subset_stats()
    rows = summ["rows"]
    V0p = summ["V0_pass"]; V1p = summ["V1_pass"]; V2p = summ["V2_pass"]
    pq = summ["per_quantity"]
    mc = summ["mcnemar_V0_vs_V2"]
    n_total = sum(cnt.values())
    tier_cn = {"alpha": "α", "beta": "β", "gamma": "γ"}
    trows = ""
    for r in rows:
        cid = r["case_id"].replace("EDA-Eval-DesignFlow-", "")
        tier = tier_cn.get(r["tier"], r["tier"])
        v0c = "pos" if r["V0"] == "PASS" else "neg"
        v1c = "pos" if r["V1"] == "PASS" else "neg"
        v2c = "pos" if r["V2"] == "PASS" else "neg"
        flip = "✓" if r.get("flip_V0_V2") else ""
        trows += (
            f"<tr><td>{esc(r['tag'])}</td><td>{tier}</td><td>{esc(cid)}</td>"
            f"<td class='{v0c}'>{r['V0']}<br><span class='muted'>{r['V0_k']}</span></td>"
            f"<td class='{v1c}'>{r['V1']}<br><span class='muted'>{r['V1_k']}</span></td>"
            f"<td class='{v2c}'>{r['V2']}<br><span class='muted'>{r['V2_k']}</span></td>"
            f"<td>{r['k_total']}</td><td>{flip}</td></tr>")
    v0r = round(pq["V0_rate"] * 100, 1)
    v1r = round(pq["V1_rate"] * 100, 1)
    v2r = round(pq["V2_rate"] * 100, 1)
    trows += (
        f"<tr style='font-weight:bold;background:#eef3f8'><td colspan='3'>每量合计</td>"
        f"<td>{pq['V0_ok']}/{pq['V0_total']}<br>{v0r}%</td>"
        f"<td>{pq['V1_ok']}/{pq['V1_total']}<br>{v1r}%</td>"
        f"<td>{pq['V2_ok']}/{pq['V2_total']}<br>{v2r}%</td>"
        f"<td>{pq['V2_total']}</td><td>{mc['b_improved']}</td></tr>")
    excl_html = ""
    if excluded:
        excl_html = (
            f"<div class='card'><b>诚实排除（非波形）</b>：{esc(excluded['task_id'])} "
            f"(shard {excluded['shard']}, domain={esc(excluded['domain'])}) 有 {len(excluded['image_path'])} 张 PNG "
            f"但 <b>零波形关键词命中</b> → <code>source=image_only_non_waveform</code>, "
            f"<code>vqa_runnable=false</code>，不进入 V0/V1/V2。理由：{esc(excluded['exclusion_reason'])}</div>")
    return summ, aud, cnt, vr, wf, n_im, excluded, V0p, V1p, V2p, pq, mc, n_total, v0r, v1r, v2r, trows, excl_html


def build_section(V0p, V1p, V2p, pq, mc, n_total, wf, cnt, vr, n_im, v0r, v1r, v2r, trows, excl_html):
    sec = f"""
<h1 style="margin-top:24px">§0 WaveView 评测子集 · EDA-Eval-DesignFlow-WaveView.jsonl（2026-11-17 16:3x 用户令）</h1>
<p class="muted">vision 线 · 自主 SSH 36.15 全量扫描 EDA-Eval-DesignFlow.jsonl 自建并维护子集 · 用户原话三问：①评测集建立了吗 ②基线(EDA_Flow_Bench)分数 ③加 Qwen3.5-2B VQA 后分数</p>
<div class="card verdict pos">
<b>三问回答</b>：<br>
① <b>已建立</b>。36.15 与本地 <code>vision/EDA-Eval-DesignFlow-WaveView.jsonl</code> 各一份（sha256 <code>{SHA256[:16]}…</code>，224 行）。<br>
② <b>基线 V0（无 VQA、纯文本不看图）</b>：整题 <b>{V0p}/10</b>，每量 <b>{pq['V0_ok']}/{pq['V0_total']}={v0r}%</b>。<br>
③ <b>+ Qwen3.5-2B VQA</b>：V1（基模）整题 <b>{V1p}/10</b>、每量 {v1r}%；<b>V2（基模+rft2 适配器）整题 {V2p}/10、每量 {v2r}%</b>。
McNemar V0 vs V2：b={mc['b_improved']} c={mc['c_regressed']} p={mc['p_value']}（仅 1 个不一致对，n=10 样本不足，p 仅参考）。
</div>
<h2>0.1 筛选口径与子集构成</h2>
<div class="card"><ul>
<li><b>全量扫描</b>：36.15 上 <code>EDA-Eval-DesignFlow.jsonl</code>（A/B/C/D 四 shard 合并，{n_total} 题含合并冗余）逐行解析。</li>
<li><b>入选判据（自定、可复算）</b>：(K) task_id/prompt/metadata/attachments/expected_artifacts 命中波形关键词
<code>waveform|waveview|fsdb|vcd|eye[-_ ]?diagram|oscilloscope?|edge[-_ ]?timing|signal[-_ ]?extract|波形|\\bwave\\b</code>；或 (I) <code>assets/&lt;task_id&gt;/</code> 下有可见光栅图。有 check.py 单独不充分（所有题都有）。</li>
<li><b>子集构成</b>：入选 <b>224</b> = 波形相关(keyword) <b>{wf}</b> + 仅图片非波形 <b>{cnt.get('image_only_non_waveform',0)}</b>；
按 source：original_png={cnt.get('original_png',0)} · text_only={cnt.get('text_only',0)} · no_check={cnt.get('no_check',0)} · image_only_non_waveform={cnt.get('image_only_non_waveform',0)}；有可见图 {n_im}。</li>
<li><b>可跑集 vqa_runnable = 波形相关 ∧ 有可见图 ∧ 有 check.py = {vr}</b>。即 V0/V1/V2 实际运行的 10 道（designflow 已恢复原形态、sha256 校验只读复制的真题 PNG）。
每条记录含 task_id/shard/domain/waveform_relevant/image_required/image_path/has_check/k_conditions/kw_match/baseline_verdict/failure_mode_tier/source/exclusion_reason/vqa_runnable。</li>
<li><b>用户第二条修正落地</b>：不预设「这道题需不需要看图」——让 V0 vs V1/V2 通过率差异说话。181 道 text_only 题无图，VQA 无图可读，V0=V1=V2 平凡相等，故实验聚焦 10 道有图可跑集；它们仍登记在子集内（完整性）。</li>
</ul></div>
{excl_html}
<h2>0.2 V0 / V1 / V2 三段对照（10 道可跑真题，同 check.py 同口径）</h2>
<table><tr><th>tag</th><th>tier</th><th>case</th><th>V0 文本</th><th>V1 基模VQA</th><th>V2 rft2-VQA</th><th>k</th><th>V0→V2翻转</th></tr>
{trows}</table>
<p class="muted">tier：α=未engage · β=只看文本 · γ=engage但读不懂图。V2 唯一整题 PASS = EyeApertureSelect（α1，9/9）。每量准确率 V0 {v0r}% → V1 {v1r}% → V2 {v2r}%（+{round(v2r-v0r,1)}pp）。数据源 <code>summary_real.json</code>（REAL/ 目录，真题 PNG 重跑）。</p>
"""
    return sec


def build_section2(aud, v0r, v2r):
    sec2 = f"""
<h2>0.3 🚫 反作弊审计</h2>
<div class="card">cheat = <b>{aud['cheat']}</b>，cheat_count = {aud['cheat_count']}，VQA 调用 {aud['vqa_calls']} 次，runner 源码内 image_reads = {aud['image_reads']}（无 PIL/cv2/OCR/base64/读字节；V1/V2 仅经 HTTP VQA 工具读图，V0 不看图）。审计源 <code>audit_real.json</code>。</div>
<h2>0.4 可复现性</h2>
<div class="card"><ul>
<li>构建脚本：<code>vision/waveview_mining/build_waveview_subset.py</code>（36.15 上同份）。在 36.15 bench 目录 <code>python3 build_waveview_subset.py</code> 重跑即可重生 jsonl。</li>
<li>子集文件：36.15 <code>/nasdata/.../EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-WaveView.jsonl</code> + 本地 <code>vision/EDA-Eval-DesignFlow-WaveView.jsonl</code>（sha256 <code>{SHA256}</code>，224 行）。</li>
<li>三段结果：<code>vision/vqa_tool/waveview_selftest/REAL/</code>（V1/V2）+ <code>V0/</code> + <code>summary_real.json</code> + <code>audit_real.json</code>。VQA 后端 :30001（基模）/ :30003（rft2_adapter）。</li>
</ul></div>
<h2>0.5 诚实结论与口径</h2>
<div class="card"><ul>
<li><b>MLLM 价值度量（用户裁定）</b>：WaveView 子集上 <b>有 VQA vs 无 VQA 通过率差异</b>。V0=0/10 → V2=1/10，每量 {v0r}%→{v2r}%（+{round(v2r-v0r,1)}pp），方向正向但 <b>n=10、仅 1 个不一致对，McNemar p=1.0，统计不可分辨</b>。</li>
<li><b>不编造</b>：181 text_only 题未单跑（无图，VQA 无作用，平凡相等）；IRReportPdf 非波形已诚实排除并写明理由；未拿合成集冒充真题。</li>
<li><b>下方正文</b>为 2026-11-14 agent 臂（G0/G1/G2）自测与 11-15 真题三段附录，保留以供溯源；本节为 11-17 扩大子集重跑的交付。</li>
</ul></div>
<hr>
"""
    return sec2


def run():
    (summ, aud, cnt, vr, wf, n_im, excluded, V0p, V1p, V2p, pq, mc,
     n_total, v0r, v1r, v2r, trows, excl_html) = main()
    sec = build_section(V0p, V1p, V2p, pq, mc, n_total, wf, cnt, vr, n_im,
                        v0r, v1r, v2r, trows, excl_html)
    sec += build_section2(aud, v0r, v2r)
    src = open(REP, encoding="utf-8").read()
    if "§0 WaveView 评测子集" in src:
        i = src.find('<h1 style="margin-top:24px">§0 WaveView 评测子集')
        j = src.find("<hr>", i) + 4
        src = src[:i] + sec + src[j:]
    else:
        src = src.replace("</h1>", "</h1>\n" + sec, 1)
    src = src.replace(
        "<title>Vision WaveView 10 题",
        "<title>Vision WaveView 子集(224题/10可跑) + agent 臂自测", 1)
    open(REP, "w", encoding="utf-8").write(src)
    print(f"[wrote] {REP} ({len(src)} bytes)")
    print(f"[stats] subset={n_total} vqa_runnable={vr} V0={V0p}/10 "
          f"V1={V1p}/10 V2={V2p}/10")


if __name__ == "__main__":
    run()


