# trace_deepread: r604 t2r9f (PDK QA sync_to_stable batch audit + archive)

- **user**: xinqiaoz
- **host**: hfeg0pkn002 (10.129.2.11)
- **session_file**: 1793581640305_t2r9f.messages.json (1.04MB, 241 msgs, 7 user turns)
- **match_count**: 457 (pdk:872; calibre:286; cmos:100; .gds:11)
- **domain**: physical_verify (PDK QA DRC deck sync tracking — pdkQaSystem)
- **旧 parked 理由**: "xinqiaoz PDK_QA calibre session (13 calibre uses); same pdkQaSystem codebase; pool saturation"
- **新判定**: 可造 — "pool saturation" 非真实排除标准（2026-11-15 令），xinqiaoz 是已知 produce-task 用户（r597 LdrFtypeZeroArchive / r603 DummyDeckMaskDiag），本 session 有独立 produce-task（归档+插入批次）。

## 真实任务（用户原话逐字）

- UI#1: `当前 /home/xinqiaoz/PDK_QA/pdkQaSystem/sync_to_stable 中的，还有哪些没有同步？`
- UI#2: `多值变量的确认没有同步，对吗？`
- UI#3: `你不应该看 yaml 文件，因为 yaml 文件可能没有更新，你得真实对比代码文件。`
- UI#4: `既然如此，也就是说，现在只有 B4 还未更新了，我的理解对吗？`
- UI#5 (核心 produce-task): `我们先把所有已经更新的批次归档，避免影响到我们的判断。`
- UI#6 (核心 produce-task): `我想插入一个新的批次，在 B4 之前，commit id 为 117b9ac。内容很简单，fix 了一个 bug。`
- UI#7: `ok`

## 真实工具链 + gold

- agent 用 run_approved_command(41) / editor(46) / read_files(23) / list_allowed_files(12) / search_codebase(5)
- **归档**（UI#5）：md5 比对 batch 快照 vs stable 代码 → 确认 B3 + drcDefinitionRule 已同步 → 建 `archive/B3_synced_20261102/`、`archive/drcDefinitionRule_synced_20261102/` → cp snapshots + letter.txt → 更新 `manifest.yaml`（B3 `replaced:true`+`replaced_date`、`order:[B3,B4]→[B4]`、加 archive 条目）→ 更新 `sync_state.yaml`（status/baseline_md5/replaced_date）→ 清理 `batches/B3/`
- **插入**（UI#6）：`git log/show 117b9ac` → 确认只改 `DrcValueCheck.py` 一行 → 计划在 B4 前插入新批次条目
- gold = 用户接受（UI#7 ok）

## B档 mock-behavioral reframe

- 源 manifest.yaml / sync_state.yaml / stable 代码路径在 xinqiaoz 私有 PDK_QA（沙盒不可达）→ asset_fidelity=synth
- 把「解析 sync 清单 + md5 比对 stable → 判定同步状态 → 归档已同步批次（产 archive 计划 + 更新 manifest/sync_state）→ 插入新批次」参数化为纯 Python3 `sync_batch_archive_plan.py <manifest.json> <stable.json> <out_report.json> [--archive-date YYYYMMDD] [--insert-batch id:commit:before_id:message]`
- JSON 输入（manifest: batches{files{path:md5}}/order/archive + stable: files{path:md5}/date），确定性 JSON 报告（sort_keys）

## case

- **task_id**: EDA-Eval-DesignFlow-SyncBatchArchivePlan-001
- **输入 A**（可见）：manifest_A（order[B3,B4]，B3 1 文件 md5 匹配 stable，B4 1 文件不匹配）+ stable_A
- **hidden B**（主判分）：manifest_B（order[B2,B5,B6]，B2 2 文件匹配、B5 2 文件匹配、B6 1 文件不匹配）+ stable_B → 归档 B2+B5、order→[B6]
- **hidden B2**（cross-input guard）：manifest_B2（order[X1,X2,X3]，仅 X1 匹配）→ 归档 X1、order→[X2,X3]
- **insert 测试**：--insert-batch B3fix:117b9ac:B6:fix... → order=[B3fix,B6]
- **14 条 a-n**：结构2(a-b:zip+py_compile/B exit0+JSON)+B 同步状态3(c: B2/B5 synced B6 pending)+归档2(d: 2 entries / e: order[B6])+manifest 更新2(f: archive list / i: replaced true+date)+sync_state(g)+archive_dir 命名(h)+反硬编 A(j: 无 B3/B4)+baseline_md5 数据驱动(m)+确定性(n)+B2 cross-input(k)+insert(l)
- 自验 ref 14/14 PASS✓；3 neg(empty/print_expected/all_synced=deleted_core)全 FAIL✓ NEGATIVE_SELFTEST ALL-FAIL-OK✓；§4.9 三假全 FAIL✓；k=14≥8✓
