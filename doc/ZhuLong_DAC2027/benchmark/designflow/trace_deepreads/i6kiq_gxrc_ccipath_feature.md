# deepread: i6kiq — glory-rc-flow skill 新增 --cci-path 可配置功能

- session: 1792055462058_i6kiq
- user: simplec @ 10.129.2.11 (hfeg0plg103)
- mc: 38 (netlist:51 lvs:50 verilog:27 calibre:21 drc:20 pyaether:19 techfile:16 aether:77)
- domain: schematic_netlist (RC extraction flow / StarRC gxrc / netlist grounding)
- ledger: claimed r844 (2026-11-18), status=claimed → next round synthesize
- trace size: 1.4MB / 310 msgs / 8 real user inputs
- A-grade verbatim 候选轮: U#0（提出需求，未给根因/方案 → A-eligible）

## 用户意图（逐字）

**U#0（A-eligible，本轮选料轮）**:
> 我要对glory RC flow 这个skill 新增一个功能：可以指定cci的路径

U#1（后续，增量需求，不作 A 档任务说明）: 增加修改 cell.list 功能（按 CCI_data 数据修改 work 下 cell.list，全部或随机抽 20 个）。
U#2/U#4: 指定 cci 路径为 `/home/simplec/to_simplechen_starrc/CCI_data_glory`，cell.list 选前 15 个跑。
U#3: 改了 `gxrc_autorun2.py` 第 106 行 bsub，希望用 bsub 运行脚本。

→ U#0 是干净的单轮"给已有 skill 加一个可配置参数"的 produce-task，用户只提出需求、未给实现，符合 A 档选轮规则。

## 真实工具链与金标准（assistant 实际产出）

1. 调 `glory-rc-flow` skill；读 `/home/simplec/.cline/scripts/data/glory-rc-flow/run_autorun_flow.py`（主流程脚本）、`SKILL.md`、`run_glory_flow.sh`、`setup_glory_flow.py`、`fix_and_run.py`。
2. **关键发现**：`run_autorun_flow.py` 第 16 行硬编码 `cci_path = "/home/simplec//to_simplechen/CCI_DB/"`，在 `creat_task_file()` 里把每个 cell 的 `{cell}/CCI_DB` symlink 进 task 目录。
3. **修改（金标准）**：
   - 加 `import argparse`
   - 新增 `parse_args()`：`parser.add_argument("--cci-path", dest="cci_path", default=cci_path, help="Parent directory containing {cell}/CCI_DB folders to symlink into each task directory. Default: %(default)s")`；`return parser.parse_args()`
   - `main()` 里 `args = parse_args()`；用 `args.cci_path`（变量名 `cci_dir`）替换原硬编码 `cci_path`，传入 `creat_task_file()`
   - 保留 default = 原 `cci_path`（向后兼容，无参运行 = 原行为）
4. 验证：`py_compile` SYNTAX OK；`--help` 打印出 `--cci-path`（确认 argparse 注册成功）。

## 资产可达性

- 原始脚本 `run_autorun_flow.py` 可从 `10.129.2.11:/home/simplec/.snapshot/SH-*/gxrc_autorun2.py` 及 `/home/simplec/.cline/scripts/data/glory-rc-flow/run_autorun_flow.py` 取（trace 内 assistant read_files 亦有完整内容，可从 tool_result 提取内联）。
- 完整原始脚本内容在 trace msg read_files 结果里（msg A#6/A#8/A#10/A#22），无需 scp 大文件即可重建 asset A。
- 用户真实路径 `/home/simplec/to_simplechen/CCI_DB/`、`/home/simplec/to_simplechen_starrc/CCI_data_glory`、`cases/list` 均在 trace 内可达（redonly 已验证）。

## 拟造 case 设计（next round 合成）

- **case_id**: `EDA-Eval-DesignFlow-GxrcCciPathArgFeature-001`
- **domain**: schematic_netlist · **track**: A 档 verbatim（U#0 逐字）· **level**: L1（离线 Python 静态改 + subprocess 跑 --help/dry-run，不需 StarRC 真跑）
- **资产 A**（visible，SUT 看）: `run_autorun_flow_A.py`（= 原始脚本，硬编码 `cci_path = "/home/simplec//to_simplechen/CCI_DB/"`，含 `creat_task_file()` 用 cci_path 建 symlink；保留真实函数名 creat_task_file/run_csh/main）+ `prompt.txt`(U#0 逐字) + `task_brief.md`(交付接口≤3 行：改 run_autorun_flow.py 加 --cci-path，打包 submit.zip)。
- **hidden B**（不进 SUT 沙箱）: `run_autorun_flow_B.py`（结构同构但硬编码路径不同，如 `cci_path = "/proj/alt/CCI_DB_v2/"`，creat_task_file 里把 cci_path 拼成 `{cci_path}/{cell}/CCI_DB`，可能多一个中间函数层）+ `hidden_manifest.json`。check() 只跑 B：候选脚本必须能在 B 上接受 `--cci-path <B_alt_path>` 并把该值透传到 symlink 生成（反硬编码 A 的路径）。
- **候选交付**: 改好的 `run_autorun_flow.py`（接受 `--cci-path`，default=原值，main 透传到 creat_task_file），打包 `outputs/submit.zip`。
- **reference**: `run_autorun_flow_REF.py`（argparse + default 保留 + main 用 args.cci_path 传 creat_task_file）+ `reference_submit.zip`。
- **check.py 拟定 ≥14 条件 a-n**:
  - (a) 合法 zip 含 run_autorun_flow.py
  - (b) py_compile 通过
  - (c) `import argparse` 存在
  - (d) `parse_args`/`ArgumentParser` 函数存在
  - (e) `--cci-path` 选项注册（`--help` 输出含 `--cci-path`）
  - (f) `--help` exit 0
  - (g) 无参运行 default = 原 cci_path（向后兼容，B 上 default=B 原值）
  - (h) `--cci-path <alt>` 被正确解析（parse_args 返回值/ sys.argv 透传）
  - (i) main() 调用 parse_args 并用其结果
  - (j) creat_task_file 收到的是 args.cci_path 而非硬编码（subprocess dry-run / monkey-patch os.symlink 捕获拼接路径含 alt）
  - (k) **cross-input guard**: 在 hidden B 上 `--cci-path <B_alt>` 运行，symlink 目标含 B_alt 而非 A 的 `/home/simplec//to_simplechen/CCI_DB/`
  - (l) **反硬编码**: 候选若忽略 args 直接用硬编码 A 路径 → B 上 symlink 目标仍为 A 路径 → (k) FAIL
  - (m) default 兜底：不传 --cci-path 时 B 上 symlink 用 B 原硬编码值（验证 default 保留逻辑）
  - (n) 3-seed 确定性（argparse 解析稳定）
  - （可选 (o) bsub/并发逻辑未破坏：concurrent.futures / subprocess 调用结构保留）
- **negative/**: ≥3 假提交（empty zip / stub 只 print "SYNTAX OK" / core_deleted 删掉 parse_args 调用）+ naive（hardcode A 路径忽略 args → (k) FAIL）+ `negative_selftest.py` NEG_RC=0。
- **§4.9 退化**: (a)空壳→a (b)只 print 期望→f/e (c)删核心 parse_args→i 全 FAIL。
- **判分隔离**: SUT workdir 只放 prompt.txt + run_autorun_flow_A.py + task_brief.md；hidden B + check.py + reference/ 不进 SUT。
- **test_rationale**: `14 条断言：①zip 含脚本 ②py_compile ③argparse import ④parse_args 函数 ⑤--cci-path 注册 ⑥--help exit0 ⑦default 保留 ⑧--cci-path 解析 ⑨main 调 parse_args ⑩creat_task_file 用 args.cci_path ⑪B 上 --cci-path 透传 ⑫反硬编码 A 路径 ⑬default 兜底 ⑭3-seed 确定性`（k_rationale=k_check=14≥8 ✓）。

## 下轮 ETA

r845 第一件事：从 `.snapshot` 或 trace tool_result 取原始 `run_autorun_flow.py` 全文 → 建 asset A + hidden B + REF + check.py(14) + negatives → 自验（ref PASS / neg FAIL / §4.9 / 3-seed）→ 落 D.jsonl → mark case。预算 ~25 min（设计已定型，纯落地）。

## 本轮结论

r844 = 选料/深读轮 · 0 case · DEBT:1（i6kiq deepread → r845 合成）· 非凑数。
**真实成果**：r843 "D-pure fresh 池 mc10-30 第十三次枯竭" 结论被证伪——根因是 ledger 排除键计算 bug（台账行存 `<sess>.messages.json` 后缀，而 fresh 过滤用 `<sess>`/`<suffix>` 未做 `.messages.json` strip → 误判已 claim 的 frplj/cepxt/7aypg 为 fresh，又误判真正 fresh 的为已 claim）。修复后用 `trace_ledger_*.tsv` 全量 + `.messages.json` strip 归一化重算：**D 域 mc≥10 真正 fresh = 203 条**（mc≥30: 56 / mc10-29: 147），其中 dpos≥50 的高纯度候选 10+ 条（w4ghz analog:6598 / t5ge3 schematic:149 / odjfu schematic:105 / 9dj4b netlist:59 / i6kiq netlist:51 等）。D 池远未枯竭，r840-r843 四轮 BLOCKED 的池前提被推翻。
