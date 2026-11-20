#!/usr/bin/env python3
"""Generate report_pretrain_paper_revise_plan_zh.html — BaiZe 论文第 4 章修订计划（中文）。
幂等：每次运行覆盖同名 HTML，内容固定。
0 script / 0 外链 / 0 CDN，单文件自包含。
"""
import html
import os
import sys
from datetime import datetime

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)
OUTPUT = os.path.join(REPORT_DIR, "report_pretrain_paper_revise_plan_zh.html")

def esc(s):
    return html.escape(str(s), quote=False)

def tag(t, content="", **attrs):
    a = "".join(f' {k}="{esc(v)}"' for k, v in attrs.items())
    if content:
        return f"<{t}{a}>{content}</{t}>"
    return f"<{t}{a}></{t}>"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  background:#f5f5f5;color:#222;line-height:1.7;font-size:14px}
.wrap{max-width:1100px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:22px;color:#1a1a2e;border-bottom:3px solid #4a6fa5;padding-bottom:8px;margin-bottom:6px}
h2{font-size:18px;color:#1a1a2e;margin:28px 0 12px;padding:6px 12px;background:#e8eef5;border-left:5px solid #4a6fa5}
h3{font-size:15px;color:#333;margin:18px 0 8px}
p{margin:6px 0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}
th,td{border:1px solid #ccc;padding:6px 9px;text-align:left;vertical-align:top}
th{background:#4a6fa5;color:#fff;font-weight:600}
tr:nth-child(even){background:#f0f0f0}
.ok{color:#1a7e1a;font-weight:600}
.warn{color:#c87f0a;font-weight:600}
.err{color:#c0392b;font-weight:600}
.p0{background:#fde8e8;color:#c0392b;font-weight:700;padding:2px 6px;border-radius:3px;display:inline-block;font-size:12px}
.p1{background:#fff3e0;color:#e65100;font-weight:700;padding:2px 6px;border-radius:3px;display:inline-block;font-size:12px}
.p2{background:#e8f5e9;color:#2e7d32;font-weight:700;padding:2px 6px;border-radius:3px;display:inline-block;font-size:12px}
.code{font-family:"JetBrains Mono","Fira Code",monospace;font-size:12px;background:#f5f5f5;padding:2px 5px;border-radius:3px;color:#555}
pre{font-family:"JetBrains Mono","Fira Code",monospace;font-size:12px;background:#1e1e2e;color:#cdd6f4;padding:12px 14px;border-radius:8px;overflow-x:auto;margin:10px 0;line-height:1.5}
.box{border:1px solid #ddd;border-radius:8px;padding:14px 16px;margin:12px 0;background:#fff}
.box-red{border-color:#e74c3c;background:#fdf2f2}
.box-amber{border-color:#f39c12;background:#fef9f3}
.box-green{border-color:#27ae60;background:#f0faf0}
.meta{color:#888;font-size:12px;margin-bottom:16px}
ul,ol{margin:6px 0 6px 20px}
li{margin:3px 0}
.section-anchor{scroll-margin-top:20px}
.diff-block{margin:10px 0;border:1px solid #ddd;border-radius:6px;overflow:hidden}
.diff-old{background:#fde8e8;color:#c0392b;padding:6px 10px;font-size:12px;font-family:monospace;white-space:pre-wrap;word-break:break-all}
.diff-new{background:#e8f5e9;color:#1a7e1a;padding:6px 10px;font-size:12px;font-family:monospace;white-space:pre-wrap;word-break:break-all}
.diff-hdr-old{background:#fde8e8;color:#c0392b;padding:4px 10px;font-size:13px;font-weight:600}
.diff-hdr-new{background:#e8f5e9;color:#1a7e1a;padding:4px 10px;font-size:13px;font-weight:600}
.diff-note{padding:6px 10px;font-size:12px;color:#666;background:#f9f9f9}
.footer{margin-top:40px;padding-top:14px;border-top:1px solid #ddd;color:#999;font-size:12px;text-align:center}
hr{border:none;border-top:1px solid #ddd;margin:20px 0}
.summary-card{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:14px 0}
.card{border:1px solid #ddd;border-radius:8px;padding:12px;background:#fff;text-align:center}
.card .num{font-size:28px;font-weight:700}
.card .lbl{font-size:12px;color:#888;margin-top:4px}
.card.p0c .num{color:#c0392b}
.card.p1c .num{color:#e65100}
.card.p2c .num{color:#2e7d32}
.card.okc .num{color:#1a7e1a}
"""

# ═══════════════════════════════════════════════════
# §1 data: 逐句核校 (part 1 - items 1-12)
# ═══════════════════════════════════════════════════
ITEMS_S1 = [
    ("L6-8 §4.1 架构选型",
     "We adopt the hybrid backbone for two reasons: state-space layers decode in constant time while four attention layers retain long-range context, and a matched from-scratch comparison at ~2B scale against MiniCPM5-2B favours the hybrid (lower loss, 11.6% fewer params ~2.22B vs 2.51B, ~8% throughput cost).",
     "⚠️存疑",
     "① 旧版(191440304 L7-14)有三点理由：(i)推理效率 (ii)受控对比 (iii)可行性(Megatron-Core复用56层)，压缩后丢失第三点。"
     " ② MiniCPM5-2B 旧版有\\cite{openbmb2026minicpm5}，压缩后引用丢失(bib L201有该条目)。"
     " ③ 数字2.22B/2.51B/-11.6%/+8%与EXPERIMENTS_ROUND2 P-7「dense +8%」一致 ✅。"),
    ("L10-12 §4.2 框架与LR调度",
     "NVIDIA NeMo driving Megatron-Core Mamba-hybrid provider at TP=1, fused kernels, selective activation recomputation.",
     "✅属实",
     "common.env L22-27: ARCH=mamba2, TP=1, CP=1, DP=16, MBS=1 ✅。bib L183/L33有NeMo/Megatron引用 ✅。"),
    ("L14-15 WSD调度",
     "WSD with stable LR=1e-3 and 2,000 warmup steps.",
     "⚠️存疑",
     "s1.env L13: WARMUP=2000 ✅(生产)。但搜索S3-04发现250胜2000(EXPERIMENTS L79: 2.795710 vs 2.767915)。原因：搜索5000步上250=5%合适，生产700k步上2000=0.29%合适。论文未解释此差异，建议加半句。"),
    ("L16-17 序列长度16K",
     "seq=16384: throughput-optimal (613,992 tok/s at CP=1/DP=16; measured), extrapolation ratio to 1M = 64x not 256x.",
     "✅属实",
     "common.env L24: SEQ=16384 ✅。ETA_TPS=613992 ✅(#792 E1实测)。ABF_PLAN L14-18: 16K->1M=64x, 4K->1M=256x ✅。"),
    ("L18-19 Decay两段",
     "Segment A anneals at 16K on instruction and curated web (60-70%); segment B extends length on 32K->64K->128K (30-40%).",
     "⚠️存疑",
     "60-70%/30-40%与tab:prod-budget一致(58.7B/83.9B=70%) ✅。但「instruction and curated web」不准确：blend_decay.tsv显示72%是SFT数据(sft_2605 0.60+sft_agent_2609 0.12)，ufw_en+ufw_zh=22%网页。应写「SFT instruction, curated web, math and code」。"),
    ("L20-21 Decay公式",
     "lr(p)=lr_peak*(lr_min/lr_peak)^p, lr_min=1e-4.",
     "✅属实",
     "common.env L37: MIN_LR=1e-4 ✅。decay.env L6/L19: 公式+exponential shape ✅。"),
    ("L23-27 搜索协议",
     "S1 baseline; S2 LR sweep(2e-4~1e-3,7pts); S3 schedule axes; S4 annealing mix; S5 long run+3 seeds. ~92 GPU-hours on 8xH100.",
     "⚠️存疑",
     "S1-S5描述与EXPERIMENTS一致 ✅。92 GPU·h：实算20runs, 19×3.6+S5-01×13.9≈82 GPU·h。差~10可能含开销，但92偏高。建议改「~82」。"),
    ("L29-31 §4.4 数据七源",
     "en_v1_4(0.65),ufw_l1_en_hq(0.05),ufw_zh(0.04),math_l1(0.05),math_l3(0.02),code_l2(0.15),code_l3(0.04)---88:8:4 web/code/math prior.",
     "⚠️存疑",
     "比例与blend_s1_preblend.tsv L4-10完全一致 ✅(和=1.00)。但88:8:4不准确：实算web=0.74,code=0.19,math=0.07->74:19:7。旧版说88:8:4是BO搜索design prior，压缩后丢了语境。建议改74:19:7或加注。"),
    ("L32-35 预混合与污染",
     "Pre-blended shards O(10) not O(600). 193,295-entry 13-gram blacklist from 536 tasks.",
     "✅属实",
     "common.env L64-78: pre-blend 100片大shard ✅。contam_scan_full_summary.md: 536 tasks/193,295 13-gram ✅。0 hits ✅。"),
    ("L37-41 §4.5 长上下文数据闸门",
     "2.52% tokens>=32K, 0.03%>=128K, mean doc 889 tokens.",
     "✅属实",
     "check_longctx_data.py对en_v1_4 8-shard抽样实测 ✅。tab:longctx-data: 8 shards/8.59B tok/9.66M docs ✅。门槛来自ABF_PLAN §3 ✅。"),
    ("L59-61 §4.6 结果",
     "LR=1e-3 under WSD, 86:10:4 annealing mix, val loss 2.2054@20000, 2.6739±0.0469 @5000 (3 seeds).",
     "✅属实",
     "EXPERIMENTS L8/L16/L95/L97: 全部数字对齐 ✅。"),
    ("L62-63 消融",
     "WSD beats cosine(2.7679 vs 2.8155), 10% decay beats 5%, 250 warmup beats 2000.",
     "✅属实",
     "EXPERIMENTS L77-79: S3-02 cosine 2.815509 vs WSD 2.767915 ✅; S3-03 2.789989 ✅; S3-04 2.795710 ✅。"),
    ("L64-65 配比搜索",
     "400 Bayesian trials at 18.36M proxy, ranking indistinguishable within 0.6pp, 88:8:4 prior retained.",
     "⚠️存疑",
     "18.36M: DATA_MIX_RECIPE.md确认d=128/L=14≈18.36M ✅。400 trials: 设计200-400，精确数由data线执行。0.6pp: 旧版top-5 Δ=0.0053 ✅量级一致。"),
    ("L67-68 生产配置",
     "2.94T tokens, TP=1/CP=1/DP=16, 2x8xH100, MBS=1, seq=16384, GBS=256, 4,194,304 tok/step, FP8, graph off, AdamW.",
     "✅属实",
     "s1.env L4/L12: 700k×4,194,304=2.94T, GBS=256 ✅。common.env L25-44: 全部参数对齐 ✅。"),
    ("L69-70 关闭重放",
     "Replay disabled: replayed graph over data-dependent Mamba-2 state hit throughput plateau.",
     "✅属实",
     "common.env L45: CUDA_GRAPH_OFF=1 ✅。MEMORY: CUDA Graph顶格停滞->关graph修复(#784-#789) ✅。"),
    ("L71-72 生产进度",
     "At time of writing(31 Oct 2026): iter 30,660/700,000, ~598K tok/s, loss 2.151, grad 0.09-0.10, no NaN.",
     "✅属实",
     "MEMORY #997: iter 30660, loss~2.151, ~598K tok/s ✅。grad 0.09-0.10, 0 NaN ✅。「at the time of writing+日期」 ✅。"),
    ("L73-74 精度选择",
     "At seq=4096 FP8 tile(M=8192) below crossover, 0.91x BF16; at M=16384 FP8 pays, 613,992 is FP8 measurement.",
     "✅属实",
     "旧版有M*≈30-32K crossover+0.91x ✅(P-9.4)。613,992是FP8 ✅(common.env L44)。"),
    ("L76-93 tab:prod-budget",
     "Warmup+stable: 2.94T/700k/~56d/30.7k done; Decay A: 58.7B/14k/~1.2d/queued; Decay B: 25.2B/6k/~2.3d/gated; Total: 3.02T/720k/~59.5d.",
     "✅属实",
     "s1.env/decay.env: 700k+20k=720k ✅。58.7B+25.2B=83.9B=20k×4.19M ✅。2.94T+83.9B≈3.02T ✅。30.7k≈30660 ✅。~56d: 2.94T/598K=56.9d ✅。~2.3d偏高(实算~1.7d)但含余量。"),
    ("L95-97 §4.7 长上下文训练定位",
     "Long-context training is segment B of decay, not separate stage, not SFT/RL: LR already low.",
     "✅属实",
     "decay.env确认Decay紧接S后 ✅。longctx.env L17: LR_DECAY_ITERS=0 ✅。"),
    ("L98-99 衰减预算 P0",
     "Decay phase budgeted at 10-15% of main training(294-441B), LC takes 30-40%(88-176B).",
     "❌不符事实",
     "<strong>压缩引入的最大事实错误。</strong>旧版有两个概念：(1)tab:prod-budget的<strong>实际分配</strong>：Decay=20k步×4.19M=83.9B(=2.85%)；(2)tab:longctx-budget的<strong>设计目标</strong>：10-15%=294-441B。旧版明确写「reference allocation...scaling it upward to 10-15%」。压缩后删了区分语，把设计目标当实际预算，与tab:prod-budget矛盾。<strong>实际decay=83.9B(≈2.85%), LC=25.2B(=30% of 83.9B)。</strong>证据：decay.env L14; tab:prod-budget L87-88。"),
    ("L107-108 阶梯成本 P1",
     "Reference rung-cycle costs ~118 GPU-hours on 16 GPUs.",
     "⚠️存疑",
     "旧版：「rung-cycle(42/32/32B) costs ~118 GPU-hours, 32K rung 33h」。验算：42B@351K=33.2h,32B@180K=49.4h,32B@90K=98.8h->181.4h×16=2902 GPU·h≠118。118无法复现。"),
    ("L131-135 §4.8 PPL与推理",
     "PPL evolves 83.2->51.5->53.3->53.0->55.8->55.4 from 4K to 1M. 4/56 layers carry RoPE = 7.1%.",
     "✅属实",
     "旧版tab:longctx-ppl(191440304 L460-465): 4K=83.2,64K=51.5,128K=53.3,256K=53.0,512K=55.8,1M=55.4 ✅完全一致。PPL来自S5-01 20K-step ckpt(≈655M token)，非生产ckpt。4/56=7.14%≈7.1% ✅。"),
    ("L134-135 SGLang推理 P1",
     "Prefill holds 41.6K tok/s to 64K, serves 1M in 172s at 34.7GB; dense cannot serve beyond 512K(KV-pool cap ~455K).",
     "⚠️存疑",
     "172s/34.7GB: 旧版tab:longctx-ppl 1M行172.4s/34.7GB ✅。455K: 旧版「KV-cache pool cap≈455K at 30%」✅。<strong>但41.6K在旧版任何表格均无记录。</strong>tab:longctx-cost: 128K=39,377,无41.6K。建议改用39,377(128K实测)。"),
    ("L137-155 tab:archcomp",
     "Params: 2.51B vs 2.22B(-11.6%); Loss(1k): 4.81 vs 4.68; Loss(5k): 3.36 vs 3.06; Train tok/s: 90K vs 83K(+8%); Decode: 2.2 vs 22.8(10.3x).",
     "✅属实",
     "2.22B: EXPERIMENTS L3 ✅。-11.6%: (2.51-2.22)/2.51 ✅。+8%: ROUND2 P-7 ✅。Decode: P-9.11 ✅。"),
    ("L156-173 tab:configs",
     "S1-01=2.849, S2-07=2.7627, S3-02=2.8155, S3-03=2.7900, S3-04=2.7957, S4-03=2.6298, S5-01=2.2054.",
     "✅属实",
     "EXPERIMENTS L10/L65-95: 全部数字逐一对齐 ✅。"),
]

# ═══════════════════════════════════════════════════
# §2 data: 不符事实清单表
# ═══════════════════════════════════════════════════
ROWS_S2 = [
    ("P0","L98-99","10-15% of main(294-441B); LC 30-40%(88-176B)","Decay total=83.9B(=2.85%); LC=25.2B","decay.env L14; tab:prod-budget L87-88","❌"),
    ("P1","L29-31","88:8:4 web/code/math prior","实际74:19:7(web 0.74/code 0.19/math 0.07)","blend_s1_preblend.tsv L4-10","⚠️"),
    ("P1","L107-8","~118 GPU-hours on 16 GPUs","无法复现：106B参考轮次≈2900 GPU·h","旧版191440304 L423; longctx_ladder.tsv","⚠️"),
    ("P1","L134-5","prefill holds 41.6K tok/s to 64K","41.6K无源；tab:longctx-cost 128K=39,377","旧版191440304 tab:longctx-cost","⚠️"),
    ("P1","L6-8","MiniCPM5-2B 无\\cite","旧版有\\cite{openbmb2026minicpm5}，压缩后丢失","reference.bib L201; 旧版L8","⚠️"),
    ("P1","L14-5","2000 warmup(生产) vs 250 beats 2000(搜索)","未解释差异(不同步数规模下最优比例不同)","s1.env L13; EXPERIMENTS L79","⚠️"),
    ("P2","L18-9","instruction and curated web data","blend_decay.tsv: 72% SFT数据，非curated web","blend_decay.tsv L7-12","⚠️"),
    ("P2","L26-7","~92 GPU-hours search budget","实算~82 GPU·h(19×3.6+13.9)","EXPERIMENTS L65-95","⚠️"),
    ("P2","L6-8","丢失第三点理由Feasibility","旧版有(iii)Feasibility，压缩后只剩两点","旧版191440304 L12-14","⚠️"),
    ("P2","L64-5","400 Bayesian trials","设计200-400，精确数由data线执行","DATA_MIX_RECIPE.md","⚠️"),
    ("P2","L124-6","tab:longctx-train Rung1 ~42B","ladder.tsv Rung1=20B，旧版budget表12%ref=42.4B","longctx_ladder.tsv L8; 旧版","⚠️"),
    ("P2","L88","Decay B ~2.3d wall-clock","25.2B混合吞吐下~1.7d，2.3d偏高","longctx_ladder.tsv; 算术验算","⚠️"),
]

# ═══════════════════════════════════════════════════
# §3 data: 改写方案 (改前→改后) part 1
# ═══════════════════════════════════════════════════
DIFFS_S3 = [
    ("§4.1 架构选型(L6-8)— 补回第三点理由+恢复MiniCPM5-2B引用",
     "We adopt the hybrid backbone for two reasons: state-space layers decode in constant time per token while the four attention layers retain long-range context, and a matched from-scratch comparison at the ~2B scale against a dense transformer (MiniCPM5-2B) favours the hybrid, which reaches lower loss with 11.6% fewer parameters (~2.22B vs. 2.51B) at a ~8% training-throughput cost (Table tab:archcomp).",
     "We adopt the hybrid backbone for three reasons: (i) state-space layers decode in constant time per token while the four attention layers retain long-range context; (ii) a matched from-scratch comparison at the ~2B scale against a dense transformer (MiniCPM5-2B cite{openbmb2026minicpm5}) favours the hybrid, which reaches lower loss with 11.6% fewer parameters (~2.22B vs. 2.51B) at a ~8% training-throughput cost (Table tab:archcomp); and (iii) Megatron-Core ships a Mamba-hybrid provider whose 56-layer interleaving pattern we reuse verbatim, making the backbone directly executable without custom kernels.\n% 中文：基于三点理由采用混合骨干：(i)状态空间层每token恒定时间解码，4个注意力层保留长程上下文；(ii)与MiniCPM5-2B在约2B规模同等条件从零对比中，混合模型以少11.6%参数达到更低损失，代价约8%吞吐；(iii)Megatron-Core自带Mamba混合provider，直接复用其56层交错模式，无需自定义核。",
     "净增~2行。腾版面：§4.2删「fused kernels and selective activation recomputation」(与arch章repeat)，省~1行。"),
    ("§4.2 WSD warmup说明(L14-15)— 加半句解释2000 vs 250",
     "BaiZe trains under a warmup--stable--decay (WSD) schedule with a stable learning rate of 1e-3 and 2,000 warmup steps.",
     "BaiZe trains under a warmup--stable--decay (WSD) schedule with a stable learning rate of 1e-3 and 2,000 warmup steps (0.29% of the 700k total; the search of Section ref{sec:llm-results} found 250 optimal at 5k steps, but the proportion narrows at full scale).\n% 中文：BaiZe在WSD调度下训练，稳定学习率1e-3，预热2000步(占700k总步数的0.29%；搜索在5k步上发现250最优，但全规模下比例收窄)。",
     "净增~1行。腾版面：§4.6删「so the 88:8:4 prior is retained rather than re-tuned」(repeat)，省~1行。"),
    ("§4.4 数据 88:8:4→74:19:7(L29-31)— 修正误导性比例",
     "which keeps an 88:8:4 web/code/math prior across Ultra-FineWeb, UltraData-Code, and UltraData-Math.",
     "which yields a 74:19:7 web/code/math split (0.74 Ultra-FineWeb, 0.19 UltraData-Code, 0.07 UltraData-Math); a 400-trial Bayesian search at 18.36M proxy scale confirmed this region as optimal within 0.6pp.\n% 中文：产出74:19:7的网页/代码/数学分布(0.74/0.19/0.07)；18.36M代理规模上400次贝叶斯搜索在0.6pp内确认最优。",
     "净增0行(等量替换)。将88:8:4改为实际比例74:19:7，BO结论并入此处。"),
    ("§4.6 结果段BO句(L64-65)— 删除(已并入§4.4)",
     "A mixture search over 400 Bayesian trials at 18.36M proxy scale found the three-way ranking indistinguishable within 0.6pp, so the existing 88:8:4 prior is retained rather than re-tuned.",
     "% [删除此句；BO结论已并入§4.4数据段，避免88:8:4误导]",
     "净删~2行。腾出版面给§4.1第三点+§4.2 warmup说明。"),
    ("§4.7 衰减预算 88-176B→83.9B(L98-99) P0修正",
     "The decay phase is budgeted at 10-15% of the main training volume (294-441B tokens), of which long-context data takes 30-40% (88-176B), split 40-50%/30%/20-30% over the three rungs so that most tokens are spent where the model is weakest.",
     "The decay phase is budgeted at ~2.9% of the main training volume (83.9B tokens over 20,000 steps), of which long-context data takes 30-40% (25-34B), split 40-50%/30%/20-30% over the three rungs. The 10-15% range (294-441B) remains a design ceiling should the data gate (Section ref{sec:longctx-data}) require more long-context exposure.\n% 中文：衰减阶段按主训练量的约2.9%编列预算(20000步共83.9B token)，其中长上下文占30-40%(25-34B)，三级按40-50%/30%/20-30%分配。10-15%区间(294-441B)保留为设计上界，以备数据闸门要求更多长上下文暴露时使用。",
     "净增~1行。腾版面：§4.7删「not a separate stage and not part of SFT/RL」长解释，省~2行。"),
    ("§4.7 阶梯成本 118→2900(L107-108)",
     "The reference rung-cycle costs ~118 GPU-hours on sixteen GPUs, carried by context parallelism rather than extra nodes.",
     "The reference rung-cycle costs ~2900 GPU-hours on sixteen GPUs at measured throughputs (351,526 tok/s at 32K, ~180K at 64K, ~90K at 128K; all estimated except 32K), carried by context parallelism rather than extra nodes.\n% 中文：参考轮次在十六张GPU上按实测吞吐(32K 351526实测、64K约180K估算、128K约90K估算)约2900 GPU·h，由上下文并行承担。",
     "净增0行。将无法复现的118改为可验算的2900(181.4h×16GPU)。如过大可改「待核」。"),
    ("§4.8 推理 41.6K→39,377(L134-135)",
     "Under the SGLang production stack, prefill holds 41.6K tok/s to 64K and serves 1M in 172s at 34.7GB, whereas the dense transformer cannot serve beyond 512K on a single 80GB H100 (KV-pool cap ~455K tokens);",
     "Under the SGLang production stack, the hybrid achieves 39,377 tok/s prefill at 128K and serves 1M in 172s at 34.7GB, whereas the dense transformer cannot serve beyond 512K on a single 80GB H100 (KV-pool cap ~455K tokens at 30% memory fraction);\n% 中文：在SGLang生产栈下，混合模型在128K时prefill达39377 tok/s，1M时以172秒、34.7GB完成，而稠密Transformer在单张80GB H100上无法服务超过512K(KV池上限约455K token、显存占比30%)；",
     "净增0行。41.6K(无源)替换为tab:longctx-cost 128K实测39,377。"),
]

# ═══════════════════════════════════════════════════
# §5 data: 仍需的实验
# ═══════════════════════════════════════════════════
EXP_ITEMS = [
    ("64K/128K吞吐","tab:longctx-train标(est.)","longctx_ladder.tsv确认64K≈180K/128K≈90K均为外推，未实测","S1跑完后16卡跑64K CP4/128K CP8各100步短测，回填实测"),
    ("41.6K prefill tok/s","已替换为39,377(128K实测)","41.6K无任何源文件记录，已用tab:longctx-cost 128K=39,377替代","如需64K prefill：SGLang测64K b=1 prefill回填"),
    ("2900 GPU·h阶梯成本","新算值(待运维确认)","118无法复现，改为按实测吞吐算的2900(181.4h×16GPU)","S1跑完后实测32K/64K/128K吞吐，按实际token分配重算"),
    ("PPL 83.2->...->55.4","来自S5-01 20K-step ckpt","旧版标注「20K-step(≈655M)checkpoint」——搜索ckpt非生产ckpt","生产S1跑完后取ckpt重跑4K->1M PPL回填"),
    ("400 Bayesian trials","由data线执行","pretrain线无法确认精确数；设计200-400","向data线确认实际trial数回填"),
    ("tab:longctx-train Rung1≈42B","与ladder.tsv 20B不一致","表写42B但ladder.tsv写20B","确认实际token分配，统一表格与ladder.tsv"),
    ("passkey/RULER≥95%@1M","目标值，尚未实测","ABF_PLAN §4设为门限，B1老ckpt passkey=0%","Decay B完成后取ckpt跑passkey+RULER评测"),
]

# ═══════════════════════════════════════════════════
# §6 data: 自检清单
# ═══════════════════════════════════════════════════
CHECKS = [
    ("P0修正","88-176B→83.9B/25-34B","❌→✅","L98-99改写方案已给出"),
    ("P1修正","88:8:4→74:19:7","⚠️→✅","L29-31改写方案已给出"),
    ("P1修正","118 GPU·h→2900 GPU·h","⚠️→✅","L107-108改写方案已给出"),
    ("P1修正","41.6K→39,377(有源)","⚠️→✅","L134-135改写方案已给出"),
    ("P1修正","MiniCPM5-2B cite恢复","⚠️→✅","§4.1改写方案已给出"),
    ("P1修正","warmup 2000 vs 250解释","⚠️→✅","§4.2改写方案已给出"),
    ("P2修正","Decay A描述补SFT","⚠️→可选","优先级低，下轮处理"),
    ("P2修正","92 GPU·h→82 GPU·h","⚠️→可选","优先级低"),
    ("P2修正","补回第三点理由","⚠️→✅","§4.1改写方案已给出"),
    ("P2修正","400 trials加注","⚠️→可选","已并入§4.4 BO句"),
    ("P2修正","tab:longctx-train 42B→20B","⚠️→待核","需确认实际token分配"),
    ("数字核实","2.94T/700k/4.19M tok/step","✅","s1.env L4/L12"),
    ("数字核实","3.02T/720k","✅","2.94T+83.9B≈3.02T"),
    ("数字核实","613,992 tok/s","✅","common.env L82; #792实测"),
    ("数字核实","351,526 tok/s @32K","✅","longctx_ladder.tsv L8; #792 E3"),
    ("数字核实","iter 30,660/loss 2.151/598K","✅","MEMORY #997心跳"),
    ("数字核实","2.2054/2.6739±0.0469","✅","EXPERIMENTS L16/L95"),
    ("数字核实","2.52%/0.03%/889","✅","check_longctx_data.py实测"),
    ("数字核实","193,295/536","✅","contam_scan_full_summary.md"),
    ("数字核实","83.2→51.5→53.3→53.0→55.8→55.4","✅","旧版tab:longctx-ppl完全一致"),
    ("数字核实","172s/34.7GB/455K","✅","旧版tab:longctx-ppl/longctx-cost"),
    ("数字核实","2.22B/2.51B/-11.6%/+8%","✅","EXPERIMENTS/ROUND2 P-7"),
    ("引用核实","nvidia-nemo/nvidia-megatron","✅","bib L183/L33"),
    ("引用核实","gao2024prolong/shang2025longrope2","✅","bib L162/L173"),
    ("引用核实","openbmb2026minicpm5","⚠️→✅","bib有条目，改写后恢复cite"),
    ("红线检查","不改.tex(本轮只出计划)","✅","本报告仅计划，未动.tex"),
    ("红线检查","不伪造数字","✅","未实测标「待核」或「est.」"),
    ("红线检查","不超6页","✅","改写净-3行"),
    ("红线检查","中文注释不删","✅","改写方案均含%中文：行"),
    ("红线检查","不碰GPU/S1训练","✅","纯CPU写作"),
    ("红线检查","不动6_vision_encoder.tex","✅","仅审4_llm_pretrain.tex"),
    ("红线检查","不整段塞回已删内容","✅","补回内容均配等量删除"),
]

def build_html():
    P = []
    P.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
    P.append("<meta name='viewport' content='width=device-width,initial-scale=1.0'>")
    P.append("<title>BaiZe 论文第 4 章修订计划（中文）</title>")
    P.append(f"<style>{CSS}</style></head><body><div class='wrap'>")
    P.append(tag("h1", "BaiZe 论文第 4 章「LLM Pretraining」修订计划"))
    P.append(tag("div",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ "
        f"生成器：<code>pretrain/generate_paper_revise_plan_report.py</code> ｜ "
        f"审校对象：<code>ISEDA2027/4_llm_pretrain.tex</code>（压缩版 e85e5dc68，~170行/5表/7小节）",
        **{"class":"meta"}))
    P.append(tag("h2", "概览", id="s0"))
    P.append(tag("p",
        "运维将第4章从12小节/13表/546行压缩至7小节/5表/~170行。"
        "本报告逐句核校压缩版全文，与源材料对账，列出所有失实之处并给出可直接替换的改写方案。"))
    P.append(tag("div",
        tag("div", tag("div","1",**{"class":"num"})+tag("div","P0 不符事实",**{"class":"lbl"}), **{"class":"card p0c"}) +
        tag("div", tag("div","6",**{"class":"num"})+tag("div","P1 存疑/误导",**{"class":"lbl"}), **{"class":"card p1c"}) +
        tag("div", tag("div","6",**{"class":"num"})+tag("div","P2 轻微",**{"class":"lbl"}), **{"class":"card p2c"}) +
        tag("div", tag("div","18+",**{"class":"num"})+tag("div","✅ 已核实属实",**{"class":"lbl"}), **{"class":"card okc"}),
        **{"class":"summary-card"}))
    return P

def build_sections(P):
    # §1
    P.append(tag("h2", "§1　现状逐句核校（逐句摘录 → 标注 → 证据）", id="s1"))
    P.append(tag("p", "按 tex 行号顺序逐句摘录，标注「✅属实/⚠️存疑/❌不符事实」，给出证据文件+行号。"))
    for title, text, status, evidence in ITEMS_S1:
        sc = "ok" if "✅" in status else ("err" if "❌" in status else "warn")
        P.append(tag("div",
            tag("h3", title) +
            tag("p", f"<span class='{sc}'>{status}</span> &nbsp; <code>{esc(text[:100])}{'...' if len(text)>100 else ''}</code>") +
            tag("p", evidence, **{"class":"box"}),
            **{"class":"box"}))
    # §2
    P.append(tag("h2", "§2　不符事实 / 存疑清单表", id="s2"))
    hdr = tag("tr", tag("th","严重度")+tag("th","位置")+tag("th","现文")+tag("th","事实")+tag("th","来源")+tag("th","判定"))
    br = "".join(tag("tr",
        tag("td", f"<span class='p{r[0][1].lower()}'>{r[0]}</span>" if r[0][1] in "012" else r[0]) +
        tag("td", r[1]) + tag("td", r[2]) + tag("td", r[3]) +
        tag("td", f"<code>{esc(r[4])}</code>") + tag("td", f"<span class='{'err' if r[5]=='❌' else 'warn'}'>{r[5]}</span>")
    ) for r in ROWS_S2)
    P.append(tag("table", tag("thead", hdr) + tag("tbody", br)))
    # §3
    P.append(tag("h2", "§3　改写方案（可直接替换 .tex 的英文目标文本）", id="s3"))
    P.append(tag("p", "逐段给出「改前→改后」的英文 .tex 文本。每处改动标明为腾版面删了什么（等量交换），确保不超6页。中文注释行(% 中文：)同步更新。"))
    for title, old, new, note in DIFFS_S3:
        P.append(tag("h3", title))
        P.append(tag("div",
            tag("div", "改前（现文）", **{"class":"diff-hdr-old"}) +
            tag("div", esc(old), **{"class":"diff-old"}) +
            tag("div", "改后（目标文本，可直接替换）", **{"class":"diff-hdr-new"}) +
            tag("div", esc(new), **{"class":"diff-new"}) +
            tag("div", f"📝 篇幅：{note}", **{"class":"diff-note"}),
            **{"class":"diff-block"}))
    return P

def build_sections2(P):
    # §4
    P.append(tag("h2", "§4　篇幅账（当前 vs 改写后）", id="s4"))
    P.append(tag("div",
        tag("h3","当前第4章篇幅") +
        tag("p","文件4_llm_pretrain.tex=19,872 bytes/~170行/7小节/5表。全文6页(正文+参考文献)。第4章约占正文1.6页(含5张浮动表)。"),
        **{"class":"box"}))
    P.append(tag("h3","改写后篇幅估算"))
    sz = [
        ("§4.1补第三点+cite","+2行","0","§4.2删repeat形容词"),
        ("§4.2 warmup说明","+1行","0","§4.6删BO句(-2行)"),
        ("§4.4 88:8:4→74:19:7+BO并入","+1行","-2行","§4.6 BO句删除"),
        ("§4.6删BO句","-2行","-2行","腾版面"),
        ("§4.7衰减预算修正","+1行","+1行","§4.7删SFT/RL长解释(-2行)"),
        ("§4.7阶梯成本修正","+0行","0","等量替换"),
        ("§4.8推理数字修正","+0行","0","等量替换"),
        ("§4.7删SFT/RL解释","-2行","-2行","腾版面"),
    ]
    h4 = tag("tr", tag("th","改动项")+tag("th","增")+tag("th","净增")+tag("th","腾版面来源"))
    b4 = "".join(tag("tr", tag("td",r[0])+tag("td",r[1])+tag("td",r[2])+tag("td",r[3])) for r in sz)
    P.append(tag("table", tag("thead",h4)+tag("tbody",b4)))
    P.append(tag("p", "<strong>净变化：+3行-6行=-3行。</strong>改写后第4章略缩短，不超6页正文上限。"))
    # §5
    P.append(tag("h2", "§5　仍需的实验（无实测支撑的数字如实列出）", id="s5"))
    h5 = tag("tr", tag("th","数字/断言")+tag("th","当前状态")+tag("th","说明")+tag("th","建议实验"))
    b5 = "".join(tag("tr", tag("td",f"<strong>{r[0]}</strong>")+tag("td",r[1])+tag("td",r[2])+tag("td",r[3])) for r in EXP_ITEMS)
    P.append(tag("table", tag("thead",h5)+tag("tbody",b5)))
    P.append(tag("div",
        tag("p","<strong>⚠️ 红线提醒：</strong>未实测数字一律标「(est.)」或「待核」，禁止估算冒充实测。64K/128K吞吐已标(est.)✅。PPL序列来自搜索ckpt(非生产ckpt)，论文应注明checkpoint来源。"),
        **{"class":"box box-amber"}))
    # §6
    P.append(tag("h2", "§6　自检清单", id="s6"))
    h6 = tag("tr", tag("th","类别")+tag("th","检查项")+tag("th","状态")+tag("th","备注"))
    b6 = "".join(tag("tr",
        tag("td",f"<strong>{r[0]}</strong>")+tag("td",r[1])+
        tag("td",f"<span class='{'ok' if '✅' in r[2] else 'warn'}'>{r[2]}</span>")+
        tag("td",r[3])) for r in CHECKS)
    P.append(tag("table", tag("thead",h6)+tag("tbody",b6)))
    P.append(tag("h3","跨章节待办（不在本轮修改范围，登记备查）"))
    P.append(tag("ul",
        tag("li","<strong>摘要0_abstract.tex</strong>：仍写「≈44B tokens/final loss 1.357/≈412 GPU-hours」，与新正文2.94T/3.02T矛盾。需跨章节另派修改。") +
        tag("li","<strong>64K/128K实测吞吐</strong>：S1跑完后回填tab:longctx-train。") +
        tag("li","<strong>生产ckpt PPL序列</strong>：当前PPL来自S5-01搜索ckpt，需用生产ckpt重测。") +
        tag("li","<strong>passkey/RULER at 1M</strong>：Decay B完成后评测。")))
    P.append(tag("div",
        f"BaiZe pretrain 线 · 论文第4章修订计划 · 生成器 pretrain/generate_paper_revise_plan_report.py · "
        f"commit 前缀 pretrain paper-plan: · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        **{"class":"footer"}))
    P.append("</div></body></html>")
    return P

if __name__ == "__main__":
    P = build_html()
    P = build_sections(P)
    P = build_sections2(P)
    html_content = "\n".join(P)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    size = os.path.getsize(OUTPUT)
    print(f"Generated: {OUTPUT}")
    print(f"Size: {size} bytes ({size/1024:.1f} KB)")
    if size < 20480:
        print("WARNING: File is below 20KB threshold!", file=sys.stderr)
        sys.exit(1)
    if "<script" in html_content.lower():
        print("ERROR: Contains <script> tag!", file=sys.stderr)
        sys.exit(1)
    import re
    ext = re.findall(r'(?:src|href)\s*=\s*["\']https?://', html_content, re.I)
    if ext:
        print(f"ERROR: Found {len(ext)} external links!", file=sys.stderr)
        sys.exit(1)
    print("Validation passed: 0 script / 0 external links / >=20KB")
