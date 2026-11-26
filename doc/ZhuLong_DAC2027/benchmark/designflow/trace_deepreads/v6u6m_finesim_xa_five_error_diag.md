# 深读笔记: v6u6m — e0024852 FineSim/PrimeSim XA SRAM-PEX 表征流「五连报错」根因诊断

**session**: `1793184099494_v6u6m` · **user**: e0024852 · **host**: hfeg0pkn004 (10.129.2.13)
**trace**: .75 scp 930KB messages.json, 186 msgs, 17 user-turns
**match_count**: 107 (1115_081559 池; 旧 audit 列 mc839 来自更早快照)
**旧 audit 判定**: reject "FineSim DSPF error diagnostic, all user turns 'the er...'" (Q&A inspection, not produce-task)
**11-15 reaudit 新判定**: 可造 (debug-Q&A 根因诊断, 操作化为 diagnose_finesim_errors.py → diagnostic_report.json)
**合成 case**: EDA-Eval-DesignFlow-FineSimDiag-001 (spice_sim L1, A 档 trace-faithful)

## 真实用户意图

e0024852 在跑 SRAM 宏 `CXN4HCSPS1024X8M16B4C1R1W1BW1RE1_FS` 的 FineSim/PrimeSim XA
PEX 后仿表征流程（dspf-tool stage1 → detect → XA probe 链），**连续遇到 5 个互相独立
的报错**，逐个把报错日志贴给 SpiceAgent 问 "how to fix it"。这是典型的 multi-error
debug-Q&A：用户不是要 agent 跑仿真，而是要 agent **读日志/脚本/网表/向量文件，定位每个
报错的根因并给修复**。

## 5 个报错 + 真实助手诊断（ground truth）

### e1 (U#0, U#3): dspf_branch_unreducible
- 报错: `ERROR: output signals: explicit DSPF output not found or branch cannot be reduced: xtop.xilio0.xirwcnt.xi_nand_ulvt_3.mmpm1:g`
- 根因: tailor.sp `_tailor.sp` 第 57 行 `.inc` 了一份 full-chip measure 文件（约 1.3 万条 `.meas`，6512 条引用 `xtop.xilio0.*/xtop.xgio.*` 整芯片层级信号），但宏 DSPF 是 flat 的（`*|DESIGN CXN4HCSPS1024X8M16B4C1R1W1BW1RE1_FS`，器件名被打平成 MMPM1，没有 `xtop/xilio0/xirwcnt` 层级），`output_signals.py:363` 在第一个解析不了的 explicit output 上 raise ValueError 把 stage1 卡死。
- 修复: 注释掉 tailor.sp 的 `.inc ...measure`；或在 netlist `.OPTION` 块加 `finesim_spfrmin=1e-3 / finesim_spfrmax=1e6 / finesim_spredtc=1e-12` 放宽 RC 约简；或 `finesim_spfnonet mmpm1:g` / `finesim_spfcnet mmpm1:g`。

### e2 (U#2, U#4): bsub_missing_executable
- 报错: `*rf_1rw_128x128_presim: command not found`（刷屏重复）
- 根因: `run_prohd.sh` 里 `bsub -Is -n 32 -q lacaa_sram CXN4HCSPS1024X8M16B4C1R1W1BW1RE1_FS_tailor.sp -np 32 ...` 把 `.sp` 网表文件名**直接当可执行命令**传给 bsub，**漏掉了 `finesim` 前缀**。bash 把 .sp 当 shell 脚本跑，第 1 行 SPICE 注释 `*rf_1rw_128x128_presim` 被当成命令 → command not found（每个并行进程刷一次）。对照同目录 `run_sim.sh:45` 正确写法 `finesim -np 8 .../CXN4HCSPS...FS.sp -o "wave/..." -format fsdb`。
- 修复: 每个 bsub 行的 .sp 文件名前加 `finesim`。

### e3 (U#6): missing_param_vdd_val
- 报错: `ERROR: detect: testbench must declare .param vdd_val=...; set simulators.xa.detect.vdd_parameter in site config`
- 根因: `detect_bundle.py:94` 用正则 `re.search(r'(?im)^\s*\.param\s+.*\bvdd_val\s*=', text)` 要求 `.param` 和 `vdd_val=` 在**同一物理行**。但 `_tailor.sp` 把 `vdd_val` 写在 `+` 续行上（`.param` 单独一行，`+ pwr = 0.75`，`+ vdd_val = 0.75`），正则 `^\.param` 匹配不到续行。用户试了 `+ vdd_val = 0.75`（仍报错），助手纠正必须让 `vdd_val` 落在 `.param` 那一行上（独立一行 `.param vdd_val = 0.75` 最稳）。
- 修复: 加独立一行 `.param vdd_val = 0.75`（值取自 pwr=0.75）；或在 site 配置设 `simulators.xa.detect.vdd_parameter` 指向已有参数名。

### e4 (U#16): xa_license
- 报错: `XA run produced no .metainfo` + `FLEXlm error code(-5): No such feature exists. Feature: primesim_beta` / `License path: 12000@hl04:` / `'xsim'/'primesim'/'primesim_beta' 全部 checkout failed` / `Error: license check failed`
- 根因: detect 阶段 `detect_bundle.py:77` 强制 `generator == "xa"`（不能换 FineSim）。XA 读 `SNPSLMD_LICENSE_FILE`，但 bsub 计算节点上该变量被截断只剩 `12000@hl04:`（交互 shell 里是一长串服务器），hl04 上没有 primesim/xsim/primesim_beta feature。`xa` 二进制存在（`/apps/synopsys/SRB/customsim/V-2023.12/bin/xa`），纯 license 问题。
- 修复: 把完整 `SNPSLMD_LICENSE_FILE` 传到 bsub 计算节点；或指向有 `primesim` feature 的服务器。

### e5 (U#11, U#15): vec_format
- 报错: `Error: (.../racing.vec:11) syntax error at '* CEB WEB A_XDC[[5:0]] A_BANK[[2:0]] A_WL[[1:0]] A_Y[[3:0]] DIN1 DIN2 BWEB TESTN TESTP CRSLE CRSRE ...'` / `Simulation is terminated.`
- 根因: `racing.vec` 是 FineSim 专有格式，用 `[[5:0]]` **双中括号**总线语法 + `*` 行首注释；PrimeSim XA 的向量解析器不认 `[[ ]]` 也不认 `*`（XA 用 `;` 注释），在第 11/12 行报 syntax error。助手初判只转括号，转完发现 `*` 表头行还挡着（XA 不认 `*`），最终 `sed -e 's/\[\[/[/g' -e 's/\]\]/]/g' -e 's/^\*/;/' racing.vec > racing_xa.vec`。
- 次级问题: `racing.inc` 桥接 BWEB[0:159]/D[0:159]/Q[0:159]（160 位，给 1024x16x? 大颗粒写的）但本宏 1024X8 只有 BWEB[7:0]/D[7:0]/Q[7:0]，高位引用不存在节点 → 端口位宽不匹配。
- 修复: sed 转换 + 改 detect.sp `.vec` 引用；racing.inc 收敛位宽到本宏真实端口。

## 操作化设计（case 合成）

5 个报错互相独立、各有具体可解析的日志/文件源，适合操作化为「写脚本解析 workdir 产出
结构化诊断报告」的 debug-Q&A 形态（同 r622 SimModelMismatchDiag 模式）：
- A 输入: workdir/ 含 run_prohd.sh / netlist.sp / tailor.sp / macro_ports.txt /
  error_logs/{stage1,detect_prep,xa}.log / detect/{racing.vec,racing.inc,detect.sp}
- 隐藏 B: 同结构，宏换 CXN4HCSPS2048X16M16B2C1R1W1BW2RE2_FS，dspf 网 mmpn2:s，
  SPICE 注释 *ddr4_predriver_presim，vdd=0.9，license 12000@hl07，vec [[7:0]]/256-bit
- 交付: diagnose_finesim_errors.py(workdir, out_json) → diagnostic_report.json
- check: 13 断言 a-m，含 cross-input guard（A vs B 在 macro_name/dspf_net/
  spice_comment/vdd_val/xa_license_server/BWEB,D,Q 位宽 6 项全异）+ 负结果断言
  （port_width_mismatches BWEB/D/Q=[160,8]）+ 5 条 fix 内容齐全
- 自验: ref 13/13 PASS + 4 negs (naive_hardcode_a/always_empty/print_only/core_deleted) 全 FAIL

## 复活池定位

v6u6m 是 11-15 reaudit 191 误杀复活池中第 5 高 mc 候选（实际 1115 池 mc=107；audit 列
mc839 来自更早快照，host 字段 audit 写 hfeg0pkn002 但 1115 池为 hfeg0pkn004 —— audit
元数据有 host/mc 漂移，但 session slug 一致，trace 真实可溯）。本次为复活池变现 #5
（承 r619/r620/r621/r622）。
