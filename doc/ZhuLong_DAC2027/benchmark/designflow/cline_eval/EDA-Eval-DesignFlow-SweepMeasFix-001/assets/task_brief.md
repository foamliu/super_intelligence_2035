交付接口：outputs/submit.zip 内含 3 个文件——`summarize_meas.sh`（修复后）、`all_corners_summary.csv`（在所给 `meas_result_by_corner_1021/` 上跑修复后脚本产出）、`fix_report.md`（diff + 改动必要性说明）。
工作目录下 `summarize_meas.sh` / `submit_ismosc_corner_meas.sh` / `meas_result_by_corner_1021/` / `superon_sweep_20261021_133105/` 为真实输入（只读）。 评测只看 submit.zip；判分在独立目录解 zip 跑候选脚本。
