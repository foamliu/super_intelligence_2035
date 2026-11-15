# c9hdy 深读笔记 — pyAether vs SKILL 脚本结果不一致/NoneType debug Q&A

> trace: `1789709270496_c9hdy` · rongjiez@hfeg0plg98(10.129.8.230) · mc35 · schematic_netlist
> r612 peek note: "debug pyaether vs skill script result mismatch/NoneType (debug, not produce)"
> r716 ssh peek (via eda_flow .75 workdir) — 30 msgs, verbatim user utterances + 3 scripts captured

## 用户逐字原话（trace U#0/U#14/U#18/U#26）

- **U#0（主问题，A-faithful 任务说明候选）**：
  `@cxmt_getLatchFFCellList.il @cxmt_getLatchFFCellList.py cxmt_getLatchFFCellList.il是virtuoso的一个脚本，实现了获取电路中可能的FF/Latch cell list，cxmt_getLatchFFCellList.py是把这个skill脚本翻译成aether的pyaether脚本，但是现在pyaether脚本跑出来的结果和skill的结果不一样，甚至有时会直接报'NoneType' object is not iterable，输出文件是空的，请你帮我看下问题出在哪里，先不要直接修改我的文件`
- U#14: `问题1和2具体怎么修改`
- U#18: 贴 traceback — `ae_load_utils.py line 59 exec(fh.read())` → `<string> line 77 IndentationError: unexpected indent`（`instPinNet_table[instId]["input"] = []` 行缩进错误）
- U#26: `@cxmt_getLatchFFCellList_t.py 这是最新的脚本，之前很多不能跑的电路可以跑了，但是我发现有的电路会报Object invalid，可能是哪里出了问题，先不要修改我的代码`

## 脚本（已抓到 .75 workdir，原路径 /home/rongjiez/jira_dev/AICAD-16/scripts/）

- `cxmt_getLatchFFCellList.il` (206 行 SKILL): `procedure(cxmt_getLatchFFCellList)` + 3 辅助 procedure（`cxmt_getLoopStructureCellView` / `cxmt_getFlatLatch_getHireCellName` / `isPossibleFlatLatch`）。功能：从当前 cellview 递归收集所有用到的 lib/cell，按名字匹配 `^lat/^ff/^rs`（hierarchy STD）或 `LAT/FF/SR/RS`（possible flatten），对 possible-flatten 调 `cxmt_getLoopStructureCellView` 找组合逻辑环路（inst1.input∩inst2.output ∧ inst1.output∩inst2.input）或 `isPossibleFlatLatch`（pin 名含 latch-pin + TECHLIB n/p transistor），输出 `*_Latch_FF_RS.list`。
- `cxmt_getLatchFFCellList.py` (153 行 pyAether): .il 的翻译，`#Convert by empyrean WenYuJia 20240920`。用 `pyAether as ae` + `ae.car/ae.cadr/ae.cons/ae.append1/ae.etSort/ae.etOutFile/ae.etFprintf/ae.dbOpenCVByType/ae.dbGetAnyInstSwitchMaster` 等 ae.* 包装。`cxmt_getLoopStructureCellView` 用 `instData = {}` keyed by `id(obj)` 代替 SKILL `makeTable` keyed by instId。
- `cxmt_getLatchFFCellList_t.py` (150 行): U#26 的"最新版"，修了很多能跑的电路，但仍报 Object invalid。

## bug 诊断（候选 v2 case 的 diagnosis 维度）

**结果不一致根因**：
1. **`cxmt_getFlatLatch_getHireCellName` 递归去重语义差**：SKILL `!member(list(libName cellName) cellNameList)` 用 list 相等；py `ae.member([instId.libName, instId.cellName], cellNameList)` 调 ae.member — ae.member 对 list-of-list 的相等判断可能与 SKILL `member` 不一致（ae.member 是 SKILL member 的 SWIG 包装，但 Python list == 比 SKILL list equal 语义可能不同），导致去重漏/重，cellNameList 内容不同 → 后续 stdLatch/flatLatch 集合不同。
2. **`cxmt_getLoopStructureCellView` instPinNet 收集差**：SKILL `foreach(instId setof(obj cvId_target~>instances obj~>purpose != "pin"))` + `if(length(instId~>instTerms)>1`；py `for obj in cvId_target.instances: if obj.purpose=="pin": continue; if len(obj.instTerms)<=1: continue` — 逻辑等价，但 py 用 `id(obj)` 做 dict key，SKILL 用 instId 对象做 table key；若同一 obj 在不同遍历中 id 不稳定（SWIG proxy 重新包装），instData 可能丢条目。
3. **`ae.car`/`ae.cadr` 返回 None 链**：若 `cellNameList` 因去重 bug 混入非 list 元素（如 string），`ae.cadr(libcell)` 返回 None → `str(cellName).upper()` = "NONE"（不报错但不匹配）→ 该 cell 被静默跳过 → flatLatch 漏。

**NoneType 'object is not iterable' 根因**：
4. **`for obj in cvId_target.instances` 当 `cvId_target` 为 None-like**：py `cvId_target = ae.dbOpenCVByType(...)` 若返回 None，`if cvId_target:` 守卫住了；但若 ae.dbOpenCVByType 返回一个"truthy 但 .instances 为 None"的对象（cellview 打开失败但返回占位），`for obj in cvId_target.instances` → `NoneType is not iterable`。SKILL `if(cvId_target then` 同守卫，但 SKILL `cvId_target~>instances` 对失败 cellview 返回 nil，`foreach` 对 nil 不迭代（SKILL 容忍 nil），py `for x in None` 抛异常 — **SKILL nil-tolerant vs Python None-intolerant** 是翻译类脚本的核心 mismatch。
5. **`obj.instTerms` 为 None**：`for instTermId in obj.instTerms` 若该 obj 无 instTerms（如 pin-only inst），SKILL `foreach` 容忍 nil，py `for x in None` 抛 NoneType-iterable。

**Object invalid 根因（U#26 _t.py）**：
6. `ae.dbGetAnyInstSwitchMaster(instId, "schematic")` 对已关闭或无效 inst 返回 invalid obj，后续 `viewId.instances` 访问 invalid → Object invalid。SKILL `viewId=dbGetAnyInstSwitchMaster(instId "schematic")` + `if(viewId then` 守卫，但 py 若 viewId 是 invalid-but-truthy 同样中招。

**IndentationError（U#18）**：纯缩进 bug（agent 已用 editor 修，ASST 21），非语义。

## 🚨 近重判（r716 peek 后）：c9hdy 与已交付 9imo1 = 同概念近重，**不应再造 case**

r716 ssh peek c9hdy verbatim U#0 后，与 r709 已交付的 **LatchFFDiagnoseQA-001（9imo1）** 对比：

| 维度 | c9hdy (本 trace) | 9imo1 (已交付 r709) |
|---|---|---|
| session | 1789709270496_c9hdy | 1789647055494_9imo1 |
| user/host | rongjiez@hfeg0plg98 | rongjiez@hfeg0plg54 |
| **U#0 逐字** | `@cxmt_getLatchFFCellList.il @cxmt_getLatchFFCellList.py ...pyaether脚本跑出来的结果和skill的结果不一样...NoneType...请你帮我看下问题出在哪里` | **逐字相同**（r709 流水记录 U#0 原句一致） |
| 附件脚本 | cxmt_getLatchFFCellList.il + .py（同 3 脚本） | 同 |
| 核心意图 | pyaether vs skill 结果不一致/NoneType debug | **同** |
| 区别 | U#26 多一条 `@cxmt_getLatchFFCellList_t.py ...有的电路会报Object invalid`（_t.py 版 Object invalid facet） | U#26 是 `现在跑出结果一样但速度慢`（性能 facet） |

**结论**：c9hdy 与 9imo1 是**同一用户、同一脚本、同一核心 debug 意图**的不同 session（rongjiez 在两台机上各跑一次同主题会话）。核心意图（pyaether vs skill 结果不一致/NoneType 诊断）已被 LatchFFDiagnoseQA-001 (r709) 覆盖。c9hdy 的区别仅 U#26 Object invalid facet，不足以支撑独立 case（同概念簇 facet 相邻，非新概念，类 r692 jackliu vblh-fighting / r693 e0039602 stdcell 簇）。

**处置**：c9hdy 标 **same-concept near-dup of 9imo1 (LatchFFDiagnoseQA-001, r709)**，**不从 prototype-proven 造题**。pool_reaudit_D.tsv 的 c9hdy 行「prototype-proven 立即可造 套 #254 v2 同族 9imo1」应订正为「same-concept near-dup of delivered 9imo1，下线造题、保留 triage 备注」。交 @A dedup 通道（rongjiez cxmt_getLatchFFCellList 簇 = 9imo1 + c9hdy 2 session 1 概念）。

**prototype-proven 剩余可造更新**：原 8 remaining（c9hdy/14921/636qr/i33cs/6sxh5/vwgeo/8c5jw + 1 需源），c9hdy 下线 → **7 remaining**（14921/636qr/i33cs/6sxh5/vwgeo/8c5jw + 1 需源）。下轮优先 14921（netlist-grounded circuit-id 套 #238 v2 同族 l2vvy）或 636qr（code-grounded refactoring-summary 套 #254 v2）。

## 进度

- r716: trace peek 完成（verbatim 问题 + 3 脚本抓到 .75 workdir + 本深读笔记落 workspace）。**peek 揭示 c9hdy = 9imo1 同概念近重 → 下线造题**（避免重复 case，dedup 收益）。case 合成 defer 至 r717+，换 14921 或 636qr。
- 下轮第一件事：选 14921 或 636qr（非近重），ssh peek trace → 合成 assets + check.py + REF + negs + 自验 → 落 EDA-Eval-DesignFlow_D.jsonl。
