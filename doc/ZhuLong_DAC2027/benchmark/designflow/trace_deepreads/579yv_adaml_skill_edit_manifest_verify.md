# deepread: 579yv adaml@hfhds201 — virtuoso-sch-editor skill self-evolution (1.0→1.1→1.2)

- **trace**: 1794987555129_579yv.messages.json, adaml@hfhds201, mc=162, 109 msgs / 845KB
- **session_file**: /home/adaml/.cline/data/sessions/1794987555129_579yv/1794987555129_579yv.messages.json
- **domain**: layout_virtuoso (virtuoso schematic editor skill maintenance)

## 用户真实意图（两阶段）

### 阶段 1 (msg 0-38): TSPC_RVT schematic 截图查看 + DB 交叉验证
- adaml 在 /proj/m2701/V0_DDR4/workdir/adaml/Test/TSPC_RVT 维护 TSPC_RVT schematic
- 用 virtuoso-sch-editor skill 打开 schematic（geOpen ?lib Test ?cell TSPC_RVT ?view schematic → window:3）
- 截图：hiExportImage(?exportRegion 'entireDesign ?width 3000 ?bgColor "white") + hiWindowSaveImage(?target win ?format "png")
- zoom：hiZoomIn(win cv~>bBox)；落盘校验 isFile(...)
- DB dump：35 实例（20 管 + 11 intDEV 电源 + 4 basic PIN）、16 nets、bBox ~10.25×4.3µm
- 截图与 DB 交叉验证：图上 PMOS 上排/NMOS 下排/vcc! tie/vss! tie/黄色 net4 长线 与 DB 一致

### 阶段 2 (msg 39-108): ai-skill-optimizer 两轮优化 virtuoso-sch-editor
- **1.0.0→1.1.0** (msg 40-70): preflight_check + audit_skill → 备份 → 13 处 SKILL.md 编辑：
  - 新增「截图自检（edit → shot → 看图 → 再改）」章节（geOpen→hiZoomIn→hiExportImage/hiWindowSaveImage→isFile→删图）
  - 截图管理纪律（路径固定沙盒 sch_shots/、同名覆盖、展示过即删、禁写 /proj）
  - description 加触发词「截图看schematic」「schematic截图」
  - 修正过时结论（geOpen bridge 实测可用，推翻原"不可用"）
  - 已知陷阱扩到 11 条（#5 扩展 nil 用 %L；新增 #8 master~>cellName、#9 foreach.mapcar 报错、#10 dbFindInstByName 未定义、#11 cv~>terms 不可靠用 net~>terms）
  - verify 脚本 _verify_vse_1_1_0.py：11/11 内容断言 OK
- **1.1.0→1.2.0** (msg 71-96): 用户「这个 skill 不需要生成版图功能，越界了」→ 范围收缩：
  - 移除 lxGenFromSource / 从 schematic 生成 layout（description、目标、边界、API 表、端到端示例、验收标准全清）
  - 加 AnaWeave 转介边界（"需要生成版图/自动布局时请用 AnaWeave 技能"）
  - version 1.1.0→1.2.0；最小端到端示例标题去掉"→ 生成 layout"；step 6 改"保存（生成版图不在本技能范围；需要时用 AnaWeave）"
  - verify 脚本 _verify_vse_1_2_0.py + audit_skill 复跑 PASS

## 关键 reframe 判断
- 阶段 1 的截图/DB dump 依赖 Virtuoso GUI + SKILL bridge，无法离线判分
- 阶段 2 的核心可判分子问题 = **verify 脚本本身**：_verify_vse_1_x_0.py 对 SKILL.md 做 frontmatter/章节/短语/陷阱计数/行数断言
- 固化为通用 **skill-edit manifest 验证器**：读 SKILL.md + manifest.json → report.json，离线纯 stdlib

## 子型正交性
- adaml 既有 C case: LvsRunCompare-001(rep 比较)、EmyCdlNetlistExtract-001(CDL netlist 解析)、CalibreLvsRepParse-001(rep 解析) — 均为 EDA 报告/netlist 解析
- 本 case `skill_edit_manifest_verify` = SKILL.md 文档结构验证（frontmatter YAML + markdown 章节 + 表格行 + 编号陷阱计数），全新子型，与既有正交

## 真实事实落地（A/B 基于这些合成）
- version 1.1.0 / 1.2.0
- 截图自检章节（hiExportImage/hiWindowSaveImage）
- 11 条已知陷阱（1.1.0 扩到 11，1.2.0 保持 11）
- lxGenFromSource 1.1.0 在表 / 1.2.0 移除
- AnaWeave 1.2.0 加入
- "从 schematic 生成 layout" 1.1.0 在 / 1.2.0 移除
- 触发词 schHiCreateWireLabel / 截图看schematic
