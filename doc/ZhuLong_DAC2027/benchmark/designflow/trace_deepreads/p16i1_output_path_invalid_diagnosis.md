# Deepread: p16i1 — 1prf.py --output path invalid + process files in cwd

**Trace**: shanliny / 10.129.2.10 / session `1793603696817_p16i1` (digital, mc20, 6 msgs+uploads, 413KB)
**Source**: 11-15 mandate Part 二 复活队列 (parked_reaudit_A REVIVABLE_QA, 旧 r? parked "Python script debug Q&A, weak"). trace_avail=EXISTS on .75 (/home/shanliny/.cline/data/sessions/1793603696817_p16i1/).

## 用户原话 (逐字)
- MSG0: 「为什么这段代码指定输出路径无效，最后这段代码会将过程文件输出在当前文件夹」 + 上传 `0_run`
- MSG16 (补充, 不满): 「你干什么，我这是一个全新的工程，和之前上传的文件都无关」

## 任务形态
debug-Q&A / analysis-only (用户问"为什么", 不要改代码). Python SRAM netlist generator `1prf.py` (基于 netlist_interface.py 的 NetTiler) 的 `--output` 行为诊断.

## trace agent 行为
agent 读 1prf.py (argparse 1510-1552 / __main__ 893-EOF / 1000-1200 / 300-450) + netlist_interface.py (100-300 / 813-EOF) + 0_run + list_allowed_files. search_codebase 多次 type-error (传 string 非 array). run_commands 被 disabled ("Raw shell tool run_commands is disabled"). **agent 始终未给出根因结论**, 用户不满. session 在 MSG22 戛然而止.

## 证据 (trace-embedded, asset_fidelity=original, 行号 " N | content")
项目文件 /home/shanliny/tiling_typical/ 已蒸发 (.75 与 10.129.2.10 均不可达), 资产全部从 trace read_files tool_results 抽取:
- `1prf_argparse.py` (1510-1552): `--output` 定义在 1528-1529, `type=str, default=""`, help="Output netlist file path (optional auto generated if not specified)"
- `1prf_main.py` (1553-1621): __main__. 1566 `if args.output:` -> 1567 `output_name = args.output`; else 1569 auto `f"CX{...}.netlist"`; 1597 `nt.write_subckt_to_file(output_name, 240)`; 1600 `with open(output_name, 'a', ...)` 追加顶层实例; 1621 print complete
- `netlist_interface_write.py` (813-842): `write_subckt_to_file(self, filename, max_len=120)`: 816 `with open(filename, 'w', ...)` 遍历 self.subckts 写入同一文件
- `0_run.txt` (用户上传, 26 行带行号): 行2/3 `#python 1prf.py ... --netlist HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.netlist --output CX64X8M4B2C1.netlist >tiling.log`; 行11-16 active `for i in $(seq 51 51); do bsub ... hspice ...; done`

## 全量 grep 文件写操作 (覆盖全部 read_files 结果)
仅: netlist_interface.py:241(读), :816(写), 1prf.py:1600(追加). **全脚本唯一文件写 = output_name 这一个文件**. 无 os.makedirs / os.path.dirname / mkdir.

## 正确根因 (从证据确定)
1. **`--output` 未被忽略**: 1566-1567 直接 `output_name = args.output`, 1597 + 1600 都用它. 它是 **文件名**, 不是目录.
2. **"指定输出路径无效"**: 脚本无 `os.makedirs(os.path.dirname(output_name))`. 若 --output 给含未创建目录的路径 (如 `/no/such/dir/x.netlist`), `open(output_name,'w')` 抛 FileNotFoundError → 用户感知"路径无效".
3. **"过程文件输出在当前文件夹" 真正来源**: (a) 用户 `--output CX64X8M4B2C1.netlist` 是裸文件名(无目录分量) → 直接落 cwd; (b) `0_run` 的 `>tiling.log` 是 **shell stdout 重定向**, 由 shell 写 cwd, 与 `--output` 完全无关. **Python 代码本身不产生任何中间过程文件** (build_top/build_all_subckt 只做内存 tiling, 不落盘).

## fix
- 代码侧: 1597 前加 `import os; d=os.path.dirname(output_name); if d: os.makedirs(d, exist_ok=True)`
- shell 侧: `>tiling.log` 改为 `<dir>/tiling.log` 或 `cd <dir>` 后再跑
- 用法侧: `--output` 给完整路径并预先 `mkdir -p`

## 合成计划 (已落地 r653)
case_id = EDA-Eval-DesignFlow-OutputPathInvalidDiagnose-001, C-A debug-Q&A / analysis-only, digital, k=14 (a-n).
交付 `output_path_invalid_diagnosis_report.json` (zip 单文件, 8 顶层段).
A=5 文件 trace-embedded; B=2prf.py DDR5 变体 (2prf_argparse/2prf_main/0_run_b, ≥8 anti-hardcode 维全异: script/project/leafcell/output_basename/log_redirect/auto_name_prefix/argparse_line/main_open_line).
check 14 条: structure(a-b)+root_cause(c-d)+code_analysis(e-f)+shell_redirect(g)+output_semantics(h)+fix(i)+evidence(j)+conclusion(k)+B judge-selfcheck(l-m)+3-seed(n).
自验: ref 14/14 PASS + 5 neg 全 FAIL distinct + 3 §4.9 fake 全 FAIL + e2e jsonl test field 抽出独立跑 PASS + negative_selftest PASS.
ledger p16i1 parked→case. parked_reaudit p16i1→DONE_r653.
