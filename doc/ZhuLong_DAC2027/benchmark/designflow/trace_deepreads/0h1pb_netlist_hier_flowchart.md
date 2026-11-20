# 深读 0h1pb — getNetlistHier 代码流程图生成

- **trace**: 1790734282663_0h1pb · user chengk · host 10.129.35.121 · mc51 · domain schematic_netlist
- **msgs**: 10 total · 1 real user turn (`<user_input mode="act">`) · 极小 trace
- **A-faithful produce-task = U#0**（唯一提出需求，未给根因/修复）

## U#0 逐字（A-faithful prompt）
```
仔细阅读/home/chengk/work/ZL_work/getNetlistHier_v1/下的代码，给出流程图
```

## 真实代码（/home/chengk/work/ZL_work/getNetlistHier_v1/，6 个 .py，881 行）
- **run.py** (110): CLI 入口 `python run.py <IddCsvFold> <measFile> <netlist> <topSubckt> <outFold>`。argv 长度校验（!=6 → Usage+exit1）。6 步流水：
  1. `parse_meas(meas_file)` → meas_result{instHdl:(fullName,pairs)}
  2. `get_power_csvs(csv_fold)` → `filter_power(csv_paths,"xi_channel",1000)` → filter_csv
  3. `collect_insthdls(filter_csv)` → needed_insthdls
  4. `parse_netlist(netlist)` → (subckt_calls, subckt_devices, subckt_list, inst_list, top_insts)；**决策分支**：`if top_subckt not in subckt_calls → [Error] exit 1`
  5. `PathResolver(subckt_calls, subckt_devices, top_subckt)` + `build_insthdl_to_realpath(meas_result, needed_insthdls, resolver)` → insthdl_to_real
  6. `output_power_hier(insthdl_to_real, filter_csv, out_fold, hier_depth=50, idd_threshold=100)` → 写 CSV (hierarchy,idd)
- **pipeline.py** (170): `build_insthdl_to_realpath`（fullname_to_insthdls 映射 → resolver.resolve_batch → map back，含 unmatched_meas 计数）；`output_power_hier`（每 CSV 写 hierarchy,idd，按 depth<hier_depth 且 idd>threshold 过滤，skipped 计数，OSError 跳过）
- **netlist_parser.py** (158): `preprocess_iter`（丢 `*` 全行注释、剥 `;`/`$` 行内注释、合并 `+` 续行）；`tokenize`（`,` 也作分隔）；`parse_netlist`（建 subckt_calls{subckt:{inst:called_subckt}} / subckt_devices{subckt:{inst:'R'|'C'}} / subckt_list / inst_list / top_insts）
- **meas_parser.py** (136): parse_meas → {instHdl:(fullName,[(rail,port)])}
- **csv_utils.py** (121): get_power_csvs / filter_power / collect_insthdls
- **path_resolver.py** (186): PathResolver 类，on-demand 遍历 call graph，resolve_batch，stats() cache

## trace agent 工具链
read_files 全部 6 个 .py + README → 产出 Mermaid 流程图（assistant#9，15059 字符）。

## 金标准 = trace 末尾用户接受的结果（assistant#9 Mermaid 流程图）
格式 = Mermaid `flowchart TD`，含：
- `classDef` 样式（dataStore/process/io/decision/startEnd）
- 外部 I/O 节点：MEAS_FILE / NETLIST / CSV_FOLD / OUT_FOLD
- START 节点：`run.py main()`
- 6 个 `subgraph Step1..Step6`：parse_meas / get_power_csvs+filter_power / collect_insthdls / parse_netlist / PathResolver / output_power_hier
- 数据存贮节点：meas_result / filter_csv / needed_insthdls / subckt_calls / insthdl_to_real
- **决策分支节点**：top_subckt not in subckt_calls → [Error] exit 1
- 边：main → parse_meas → get_power_csvs → filter_power → collect_insthdls → parse_netlist → {top_subckt check} → PathResolver → build_insthdl_to_realpath → output_power_hier → OUT_FOLD

## 合成策略（下轮执行）
真实代码不可附加（用户私有 /proj 路径 + 881 行依赖外部 netlist/csv）→ **B-grade synthesized**：
- 参数化生成 A/B/B2 三套「多模块 Python pipeline」代码目录（每套 = main entry + 3-4 被 main 调用的函数模块 + 1-2 决策分支如 argv 校验/文件存在检查/阈值过滤），模块名/函数名/分支条件/步骤数跨变体不同（反硬编码）
- 金标 `code_flowchart_ref.py <code_dir>`：扫描 .py 文件，提取 `def` 名 + 函数内调用 + `if`/argv 校验分支，emit Mermaid `flowchart TD`（main 入口节点 + 每个被调函数节点 + 调用边 + 决策菱形 + I/O 节点）
- check 验证流程图含 B 的模块/函数节点 + 调用边 + 决策分支 + 反硬编码（重跑 A 产 A 节点 ≠ B）+ 跨输入 B2 + CLI + 确定性（≥12 条件 a-l）
- A-faithful prompt = U#0 逐字；task_brief 只写交付接口（`code_flowchart.py <code_dir> -o flowchart.mmd`，Mermaid flowchart TD 格式，打包 submit.zip）

## 状态
**claimed + deepread 完成，未合成**（DEBT）。原因：本会话发现 ziv3j 已被并行 shard D #311 会话交付（CdlXistorAudit-001），清理重复后改选 0h1pb；40 分钟硬预算内无法完成合成。下轮**第一件事**：基于本深读合成 NetlistHierFlowchart-001（L1 代码流程图生成，schematic_netlist）。
