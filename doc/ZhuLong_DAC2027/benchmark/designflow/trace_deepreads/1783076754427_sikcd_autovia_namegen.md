# 深读笔记 — 1783076754427_sikcd (e0014566 @ hfeg0pkn001, mc=252)

- **trace**: 240 msgs / 487KB, agent `cline(lead)`, cwd `/home/e0014566`
- **tools**: calibre:176 / virtuoso:173 / cellview:91 / skill:51 / dbCreateInst:4
- **domain**: layout_virtuoso (Virtuoso AutoVia SKILL 流)
- **真实任务**: 用户跑 `virtuoso-auto-via` SKILL 流（`IMCleAutoVia_nogui.il` + `addViaToLayout.il`）给 `austin/layout_austin4` 自动打 power via

## 用户轮（提出需求 / 表达目标）
- USER#0: "read the usage_prompt.md and do the job in it."（A-档 seed 合格：提出需求未给根因）
- USER#12: "Source Library: austin . Source Cell: layout_austin4 . Power Nets: vss! . Stream-in Library: austin . 其余的参数给我点建议。"
- USER#13: "run dierectory: /proj/train/AI_Virtuoso/ver/autovia/austin/layout_austin4 ."
- USER#115: "就这个没有内容的，你把他跑完，产生出一个via cell, 然后加入到原layout呗。校验不要设置太严格，保证这种情况下也是可以跑通的。"
- USER#82/110: 报 strmout 失败 / 缺共享库（已给根因，不作 A-档 seed）

## agent 工具链与产物
1. read `usage_prompt.md`、`SKILL.md`、`references/parameters.md`、`IMCleAutoVia_nogui.il`、`addViaToLayout.il`
2. `ask_question` 收集参数 → 建参数表（pwrnets=vss!, viaTypes=CT V1 V2 V3, strminLib=austin, runDir, topCell=layout_austin4, coreNum=4, addDateSuffix=No, genTopCell=No）
3. 拼 SKILL 命令束：`load(IMCleAutoVia_nogui.il)` + `load(addViaToLayout.il)` + `IMCleAutoViaAndAddToLayout(...)` / `IMCleAutoViaRun(...)`
4. SandBox_MCP_Server（pyAether SKILL）执行：`load` 成功，`IMCleAutoViaRun` 跑通但无产物；`IMCleAutoViaAndAddToLayout` step1 成功、step2 "Failed to open via master"
5. 发现 `geGetEditCellView()` 返回 `austin/layout_austin4/layout`，但 `cv~>figs` 长度=0（空壳 cell，只有 bBox）
6. `strmout` 命令行工具缺 `libXss.so.1`（IC617/IC231 都缺），无 root 装不了
7. 分析 `IMCleAutoViaAndAddToLayout` @optional 参数顺序 vs `IMCleAutoViaRun` @optional 顺序
8. 最终给 Virtuoso CIW 命令串

## 关键发现：agent 把 viaSelStr 顺序算错了
- agent 算的 via cell 名：`layout_austin4_CTV1V2V3_vss_VIA`（按用户 viaTypes **列表顺序** CT,V1,V2,V3 拼）
- 但 `IMCleAutoVia_nogui.il` 里 `viaSelStr` 是按**固定 canonical 顺序**拼接（V2A,V1A,RDV,V5,V4,V3,V2,V1,CT,...），与用户列表顺序无关
- 对 [CT,V1,V2,V3]：canonical 拼出 `_V3V2V1CT` → 正确 via cell 名 = `layout_austin4_V3V2V1CT_vss_VIA`
- 旁证：库里已有 `layout_austin2_V4V3V2V1CT_vss_VIA`（canonical 序，非用户序）→ SKILL 一致用 canonical

## SKILL 命名逻辑（IMCleAutoVia_nogui.il 真实代码）
- `IMCleAutoViaGetDefaults()`：processName→processDef 映射（imc17n→G1, cxmt10G4plus*→G4plus, ...，未映射落 else→cxmt10G3）；viaTypeList/viaListDef 按工艺/项目/Ver 分支；runDirDef=`/proj/<PROJ_NAME>/<Ver>/ver/autovia/<lib>/<cell>`，gdsFileDef=runDirDef+`/`+cell+`.gds`
- viaTypes→selectionFlags：用户给 viaTypes 时按 `member` 判定每个 via 的 y/n；否则按 viaListDef 的 `nth()` + 工艺分支
- `viaSelStr` 拼接：`_` 起头，按 canonical 序 V2A,V1A,RDV,V5,V4,V3,V2,V1,CT,T2V1,T2V2,T8V3,T2V3 依次 if-selected 拼接；`hl22` 工艺再拼 RV（RDV 选中时）；`ts22` 工艺改拼 VIA1..VIA9；`lhioa` 工艺再拼 Vy2,Vy1,Vr2,Vr1,V1andV2,V1,RV；addDateSuffix 时末尾追加 `_dateString`
- `date` = `nth(3)+nth(0)+nth(1)` of `parseString(getCurrentTime())`（年+月名+日）
- `dateString` = `IMCleGetTimeString` = `year + MM + day`（月份名 Jan..Dec→01..12）
- `genViaCell`：对每个 pwrnet（`!` 剥离），`projName=="lhioa"` 时 `<top>_<pwrnet>_VIA_<date>`，否则 `<top><viaSelStr>_<pwrnet>_VIA`
- `genViaTopCell`：genTopCell 时，addDateSuffix `<top>_<dateString>_VIA_TOP` 否则 `<top>_VIA_TOP`
- `IMCleAutoViaRun` 9 个 @optional 位置参数：pwrnets, strminLib, runDir, gdsFile, topCellName, viaTypes, coreNum, addDateSuffix, genTopCell
- `IMCleAutoViaAndAddToLayout` 13 个 @optional：pwrnets, viaTypes, strminLib, runDir, gdsFile, topCellName, coreNum, addDateSuffix, genTopCell, viaOrigin, viaOrient, dstLib, dstCell（内部按 IMCleAutoViaRun 顺序转调）
- `gdsFile` 默认值用 **runDirDef（默认公式）**，不是用户传入的 runDir（SKILL 真实行为，复刻时不要"修正"）

## gold 可行性
- A-档（faithful）不可行：gold = live Virtuoso OA 里跑 SKILL 产生的 via cell + 合并 layout，强状态依赖，不可离线静默判分
- B-档（synthesized）L1-boundary 可行：把命名逻辑抽成离线可计算核心（JSON spec→JSON out），见 EDA-Eval-DesignFlow-AutoViaNameGen-001
