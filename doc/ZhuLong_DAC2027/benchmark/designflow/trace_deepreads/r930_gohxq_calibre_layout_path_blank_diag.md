# r930 deepread — gohxq (Calibre DRC "Layout Path cannot be blank" 诊断)

- **session**: `1795228793423_gohxq.messages.json`
- **user / host**: felixw @ hfeg0plg54 (10.129.35.73)
- **match_count**: 29 (physical_verify: drc 430 / calibre 158)
- **size**: 164785 B, 10 msgs, 1 user turn
- **claim**: C ledger `trace_ledger_C.tsv`
- **case_id**: `EDA-Eval-DesignFlow-CalibreDrcLayoutPathBlankDiag-001`

## 真实任务（USER msg 0，全文 1 轮）

felixw 问：跑 `calibre -gui -drc -runset drcRunset -batch` 报 `ERROR: Layout Path cannot be blank`，但 `drcRunset` 第 4 行明明设了 `*drcLayoutPath`，为什么？

附了：
- `drcRunset`（G4C PDK，38 行，`*drcLayoutPrimary: test1` + `*drcLayoutPath: /proj/drgqx/V0/agentdir/felixw/DRC_test/test1.gds`，`cmnRunHostType:remotelsf`，`cmnRunHyper:1`，`cmnNumTurbo:16`）
- `parent_drcRunset`（父目录同名 12 行变体）
- `calibre_drc_output.log`（VCO env 不匹配：`runtime VCO=aok` / `software_tree VCO=aoi`）
- `calibre_stdout.log`（一次成功直接 `calibre -drc -hier -turbo 16` 调用）
- `.drcRunset.swp` / `.drcRunset.swo`（VIM swap 残留）

## Gold 答案（msg 9，assistant）

5 根因 + 4 步修复 + 侧注：

1. **相对 `-runset` 路径 + /proj→/ai_sandbox 符号链接**：`-runset drcRunset` 是相对名，/proj 在 sandbox 被 symlink 到 /ai_sandbox，calibre 解析到错误副本
2. **VIM swap 文件污染**：`.drcRunset.swp`/`.swo` 残留，编辑器未正常退出，runset 解析被 swap 干扰
3. **`-gui -batch` viewer-check quirk**：`-gui` 启动 viewer，但 `*drcLayoutGetFromViewer: 0` 让 viewer 不供应 layout，path 必须来自 runset；`-batch` 模式下 viewer 检查路径与预期不一致
4. **两份 drcRunset 混淆**：`debug/drcRunset` 与 `DRC_test/drcRunset` 内容不同，相对路径解析可能选错副本
5. **GDS 权限/锁**：GDS 文件被锁或权限不足（次要）

修复 4 步：①用绝对路径 `-runset $(pwd)/drcRunset` ②删 swap `rm -f .drcRunset.swp .drcRunset.swo` ③去 `-gui` 改 `calibre -drc -runset <abs> -batch` ④确认 GDS 权限/无锁

侧注：VCO env mismatch（`runtime=aok` vs `software_tree=aoi`）需 source 正确环境；`calibre_stdout.log` 里成功的直接 `calibre -drc -hier` 证明 GDS+rule 本身 OK，问题在 runset 解析+环境。

## Reframe 决策

真实任务=单轮诊断问答（无代码产出）。reframe 成**自动化根因诊断器** `calibre_layout_path_diag.py`：读 fixture 目录（runset+parent+stdout/output log+swp/swo）+ spec，输出结构化 JSON root-cause 报告。

7 类根因映射自 gold 5 根因：
- `missing_layout_path`（B runset 缺 `*drcLayoutPath`，触发器）← gold 根因 1/3/4 的共同后果
- `missing_layout_primary`（B runset 缺 `*drcLayoutPrimary`，关联触发器）
- `swap_file_corruption` ← gold 根因 2
- `duplicate_runset` ← gold 根因 4
- `viewer_quirk` ← gold 根因 3
- `relative_path` ← gold 根因 1
- `env_mismatch` ← gold 侧注 VCO

## B vs A 反硬编码

| 维度 | A (env_A, felixw G4C) | B (hidden, G5) |
|---|---|---|
| PDK gen | G4C | G5 |
| rule file | v0/current/ | v1/current/ |
| CustomizationFile | cxmtG4C | cxmtG5 |
| `*drcLayoutPath` | 有 | **无**（触发器） |
| `*drcLayoutPrimary` | 有 (test1) | **无** |
| cmnRunHostType | remotelsf | local |
| cmnRunHyper | 1 | 0 |
| cmnNumTurbo | 16 | 4 |
| primary_cell (spec) | test1 | audit_cell_v2 |
| layout_path (spec) | /proj/drgqx/.../test1.gds | /tmp/audit_run/audit_cell_v2.gds |
| VCO runtime | aok | **aoi**（反向） |
| VCO software_tree | aoi | **aok**（反向） |
| swap host | hfeg0plg54 | auditbox |
| swap user | felixw | audituser |

VCO 配对反向是关键反硬编码点：A-hardcode 的诊断器会把 runtime 写成 aok，但 B 要求 aoi — tooth (m) 据此判 FAIL。

## 判分（check.py, k=15 teeth）

(a) zip+py_compile / (b) --help 无 traceback / (c) B exit0+JSON / (d) diagnosis / (e) primary_cell / (f) root_causes≥5 / (g) 5 字段类型 / (h) missing_layout_path critical / (i) missing_layout_primary / (j) swap_file_corruption / (k) duplicate_runset / (l) viewer_quirk / (m) env_mismatch aoi/aok / (n) 反硬编码 A markers / (o) 3-seed 确定性

## 自验

- ref solve PASS 全 15 teeth
- 4 negatives (empty_shell/only_print/hardcoded_A/no_env_parse) FAIL 各异 teeth
- §4.9 (a)(b)(c) 全 FAIL
- 3-seed 确定性 PASS
