# Deepread: 0ekf9 — DFT TestMAX demo launch flow

- **session**: 1793927271206_0ekf9.messages.json
- **user/host**: e0030085 @ hfeg0pkn002 (10.129.2.11), mc=352
- **size**: 1.23MB, 412 msgs
- **keywords**: synopsys:2253; rtl:409; verilog:259; vhdl:148; drc:92; dc_shell:61; hspice:50; netlist:24
- **tools col**: hspice:48, netlist:24, pyAether:4, synthesis:2

## User intent (verbatim)
- USER#1 (msg0): `去/apps/synopsys`
- USER#2 (msg4): `根据tetsMAX 给我一个testMax demo`  ← **A-faithful produce-task seed**
- USER#3 (msg59): `实际运行这个Demo 帮我生成完整的启动脚本/环境变量`  ← **核心 produce-task**（提出需求，未给根因/方案 → A-faithful ✓）
- USER#4-10: 仿真/波形调试（怎么跑仿真、run_sim.py 报错、打开波形、verdi/gtkwave shared-lib 错、用 verdi 打开波形）→ 后续诊断轮，不作 A 档任务说明

## Assistant 行为（msg4 → msg175）
1. 发现 `/home/e0030085/Documents/dft_testmax_demo/` 已存在完整 demo（rtl/adder_top.v, add_sub_unit.v, dft_top.v, tb_dft_top.v; scripts/dft_compile.tcl, atpg.tcl; results/*.rpt）
2. 探测 TestMAX 安装 (`/apps/synopsys/testmax/X-2025.06`, `TestMAX_DFT/syn/V-2023.12-SP4`, `TestMAX_ATPG/txs/W-2024.09`) + VCS (`vcs/X-2025.06-SP2-1`) + Verdi
3. 生成 deliverable（launch flow，graceful degradation：无真实工具时回退到预生成结果）：
   - `setup_env.sh` — TESTMAX_HOME/VCS_HOME/VERDI_HOME + PATH + aliases(dft/tmax/vcs_sim/go_dft/wave)
   - `run_full_flow.sh` — 子命令分发(all|check|dft_only|atpg_only|simulate) + run_dft_compile/run_atpg/run_simulation + 彩色 print_ok/warn/err + 环境检查
   - `run/run_dft.sh` — dft_shell→dc_shell / tmax→tetramax 工具回退 + 无工具时 heredoc 写预生成 dft_compile.log(4 chains/75 cells/21-18 len)/atpg.log(94.58%/88.26%/124 patterns/1618 faults)
   - `run/sim_filelist.f` — RTL + TB + `+define+SCAN`
   - `run_sim.py` — VCS wrapper，无 VCS 时生成 simulation.log("ALL TESTS PASSED") + 调 gen_waveform.py 产 VCD
4. USER#4-10: run_sim.py 反复修错（路径/license/iverilog fallback）、gen_waveform.py、vcd_wave_viewer.py、view_wave.py、launch_verdi.py、check_verdi.sh、try_verdi.py、run_verdi.sh（verdi libxkbcommon 缺失 → gtkwave/verdi 调试）

## 金标准（trace 末尾用户接受的真实产物）
- `/home/e0030085/Documents/dft_testmax_demo/setup_env.sh`（2280B .json 元数据，setup_env.sh 实际 ~2.5KB）
- `run_full_flow.sh`（~5KB，完整子命令分发 + 三 phase 函数 + 彩色 + 环境检查）
- `run/run_dft.sh`（~4KB，工具回退 + 预生成 fallback）
- `run/sim_filelist.f`（RTL+TB+define）
- `run_sim.py`（~3KB，VCS wrapper + sim log 生成）
- ssh 可读：10.129.2.11:/home/e0030085/Documents/dft_testmax_demo/

## 现有 demo 项目（A 输入 = assets）
- `rtl/adder_top.v`（8位累加器+扫描端口，9-bit sum_reg, 3-bit state_cnt, valid_flag）
- `rtl/add_sub_unit.v`（16位 加/减单元，17-bit result_ff, pipe_stage）
- `rtl/dft_top.v`（顶层：u_adder + u_alu 实例化，scan 链贯穿）
- `rtl/tb_dft_top.v`（TB：Phase1 功能(10+5=15, 20+5=25) + Phase2 scan shift 75-bit + Phase3 cross-check, $dumpvars VCD）
- `scripts/dft_compile.tcl`（DFT Compiler: analyze/elaborate/link + SDC + set_dft_configuration -scan + set_scan_configuration -chain_count 4 + insert_dft + report_scan_path + create_test_protocol + write scanned.v）
- `scripts/atpg.tcl`（TetraMAX: read_netlist + run_build_model + read_test_protocol + run_drc + set_fault_type -stuck_at + add_faults -all + create_patterns -auto + write_patterns stil/verilog/wgl）
- `results/scan_path.rpt`（4 chains, 75 cells, max 21 / min 18, TestMAX-2023.12）
- `results/atpg_summary.rpt`（DT 1428, UD 152, AU 38, total 1618, TC 94.58%, FC 88.26%, 124 patterns）
- `results/simulation.log`（"ALL TESTS PASSED", key_in=10→15, 20→25, 0x55→85）

## 判分设计
- **A 档**：prompt = USER#2 + USER#3 逐字；assets = 现有 demo(rtl/scripts/results)；deliverable = `gen_dft_launch_flow.py` + `spec_a.json`（spec-driven 生成器，CLI: `python3 gen_dft_launch_flow.py spec.json outdir` 产 5 个 launch 脚本）
- **hidden B**：spec_b.json（异构：不同 user/root/RTL 名/工具版本/scan chain 数/cell 数/ATPG 覆盖率/fault 数）
- **check()**：跑生成器 on spec_b → 16 条断言（zip 结构 / setup_env 工具路径+PATH+aliases / run_full_flow 子命令分发+三函数+彩色 / run_dft 工具回退+预生成 fallback 含 B scan 数 / sim_filelist 列 B RTL / run_sim py_compile+VCS 引用 / subprocess `run_full_flow.sh check` exit0 / subprocess `run_dft.sh` exit0+fallback log 含 B Total Scan Cells / 反硬编码 A 值不现 / 3-seed 确定性）
- 真实 TestMAX/VCS 不可在判分环境跑 → 全部靠 graceful-degradation fallback 路径 subprocess 验证（L1-static + L2-subprocess）

## 档位
- A-faithful（USER#3 提出需求未给根因）· domain=eda_other · L1-static+L2-subprocess
