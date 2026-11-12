# trace_deepread — 1794131955891_zm0zw (tongfanl@hfhds201, mc=92)

**session**: `1794131955891_zm0zw` · user `tongfanl` · host `hfhds201`(=.75) · model `glm-5.3-flash`
**domain**: spice_sim（DDR6 DSCQA 仿真激励向量生成 / Aging characterization）
**时间**: 2026-11-08 09:59–12:35 (2.5h, 83 msgs, completed)

## 用户真实意图（原话）
> 帮我对比下 ./runsti/gen_stimulus_Aging 和 run_compress，告诉我为啥报错。
> 报错信息：xmsim: *E,ERRSEV (./patterns/analogsim/Compress/Compress_task.v,268): (time 6087002 PS). TOP.sc0.Compress_Load_TestMode_Task. 1p6 mode, dqselect=0, dq0 can not input

## assistant 工具链
list_allowed_files → search_codebase(失败 ENAMETOOLONG) → run_approved_command(shell 被策略禁用) → editor 写 python 查找脚本 → run_approved_command(python-runner, 超时后缩小范围) → 定位 `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/runsti/{gen_stimulus_Aging,run_compress}` → 读 Compress_task.v 第 268 行 + cfg_Aging → 查 log/stimulus_tongfanl/Aging_1108_Aging0024/ 的 xrun.log → 历史成功运行 Aging_0909 反证 → 结论。

## 关键产物 / 根因
- **根因**：`gen_stimulus_Aging` 第 7 行 `-d "WRNOPAD NOENDMRR AGING"` **缺 `DQSELH`**。
- **机制**（Compress_task.v）：
  - 第 163~170 行：`Mode="1P6"` → `MODE_1P6=1`；`` `ifdef DQSELH ``→`dqselect=1` else `dqselect=0`。
  - 第 268 行：`DQ_or_TDQ="DQ0"` 分支 `if(MODE_1P6==1 && dqselect==0) $error("1p6 mode, dqselect=0, dq0 can not input")`。
  - 即 1P6 + 无 DQSELH → dqselect=0 → DQ0/DQ1 输入报错；DQ6/DQ7 允许。
- **命中 pattern**：Aging002_RDBI_1BANK_NONMCI / Aging004_HTOL_LTOL_NONMCI（均 1P6 + DQ0），6 个 case(FF/TT/SS) 全报。
- **vecgen.rpt 假阳性**：vecgen 未把 $error 判失败，但 xrun.log 有 `fail_cp_num=1`，DQ0 路径在 dqselect=0 下不工作，激励 compress 读数比对错误。
- **历史反证**：9 月 Aging_0909 case 目录后缀 `_FSMSHORT_COMPRESS_DQSELH`；脚本注释历史均带 DQSELH。
- **run_compress 约定**：DQ0/DQ1 输入必须带 DQSELH；DQ6/DQ7 不带。

## 合成决策
- A 档 trace-faithful：prompt 用用户原话 + 真实报错信息 + 真实文件名/路径/用户名。
- domain = spice_sim（DDR sim-vector / Aging characterization 邻域）。
- 难度 L2：check 真跑 compress_check_model.py（Compress_task.v 报错逻辑的 Python 仿真模型）验证候选 -d defines，含随机化(DQ0/DQ1×corner×3seed) + 负对照(原始缺 DQSELH 必报错) + DQ6 对照(不被过度修复破坏)。
- 隐藏输入 B：compress_check_model.py + 3 pattern json（2 DQ0/1P6 触发 + 1 DQ6 对照），不进 SUT 沙箱。
- 判分 14 条独立断言(a-n)，真跑 subprocess 满足 §4.2，随机化满足 §4.5。
- .75 上 /proj/dscqa 属 tongfanl 不可读(e0031982 身份)，附件用 trace 原句忠实重建（trace_source 记录真实 session）。

## case_id
EDA-Eval-DesignFlow-DdrVecgenDQSELH-001
