# 深读笔记 — 1790083095684_oblxr (e0014566 @ hfeg0pkn001)

- session: 1790083095684_oblxr.messages.json, user e0014566, host hfeg0pkn001 (10.129.2.10), mc=274
  (keywords: virtuoso:1143 / schematic:248 / cellview:131 / dbGet:120 / pyAether:82 / calibre:56)
- meta: model glm-5.2, cwd /home/e0014566/Desktop/PA_0922_LJ/PowerAnalysis, 300 msgs / 2.6MB,
  status completed exit 0
- tools: read_files（读 4 config + 3 generator .py + 3 SKILL.md + 3 nogui.il 模板 + test_layout_rscalc_flow_19
  历史样例 baseline_rpoints.csv/common.config）/ run_approved_command(python-runner) 跑
  apply_poweranalysis_edits.py 一次性改 3 个 config / editor 修 rscalc.config 注释

## 真实意图（USER 原话逐字）
- USER#0 (idx0, 唯一用户指令, A-档 seed 提出目标未给根因):
  「现在我重新在 project 里新建了一个 OA 数据
   /proj/train/V0_Austin/workdir/e0014566/auto_qx_case1/BCenterCA，把 common.config 的 lib/cell 改了，
   其余没变；你看我还有什么要改的」
- 全程只有 1 条用户文本指令（其余用户消息均为 tool_result）。单轮闭环咨询任务。

## 真实 agent 行为（cline）
- read_files 读 common.config（process cxmt10G4plus / project train / libName auto_qx_case1 /
  cellName BCenterCA / version V0_Austin / workDir /proj/train/V0_Austin/workdir/e0014566/）。
- read_files 读 rscalc.config（version V0_qx / useExistGds Yes / gdsFile Array16G_T_rscalc.gds /
  checkPoints 52 个 vcc!/vss! 真实坐标表）。
- read_files 读 run_autovia_config.il（strminLib auto_austin_case1 / runDir / outLibName /
  outCellName Array16G_T_rscalc_via1）。
- read_files 读 run_powerfill_config.il（strminLibCfg / outLibName / outCellName
  Array16G_T_rscalc_opt1 / workDir /proj/train/V0_Austin/workdir/e0014566/）。
- read_files 读 genPowerFill.py（32KB），发现 get_info() 用 os.getcwd() 正则
  `^/proj/([^/]+)/([^/]+)/` 推导 projName/ver（启动坑：必须从 /proj/... 启动，不能从 Desktop 启动）。
- run_approved_command(python-runner) 跑 apply_poweranalysis_edits.py 一次性改 3 个 config
  （common.config 单一来源已改，rscalc/autovia/powerfill 三处写死旧 lib/cell/路径/坐标需同步）。
- editor 修 rscalc.config 注释（标注 useExistGds/gdsFile/checkPoints 的迁移语义）。

## 真实 gold（人工复核 msg#28 / msg#77，迁移 runbook）
迁移 runbook——common.config 单一来源已改，其余三 config 写死旧 lib/cell/路径/坐标需同步：
- rscalc.config: version V0_qx → V0_Austin（对齐项目路径）/ useExistGds Yes → No /
  gdsFile 清空（Array16G_T_rscalc.gds → ""）/ checkPoints 旧 52 坐标 → nil（从 RNODE 重生成）。
- run_autovia_config.il: strminLib / runDir / outLibName / outCellName 同步新 lib/cell。
- run_powerfill_config.il: strminLibCfg / outLibName / outCellName 同步（workDir 不改 = cds.lib OA 目录）。
- generator .py 与 nogui.il 模板无硬编码 lib/cell，不改。
- 启动坑: genPowerFill.py 由 os.getcwd() `^/proj/([^/]+)/([^/]+)/` 推导 projName/ver，必须从
  /proj/... 启动，不能从 Desktop 启动（否则推导失败）。
- cwd 推导坑: 项目路径 /proj/train/V0_Austin/... → projName=train / ver=V0_Austin。

## A-档 faithful 不可行性
- gold 依赖 live OA / PowerAnalysis 代码树（live genPowerFill.py 32KB）+ live Virtuoso 环境。
- 内网源码树 + live Virtuoso 不可整体 fixture 化 → A-档 faithful 不可行。
- → B-档 synthesized L1-boundary: 离线 config bundle fixture（4 config + genPowerFill.py 节选）
  → 参数化迁移脚本 + runbook, stdlib-only, 确定性, 不硬编码旧/新值。

## 资产 A 忠实（取值真实）
- common.config: process cxmt10G4plus / project train / libName auto_qx_case1 / cellName BCenterCA /
  version V0_Austin / workDir /proj/train/V0_Austin/workdir/e0014566/。
- rscalc.config: version V0_qx / useExistGds Yes / gdsFile Array16G_T_rscalc.gds /
  checkPoints 52 个 vcc!/vss! 真实坐标表。
- run_autovia_config.il: strminLib auto_austin_case1 / outCellName Array16G_T_rscalc_via1。
- run_powerfill_config.il: outCellName Array16G_T_rscalc_opt1 /
  workDir /proj/train/V0_Austin/workdir/e0014566/。
- genPowerFill.py: 真实 get_info() cwd 正则 `^/proj/([^/]+)/([^/]+)/`。
- prompt.txt: USER#0 逐字 + 场景（用户在新 OA 项目里改了 common.config，问其余 config 还要改什么）+ 交付要求。

## hidden B（结构同、取值不同）
- 项目 drgqa / 工艺 cxmt10G5 / new_lib ddrga_top_lib / new_cell DDR5TopCA / new_ver V0_ddrga /
  旧 lib legacy_ddr4_lib / 旧 cell DDR4Top_rscalc / 旧版本 V0_legacy /
  workDir /proj/drgqa/V0_ddrga/workdir/qateam / 不同 vdd!/vss! 坐标 20 个。
- → 杀硬编码 A 的 BCenterCA / auto_qx_case1 / V0_Austin / Array16G_T / 52 坐标 / cxmt10G4plus。

## 合成 reference
- migrate_ref.py: --bundle-dir/--out-zip → 读 common.config（单一来源 new_lib/new_cell/new_ver）→
  迁移 rscalc.config（version 对齐 / useExistGds No / gdsFile 清空 / checkPoints nil 重生成）→
  迁移 run_autovia_config.il（strminLib/outLibName/outCellName）→ 迁移 run_powerfill_config.il
  （strminLibCfg/outLibName/outCellName，workDir 不改）→ emit migration_runbook.md（中文 runbook）+
  migrate.py（参数化迁移器）→ zip 打包。
- migration_runbook_ref.md: 中文迁移手册（§1 common.config 已改 §2 rscalc.config §3 autovia §4 powerfill
  §5 启动坑 cwd 推导 §6 不改项）。
- check.py: 18 条独立 `_check()` 条件（见 jsonl test_rationale）。
- negative/: migrate_naive.py（硬编码 A 值）/ migrate_stub.py（空壳）/ migrate_ref_corecut.py（删 checkPoints 重生成）/
  negative_selftest.py（ref PASS + 5 negative 全 FAIL + §4.9 三假全 FAIL）。

## 18 条断言（k=18，check.py `_check(` 数 = rationale 数）
①zip 含 migration_runbook.md 与 migrate.py 非空 ②migrate.py 在隐藏 B 上 exit 0 无 traceback
③rscalc.config useExistGds → "No" ④rscalc.config gdsFile 清空 "" ⑤rscalc.config checkPoints nil 重生成
⑥rscalc.config version 对齐 B new_ver ⑦run_autovia_config.il strminLib 改 B new_lib ⑧run_autovia outCellName 含 B new_cell
⑨run_powerfill_config.il strminLibCfg 改 B new_lib ⑩run_powerfill outCellName 含 B new_cell
⑪workDir 不可改（保持 B 原 workDir）⑫migrate.py stdlib-only ⑬确定性 3×md5 一致
⑭交叉纯净: runbook 引用 B 独有 DDR5TopCA/ddrga ⑮不泄漏 A 的 BCenterCA/auto_qx_case1
⑯runbook 含启动坑 cwd 推导说明 ⑰runbook 含 workDir 不改说明 ⑱checkPoints nil 派生（非硬编码空）。

## 正交性
- pg_layout 域现有 case: InnovusViaCutDiag（via cut 诊断）/ 1784623431472_gvm3g（pwrirem cfg fix）。
- 本案 = Virtuoso PowerAnalysis **多 config 同步迁移**（common.config 单一来源 → rscalc/autovia/powerfill
  三处写死 lib/cell/路径/坐标同步 + cwd 推导启动坑 + checkPoints nil 重生成），首次覆盖"PowerAnalysis
  config bundle 迁移"子主题。e0014566 首个 oblxr trace（与 RsCalc 系列 e0014566/sikcd 不同任务：sikcd 是
  autovia agent 生成，本案是 config 迁移）。
