# 深读笔记 · 4fq1p · t0002224@hfeg0pkn004 · mc=347 · schematic_netlist

> shard D #520 选料深读。资产可达性：真实 fullchip.cdl 在 `/proj/ddcpb/...` Permission denied（资产可达性枯竭第三模式持续）；但用户最终交付 `wl_prune_cli.py` 在 `/home/t0002224/spicepurning/` **可达**，可直接读取作为金标准机制依据。

## 真实任务（用户原话轮次）

- U#0: `/home/wellesc/netlist_prunning_v2 帮我看一下这个目录中的项目，详细介绍`
- U#26: `现在我想从一个section中抽取一个wordline相关的电路，我需要提供什么？是否可以实现`
- U#30: `我想看这个信号 XI_Array24GTop/XI_Array12G_Top/XI_Array1d5GBK2/XI_m1d5G/XIm768Meg_U/XImarray_53/GrDecN2<131>，能否从XIm768Meg_U中提取？`
- U#61: `把 /proj/ddcpb/V0/workdir/shunlinp/daoda 这个目录copy（含 ddcpb fullchip 网表 fullchip.cdl）`
- U#165: `先只做可行性/规模分析（定位该 wordline 的 cell 闭包、器件数、netlist_v2 能否 build）`
- U#185: `直接在这份 LP5TOP 上做 GrDecN2<131> 的目标导向闭包提取 + 剪枝（产出 wordline 切片）`
- U#257: `把 build_lp5_wl2.py 整理成带参数的交付版（--seed m1d5g_top --max-nets 6e7 等可传）`
- U#269: `python3 wl_prune_cli.py --netlist LP5TOP/netlist.presim --header LP5TOP/input.ckt --seed array11meg_ou_ccr --net grdecn2<131> ...`

**金标准机制**（读取 `/home/t0002224/spicepurning/wl_prune_cli.py` 295 行）：

1. `scan(netlist)`：解析层级 SPICE 网表——`.subckt`/`.ends` 入栈、`+` 续行合并、token 化为 `cell_stmts{cell: [(lineno, toks)]}`。
2. `collect_param_names(args)`：从 `--header`/netlist 顶部 `.PARAM` 段提取**声明无值的顶层参数名**（token after `.param`，过滤 `param` 自身与 `.` 开头）。
3. `build_deck(args, cell_stmts)`：
   - **闭包**：从 `--seed` BFS，沿 `X`-实例（`toks[0][0]=='x'`）的 master（`master_idx`：`=`-参数前最后一个 token）若 master 在 `defined`（有 `.subckt` 定义）则加入闭包。
   - **模型 stub**：被 X 引用但无 `.subckt` 定义的 master（model 卡 nmos/pmos/nand 等）→ 按端口数（`len(toks[1:mi])`）生成空 `.subckt <model> n0 n1 ... / .ends`；多端口数不一致记 inconsistent。
   - **剥 context**：cell body 中 `.ic`/`.nodeset`/`.save`/`.print`/`.plot`/`.probe`/`.measure`/`.meas`/`.tran`/`.op`/`.dc`/`.ac` 被剥离（`--keep-ic` 保留）。
   - **发射 deck**：`.param NAME=0`（每个 header 参数）+ 排序后闭包各 cell（`.subckt` header + body + `.ends`）+ 模型 stub + `.end`。
4. 输出 `<prefix>_<seed>_deck.sp`，再交给 netlist_v2 build/prune（外部包，**本 case 不含**——deck-building 是自包含核心）。

## B-grade synthesized 设计（ClosureDeckBuilder-001）

**SUT 任务**：写 `closure_deck_builder.py --netlist <deck> --header <hdr> --seed <cell> --outdir <dir> --prefix <p>` → 输出 `<outdir>/<prefix>_<seed>_deck.sp`，实现 scan + closure + model-stub + context-strip + param-default + emit，纯 stdlib。

**A/B/C 三档网表**（net/cell/model/param 前缀全不相交）：
- A（SUT 见）：`WLdecTop_A` → `decA_sub`/`invA_sub`（defined）+ `nandA_model`/`norA_model`/`nbufA_model`（undefined → stub）；含 `.ic`/`.nodeset` context + `+` 续行 + `*` comment；header `.param WLDRV WLBYP`。
- B（hidden，check 跑）：`SenseAmpTop_B` → `sa_sub`/`blkB_sub`（defined）+ `preB_model`/`nmosB_model`/`pmosB_model`/`latchB_model`（stub）；含 `.tran`/`.ic`/`.nodeset`/`.save` context；header `.param SAVDD SAPRE SAWL`。
- C（嵌入 check.py 反硬编码）：`MuxTop_C` → `muxC_sub` + `drvC_model`/`pasC_model` stub；含 `.print`。

**check.py 12 条件 a-l 独立 oracle**（manual line parse + set ops，与 ref state-machine 结构不同）：
a 跑通B出deck / b py_compile+无禁import/eval/exec/B字面量/泄漏 / c deck 以 .end 结尾 / d deck 含闭包cell的.subckt/.ends对（集合匹配）/ e 闭包集正确（oracle BFS vs ref）/ f undefined-model stub 端口数正确 / g context 指令剥离 / h header .PARAM→.param NAME=0 顶部 / i + 续行合并 / j * 与 // comment 剥离 / k 反硬编码 C 闭包+stub 正确 / l 3-seed sha256 一致。

**维度正交**（vs 既有 D case）：
- vs SchemExplodeLabel-001（#503 标签展开）：不同——本 case 是层级闭包提取+stub 生成，非标签展开。
- vs NetlistStructDiff-001（#434 网表 diff）：不同——本 case 是单网表闭包提取，非两网表对比。
- vs HiePathFinder-001（#474 verilog hie 路径查找）：不同——本 case 是 SPICE .subckt 闭包提取+deck 重建，非 verilog 信号路径。
- vs NetlistGlobResolve-001：不同——本 case 是闭包剪枝，非 glob 展开。
⇒ 非 dup ✓。

**dup-check**：t0002224 D.jsonl=0（fresh user）+ ClosureDeckBuilder task family 无 + 4fq1p session 无既有 case ⇒ 非 dup ✓。

**difficulty=L1**（诚实标：SUT 纯 stdlib SPICE 文本解析+闭包计算，无 EDA 工具运行时，与 #519/#518 一致；资产可达性枯竭逼合成）。

**资产可达性**：`/proj/ddcpb/.../fullchip.cdl` Permission denied ⇒ B-grade synthesized（第三模式实证，呼应 r514 P-002 @D）。但用户真实交付 `wl_prune_cli.py` 可达，金标准机制有真实依据（非凭空合成）。

**#520 偿还计划**：本轮直接合成交付（deepread + 合并一轮完成，§3 单轮闭环）。
