# 深读笔记 — fxian / 1792559768471_mc7z1 (layout_aether, B 档 synthesized, L1-boundary)

- **session**: `1792559768471_mc7z1`，fxian @ hfeg0pkn002，mc=329，tools: schematic 916 + pyAether 328 + dbGet 267 + cellview 173 + netlist 32 + virtuoso 32（layout/pyAether-dominant，NEW 用户）。
- **meta**: model deepseek-v4-flash，cwd `/ai_sandbox/drgqa/V0/agentdir/fxian`，status=**idle**（无干净"成功了"接受），n_msgs=403，17 user_input 轮。
- **T0=U[0] 逐字原文**: 「可以做一些自动化工具么？譬如帮忙从顶层cell打到指定cell的port，同步更新schematic和symbol」= 纯需求委托轮，无根因、无修复 = 合规 A-档 seed。
- **U[2] idx=136**: 「最好能配个gui界面用户操作，指定lib&cell name(顶层到底层)」= refine（加 GUI）。
- **U[5] idx=248**: 「顶层 lib:drgqa_cmos_work, cell name=Rasbanklogic_lg260731, 最下lib=drgqa_cmos_work,cell=R_SaCtrol_sub_UVW_Dummy, 新加的port name=in_test(input), 你试试」= 具体参数 + 试跑。
- **U[7-8] idx=348/382**: bug 报告（卡 / RuntimeError 未找到实例路径）= debug 轮，不进 prompt。
- **assistant 工具链**: RAG search_apis ~20（pyAether: dbOpenCV/dbFindInst/dbCrtSchWire/dbCrtSymbolPin/dbSchGetPinOrder/emyTermGetPinFigs/dbGetInstTransform）+ editor 45 次（route_to_port.py 15 → route_hierarchy.py 18 → route_gui.py 12）+ run_approved_command 多次跑 _dryrun_*.py / _compile_check.py / _final_validate.py。
- **gold 形态**: assistant 自写 `_dryrun_propagate.py` 用 mock pyAether 验 4 场景 **A=wire+symbol create PASS / B=idempotent skip PASS / C=requires wire_points PASS / D=auto coord hint PASS**；末轮 `compiled OK: route_to_port.py / route_hierarchy.py / route_gui.py`。但因 status=idle + 末轮 bug 报告未闭环 → 无 byte-faithful accepted gold → **B 档 synthesized**：gold `route_hierarchy.py` 按 trace API 面（dbOpenCV/dbFindInst/getMaster/getOrigin/getPinFigBBox/dbCrtSchWire/dbCrtSymbolPin/dbSaveCV + CV.getTerms/getLibName/getCellName + addTerm）合成，自包含、CLI 驱动。
- **L1-boundary**: 离线 Python，check.py 内嵌 fake pyAether 模块（确定性 seed 3 层 hidden B hierarchy），subprocess 真跑候选 on B，判分机无需真 Aether（§4.2 ✓）。
- **与既有区别**: HierJump-001（pulldown 菜单 sleGuiDescendRead 下钻）/ FindCircuitByPath-001（GUI 输入表单 dbOpenCV 链查 cell）→ 本案 **port 沿层次向上传播**（逐层加 pin + 连线到子实例 pin + sync symbol 加 pin），主题不同，非 near-duplicate。layout_aether 域 12→13。
- **hidden B**: 判分器内嵌，LIBB/TopB → inst U_MID → LIBB/MidB → inst U_LEAF → LIBB/LeafB(terms din/dout/vdd)，port=din，预期 path=[U_MID,U_LEAF]，结构性 ≠ A 的 drgqa_cmos_work/Rasbanklogic/R_SaCtrol/in_test。cross-input guard (n) 拦 A 专属 token。
- **check.py 15 条独立断言 k=15=k_check≥8**: ①zip 含 route_hierarchy.py≥800B ②py_compile ③import pyAether ④def find_inst_path/propagate_port_up/sync_symbol ⑤B 上 subprocess exit 0 ⑥stdout 含 PATH+U_MID+U_LEAF ⑦TopB sch 有 wire ⑧MidB sch 有 wire ⑨TopB symbol sympin=din ⑩MidB symbol sympin=din ⑪TopB sch+symbol 均 save ⑫MidB sch+symbol 均 save ⑬not-found 抛 RuntimeError ⑭无 A token 泄漏[cross] ⑮二次 run wire+sympin 签名一致(确定性)。
- **自验（local）**: gold → CHECK PASS 15/15 ✓；4 negatives 全 FAIL：empty_shell→(a) / print_only→(g)（passes a-f, fails wire，§4.9b 防御成立）/ core_deleted→(g) / naive_hardcode_A→(g)（§4.9c）✓；NEG_RC=4/4 ALL-FAIL。断言闸门 k_rationale=k_check=15≥8 GATE PASS ✓。
- **资产**: assets/{prompt.txt(U[0] verbatim+沙盒注)+task_brief.md(交付接口 route_hierarchy.py)+hidden_manifest.json} / reference={route_hierarchy.py(gold)+check.py+negative/{empty_shell,print_only,core_deleted,naive_hardcode_A}+negative_selftest.py}。jsonl_C 38→39 行，test field sha 6af1d02c3c21 == disk check.py ✓。
- **传输坑**: 无（纯文本资产，无 GDS/base64 腐蚀风险）。
- **ledger**: 已动 59：case 39 · parked 20 · claimed 0，layout_aether 12→13。
