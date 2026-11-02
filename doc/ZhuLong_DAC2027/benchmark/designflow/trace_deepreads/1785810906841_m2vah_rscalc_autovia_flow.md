# trace deepread — 1785810906841_m2vah (e0014566 @ hfeg0plg58, mc=975)

- **session**: `/home/e0014566/.cline/data/sessions/1785810906841_m2vah/1785810906841_m2vah.messages.json` (573 msgs, 447 user / 420 assistant, agent=lead)
- **workdir**: `/home/e0014566/test_layout_rscalc_flow_3`
- **tools freq**: run_commands:182, read_files:41, editor:38, SandBox_MCP run_code:23, search_codebase:1
- **keyword summary**: netlist:755 / virtuoso:731 / calibre:51 / hspice:15 / pyAether:5

## 用户意图流（11 条 user text 轮）
1. **U#1 (idx=0, 需求轮 — 用作 A 档任务说明)**：分析两个 skill；梳理配置抽出共享参数到 common.config；构建「算电阻→优化版图→降电阻」工作流；写 prompt_flow.md；上一步输出=下一步输入；降幅+最大迭代次数写进配置。
2. U#2：先分别跑通两个工具，不要一上来做整体 flow。
3. U#3：把 common.config 里的 powernet 挪到 rscalc.config（不公用）。
4. U#4：两个工具的 powernet 支持为空→自动检测全部 power net，固化逻辑。
5. U#6：autovia 只发现一个 powernet，rscalc 发现多个，分析差异。
6. U#7：看 flow 流程需不需要改，行就跑。
7. U#8：优化电阻是**所有点位**都要优化，不是只优化最大的。
8. U#9：再完整跑一遍 flow。
9. U#10：autovia 是否只能在低层金属找 via 插入位置。
10. U#11：再引入 powerfill，放到 autovia 后面，构成 算电阻→autovia→powerfill→算电阻 循环迭代；共用配置提到 common.config；上一步输出=下一步输入。

## 工具链（真实产物）
- **virtuoso-rscalc-runner**：RsCalc。`assets/run_rscalc_nogui.il`（645 行）含 `RunRsCalcNoGui()` 入口、`CXMTutRscalc_run` 调 `/proj/shdc/cad/script/rscalc/runrsc` 经 `bsub -I -n <parallel> -q rscalc` 算每个 check point 的 parasitic resistance，输出 `RSDB_<net>/<net>.rvn`（第 12 列=电阻）。配置占位 `load("RSCALC_CONFIG_PLACEHOLDER")` + 尾部 3 行提示。空 pwrNets → `CXMTAutoDetectNets` 从 RTEXT label 自动检测。
- **virtuoso-autovia-runner**：AutoVia。`assets/run_autovia_nogui.il`（770 行）含 `RunAutoViaNoGui()`、插 via + Calibre DRC（`drc.rep` TOTAL RESULTS）+ `leoXstreamOut`/strmOut 写 merged layout（`<outLibName>/<outCellName>`）。配置 `load("/home/.../run_autovia_config.il")` 块 + 尾部提示。空 pwrnets → 从 GDS TEXT label（带 `!`）自动检测。
- **virtuoso-powerfill-runner**：PowerFill（U#11 引入，填 power rail / metal widening，写进一步 merged layout；trace 末段引入，本 case 不强制交付其生成器）。

## 配置合并层（可复用产物 — 本 case 的交付目标）
- `gen_rscalc_agent.py` / `gen_autovia_agent.py`：读 common.config（共享）+ 工具 config + .il 模板 → 产出**自包含** agent .il：配置内联、替换 `load()` 占位、丢流控键（targetReduction/maxIterations）、加 `Run*NoGui()` 自启动。AutoVia 做名字映射 project→projName / viewName→viewType / pwrNets→pwrnets。向后兼容（不传 common.config 也工作）。
- `common.config`：共享 process/project/libName/cellName/viewName + 流控 targetReduction/maxIterations。**不含 pwrNets**（pwrNets 在 rscalc.config，pwrnets 在 run_autovia_config.il，因两工具读 net 名的源不同）。
- `prompt_flow.md`：迭代流文档（AutoVia→PowerFill→RsCalc 循环）、收敛判据（每个 check point R_i ≤ R_0·(1−targetReduction)）、step I/O 链式、降幅+最大迭代次数。

## 真实数值（trace 中验证）
- gen_rscalc on A：内联 18 参数，0 个 RSCALC_CONFIG_PLACEHOLDER 残留，含 `RunRsCalcNoGui()`。
- gen_autovia on A：load() 块替换为内联，projName/viewType/pwrnets 映射正确，含 `RunAutoViaNoGui()`。

## case 抽取
- **case_id**: EDA-Eval-DesignFlow-RsCalcAutoVia-001（shard B / characterization / A 档 faithful / L2）
- 交付：6 文件（gen_rscalc_agent.py / gen_autovia_agent.py / common.config / rscalc.config / run_autovia_config.il / prompt_flow.md）打 submit.zip
- 隐藏 B：同结构 .il 模板 + 值全不同的配置（process=cxmt10G5/project=ddgoa/libName=libRscB/cellName=cellB7/pwrNets="vdd vss"/... + autovia pwrnets="vdd! vss!"/outCellName=cellB7_opt/coreNum=8/viaV5=t/viaRDV=t + 流控 0.4/8）
- check：14 条独立条件，subprocess 真跑生成器校验内联结构；3 negative + §4.9 三假提交自验全 FAIL；ref PASS。
