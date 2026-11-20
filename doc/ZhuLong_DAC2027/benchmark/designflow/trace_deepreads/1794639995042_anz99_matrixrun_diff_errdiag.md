# trace_deepread: 1794639995042_anz99 — matrixrun script diff + sim-launch err diag (ericw)

- **user/host**: ericw @ hfeg0plg58 (10.129.32.80)
- **session**: `1794639995042_anz99.messages.json` (459KB, 49 msgs, mc=41)
- **trace_source keywords**: netlist:379;verilog:77;drc:18;synopsys:17;hspice:11;analog:10;virtuoso:4;pex:2

## 用户真实意图（原话）
> U#0: 「/apps/cad/bin/matrixrun /proj/drexp/V0/simdir/finesim/drexpF/RunFile/Vcap/matrixrun_igzo 这两个有啥不一样」
> U#10: 「用 matrixrun 脚本生成的 si.inp 中 … Project: drdxq/V0 … The drdxq was not exist! Please check. 报了这个项目不存在的 log 为啥」

两段任务：(1) 结构化比对 CAD 官方 `matrixrun`（/apps/cad/bin/）vs drexp 项目 IGZO 定制版 `matrixrun_igzo`；(2) 诊断生成的 si.inp 里 "drdxq was not exist" 错误的根因。

## assistant 工具链（~25 tool_use: 全 read_files + list_allowed_files + 1 run_approved_command grep）
1. read_files 两份脚本（各 ~3700/~3300 行）逐段读
2. list_allowed_files 检查 /proj/drdxq /proj/drexp 路径是否存在 → drdxq 不存在
3. grep "drdxq|was not exist|Please check" 在 matrixrun_igzo
4. read_files /home/coverage/sim/bin/createControlFile_v3 → 定位外部工具

## 实质差异 + 根因（结论）
- **脚本差异**：matrixrun_igzo 是 drexp 项目 IGZO 定制版（加 IGZO 模型路径、改 netIgnoreFile 处理、改 corner 配置），CAD 官方版是通用版。
- **错误根因**：si.inp header 的 "Project: drdxq/V0" + "drdxq was not exist" **不是 matrixrun 脚本本身报的**，而是它调用的外部工具报的。调用链：
  `matrixrun → createIgnoreCtrlFile() [内部函数] → /home/coverage/sim/bin/createControlFile_v3 [外部工具] -p drdxq`
  createControlFile_v3 用 `-p drdxq` 找 /proj/drdxq，但实际项目是 drexp（/proj/drexp 存在，/proj/drdxq 不存在）⇒ 报 "was not exist"。
- **fix**：把 PROJECT 从 drdxq 改成 drexp（或建 /proj/drdxq 软链）。

## 交付物（真实 trace）
无显式交付文件（Q&A 诊断型）。B 档合成：自包含小型 matrixrun 脚本 + si.inp，oracle = 结构化 diff + 调用链根因诊断。

## 域判定
spice_sim（FineSim 仿真矩阵编排脚本的 diff + sim-launch 错误诊断）。关键词 hspice:finesim 上下文 + sim-launch pipeline。非 layout/lvs/drc 实操。
