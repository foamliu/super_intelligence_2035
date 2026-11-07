# Trace deepread: 5hbdw — SA offset-cancel nsa vs n_driver 晶体管区分

- **session**: `1792205134941_5hbdw.messages.json` (539 msgs, 1.81MB)
- **user/host**: hengbow / hfeg0pgn045 (mc=144)
- **ledger**: shard A r148 parked note「analog/netlist session, unfit shard-A L2」→ D 跨 shard 共享第七例（同 hengbow 用户已有 u78sz=WvSigListGen-001，本 trace 不同意图/domain）
- **domain**: schematic_netlist（D shard 主域）
- **真实意图**: DRAM SA (sense amplifier) offset-cancel (OC) 阶段 VCOM 偏低诊断 + nsa vs n_driver 敏感性分析
- **session 路径**: `/home/hengbow/.cline/data/sessions/1792205134941_5hbdw/1792205134941_5hbdw.messages.json`（目录式存储）

## 用户意图轮（clean produce / A-faithful 候选）

- **U#0**：「我在设计一个SA，现在主要关注ofset cancel阶段...oc在结束的时候，bl和blb的电压vcom偏低，导致SM d0<d1,可能的原因有那些，我应该从哪些方面入手」= Q&A 诊断（不是 produce，A-faithful rule2 边界：问「可能原因」算 clean need 但无单一可验交付物）
- **U#5**：`@/rundata/drvqa/.../12_vcom_coupling/` 指仿真环境（附件私有不可移植）
- **U#35**：「你可以帮我跑吗」= 委托真跑 FineSim（live LSF bsub，不可移植）
- **U#230**：「tsdt是charge sharing阶段...我要看的是oc结束时的vcom，也就是sec0uwler<0>开启时对应的vcom电压」= 修正测量点（诊断指导）
- **U#266** ★：「下拉有两种关键的管子，一个是SA的n管nsa；另一个是nsa sourse的驱动管n driver，可以具体分析一下网表看看是那个管子，然后看看这两个哪个的影响更大」= **clean produce**（分析网表区分两类管子）→ assistant 解析 LYX_schematic.netlist 抽 nsa/n_driver
- **U#341**：「单独弱化oc阶段的n driver会不会影响oc的效果，从而对SM有影响」= Q&A
- **U#343**：「先跑那组失配版 pvnoc 对比，mismatch参数可以参考脚本gen_sp.py添加」= 委托真跑（live sim）
- **U#486**：`@/rundata/.../sm_256_collect_aryrouting_sec0_A1.py参考这个脚本收集SM数据` = 引用真实脚本（附件私有）
- **U#497**：「根据现有的结果生成workspace报告」= 报告生成（依赖前面真跑结果，premise-missing）

## assistant 工具链（关键 produce）

1. **ASST #18-#34**：editor 写受控 Python 脚本从 `CXSAx16_x3.spf_RCC_addmis_V2B_vtshift` 提取 SA 核心对管、OC 信号；读 mt0 量化 d0/d1
2. **ASST #271-#283** ★：定位真实器件在原理图网表 `LYX..._schematic.netlist_V2B_vtshift`，提取子电路 `CXSA_1x16_CBCC_schematic_drvqa_cmos_core`：
   - **nsa 交叉对管**：模型 `ntnlvio_sa`，源端接 `NCS_e`/`NCS_o`（SA 公共源节点），漏极位线、栅交叉互连。例如 `XMMN36 SaBla<4> Blb<4> NCS_e`
   - **n_driver**：SanEn 门控的尾驱动管
   - iso 隔离管、csl 列选管也在同一子电路里
3. **ASST #285-#340**：sed 改 nsa 宽度（被模型 binning 拒）→ 改用 `dvt_NSA` Vt 旋钮 + `pvnoc` 栅压旋钮；提交 LSF bsub 跑敏感性 case，得 OC 结束 VCOM 变化
4. **ASST #409-#494**：二分法 SM（`sweep OPTIMIZE=v_opt RESULTS=MaxVBL GOAL=0.8 METHOD=BISECTION Itropt=12`），修 KCTB↔列25 映射，跑 pvnoc 基线 vs 0.7 对照
5. **ASST #498-#516**：editor 生成 REPORT.md + REPORT.html（workspace 报告）

## 合成判定

- **A-faithful 不可行**：(1) U#0 是 Q&A 诊断无单一可验交付物；(2) U#266 clean produce 但真实网表 `LYX_schematic.netlist_V2B_vtshift` 在 `/rundata/drvqa/...` 私有不可附加 + 1.3M 行；(3) 真跑 FineSim/LSF 不可移植；(4) U#497 报告生成依赖前面真跑结果 premise-missing → **B 档 synthesized**
- **facet**：取 U#266「网表里区分 nsa vs n_driver 两类管子」的离线可验子任务——SPICE subckt MOS 实例抽取 + 按模型名子串五类分类（nsa/n_driver/iso/csl/other）+ 统计 + 报告。生成器 `gen_sa_transistor_report.py --netlist <sp> --outdir <dir>` → `transistors.json` + `report.md`
- **L-grade**：L1（离线静态 SPICE 文本解析，无需 live EDA 工具）
- **真跑候选**：check.py 用 subprocess 在 hidden B/B2 上真跑生成器，校验结构化输出（不验 SPICE sim 结果）

## check.py 16 条件 a-p

a: zip 无泄漏 + 候选 .py 存在 | b: py_compile | c: B-run exit0 + 2 文件 | d: 顶层键 | e: instances 结构 + type 合法 | f: summary 五类计数 | g: nsa 名集合 | h: n_driver 名集合 | i: iso+csl+other 名集合 | j: models dict | k: subckt 名 | l: report.md 含 subckt+三标题 | m: report.md 提及每实例名 | n: 跨输入 A nsa 名==期望且≠B | o: 跨输入 B2 nsa 名==期望且 iso/csl/other 全 0 且≠B | p: 反硬编码（无 A 字面量）+ 确定性 3x sha256

## 反硬编码五轴

1. subckt 名：CXSA_1x16_CBCC_schematic_drvqa_cmos_core / SA_2x8_CBCC_core / SA_core_simple（全不同）
2. nsa 模型名：ntnlvio_sa / ntn_sa_v2 / sa_npair
3. nsa 源节点：NCS_e/NCS_o 分裂 / NCS_single / NCS
4. 类别组合：A 全五类 / B 全五类但计数不同 / B2 仅 nsa+n_driver（无 iso/csl/other）
5. 实例数：A=18 / B=9 / B2=3（硬编 A 计数者 B/B2 上 f FAIL）

## 自验

- ref PASS 16/16 a-p
- 5 negatives 全 FAIL：empty_shell→c / hardcode_a→f / print_expected→c / ref_core_deleted→f / naive_stub→f
- §4.9 三假 FAIL：empty→c / print_expected→c / ref_core_deleted→f
- 断言闸门 k_rationale=k_check=16 ✓
