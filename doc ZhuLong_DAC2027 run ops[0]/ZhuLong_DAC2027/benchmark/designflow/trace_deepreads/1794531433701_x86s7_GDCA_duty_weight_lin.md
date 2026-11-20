# Trace deepread — 1794531433701_x86s7 (curryxu @ hfeg0pkn002)

- **user/host**: curryxu / hfeg0pkn002 (10.129.2.13)
- **session**: 1794531433701_x86s7.messages.json, 148 msgs, mc=109, domain=spice_sim/characterization
- **mtime**: 2026-11-12, 写入于 11/13 全量扫描 ssh_eda_search_20261113_131349（fresh @ mc≥10）
- **keywords**: netlist:536;hspice:173;pdk:111;schematic:74;transistor:22;...

## 设计背景
DDR4 PLL **GDCA**（Gate Duty Cycle Adjust）：一个 3-bit moscap DAC 调节占空比。bit0/bit1/bit2 的 moscap 宽度按 `width*1 / *2 / *4`（电容 1:2:4 二进制配比），目标让数字码 P<2:0> 线性改变 duty。
真实仿真产物：激励 `PLL_GDCA_tb_6G.sp`、网表 `PLL_GDCA/hspiceD/schematic/netlist/netlist`、测量 `result.mt0.csv`（FineSim/HSPICE alter sweep，5 档 width 100/200/300/400/500nm）。

## 用户 4 轮意图
- U0 (msg0): 「这个激励算出来的 duty 的变化不够线性，我需要怎么优化电路结构或者 moscap 的尺寸参数？」+ 给 .sp / netlist / result.mt0.csv 路径
- U1 (msg54): 「根据我实测的权重表，算出把 bit1/bit2 放大到多少能恢复 1:2:4 并保证单调」← **本 case 选取的核心可做任务**
- U2 (msg82): 「需要」→ 要求落地为改网表补丁脚本 + 复测重算脚本
- U3 (msg102): 报错 `failed to find correct binning model for mosfet 'xnm88.main'(nlvt l=0.02565u w=3.42u)` —— PDK binning model 缺失（旁支，未纳入 case）

## agent 工具链（关键产物）
1. `analyze_duty.py` —— 解析 result.mt0.csv，按 P<2:0> 8 码提取 duty，算单 bit 权重（drop_from_000），输出 5 档 width 的权重表。
2. `compute_scale.py` —— 三物理模型（仿射 `w=a·n+b` / 幂次 `w=c·n^p` / 饱和 `w=a·n/(n+b)`）最小二乘拟合，**仿射残差最小**（SSE≈0.0005~0.003），反解 n1=2w0、n2=4w0，给 scale factor 与新电容值。
3. `resize_netlist.py` —— 按 300nm 基准把 8 个目标 moscap 的 `w=` 改写（bit1 2u→4u、bit2 4u→10u），另存 netlist_lin，diff 验证仅 8 行改动。
4. `make_tb_lin.py` / `recalib.py` —— 指向新网表的激励副本 + 复测自动重算。

## 实测权重表（duty_percent_drop_from_code_000）
| width | bit0(n=1) | bit1(n=2) | bit2(n=4) | 实现比(应 1:2:4) |
|--|--|--|--|--|
| 100 | 1.201 | 1.359 | 1.757 | 1.13 : 1.46 |
| 200 | 1.376 | 1.796 | 2.492 | 1.36 : 1.99 |
| 300 | 1.583 | 2.160 | 3.157 | 1.45 : 2.18 |
| 400 | 1.782 | 2.501 | 3.748 | — |
| 500 | 1.953 | 2.836 | 4.261 | — |

width=100 8 码 duty: 49.41 48.21 48.05 46.73 47.65 46.29 46.09 44.66（011→100 回跳 +0.92，非单调）。

## 仿射拟合反解结果（agent 输出，已复算核对一致）
- width=100: a=0.1873, b=1.0020 → bit1 ×3.74(2u→7.5u), bit2 ×5.08(4u→20.3u)
- width=300: a=0.5209, b=1.0845 → bit1 ×2.00(2u→4u), bit2 ×2.52(4u→10.1u)
- 恢复 1:2:4 后 MSB=4w0 > 低位和 3w0，裕量=1 个 LSB(w0)，8 码 drop 严格单调递增 → 单调。

## case 取舍
- A 档不可行：真实网表在 `/proj/m2701/V0_DDR4/...`，受 FineSim license + 项目目录权限限制，无法进 SUT 沙盒。
- B 档合成：用真实 trace 的实测权重表（width=100 作 visible A，width=300 作 hidden B），合成自包含 Python 求解器 `compute_scale.py`，check 在 hidden B 上真跑 + 独立复算仿射 ground-truth 比对 + visible A 交叉 guard。
- domain = characterization（占空比 DAC 权重线性化外推），layer = L2（subprocess 真跑 + 独立复算，非纯文本比对）。
- 12 条独立断言（a–l），ref 12/12 PASS，2 negative（naive_ratio / stub_hardcode）全 FAIL，3 假提交（空壳/print-only/core-removed）全 FAIL。
