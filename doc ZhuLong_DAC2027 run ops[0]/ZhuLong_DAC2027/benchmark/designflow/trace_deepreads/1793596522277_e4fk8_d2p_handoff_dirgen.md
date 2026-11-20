# trace_deepread: 1793596522277_e4fk8 (e0045128 @ hfeg0pkn005, mc=53)

**Session**: 3183 lines / 142 msgs / 80 user turns. cline python-runner sandbox.
**Domain**: digital (D2P = Digital→PD handoff 目录结构生成). shard A.

## 用户意图（逐字）

- **U#0 (msg 0, A档任务说明)**: "帮我生成一个python脚本，功能是可以帮我创建/proj/lacaa/TV1_TestChips/CXTV1_FS001A/exchange/dig2pd/Datain_20261014/下面的目录，和readme文件"
  - 纯提需求（生成 Python 脚本创建交接目录+readme），未给根因/修复 → **A档合格**。
- **U#20 (msg 33)**: "在当前目录新建和.../Datain_20261014/下面11个子目录一样的子目录，产生一个和.../readme一样的文件"（明确 11 子目录 + 当前目录 + 同 readme）。
- **U#35 (msg 61)**: "脚本是独立运行的，运行时和.../Datain_20261014/下的内容无关，只是创建11个目录和一个readme文件"（**独立运行，不读源**）。
- **U#46 (msg 83)**: "不需要--dry-run 的功能"（去 dry-run）。
- **U#55 (msg 99)**: "请读.../readme的内容，在脚本执行时，不用再读了，直接把这段内容打印到当前目录的readme中"（**内置 readme 内容**，运行时不读源文件）。
- **U#68 (msg 123)**: "把注释都改成英文"（**英文注释**）。
- U#4 = U#0 重发（首次 code_sidecar_sigterm）。

## assistant 工具链

editor 写 `create_d2p_dir.py` → 重构为 `copy_d2p_struct.py`（多轮 diff）：
1. 初版从源目录 listdir 读子目录 + 读 readme（U#20 后）。
2. U#35 改独立运行：内置 `DEFAULT_SUBDIRS`（11 个）+ `FALLBACK_SUBDIRS`。
3. U#46 删 `--dry-run` 分支。
4. U#55 把 readme 内容内嵌为 `README_CONTENT` 常量，运行时不再读源。
5. U#68 注释/docstring/print 全改英文。
python-runner 在 `_indep_test` 测试目录反复验证：11 dirs [OK] + readme 生成。最终 `copy_d2p_struct.py` 82 行，sandbox 路径 `/home/e0045128/sandbox/copy_d2p_struct.py`（已 scp 取回作 gold）。

## gold = 真实产物（人工复核）

`copy_d2p_struct.py`（独立运行）：
- `DEFAULT_SUBDIRS` = 11 个：`00_lib_path, 01_netlist, 02_sdc, 03_upf, 04_phy_constraint, 05_cts_constraint, 06_scan_def, 07_lec_constraint, 08_b2b_list, 09_mtbf_sync_list, 10_incr_sdc`
- `README_CONTENT` = 源 readme 原文（813 字节，逐行描述 11 个交接目录用途）
- `main()`: `os.getcwd()` → 打印 [Info] → `os.makedirs(exist_ok=True)` 每个子目录打印 [OK] → 写 `readme` 文件 → 打印 [OK] readme
- 英文注释，无 --dry-run，无 /proj 源读取

## 本 case 泛化（反硬编码）

gold 是硬编码（11 dirs + readme 内嵌），无法在隐藏 B/B2 上泛化。按 r232 先例，reference 泛化为 **config-driven**：读 `config.json` 的 `subdirs` + `readme_content`，在 CWD 创建。A config = 真实 11 dirs + 真实 readme（`source_readme.txt` = 源 readme 原文作 asset）。隐藏 B（8 dirs rtl/tb/syn/...）/ B2（9 dirs doc/sim/...）结构对立 + 随机化。

## 判分

check.py 13 条 a-m：静态结构 a-g（zip/compile/config/standalone无源路径/英文注释/makedirs/readme）+ A 子进程 h-k（rc0/11 dirs 集合相等/readme 逐字/[OK][Info]）+ 隐藏 B/B2 子进程 l-m（dirs 集合相等 + A 目录名不泄露 + readme 匹配）。自验全绿（REF 13/13 + 5 negs FAIL distinct{c,f,i,j} + §4.9 三假全 FAIL + selftest DISTINCT=4）。k=13 闸门 PASS。test_sha8=30615da8。

---

## 附：本轮弃用 trace 1791871316059_iih6g? (否，r232 已用)。本轮先选 aq5lg 弃用记录

**aq5lg (johnl@hfeg0pkn001, mc131)**: SGE "Port map mismatch" 诊断。assistant 报告称 `change_names -rules verilog` 把 bus 输出端口拆成标量 `BA_4/BA_3...`。**经核实为错误诊断**：`T_mBistTopNew_mapped_aether.v` 中 `mbist_address_decoder` 端口仍为 `output [4:0] BA;`（bus 形式），全文 0 处 `output BA_`。用户两次质问"你确定吗 你要做实验验证"即因此。无 accepted gold → **parked**，不入 case。
