# 3io69 deepread — VWLN DFT 知识库检索 Q&A (r782, 2026-11-19)

## trace 溯源
- session: `1792069835790_3io69` (e0014566 @ hfhds201=10.129.32.75, also pkn002/plg58/plg106/plg49/plg08)
- mc=7, keywords verilog:124;cmos:23 (但实际内容是 DFT/测试 — verification 域)
- agent: lead; 19 msgs; 285KB messages.json; ALIVE on hfhds201 (.75 本机, 直接读)
- trace_source: 真实 cline 会话, e0014566 用 cimi-kb-search skill 检索内部知识库

## 用户真实意图 (单轮)
msg[0] (skill 触发) → msg[2] command-args: **「测试VWLN,使用什么DFT」**
- 用户想知道: 测试 VWLN (字线 WL 低电压/电压相关测试) 用什么 DFT (Design for Test) 信号/模式
- 任务形态 = doc-search / retrieval-Q&A (11-15 reaudit 明确恢复为可造)

## agent 工具链
9 次 `run_approved_command` 调 `kb-search-cli.py retrieve` (cimi-kb-search skill):
- q0="测试VWLN,使用什么DFT" (count 58)
- q1="VWLN word line low 测试信号" (1)
- q2="VWLN word line voltage DFT CM" (0, 空)
- q3="WL short 测试 DFT 信号 cm0_ts" (19)
- q4="VWL 字线电压 测试模式 CM 信号 WL电压" (22)
- q5="floatWL Phase driver WL 降低有效电压 写1 fail" (10)
- q6="cm0_ro cm WL 字线 测试信号 WL 激活 precharge VWL" (50)
- q7="VWLN 字线电压 WL 相邻 short 用法1 用法2 float WL DFT 信号" (2)
- q8="Vwl VWLN 测试 模式 信号 tm 字线 WL voltage DFT name" (14)
来源文档: `【G3】LP4_CM_Manual_DBPMA_RevF.docx` (datasetId c82ec72a92a611f082b5f2d30f4e402e)

## agent 最终答案 (msg[18]) — ground-truth 候选
VWLN 测试对应的 DFT 信号 (CM 组合, 非单一信号):
1. **floatWL** — 后开多 WL (共享 Phase driver) 降低 WL 有效电压; 用法1=写"1"能力/写裕量(VWL 低压写)评估; 用法2=WL 相邻 short 检测; 配套 Vwln level / Vss level vth of ptk_sv 波形
2. **cm0_ro_MultiRow<1:0>** — 快速打开多 bank WLs; 模式 `11`(AllMulti) 打开大数量 WLs; 配合 cm0_ts_CompActAsRef / cm0_ts_CompWrMultiBnk 压缩模式省时
3. **cm0_ro_AsyncWlOff<1:0>** — 异步 WL off 时序, tWR/tRAS 测量校准
4. **cm0_ro_AsyncCtrlRow<4:0>** — AsyncWL/AsyncEq 异步阵列控制 (WL/Eq/SA/NC/Iso)
5. **cm0_ts_RedTest<1:0>** — Redundancy/pretest RWL 测试, 区分 normal WL 与 pretest RWLs

## 拟造任务形态 (S5 第二范式: analysis-Q&A + specificity oracle, 沿 r776/r778)
- **A 资产** (SUT 可见): `kb_results_A.json` — 9 次 retrieve 的 KB chunk (curated top-8/similarity, 97KB; 已含 ground-truth 信号 floatWL×3, cm0_ro_MultiRow×3, cm0_ts_RedTest×6, Phase driver×3, Vwln level×30, ptk_sv×24, LP4_CM_Manual_DBPMA_RevF×6). 注意: curated 后 cm0_ro_AsyncWlOff / AsyncCtrlRow / AllMulti 被裁掉 → check() 不要求这几个, 只要求核心 floatWL + cm0_ro_MultiRow + cm0_ts_RedTest + 源文档 + 语义
- **deliverable**: 中文 markdown `vwln_dft_report.md` — 基于 A 检索结果说明 VWLN 测试用什么 DFT 信号
- **B 隐藏** (specificity oracle): `kb_results_B.json` — 重命名信号 (floatWL→floatWLB, cm0_ro_MultiRow→cm0_ro_MultiRowB, cm0_ts_RedTest→cm0_ts_RedTestB, ptk_sv→ptk_svB, AllMulti→AllMultiB, LP4_CM_Manual_DBPMA_RevF→..._B, Vwln level→VwlnLevelB, Phase driver→PhaseDriverB) + question 加 [B-variant]; B-only token 不出现在 SUT 关于 A 的报告 (防背题/防抄 B); 已验 B-only 在 A 出现 0 次
- **check.py 拟 10 条独立断言**:
  ① 报告非空 .md (≥200 字) 含 "VWLN"
  ② 含 floatWL 且附近有 (写|short|电压|fail|裕量) 之一 — VWLN 语义
  ③ 含 cm0_ro_MultiRow (多 WL 打开)
  ④ 含 cm0_ts_RedTest (redundancy/pretest RWL)
  ⑤ 引用源文档 (LP4_CM_Manual_DBPMA 或 RevF 或 【G3】)
  ⑥ 解释 VWLN 测试目的 (WL 电压降低 / 写裕量 / WL 相邻 short) — 语义断言
  ⑦ 反造假: 报告中所有 cm0_* 形 token 必出现在 A blob (禁止编造信号名)
  ⑧ specificity oracle: 报告不含任一 B-only token (floatWLB / cm0_ro_MultiRowB / cm0_ts_RedTestB / ptk_svB / AllMultiB / VwlnLevelB / PhaseDriverB / LP4_CM_Manual_DBPMA_RevF_B / LP4_CM_Manual_DBPMA_B)
  ⑨ 随机化: 3 seeds 对 A chunk 子集抽样, 核心信号 (floatWL + cm0_ro_MultiRow) 一致要求
  ⑩ 报告含 Vwln level 或 ptk_sv 波形电平标记 (chunk 中 30/24 次, 是 VWLN 测试判据)
- **reference 解**: agent msg[18] 原文 (中文 markdown, 已含全部 ground-truth, 需微调去掉对 B 不存在的 AsyncWlOff/AsyncCtrlRow 段以匹配 curated A — 或保留, 因 §⑦反造假只查 cm0_* token, AsyncWlOff 在 curated A 缺席会触发 §⑦ FAIL → ref 解必须只写 curated A 里有的信号)
- **5 negatives**: neg1=空壳/noop; neg2=只 print 期望串 "floatWL cm0_ro_MultiRow"; neg3=core-deleted (只写源文档名不写信号); neg4=抄 B (用 B-only token) → 触发 §⑧; neg5=造假信号 cm0_ro_FakeSignal → 触发 §⑦
- **§4.9 a/b/c**: 空壳→①, print-expected→② (缺语义邻近词), core-deleted→③④ → 全 FAIL
- **domain**: verification (DFT = Design for Test)
- **CID**: `EDA-Eval-DesignFlow-VwlnDftSignalExplain-001`

## ⚠️ 关键注意 (next round 合成时)
1. **curated A 裁掉了 AsyncWlOff/AsyncCtrlRow/AllMulti** — ref 解 & check() 都不要要求这几个; 否则 ref 解会 §⑦反造假 FAIL (写 A 里没有的信号). 若想保留, 改用 full A (218KB, kb_results_A.json on .75 workdir root, 含全部信号) — full A 里 AsyncWlOff×8, AsyncCtrlRow×5, AllMulti×1 都在. 建议用 full A 更忠实于 trace, ref 解直接用 msg[18] 原文.
2. **A/B JSON 已存 .75 workdir** `_r782_3io69_assets/` (workdir keep=True, 下轮 open_session 同 task_id/eval_id 复用): kb_results_A.json (curated 97KB) / kb_results_B.json (97KB) / 3io69_extract.txt / 3io69_full.txt / omdil_extract.txt. workdir root 还有 full kb_results_A.json (218KB) + kb_results_A_curated.json.
3. **本地转移**: .75↔local 无共享 fs; 下轮用 .75 workdir 的文件, 经 return_files 取回写本地 assets dir (内容不经 agent context, 用 transfer.py 模式 urllib POST 18891/mcp). 或直接 read_file 取 content 再 write 本地 (97KB 可过, 218KB 偏重).
4. **ledger**: 3io69 已 claim (e0014566/hfhds201, mc7, digital→应改 verification); omdil 已 parked (unmakable A-pure).

## omdil (r782 first pick, parked) — 教训
- 1793604555578_omdil (e0046913 @ pkn004, mc6, netlist/rtl/icc2/primetime — 看似 pnr_signoff A-pure)
- 3 turns: T0=解释 SYN setup TCL (A-pure digital), T8/T29=.vimrc env-config (非 A-pure)
- **T0 read_files 结果被 lead agent 剥光** (msg[4]/[6] TRES len 2/0) — c8v5k 同款 trace-format-incompatibility
- 真实 TCL 路径 /proj/lacaa/TV1_digital/simdir/yutingq/SYN/setup/ — **Permission denied** (e0046913 读不了 yutingq 的文件), 无法重建 A 资产
- /home/e0046913/.vimrc 可读 (100 行, 但已是 agent 修复后版本, 含 `function! s:OpenNERDTreeIfEmpty(timer)`)
- 结论: omdil EDA turn 不可造 (asset 剥光+perm denied), env-config turn 非 A-pure → parked. r778 flag「fet7_i 等 A-pure」存疑 (fet7i=cellview C 域, 亦非 A-pure)
