# Trace deep-read: 1792137921430_3lvd6 (jackliu / hfhds083 / 10.129.32.83 / mc88)

## 来源
- session_file: `1792137921430_3lvd6`
- user: jackliu
- host: 10.129.32.83 (hfhds083)
- match_count: 88
- tools 关键词: synopsys:359; netlist:120; cadence:116; skipper:88; hspice:72; calibre:30; analog:...
- raw messages.json: 814126 bytes / 207 msgs / 5 user turns

## 用户轮逐字（提取自 messages.json，目录式存储 `<sid>/<sid>.messages.json`）

- **U#0**：「你可以读取verilog波形文件吗，比如/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/log/log.regression_20261016_093556/scan_allspeed.x16/ncsim.shm/ncsim.trn」
- **U#1**：「以后都说中文」
- **U#2**：「刚才的波形文件你有读吗，你会发现里面的inh_vblh都是x态」
- **U#3**：「如果你可以读到波形内的信号数据，请根据网表分析一下vblh是x的原因，可能哪里存在fighting，你可能需要网表 /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct15.193816/netlist」
- **U#4**（与 U#3 重复，疑似重试）

## assistant 工具链（关键节点）
1. MSG#1-10：list_allowed_files 探 `/rundata/.../ncsim.shm` → 发现 ncsim.dsn(2.82GB)+ncsim.trn(883.8MB)，Cadence INCISIVE 15.20.024 SHM 格式。run_commands 被禁（"Raw shell tool run_commands is disabled; use run_approved_command"）。
2. MSG#11-28：用 editor 写 check_waveform.py / check_shm_tools.py，run_approved_command(python-runner) 探 ncsim/simvision/verdi 位置。发现 `cshm`/`iregval`/`extract_signal_from_tcl.pl` 等。
3. MSG#57：给出第一版回答（只分析工具可用性，未读波形内容）。
4. MSG#58-67（U#2 后）：实际尝试读波形。editor 写 read_wave_header.py / read_wave_detail.py → 在 DSN 中 grep 到 `inh_vblh`（offset 366344/367861，附近 `inh_vblhbk`）。
5. MSG#69-79：写 dump_inh_vblh.tcl（simvision TCL `database -open .../ncsim.trn`）+ run_simvision_dump.py，尝试用 SandBox_MCP_Server__run_code 调 pyAether 读 SHM → Connection refused (sandbox 10.129.8.105:56290 未起)。
6. MSG#84-93：写 explore_trn.py 解析 TRN 头（magic a19511bf），list_allowed_files 看 log 目录 → 发现 `probe.tcl`（dump 所有信号）+ `irun.log`+`A_Compare.rpt`，read_files 读这些了解信号层次。

## 关键产物 / 真实事实
- 波形：Cadence NCsim SHM 二进制（ncsim.trn 883.8MB + ncsim.dsn 2.82GB），LPDDR5 full-chip regression `scan_allspeed.x16`。
- X 信号：`inh_vblh`（及 `inh_vblhbk`）在波形中为 x 态。
- 用户根因假设：**driver fighting**（「可能哪里存在fighting」）。
- 真实网表路径：`/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct15.193816/netlist`（thomaswu 私有，非 e0031982 可读，且 GB 级不可附加）。
- 真实波形 .trn 在 /rundata，二进制不可附加。

## A-faithful 判定
**不可行**：
1. U#3/U#4 用户已指出根因假设（fighting）→ 按红线 #2「凡用户已指出根因的轮不得用作 A 档任务说明」，A 档禁用。
2. 真实网表（/rundata thomaswu 私有，GB 级）+ 真实波形（SHM 二进制 883MB）均不可附加、不可便携。
3. live ncsim/simvision 不可移植（需 INCISIVE license + LD_PRELOAD 报错）。
→ **B 档 synthesized**。

## 合成 facet（B 档）
**netlist fighting / X-contention 静态诊断器**（`gen_fighting_diag.py --netlist --xsignals --outdir`）：
- 输入：结构化网表（`# design:` + `PORT <name> <dir>` + `INSTANCE <inst> <cell> <pin>:<dir>:<net>`）+ X 信号 JSON 数组。
- 静态分析：net→drivers（out/inout pin + out/inout port）；contention（≥2 driver）；undriven（0 driver 且非 port）。
- X 信号交叉比对：reason ∈ {contention(fighting), undriven, single_driver}，is_fighting=(reason==contention)。
- 输出：fighting_diag.json（9 顶层键）+ report.md（## Summary + ## Contention Nets + ## X-Signal Analysis）。
- L 级别：**L1**（离线 Python 解析，不跑 EDA 工具；netlist fighting 是静态分析，本质无需 sim）。

## 输入设计（A/B/B2 反硬编码五轴）
| 项 | A (visible) | B (hidden, primary) | B2 (hidden, cross-input) |
|---|---|---|---|
| design | DDR5_VBLH_A | SRAM_SBL_B | MUX_OUT_B2 |
| n_instances | 5 | 7 | 7 |
| n_nets | 13 | 13 | 14 |
| n_contention | 1 (vblh, 2drv) | 1 (sbl, 3drv) | 2 (mout 2drv, vcg 2drv) |
| n_undriven | 1 (vfloat) | 1 (vnetx) | 1 (vf) |
| n_x / n_fighting | 3 / 1 | 4 / 1 | 5 / 2 |
| contention net 名 | vblh | sbl | mout, vcg |
| inst 名 | I1/I2/I3/L1/G1 | J1-3/K1/K2/L2/M1 | P1-6/L3 |
| X 信号 | vblh/vdl/vfloat | sbl/qn/qout/vnetx | mout/vcg/vcg2/ven/vf |

五轴不相交：design / inst / net / x-signal 名全不同；n_contention 1/1/2（硬编 1 者 B2 g FAIL）；n_fighting 1/1/2；n_x 3/4/5。A_LITERALS = [DDR5_VBLH_A, vblh_drv1, vblh_drv2, vdl_in, vfloat, vsel, vq, vblh]，ref 源码无任一字面量。

## check.py 16 条件 a-p
a(zip 防泄漏+py_compile+脚本) / b(B-run exit0+2文件) / c(9 顶层键) / d(design==SRAM_SBL_B) / e(n_inst==7) / f(n_nets==13) / g(n_contention==1) / h(n_undriven==1) / i(contention_nets 结构 net+n_drivers≥2+drivers) / j(driver 含 inst/pin/cell/dir 且 dir∈{out,inout}) / k(x_signals 长度==n_x==4 且每项 5 键) / l(reason∈{contention,undriven,single_driver,external} 且 is_fighting==(reason==contention) 且 (n_drivers≥2 iff contention)) / m(n_fighting==count(is_fighting)==1) / n(report ## Summary+## Contention Nets+## X-Signal Analysis+每 contention net+每 x_signal Fighting verdict) / o(反硬编码源码无 A 字面量 + A-run design==DDR5_VBLH_A + B2-run design==MUX_OUT_B2+n_contention==2+n_fighting==2) / p(3x B-run sha256 一致)

## 自验
- ref PASS 16/16 a-p。
- 5 negatives 全 FAIL，5 distinct first_fail: empty_shell→b / hardcode_a→d / print_expected→n / ref_core_deleted→g / naive_stub→l。
- §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL（与 negatives 重叠）。
- 3x sha256 deterministic（hash 1a7a8003 一致）。
- 断言闸门 k_rationale=k_check=16 ✓。

## 教训
1. **waveform X-fighting 静态诊断是 waveform+netlist L1 可验好范式**：contention/undriven/single_driver 三分类 + X 信号交叉比对 → 16 条件天然丰富（计数/结构/枚举一致性/报告/跨输入/确定性），与 FFLatchExtract(反馈环路)/AnalogGroupRoleInfer(@group)/LvsRuleAudit(SVRF) facet 不同无重复。
2. **cline session 存储确认为目录式** `<sid>/<sid>.messages.json`（207 msgs），peek_dirbased.py 路径正确。
3. **A-faithful 仍受红线 #2 约束**：用户在 U#3 已给出「fighting」根因假设 → 即便产物可附加也禁用 A 档，只能 B 档。这是对「难度稀释」的天然防护——用户自己把答案说了一半。
4. **netlist 格式须显式 pin 方向** `<pin>:<dir>:<net>`（三段冒号），`<pin>:<net>`（两段）会让 driver 检测失效——首轮 ref 跑出 n_nets=8/n_contention=0 即此 bug，加 dir 后修正为 13/1。
5. **L1/L2 比例债 10 轮**：本 case 亦 L1（静态网表分析无需 sim）。fresh 池 top-mc clean L2 produce 仍稀缺（连续 10 轮 #317/#332/#345-351）。waveform domain 的 L2 需要 live waveview/ncsim/fscript，trace 里这些工具调用受 license/sandbox 限制不可移植，是 L2 稀缺的结构性原因。
