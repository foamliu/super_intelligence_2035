# 深读 1794964207896_jx42b — sierraw@hfeg0plg09 (mc=433, physical_verify)

**session**: `/home/sierraw/.cline/data/sessions/1794964207896_jx42b/1794964207896_jx42b.messages.json` (371 msgs)
**扫描 kw**: virtuoso:1334; pex:566; lvs:23; calibre:18; dspf:14; spf:9

## 真实任务（reframe 后的独立意图）

trace 原始 user msg 是"继续改下代码"——延续性指令，本身没有可判分的独立意图。向上回溯整段会话还原出 sierraw 在做的事：用 Calibre PEX 抽 DDR5 top-chip 寄生网表，落到一组 DSPF `.spf` 文件（角点 cbest/typical/cworst × 温度 0/85/125 共 9 份），写一个 Python 工具 `lpe_trend.py` 一次性吃 9 份 `.spf` 做"角点-温度"双维度的 R/C 趋势分析与 QA。具体诉求四条：

1. 给每个元件算**温度系数 TC（1/℃）**——不是和某个固定角点的比值，而是在 typical 角点上对同一元件跨三温度的 (T, R) 点做线性拟合 `R(T) ≈ a + b·T`，得 `TC ≈ b / (a + b·t_ref)`；
2. 跨角点核验 **captab C 不变性**——C 由版图几何决定、不随 PVT 变，所以 9 份快照里同名 cap 的 C 应当一致（容差 1e-9）；
3. **二极管单独分桶**——`*D` 行（`nwdio_p` / `nwdio_n` 子类型）不能混进普通电阻统计；
4. **TC=0 异常件列出**——之前发现 deck 规则漏覆盖导致部分元件 TC=0，要 QA 通道把这类元件挑出来。

## reframe 决策

原始 trace 是延续性"继续改代码"，无独立可判分意图，按 §4 reframe 规则合成 gold：
- 任务：单文件 `lpe_trend.py`，调用接口 `python3 lpe_trend.py --spf-dir <dir> --config <config.json> --out <out_dir>`，输出 `trend_report.json` + `qa_report.json`；
- 可见输入 A：3 角点 × 3 温度（0/85/125）共 9 份合成 `.spf` + `config.json` + `corner_mul.json`；
- 隐藏判分输入 B：3 角点 × 3 温度（**-40/25/105**，与 A 不同）共 9 份合成 `.spf`，元件名 / R / TC / 异常集合都不同（A 异常 {R_metal_2, R_via_1}，B 异常 {R_metal_1, R_via_3, R_well_2}），二极管数 A=3 / B=4，元件总数 A=25 / B=27；
- 14 条独立可 FAIL 断言（a-n），覆盖：脚本存在非 trivial / 在 B 上 exit0 / 双 JSON 可解析 / 顶层键齐全 / total_elements==27 / r_by_corner_temp 9 键 2% 内 / tc_by_element 19 键 10% 内（含 TC=0 异常件≈0）/ 5 桶 count / diode 桶 / 异常集合精确匹配 / captab 一致 / 跨角点单调 / 跨温度单调 / anti-degenerate（防 print-only/全零/空 stub）；
- 4 个负样本各命中不同断言：empty_stub→(a)、print_fixed→(f)、no_diode→(g)、zero_tc→(g)。

## fixture 合成说明

sierraw 真实 artifact `/proj/lacaa/TV1_FS_Virtuoso/workdir/sierraw/lpe_trend/` 从 e0031982 账号 permission-denied，所以 fixture 是**合成的 DSPF-like 文本**（sanitized，不是真实 PEX 输出）。`.spf` 格式自描述：每行以 `*R` / `*D` / `*C` 标注元件类型与参数，头部 `.CORNER` / `.TEMP` / `.TREF` 标记快照角点/温度/参考温度，`*R` 行已按 `R = RREF × MUL × (1 + TC × (T - TREF))` 算好当前 R 值。B fixture 的 R 值随温度单调非降、跨角点 cbest≤typical≤cworst 单调非降，C 值跨 9 角点完全一致——满足判分器对真实物理趋势的期望。

## 落地

- case json: `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/C/EDA-Eval-DesignFlow-DspfRcTrendAnalyze-001.json`
- reference: `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/DspfRcTrendAnalyze-001/`（check.py 自包含 base64 嵌入 B、lpe_trend_ref.py、gen_dspf_fixtures.py、negative/ 4 负样本）
- assets: `EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/DspfRcTrendAnalyze-001/`（A 可见 + hidden/ B 附件）
- C.jsonl 重建已含本 case（563 case）；台账 mark=case；自检 PASS / 4 负样本全 FAIL / 3-seed 确定性 PASS。
