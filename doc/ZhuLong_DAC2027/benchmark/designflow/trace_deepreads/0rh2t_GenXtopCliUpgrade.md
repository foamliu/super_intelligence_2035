# trace_deepread · 0rh2t · GenXtopCliUpgrade (r910 deepread, synthesize next round)

- session: `1794964870215_0rh2t` · user: shanliny · host: hfeg0pkn003 (10.129.2.12) · mc=24
- domain: spice_sim (SRAM characterization tooling)
- ledger status: **claimed** (r910) → 待下轮合成
- trace: 74 msgs / 554 KB / agent=lead / fetched to .75 workdir (peek session shardB_20261120-r910)
- keywords: netlist:24;hspice:17;transistor:5;spectre:5;pex:3;pdk:3;floorplan:1

## 为什么本轮没合成（r910）
40-min 硬预算：本轮取证（扫 1119 B-pool 209 mc≥10 → 8 条 peek → 全 near-dup/weak-teeth，仅 0rh2t 真正 distinct）后剩余预算不足以走完「重建 A 原 script + hidden B + check ≥8 断言 + negatives + .75 self-verify + 双仓 commit」全闭环。故按 §3/r908 先例：claim + deepread，下轮第一件事合成。

## 真实用户意图（trace-faithful，原话）
- U#0(act):「告诉我这些代码是如何使用的」+ 附件一整套 SRAM characterization 工具（uploads/：0_run, char.input, char.opt, config_inst.txt, config_meas.txt, config_path.txt, config_pvt.txt, config_rule.txt, config_racing_meas.txt, deploy{,2,3,4}.py, generate_xtop.py, inspect_dspf.py, parse_real_top.py, prove_scalability.py, racing.pdef/.vec, racing_m4b2.sp, rmwm.pdef/.vec, rmwm_meas.txt, sram_meas.py, sram_meas_gen.py, test_xtop.dspf.TYPICAL_25(+.xtop), validate{,2,3}.py, xtop_out, PARAM, PVT_LIST）
- U#4(act):「你这generate_xtop.py应该没有只能 `python generate_xtop.py <文件>` 这个用法这么弱智吧？连输出在哪都不能改？」
- U#8(plan):「之前你说的 memchar 检验的那个工作流需要这 generate_xtop.py 能够指定输出目录吗？」

⇒ **核心可交付 produce**：把「朴素」的 generate_xtop.py 重写成可用工具——加 `-o/--output-dir`（及其它 CLI 选项），并修掉 SPICE 续行符 `+` 被当成 pin 名的 bug。U#0 的“讲解用法”是 Q&A 前置，不是判分对象（按 2026-11-15 reaudit，Q&A 合法但 check() 要有牙 ⇒ 判分只钉 produce 部分）。

## assistant 工具链（实测）
list_allowed_files(uploads) → read_files(全附件) → editor(generate_xtop.py 重写) → run_approved_command(py_compile / --help / 跑 test_xtop.dspf.TYPICAL_25) → read_files(.xtop 输出) → 发现 `+` 混入 pin 列表 → editor(过滤 `+` token) → 再验证。共 10 read_files / 5 editor / 12 run_approved_command。

## 参考解（已在 .75 上，可直接复用为 reference）
.75 路径：`/home/shanliny/.cline/data/sessions/1794964870215_0rh2t/uploads/generate_xtop.py`（274 行，已含完整 CLI + `+` 修复，作者署名 zhulong —— 这是 assistant 最终版）。已 scp 到 peek workdir `gen_xtop.py`。
- CLI: `usage: generate_xtop.py [-h] [-o DIR] [-s SUFFIX] [-f] [-q] [-n] SPF_FILE [SPF_FILE ...]`
- 核心解析：从 SPF/DSPF 找 `*|DESIGN <top>` 与 `.SUBCKT <top> <pins...>`（含续行 `+`），过滤纯 `+` token，生成 `XTOP <pin1> ... <top_cell_name>` 写到 `<outdir>/<basename><suffix>`（默认 outdir=源文件目录, suffix=.xtop）。
- `-f` 覆盖、`-q` 静默、`-n` dry-run、`-h` help。

## 下轮合成 SOP（直接派活）
1. **A（SUT 可见）**：重建「原版朴素 generate_xtop.py」——去掉所有 argparse 选项、只支持 `python generate_xtop.py <file>`、输出固定写到源文件目录、**保留 `+` 续行符 bug**（即 tokens[2:] 不过滤 `+`）。可从参考解反向裁剪，或从 trace editor diff 的 old_text 拿到原版片段拼回。
2. **hidden B**：另造一份不同 top/pins/续行结构的 DSPF（如 8 钟控 + 双向数据总线 + 多段续行 + 注释行 + 内部 .SUBCKT 子电路干扰），放 `assets/<id>/hidden/`，不进 SUT 沙箱。
3. **check()（≥8 断言，钉 produce）**：在独立 tmpdir 解 zip → py_compile 通过 → 无参/错参非零退 → `-h` exit 0 且含 `-o, --output-dir` → 默认(无 -o)输出落源文件目录 → `-o <dir>` 输出落指定目录且文件名 = basename+suffix → `-s .top` 改后缀生效 → `-n` dry-run 不写文件 → `-f` 覆盖已存在、不加 `-f` 遇已存在跳过 → 生成的 .xtop 首行 `XTOP ` 开头且含全部 pins（**断言 `+` 不在 pin 列表**）且末尾 token == top_cell_name → 多文件批量 → 随机化(随机抽 pin 子集断言存在)。k_check≥12 可达。
4. **negatives**：(a) 空壳 stub (b) 只 print `XTOP ...` 不解析 (c) 删 `+` 过滤逻辑的退化版（在含续行 B 上 pin 列表混入 `+` ⇒ FAIL）+ negative_selftest.py 全 FAIL。
5. §4.9 三假（empty/print/core-deleted）全 FAIL。
6. trace_source.real_task_summary 用上面原话；test_rationale = `k 条断言：①…` 与 check() 一一对应。
7. case_id 建议 `EDA-Eval-DesignFlow-GenXtopCliUpgrade-001`，落 cases/B/ + append B.jsonl，ledger mark case。

## near-dup 自检
shanliny 已有 5 case（MeaNetPathDiag / MonteMt0Stats / Mt0MeasDiag / RcVizTreeAnalyzer / WmMt0Diag）——全 mt0/meas 诊断域；本 case 是 **SRAM char 工具链里 generate_xtop.py 的 CLI 升级 + `+` 续行 bug 修复**（SPF→XTOP 生成器），动作动词「CLI 升级 + bug 修复」与既有「mt0 诊断/meas 分析」正交。无重叠。
