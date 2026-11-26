# Deepread: ckulq (e0045144@hfeg0pkn002, mc129) — VC-SpyGlass RDC violation catalog

**trace**: `/home/e0045144/.cline/data/sessions/1791977055190_ckulq/1791977055190_ckulq.messages.json`
**size**: 2.04MB, 517 msgs, 10 user-text turns
**domain**: verification (VC-SpyGlass RDC = Reset Domain Crossing static verification)
**keywords**: synopsys:368/rtl:283/verilog:153/vhdl:90/systemverilog:45/schematic:107/drc:12 (digital-dominant, digi494 vs ana119)

## 用户轮 (10 turns)
- USER#0 你会做什么？ (intro, skip)
- USER#2 你会跟据spec写完整到RTL code吗 (capability, skip)
- USER#4 读取 vc_spyglass_rdc_userguide.pdf，根据 lint 需求书格式写 RDC 流程需求书 (大段 inline lint spec 模板 + RDC user guide PDF 作源 → 产 CXDP_RDC_Flow_Requirement.md)
- USER#100 可以帮我把 RDC user guide 翻译成中文吗 → vc_spyglass_rdc_userguide_zh.md
- USER#184 翻译内容太少只有章节基本描述，细节要一并翻译输出
- **USER#340「帮我列出 setup/corruption 中的 violation 类型」** ← 选为本 case (干净需求轮, A-faithful rule2 未违反: 用户只提目标, 未给根因/修复)
- USER#360「帮我把上述违例对应的具体修复方式列出来，并输出到文档」→ vc_spyglass_rdc_violations_fixes.md (322 行, 35 Tag 详解) — 依赖「上述违例」(=USER#340 输出), 有前提依赖, 不选
- USER#418 帮我画一个 RDC 执行流程，包含 setup,corruption 阶段
- USER#432 可以生成图形格式吗
- USER#504 如何打开 png 格式文件 (out-of-scope, skip)

## 本 case 选轮: USER#340 (A-faithful)
- **逐字原文**: 「帮我列出 setup/corruption 中的 violation 类型」
- **gold (msg#359)**: 助手从 RDC user guide 提取 148 个违规 Tag, 整理成功能分类清单:
  - 🔴 SETUP 违规 (72 个): ① 时钟配置类 (Clock Setup) 11 Tag | ② 复位完整性类 (Reset Integrity) 20 Tag | ③ 黑盒/库单元建模类 5 Tag | ④ SDC 约束类 17 Tag | ⑤ RDC 约束类 ...
  - CORRUPTION 违规: RDC_CORRUPT_OBSERVED / RDC_CLOCK_CORRUPT_OBSERVED / RDC_CORRUPT_BLOCKED / RDC_CORRUPT_POTENTIAL / SRC_CONV_* / GLITCH_*
  - 每 Tag: Tag 名 + 严重级别 (Error/Warning/Info) + 说明
- **工具链**: read_files (PDF/txt) → editor (list_violations*.py 提取脚本) → run_approved_command (跑脚本) → 整理成分类清单
- **真实源**: vc_spyglass_rdc_userguide.pdf @ /apps/synopsys/SRB/vc_static_2023.12-SP1/doc/... (SUT 不可达 → B 档合成资产)

## 合成决策 (B 档资产, A 档 task说明)
- 真实 PDF 在 /apps/synopsys 远程路径, SUT 沙盒不可达 → 合成 RDC rule reference (markdown, 含 Tag+severity+description, 按 SETUP/CORRUPTION 分节, 子类别)
- A (SUT 可见): rdc_rules_reference_A.md (~30 Tag, SETUP 5 子类 + CORRUPTION 2 子类)
- 隐藏 B: rdc_rules_reference_B.md (~20 Tag, 不同分布/子类名/Tag 名, 结构与 A 不同)
- B' (随机化 seed): ~15 Tag, 反硬编
- 候选 = gen_rdc_violation_catalog.py (通用 markdown 解析器: 读 reference → 输出分类目录)
- gold for check = 候选在隐藏 B 上应产的目录 (从 B reference 派生, 非硬编 A)

## 契约
- mode: design_flow, entry_point: outputs/submit.zip, test: check(deliverable, workdir)
- candidate: gen_rdc_violation_catalog.py (读 reference 路径, 输出 catalog.md)
- L1-static (离线文本解析, 无 EDA 工具真跑; subprocess 真跑候选于隐藏 B)
- domain: verification (RDC 静态验证)
