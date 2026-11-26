# r825 深读笔记 — ec2jo (chengk@hfeg0pkn002) → PtuGuiRecomputeProduce-001

## 候选
- session: `1795068626907_ec2jo` (chengk @ hfeg0pkn002 / 10.129.2.11, mc58)
- trace ALIVE @ **subdir-path** `/home/chengk/.cline/data/sessions/1795068626907_ec2jo/1795068626907_ec2jo.messages.json`
  (417KB, 64 msgs, agent=lead) — flat-path 已 NOFILE，path-bug revival 第五例
  (r821 4i1w4 / r822 yseg9 / r823 sr0ca / r824 q1589 / r825 ec2jo)
- keywords: pyaether:213;rtl:135;aether:85;cellview:40;virtuoso:23

## 域归属判定（关键）
- rtl:135 是 keyword 命中，但**深读 64 msgs 后用户真实意图是 pyAether GUI 脚本完善**
  (IDD/PTU 功耗计算工具的表格交互改造)，**不是 digital RTL 设计/验证**。
- pyAether 脚本自动化 = **eda_other** 域（A shard 负责域之一）。
- 不强造 digital，按任务初衷第 1 条判为 eda_other。

## 用户意图（UT#0，单轮 produce-task，原话）
> 需要你完善 /home/chengk/work/ZL_work/IDD_PTU/cxmt_IDD_PTUCalculation.py 这个 pyaether 的代码，
> 读取 config，仔细理解代码的整体逻辑，需要作出以下功能的完善：将 gui 界面表格中 IDD(mA) 一列
> 的属性进行完善……对于 IDD(mA) 这一列每个单元格可以点击并且输入，然后自动计算出 PTU_gain，
> 此外需要完善的内容是将 gui 界面表格最后一行 Total，可以自动计算 IDD(mA) 一列已有数据的综合
> 以及 PT 的总和，代完善的代码要求最小化修改

两点完善：
1. IDD(mA) 列每个数据行单元格可原地编辑 → 编辑后**自动**算 PTU_gain(W)/PTU_gain(100%)，
   替代旧的「选中行→底部 IDD 输入框→Calculate 按钮」流程。
2. Total 行自动汇总 IDD(mA)(col3) + PTU_gain(W)(col4) + ratio(col5) 三列总和
   （旧版只汇总 col4/col5，**不汇总 col3**——Feature 2 是新需求）。

## trace assistant ground-truth（lead, msg62 交付）
- 用 brainstorming/eda_agent skill + RAG search_apis 查 Aether report-field API
- 关键结论：Aether `hiCreateReportField` **不支持单元格原地编辑**，唯一钩子是 hiClickedCallback
- 选**方案 C**：用 PyQt5 `QTableWidget` + `ae.aePyQtToQWidget()` 包装替换 report field，
  `itemChanged` 信号触发自动重算
- 新增纯逻辑函数：`_cxmt_is_number` / `_cxmt_fmt` / `_cxmt_ptu_build_table` /
  `_cxmt_ptu_recompute` / `_cxmt_ptu_on_item_changed` + 模块级 `_cxmt_ptu_state`
- 公式（沿用原代码）：`PTU_gain = (PTU_Index * IDD * die_stack * Channel)/1000`，
  `ratio = PTU_gain/PTU_target*100`
- 验证：py_compile + 桩模块隔离（stub pyAether/PyQt5）import 后跑重算逻辑，
  真实 config（die_stack=16/Channel=4/PTU_target=7.04）Total IDD=17.5/PTU=12.8784 与手工一致

## 资产获取（.75 eda_flow session r825）
- 原 file `cxmt_IDD_PTUCalculation.py`（增强前）= **从 trace 的 4 个 editor old_text 反向重建**
  （trace 中 assistant 用 editor 工具做了 4 处编辑：imports / report_GUI / callbacks / _fmt；
   现盘上文件是 user 后续再改版，含 _cxmt_make_item 等额外改动，故不能直接当 original）
  → 反向应用 4 个 old_text 重建出 13228B/291 行/8 def 的原始文件，py_compile 通过
  → 含 `hiCreateReportField` + 旧 ReportFieldCB/IDDfillIn_CB，无 QTableWidget/_cxmt_ptu_recompute
- config A `IDD_PTUconfigFile`：die_stack=16/Channel=4/PTU_target=7.04，22 数据行（含负 PTU_Index）

## case 合成（B档 synthesized produce-task, §5 reframe）
- **reframe 理由**：GUI 部分（QTableWidget 嵌 hiCreateAppForm）只能在真实 Aether 跑、
  无头沙盒测不了；可 headlessly 测的核心是**重算逻辑**（公式 + Total 三列汇总）。
  把它固化为模块级 `recompute(table)` + `_ptu_cfg` 接口（trace assistant 自己也是用桩模块
  隔离测的这个接口，故 reframe 忠实于 trace 验证方式）。
- case_id: `PtuGuiRecomputeProduce-001`，domain=eda_other，mode=design_flow
- 可见 A：原始 cxmt_IDD_PTUCalculation.py + IDD_PTUconfigFile + task_brief.md + prompt.txt
- 隐藏 B：IDD_PTUconfigFile_B（die_stack=8/Channel=2/PTU_target=5.20，10 不同数据行 IDDP1-10，
  与 A 完全不同值/名/数量，反硬编）
- reference：cxmt_IDD_PTUCalculation_ref.py（干净增强版，暴露 _ptu_cfg + recompute + GUI 函数）
- check.py：stub pyAether/PyQt5 → import 候选 → 喂 B 到 _ptu_cfg → 建 stub 6 列 table →
  调 recompute → 22 条独立断言（逐行 PTU_gain/ratio、Total 三列汇总、非数字拒识、空跳过、
  全空=0、幂等、3 随机子集 anti-hardcode、PTU_target=0 不除零）
- 3 negatives：neg1_empty_stub / neg2_print_only / neg3_coredel（删 die_stack+Total IDD）
  全 FAIL（§4.9 退化提交回归 (a)(b)(c) 全 FAIL）

## 自验
- ref PASS check 22/22
- 3 negatives 全 FAIL（命中不同断言组：①empty→Total 不写 ②print→cell 空 ③coredel→公式错+Total IDD 缺）
- k_check == k_rationale == 22（≥8 硬闸门过）
- 3 seed 随机子集 anti-hardcode 全过
- A.jsonl 413→414. ledger mark ec2jo→case.
- eda_flow session r825 closed.

## 与既有 case 关系
- 与 r818 NoConnPurposeExplainQA-001 / r817 DdjocCircuitPlanReconQA-001（analysis-Q&A）不同范式
  （本条是 produce-task）；与 r819 RowredB64RestoreProduce-001 同为 B档 produce-task 但不同域
  （eda_other vs digital）不同主题（GUI 重算 vs base64 还原），非碰撞。
- 同 user chengk 无既有 case（本 shard 首条 chengk）。
