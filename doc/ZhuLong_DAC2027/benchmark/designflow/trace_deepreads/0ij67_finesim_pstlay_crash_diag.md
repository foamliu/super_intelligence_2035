# Deepread — 0ij67: FineSim post-layout sim 崩溃诊断 (log/deck-grounded crash-diagnosis Q&A)

**Session**: `1794444455754_0ij67` | **User**: reedchen | **Host**: hfeg0pkn003 (10.129.2.12)
**mc**: 28 (per-host) | **Domain**: schematic_netlist
**Agent**: lead | **NMSG**: 23 | **User_input turns**: 1 (clean single-intent)
**旧判定**: parked "目录下模块仿真一直跑不出来帮我分析原因 = debug Q&A sim-fail diagnose; mc28" (2026-11-13 dailylog-1113 post1109 peek r570)
**11-15 revival**: ✅ 复活 — 真实用户意图=post-layout sim crash 根因诊断，单轮闭环可造，gold=结构化崩溃诊断（事实断言，可 falsify）

---

## 1. 用户原话（A档 verbatim，唯一 propose-need 轮）

**U#0 (msg#0)**:
> `/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_top_ChannelLeft/sim_smoke/output/ 我这个目录下的模块仿真一直跑不出来，请你帮我分析原因`

= "the module simulation in this directory keeps failing to run, please help me analyze the cause"

模式：log/deck-grounded post-layout simulation crash diagnosis Q&A（仿真崩溃根因诊断）。
旧规则判 "analysis not produce" → 11-15 令复活为合法 debug-Q&A 子型（D 域 crash-diagnosis 子型，承 r785/r787 debug-Q&A pattern，但 fixture=仿真日志+SPICE deck 而非源码）。

## 2. 金标准（assistant 最终诊断，msg#22）

**根本原因**: 仿真在 DC 初始化阶段因收敛失败（SIGQUIT 崩溃）而中断。

**证据链（4 条，全部结构化、可程序化检测）**:

### 证据 1 — 崩溃证据（core dump + 日志截断）
- `output_TT_0.8V25C.log` 仅 241 行，最后一行停在 "Starting DC Initialization" + "pseudo-tran final try used gshunt=1.000000e-12"
- 同目录有 `core.50786` 19.2GB（SIGQUIT 崩溃 dump）
- 仿真器 = FineSim（log banner），host = hfeg0pkn003，PID = 50786

### 证据 2 — 11 个浮动 bias/control 节点（主因）
log 中 `no dc path to ground` / `added to floating node` 警告覆盖 11+ 个 bias/control 节点：
- `biasp`, `biasn_i`, `glbref03mid`, `glbref06mid`（bias 网络）
- `actcmd<0..N>`, `actadr<0..N>`（command/address 控制）
- `chipprobeenlo`, `vmwln!`, `pwron3_i`, `pwronlsvwlp_i`, `disvpgintbuscompbuf_in`
- 根因：`XI_ChanLeft` 子模块**独立运行**（standalone），上层驱动这些 bias/control 的模块未实例化 → 节点悬空无驱动 → DC 无法收敛

### 证据 3 — `.probe v(*)` 探测过载（次因）
- `template_rd.sp` 第 83 行 `.probe v(*)` 匹配 **19715156** 个节点 → ~39GB 内存压力
- 而 `SignalList.txt` 只列了 ~10 个真正需要观测的信号
- 巨大 probe 表 + core dump 19.2GB 共同促成 OOM/SIGQUIT

### 证据 4 — 未定义参数 `pvdiv`（三因）
- log 警告 "undefined parameter pvdiv"
- `template_rd.sp` 第 42 行 `.param pvdpg=pvdiv` 引用 `pvdiv`，但 deck 中无 `pvdiv` 定义
- 导致 `pvdpg` 取默认值，可能影响 sub-circuit 参数正确性

### 证据 5 — PVT 角数不一致（四因）
- `run_all_pvt.sh` 注释宣称 "9 corners"（含 TYP_98_RCC 等）
- 但实际只 `bsub` 提交了 1 个角（TT 0.8V25C）
- named_count=9 vs submitted_count=1，mismatch=True

## 3. 资产可达性

原 `/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_top_ChannelLeft/sim_smoke/output/` 在 10.129.2.12，直接 ssh 超时，经 .75 eda_flow sandbox ssh 可达。
从 trace read_files tool_results 提取 6 个 A 文件（去行号前缀）：
- `output_TT_0.8V25C.log`（241 行，仿真日志，FineSim banner + DC init crash）
- `output_TT_0.8V25C.elog`（elog header）
- `template_rd.sp`（SPICE deck，含 .param pvdpg=pvdiv + .probe v(*) + XI_ChanLeft）
- `stimulus_rd.sp`（stimulus deck）
- `SignalList.txt`（~10 个信号）
- `run_all_pvt.sh`（PVT 提交脚本，9 named / 1 submitted）

## 4. hidden B（不进 SUT 沙盒）

identifier-renamed structural variant，零 A 标识符重叠：
- FineSim→SpcFine, finesim→spcfine, spicehd→hdspice, fsdb→bsdf
- ChannelLeft→RimRight, XI_ChanLeft→XR_RimRight, ddgoa→gaodd, reedchen→neilreed
- biasp→polb, biasn_i→poln_i, glbref03mid→gbref03mid, glbref06mid→gbref06mid
- actcmd→cmdact, actadr→adract, chipprobeenlo→probechiplo, vmwln!→wvmnl!
- pvdiv→vdpiv, pvdpg→pdpgv, pseudo-tran→tran-pseudo, gshunt→shuntg, gdcpath→dcgpath
- hfsds512→hfsds513, bsub→jsub, fqueue3→qf3, TYP_98_RCC→TYP_99_RCC
- vss!→gnd!, vcc!→pwr!, 19715156→19876543
- 其它 pwron3_i→pwr3on_i, pwronlsvwlp_i→pwrlsvpwl_i, disvpgintbuscompbuf_in→vpgdisbuscmp_in, analog_controlrefab_l→analog_ctrlrefab_l

B 保留全部 4 类问题结构（DC init crash + 11 floating nodes + .probe v(*) overload + undefined param + 9-named/1-submitted mismatch），零 A 标识符泄漏（word-boundary regex 验证 53 A_FORBIDDEN token 全无匹配）。

## 5. candidate.py 设计

通用 log/deck parser（无硬编码标识符），CLI: `python3 candidate.py <deck_dir>`：
- find_log/find_elog/find_deck/find_stimulus/find_signal_list/find_run_script/find_question 自动发现文件
- strip_prefix 去行号前缀
- parse_crash_evidence: simulator/host/pid/last_phase/log_terminated
- parse_convergence: phase + convergence_helper_used (pseudo-tran/gshunt/gmin 检测)
- parse_floating_nodes: "no dc path to ground" / "added to floating node" 正则
- parse_probe_overload: `.probe v(*)` 模式 + 节点计数 + SignalList 计数对比
- parse_undefined_params: "undefined parameter" 警告 + `.param X=Y` 链回溯
- parse_pvt_corners: 注释角数 vs 实际 bsub 提交数
- root_cause_primary/secondary + recommendations + cited_identifiers（从输入文件提取，证明 grounded）

## 6. check.py 13 断言 a-m

a zip含candidate.py / b py_compile / c 11必需顶层键 / d simulator非空 / e log_terminated True / f convergence_helper_used True / g floating_nodes≥5 / h probe num_nodes>1e6 / i undefined_params非空 / j pvt mismatch True / k cited≥8全grounded于B / l anti-hardcode 53 A_FORBIDDEN token零泄漏 / m 3-run md5确定性

## 7. 自验结果

- ref candidate 13/13 PASS（check.py __main__ self-test）
- 4 negatives FAIL distinct labels: fake_empty→c missing keys / fake_print_only→d/e/f/g/h / fake_core_deleted→d/e/f/g/h / fake_print_expected→l A-token leak
- §4.9 三退化（empty/print_only/core_deleted）全 FAIL
- cross-input guard: A run → simulator=FineSim, pvdiv, 19715156, A-identifiers；B run → simulator=SpcFine, vdpiv, 19876543, B-identifiers（证明非 canned）
- 3-run md5 deterministic
- k_rationale == k_check == 13 ≥ 8 GATE PASS
