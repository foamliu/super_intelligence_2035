# Deepread: xgfh1 — FineSim time step too small (diverged) 根因诊断

- session: 1793955137675_xgfh1
- user: curryxu @ hfeg0pkn001
- match_count: 51, domain: spice_sim
- trace path: /home/curryxu/.cline/data/sessions/1793955137675_xgfh1/1793955137675_xgfh1.messages.json (66KB, 16 msgs)
- agent: lead, updated 2026-11-06T08:56:50

## 用户意图（真实任务）
用户跑 FineSim 瞬态仿真遇到报错，问原因：
> finesim仿真报这个错，是什么原因
> ERROR! time step too small (diverged).
> diverged at node: "xi_channel.xi_bcenter.xi_bcenterca.xi_dl_dlltop.xi_dl_dcc_qb.xi2<0>.xi0.xmmn0:drn"

这是 debug-Q&A / 根因诊断类任务（旧判 reject consulting，新标准恢复可造）。

## 对话流
1. U1/U2: 用户报错 + 问原因（重复发了一次）
2. A 加载 spice_tb_stimulus 技能
3. A 读 /home/curryxu/.cline/skills/spice_tb_stimulus/references/simulator_options.md
4. A 用 cimi-kb-search 检索"finesim time step too small diverged 收敛 报错 解决"（内部 KB 未配 API Key，跳过）
5. A 用 ask-eda 技能检索，命中 finesim_user_guide.pdf (score 0.99) + primesim_user_guide.pdf (0.97)
6. A 给出完整根因诊断 + 解决方法

## 关键诊断内容（A 最终回答）
**报错性质**：瞬态分析数值收敛失败——仿真器反复缩小步长仍无法收敛，步长到下限中止。
**diverged at node**：收敛误差最大的节点（DCC 模块一个 NMOS 漏端），是"症状"不是"病根"。

**常见诱因（5 类）**：
- 电路强非线性/刚性（DLL/DCC 反馈环路典型）
- 上电/复位激励边沿太陡（理想源阶跃）
- 初始工作点离真实工作点太远（DC 收敛差、节点悬空）
- 多核并行（-np N）分区破坏关键环路
- 后仿 spf 寄生引入极小时间常数

**解决方法（按优先级）**：
1. `finesim_convlevel`（首选，加一行 option）：
   - 0=默认；0.5=缓解并行仿真收敛；1=关闭时间步预测+GEAR2+增大 pivot；2=1 基础上关闭电荷计算/增量 stamping/LUT；3=2 基础上 imax=32+强制后向欧拉
   - 建议从 1 开始试，不行升 2/3
2. `finesim_detect_vcvs_loop=1`（VCVS/Verilog-A 环路时分区前检测保持环路完整）
3. 通用：delmax / reltol/abstol/vntol / finesim_method(gear2only/trap) / -np 1 / finesim_mode
4. 电路/激励层：PWL 缓升电源(10~50ns ramp) / RESETB power-on 后释放 / .ic/.nodeset / spf 角本核对

**KB 来源**：finesim_user_guide.pdf (0.99), primesim_user_guide.pdf (0.97)

## 合成决策
- B 档 synthesized（A 档不可行：真实 /proj 内网工程目录 SUT 沙盒无 /proj 权限不可达）
- 任务形态：写 finesim_convergence_diag.py 解析 doc/ 产 finesim_convergence_diag.json
- A=报错日志+提交命令+网表片段+option 文件；hidden B=不同节点(dl_dcc_qa/xmpp1/src)/不同 np(8)/不同 queue(fqueue3h)/不同 mode(spicemd)
- 16 断言(a-p)：含 cross-input guard(d/e/f/g B≠A) + A-leak guard(k) + 真跑候选(o) + 确定性(p) + 5 级 value_table(i) + 5 类诱因≥4(j) + detect_vcvs_loop(n)
- case_id: EDA-Eval-DesignFlow-FinesimConvDiag-001
- ref PASS 16/16 + 4 negs(naive_hardcode_a/empty_shell/print_only/core_deleted) 全 FAIL ✓
