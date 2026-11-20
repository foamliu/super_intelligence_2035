# Deepread — 1794212090584_3gk8d (rhyanw @ hfeg0pkn001, mc=51, schematic_netlist)

## 任务原文（提出需求轮）
- **U0 (msg#0)**：「/proj/drvqa/V0/workdir/rhyanw/SM/05_SANEN_SAPEN/SMmismatch20261109/mixbest.sp，基于我这个文件，.param delvtoBL0_NsR='NsR' delvtoBL0_PsR='PsR' delvtoBL0_NsL='NsL' delvtoBL0_PsL='PsL' .param delvtoBL1_NsR='NsR' ... .param delvtoBL3_NsR='NsR' ...」——用户提供 delvto 宏结构，要基于 mixbest.sp 做参数 sweep 批量生成。
- 后续轮多为诊断 Q&A（inc 路径错、二分失败、量级、netlist 版本差异），**不属 A 档任务说明**（用户已指出根因/给修复）。

## 真实工具链 / 产物
- mixbest.sp（64 行）：line 49-53 = delvto 宏（`.param delvtoBL{0..3}_NsR='NsR' ...`，注意 line 51 是 BL1 重复，原文件真实 quirk），line 55 = sweep 定义行 `.param NsL=0 NsR=0 PsL=0 PsR=0`。
- agent 产物 **mixbatch.pl** + generate_sp 子程序：读 sweep corners（mixbest/mixworst/senbest/senworst 四角，值如 NsR=23.1m PsR=-23.1m NsL=-27.28m PsL=27.28m），对每个 corner **只替换 line 55**（`.param NsR=$nsr PsR=$psr NsL=$nsl PsL=$psl`），delvto 宏 line 49-53 原样保留，文件总行数 64 保持。
- 验证（test_gen.pl, msg#25/#63）：`replaced=1`, GEN_OK, delvto 行逐字保留, line 55 替换, `wc -l` src=64 dst=64 一致。
- LSF bsub 提交部分（bsub -q ... primesim ...）**不可自包含**（沙盒无 LSF）→ 放弃。

## 金标准机制
- sweep 定义行 = `.param` 行中 4 个 sweep 参数被赋**具体数值**（`NsR=0`），区别于 delvto 宏行（参数以**引号引用的参数名**出现 `NsR='NsR'`）。
- generate_sp 只替换「sweep 定义行」，delvto 宏行（参数被名引用）**不动**。
- 文件总行数必须保持（替换不是增删）。
- 每 corner 一个 `<stem>_<corner>.sp`。

## B-grade A/B/C 不相交设计（SpiceMismatchSweep-001）
- 机制：纯 stdlib SPICE 文本解析 + `.param` sweep 定义行识别（数值赋值 vs 引号名引用）+ per-corner 替换 + manifest。L1（无 EDA 运行时）。
- A：params `blN_r/blP_r/blN_l/blP_l`，corners `mixbest/mixworst/senbest/senworst`，delvto 前缀 `delvtoBL`，stem `mixbest`，decoy `.param tstart=0 tstop=10n tempp=25`。
- B（hidden）：params `dwN_r/dwP_r/dwN_l/dwP_l`，corners `fast/slow/typ/worst_c`，delvto 前缀 `delvtoDW`，stem `dwbase`，decoy `.param vdd=1.2 temp=85`。
- C（嵌入 check.py）：params `saN_r/saP_r/saN_l/saP_l`，corners `c0/c1/c2/c3`，delvto 前缀 `delvtoSA`，stem `sabase`，decoy `.param icorr=1`。
- A/B/C：param 名 / corner 名 / 值 / delvto 前缀 / stem / decoy 行全不相交。
- 关键 fixture：delvto 宏行含 `<P>='<P>'`（引号名引用）须原样保留；sweep 定义行 `<P>=<数值>` 须按 corner 替换；decoy `.param` 行（不含 sweep 参数）须不动（测过度替换）。

## check.py 14 条件 a-n（独立 oracle，subprocess 真跑 SUT on B/C，不 import SUT）
a zip 含 py + 无禁 import/call + 无 B/C 字面量泄漏 / b py_compile / c 跑 B 退 0 + manifest + per-corner .sp / d manifest schema / e .sp 数 == B 行数 / f 每 .sp 行数 == base 行数 / g delvto 行逐字保留 / h delvto 引用名非数值 / i 替换行按名匹配 B 行值 / j decoy .param 行不变 / k 替换行 index 正确 / l 反硬编码 C 匹配 C-oracle + C≠B / m 3-seed sha256 一致 / n 输出文件名 `<stem>_<corner>.sp`

## 维度正交（非 dup）
- vs SpiceUndefParamScan-001 (#519, rhyanw s08eb)：扫描 include 链中「引用未定义」参数；本 case sweep 定义行值注入 → 机制不同。
- vs SpiceUndefParamScan / SpiceMosCapRatio / SpfResPathTrace / SpfTrueShortScan / SpfLayerAnnotate：均为 SPF/SPICE 解析或路径，无「per-corner `.param` 行值注入 + delvto 宏保留 + 行数保持」机制。
- vs RonMismatchExtract/RonMismatchMd0：.md0 RON mismatch 数值后处理；本 case .sp deck 生成 → 不同。
