# trace deepread — yzpwv (UlvtDelvtoInject-001)

- session: 1795051687187_yzpwv.messages.json
- user/host: joeyl @ hfeg0plg74
- match_count: 246, domain: spice_sim (spice-ratio 0.92, netlist:1103 + hspice:93)
- trace size: 159 msgs
- status: case → EDA-Eval-DesignFlow-UlvtDelvtoInject-001 (r977)

## 用户原话
> 请帮忙用这个：/home/joeyl/ulvt_delvto/ 给这里的netlist：/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/simulation/Bias/hspiceD/schematic/netlist/netlist 加vth=-0.2v

## 意图
用 `/home/joeyl/ulvt_delvto/` 工具包（含 `reduce_vth.py` + `config.cfg`）给 FineSim/HSPICE **Bias** netlist 里的 ULVT 管（`pulvt_ckt` / `nulvt_ckt`）追加 `_delvto=-0.2`，降低 vth。

## trace 实际行为
- assistant 跑 `reduce_vth.py`，扫描 netlist 找 X 实例语句中模型为 `pulvt_ckt`/`nulvt_ckt` 的器件，在语句末尾追加 `_delvto=-0.2`（已有则替换值，幂等）。
- 修改 3 个器件：XM10/XM9（pulvt_ckt）+ XNM18（nulvt_ckt）。
- 支持 `+` 续行（`_delvto` 追到语句最后一条物理行）、行尾 `$`/`//` 注释（插到注释前）、token 精确匹配（不误改 `delvto_user`）。
- 非 in_place 模式输出 `<原名>_delvto<值>.sp`。
- verify PASS。

## 资产便携性
- /rundata 原 netlist 是 joeyl-only 权限拒绝；工作副本 `/home/joeyl/ulvt_delvto/work/netlist` 可读（即 netlist_A，md5 9d0667b1368ab9d5b2a7812481b6faa7，84 行）。
- reduce_vth.py（313 行）+ config.cfg + AI_USAGE.md 全部可读。
- A-faithful（文本便携）。

## case reframe (r977)
- trace 意图 = use-tool（用现成工具包）；case 交付 = produce-tool（写 reduce_vth.py + config.cfg，功能同 trace 工具）。同形映射，意图零偏移。
- visible `reduce_vth_ref.py` = **基线**（仅处理单行 X 实例语句，不处理 `+` 续行、不处理 `$` 行内注释）；候选须按 AI_USAGE.md 补全这两项。
- hidden B = **VrefBuf** cell（不同 cell）：4 ULVT（2 pulvt_ckt XM_A/XM_B 在 VrefBuf_Core subckt + 2 nulvt_ckt XM_ULVT_A/XM_ULVT_B 在顶层），含 `+` 续行（XM_ULVT_A）和 `$` 行内注释（XM_ULVT_B）两个 A 不具备的边角；delvto=-0.15（不同值）。anti-hardcode-A：值(-0.2→-0.15)、数量(3→4)、cell(Bias→VrefBuf) 全异。
- check.py 14 条 a-n：zip 含 .py+config / py_compile / B exit0 / 输出非空 / 恰 4 ULVT 改 / delvto_user=0 保留 / 非目标模型不动 / `+` 续行 _delvto 在末行 / `$` 注释 _delvto 在前且注释保留 / 行数保持 / 幂等 / 3-seed 确定性 / anti-hardcode-A。
- k_check=14==k_rationale=14 ✓
- 自验：ref 14/14 PASS；NEG 5/5 FAIL（neg_empty[e]/neg_print[e]/neg_core_removed[f]/neg_no_continuation[i]/neg_no_comment[j]）；§4.9 三假全 FAIL ✓。
- layer=L1（仅 subprocess 跑候选 python 文本处理，不启 EDA 二进制）。
