# trace_deepread: n91pk — SpiceAgent CTLE_alenxu AC 设计 + 仿真结果整理

- **session**: `1790142100320_n91pk.messages.json` (alenxu @ hfeg0plg94)
- **size**: 3.46MB, 1017 msgs (530 user / 487 assistant)
- **match_count**: 755 (aether:1653, pyaether:548, netlist:247, schematic:87, calibre:53, hspice:40)
- **shard D domain**: waveform / analog_context（AC 频域仿真响应分析）

## 用户真实意图（提出需求轮，非给根因/修复轮）
- U[2]: 仿真 DFE_alenxu 的 CTLE，扫描 DQC1/C2/R2 找最佳眼宽眼高。
- U[371]（关键需求轮）: "停止，我觉得CTLE设计不合理，peaking增益太高，以DFE_alenxu中CTLE为基础，复制一个CTLE，命名为CTLE_alenxu，取消增益可调，RC可调功能，新增spec：dc_gain=6db，peaking=6dB，peaking中心在5.2GHz，BW大于8GHz"。
- U[388]: 输入共模 0.83V，功耗<4mA。
- U[448]: "仿真结果每次跑完都需要整理好"。
- U[453]: "bw 为 -3db 带宽，dcgain-3db 对应的频点"。
- U[464]: 集成 channel+CTLE 联合眼图、PVT corner、生成 OA 原理图脚本。

## assistant 工具链与真实产物
- 读 `dut_IO_DqPreamp_hier.sp`/`dut_IO_DqBiasGen_hier.sp`/`switch.inc` + golden `ctle_rx_v17/design-report.md`/`dut_ctle_rx_v17_hier.sp`。
- 写 `dut_ctle_alenxu.sp`（v1→v6 迭代，SD+NC3 拓扑：输入对 ntn_lvio 98.9u/0.1u nf=286，负载 rnpo_2t_ckt 0.13u/3.6u，退化 RS rnpo_2t + CS ntn_lvio 700u，NC3 交叉耦合 M5/M6 ntn 15.93u + CCS_MOS ntn_lvio 42u，尾电流 ntn_m 固定）。
- 写 `tb_ctle_alenxu_ac.sp`（FineSim AC testbench，`.LIB /proj/drvqa/V0/model/current/model...`）。
- 跑 `finesim tb_ctle_alenxu_ac.sp -o runs_ctle_alenxu/tb_vN` → `.ma0`(.meas) + `.pa0`(AC 扫描曲线) + `.op`。
- 写 Python 从 `.pa0` 算 BW（dc-3dB 口径）→ `ctle_alenxu_spec_report.txt`。

## 金标准（用户接受的最终结果，runs_ctle_alenxu_best/）
- `tb.ma0`: dc_g=5.9526, nyq_g=12.144, peak_g=12.148, fpeak=5.3088e9, peaking=6.1957
- `ctle_alenxu_spec_report.txt`: DC Gain 5.95dB, Peaking 6.20dB @ 5.31GHz, BW(dc-3dB) 14.79GHz, Idd 1.09mA
- 各迭代 `.ma0`: v1(dc_g=-1.03,peaking=3.93), v5(dc_g=4.68,peaking=4.76), v6(dc_g=6.23,peaking=5.81)

## 本 case 取的判分侧面（B 档 reframe）
- 用户需求 U[448]/U[453]：把每次跑完的 FineSim AC 结果整理成指标报告（dc_gain/peaking/fpeak/BW）并按 spec 判定。
- 交付 = `ac_metric_extractor.py`：读 `.pa0`（差分输出 vr(outp,outn)+j*vi(outp,outn)）+ spec JSON → 算 5 个频域指标 + verdict → JSON。
- assets A = `tb_A.pa0`(=best 真实产物) + `spec_A.json`(用户原 spec：dc_gain≥5.8/peaking∈[5,7]/fpeak∈[4.8G,5.6G]/BW>8G)。
- hidden B = v1/v5/v6 真实 `.pa0`（不同响应）+ `tb_mono.pa0`（合成单调 RC 低通，无过峰边界）+ `spec_B.json`（不同门限：dc_gain≥4/peaking∈[4,9]/fpeak∈[3G,7G]/BW>10G）。
- check.py 内嵌独立参考解析器算期望值，候选在 B 上跑，15 条件 a–o。

## 防硬编码
- 候选只见 A（best.pa0 + spec_A）。check 在 4 个未见 B 的 `.pa0` + 不同 spec_B 上评测；硬编码 A 数值必在 tb_v1(dc_g=-1.03) 上 FAIL。
- BW 用 dc-3dB 口径（用户 U[453]），不是 peak-3dB。
