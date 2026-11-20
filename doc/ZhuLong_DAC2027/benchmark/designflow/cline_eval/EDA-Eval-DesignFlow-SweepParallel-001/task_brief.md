交付接口：outputs/submit.zip 内含 2 个文件——`run_sweep.sh`（改为每 corner 一个并行 LSF 任务）+ `compare_report.md`（与原版 diff + 改动必要性说明）。
工作目录下 `run_sweep.sh`（原版，单任务串行）与 `IsmOscTestSweep.sp`（含 4 个 `.alter` PVT corner 的 FineSim 网表）为真实输入（只读）。评测只看 submit.zip；判分在独立目录解 zip，用隐藏网表跑候选脚本验拆分正确性。
