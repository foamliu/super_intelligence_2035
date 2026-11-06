# trace deepread: j0t84 — OTA 仿真报告生成

## 来源
- session: `1792549549929_j0t84.messages.json`
- user: zhukaic @ 10.129.33.26 (hfeg0pfn119)
- mc=87, hint: aether:115;hspice:79;synopsys:29;pdk:27;waveview:25;pyaether:25;netlist:24;mosfet:16
- size: 403KB, 1 user turn (peek nturns=1, nedit=9)

## 用户意图（逐字原文 U#0，唯一 produce-demand）
> 读取/home/zhukaic/aether_skill/ota_skill/ota_2stg_sim/目录下的数据结果，生成仿真报告到https://workspace.cxmt.com/folder?guid=549894646957912077路径下

**A-faithful 判定**: 纯提需求（"读取数据结果→生成仿真报告"），未给出根因或修复方案 → 符合 §A ① 选轮规则。

## 真实数据目录（/home/zhukaic/aether_skill/ota_skill/ota_2stg_sim/）
两级 OTA PrimeSim HSPICE 前仿结果（2026-10-19 16:42:38）：
- `ota_2stg_sim.lis` (97KB)：仿真日志 — 电路统计(#nodes=59/#elements=85/#resistors=3/#capacitors=54/#mosfets=22)、BSIM6 Level 77 模型 incFile_G5_CIP、22 MOSFET 实例(xmmp2<3:0>/xmmp0<3:0>/xmmp1<3:0>/xmmn1<3:0>/xmmn0<3:0>/xmmn3/xmmn2, ptn/ntn_m)、LSTB(loop_gain 55.77620dB/phase_margin 80.71403°/pm_freq 9.72e5Hz/gm 44.447874dB/gm_freq 7.83e7Hz)、AC measures(gain 55.776202@100m/pm 80.722124/gbw 973.293456k/f_3db 1.818965k/gain_margin -44.448713/psr_min -6.625865@1000k/psr_dc -70.390492)、transient(offset 418.646739u)、运行时(op 0.02s/58iter, ac 0.03s/221pt, tran 0.00s/1000001pt, peak mem 650.33MB, cpu 0.76s, elapsed 0.90s)、user zhukaic/host hfeg0pfn119
- `ota_2stg_sim.ma0` (297B)：AC measure $DATA1 表(gain pm gbw f_3db gain_margin psr_min psr_dc temper alter#)
- `ota_2stg_sim.mt0` (186B)：transient measure(offset temper alter#)
- `ota_2stg_sim.ic0` (791B)：直流工作点 .nodeset(fb 800.418647m/inn 800.418647m/inp 800m/net0 627.885330m/net1 368.594004m/net3<0-3> 602.136666m/net6 627.885330m/net8 534.652349m/out 900.471006m/vcc! 1.025/vss! 0)
- `ota_2stg_sim.pa0` (412B)：22 MOSFET 实例列表
- `ota_2stg_sim.st0` (4283B)：license/状态(USER zhukaic/HOSTNAME hfeg0pfn119/primesim license/option search paths/ac 221 sweeps/tran 10 sweeps)

## agent 工具链与产物
- U#0 提需求 → agent read_files 读数据目录 → editor 写 ota_2stg_sim_report.md (4831B) + ota_2stg_sim_report.html (8134B)
- 后续(Oct 26): gen_ac_plots.py + make_plots.py + ac_metrics.json + ota_2stg_sim_ac_report.html/md (AC 波形报告，含 img_ota_lstb_bode.png/img_ota_ac_psr.png base64) — 后续 AC 报告依赖 WaveView 读 .ac0 二进制，本轮不取

## user-accepted 金标
- ota_2stg_sim_report.md：解析 .lis/.ma0/.mt0/.ic0/.pa0/.st0 → 结构化 markdown（电路概况/直流工作点/AC 指标/LSTB/瞬态/计算资源/告警/结论）
- 关键提取：gain 55.78dB, pm 80.72°, gbw 0.97MHz, f_3db 1.82kHz, gain_margin -44.45dB, psr_dc -70.39dB, psr_min -6.63dB, offset 418.65µV, nodes 59, mosfets 22, temp 85℃, vcc! 1.025V, v(out) 900.47mV

## 合成决策
- 真实数据文件全为文本、可离线 Python 解析（无需 EDA 工具/二进制波形）→ **A 档 faithful**
- asset A = 真实 6 数据文件（.lis 取 faithful 子集保留全部真实数据值，去掉 BSIM6 model-card dump 4700 行，与 #316 ToggleCounterBindGen 子集化真实 cell_define 同先例）
- hidden B = 合成全不同值（gain 62.42dB/pm 68.31°/gbw 2.48MHz/f_3db 2.10kHz/gm -52.12dB/psr_min -5.21dB/psr_dc -78.14dB/offset 352.17µV/nodes 73/mosfets 28/temp 27℃/vcc 1.2V/vout 1.082V/设计名 ota_5stg_iref/节点名 na/nb/nc/nd/user liuwen）
- 交付接口：`python3 gen_ota_report.py <data_dir> <out_report_md>` + submit.zip
- check：subprocess 跑候选脚本于 hidden B → 16 条件 a-p 断言 B 值 + 交叉输入护栏禁 A 专属串
