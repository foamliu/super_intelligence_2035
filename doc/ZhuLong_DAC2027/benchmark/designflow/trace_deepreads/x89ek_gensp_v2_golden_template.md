# Deepread: 1792216766099_x89ek (reedchen @ hfeg0pkn004, mc=163)

- **User**: reedchen  **Host**: hfeg0pkn004  **Session**: 1792216766099_x89ek.messages.json (1.47MB, 418 msgs)
- **Domain**: waveform (FineSim SPICE deck 生成 / TrTf·skew 测量)  · **Track**: A (trace-faithful)
- **A-faithful 任务说明轮**: msg[U#15]（提出需求 + 表达目标，非根因/非修复）
  - 原文逐字：环境里 GenSP.py 有 bug；两个 measure SP（TrTf / skew）应只 include 一个；希望 GenSP 支持 MC 模式（.param mis_flag=1 + .tran 50p 100n sweep monte=1000 打开、常规 .tran 注释）；stress vs normal = sigmaflag=6 vs *.param sigmaflag=1.36；vintbus vs vintcore = .param pvintbus=0.25v vs .param pvintbus=pvcc；优化脚本 + 做 golden templateSP 作为脚本输入；跑 vintbus stress PVT_HighVoltage corner 常规 trtf 仿真。
  - msg[U#0] = 工作流能力评估（太泛，不用作 A 任务说明）；U#184「非常好，你直接提交仿真」= 用户接受 GenSP v2 交付。
- **Agent 工具链**: list_allowed_files / read_files / editor / run_approved_command。先探查 simulation/scripts/ + template_sp/ 现有脚本（GenSP.py v1, GenSignalTrTf.py, GenSkewMea.py, MergeMt0.py），识别 v1 问题（模板爆炸 10+、--mea_file 正则脆弱、MC 靠后缀模板、stress/normal 区分混乱）。
- **交付**: 
  - `golden.sp`（单一黄金模板，替代 10+ 遗留模板，默认 vintbus/normal/trtf/non-MC，marker 行：.param pvintbus=0.25v / *.param sigmaflag=1.36 / **.param mis_flag=1 / .tran 50p 400n / .inc trtf active + skew commented）
  - `GenSP.py v2`（206 行，4 轴变换：apply_mode / apply_stress / apply_mc / apply_mea + apply_pvt corner；CLI: --mode --stress --mc --mea -t -o）
  - `gensp_v2_README.md`
- **验证** (msg[A#143]): 全 8 variant + MC 关键行逐行核验通过（sigmaflag=6 / .temp -40c / .lib SS / pvintbus=0.25v / .tran 50p 400n / **.param mis_flag=1 / .inc trtf）。msg[A#172] vintcore/skew/MC 全 variant 再核验通过。
- **真实文件可读性**: /home/reedchen/GenSP.py（8362B, reedchen-owned, e0031982 可读 via ssh cat）= 参考解来源；/home/reedchen/golden.sp 已不存在（agent 中间产物被清）；simulation/template_sp/ + scripts/ + *.csv = Permission denied（rundata reedchen-only）。
- **合成策略**: golden.sp / pvt.csv / meas inc stub 按 trace 公开事实（U#15 逐字 .param 行 + README marker 表 + GenSP_ref.py 正则）合成（A 资产）；真实 GenSP.py v2 直接用作参考解（适配 DEFAULT_GOLDEN 为相对路径）。hidden B = 同 marker 值（保证候选变换正则可匹配）+ 不同 .lib 路径前缀 (/proj/ddgoaB/) + 不同 corner (SS_0.72V-40C) + 不同 stimulus net 名 → 跨输入护栏。
- **判分**: check.py 16 条件 a-p（zip+compile / 8 variant 跑通 / 4 轴 marker 各 2 条 / PVT .temp / PVT .lib corner / runscript / 跨输入 B / 确定性 / 退化 FAIL）。ref PASS 16/16 · 4 negatives ALL-FAIL distinct{empty→b / print-fixed→n / core-deleted→d / naive→d} · NEG_RC=0。
