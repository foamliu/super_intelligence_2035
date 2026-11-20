# 深读笔记 — 1792204147117_hsrib (justind @ hfeg0plg53)

- **trace_source**: user=justind, host=hfeg0plg53, session_file=1792204147117_hsrib.messages.json, match_count=88
- **域**: spice_sim (FineSim 瞬态噪声分析 / TRNG 前仿)
- **msgs**: 84；size 477KB；工具链：RAG_MCP_Server__search_apis / get_api_details、list_allowed_files、read_files、editor、get_agent_policy_status
- **A档 trace-faithful**：用户原话逐字可用

## 用户意图（原话）
1. `finesim前仿怎么仿真真随机数生成电路？`
2. 贴出 DSIM 生成的 testbench（`TRNG_STUDY_V0`，`.tran 1p 1900n`，`.option noisefmax=50G`，5 条 .lib G5_CIP_Model，.include netlist + TRNG_TEST_v0.sp）→ `这是我的testbench 我怎么修改？`
3. 第一次改完跑出 `Starting Transient Noise Analysis ... fmax=1e11 fmin=5.263e5 seed=1 ntmin=1e-15 0.000us(0.0%)` → `为啥跑不动`
4. 改成 `.tran 1p 1900n NOISE=1 NOISEFMIN=1 NOISEFMAX=10G NOISESCALE=1 NOISESEED=1` 成功 → `改成这个就成功了 帮我解释一下为啥能成功 每个参数都是啥意思`
5. 追问 `NOISEFMIN=1 这个没有用是吗 可以改成啥` / `为啥种子会有影响` / `seed 一共能到几` / `noise=1 是啥意思`

## 电路结构（assistant 从 netlist 解析）
双环形振荡器 TRNG（Dual-RO）：
- `XI7` TRNG_RO_Solution0_plus → 采样时钟 RO，输出 `net9` → 经 XI3/XI4 buf → `TRNG_Clk_pre`
- `XI1` TRNG_RO_Data_3invs → 数据 RO，输出 `net1`
- `XI0` ffrqCSx1_TRNG → DFF，用 TRNG_Clk_pre 采样 net1 → `TRNG1` → XI12 buf → `RandomNumber_Serial`
- 随机性来源：两 RO 各自相位抖动 → DFF 时钟沿采样不确定

## 核心技术点（判分依据）
1. **原 deck 缺陷**：`.tran 1p 1900n` 只有 `.option noisefmax=50G`（仅对 AC 噪声有效），**未启用瞬态噪声** → 两 RO 理想振荡 → DFF 永远采样确定值 → 无随机数。
2. **卡死陷阱**：`NOISETMIN=1e-15`（1 飞秒噪声步长）+ `NOISEFMAX=100G` → 1.9μs/1fs ≈ 19 亿步 → 卡在 0.0%；且 FineSim 把 `NOISEFMIN=1` 自动 clamp 到 `1/stop_time ≈ 526kHz`。
3. **正确修复**：`.tran 1p 1900n NOISE=1 NOISEFMIN=1 NOISEFMAX=10G NOISESCALE=1 NOISESEED=1`（去掉 NOISETMIN，NOISEFMAX 降到 10G），另加全局 `.option noisefmax=10G` / `.option noisefmin=1`。
4. **参数语义**：NOISE=1 开瞬态噪声注入（热噪声/闪烁/散粒）；NOISEFMAX 覆盖 RO 频率 5-10×；NOISESEED 正整数 1..2³¹−1，同种子可复现、异种子模拟"多次上电"；验证 TRNG 有效性 = 换种子输出必须变。

## 适配为 design_flow case
- SUT 提交 `enable_trng_noise.py`（读 input_sp + spec_json → 写 output_sp），对 FineSim testbench 做瞬态噪声启用改写。
- hidden B 用不同 RO/stop(500n)/seed，且**预置陷阱**（NOISETMIN=1e-15 + NOISEFMAX=100G + 无 NOISE=1）→ 脚本必须修正。
- check() 解析 out deck 结构（NOISE=1 / NOISEFMAX∈(1G,50G] / NOISEFMIN>0 / NOISESEED 正整数 / 无飞秒 NOISETMIN 陷阱 / 保留 .tran stop 与 .lib/.include/.END）+ A/B 交叉防硬编码 + 确定性。
- k_check=12 条断言（详见 test_rationale）。

## 关键节点对照（写 prompt 用）
| 节点 | 信号 | 作用 |
|---|---|---|
| net9 | 时钟 RO 输出 | 采样时钟 |
| net1 | 数据 RO 经 buf | DFF 数据 |
| TRNG_Clk_pre | DFF 时钟 | |
| TRNG1 | DFF 输出 | 原始随机比特 |
| RandomNumber_Serial | 最终输出 | |
