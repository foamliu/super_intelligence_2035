# deepread: vhb6i — pyAether port 性能根因诊断 Q&A (cross-language perf-porting)

- session: `1789717866261_vhb6i.messages.json`
- user/host: rongjiez @ hfeg0pkn005 (10.129.2.14, NFS-shared; also on hfeg0plg54/58/52/pjn200)
- mc: 133, domain: schematic_netlist (shard D)
- trace: 26 msgs / 1 real user input (msg#0), agent=lead, 217KB
- 旧判定: parked 2026-11-05 (D) "root-cause Q&A ... analysis not production"; C 亦 parked 2026-11-09 "hard to make 8+cond check"
- 11-15 revival mandate: diagnosis-Q&A 子型已合法化 (r785 LvsPrfLogicDiag / r797 FinesimPstlayCrashDiag / r798 VblhhXStateDiag) → 复活为 cross-language perf-porting 根因诊断 Q&A (D域新子型)
- 交付 case: `EDA-Eval-DesignFlow-PyAetherPortPerfDiagQA-001` (r801)

## trace 逐字（U#0）

> @cxmt_getLatchFFCellList_t copy.py @cxmt_getLatchFFCellList.il  cxmt_getLatchFFCellList.il是virtuoso的skill脚本代码，实现了对电路中抽取latch，cxmt_getLatchFFCellList_t是把skill脚本翻译为aether的pyaether脚本，现在功能没问题，但是同一个电路，pyaether脚本运行时间远远超过skill脚本时间，这是什么原因

## 素材可达性

- ssh 10.129.2.14 (e0031982 公钥) ✓
- `/home/rongjiez/.cline/data/sessions/1789717866261_vhb6i/1789717866261_vhb6i.messages.json` (217KB) scp 到 .75 workdir
- 原脚本均在磁盘: `/home/rongjiez/jira_dev/AICAD-16/scripts/cxmt_getLatchFFCellList_t.py` (150 行/7463B) + `cxmt_getLatchFFCellList.il` (206 行/7983B)
- (`cxmt_getLatchFFCellList_t copy.py` 已不在磁盘；canonical `cxmt_getLatchFFCellList_t.py` 即被诊断的慢脚本)

## trace 真实形态

单用户意图轮。agent msg#1 read_files 慢脚本 → msg#3/5 list+read 两份 .py → msg#7/11 search_apis/get_api_details (aeMember/aeCons/aeAppend1/aeCar/aeCadr/etMakeTable/etSort/etPrintf/...) 核对 pyAether API 语义 → msg#13/15/17/21 editor 写优化版 `cxmt_getLatchFFCellList_optimized.py` → msg#25 gold (3626 字符)。

## 金标准（assistant msg#25）：5 类根因（按影响从大到小）

1. **`ae.cons()` / `ae.append1()` 在 Python 里是「拷贝整个列表」**(O(n))，非 SKILL 的 O(1) cons cell。`cxmt_getLoopStructureCellView` 的 O(n²) 双循环里反复 `ae.cons(...)` → 总体接近 **O(n⁴)**；同理 `cxmt_getFlatLatch_getHireCellName`。⇒ `list.append()`。
2. **`ae.member()` 在最内层循环对「不断变长的列表」线性扫描**，每次先构造新列表 `[a,b]`，对长到 O(n²) 的 `usedInstList` 线性查找又叠一层 O(n)。⇒ `set` + `in`。
3. **emy 对象属性访问都是 Python→Aether 桥接调用**（`instId.name`/`.libName`/`.cellName`/`instTermId.net.name`/`.direction`），O(n²) 循环里每条迭代多次；`stdcell/TECHLIB/INV` 过滤条件对同一外层实例重复计算 n 次。⇒ 预计算每实例 flag。
4. **`ae.etMakeTable` 表访问也是桥接调用**，且用 emy 对象作 key。⇒ 原生 `dict`（key 用 name）。
5. **次要项**：`ae.etSort`→`sorted()`、`ae.strcat`→`+`/f-string、`ae.car`/`ae.cadr`→`x[0]`/`x[1]`、`re.search(r"^lat"...)`→`str.startswith(("lat","ff","rs"))`；另 `ae.dbOpenCV` (line 128) 已 deprecated 应 `dbOpenCVByType`；`ae.dbCloseCV` 位置留到双循环之后（SKILL 原版建完表立即 close）。

## 反模式调用点（slow_port_A.py 150 行）

`ae.cons`×4 (L81,86,102,109) · `ae.append1`×3 (L33,41,44) · `ae.member`×8 (L100,104,106,108,117,120,138,143) · `ae.etMakeTable`×2 (L64,74) · `ae.etSort`×2 (L47,49) · `ae.strcat`×4 · `ae.car`/`ae.cadr`×2 (L29,30) · `ae.dbOpenCV` deprecated (L128) · emy attr 访问 23+ 处 · `re.search(r"^lat"/"^ff"/"^rs")` (L31)。

## case 合成（synth_deck 模式）

- asset A (visible): `slow_port_A.py` (150 行 verbatim) + `skill_original_A.il` (206 行 verbatim) + `question_A.txt` (verbatim U#0) + `task_brief.md`
- hidden B: `slow_port_B.py` (150 行, identifier-renamed 变体, 零 A 标识符重叠; 用户自定义标识符 + 区分性字符串字面量全重命名; **emy 属性 `.libName`/`.cellName`/`.name`/`.direction`/`.purpose`/`.instances`/`.instTerms`/`.terminals`/`.net` 保留**因属 Aether API 且为被诊断对象; `ae.*` API 调用名保留因是被诊断对象)。rename map 关键: 用 `(?<![\w.])` 负向后顾保护 `.attr` 属性访问不被误改 (libName/cellName 同时是变量名和属性名)。
- candidate_ref.py: 通用静态分析器 (无硬编码标识符), 行级扫描 `ae.cons/append1/member/etMakeTable/etSort/strcat/car/cadr/dbOpenCV` 调用 + emy 属性访问 + `re.search(r'^...')`, 跟踪 for 循环栈判定 in_loop, 按 SEVERITY_ORDER 聚合 6 类 root_cause + minor_findings(regex→startswith) + deprecated_apis, cited_identifiers 从源码提取 (ae.* + def 名 + emy attr) → 输出 9 顶层键 JSON。
- check.py: 12 断言 a-l (①zip含candidate ②py_compile ③>=8必需键 ④list_copy_O_n ⑤linear_scan_member ⑥emy_bridge_calls ⑦etMakeTable_bridge+deprecated ⑧rank-1=list_copy_O_n&in_loop ⑨native_replacement正确原生构造 ⑩anti-hardcode不含A专属token ⑪cited全grounded于B ⑫3-run md5确定性)。
- 自验: ref 12/12 PASS + 3neg (fake_empty/fake_print_only/fake_core_deleted) 全 FAIL distinct labels NEG_RC=0 + §4.9 三退化全FAIL + candidate on A 同样检测 71 反模式 rank1=list_copy (generic 确认) + embedded test byte-identical to reference check.py + k_rationale==k_check==12≥8 GATE PASS。
- D.jsonl 460→461。📊 覆盖率 446→447/2907 mc≥10=15.4%。
