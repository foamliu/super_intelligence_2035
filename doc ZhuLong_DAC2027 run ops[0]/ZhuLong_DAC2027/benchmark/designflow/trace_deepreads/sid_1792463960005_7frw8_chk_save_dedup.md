# trace deepread — sid 1792463960005_7frw8 (zqzhan, hfeg0pkn005, mc=371, layout_aether)

- **session**: `/home/zqzhan/.cline/data/sessions/1792463960005_7frw8/1792463960005_7frw8.messages.json` (1.93MB, 234 msgs, 9 real UI)
- **host**: 10.129.2.14 (hfeg0pkn005), scp 经 eda_flow run_commands(e0031982 身份) 到 .75 workdir
- **domain**: layout_aether（Aether/CXMT cellview Custom Check-and-Save .hist 审计机制，cellview 级，layout/schematic 通用）
- **选档**: A-档 seed UI#0 逐字「帮我看一下Aether里面，Custom Check and Save function called.对schematic进行check save，但是看log只有save」= 纯需求（用户只给现象，未给根因/修复）；但末轮无 byte-faithful 单一接受产物（用户 UI#6 给出可工作 log 后 UI#7/UI#8 转总结/交接）→ A-档 disqualified → **B-档 synthesized**。

## 真实机制（agent 5 轮迭代定位）
- 菜单/toolbar 映射在 `CXMThiSHBarIconRemap.il::CXMThiSHSchematicBarIconRemap`：`schHiCheckAndSave` → `CXMTseSHCheckAndSave`，`_schHiSave` → `CXMTseSHhiSave`。
- `CXMTseSHCheckAndSave()`（line 57-98）：`CXMTdbMakeReadOnlyCv` 通过 → `printf("Custom Check and Save function called\n")` → `CXMTutAddSaveHistory(?cv geGetEditCellView() ?comm "Checkandsave")` → 预检（noteSymbol designer / R0 inst name）→ 调原生 `schHiCheckAndSave()`（内部 check + dbSave）。
- `CXMTseSHhiSave()`：`CXMTutAddSaveHistory(?comm "Save")` → `_schHiSave()`。
- **根因**：`CXMTutAddSaveHistory`（line 336-428）去重逻辑读 `.hist` 最后一行作 `prior`：`when(puser == username && ptime) { delta=compareTime(ctime ptime); when(delta<time_interval) flag=nil }`。**只比 user + delta，不看 comm**。time_interval=600s（schematic/layout）。
- **bug 场景**：用户先 Save（写 `Save`，last_user=T）→ 10min 内 Check and Save → `CXMTutAddSaveHistory(?comm "Checkandsave")` 被读最后一行（Save）+同 user+delta<600 → `flag=nil` → `.hist` 不写 Checkandsave → 审计只看 Save。CIW 仍打印 "Custom Check and Save function called"（check 真跑了），仅审计条目被丢。
- **debug 症状原文**（UI#3）：`Debug: not print user sczhang,sczhang, time delta 171, 2026/10/20 10:57:21	2026/10/20 10:54:30.`（delta 171<600 被抑制；后两行 223/230s 同）。
- **修复方案B**（用户选 UI#1「方案B」）：去重条件加 `pcomm == comm` + 捕获 `pcomm = nth(5 tmp_s)` → 只有同 user+同 comm+最近才抑制；不同 comm 互不抑制。agent 因 `/proj/shdc/cad/skill` 不在 writable scope，给用户贴改动（变量列表加 `pcomm` / 第二次读捕获 `pcomm` / 条件加 `&& pcomm == comm`）。
- **接受**（UI#6）：用户贴可工作 log `drcpa_digital   R_trimSanpDlyA_LP   schematic   sczhang   Oct_20_12:37:46_2026   Checkandsave` → 「这样应该就是ok了吧」。

## .hist 格式（ground truth，来自 UI#6）
`<lib>  <cell>  <view>  <user>  <timestamp>  <comm>`（6 字段，空白分隔）
timestamp: `Mon_DD_HH:MM:SS_YYYY`（`Oct_20_12:37:46_2026`），SKILL `buildString(parseString(nth(...) "_") " ")` → `compareTime`。

## 合成（L1-boundary，离线 Python3）
真 L2（live Aether + CXMT SKILL + /proj/shdc/cad/skill）沙盒不可复现 → L1-boundary：`chk_save_hist_dedup.py`（stdlib）。
- parse `.hist`（6 字段 + epoch via calendar.timegm UTC，跳 # 注释/空行）
- 模拟双守卫：BUGGY(comm-blind: puser==user && delta<interval) vs FIXED(comm-aware: + pcomm==comm)
- per-op diagnosis: bug_triggered / correct_dedup / delta_exceeded / different_user / no_prior / written
- 输出方案B SKILL patch（let pcomm + pcomm=nth 捕获 + pcomm==comm 条件，非 buggy 版）
- 核心坑：comm-blind 去重把不同类型操作误抑制 → bug_triggered 必须与 correct_dedup(同 comm)区分；naive「全抑制=bug」/「全 WRITTEN」/「hardcoded B」全 FAIL。

## 自验
- ref PASS 15/15（k_check=15=k_rationale≥8 GATE PASS）
- 5 neg FAIL: empty_stub→(a) / always_print→(e)+(o) / no_comm_logic→(h) / hardcoded_A→(d) / core_deleted→(g)
- §4.9 (a)空壳(b)只print(c)删核心 三假提交全 FAIL
- A/B/B2 规模/取值/结构全不同（§4.1 ✓），判分机无需 live Aether（本地纯 Python3）

## 案件
- task_id: EDA-Eval-DesignFlow-ChkSaveHistDedup-001
- ledger: 117 (case 53 · parked 64), jsonl_C 52→53, layout_aether 17→18
