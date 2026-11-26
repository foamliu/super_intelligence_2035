# deepread: h033j — HighSigma 文档学习 → HTML 摘要生成

- **session**: 1794998877326_h033j
- **user**: e0047547 @ hfeg0pkn003 (e0047547 已有 1 case 在 B.jsonl, 非 NEW-user)
- **mc**: 62 (spectre:351; netlist:87; cadence:36; pdk:28; mosfet:8; aether:6)
- **trace**: 139 msgs / 72 user / 67 assistant, messages.json 926KB (目录式存储 `h033j/h033j.messages.json`)
- **scan**: ssh_eda_search_20261119_172105, r898 fresh list 剩余 25 条 mc≥10 之一
- **claimed**: r904 (2026-11-20), ledger_B status=claim

## 用户真实意图（trace 原话）
1. U0: 「/home/e0047547/HighSigma/NanoSpice_HighSigma_Analysis_Application_Note.pdf 学习这篇文档，说明 highsigma 是要做什么事情，怎么做，需要什么输入信息，输出什么结果」
2. U33–U48: 一连串追问 — 直方图横纵坐标、"使能工艺库统计部分"数据格式、6σ 良率↔直方图、均值判据、spec 单边/双边阈值统计处理、.lib 模型随机变化是否正态、dist=gauss 语义、Pelgrom 定律、模型随机变量来源/范围
3. U49: 「/home/e0047547/HighSigma/spectreuser.pdf 学习此文档，提取 Monte carlo 和 HighSigma 相关内容，并依据此内容重新校准之前问答的结论」
4. U61: 「从 Monte carlo 的 3sigma 数据是否能推到 6sigma，如何推，可靠性如何」

## 交付物（assistant 最终产出）
- `/home/e0047547/HighSigma/highsigma_summary.html` (~22KB, 12 章节, 自包含可浏览器打开)
- 结构：①HighSigma 是做什么(重要性采样/两阶段/两种分析类型) ②输入输出(.highsigma 语法/输出文件表) ③直方图与 sigma 对应(坐标/6σ↔失效率对照表/"整体太差"判据) ④统计分布(dist=gauss/...) ⑤Pelgrom 定律 ⑥Monte Carlo 3σ→6σ 外推 ... 共 12 节
- 过程产物: verify_html.py (HTML 标签配平校验), cleanup2.sh (清理脚本) — 最终均已删

## 拟造 case 形态（portability-reframe: doc-Q&A → produce-HTML-summary 生成器）
- **case_id 候选**: EDA-Eval-DesignFlow-HighSigmaDocSummaryGen-001
- **domain**: spice_sim (spectre/HighSigma Monte Carlo 统计分析)
- **layer**: L1 (离线 Python/HTML 静态产出, 无需真跑 spectre)
- **asset A (format-faithful)**: 两份 PDF 的关键章节文本提取(或简化重写版) + 用户追问清单(原话)
- **hidden B**: 结构性反转 — 不同 PDF 章节片段 + 不同追问子集(如改成 hspice Solido Monte Carlo / 改成问 3σ→9σ 外推 / 改成问 .lib dist=uniform), 答案要点与 A 不同, 防背题
- **reference 解**: 参数化 HTML 摘要生成器 `highsigma_summary_gen.py`, 输入(PDF 文本片段 + 问题清单) → 输出自包含 HTML(章节/表格/对照表)
- **check.py ≥8 条断言候选**:
  ① zip 内文件齐全 ② HTML 自包含(无外链/CDN) ③ 章节数 ≥10 且 `<section>` 标签配平 ④ 含"重要性采样"/"importance sampling" ⑤ 含 `.highsigma` 语法说明 ⑥ 含 6σ↔失效率对照表(ppm 数量级正确) ⑦ 含 dist=gauss 语义说明 ⑧ 含 Pelgrom 定律 ⑨ 含 Monte Carlo 3σ→6σ 外推方法 + 可靠性说明 ⑩ hidden B 重跑: 章节内容随 B 输入变化(防 hardcoded A 答案) ⑪ cross-input guard: B 的不同问题子集 → 不同章节标题 ⑫ 退化提交(空壳/只打印期望/删核心)全 FAIL
- **k 预估**: 12–14 (a–l/n)
- **negative**: 4–5 个(空壳/只打印期望串/删 Pelgrom 段/删对照表/hardcode A 答案→在 B 上 FAIL)
- **与既有 case 区分**: e0047547 既有 1 case 需查重(不同 session/不同意图即不冲突); shanliny 的 WmMt0Diag(97z71) 测 .mt0 诊断, 本题测文档学习→结构化摘要生成, 形态不同
- **风险**: PDF 大文件提取需简化; 需确认 e0047547 既有 case 不是同意图(若同意图则 park)

## 状态
- **DEBT: 1 deepread 已完成, 合成未做** — r904 时间预算耗尽(候选发现+trace 获取+deepread 占满 40min), 合成留 r905
- 下轮第一件事: 据本笔记合成 case (assets/hidden/reference/check.py/negative) + 自验 + 追加 B.jsonl
