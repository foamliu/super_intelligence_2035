交付 outputs/submit.zip，含 gen_sdc.py（通用 SDC 生成器）与 cla_top.sdc（为 A 设计 cla_top 生成）。
gen_sdc.py CLI: python3 gen_sdc.py <rtl_dir> <top_module> [-o <out.sdc>]，读 rtl_dir 下 .v 解析 top_module 端口并输出 SDC。
判分: check(deliverable, workdir) 双参；assets/EDA-Eval-DesignFlow-CombSdcGen-001/A/ 为可见 RTL 输入。
