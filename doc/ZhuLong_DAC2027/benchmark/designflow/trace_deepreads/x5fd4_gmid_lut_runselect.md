# Deepread: 1792041709940_x5fd4 — gmid LUT 构建 (run-selection)

- **session**: `1792041709940_x5fd4.messages.json`
- **user / host**: t0002801 / hfeg0plg49
- **match_count**: 119 (keywords: netlist:1942; schematic:575; analog:445; cmos:418; waveview:334; hspice:123)
- **NMSG**: 157
- **domain**: characterization (B shard)
- **case_id**: EDA-Eval-DesignFlow-GmidLutRunSelect-001
- **track**: faithful (A-档, 用户原话作 prompt)

## 用户意图 (A-档 goal turn, msg 26/27, 逐字原文)
> 我重新跑了仿真，结果在 /proj/ddaop/V0/workdir/t0002801/simulation/sijie/gmid/platform/Results/，帮我看看能否建立gmid查找表？如果可以，在这个路径下面创建 /home/t0002801/gmid_LUT/

(此轮是"提出需求/表达目标"，用户未给根因或修复方案 → 合格 A-档任务说明)

## 真实对话流
1. **msg 0**: 用户报 aether 仿真错误 — `MN0' has 0 node and ntn_lv has 4 node` (subcircuit pins/ports mismatch)。
2. **msg 1-25**: 助手定位根因 — 网表 `gmid.netlist:31` 生成了 `MN0 ntn_lv` (0 节点)，而 `ntn_lv` subckt 有 4 端口 (DRN GATE SRC BULK)；正确应为 `MN0 (net3 net5 0 0) ntn_lv`。原理图 MN0 的 4 个 pin 全悬空。
3. **msg 26**: 用户重跑仿真，要求建 gmid 查找表到 `/home/t0002801/gmid_LUT/`。
4. **msg 28-40**: 助手列 PlatRun.7~10，逐一查 gmid.log / gmid.netlist / alps.out。发现 **PlatRun.7 成功** (Simulation Completed, 0 error)，PlatRun.8/9/10 仍是 `MN0 ntn_lv` (原理图未修复)。
5. **msg 41-98**: 助手尝试解析 PSF。`dc.op` 只有最后一个 sweep 点 (l_n=2um) 的 OP (因 `annotate=status`)；51 点的 per-sweep Id 在二进制 `dc.dc` (PSF)，缺解析工具。
6. **msg 100-149**: 助手从 dc.op 提取单点 OP，写 `create_lut.sh` (shell-runner profile) 在 `/home/t0002801/gmid_LUT/` 生成 4 文件。
7. **msg 156**: 助手总结 — 仅 l_n=2um 单点 OP 可用，建议重扫 Vgs 获完整 LUT。

## 真实产物 (用户接受)
`/home/t0002801/gmid_LUT/` 含:
- `gmid_LUT_PlatRun7.json` — 单条目 OP (l_n=2um)
- `gmid_LUT_PlatRun7.csv` — 同数据 CSV
- `gmid_LUT_sweep.scs` — Vgs 扫描的 ALPS 网表
- `README.md`

### 真实 OP 值 (PlatRun.7, l_n=2um, ntn_lv NMOS W=2um, Vgs=0.7 Vds=1.2 Vbs=0)
| 参数 | 值 |
|---|---|
| id | 3.03669e-05 (30.37 uA) |
| gm | 2.00772e-04 (200.77 uS) |
| gm/Id | 6.61155 S/V |
| gds | 1.28364e-06 |
| gmb | 2.39821e-05 |
| vth | 0.381413 |
| vdsat | 0.333991 |
| ft | 1.20768e+09 |
| vearly | 23.6569 |
| self_gain | 156.408 |
| cgg/cgs/cgd | 2.6459e-14 / 2.41956e-14 / 4.65543e-16 |

Sweep: l_n 36nm→2um, 51 点。成功网表 `MN0 (net3 net5 0 0) ntn_lv w=2u l=l_n nf=1`。

## 关键鉴别点 (本 case 的难度核心)
- **run-selection**: 4 个 PlatRun 里只有 1 个成功 (网表有 `MN0 (...)` 4 节点 + log "Simulation Completed")，3 个失败 (`MN0 ntn_lv` 0 节点 + log "Error")。SUT 必须从 netlist/log 判别，不能盲取第一个。
- **dc.op 解析**: text 格式 `#### mosfetLevel77:` 块 + `key = value`；sweep 变量 `l_n = 2.000000e-06.` (注意尾句点，trace 的 psf_reader 用 `l_n\s*=\s*([\d.eE+\-]+)\.` 正则)。
- **隐藏 B**: 不同成功运行 (PlatRun.3, l_n=1.5um, Vgs=0.65, Vds=1.0, W=1.5um) + 失败 PlatRun.5，验证脚本泛化 (非硬编码 A 值)。

## 判分
- 16 条独立断言 (a-p)，ref 16/16 PASS，3 个负样本 (empty/print-only/core-deleted) 全 FAIL，hardcode-A 在 B 上 FAIL (跨输入)。
- L2 (真跑 = 解析真实 EDA 仿真输出格式 dc.op/ALPS log/netlist，非纯 Python 复刻)。

## 备注
- 与已有 `EDA-Eval-DesignFlow-GmidLut-001` (session d7cbo, HSPICE .op Vds=0→Cgg=0 陷阱) 不同：本 case 强调 **多 PlatRun run-selection + 网表断连诊断**，是同一用户的不同 session、不同失败模式。
- 原始 /rundata 仿真文件对 e0031982 不可读 (permission denied)，附件按 trace 中助手读到/引用的真实值重建 (dc.op/netlist/log 内容与 trace 一致)。
