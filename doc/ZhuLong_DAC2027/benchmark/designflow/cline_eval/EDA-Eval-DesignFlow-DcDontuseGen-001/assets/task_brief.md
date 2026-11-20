交付接口：submit.zip 含 `gen_dontuse.py`（CLI `--lib <path> --allow <allow.txt> -o <out.tcl>`，纯 stdlib，须从 lib 解析 LIB_NAME 不得硬编）+ `dont_use_A.tcl`（对可见 `lib_A.lib` + `allow_A.txt` 预生成）。
可见附件位置：`assets/EDA-Eval-DesignFlow-DcDontuseGen-001/lib_A.lib` + `allow_A.txt`。
判分：`check(submit.zip, workdir)` 跑候选于可见 A + 隐藏 B，独立 oracle 比对「解除禁用 cell 集合」与 LIB_NAME；B 异构击破硬编。
