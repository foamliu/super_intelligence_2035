# Deepread: 1793849459663_qo3pd (e0046913 @ hfeg0pkn003, mc39, digital)

**User**: e0046913 (yutingq 的 lowpower DC 综合 run, TV1 DBC001A test-chip, SramPwrTcqGrp0 顶层)
**Tool**: Synopsys Design Compiler V-2023.12-SP5 (DC Ultra + Power Compiler), low-power flow with UPF
**81 msgs / 506KB**. 读法：directory 格式 `<sid>/<sid>.messages.json`（cline 迁移后；flat 路径 ESTALE）。

## User turns
- U#1-3: `/proj/lacaa/TV1_digital/simdir/yutingq/lowpowerDC_for_IP/logs 分析综合情况` (分析 DC 综合日志)
- U#20: `检查并核对 upf/SramPwrTcqGrp0.upf，给出第 5 步 connect_supply_net … -cells/-pins 的具体补丁`
- U#27: `直接生成修改后的UPF文件，放在我的home目录下` (**PRODUCE-TASK**: 生成修正后的 UPF)
- U#37: `确认upf中 i6/i8/i10 与 I3/I4/I5 的对应关系是否真的是我想要的` (验证 domain↔instance 映射)

## Agent 工具链 (digital/low-power)
1. read dc.log (2137→1419 行，DC RM flow) → 2 errors: SEC-51 license + compile_ultra 失败 (unmapped)
2. grep UPF/supply/connect_supply 关键字 → `connect_supply count=14`, `create_supply count=28`
3. read `upf/SramPwrTcqGrp0.upf` (140 行, 4 节: supply_port / supply_net / connect_supply_net→ports / power_domain+set_domain_supply_net)
4. **根因 (UPF-579)**: 第 3 节 connect_supply_net 只绑顶层端口 (-ports)，**全文无任何 connect_supply_net -cells 把供电网连到 6 个 big_pwr SRAM 宏的 VDD/VSS 引脚** → DC 无法推断 hcsp8kx160_i0 的 VSS 供电网
5. 生成 Section 5 补丁: 12 条 `connect_supply_net VDDIxN/VSSIxN -cells {<macro_inst>} -pins {VDD/VSS}` (6 宏 × VDD/VSS)
6. verify_upf.py 校验: 6 实例名与 create_power_domain -elements 一致；175 行；26 条 connect_supply_net (14 原 -ports + 12 新 -cells)
7. U#37 验证: 解析 SramPwrTcqGrp0_presyn.v 网表 → 12 个 TCQ 宏, i0/i1/i2/i6/i8/i10=big_pwr (PD_I0..I5), i3/i4/i5=custom (TOP domain) → I3↔i6/I4↔i8/I5↔i10 映射正确

## 6 个 big_pwr SRAM 宏 (PD_I0..PD_I5)
| PD | 实例 | 网 (power/ground) |
|---|---|---|
| PD_I0 | hcsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i0 | VDDI0N/VSSI0N |
| PD_I1 | hc1prf1kx144cm2b2c1r1_dbc_big_pwr_tcq_g0_i1 | VDDI1N/VSSI1N |
| PD_I2 | hc2prf1kx72cm4b4c1r1_dbc_big_pwr_tcq_g0_i2 | VDDI2N/VSSI2N |
| PD_I3 | hd2prf1kx72cm4b4c1r1_dbc_big_pwr_tcq_g0_i6 | VDDI3N/VSSI3N |
| PD_I4 | hd1prf1kx144cm2b2c1r1_dbc_big_pwr_tcq_g0_i8 | VDDI4N/VSSI4N |
| PD_I5 | hdsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i10 | VDDI5N/VSSI5N |

## A-faithful 判定
✅ 合格。用户给 UPF 路径 + 指定修复步骤 (connect_supply_net -cells/-pins)，未给根因；agent 自行诊断出「宏电源引脚未 connect」(UPF-579) 并生成补丁。deliverable=修改后私有 UPF → INFEASIBLE (SUT 无法访问 /home/e0046913/) → **B档合成**: 抽取自包含确定性子任务 = UPF connect_supply_net -cells/-pins 修复器。

## 合成方向
`EDA-Eval-DesignFlow-UpfSupplyConnect-001` (digital L1-B档, archetype=upf-connect-supply-fixer)
- SUT 写 `upf_connect_fixer.py`: 解析 UPF → 提取 power_domain(-elements) + set_domain_supply_net(primary_power/ground_net) → 为每个非-TOP 域的 element 生成缺失的 `connect_supply_net <pwr_net> -cells {<inst>} -pins {VDD}` + `<gnd_net> -cells {<inst>} -pins {VSS}` → 输出修正 UPF
- A=power_A.upf (4 域 PD_I0..I3, VDDI0..3, 4 宏), B=hidden power_B.upf (5 域 PD_A0..A4, VCCA0..4, 5 宏, 不同实例名/网名) — 击败 hardcoded_A
- check.py: 跑 fixer on B, ≥14 条件 (宏 VDD/VSS connect 齐 / 网名匹配 set_domain_supply_net / -cells 匹配 -elements / -pins / 原命令保留 / 无重复 / 跨输入守卫 / 3-seed 稳定)
