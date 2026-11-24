# Deepread: bqr3b — CXDP PrimeTime STA 结果评估

**session**: 1795415904283_bqr3b.messages.json
**user**: e0046913 @ hfeg0pkn005 (10.129.2.14)
**mc**: 29 (netlist:189;rtl:15;primetime:14;verilog:9;synopsys:7;pt_shell:7;.lef:4;.gds:3)
**domain**: pnr_signoff (PrimeTime STA 主体)
**NMSG**: 37 / 345KB

## 用户真实意图（逐轮原话）

- **U#0（三问）**：
  1. 评估 `/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/1118_TV1-copy-for-feature/sta/all_out/v1.0_Latest/log` 本次 STA 结果（是否有时序、drv 问题和脚本问题）。作为 flow 搭建工程师，是否可以不用关注时序/DRV，只需关注 flow 能否跑通？
  2. `/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/Datain_20261103_DBC` 是用户给的 CXDP STA flow 验收 database。结合已有资源，最多可以跑哪些模式、以最少任务运行次数、最大化功能覆盖程度，去验证哪些功能？（表格列举）
  3. 想测试带子 harden 的 SoC 级上层 harden STA（子 harden 输入件以 db 或 flatten 格式读入），现有资源是否满足？不满足缺什么？
- **U#36**：评估新路径 `/proj/lacaa/TV1_digital/simdir/yutingq/CxDP/1123-copy-from1118-for-pass/sta/all_out/v1.0_Latest` 下新 design 的 STA 结果。

## 助手关键产物（trace 原文数字）

读取 `sta_pre_WL_ssgnp_v0p675_0c.log` + `pa_cpu_merged_top_qa_summary_ssgnp_v0p675_0c.txt` + flow config (CFG_VARS/CXDP_STA_CFG/proc/*.tcl) + Datain database 结构。

**Q1 答案核心数字**（trace-faithful，来自助手 #35）：
- **Flow 健康**: `CXDP-STA: flow completed successfully.` / `Error(0) Warning(228) Information(31)` / `blackbox_count=0` / `sdc_read_errors=0` / 产物齐全 / runtime 43s / PT 峰值 RSS 3.5GB
- **Setup**: WNS=0.0, TNS=0.0, vio_setup=0 ✅ 干净
- **Hold**: WNS=-0.943, vio_hold=6 ⚠️ 集中在 clock-gating check（clock_uv_tck→APB_CLK），pre-CTS 理想时钟，预期内
- **DRV**: max_transition=1457, max_capacitance=36, max_fanout=400, min_pulse_width=0；大量 0.000 VIOLATED 假阳性（精度假阳性）
- **约束质量**: PTE-060（MBIST/scan clk-mux 未推断 clock-gating check）+ PTE-074（uv_test_clock 缺上升沿），SDC 约束缺口，非脚本崩溃
- **判定**: flow 跑通(PASS)；时序/DRV 是 design/stage 层面问题（pre 阶段预期内），非 flow bug；flow 工程师须鉴别违例是设计真问题还是 flow 注入假问题

**Q2**: Datain database 结构（00_lib_path/01_netlist/02_sdc/03_upf/04_phy_constraint/05_cts_constraint/06_scan_def/07_lec_constraint/08_b2b_list/09_mtbf_sync_list/verdiLog），readme 列出每目录用途；lib_setup.tcl 提供 std/sram/dig_mac/ana_mac lib path；可跑模式表（corner×delay_model×stage 组合）

**Q3**: 子 harden SoC 级 STA 需 db/flatten 子 harden 输入件 + 层次化 STA 配置；现有 database 是 flat netlist，缺子 harden db/CLFModel

## 造题方向

**case 形态**: produce-task（debug-Q&A → produce）。聚焦 Q1（STA 结果评估），这是最可判分的核心意图。
**交付**: `submit.zip` = `eval_sta_result.py`（通用 PrimeTime STA log + QA summary 解析器 → 结构化 evaluation JSON + markdown 报告，含 flow 健康/时序/DRV/约束质量/verdict）+ `sta_evaluation.md`（中文评估报告，覆盖 flow 健康度/时序 setup+hold/DRV/约束质量/verdict 五节）。
**A 档说明**: 真实 /proj/lacaa 路径沙箱不可达（e0031982 身份 permission denied 读 e0046913 文件）→ B 档 synthesized，按 trace-faithful 结构与真实数字合成 sta_log_A + qa_summary_A；hidden-B 用不同 design/corner/数字，零判别 token 相交。

## A/B 隔离设计

- **A**: design=pa_cpu_merged_top, corner=ssgnp_v0p675_0c, delay=WL, PT=U-2022.12-SP5, hold WNS=-0.943 vio_hold=6, DRV 1457/36/400, Warning(228), PTE-060/PTE-074
- **B**: design=pcie_top, corner=ff_v1p1_125c, delay=ML, PT=U-2023.06-SP2, setup WNS=-0.187 vio_setup=3, hold clean, DRV 892/17/256, Warning(174), PTE-040/PTE-053 — 全部判别 token 与 A 不相交
