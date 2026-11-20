# deepread: 1794224570631_afkmz — sim_setup folder analysis Q&A

**trace**: zjqiao @ hfeg0pgn043 (IP 10.129.35.142), session `1794224570631_afkmz.messages.json` (418KB, 24 msgs, 19 user turns / 5 assistant turns), mc=20, D-domain keywords: lvs:659;verilog:250;netlist:101;pex:34;analog:5;synopsys:3;skipper:1;calibre:1.

**fetch path**: eda_flow open_session → ssh from .75 (hfhds201) to 10.129.35.142 → scp /home/zjqiao/.cline/data/sessions/1794224570631_afkmz/1794224570631_afkmz.messages.json → /tmp/afkmz.messages.json (418KB). 解析 24 msgs (dict format: version/updated_at/agent/sessionId/messages/system_prompt).

## 用户真实意图 (U#0 逐字, msg[0])

> `/proj/drvqa/V0/setup/sim/sim_setup这是我仿真的配置文件夹，请帮我分析一下其中各个文件夹及文件的作用`

用户给出一个仿真配置文件夹路径，要求分析**每个子文件夹及文件的用途**。这是 folder-structure-grounded analysis Q&A — 用户没有要求改任何东西，只要"看懂结构 + 说明用途"。按 2026-11-15 用户令「Q&A-investigation 造-able」，此类任务 revival-from-parked (旧规则 r608 parked 因 'sim_setup folder analysis Q&A not produce-task')。

## assistant 工具链 (msg[1-22])

- msg[1]: `list_allowed_files` depth=3 → 列 sim_setup 根目录
- msg[3]: 6 个并行 `list_allowed_files` (Control/Netlist/Normalsim/finesim_option/Powervoltage/stdspf/verilogA/post_sim/compare/Compare/Bin)
- msg[4-15]: 11 个 tool_result 返回各子目录的 entries (JSON)
- msg[16]: `read_files` 读关键文件 (stdspf_file/spf.list/cosim_model.v/Bin/vcaps_3c_stdspf.pl/Control/control.finesim_promd_spfba_A1/stdspf/20261020/invLx1.spf_RCC) + `list_allowed_files` verilogA/cosim_timing_param/Bin/measure
- msg[17-21]: tool_results (verilogA/Bin/measure/stdspf/20261020 列目录)
- msg[20]: 补充 `list_allowed_files` stdspf/20261020 + `read_files` invLx1.spf_RCC + control.finesim_promd_spfba_A1 头 30 行
- msg[22]: 空 user msg (continuation)
- msg[23]: **assistant 综合分析金标准** (markdown, 11 sections)

## 金标准 (msg[23] 摘要)

**项目背景**: DDR5 DRVQA (Driver/Receiver 验证与质量保证), Synopsys **FineSim** SPICE 仿真器。

**11 子目录用途**:
1. `Control/` — FineSim .control 主入口 (control.finesim_promd_spfba / _vcap / _A1 / _CRG / _ODT / _nano 等, .option finesim_mode=promd + module 精度层级 + variant tags A1/A2/nano/ODT/PD/CRG/UVW/read/blown/hf/RAS/VREF/compress)
2. `finesim_option/` — .option 配置 (spfba/vcap/spf_block/vcap_block, finesim_spfprb/finesim_pwrloadmodel/vdd)
3. `Netlist/` — 8 Bank Group 顶层网表 (bnktop_net_connect_BG0..BG7.sp + BankLogic_BG0..7_ignore + netlist_spare)
4. `stdspf/` — 标准单元 SPF 寄生库 (stdspf_file 923 行 + spf.list .inc form + 20261020/ 子目录, StarRC RCC, DSPF 1.3, invLx1/and2Lx1/bufCSx32/mx2LVSx1_pc60 .spf_RCC)
5. `post_sim/` — 后仿配置 (CCK/pex/SPF 三子目录, cckfile/hcell/skip_cell/spf_cell)
6. `Powervoltage/` — 电源激励 (Pattern_Power*.sp / Array_vcap_Param*.sp / Zpower_force.inc, HTOL/LTOL/RAS/RDBI/VREF 场景)
7. `Normalsim/` — 标定 CSV/TXT (Ivdbias_spf.csv/Vdbias_spf.csv/tdqs2dq_spf.csv/wica_spf.txt/zqcode_spf.txt/vblh.csv/viso.csv 等, _spf vs _vcap 对照)
8. `verilogA/` — Verilog-A 行为模型 (cosim_model.va 含 module IO_CABufCore/D_YioDiffSA/T_CmFsLatchX6Unit + cosim_timing_param/ per-corner .dat)
9. `Bin/` — 自动化脚本 (vcaps_3c_stdspf.pl 3415 行 Perl 核心 + compare_wave_ddr5.pl + createControlFile/createCornerFile/create_siinp.pl/charFFLat/meas.perl/shcal.perl/runBiasTrimAccuracy/runCrcAlertChk.pl/vcap_BA/vcap_Pre + measure/ 子目录 run_check_*.py 10 个 + vsim_script/)
10. `compare/` — 波形比对配置 (config_X4/X8/X16/Alert/pincheck/pincheck_compress)
11. `Compare/` — 波形比对配置 (config_Compress/pincheck/compare_wave_ddr5.pl/meas_crc_alert.sp/meas_odt_tadc.sp/meas_odt003_tadc.sp)

**整体架构**: 4 种仿真场景 (VCAP 前仿 / SPFBA 后仿 / Block 级前仿 / Block 级后仿) × variant (A1/A2/nano/ODT/PD/CRG/UVW/read/blown/hf)。

用户接受该分析 (msg[22] 后无后续修正)。

## reframe (A档 trace-faithful produce-task)

套 r880/r884/r887/r889 folder-structure-grounded explain Q&A 范式 → 候选交付 `analyze_sim_setup.py` (扫 sim_setup 目录 → 分类各子目录 → 推断仿真器/项目背景 → 结构化 JSON)。判分用合成平行场景 B (LPDDR5 PHY + HSPICE, 8 子目录, V1/V2/TT/FF/SS variant, INVX1/NAND2X1/BUFZ4/MUX2X1 单元, LP5_PHY_RX_TOP/LP5_IO_SAMP/LP5_WS_LATCH Verilog-A, VDD_Pattern*.sp) 反硬编码，B2 (HBM3 PHY + Xyce) 反硬编码 B1，B3 空目录优雅。

资产 A = 真实 B-grade 重建 sim_setup_A/ (10 子目录, 真实文件名 + 真实 FineSim .option/DSPF 1.3/Verilog-A 签名, 最小 stub 内容) — 真实 sim_setup 在 /proj/drvqa/V0/setup/sim/sim_setup (xxchen 私有 /rundata 类路径, 权限/体积不可直接复用)。
