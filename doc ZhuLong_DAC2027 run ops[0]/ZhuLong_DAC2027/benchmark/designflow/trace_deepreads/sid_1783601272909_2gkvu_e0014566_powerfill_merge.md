# 深读笔记 — sid 1783601272909_2gkvu (e0014566 @ hfeg0pkn001)

- **session**: `1783601272909_2gkvu.messages.json` (e0014566 / hfeg0pkn001 / 10.129.2.10, mc=295)
- **规模**: 245 msgs (124 user / 121 assistant), 545 KB
- **工具分布**: run_commands 64, SandBox_MCP_Server__run_code 26 (SKILL via Virtuoso), read_files 18, editor 8, search_codebase 1
- **关键词**: virtuoso:387, dbopencellviewbytype:157, ddgetobj:146, .gds:55, dbcreateinst:31, cellview:24, calibre:21, schematic:18
- **domain**: layout_virtuoso (真实 dbCreateInst + dbOpenCellViewByType + .gds 版图编辑)
- **A-档 seed 轮**: USER#0「read the prompt_powerfill.md and do the job in it.」(提出目标未给根因/修复 → A-档 seed 合格)
- **后续反馈轮 (hint, 不进 prompt)**:
  - USER#1「看看你生成的merge 后的 layout, 是不是与我手动操作的一致(test_20260709)」——对照手动参考 cell 验证合并结果
  - USER#2「我看你最终merge得到的test_20260528_powerfill 里有个view test_20260528, 不想要这个，把这个去除。」——合并不能带进无关 view
  - USER#5「你一开始跑的时候出现了一次文件锁问题，而重跑了，如果避免，不想你重跑。」——锁失败清锁重试，不要重跑整流
  - USER#6「你这个生成merge后的layout的方法很好，直接应用到skill  virtuoso-autovia-runner 中」——把合并方法泛化到 autovia-runner skill

## 真实意图
PowerFill 流末步「合并」：把源版图 `austin_new/test_20260528/layout` 拷到输出 `austin_new/test_20260528_powerfill`，再把 PowerFill 生成的填充单元 `auto_pgfill/test_20260528_auto_pgfill` 实例化进去，得到合并版图。要求：只拷 layout view（不带 schematic/symbol）、锁失败清锁重试（不重跑）、复刻手动 GUI 工作流、参数化可复用到 autovia-runner。

## gold (用户实际接受的产物)
真实 final 文件（仍在远端 /home/e0014566/test_power_analysis_5/skills/.../）：
- `virtuoso-powerfill-runner/assets/run_powerfill_nogui.il` (26879 B) — 含 legacy 过程 + `RunPowerFillNoGui()` 主体 + **合并块**（单 view cp -rf + rm .cdslck + dbOpenCellViewByType "a" 三级重试 + dbCreateInst 原点 R0 + dbSave/dbComputeBBox/dbSave/dbClose）
- `virtuoso-autovia-runner/assets/run_autovia_nogui.il` (34605 B) — 同合并方法套用到 autovia
- `run_powerfill_config.il` (1773 B) — 真实配置（process=cxmt10G4plus, libName=austin_new, cellName=test_20260528, viewType=layout, workDir=/proj/train/AI_Virtuoso/workdir/e0014566, powerName=VCC! VSS!, outLibName=austin_new, outCellName=test_20260528_powerfill）

### 合并块关键 SKILL 形式（gold 核心）
```skill
unless(libName == outLibName && cellName == outCellName
  shell(strcat("cp -rf " ddGetObj(libName)~>readPath "/" cellName "/" viewType " "
               ddGetObj(outLibName)~>readPath "/" outCellName "/" viewType " 2>/dev/null"))
  shell(strcat("rm -f " ddGetObj(outLibName)~>readPath "/" outCellName "/" viewType "/*.cdslck* 2>/dev/null"))
)
dstCV = dbOpenCellViewByType(outLibName outCellName viewType "" "a")
unless(dstCV
  shell(strcat("rm -f " ... "*.cdslck*"))
  dstCV = dbOpenCellViewByType(outLibName outCellName viewType "" "a")
)
unless(dstCV
  let((tmpCV) tmpCV = dbOpenCellViewByType(outLibName outCellName viewType "maskLayout" "w")
    if(tmpCV then dbDeleteObject(tmpCV)))
  shell(strcat("rm -f " ... "*.cdslck*"))
  dstCV = dbOpenCellViewByType(outLibName outCellName viewType "" "a")
)
fillMasterCV = dbOpenCellViewByType(fillLibName fillCellName "layout" "" "r")
dbCreateInst(dstCV fillMasterCV fillCellName list(0 0) "R0")
dbSave(dstCV) dbComputeBBox(dstCV) dbSave(dstCV) dbClose(dstCV)
```

## A-档 vs B-档判定
- gold 依赖 live Virtuoso + live `austin_new/test_20260528` 库 + `/proj/train/AI_Virtuoso/workdir/e0014566` workdir → .75 沙盒不可达 → **A-disqualified**
- → **B-档 synthesized L1-boundary**（spec→SKILL 代码生成）：候选 `gen_powerfill_merge_skill.py` 读 `merge_config.json` → 生成 `run_powerfill_merge.il`

## 正交性
与 r86 DRCReportIpAudit（DRC 报告解析）、r80 DRCSpecGen（spec→SVRF）、PFMergeAudit-001（FIG inventory 审计）、PFMergeDupAudit-001（重复审计）、PowerFill-001（GDS calibredrv 审计）、FillImplantFlowAudit-001（AST 审计）正交。本案是 **PowerFill 合并步的 spec→SKILL 代码生成**（单 view 拷贝 + 锁清理重试 + dbCreateInst 合并）。

## 合成产物
- case_id: `EDA-Eval-DesignFlow-PowerFillMergeGen-001`
- 资产 A: `artifacts/merge_config.json` + `artifacts/baseline_run_powerfill_nogui.il` (缺合并块, 仅上下文) + `task_brief.md`
- 隐藏 B: HD3P DDR SRAM top（测内联防硬编码 A）; B2: src==dst test_20260709（测自拷贝守卫）; B3: 缺 fillCellName（测优雅失败）
- check.py: 15 条断言 (a..o), 自验 ref PASS 15/15, 4 neg 全 FAIL, §4.9 (a)(b)(c) 全 FAIL
- test_rationale: `15 条断言：①…⑮` (k_rationale=k_check=15 ≥ 8 GATE PASS)
- jsonl_C: 86 → 87; layout_virtuoso 17 → 18
