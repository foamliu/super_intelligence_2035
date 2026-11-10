# Deepread: 1793091372339_bjl02 · harrywu@hfeg0plg99 · mc=90

**Domain**: analog_context (D)
**User original (U#14, verbatim)**:
> 目前是丢一次queue会测量多个corner下的数据，我希望你把它改成每个corner的测量并行单独run，我只需要输入一个命令即可丢所有的run。

**意图**：把 DDR6 core-timing 老化后测量流程从「一次 queue 作业串行跑全部 PVT corner」改成「每个 corner 一条独立 bsub 并行 run，一条命令提交全部」。

**对话流（96 msgs, 842KB）**：
- U#0–U#13：harrywu 围绕 `/proj/dscqa/V0/agentdir/harrywu/Temp` 下 DDR6 core-timing 老化测量流程做若干上下文/调试 turn（看 measure1/measure2 脚本、fscript 用法、bsub 队列）。
- U#14（produce task，原话见上）：要求把多 corner 串行测量改成每 corner 并行单独 run。
- 助手读取 `measure1_set_PRAC_coretimng_harrywu_Aging`（单个 `fscript <<EOF` heredoc 内 11 条 `meas ./Timing_Meas.sp -i ${WAVE_Normal}/primesim.A_Perbank_RAS_CAS_<PROC>_AGING.X1P6.<CORNER>.X1P6 -o ${Result_dir}/<CORNER>_CORET_A.mt0 -l ...`，corner = TT1.0V25C/TT1.0V85C/FF1.1V±40/110C/FS0.9V±40/110C/SF0.9V±40/110C/SS0.9V±40/110C/FF1.0V25C，PROC = CORNER 前 2 字符）与 `measure2_set_PRAC_coretimng`（`bsub -q pv -n 8 measure1_set_PRAC_coretimng_harrywu_Aging -o ./meas.log`，单作业串行）。
- 助手产两个新脚本：
  1. `measure_one.sh` — 参数化单 corner：`CORNER="$1"`、`PROC="${CORNER:0:2}"`、`set -euo pipefail`、缺参 usage 报错、`fscript` heredoc 只跑一条 `meas`（路径用 `${WAVE_Normal}/primesim.A_Perbank_RAS_CAS_${PROC}_AGING.X1P6.${CORNER}.X1P6`、`-o/-l` 用 `${CORNER}` 拼后缀）。
  2. `submit_all.sh` — 内嵌 corner 列表、`for CORNER in $CORNERS; do bsub -q pv -n 8 -J "meas_${CORNER}" -o "./logs/${CORNER}.bsub.log" ./measure_one.sh "$CORNER"; done`、`mkdir -p`、最后打印提交计数。
- 助手另做了校验（检查 bsub 数 == corner 数、参数化是否正确）。

**关键正确点（从 trace 提炼）**：
1. 从 `<CORNER>` 取前 2 字符推工艺 token `PROC`（TT/FF/FS/SF/SS），不可手写 PROC 列表。
2. `measure_one.sh` 的 fscript heredoc 只能有一条 `meas`（参数化的单 corner），不可保留原 11 条。
3. `submit_all.sh` 必须每 corner 一条独立 `bsub`（`-J`/`-o` 按 corner 区分），`bsub` 数 == corner 数；一条命令提交全部。
4. 队列/核数从原 `measure2` 解析（`pv`/`8`），不可在新脚本里改成别的队列。
5. `./measure_one.sh "$CORNER"` 传参（带引号防 corner 名含特殊字符如 `-`）。

**金标准状态**：trace 有明确最终产物（measure_one.sh + submit_all.sh + 校验），属干净 single-produce。但产物与 harrywu 真实 `/proj` 路径、具体 11 corner、`pv` 队列强绑定，且 fscript/bsub 真实执行环境不可复刻 → 采 B-grade synthesized：把「(measure1, measure2) → (measure_one.sh, submit_all.sh)」抽成单文件 Python 生成器 CLI，纯 stdlib、可离线判分。

**真实环境不可复刻点**：私有 `/proj/dscqa` 路径、harrywu 真实 11 corner + `pv` 队列 + finesim/LSF 队列执行 → 全部抽离；生成器只解析输入脚本 + 写两个新脚本，不真的提交作业（禁 subprocess/socket/requests/urllib/pty）。

**B-grade synthesized 设计**：
- 可见 A：11 corner（TT/FF/FS/SF/SS × V/T）、`pv` 队列、8 核、`primesim.A_Perbank_RAS_CAS_*` 路径、`_CORET_A` 后缀、`###Coretiming` 头。
- 隐藏 B：7 corner（不同 V/T，名字与 A 完全不相交）、`fqueue2h` 队列、16 核、`primesim.B_IoLink_*` 路径、`_IOTIM_B` 后缀、`###Iotiming` 头。
- SUT = `parallelize_measure.py`（--measure1/--measure2/--out）解析 WAVE_Normal/Result_dir 变量、fscript 头 + meas 行、corner 列表（从 -o basename 首 `_`-token 推）、PROC（CORNER 前 2 字符）、路径模板（`_PROC_` 与 `.CORNER.` 双槽替换）、-o/-l 后缀、bsub 队列/核数/作业名/日志 → 生成 measure_one.sh + submit_all.sh。
- check.py 14 条件 a-n，独立 oracle（从 -o basename split 推 corner、从 bsub 行 split 推 queue/cores，与 reference 的 regex 解析结构不同）+ 子进程真跑 SUT + 反硬编码（B-only + A-only 字面量均禁）+ 跨输入 A 泛化 + 3-seed md5 + 缺参执行。
- 自验：ref PASS 14/14；negative_selftest 6/6 全 FAIL，命中条件互异（naive_stub→g / hardcode_A→h / hardcode_B→k / §4.9 empty→a / printonly→c / core_removed→f）。

**维度正交检查**：既有 D analog_context/schematic_netlist/waveform case 多为 svwf 路径展开 / FSDB 功耗目录/窗口 / 眼孔径 / IV 曲线分类 / net 前缀高亮 / 表达式布尔对拍 / verdict JOIN / 网表端口清洗 / SA 搭建 / 驱动溯源 / 拓扑重构 等；本 case =「fscript heredoc 多 corner 顺序测量 + 单 bsub → 参数化单 corner + per-corner 并行 bsub 扇出」的**生成器**（heredoc 行解析 + 路径双槽模板 + bsub 解析），机制/产物全不同。同 shard A 的 digital SweepParallel-001 是 shell run_sweep 直接并行化（非 Python 生成器、非 fscript heredoc 解析），亦不冲突。
