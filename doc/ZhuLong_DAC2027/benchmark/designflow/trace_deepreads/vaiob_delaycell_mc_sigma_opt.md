# Trace 深读：vaiob — DRAM 延迟单元 Monte Carlo Sigma 优化

- **session**: `1792829537180_vaiob.messages.json`
- **user / host**: harrywu / hfeg0pkn002 (mc=506, spice_sim 域)
- **size / msgs**: 2.84 MB / 964 msgs (491 user / 473 assistant)
- **tools**: run_approved_command 183 · editor 162 · read_files 87 · list_allowed_files 28 · search_codebase 6
- **选料理由**：hspice:910 + finesim 关键词 + 711 netlist/686 hspice 工具命中 → 真 L2/L3 仿真；新用户 harrywu（bench 中 0 case）；主题（MC sigma 优化）与现有 11 域 case 无重叠。
- **本轮节奏**：trace >2MB → 按 §3 例外本轮**只深读**，下一轮合成交付（DEBT:1）。第145轮已交付 NetlistChk-001，不违反「禁止连续两轮只深读」。

## 1. 用户真实意图（5 条 substantive user_input）

1. `hi` / `Set the interface to Chinese` —— 切中文界面（旁支，非主线）。
2. `/proj/dscqa/V0/agentdir/harrywu/simulation/LowSigma_Delaycell` —— 理解项目内容 + 解决中文输入问题。
3. **核心需求**：「修改 R_RasVdbiasDlyStd_gut_MC 单元中 MP0/MN0/MP10/MN15 的尺寸，用 Monte Carlo 仿真验证延迟单元延迟值（In 上升沿 → Out 上升沿）的 sigma。建议用系统自带的 Solido 工具或 hspice 自带 MC。步长 Δwidth=0.1um、Δlength=10nm。迭代优化。」
4. `Develop it as a Skill` —— 把优化工具做成 Cline Skill 可关键词触发。
5. `对 delay cell 做 sigma 优化` / `Solido HSMC 🏆（推荐）` / `You submit the simulation task by yourself` / `lhs5~29 进入 Solido HSMC` / `.param mis_flag needs to be set to 1 in input.sp` —— 指定用 Solido HSMC 评 sigma，agent 自主提交作业。

## 2. 项目结构（agent 解析 LowSigma_Delaycell 目录）

DRAM DDR5 DRCOA 验证子项目 —— **High-Sigma Monte Carlo (HSMC) 仿真**。

| 文件 | 作用 |
|------|------|
| `input.sp` | **Finesim 仿真 testbench**，含 16 条延迟路径测量 STD0~STD15；需 `.param mis_flag=1` |
| `netlist` | 从 Aether-SE 导出的完整电路网表 |
| `Pattern_Power.sp` | 电压/温度 corner 配置 |
| `HSMC_script/` | `corners.csv` / `run.sh` / `specs.csv` —— Solido HSMC 运行脚本 |
| `hsmc-nq-data.csv` | HSMC NQ 拟合数据 |
| `variation_designer/` | Solido Variation Designer 配置：`process-model-files/devices.json`、`appsetup/hsmc_app_setup.xml` |
| `delaycell_sigma_sweep.py` | **agent 产出的主自动化工具**（5 种搜索策略） |
| `run` | 仿真启动脚本 |

## 3. 电路与四管目标（核心 discriminator 料）

**顶层设计**：`trim_cell_lg / schematic`；**核心电路**：`R_RasVdbiasDlyStd_gut_MC` —— 可编程电容负载的可调延迟链。
**延迟路径**：`In → InN → delay1 → delay2N → Out`，测量 **STD15**（16 级中最长/最慢路径）。
**标准单元**：invLV / bufLVx2 / invLVx1 / invLVx2。

| 器件 | 实例名 | 类型 | W (μm) | L (nm) | nf | 功能 |
|------|--------|------|--------|--------|----|------|
| **MP0** | XMMP0 | PMOS | 7.952 | 325 | 4 | 输入级上拉 (In→InN) |
| **MN0** | XMMN0 | NMOS | 3.976 | 325 | 4 | 输入级下拉 (In→InN) |
| **MP10** | XMMP10 | PMOS | 8.001 | 325 | 3 | 输出级上拉 (InN→delay1) |
| **MN15** | XMMN15 | NMOS | 3.999 | 325 | 3 | 输出级下拉 (InN→delay1) |

搜索范围（LHS 30 点，±~30%）：MP0 W 5.57~10.27 / MN0 W 2.78~5.08 / MP10 W 5.70~10.30 / MN15 W 2.90~5.20；L 均 227.5~417.5 nm。

## 4. 仿真器与提交方式（self-containedness 关键）

- **Finesim**：`input.sp` 是 Finesim testbench；作业经 **LSF 集群**提交：
  `bsub -q fqueue2h -J n2_${tag} $FIN_PATH input.sp -o ./results -np 8`
- **HSPICE**：亦被 agent 检查 (`which hspice`)，作为备选。
- **Solido HSMC**：每 sizing 点跑 HSMC（~11 min / 13k 样本）评 sigma。
- **sigma 提取公式**（来自 `full_summary.txt` 的 NQ 拟合）：
  `NQ = -58.42 + 5.132e+10 * STD15` → delay sigma ≈ 1/5.132e+10 ≈ **1.95e-11**（要最小化的目标量）。

### .75 可复现性判定
- ❌ **LSF bsub 集群**：fqueue2h 队列，.75 无（同 s2f9d parked 的卡点）。
- ❌ **Solido HSMC**：商业 Variation Designer，.75 无许可/二进制。
- ✅ **Finesim headless**：.75 已验证（第141轮 TotemSC-001 用 `/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim`，`finesim -np 2 <netlist>` 可跑）。
- ✅ **HSPICE headless**：.75 已验证（第128/144轮用 `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice64`）。
- ⚠️ **真实 input.sp / netlist / 模型**：sandbox `/ai_sandbox/dscqa/V0/agentdir/harrywu/...` 对 e0031982 **permission denied**；但文件内容**已存在于 trace 的 read_files tool_result**（下一轮合成时从 trace 提取，或据四管参数+延迟链结构重建代表性 delay cell）。

## 5. agent 主线流程

1. 切中文 → 读 LowSigma_Delaycell 全目录（list_allowed_files）→ 解析项目结构（input.sp / netlist / HSMC_script / variation_designer）。
2. 设计 `delaycell_sigma_sweep.py`（editor 多版迭代）—— 5 策略：one_at_a_time / grid_search / random_search / bayesian_opt / latin_hypercube；含四管 nominal 值表、LSF 提交封装、.tran measure 解析。
3. 语法检查 / dry-run（`check_syntax.py` / `run_dry.py`）—— 全量 sweep 超时，改 dry-run 验证逻辑。
4. 打包成 Cline Skill（`/home/harrywu/.cline/skills/delaycell-sigma-sweep/SKILL.md` + 关键词触发）。
5. 用户澄清「每个点只跑 1 次 tran 不是真 MC」→ agent 设计**两阶段方案**：
   - **阶段 1**：LHS 30 点 nominal .tran → 延迟趋势 → 选 Top-K（5~8）候选。
   - **阶段 2**：候选点跑 Solido HSMC → 从 NQ 斜率提 sigma → 找最小 sigma。
6. 集成 Solido HSMC（`prep_hsmc.py` / `HSMC_script/run.sh`）→ 用户指定 `lhs5~29 进入 HSMC` + `input.sp 中 .param mis_flag=1`。
7. 文本量满 → 用户要求新会话续做（handoff）。

## 6. 判分 discriminator 候选（下一轮合成用）

构建 case 时，把不可复现的 LSF/Solido 抽象掉，聚焦 **.75 可复现的 Finesim/HSPICE tran + delay measure + 尺寸扫描** 核心：

1. **testbench 解析**：从 input.sp 提取 16 条 .measure 延迟路径名（STD0~STD15）+ .tran 区间 + .param（mis_flag）—— 断言解析完整且 STD15 命中。
2. **四管尺寸改写**：在 netlist 中定位 XMMP0/XMMN0/XMMP10/XMMN15，按给定 W/L/nf 改写实例参数 —— 断言改写正确（pin 顺序保留、nf 保留、未误改同名器件）。
3. **真跑 Finesim/HSPICE**：subprocess 跑候选脚本生成的 testbench on **隐藏 B**（不同四管尺寸 + 不同延迟链级数/负载）—— 断言 exit 0 + 仿真收敛 + .lis 产出。
4. **delay measure 提取**：从 .lis/.mt0 解析 STD15（及 STD0~STD15）延迟值 —— 断言与 .75 独立重跑 GT 逐字段对齐（非文本相似）。
5. **尺寸扫描逻辑**：候选脚本对 ≥3 个 sizing 点扫描，每个点跑 tran 取 STD15 —— 断言扫描产出了多点结果且 STD15 随尺寸单调/合理变化（非硬编）。
6. **sigma/分布代理**（替代 Solido）：用 hspice `.MC` 或多次 tran + 统计 std —— 断言 sigma 计算结构正确（n、mean、std 公式），非 print 假数。
7. **跨输入 guard**：A（基线四管）与 B（不同尺寸/级数）的 STD15 量级/趋势不同 —— 硬编 A 值在 B 上败。
8. **随机化**：3 种子抽 sizing 子集，结论一致。
9. **mis_flag param**：候选须在生成的 testbench 设 `.param mis_flag=1`（用户明确要求）—— 断言存在。

≥8 条件，§4.2 subprocess 真跑 B，§4.9 三假提交全 FAIL。

## 7. 真实 artifacts 来源（下一轮提取）

- `input.sp` / `netlist` / `Pattern_Power.sp` 内容 → 从 trace 的 read_files tool_result 提取（本轮 read_files 配对结果为空，需用更细的解析：按 list_allowed_files 路径 + 后续 read_files 块的 content.text 逐条匹配；或从 `delaycell_sigma_sweep.py` 源码中的 nominal 值表 + 延迟链结构**重建**代表性 delay cell netlist + testbench）。
- `delaycell_sigma_sweep.py` 完整源码 → 已在 trace（editor new_text 块，43764 字符），含四管定义、LSF 封装、measure 解析、5 策略 —— 可作 reference 逻辑蓝本。
- HSMC NQ 公式 → `NQ = -58.42 + 5.132e+10 * STD15`（来自 full_summary.txt，trace 中提及）。

## 8. 难度定级

**L2/L3**：真跑 Finesim/HSPICE tran（L2）+ 多点尺寸扫描 + measure 提取 + sigma 代理统计（L3 多步链路）。新用户 + 新主题，满足 §5「新建只做 L2/L3」与用户/主题多样性。下一轮合成时 B 用不同四管尺寸 + 不同延迟链级数/负载电容，确保与 A 结构不同（非换文件名）。

## 9. 台账

`trace_ledger.py claim vaiob --domain spice_sim` 已落。z44lk 已 parked（近 dup DummyDeck-001 + xinqiaoz 饱和）。本轮 DEBT:1，下一轮**必须先交付 vaiob case**。
