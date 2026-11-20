# trace_deepread: 1792044214783_zwqbl (zhukaic / hfeg0plg58, mc=104)

**session**: `1792044214783_zwqbl.messages.json` (597KB, 73 msgs)
**user/host**: zhukaic @ 10.129.35.82 (hfeg0plg58)
**domain**: spice_sim (五管 OTA 自动调参)
**real_task_summary**: zhukaic 让 agent 读取 `ota.md` skill 后「开始执行」——自动调参五管 OTA，目标 gain>38dB / PM>60° / GBW>200MHz。agent 4 轮迭代 × 并行 2 仿真 = 8 次 hspice（bsub -q fqueue3_analog），全部成功 0 error。基线 34.72dB/56.96°/273.3MHz → 终版 i4a：XMMN L=3.2u, XMMP L=7.8u, i4=3.55uA → gain=38.10dB ✓ / PM=65.00° ✓ / GBW=178.4MHz ✗（GBW 被 XMMN2/XMMN3 尾电流镜结构性钳位，I>2.7uA 后 XMMN2 进三极管区）。

## trace 价值
- **真实完成的设计流**（非空转）：agent 建了 gm/gds/C 定量模型（gds_n=218.4n×(2/L_n)^0.88 回代误差<0.4dB），用模型驱动选参，每轮用 run_trials.py 并行 bsub + 解析 .lis。
- 工具链：read_files(5) / list_allowed_files(2) / search_codebase(2) / editor(18) / run_approved_command(9) / get_agent_policy_status(1)。editor 写 extract_op.py、run_trials.py、trial_specs.json、opt_search.py、ota_tuning_report.txt；run_approved_command 跑 python + bsub hspice + 轮询。
- 产物：ota_tuning_report.txt（含 4 轮 Trial Summary + 最终总结 + GBW 缺口根因闭环分析）+ 同步后的 ota_netlist.sp（i4a 工作点）。

## 输入文件（从 trace read_results 重建，磁盘上已被同名 ota_2stg_* 两级运放版本覆盖）
- `ota.md`：五管 OTA skill，验收 gain>38/PM>60/GBW>200MHz，可调 XMMN0/XMMN1/XMMP0/XMMP1 的 w/l（finger max=7.8u min=200n），3 次迭代 + 1 次偏置电流(2~4uA)杠杆；附 4 组学习数据。
- `ota_netlist.sp`：五管 OTA 网表（XMMP1/XMMP0 ptn, XMMN0/XMMN1 ntn_m, XMMN2/XMMN3 ntn_m 尾镜, i4 DC=2e-6, v0 out net3 DC=0, cg1~cg4）。
- `ac_sim.sp`：hspice AC + LSTB stb，.meas ac GAIN/PM/GBW/f_3db/gain_margin，.TEMP 85，corner ttt。
- `runsim.sp`：`bsub -q fqueue3_analog hspice -i ac_sim.sp -mt 4 -o ./ac_sim/`。

## case 抽取（EDA-Eval-DesignFlow-OTATunePlan-001）
抽取「解析基线 .lis → 建 gm/gds 模型 → 设计首轮并行试验 → 出优化网表 + 报告」这一可复用 L2 子流，**不要求 SUT 真跑 hspice**（PDK/corner 路径 `/proj/dscqa/...` 不在 .75 沙盒）。check 用 subprocess 跑候选 `parse_lis.py` 在**隐藏 B .lis**（不同 sizing：XMMN L=1.0u/XMMP L=1.5u，GAIN=31.45/PM=52.30/GBW=198.7M，与 A 的 34.72/56.96/273.3M 全不同）上解析，与 check 独立解析逐字段比对（击败硬编码 A / print-expected stub）；并校验 trial_plan.json（≥2 trial、w/l 在 [200n,7.8u]、i4 在 [2u,4u]）、proposed_netlist.sp（4 核心管子齐全 + w/l/i4 在范围）、analysis_report.txt（含基线 3 指标数值 + gm/gds|ro|gm-id 模型推导）。

## 难度定位
L2（真跑候选脚本解析隐藏 B .lis，subprocess 执行，断言输出结构而非文本相似）；非 L1（不是离线复刻 A 的固定数值，B 主动换 sizing 防硬编码）；非 L3（不要求多工具链路 + 修复 + 回归，因沙盒无 hspice PDK）。
