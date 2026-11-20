交付接口：
- 工具：`tools/set_dc_result_dir.py <new_dc_result_dir> [--project <项目根>] [--dry-run] [--backup]`，替换各流程 Makefile 中 DC_RESULT_DIR/POWER_RES_DIR 的 dc_ 时间戳、fm/fm.tcl 回退默认、以及 rtl_power/<TOP>.vf 的 $sdf_annotate SDF 路径。
- 交付件：`submit.zip` 内含 `set_dc_result_dir.py` 与 `Makefile`（项目根顶层，含 `scan` 与 `replace` 两个目标）。
- 判分：独立临时目录解 zip 后，在隐藏输入 B 上运行工具，校验各处替换正确性、scan 选最新 dc_* 目录、replace 透传、--dry-run 不写盘、非法目录非零退出。
