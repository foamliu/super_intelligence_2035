# Deepread: 1793868684086_ytxf3 (zlhou @ hfeg0pkn005, mc=198, physical_verify)

- **User**: zlhou (NEW user for shard C)
- **Host**: hfeg0pkn005
- **mc**: 198 (calibre:187 + netlist:92 + pyAether:3 + schematic:1)
- **Domain**: physical_verify (Calibre CCI-LVS + GloryEX PEX extraction signoff)
- **Topcell**: `CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS` (35H FS SRAM, 634132 inst / 241690 nets / 272 ports)
- **Run dir**: `/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/pex/FS`
- **Flow**: `run_pex.sh` = env load → `calibre -lvs -hier *.lvs` → `gxrc -c gxrc_cci_cmd`
- **152 msgs**, 438KB messages.json

## User intent arc (debugging dialogue, no single clean delivered artifact)
1. msg#1: "我检查cdl中电阻的l都是20n，没看出问题在哪里" — CDL 里 rm2ca_fs 全 l=20n，但 LVS source 读到 0.04u
2. msg#19: "LVS REDUCE SERIES RESISTORS在哪里"
3. msg#29: "他把两个电阻串联了为什么没有显示电阻数量少了"
4. msg#31: "我重新跑了一下lvs，你查看一下svdb中的结果"
5. msg#57: "为什么我把cdl中lio和gio中那个rm2ca_fs电阻去掉了，电阻检查反而正确了"
6. msg#67: "source 端 21→19 的归并是怎么进行的"
7. msg#73: gxrc_cci_cmd command file read failed
8. msg#79/87/89: calibre -query_input query_cmd -query svdb topcell 用法
9. msg#91: calibre -lvs -hier *.lvs 含义
10. msg#93/99/102: TRDB-1004 captab read failed + line 1499 syntax error at "DEVICE_FIN_MODEL" (GloryEX 2026.03_POC)
11. msg#114/116: 切到 GloryEX 2026.06_P010，captab 加载 OK 但有 warning (VIA V6 cross metal, via absence M6→HiR)

## Key real findings (assistant)
- **LVS REDUCE SERIES RESISTORS YES [TOLERANCE w 0]** with `l = sum(l)` rule merges 2× 20n series resistors → 40n on source side; layout keeps single 20n → Property error
  - 统计行: "4 series source resistors were reduced to 2." → source 21→19
  - DISC `R(rm2ca_fs)` layout l=0.02u vs source l=0.04u, diff 50%
- 规则文件 `35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test08.lvs`: 第108行 `#DEFINE LVS_REDUCE_SERIES_RES TRUE`，第601/608行 `LVS REDUCE SERIES RESISTORS YES`
- 删 dummy 电阻后电阻检查 CORRECT，但出现 2 个 Short circuit:
  - LAYOUT net 27 shorted matching SOURCE nets `XLIO/DWBL_ROUT_STR` and `XLIO/DWBL_ROUT_END`
  - LAYOUT net 26 shorted matching SOURCE nets `XGIO/RDMIMIC_STR` and `XGIO/RDMIMIC_END`
- gxrc 命令文件在子目录 `CCI_Flow_for_CUI/gxrc_cci_cmd_V0d1_Rev07`，当前目录 `gxrc -c gxrc_cci_cmd` 找不到 → "Open gxrc_cci_cmd for read failed"
- GloryEX 2026.03_POC: TRDB-1004 captab read failed + DEVICE_FIN_MODEL syntax error line 1499 → extraction failed
- GloryEX 2026.06_P010 (gxrc_t path `/rundata/lacaa/TV1_DBC_Virtuoso/simdir/.../GloryEX_2026.06_P010/tool/bin/gxrc_t`): captab 加载 OK，warnings:
  - `-W- VIA V6 cross multiple metal layers, please check!`
  - `-W- via absence from CONDUCTOR M6 to CONDUCTOR HiR is found, please check.`
  - Partition halo = 4.050um, License gx_base/gx_pro checkout, extraction OK

## Synthesized case design (B-synthesized, L1-boundary)
**Case ID**: EDA-Eval-DesignFlow-PexFlowRunLogDiag-001 (physical_verify)

**Task**: SUT writes `pex_flow_diag.py` (CLI 1 arg `<pex_run_log>`, stdlib only json/re/sys), parses a combined Calibre-CCI-LVS + GloryEX-gxrc PEX run log → JSON dict with 12 keys:
1. `topcell` (str, from `# Topcell:` / `LAYOUT PRIMARY:`)
2. `lvs_verdict` (CORRECT/INCORRECT)
3. `property_errors` (list of {device, layout_val, source_val, delta_pct})
4. `reduce_series` ({status: YES/NO, reduced_from, reduced_to})
5. `short_circuits` (list of {layout_net, source_nets:[]})
6. `gloryex_version` (str from gxrc_t path `GloryEX_<ver>`)
7. `command_file` (str, the `-c <path>` arg)
8. `trdb_errors` (list of {code, file, message})
9. `syntax_errors` (list of {line, token})
10. `captab_warnings` (list of str, the `-W-` lines)
11. `extraction_verdict` (success/fail)
12. `reduce_series_rule` (YES/NO, the `LVS REDUCE SERIES RESISTORS <YES/NO>` line)

**DISTINCT from**:
- r216 CalibreLvsRepDiag (pure lvs.rep SUMMARY 4-number + DECRYPT2 version compat + correspondence ports — NO PEX/GloryEX, NO REDUCE SERIES, NO captab, NO property DISC)
- r220 SvrfTvfLayerMapGen (SVRF/TVF deck writing)
- r218 ErcPathchkTopoDiag (ERC PATHCHK topology)
- r217 DrcExtendRuleValidator (DRC GDS geometry)
本案首次 ground on **PEX flow (Calibre CCI-LVS + GloryEX gxrc) run-log 诊断**: LVS REDUCE SERIES RESISTORS 归并机制 + Property DISC error + Short circuit + GloryEX 版本/captab TRDB-1004/syntax error/captab warnings + extraction verdict. 与纯 LVS 报告解析互补不重叠.

**A (visible)**: grounded on ytxf3 — topcell `CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS`, INCORRECT, 2× DISC `R(rm2ca_fs)` layout 0.02u/source 0.04u/diff 50%, reduce_series 4→2, no short_circuits, gloryex `2026.06_P010`, command_file `gxrc_cci_cmd_V0d1_Rev07`, no trdb/syntax errors, captab_warnings [VIA V6 cross metal, via absence M6→HiR], extraction success.

**B (hidden)**: 全重参数化 — topcell `CXN5HC2PS2048X144M8B8C2R2W2BW2RE2_FS`, INCORRECT, 2× DISC `R(r3ca_fs)` layout 0.05u/source 0.10u/diff 50%, reduce_series 6→4, 2 short_circuits (Net 51/52), gloryex `2026.12_SP02`, command_file `gxrc_cci_cmd_V0d2_Rev09`, captab_warnings [VIA V8 cross metal, via absence M8→HiR2], extraction success. B 与 A 全重参数化(topcell/device/values/reduce counts/short circuits/version/command file/captab warnings 全不同)击穿硬编码 A.

**B_broken (hidden sentinel)**: topcell 同 B, gloryex `2026.03_POC`, trdb_errors [TRDB-1004 captab read failed], syntax_errors [line 1499 DEVICE_FIN_MODEL], extraction_verdict fail → 测 fatal-error 路径 + 杀 always-pass.

**16 条 ①–⑯ a–p** (k_check=16=k_rationale≥8):
- (a) submit.zip 合法 zip 含 pex_flow_diag.py
- (b) py_compile + 仅标准库 (json/re/sys)
- (c) B exit 0 + stdout JSON dict
- (d) JSON 12 顶层键齐全
- (e) B topcell == B-specific (反硬编码 A)
- (f) B lvs_verdict == INCORRECT
- (g) B property_errors 2 条 + device == R(r3ca_fs) (反硬编码 A rm2ca_fs)
- (h) B property_errors[0] layout_val 0.05u + source_val 0.10u (反硬编码 A 0.02u/0.04u)
- (i) B reduce_series reduced_from 6 + reduced_to 4 (反硬编码 A 4→2)
- (j) B short_circuits 2 条 Net 51 + Net 52 (A 0 条, 反硬编码 A)
- (k) B gloryex_version == 2026.12_SP02 (反硬编码 A 2026.06_P010)
- (l) B captab_warnings 含 "VIA V8 cross" + "via absence from CONDUCTOR M8 to CONDUCTOR HiR2" (反硬编码 A V6/M6/HiR)
- (m) B extraction_verdict == success
- (n) B command_file 以 gxrc_cci_cmd_V0d2_Rev09 结尾 (反硬编码 A V0d1_Rev07)
- (o) 跨输入守卫 A: 重跑候选 on A log → topcell=A + lvs_verdict INCORRECT + property_errors[0].device R(rm2ca_fs) + reduce_series 4→2 + gloryex_version 2026.06_P010 + captab_warnings 含 "VIA V6 cross" (杀硬编码 B)
- (p) B_broken 哨兵: extraction_verdict == fail + trdb_errors 非空(TRDB-1004) + syntax_errors 非空(line 1499 DEVICE_FIN_MODEL) (杀 always-pass + 杀漏判 fatal 路径)
