# Deepread — n693x (dsgao @ hfeg0pkn001) — Id-Vg DC sweep Vth extraction

## trace meta
- session: `1795052470117_n693x.messages.json` (dsgao @ hfeg0pkn001, 10.129.32.189)
- mtime: 2026-11-19, 197 msgs, 904KB, lead agent (zhulong)
- match_count: 116 (netlist:258;drc:233;schematic:162;synopsys:127;hspice:62;transistor:40;analog:20)
- shard/domain: **D / waveform** (FSDB 波形分析 + FineSim .dc 仿真 Vth 提取)
- agent: lead

## 用户轮（A-faithful 选轮）
- **U#1**: `<user_input mode="act">Path: .../Result/input.fsdb 分析一下M5 和 M1 的开启电压</user_input>` — 从 FSDB 瞬态波形分析 M5(NMOS ntk_hv) 与 M1(PMOS ptk) 的开启电压。agent 定位 netlist(R_GrDecGut_Sim.sp)、识别器件(XMM1=PMOS ptk gate=ra543i src=grdecpwr; XMM5=NMOS ntk_hv gate=ra543i src=grpdncom)、dump FSDB 61001 样点，发现瞬态 ra543i 是逻辑阶跃(~0.1ns)，无法读精确 Vth。
- **U#2**: `补做一次慢 sweep 的 Id–Vg 直流仿真来给出精确 Vth` — agent 搭 FineSim .dc sweep testbench（两器件各自，Vg 0→VDD 1mV/点），解决 LD_LIBRARY_PATH/libstdc++ 冲突（GCC 11.2 libstdc++ GLIBCXX_3.4.29），跑出 .pd0 print 表，用恒定电流法 + max-gm 线性外推法提取 Vth，存 CSV。

## 金标准（assistant 末轮）
- M5 = NMOS ntk_hv, W=3.726µm L=545nm, VDD=3.4V, corner SS/0.94V/-40C
- M1 = PMOS ptk, W=1µm L=479nm
- .dc sweep → input.pd0 (1mV/点 text print 表: v(ng), i(vd))
- Vth 提取: ① 恒定电流法(CC): Vgs@|Id|=Iref ② 线性外推法(ELR/max-gm): max gm 点切线外推至 Id=0

## 合成 case（L1 reframe, fixture-driven）
- task_id: `EDA-Eval-DesignFlow-IdvgVthExtractProduce-001` (waveform, L1, k≥12)
- 真实契约: 交付 `vth_extract.py` + `report.json`（解析 FineSim `.pd0` .dc print 表，按恒定电流法 + max-gm 线性外推法提取每器件 Vth，输出结构化 JSON）
- A = idvg_M5_A.pd0 + idvg_M1_A.pd0 (Shichman-Hodges 生成, NMOS ntk_hv W=3.726u L=545n Vth0=0.68 VDD=3.4 + PMOS ptk W=1u L=479n Vth0=-0.72) + manifest_A.json
- hidden B = idvg_J2_B.pd0 + idvg_J7_B.pd0 (不同器件 NMOS ntk_lv W=2u L=180n Vth0=0.52 VDD=1.8 + PMOS ptk_lv W=1.5u L=180n Vth0=-0.55, 不同 corner FF/1.1/125C) + hidden_manifest.json — Vth/曲线/规模全异, 反硬编
- A' = 内联第三器件对 (NMOS W=5u L=300n Vth0=0.60 + PMOS W=3u L=300n Vth0=-0.65, VDD=2.5), check.py 生成 SUT 不可见
- check.py ≥12 断言: a zip 2 文件 / b py_compile / c report.json 顶层键 / d B 两器件均解析 / e CC-Vth 容差 / f ELR-Vth 容差 / g gm_max>0 / h Id@Vth_cc≈Iref / i 单调性 / j PMOS |Vgs| 转换正确 / k A' 交叉(不同 Vth 击穿硬编) / l 确定性 3-seed / m 负样本守卫
- 反硬编: B 与 A/A' 的 Vth/曲线/w/L/VDD 全维不相交; A' 交叉击穿任何硬编码 A 或 B 答案的 stub
