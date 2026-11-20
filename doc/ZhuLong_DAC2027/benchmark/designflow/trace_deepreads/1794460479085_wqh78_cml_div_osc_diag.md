# Deepread: 1794460479085_wqh78 — CML ÷2 divider 振荡诊断 (joeyl / hfeg0pkn004)

- trace: `1794460479085_wqh78.messages.json` (1.59MB / 393 msgs), scp 自 10.129.2.13:/home/joeyl/.cline/data/sessions/1794460479085_wqh78/
- mc=235, keywords: netlist:571;hspice:402;pdk:362;synopsys:244;transistor:170;opamp:106;schematic:59
- domain: spice_sim (强 B 信号: hspice:402 / opamp / transistor / pdk)

## 用户意图（原话）
- MSG0: `/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/5_DIVIDER/2_TRAN.sp`（隐含：修复不振荡的分频器）
- MSG61: 「如果有什么问题，请与我确认」

## agent 工作链（L3 调试 + 修复 + 回归）
1. 在 /ai_sandbox 建副本（/rundata 只读），tb_base.sp 加 `.print tran v(f0) v(f1) v(r0) v(r1) v(wckt) v(wckc) ...` 跑 FineSim 出 ASCII .pt0
2. 解决沙箱 LD_PRELOAD/libstdc++ 注入问题，FineSim 跑通
3. **诊断**: 复位后 4 输出全锁死 ~0.82V，摆幅仅 18mV，时钟 12.6GHz 正常翻转 ⇒ 分频器死锁
4. **根因**: CML 上拉 PMOS 负载过强（ResCtr0=0 使 PMOS 全导通三极管区），尾电流建不起输出差分摆幅 ⇒ 无再生增益
5. **修复验证**: ResCtr0=VDD（关 PMOS 负载、用无源电阻）⇒ 摆幅 18mV→177-220mV，÷2 振荡 6.31GHz = 12.6/2，F/R 正交；备选: PMOS 负载宽 24µ→1µ（仍 ResCtr0=0）也起振 6.28-6.31GHz
6. 写 HANDOFF_CML_divider.md 交付

## 关键复用脚本（agent 自写，正文持久化）
- `analyze.py` (MSG78): `load_pt0`(跳 `.` 行/首非数字行=header/数据行=float) + 稳态窗(>=2ns) min/max 峰峰摆幅 + mid=(min+max)/2 过零计数 + 启动区采样
- `collect3.py` (MSG352): 末 2ns 稳态段 + 上升沿检测(prev<mid<=v) + 周期=相邻上升沿间隔均值 + freq=1/period
- `sf.py` (MSG236): 同上 + 输出摆幅/频率报告

## 合成决策
- A 档不可行: /rundata/m2701 项目目录对 e0031982 权限拒绝 + FineSim tool_result 已清空 + 无 license
- B 档合成: 抽 .pt0 波形分析 archetype → **CML ÷2 振荡诊断器** (parse .pt0 + 摆幅/上升沿/频率/分频比 + 死锁/÷2/÷1 判定)
- 与 h3vpf(r484, joeyl CML divider SWING×Vref 扫描 TB 生成器) 区分: 不同 deliverable（波形诊断 vs TB 生成）、不同技能
- 真实参数忠实: 死锁 18mV/0.82V、修复 220mV/6.31GHz/÷2、信号名 f0/f1/r0/r1/wckt/wckc/rst_p/biasn/biasp、.pt0 格式
- hidden B = ÷2 修复(210mV/ratio 0.5)、B2 = ÷1 错误分频比(128mV/ratio 1.0) 非硬编码探针

## 交付
- task_id: EDA-Eval-DesignFlow-CmlDivOscDiag-001 (spice_sim L2, k_check=10)
- 自验: ref PASS 10/10 + §4.9 三假(empty/print_only/core_removed)全 FAIL + 5 negative 全 FAIL
