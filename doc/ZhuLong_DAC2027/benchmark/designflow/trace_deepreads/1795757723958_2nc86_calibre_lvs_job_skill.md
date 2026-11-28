# 深读笔记 — 1795757723958_2nc86 (felixw@hfeg0pin004, mc214, physical_verify)

> **状态**：✅ full deepread 完成（r1532，取 messages.json 解析 152 msgs assistant 工具链 + 真实交付件 SKILL.md 550 行）→ 已合成 case `EDA-Eval-DesignFlow-CalibreLvsRunsetBuilder-001` 落盘 + 自验全绿。

## 0. Trace 身份
- session_file: `1795757723958_2nc86.messages.json`（152 msgs, 656KB）
- user/host: felixw / hfeg0pin004（与 r1530 gohxq 同用户同 host，但意图不同：gohxq=DRC runset blank diag, 2nc86=Calibre LVS job runner + skill 集成）
- mc=214, keywords: `lvs:2194;drc:1224;calibre:751;.gds:105;.cdl:78;aether:69;schematic:56;waveview:18`
- domain: physical_verify（LVS 主导，calibre/drc/.cdl/.gds 强）
- ledger: r1531 claim → status=claimed, 待 mark case

## 1. 用户真实意图（逐条 user_input）
1. **U0/U1/U5（主任务）**：用 **Calibre 跑一个 LVS job**。运行路径 `/proj/drgqx/V0/agentdir/felixw/LVS_test`（用户提供，不存在则创建）；GDS `.../LVS_test/and2DSx2.gds`；CDL `.../LVS_test/and2DSx2.cdl`；还需要 `lvsRunset`。两种模式：①给 lib cell view 让 skill 抽 gds+cdl 再跑 LVS；②给已抽好的 gds+cdl 跑 LVS。**必须丢 LSF 上跑，不要本地运行**（会影响其他用户）。
2. **U80**：continuous-learning 触发——维护 workspace 知识体系（session 产生新积累时判断固化到哪类 skill/记忆）。
3. **U123（收口指令）**：把 `update_lvs_runset.py` 整合进 `/home/felixw/.cline/skills/lvs_test/SKILL.md`，**不要写死为本次案例**，用传参方式，方便后续用其他 case 测试。

## 2. 真实产物线索（待 full deepread 确认）
- 真实输入文件（pin004 上）：
  - `/proj/drgqx/V0/agentdir/felixw/LVS_test/and2DSx2.gds`（真实 GDS）
  - `/proj/drgqx/V0/agentdir/felixw/LVS_test/and2DSx2.cdl`（真实 CDL netlist）
  - `lvsRunset`（Calibre LVS rule deck，待定位具体路径）
  - `/home/felixw/.cline/skills/lvs_test/SKILL.md`（skill 文件）
  - `update_lvs_runset.py`（assistant 产出的 runset 更新器，待取源码）
- 后半段提到 **Argus 跑 LVS**（工具不同，整体差不多）——次主线，可酌情取舍。
- LSF 提交（`bsub -I -q pv -n <核数>`，默认核数 12，见 eniu7 同类；felixw 此处待确认）。

## 3. 合成计划（下轮 r1532 执行）
- **任务形态**：flow-driving + skill-authoring 合法真实意图（用户在跑 LVS job 并把流程固化成参数化 skill）。
- **deliverable 候选**：`outputs/submit.zip` 含
  1. `update_lvs_runset.py`——参数化 LVS runset 更新器（接收 gds/cdl/runset/run路径/核数 等参数，生成可跑的 LVS runset + LSF 提交脚本）；
  2. `run_lvs_lsf.sh`（或 .py）——LSF 提交封装（`bsub -I -q pv -n <N>`，非本地跑）；
  3. （可选）`SKILL.md` 片段——参数化 skill 说明。
- **LIVE 三分类（preliminary）**：
  - 倾向 **LIVE-NA**：deliverable = 脚本/skill 配置 + runset 文本改写，check 用独立 oracle 比对 runset 关键字段（LAYOUT PATH/PRIMARY/SYSTEM、SOURCE PATH/PRIMARY、LAYOUT LC .* vs SOURCE LC .*、PEX/LVS 开关、LSF bsub 行结构、参数化占位符非写死）。
  - **但**若 check 实质依赖真实 Calibre LVS 产物（LVS 结果 db / summary report CORRECT vs INCORRECT），则升 **LIVE-REQ**（.75 calibre 可达，r1530 已确认 calibre 在 PATH）。下轮 full deepread 后定。
- **判分有牙设计草案**（≥8 独立断言）：
  1. zip 合法 + ≥2 文件齐全；
  2. update_lvs_runset.py 接受 CLI 参数（gds/cdl/runset/outdir/cores），非硬编码 and2DSx2；
  3. 生成的 runset 含 `LAYOUT PATH "<gds>"` `LAYOUT PRIMARY "<cell>"` `LAYOUT SYSTEM GDSII`；
  4. 含 `SOURCE PATH "<cdl>"` `SOURCE PRIMARY "<cell>"` `SOURCE SYSTEM CDL`；
  5. 含 LVS 开关（`LVS ISOLATE NAMES`/`LVS RECOGNIZE GATES`/`LVS PORTS` 类，至少 1 条 LVS 指令）；
  6. LSF 提交脚本含 `bsub` + `-q` 队列 + `-n` 核数（核数参数化，默认 12）；
  7. **不本地跑**（无 `calibre -lvs ...` 直跑行，或仅注释）；提交脚本可独立执行生成 bsub 命令；
  8. 参数化占位符：换 hidden B（不同 gds/cdl/cell/outdir）后 runset 字段正确替换（hidden B 反根因：B 用不同 cell 名/路径，hardcode-A 的会臆造 and2DSx2 → FAIL）；
  9. 确定性（同输入 3 次同输出）；
  10. §4.9 trio（空壳 / print-A-runset / 删核心参数化逻辑）全 FAIL。
- **hidden B**：不同 cell（如 `nand2DSx4`）+ 不同 gds/cdl 路径 + 不同核数（8）+ 不同队列，反硬编码。
- **资产获取**：下轮从 pin004 scp and2DSx2.gds/.cdl/lvsRunset + update_lvs_runset.py + SKILL.md（参考解来源）。

## 4. 去重确认
- 全 C cases 扫「lvs job」0 命中；felixw 已有 case 仅 `CalibreDrcRunsetBlankDiag-001`（gohxq, DRC runset blank diag，意图不同）。
- LVS 家族已有：`LvsRepDiagnose / LvsSeedPromoDetect / LvsFlagFlipRunme / LvsShortCheckRunsetPatch / LvsConfigReport / CalibreLvsRepDiag / CalibreLvsRepParse / CalibreLvsRulePtnFix` —— 均为 LVS 报告解析/runset 修补/flag 翻转，**无「跑 LVS job + LSF 提交 + 参数化 skill 集成」意图**。2nc86 不重复。

## 5. 风险
- session 含 Argus LVS 次主线 + continuous-learning 元指令，full deepread 须区分主线（Calibre LVS job + skill 集成）与噪声。
- 真实 GDS/CDL 可能较大，A 附件需裁剪或用小真实样例。
- LSF 在 SUT 沙盒未必可用 → LIVE 分类与 check 设计须据此调整（可能纯静态判 runset+提交脚本结构 = NA）。
