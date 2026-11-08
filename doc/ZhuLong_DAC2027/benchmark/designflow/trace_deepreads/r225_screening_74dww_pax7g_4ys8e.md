# r225 shard C 选料筛选笔记（3 条 trace 全 parked，0 case）

> 轮次：r225（2026-11-08）。本轮为**选料筛选轮**：mc>=30 layout-affinity 顶部 3 条候选经深读全部判 non-seed，parked 入台账。0 case 落库（DEBT:1，下轮必须先补）。

## 选料方法
- 在 .75 上对 `summary.tsv`（扫描源 `ssh_eda_search_20261105_192825`）跑 layout-affinity 打分：
  `score = sum(LAYOUT_TOOLS counts) − 0.6×sum(SIM_TOOLS counts)`，LAYOUT={calibre,virtuoso,aether,dbGet,dbCreate,cellview,innovus,pcell,layout,lvs,drc,pex}，SIM={netlist,hspice,schematic,synthesis,spectre,finesim,primesim,fsdb,verdi,waveview,ncsim}。
  排除 ledger_C 已动过的 364 个 session（写 excl_C.txt → grep -vFf）。
- 顶部得分候选（lay_ratio≥0.7）多被 sim/netlist 主导或 ledger 已排除；真正 lay≥0.9 的候选寥寥。

## 候选 1：1792739133486_74dww（e0047434 @ hfeg0pkn002, mc=91, 109 msgs, 323KB）→ PARKED
- 关键词：virtuoso 278 / calibre 185 / innovus 12 / cellview 4（lay=0.97 sim=0.03）——表面信号极干净。
- 深读：**env-recon / how-to 会话**，非设计任务。
  - UI#0 `pwd` → UI#6 `in this directory, find the autocell document` → UI#12 `what software can be used show gds in this machine` → UI#19 `If use klayout, do I need to source sth?` → UI#57 `please use chinese` → UI#75 `请告诉我，当前机器上，如何运行virtuoso，并打开gds文件` → UI#89 `IC231 这个virtuoso是哪年的版本？` → UI#91 用户粘贴失败日志 `libicui18n.so.50: cannot open shared object file` → UI#108 assistant 结论「Cadence Virtuoso 在这台 RHEL8 登录节点跑不起来，用 Aether/gdspy」。
- 判 non-seed 理由：
  1. 用户意图是 how-to Q&A（"用什么软件看 GDS"/"怎么跑 virtuoso"），gold = prose 推荐建议，非 runnable 脚本 → 违反 §4.2 真跑候选 / §4.3。
  2. UI#91 用户已给出根因（`libicui18n.so.50` 缺失）→ A-档 disqualify（§③ ②「凡用户已指出根因的轮不得用作 A 档」）。
  3. 检测脚本族（check_gds_tools.py / check_klayout_env.py / scan_icu.py …）是 agent 生成的探针，非用户请求的交付物。
  4. 同类已 parked：qk0vo（how to launch innovus）、0i3r5（env-bootstrap pyAether）、unnkw（e02141 devops setup）。
  5. L1-borderline + 与 ToolchainID-001 / LayToolFingerprintAudit-001 / CalibreLabInventory-001 tool-inventory 主题重叠。
- 台账 note：`env-recon/how-to … A-disqualify … same class as parked qk0vo/0i3r5/unnkw`。

## 候选 2：1790145633753_pax7g（miccao @ hfeg0plg37, mc=106, 88 msgs, 760KB）→ PARKED
- 关键词：calibre 710 / netlist 207 / schematic 56 / cellview 8（lay=0.73 sim=0.27）——calibre 信号极强。
- 深读：**AutoCell TCL flow 生成 + calibre VCO aok/aoi mismatch DRC 引擎修复**会话。
  - UI#0（唯一 A-档合格 seed，提出需求纯意图）：「[autocell-tcl-flow-generator] /home/miccao/autocell/ddcpc/cell_constraints_template.txt 这是我的配置文件，运行路径…网表…xord2x2.cdl，生成的 gds 放到…autocell 用 /apps/proplus/autocell.1.2026.8。同时请修复 DRC」。
  - assistant 链：加载 autocell-tcl-flow-generator skill → 读 cell_constraints_template + 旧 decqa flow（run.tcl+7 文件）→ 诊断 DRC 失败根因 = calibre VCO=aok（RHEL8 自动检测）vs calibre tree=aoi 不匹配 → 找 calibre_env VCO 逻辑（aok=RHEL8, aoi=老系统）→ 搭 flow dir 8 个 TCL 文件 + nanov.drc，修 DRC 引擎 + 网表路径 → 跑静态 validator validate_flow.py：1 FAIL（pin22 未定义，循环生成 `pin${i}${j}` 静态不可见）+23 WARN → 修 pin22 → `[PASS] No errors found`。
  - UI#87 用户粘贴 autocell-tcl-flow-generator SKILL 定义全文（重申 skill spec，非新需求）。
- 判 non-seed 理由（重叠双重命中）：
  1. **VCO 修复半**与已有 **VcoChainFixGen-001**（physical_verify, e0014566 q3ks5, mc=190）重叠——该 case 已覆盖 calibre VCO 环境链根因（dbdiff→calibre_env→calibre_vco，VCO=aoi vs aok，USE_CALIBRE_VCO 分支）。
  2. **AutoCell TCL flow 生成半**与 6 个已有 miccao AutoCell case 重叠：AutoCellExtEngineCfg / AutoCellKitMap / AutoCellFlowAudit / AutoCellFlowValidate / AutoCellLossPara / AutoCellClassify。
  3. miccao AutoCell 主题池饱和（7th miccao case 风险）。
- 台账 note：`overlaps VcoChainFixGen-001 (calibre VCO env-chain) + 6 miccao AutoCell cases; pool saturation`。

## 候选 3：1789634880745_4ys8e（ellawu @ hfeg0pkn005, mc=178, 158 msgs, 1.47MB）→ PARKED
- 关键词：calibre 452 / schematic 35 / virtuoso 8 / pyAether 8 / dbGet 5（lay=0.92 sim=0.07）——calibre 主导。
- 深读：**prose 文档生成**会话，非脚本任务。
  - UI#0 `DFM SPEC FILL` + 附件 calbr_drv_ref.pdf（3.4MB Calibre DRC reference PDF）。
  - assistant 全程把 26KB markdown 文档 `DFM_Spec_Fill.md`（DFM 规范说明）分块通过 editor 工具写入 `/home/ellawu/`，反复与 editor insert_line 限制 / 重复内容 / 文本不匹配搏斗（msg 39–94 全是 editor 报错），最终未产出任何 runnable 脚本。
  - 「DFM SPEC FILL」= 写 DFM 规范文档，gold = prose markdown spec。
- 判 non-seed 理由：
  1. gold = 26KB prose markdown 文档 → 强制 substring/结构判分 → 违反 §4.2 真跑候选 / §4.3「🚫 仅子串出现式断言」。
  2. UI#0 `DFM SPEC FILL` 是标签式极简意图，非合格 A-档 需求语句。
  3. 同类已 parked：iacrk（解析 calibreDummy.rule BWZ dummy 逻辑=prose 解释非 script）、kkjsm（解析 CT_F rule 24 轮 prose Q&A）。
  4. ellawu 已有 4 个 physical_verify case（ViaFillSvrfGen / ImplantFillDeckGen / SVRFDepAudit / FillImplantFlowAudit）都是 **SVRF deck GENERATION**（runnable），与本 4ys8e 的 spec-doc 写作主题正交且不可判分。
- 台账 note：`prose-doc: DFM_Spec_Fill.md 26KB markdown, non-runnable, violates 4.2/4.3; same class as parked iacrk/kkjsm`。

## 结论与下一步
- mc>=30 layout-affinity 顶部 3 条全部 non-seed（env-recon / 重叠 / prose-doc）。pool 在该层饱和。
- **下轮（r226）第一件事**：补 r225 的 DEBT:1（交付 1 条 case）。建议：
  1. 降 mc 阈值到 15（参考 shard A 11/06 已放宽），扫下一层；或
  2. 用 layout-affinity 打分取 lay_ratio≥0.9 但 mc 在 30–60 区间的候选（如 mwxi NEW user calibre 405 系列 6bs3u/7vfvg/i96df，mc~60，纯 calibre，待深读是否真 DRC deck 任务）；或
  3. 触发新一轮 .75 rescan（当前扫描源 11/05，已 +984 sessions）刷新候选池。
- 优先 pg_layout 域（34，最低覆盖），但避开 alan3zh test_chip_v1 APR 项目（已有 4 case）。
