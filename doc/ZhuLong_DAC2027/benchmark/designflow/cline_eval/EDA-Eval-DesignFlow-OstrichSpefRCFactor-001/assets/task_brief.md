交付接口：outputs/submit.zip 内含 1 个文件——`ostrich_rc_factor.tcl`（用 Cadence Ostrich 比较两份 SPEF、生成 RC Factor 与 per-net 差异报告的 TCL 脚本）。
工作目录下 `golden_quantus.spef`（sign-off 抽取）与 `target_innovus.spef`（实现抽取）为真实输入（只读）。评测只看 submit.zip；判分在独立目录解 zip，用隐藏 SPEF 对（不同 net 数/命名/数值）跑候选脚本结构断言，不跑真实 ostrich（license 不可用）。
