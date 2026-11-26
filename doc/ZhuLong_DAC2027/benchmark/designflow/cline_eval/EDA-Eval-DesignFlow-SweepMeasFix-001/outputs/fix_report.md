# fix_report — `summarize_meas.sh` 修复说明

## 1. 问题现象

在给定输入 `meas_result_by_corner_1021/`（单 sweep 数据集：仅 `corner0/` 存在 8 个 `.mt0` 结果 `IsmOscTestSweep_s0..s7.mt0`，`corner1/2/3` 目录缺失）上运行**原始** `summarize_meas.sh`：

- 脚本正确处理完 `corner0`（其中 s7 被判为 FAIL）后，继续处理 `corner1`；
- 对 `corner1` 执行 `find "$result_dir" ...`，但该目录不存在，`find` 返回非零；
- 因脚本开头 `set -eu` + `set -o pipefail`，管道 `find ... | sort_by_sample_number > "$input_list"` 整体返回非零，脚本立即中止；
- 结果：`all_corners_summary.csv` **没有被写出**，脚本以退出码 1 崩溃。

实际复现（原始脚本输出）：

```text
[ALARM] corner0 sample=s7 pass_flag=0.000000e+00 file=.../IsmOscTestSweep_s7.mt0
find: '.../meas_result_by_corner_1021/corner1': No such file or directory
```

## 2. 根因

脚本写死 `CORNERS="corner0 corner1 corner2 corner3"` 并假设 4 个 corner 的结果目录都存在。而当前数据集（`superon_sweep_20261021_133105`）只产出了基础 corner0 的 FSDB（corner1–3 无数据，`submit_ismosc_corner_meas.sh` 已按“单 sweep 数据集”跳过），因此 `meas_result_by_corner_1021/` 只有 `corner0/`，缺失的 corner 目录触发了 `find` 非零退出 + `set -e/pipefail` 的崩溃。

## 3. 改动内容（diff）

```diff
--- a/summarize_meas.sh
+++ b/summarize_meas.sh
@@ -8,8 +8,8 @@
 # Produces:
 #   <BASE_DIR>/meas_summary/cornerN.csv           per-corner measurement table
 #   <BASE_DIR>/all_corners_summary.csv            combined table (all corners)
-# Exit status: 0 if all samples PASS; 2 if any sample FAIL (summary still written);
-#              non-zero (find/set -e) if a corner result dir is missing (BUG).
+# Exit status: 0 if all samples PASS; 2 if any sample FAIL (summary still written).
+#              Missing corner result dirs are skipped rather than aborting the run.
 set -eu
 set -o pipefail
 
@@ -36,8 +36,11 @@
 overall_fail=0
 for corner in $CORNERS; do
   result_dir="$RESULT_ROOT/$corner"
+  # skip corners whose result dir is absent (e.g. single-sweep dataset only ships
+  # corner0); find on a missing dir would abort the whole run under set -e/pipefail.
+  [ -d "$result_dir" ] || { echo "[INFO] $corner: no result dir ($result_dir); skipping"; continue; }
   input_list="$SUMMARY_ROOT/${corner}_input.list"
-  # (original) list mt0 files for this corner
+  # list mt0 files for this corner
   find "$result_dir" -maxdepth 1 -type f -name '*.mt0' | sort_by_sample_number > "$input_list"
   corner_csv="$SUMMARY_ROOT/${corner}.csv"
   : > "$corner_csv"
@@ -60,7 +63,7 @@
 echo "corner,sample,pass_flag,last_pls_pre0,status" > "$ALL_CSV"
 for corner in $CORNERS; do
   corner_csv="$SUMMARY_ROOT/${corner}.csv"
-  [ -f "$corner_csv" ] && grep -v '^$' "$corner_csv" >> "$ALL_CSV"
+  [ -s "$corner_csv" ] && grep -v '^$' "$corner_csv" >> "$ALL_CSV"
 done
 echo "Wrote $ALL_CSV"
```

## 4. 改动必要性说明

1. **corner 目录缺失守卫（核心修复，必需）**
   `[ -d "$result_dir" ] || { echo ...; continue; }`
   - 这是修复崩溃的**最小必要改动**：缺失的 corner 目录不再触发 `find` 非零退出，而是打印 `[INFO]` 后跳过，脚本继续处理其余 corner 并最终写出合并 CSV。
   - 完整保留了原本“按 corner 汇总 / 合并 CSV / 退出码语义（0=全过，2=存在 FAIL）”的全部能力，行为对“4 个 corner 全在”的正常数据集完全不变。
   - 仅新增一个 shell 内建判断（`[ -d ]` + `continue`），未引入任何新命令，符合“主要利用现有脚本能力”的约束。

2. **头部注释更新（必要）**
   删除已被修复的旧描述“corner 结果目录缺失 → 非零退出 (BUG)”，改为“缺失的 corner 目录将被跳过”。否则注释与实际行为相矛盾，会误导后续使用者。

3. **合并阶段 `[ -f ]` → `[ -s ]`（防御性，建议保留）**
   原始写法对“存在但为空”的 corner 目录，`grep -v '^$'` 会在空文件上返回 1，同样触发 `set -e` 中止。改用 `[ -s ]`（文件存在且非空）后，空 corner 目录在合并阶段直接跳过，与缺失目录行为保持一致。
   - 该改动不影响当前数据集结果（corner0 非空、corner1–3 不存在），但使脚本对“空目录”场景更健壮，且只改动一个判断开关，风险极低。

## 5. 验证结果

在给定 `meas_result_by_corner_1021/`（corner0 含 s0–s7 共 8 个 `.mt0`，其中 s7 pass_flag=0 为 FAIL）上运行修复后脚本 `bash summarize_meas.sh`：

- 正常汇总全部 8 行并写出 `all_corners_summary.csv`（表头 + 8 行数据，按样本号升序）；
- s7 正确判定为 FAIL（`last_pls_pre0=failed`），脚本按约定以退出码 2 结束；
- 缺失的 corner1/2/3 打印 `[INFO] ... skipping` 并被跳过，不再导致崩溃；
- 产出文件 `all_corners_summary.csv` 内容见同目录。