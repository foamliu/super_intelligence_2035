交付接口：outputs/submit.zip 内含 2 个文件——`innovus_fp.tcl`（分代网表感知的修复版 fp 脚本）与 `diagnose.json`（IMPSR-1253 根因诊断结果）。
工作目录下 `inv_fp.log`（fp 日志）、`innovus_fp.tcl`（原版，未修复）、`dc_netlist_A.v`（DC 网表片段）、`power.globals` 为真实输入（只读）。
评测只看 submit.zip；判分在独立目录解 zip，用隐藏 fixture B（不同 net 名/子树/计数/revision）跑候选 tcl 结构断言 + diagnose.json 内容断言，不跑真实 Innovus（license 不可用）。
