# Deepread — 1795511082423_uy3zo (siyuji @ hfeg0pgn123, mc=212)

- **来源**: `.75:/home/t0002965/log/ssh_eda_search_20261129_000259/summary.tsv` 行
  `10.129.35.222 hfeg0pgn123 siyuji 1795511082423_uy3zo.messages.json 212 synopsys:2424;netlist:553;analog:462;hspice:244;dbget:66;mosfet:56;spectre:53;schematic:38`
- **trace**: 经 eda_flow open_session → ssh hfeg0pgn123 scp
  `/home/siyuji/.cline/data/sessions/1795511082423_uy3zo/1795511082423_uy3zo.messages.json`
  (1.45MB / 138 msgs / 74 user / 64 asst, agent=lead)。real user inputs 13 条（cline `<user_input mode="act">` 块）。
- **session 主题**: Synopsys PrimeSim CCK (Circuit Check) `netlist` Tcl 命令的跨版本文档对比。

## 用户真实意图（逐条 user_input）

1. 总结 deepDFS 已知信息+推断；解释 anaExplore（V-2023.12-SP1 新增）。
2. 读 `~/Desktop/scripttest/zlong/xtalk.tcl` 看 anaExplore 能否用到。
3. 读 `/apps/synopsys/cck/U-2023.03-SP1-1/doc/ccktopicmap.xml`。
4. 看 `appMeasXtalk` 和 `circuit_traverse`。
5. 看 `appMeasXtalk.tbc` 完整脚本+文档路径，对比官方脚本 vs 用户脚本差异。
6. 问导师结论：官方成品命令不灵活，不能适应 param/model；xtalk.tcl 是资深 design+AE 搭的。
7. U-2023.03-SP1-1 vs V-2023.12-SP1 区别。
8. **生成版本对比总结**：P-2019.06-SP1-BETA vs U-2023.03-SP1 关于 `netlist` 用法区别，以及 U-2023.03-SP1 `-parser cck` vs `xa` 区别。
9. 讲 `xa` 解释器 vs `cck` 解释器区别。
10. 之前版本里有没有对这两种解释器的解释，多查找。
11. 找 S-2021.09 相关或之后版本里的解释器内容。
12. 把相关说明的位置发给我。

## 关键技术发现

- **PrimeSim CCK `netlist` 命令**: 加载待分析网表，Tcl 接口，多参数控制解析
  (`-preserve`/`-top`/`-case`/`-check`/`-keep_top_inst`/`-macrosub`/`-mark`/`-report`/`-rmdummy`/`-rmin`/`-syntax`/`-parser`)。
- **`-parser cck|xa`**: 前端解释器选择。`cck` = CCK 原生 parser，`xa` = CustomSim/XA common parser
  （U-2023.03 起引入 common parser 让 CCK 前端与 CustomSim 一致）。跨版本差异核心。
- **`deepDFS`**: `cckSearchPath -method` 的一个选项（bfs/dfs/deepdfs）；
  `cckExplore` 文档只列 BFS|DFS 但实现默默接受 deepdfs（未文档化行为）。
- **`anaExplore`**: V-2023.12-SP1 新增模拟电路探索引擎，无 `-method` 参数（替代旧 HP API）。
- **文档结构（实测真实 netlist.html, 53KB, DITA-OT 生成）**:
  - `<meta name="description" content="...">` 含 syntax 概览
  - `<meta name="DC.rights.owner" content="(C) Copyright YYYY">` — 仅 copyright 年，**非**版本号
  - `<title>netlist</title>`
  - 单个 `<table>`：首行表头 `Argument|Description`，每行 `<tr><td>参数</td><td>描述</td></tr>`
  - 参数名首列可能包 `&lt;...&gt;`（可选参数）或带取值（`-preserve gnds|none`）
  - `-parser xa|cck` 出现在 `<pre><code>` 块 + `<code class="ph codeph">` 内联

## 判可移植

原 deliverable 依赖 Synopsys 文档树（`/apps/synopsys/cck/.../doc/webworks/...`，多版本安装路径 +
专有 HTML）+ 用户私有 `xtalk.tcl`/`appMeasXtalk.tbc` → 不可直接移植到 SUT 沙箱。

**可移植抽象** = 纯 Python CCK `netlist` 命令文档版本对比器：输入两份 DITA-OT HTML 文档页
（不同版本，doc_v1=新/doc_v2=旧），提取 version / 参数列表 / parser 选项，输出 `cmp_report.json`
（v1/v2 + added/removed params + parser_added/removed）+ `summary.txt`。无 EDA 二进制/许可/项目库依赖。

## 显性化 gotcha（造题核心，均从真实文档结构提取）

- **G1 参数表排版因版本而异**：新版用 `<table><tr><td>` 表格（表头 `Argument`），旧版用
  `<dl><dt>/<dd>` 定义列表。朴素「只认 table」在旧版文档拿到空参数列表 ⇒ added_params 全错。
  （真实 trace 里 P-2019.06 旧版文档用 dl 风格，U-2023.03 新版用 table — 造题把这个结构差异显性化。）
- **G2 parser 选项位置因版本而异**：新版在独立 `<pre><code>-parser xa|cck|...</code></pre>` 块，
  旧版在描述里内联 `<code class="ph codeph">-parser cck|xa</code>`。朴素「只扫 `<pre><code>`」
  在旧版漏掉 parser 选项。
- **G3 版本号来源**：`<meta name="DC.source.version" content="...">` 才是版本号；
  `<meta name="DC.rights.owner" content="(C) Copyright YYYY">` 只是 copyright 年（2019/2021/2023）。
  朴素「取 copyright 年当版本」错。
- **参数名归一化**：首列 `&lt;-keep_top_inst 1|0&gt;` → `-keep_top_inst`（去 `<>` 取首 token）；
  `-preserve gnds|none` → `-preserve`；`file_name` → `file_name`（位置参数无 `-` 前缀，原样）。

## 与既有 case 区分（避免 dup）

- `CharSensSummaryGen-001` (r1409) = MOS 表征 summary 生成（sensitivity 比值/绝对 gotcha）— 不同算法/数据源。
- `PulseWidthSweepExtract-001` (r1408) = WaveView swept 波形脉宽提取（起始电平配对 gotcha）— 不同。
- `NetlistHierPathResolve-001` (r1407) = SPICE 扁平 netlist 层级路径解析（扁平顶层/总线数组 gotcha）—
  本 case = HTML 文档版本对比（table/dl/pre/inline 多格式解析 gotcha），数据源=文档 HTML 非 netlist，正交。
- `RunDirDerive-001` (r1405) = VT/corner 后缀→目录名推导 — 不同。
- 全无「CCK 文档跨版本结构化对比」类 case。

## case 形态

- **task_id**: EDA-Eval-DesignFlow-CckNetlistDocCmp-001
- **domain**: spice_sim (CCK = circuit check, SPICE 网表工具链；B 域)
- **layer**: L1 judge-run, LIVE-NA, judge_layers=[L0,L1]
- **candidate**: `cck_doc_cmp.py <doc_v1.html> <doc_v2.html> <out_dir>` → cmp_report.json + summary.txt
- **A/B 双输入 token-structurally 不相交**:
  - A: v1=U-2023.03-SP1 (table, 13 params, parser xa|cck) / v2=P-2019.06-SP1 (dl, 10 params, parser cck)
  - B: v1=V-2023.12-SP1 (table, 15 params 含 -vsrc/-netlist_filter, parser xa|cck|spice) /
    v2=S-2021.09-SP1 (dl, 12 params 含 -vsrc/-legacy_mode, parser cck|xa)
  - 版本号/参数集/parser 选项/拓扑全不同。
- **15 断言** (a,b,sa 静态 + c..n L1)：含 G1 trap(g v2.params dl)、G2 trap(k v2.parser inline)、
  G3 trap(d/e version meta)、removed 方向(i)、anti-hardcode(n A-only 版本字面量)、确定性(m)。
- **§4.9 negatives 4 个 first-fail distinct**: solve_empty→c / solve_print_expected→d(硬编 A gold) /
  solve_table_only→g(G1 不解析 dl) / solve_pre_only→k(G2 不解析 inline)；trio{c,d,g} 3-distinct，4th{k}。
- **自验全绿**: (1) ref solve 15/15 PASS (2) negative_selftest ALL_FAIL+TRIO_DISTINCT+4TH_FAIL
  (3) SKIP_RUN=1 eval/run_one.sh framework accepts (B.jsonl 612, infra_fail=0, hook_blocks=0, workdir clean no-leak)。

## 落盘

- `cases/B/EDA-Eval-DesignFlow-CckNetlistDocCmp-001.json` (test field=check.py, k_check=15, sha synced)
- `assets/<CID>/{doc_v1_A.html, doc_v2_A.html, task_brief.md, hidden/{doc_v1_B.html, doc_v2_B.html, hidden_manifest.json}}`
- `reference/<CID>/{check.py, solve.py, cck_doc_cmp.py, negative/{solve_empty, solve_print_expected, solve_table_only, solve_pre_only, negative_selftest}.py}`
- 台账 uy3zo claim+mark case
- 本 deepread 落 `designflow/trace_deepreads/1795511082423_uy3zo_cck_netlist_doc_cmp.md`
- eda_flow session closed
