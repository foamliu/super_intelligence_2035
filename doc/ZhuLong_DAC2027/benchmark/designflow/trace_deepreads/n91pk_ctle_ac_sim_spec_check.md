# n91pk — alenxu SpiceAgent CTLE AC 仿真 + spec 自检 (spice_sim 域)

## trace 元数据
- session: `1790142100320_n91pk.messages.json` (alenxu / hfeg0pkn003, mc=755)
- size: 3.46MB, 1017 msgs (530 user / 487 assistant), 465 tool_use (436 run_commands / 21 read_files / 3 editor / 3 search_codebase / 2 ask_question)
- keywords: aether:1653 / pyaether:548 / netlist:247 / schematic:87 / calibre:53 / pdk:51 / transistor:48 / mosfet:23
- tools 调用统计: 283 pyAether / 144 netlist / 87 schematic / 40 calibre / 4 hspice
- session 结束 exit_code=1 (failed)；model deepseek-v4-flash；cwd /home/alenxu
- trace-keyword 域 = layout_aether，**实产 case 域 = spice_sim**（FineSim AC 仿真子流）

## 主线（从 65 条 user msg 提炼）
SpiceAgent 入口 → 仿真 DFE_alenxu 的 CTLE（扫描 DQC1/DQR1/DQC2 寄存器组合找最佳眼宽眼高）→ 用 channel+CTLE 联合跑 PRBS7 眼图/AC/瞬态/单脉冲 → **认为 CTLE 不合理（peaking 太高）→ 复制并重命名为 CTLE_alenxu，取消可编程性，新增 spec：dc_gain=6dB / peaking=6dB@5.2GHz / BW>8GHz / I=4mA**（后迭代到 U#57 最终 spec：DC=6dB / acgain@5.2G=10dB / BW=10GHz / I<3mA / 输入共模 0.83V / 输出共模 0.8 / 1级 CTLE+NCE / l_min=39n / 尾管 ntn_lv）→ 多轮重设计 → 在 DFE_alenxu 库生成 schematic/symbol → 固化 → 跑 PVT corner。

## 关键真实 artifacts（.75:/home/alenxu/SpiceAgent_Skill/dfe_design/ctle/）
- `dut_ctle_alenxu.sp` — CTLE v13 (精确计算版, SD+NCE, 6 MOSFET 级, w=13u l=39n)
- `dut_ctle_alenxu_best.sp` — CTLE_alenxu final (w=98.9u l=0.1u nf=286, 多尾管并联)
- `tb_ctle_alenxu_ac.sp` — AC testbench (FineSim, .ac dec 200 1e6-2e10, .meas dc_g/nyq_g/peak_g/fpeak/peaking/bw_3db/idd, .op)
- channel: `DMR_ChH.s30p` / `GNRAP_channel.s30p` (S-param)
- eye 分析脚本: `eye_analysis_*.py`, `channel_eye_gen.py`

## .75 EDA 栈（实测探明，trace 里写的路径已失效）
- **FineSim**: `/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim` (V-2023.12-1, linux64)；`FINESIM_HOME=/apps/synopsys/SRB/finesim/V-2023.12-1`
- **模型**: `/apps/imctf/models/G6/model_local/V1_HK_Model_D5_v0d9_t01/V1_HK_Model_D5_v0d9_t01.sp` + `.lib ... incFile_V1_HKMG res_tt`（trace 里 `.LIB '/proj/drvqa/V0/model/current/model.sp' tt` 路径已不存在；agent 的 `./spiceagent` wrapper 会改写）
- **hspice**: V-2023.12 可用；Q-2020 安装损坏（缺 check_cpu/gcc）
- finesim -np 4 跑小 CTLE AC ~5-7s

## .meas / .op 解析要点（本 case 的核心解析契约）
- `<deck>.log` 里 `.meas` 行形如 `       dc_g= 6.4844e+00` / `     peak_g= 8.8820e+00  at= 2.8184e+09` / `     bw_3db=     failed`
- **`.meas ac idd param='-i(vvdd)'` 在 .ac 下返回 ~0（不可靠）** → 必须从 `<deck>.op` 的 `**********Voltage Sources**********` 段 `element  vvdd` 块的 `amps` 行取，`idd[A] = -amps`（amps 为负=电流流出 VVDD）
- `bw_3db` 用 `when vdb(...)='dc_g-3' fall=1`，若频带内增益未降到 dc_g-3 则返回 `failed` → harness 必须记 null

## 实测 ground truth
| netlist | dc_g | nyq_g | peak_g | fpeak | bw_3db | idd (vvdd amps) |
|:--|--:|--:|--:|--:|:--|--:|
| A = dut_ctle_alenxu_best.sp (vbias 0.68/0.72) | 6.4844 | 8.1113 | 8.8820 | 2.8184e9 | 1.4558e10 | -8.322e-4 → 0.832 mA |
| B = dut_ctle_alenxu.sp v13 (vbias 0.66/0.70) | 1.5401 | 3.7481 | 3.7743 | 4.0738e9 | **failed** | -2.070e-3 → 2.07 mA |

## 抽取的 case
- `EDA-Eval-DesignFlow-CTLEAC-001`（spice_sim 域扩量#2，L2 真跑 FineSim）
- 交付件 = `ctle_ac_check.py`：吃 `<testbench.sp> <spec.json> <out_report.json>`，真跑 finesim，解析 .meas + .op，逐条 spec 判定，写 report.json
- 隐藏 B = v13 网表 + 0.66/0.70 偏置 + spec(dc2/nyq3/bw0.5/idd3)，bw_3db 故意 failed 测 robustness
- check.py 12 条件 a-l（见 jsonl test_rationale）
- ref 自验：reference harness 跑 B → raw_meas dc_g=1.5401/idd_a=2.0698e-3/bw_3db_hz=null，spec 4 条 pass=true/false/false/true... 实为 dc✗ nyq✓ bw✗ idd✓，overall=false，与独立 ground truth 完全一致
