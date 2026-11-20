交付接口：把修改后的 `synth.tcl` 与清理后的 `addr_to_rowcol_region_mapped.sdc` 两个文件打进 `outputs/submit.zip`（仅这 2 个文件）。判分器 `check(submit.zip, workdir)` 会解 zip 校验两文件内容，不在 workdir 留痕。
