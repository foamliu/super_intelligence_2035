# 深读笔记: qo3pd — DC 综合 UPF-579 诊断补丁 (digital)

## trace
- session: `1793849459663_qo3pd`
- user: e0046913 @ hfeg0pkn003 (mc=39)
- size: 506KB / 81 msgs / session 文件最后修改 2026-11-05
- tools: cline 在 TV1 DBC001A `SramPwrTcqGrp0` 功耗测量组的低功耗 DC 综合环境上工作；核心交付是 UPF 第 5 节 `connect_supply_net -cells/-pins` 补丁
- ledger: 行 195（claim 2026-11-07 13:55 → case 2026-11-07, case_id=EDA-Eval-DesignFlow-Upf579Patch-001）
- 与同用户 r174 UpfGen-001 的区别：UpfGen 是从 design_spec.json **生成**全新 UPF（生成类）；本 case 是从 dc.log **诊断** UPF-579 + **修补**现有 UPF（修补类），无重叠

## 用户意图
USER#35（干净需求轮，A-faithful rule2 未违反）逐字原文：
> 检查并核对 upf/SramPwrTcqGrp0.upf，给出第 5 步 connect_supply_net … -cells/-pins 的具体补丁

干净需求轮 = USER#0/#35/#46/#66 均为同一意图的迭代（核对 UPF + 给第 5 步补丁），无敏感信息、无前序污染。

## assistant 工具链 / 真实产物
1. 读 `upf/SramPwrTcqGrp0.upf`（145 行原 UPF：14 PG 端口 + 14 supply_net + 14 port_bind + 1 TOP + 6 PD_Ix 独立供电域 + set_domain_supply_net，但**无 Section 5** `connect_supply_net -cells/-pins`）
2. 读 `dc.log`（334 行）找到关键报错：`Error: A supply net cannot be determined for the power pin VSS on the cell hcsp8kx160cm4b8c1r1_dbc_big_pwr_tcq_g0_i0. (UPF-579)`
3. 诊断根因：SRAM 宏的 VDD/VSS power pin 不由普通 wire 连接，DC 无法从 domain 归属自动推断其 supply net，必须显式 `connect_supply_net <pwr_net> -cells {<macro>} -pins {VDD}` + `... -pins {VSS}`
4. gold 补丁 = msg#47 editor tool_use `new_text`（8256 字符 / 175 行），在原 UPF 末尾的 `set_domain_supply_net PD_I5` 后插入 Section 5，含 12 条 `connect_supply_net -cells/-pins`（6 域 × VDD+VSS 各一）+ 注释说明 power pin 核对方法
5. 注：editor 因 "too large >6000" 报错未落盘，但 new_text 完整保留在 messages.json = trace 末尾用户实际接受的结果（A-faithful rule4 金标准）

## A-faithful 判定
**A 档 faithful**：任务说明 = USER#35 逐字原文（仅掩码无敏感信息需掩）；task_brief 只写交付接口 ≤3 行（patch_upf.py 读 UPF+dc.log 诊断输出修补 UPF）；gold = trace msg#47 new_text。真实 dc.log + 原 UPF 可作为 SUT 可见资产附给候选开发自验。

## 合成 plan (隐藏 B)
facet = **UPF-579 补丁生成器**(`patch_upf.py`，python)
- 输入: 一个待修补 UPF 文件路径 + 对应 dc.log 路径
- 诊断: 解析 UPF 的 power_domain（1 TOP + N CHILD）+ 每个 CHILD 的 `-elements` + `set_domain_supply_net -primary_power_net/-primary_ground_net`
- 输出: 在最后一个 CHILD 的 `set_domain_supply_net` 后插入 Section 5，每 CHILD 域产 2 条 `connect_supply_net <pwr_net> -cells {<element>} -pins {VDD}` + `connect_supply_net <gnd_net> -cells {<element>} -pins {VSS}`

### 隐藏 B（ClkTreePwrGrp2，4 域）
- 顶层: `ClkTreePwrGrp2`（vs A 的 `SramPwrTcqGrp0`）
- PG 端口: 10（vs A 的 14）
- 独立供电域: 4（vs A 的 6）
- SRAM 实例名: `sram_rf8x256_pwr_msr_g2_i2` / `sram_rf4x512_pwr_msr_g2_i5` / `sram_rf2x1024_pwr_msr_g2_i9` / `sram_rf1x2048_pwr_msr_g2_i11`（vs A 的 `hcsp8kx160...` / `hc1prf1kx144...` 等）
- 域→实例映射非连续: J0→i2 / J1→i5 / J2→i9 / J3→i11（vs A 的 I0→i0 / I1→i1 / I2→i2 / I3→i6 / I4→i8 / I5→i10）
- 电压: 0.80V（vs A 的 0.75V）
- B 的 UPF 有同样 UPF-579 bug（无 Section 5）；B 的 dc.log 报 UPF-579 on `sram_rf8x256_pwr_msr_g2_i2`
- 硬编 A 的 SramPwrTcqGrp0 / 6 域 / A 实例名的补丁会在 B 上每个结构条件全 FAIL

### 反硬编码守卫
1. **A/B 结构全异**（顶层/实例名/域数/电压/映射全不同）
2. 条件 `h`: -cells 只能用 B 元素，含 A 名（hcsp8kx160/SramPwrTcqGrp0）即 FAIL
3. 条件 `n`: 输出 UPF 不含 A 标记（SramPwrTcqGrp0/hcsp8kx160/hdsp8kx160/hc1prf1kx144/hc2prf1kx72/hd2prf1kx72/hd1prf1kx144/big_pwr_tcq_g0）
4. 条件 `o`: 源码 patch_upf.py 非注释行不含 A marker 硬编
5. 条件 `p`: 随机化 B'（seed 7/11，域数 2..5，不同实例名）各产正确 Section 5，反硬编 B gold

### check 16 条件 a-p
- a: submit.zip 存在 + 合法 zip + 含 patch_upf.py
- b: patch_upf.py `py_compile` 通过
- c: [B] 运行 exit 0 + 产出非空 UPF（含 connect_supply_net）
- d: 输出 UPF 大括号/小括号配平
- e: 原 4 节保留（supply_ports/supply_nets/port_binds/power_domains 数 ≥ B 原值）
- f: Section 5 connect_supply_net -cells/-pins 数 == 2*n_child（B=8）
- g: 每个 B 子域 element 被 -cells 覆盖
- h: -cells 只用 B 元素（无 A 名 hcsp8kx160/SramPwrTcqGrp0，无臆造名）
- i: 每域 pwr_net → element -pins{VDD}
- j: 每域 gnd_net → element -pins{VSS}
- k: -pins 只允许 VDD/VSS
- l: 无跨域（element 的 VDD/VSS net 必须是其自身域的 pwr/gnd_net）
- m: Section 3 port binds 保留（B 的 -ports binds 不变）
- n: 输出 UPF 不含 A 标记（SramPwrTcqGrp0/hcsp8kx160/hdsp8kx160 等）
- o: 源码 patch_upf.py 非注释行不含 A marker 硬编
- p: 自洽（-cells net 已 create_supply_net，element 已 create_power_domain -elements）+ 随机化 B'（seed 7/11）各产正确 Section 5（反硬编）

## 自验
- ref patch_upf.py 在 A 产 12 binds（6 域 × 2，匹配 gold msg#47）；在 B 产 8 binds（4 域 × 2，匹配 B gold）
- check.py: ref PASS 16/16；7 negatives 全 FAIL，distinct first-fail conds = {c, f, j, p}（≥2 独立）
  - naive_noop→f / hardcoded_A→f / print_expected→c / wrong_pins→j / fake_empty→c / fake_core_deleted→f / hardcode_B_gold→p（随机化 B' seed=7 抓）
- negative_selftest.py PASS（ALL_FAIL True, DISTINCT_CONDS=4 ≥2）
- 本地（/nasdata 仓库目录）与 .75 双验一致
