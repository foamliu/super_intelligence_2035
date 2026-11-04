# Deepread: ellawu / 1789545344007_xchvr (fill-implant DRC flow audit)

- trace: ellawu / hfeg0pkn005 / session 1789545344007_xchvr.messages.json
- mc=122, tools: 2246 calibre + 8 virtuoso + 7 schematic + 6 pyAether + 2 dbGet
- 75 msgs / 1.385 MB, agent=lead, updated 2026-09-16
- NEW user ellawu (decqa group); domain physical_verify (fill-implant DRC)

## User turns (verbatim, A-档 seed candidates)
- USER#1 (msg0): `ERROR: Error OPEN1 - problem with access, file type, or file open of file: calibreSTIcmp.rule.` (reports error symptom)
- USER#2 (msg51): pastes auto_pgdm GUI script (46975 chars, AA/PG DUMMY gen for logic cells)
- USER#3 (msg59): `workDir = ...; if not os.path.exists ... 后加如果存在就删掉之前的所有文件` (gives fix -> hint)
- USER#4 (msg63): `jiandianyidande` (pinyin: 简单一点的)
- USER#5 (msg65): pastes 10G5 Calibre DRC deck (20170 chars)
- USER#6 (msg67): pastes IMCleFillImplantDRC pyAether script (178229 chars) — the fill_implant_flow
- USER#7 (msg69): `ruguobucunzai xiayigeminglingyebushengchengdummy zenmeban`
- USER#8 (msg71): `flow youshenmewentima` (flow 有什么问题吗) ← **A-档 seed** (pure goal, no root cause given)
- USER#9 (msg73): `open1 shishenme` (open1 是什么)

## Assistant tool chain (msg1..msg74)
- list_allowed_files(/proj/decqa/V0/workdir/ellawu) + search_codebase(calibreSTIcmp.rule, OPEN1)
- read_files(genPGDummy_for_Logic.py, gen_preAA_G5_CIP.py, gen_preAA_G5_CIP_final.py, log.txt) — file contents stripped from trace tool_results (only list_allowed_files JSON kept)
- run_commands DISABLED (raw shell off; must use run_approved_command)
- list_allowed_files(/apps/imctf/runset/calibre/{cxmt10G5,cxmt10G4plus,cxmtG5_CIP}/current) → discovered cxmtG5_CIP/current/decqa/runset/calibreSTIcmp.rule
- read_files(calibreSTIcmp.rule lines 1-50/50-120/880-1000/12400-12471) → rule has LAYOUT path/primary but NO LAYOUT PRECISION
- read_files(.PG_DUMMY_for_Logic.config) → process=cxmtG5_CIP, libName=ella_train, topCell=AF_Fs...
- get_agent_policy_status → agent policy restricts writes to /ai_sandbox + /home; workspace on /proj → CANNOT edit
- msg58: root-cause analysis (4 issues): (1) LAYOUT PRECISION never injected (PRIMARY), (2) rsync return unchecked, (3) no file existence check before calibre, (4) sed case mismatch
- msg72: flow problem audit of IMCle_generate_implant_fill() — 8 problems (see gold)

## Gold (msg72) — 8 flow problems in IMCle_generate_implant_fill()
1. drcMainDeck 用 `if` 非 `elif` 无 else -> 未知工艺 (e.g. cxmt10G8) 未定义 -> `cp -rf ` 空串报错; cxmt10G4plus/G4B_CIP 完全无 deck
2. LAYOUT PRECISION 算了 precision=10000 但从没写进 rule -> 同 OPEN1 重现
3. `bsub -Is` 交互式 -> 卡队列/socket 超时/无 tty
4. `cp -rf` rule 文件没检查返回值 -> 静默失败 -> OPEN1
5. `os.makedirs` 在 try/except 只 print -> 目录没建成却继续
6. workDir 残留旧文件 -> 误判
7. 十几个 `os.system` 无一检查返回值
8. `cv = da.getEditDesign()` 然后 `cv = ae.aeGetCurDesign()` 取两次 -> 竞态

## A-disqualified reasoning
Gold = live 静态分析报告, 但脚本读取的 /proj/decqa/V0/workdir/ellawu/*.py 与 /apps/imctf/runset/calibre/cxmtG5_CIP/* 均在内网 (hfeg0pkn005), .75 沙盒不可达; 且 live pyAether/Aether/Calibre 不可达. → A-disqualified → B-档 synthesized L1-boundary (纯离线 AST 静态审查, 不依赖任何 live 工具/路径).

## Synthesized case (FillImplantFlowAudit-001)
- 资产 A: flow_script.py 忠实复刻 IMCle_generate_implant_fill() 缺陷结构 (cxmtG5_CIP, 8 类全)
- 隐藏 B: cxmtG4C 变体, 6 类 (无 bsub, 无 duplicate_cv)
- 隐藏 B2: cxmt10G6 变体, 3 类 (elif+else 无 process_deck_map, workDir 清理, makedirs re-raise)
- 隐藏 B3: 干净流, 0 类 (precision 注入 + 全 _checked + elif+else + workDir 清理, verdict CLEAN)
- 候选 audit_fill_implant_flow.py: AST + 字面量扫描, 8 类缺陷检测, 输出结构化 JSON
- check.py 14 断言 (a..n): 独立 AST oracle 重推 B/B2/B3/A 的 bug 集合与计数对账 + 跨输入 guard + 确定性
- ref PASS 14/14; 4 neg (empty/print_expected/hardcode_B/count_only) 全 FAIL; §4.9 三假提交全 FAIL; test==disk OK
- jsonl_C 83 → 84; physical_verify 31 → 32; ledger 180 (case 84 · parked 96)
- k_rationale = k_check = 14 ≥ 8 GATE PASS
