# deepread 1792563728390_19ycs — SpiceMeasGroupExpand-001

- trace: 1792563728390_19ycs · devonma @ 10.129.2.10 · mc=19 · schematic_netlist (schematic:45;analog:24;verilog:5;netlist:4)
- session: /home/devonma/.cline/data/sessions/1792563728390_19ycs/1792563728390_19ycs.messages.json (1612 行, 59 msgs)
- claimed: 2026-11-12 (#539) · status → case SpiceMeasGroupExpand-001

## 用户原文（4 user-turn，逐字）

- **U#0**：「/proj/dscqa/V0/simdir/finesim/dscqaF/Runfile/Vcap/local/vsim_script/meas_cstm_DSCQA_SC0.sp 对这个文件进行扩写，将每组CSTM_SMP和CSTM_SDO以及CSTM_SMP_OUT  CSTM_SDO_OUT，扩写至32个」
- **U#42**：「/proj/dscqa/.../meas_cstm_DSCQA_SC0.sp 以这个文件为基础，copy一个meas_cstm_DSCQA_SC1.sp，将其中所有的XI_ChanPSD0改为XI_ChanPSD1」
- **U#50**：分析 run_all.sh 报 PermissionError (os.chmod) 原因 + 怎么修
- **U#51**：分析 xrn.log 报错原因 + 怎么改

→ U#0 为核心 produce-task（SPICE .meas deck 扩写）。U#42 为衍生 copy+rename（次级）。U#50/U#51 为 Q&A/debug（非 produce）。

## 真实任务语义（U#0）

输入 `meas_cstm_DSCQA_SC0.sp` 是 FineSim/PrimeSim `.meas tran` 测量 deck，结构：

**Header（10 行）**：`.option finesim_measout=1` / `VVDD AVG v(vcc!) from=200n to=220n` / `.param Vmid='VVDD/2'` / `.param VHmid='VVDD*0.95'` / `.param Vmidckt='0.174V'` / `PERIOD trig/targ v(ck_t)='Vmidckt' rise=11/12`。

**VSV/CPS 块**：`CSTM_VSV{1..V}` when v(GP.CSTM_VSV)=Vmid rise={v} td='350n'；`CSTM_CPS1` when v(GP.CSTM_CPS)=Vmid rise=1 td='350n'。

**时间测量块（每 vref 一段 `**vref{v}`）**：
- `CSTM_SMP_{v}_{s}` when v(SMP_SIG)=Vmidckt fall=1 td={s==1?'CSTM_VSV{v}':'CSTM_SMP_{v}_{s-1}+10n'}
- `CSTM_SDO_{v}_{s}` when v(SDO_SIG)=Vmidckt fall=1 td={s==1?'CSTM_VSV{v}':'CSTM_SDO_{v}_{s-1}+10n'}

**输出测量块（每 vref 又一段 `**vref{v}`）**：
- `CSTM_SMP_OUT_{v}_{s}` find V(OUT_SIG) when v(H_OUT_SIG)=Vmid fall=1 td='CSTM_SMP_{v}_{s}+10n'
- `CSTM_SDO_OUT_{v}_{s}` find V(OUT_SIG) when v(H_OUT_SIG)=Vmid rise=1 td='CSTM_SDO_{v}_{s}+10n'

其中 GP=`XI_DDR6TOP_R.XI_Channel.XI_ChanPSD0.XI_Controller.`，SMP_SIG=GP+`CSTM_SMP`，SDO_SIG=GP+`CSTM_SDO`，OUT_SIG=GP+`CSTM_OUT`，H_OUT_SIG=GP+`XI_C_CSTM.H_out`。

原 deck：10 vref × 17 samples/family（4 family: SMP/SDO/SMP_OUT/SDO_OUT）。用户要求扩到 32 samples/family。

## agent 解法（实际）

agent 找到现成模板生成器 `/home/devonma/gen_meas_10vref.py`（SAMPLES=17, VREF_COUNT=10），改 `samples_per_vref=32` 重生成整个 deck → 覆盖原文件（1342 行）。verify_counts.py 确认：CSTM_SMP/SDO/SMP_OUT/SDO_OUT 各 320 = 10×32，CSTM_VSV=10，CSTM_CPS=2。

（注：agent 用 regen-from-template 而非 parse+append-expand；用户字面要求"对这个文件扩写"语义上是 parse+expand，但 agent 走了模板捷径。）

## B-grade 合成设计（SpiceMeasGroupExpand-001）

**机制**：parse 现有 .meas deck → 检测 vref 组数 + 每 family 当前 max sample → 在每 family block 末尾 append 新 sample 行（max+1..target），td 链式引用前一个 measurement 名 + 增量。**纯 stdlib 文本 parse + 行生成**，无 EDA 运行时。L1。

**放弃**：regen-from-template（agent 捷径，依赖外部模板脚本，非自包含 parse）；FSDB/.mt0 测量结果解析（U#50/U#51 Q&A，非 produce）；copy+rename（U#42 太浅）。

**A/B/C 不相交设计**（disjoint: GP 前缀 / vref_count / input_samples / target / Vmidckt / td_inc）：

| | GP prefix | V | in_samples | target | Vmidckt | td_inc |
|---|---|---|---|---|---|---|
| A(visible) | `XI_DDR6TOP_R.XI_Channel.XI_ChanPSD0.XI_Ctrl.` | 8 | 12 | 24 | 0.174V | 10n |
| B(hidden)  | `XI_DDRTOP_R.XI_Chan.XI_ChanPSD1.XI_Controller.` | 6 | 9 | 20 | 0.180V | 12n |
| C(嵌 check.py) | `XI_MEMTOP_R.XI_Channel.XI_ChanPSD2.XI_Ctl.` | 5 | 7 | 18 | 0.165V | 8n |

family 名（CSTM_SMP/SDO/SMP_OUT/SDO_OUT）共享（任务语义，非"参数"）。边沿语义共享（time=fall=1, SMP_OUT=fall=1, SDO_OUT=rise=1，CSTM 协议常量）。

**SUT** `spice_meas_group_expand.py --deck <in.sp> --target <N> -o <out.sp>`：纯 stdlib（re/os/sys/argparse/json 禁 subprocess/socket/urllib/ctypes/eval/exec/numpy）+ 禁 B/C 字面量。

**check.py 14 条件 a-n 独立 oracle**（o_parse_deck 独立算 expected 新行 + 结构，subprocess 真跑 SUT on B+C，不 import SUT 不硬编码）：a zip 含 py + 无禁 import/call + 无 B/C 泄漏 / b py_compile / c 输出存在且非空 / d 输出行数 == header + VSV/CPS + 2×V×(2×target) time-block + 2×V×(2×target) out-block + 分隔 / e 每 family 每 vref sample 数 == target / f VSV 数 == V 保留 / g CPS 保留 / h header 逐行保留 / i 原 deck 前 K 行（existing）逐行保留（prefix 不变）/ j 新增行 td 链正确（s==max+1 → td='CSTM_VSV{v}'，s>max+1 → td='CSTM_{fam}_{v}_{s-1}+{inc}'）/ k 新增 SMP_OUT/SDO_OUT td 引用对应 CSTM_SMP/SDO_{v}_{s}+inc / l 无重复 meas 名 / m 全部 meas 名形如 CSTM_{FAM}_{v}_{s} 格式 / n Vmidckt/Vmid 参数行保留。

## 维度正交（非 dup）

vs SpiceMismatchSweep-001(#537 per-corner .param 行注入) · IddMeasPostProcess-001(#518 .meas 结果后处理) · FsdbMeasRun-001(FSDB 波形测量) · HierSpiceMosCount-001(层次 MOS 计数) · 2StepOCChainAnalyze-001(OC 链分析) · SdlGroupPlan-001(SDL 组规划) · SpiceUndefParamScan-001(#519 undefined-param 扫描) · ClosureDeckBuilder-001(#520 closure deck 构建) — **机制不同**：本 case = 解析 .meas deck + 按 sample 索引 append 链式 td 测量行扩组，无 corner sweep / 无结果后处理 / 无波形 / 无层次计数 / 无 deck-from-scratch 构建。非 dup ✓。
