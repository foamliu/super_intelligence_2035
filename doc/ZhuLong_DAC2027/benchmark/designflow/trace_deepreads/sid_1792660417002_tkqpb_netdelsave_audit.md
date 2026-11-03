# 深读笔记 — sid 1792660417002_tkqpb (colinxu / hfeg0pgn041)

- **trace**: colinxu @ hfeg0pgn041, session 1792660417002_tkqpb, 250 msgs / 12 user_input, mc=257
- **tools**: cellview 480 + schematic 296 + virtuoso 42 + dbCreateRect 28 + dbGet 24 + dbCreateInst 2 + pyAether 3 (per summary.tsv)
- **user turns** (verbatim):
  - UI#0 「现在帮我查看打开的项目是哪个？」= 查询弃
  - UI#30 「现在打开的是哪个cell？」= 查询弃
  - UI#34 「帮我找到TESTPIN2」= 操作
  - UI#63 「帮我有哪些API 可以删处TESTPIN这个pin」= 问 API
  - UI#71 「帮我删了它」= 提出需求(删 pin/net)✓ 但过薄
  - UI#158 「分别使用各种删除api产生脚本试试删掉它看看」= 提出需求(用各种删除api试)✓ A-档 seed 候选
  - UI#187 「我修改了policy，现在再试试能否删除他们？」= 用户给出修复方向(改 policy)→ A-档 disqualify
  - UI#216 「帮我用多种api进行保存」= 提出需求(多种 save api)✓
- **A-档判定**: UI#187 用户给出修复方向(改 policy)→ 整轮不纯需求；且 live Virtuoso+私有 drjpa_analog OA 库沙盒无权 → A-档 disqualified → **B-档 synthesized L1-boundary**

## assistant 工具链 (124 tool_use)
- RAG search_apis: "delete pin/terminal/net"、"save cellView"、"dbCheckAndSaveDesign"
- RAG get_api_details: dbDeleteObject / dbDeleteAllNet / dbDeleteEmptyNet / dbSave / geSave / schHiSaveCellView / dbCheckAndSaveDesign / schHiCheckAndSave
- SandBox run_code (lang=skill, host=virtuoso): 在 drjpa_analog/AG_AnalogBankBuf/schematic 上 live 真跑

## live 实验结果 (ground truth)
**cellview**: drjpa_analog / AG_AnalogBankBuf / schematic, mode="a", isEditable=nil
**delete-net API**:
| API | live 结果 | 结论 |
|---|---|---|
| dbDeleteObject(net) | t, TESTPIN removed | ✓ 通用 DB 删除, net 的 terminal auto-del + instTerms auto-disconnect |
| dbDeleteAllNet(cv) | t, before=1 after=0 | ✓ 但 destructive (删 ALL nets) |
| dbDeleteEmptyNet(net) | t (空 net 时) | ✓ 仅删空 net (无 instTerm/fig) |
| dbDeleteNetByName | (search 命中) locate-by-name + dbDeleteObject | ✓ targeted |
| schDelete(net) | nil, TESTPIN 仍在 | ✗ schDelete 不删 net (只删 schematic/symbol figure) |
| leDeleteNetByName | (layout 域 API) | ✓ layout 域 targeted |

**save API**:
| API | live 结果 | 结论 |
|---|---|---|
| dbSave(cv) | t | ✓ 通用 save (write/append mode) |
| dbSave(cv,lib,cell,view) | t | ✓ save-as |
| geSave() / geSave(win) | t | ✓ window-based |
| schHiSaveCellView() | t, "INFO (SCH-1117) saved" | ✓ schematic canonical save |
| schHiCheckAndSave() | (RAG: check+save schematic) | ✓ schematic check+save |
| dbCheckAndSaveDesign(cv) | *Error* undefined function | ✗ 环境无此函数 |

**API signatures (get_api_details)**:
- `dbDeleteObject(d_object) => t/nil` — deletes shapes/nets/terminals/instTerms/pins/instances/...; net→terminal auto-del + instTerms disconnected
- `dbDeleteAllNet(d_cellView) => t/nil` — deletes ALL nets
- `dbDeleteEmptyNet(d_netId) => t/nil` — deletes net not associated with other objects
- `dbSave(d_cellview [d_destCV|t_lib t_cell t_view]) => t/nil`
- `schHiSaveCellView() => t`
- `schHiCheckAndSave() => t/nil` — schematic only
- `dbCheckAndSaveDesign` — undefined

## 合成 (B-档)
**case**: EDA-Eval-DesignFlow-NetDelSaveAudit-001 (layout_virtuoso, L1-boundary)
**主题**: SKILL net-deletion + cellview-save API 能力审计 + 安全策略选择
**与既有区别**:
- AddCellPin-001 (hxh3n, colinxu) = layout dbCreatePin **创建** pin + API 序列提取
- SchPinPlanAudit-001 (po4s1, colinxu) = schematic schCreateSymbolPin **创建** symbol pin + plan 审计
- 本案 = net **删除** + save API **能力枚举 + 安全策略选择** (destructive/works_on_net/view_restriction 分类 + connected/empty net 决策) — 主题/断言独立

**候选交付**: `net_del_save_audit.py` (Python3 stdlib) 读 cv_state.json → 产 audit_manifest.json (delete_apis 6 + save_apis 6 + delete_strategy + save_strategy + verdict)

**A** (visible): drjpa_analog/AG_AnalogBankBuf/schematic, mode=a, 1 net TESTPIN(empty instTerms=0) → del=dbDeleteEmptyNet, save=schHiSaveCellView, verdict=EMPTY_NET_SCHEMATIC
**hidden B**: drjpa_analog/AG_AnalogDCCore/**layout**, mode=w, 12 nets, target VDD_NET(instTerms=3 connected) → del=dbDeleteObject(auto-disconnect), save=leHiSave, verdict=CONNECTED_DISCONNECT_LAYOUT
**hidden B2** (destructive trap): AG_AnalogMux/schematic, 50 nets, target CLK(empty) → must NOT dbDeleteAllNet (destructive, 50 nets), del=dbDeleteEmptyNet
**hidden B3** (schDelete trap): AG_AnalogBias/schematic, 8 nets, target BIAS(instTerms=2 connected) → must NOT schDelete (works_on_net=false), del=dbDeleteObject

**check.py 17 条断言 (a)-(q), k_check=17 ≥8 GATE PASS**:
①(a)zip+py_compile+manifest_A ②(b)manifest_A 8 顶层键+schema_version 0.1 ③(c)delete_apis 6 API 齐全+签名 ④(d)dbDeleteAllNet destructive=True safe=False ⑤(e)schDelete works_on_net=False safe=False ⑥(f)dbDeleteEmptyNet works_only_if_empty=True ⑦(g)save_apis 6 API 齐全+签名 ⑧(h)dbCheckAndSaveDesign available=False ⑨(i)schHiSaveCellView view_restriction=schematic ⑩(j)A target TESTPIN empty + nets_total=1 ⑪(k)A del 策略 empty→dbDeleteEmptyNet/dbDeleteObject + needs_disconnect=False + rejected dbDeleteAllNet+schDelete ⑫(l)A save schematic→schHiSaveCellView + rejected dbCheckAndSaveDesign ⑬(m)A verdict=EMPTY_NET_SCHEMATIC ⑭(n)cross-input guard: hidden B(LAYOUT,VDD_NET instTerms=3)→dbDeleteObject+needs_disconnect=True+leHiSave+verdict CONNECTED_DISCONNECT_LAYOUT ⑮(o)destructive guard: B2(50 nets,empty)→primary≠dbDeleteAllNet+rejected dbDeleteAllNet destructive ⑯(p)schDelete guard: B3(BIAS instTerms=2,schematic)→primary dbDeleteObject≠schDelete+rejected schDelete works_on_net=false+verdict CONNECTED_DISCONNECT_SCHEMATIC ⑰(q)确定性 B 3 次 md5 一致

**自验**: ref PASS 17/17 ✓; 5 neg(fake_empty→a / fake_print_expected→c(catalog empty) / fake_core_deleted→k / naive_always_destroy→k / naive_always_schdelete→k) 全 FAIL NEG_RC=0 ✓; §4.9(a)(b)(c)+2 naive 全 FAIL; test==disk check.py roundtrip OK (13028B)
