# 深读笔记 — sid 1786015275938_i4wto · e0014566/hfeg0plg58 · rscalc vdd/vss 短路诊断

> trace: `scp hfeg0plg58:/home/e0014566/.cline/data/sessions/1786015275938_i4wto/1786015275938_i4wto.messages.json`
> 147 msgs / 719 KB / agent=lead / 74 user · 73 assistant / match_count=298 (264 virtuoso + 25 calibre + 5 cellview + 2 hspice + 2 skill)
> NEW 用户 e0014566（shard C 首次覆盖）。host hfeg0plg58。

## 真实用户意图（A-档 seed，逐字原文，仅掩码 key/token）

- **USER#1 @idx0**：`read the prompt_flow.md and do the job in it.` —— 通用起始令（真实任务在 `/home/e0014566/test_layout_rscalc_flow_7/prompt_flow.md` 内，是一个 rscalc+autovia+powerfill 多 runner + adaptive_tuner 的 layout 流程）。
- **USER#58 @idx113**：`为什么 rscalc 计算失败了，排查下原因` —— **A-档 seed**（提出目标 / 未给根因 / 未给修复）。assistant 在 idx114–146 全程排查。

> USER#58 没有指出根因，也没有给修复方案 → 符合 A-档选轮规则。

## assistant 工具链（idx1–146）

1. read_files `prompt_flow.md`（idx1/3/5，分三段读完）→ 理解 rscalc+autovia+powerfill 流程。
2. read_files `common.config`/`rscalc.config`/`run_autovia_config.il`/`run_powerfill_config.il`/`adaptive_tuner_design.md`/`gen_final_report.py`（idx11）+ 各 runner `SKILL.md`/`adaptive_tuner.py`（idx13）。
3. **USER#58 → 排查 rscalc 失败**：
   - read_files `/rundata/train/AI_Virtuoso/ver/rscalc/e0014566/testpg1/lvnt.log:100-250` + `lvextract/lvnt_dbtext` + `lvextract/info_log.txt`（idx114）→ 看到 `lvnt.log:131 [WARNING] : Short node = 1` + `lvnt_dbtext` 里 vss 标签 y=-2、vdd 标签 y=+2（TX_M1 ATTACH M1）。
   - run_commands cat `lvextract/normalizedNode` + sed `CheckRscalcShort:230-240` + perl -v + strings `0_merge.node`（idx116，shell 转义异常）→ 改用 read_files。
   - read_files `CheckRscalcShort:228-245` + `normalizedNode` + `lvnt_vconnect.txt`（idx118）→ 发现 `CheckRscalcShort` line 236 `if($lvsmainfile =~ /append\s+PIN_LAYER\s+\${met}_pin\s+\"\s+\"/){` 的 `\${met}` 花括号未转义；`lvnt_vconnect.txt` = `vdd\tvdd\tvdd\nvss\tvss`。
   - run_commands 内联 Python 解 GDS（idx120，shell 转义失败）→ editor 写 `diag_short.py`（idx122）→ run（idx124）→ `0_merge.node` strings = `vdd&vss`,`vdd`,`vss` → **短路确认**。
   - run_commands cat `layermap.txt` + grep `lvnt.conf`（idx126）→ 层映射：`"M1" 3 88`、`"M2" 4 91`、`"M3" 5 93`、`"M4" 6 95`、`"M5" 7 103`（GDS 层 / TX 层）。
   - editor 写 `diag_short2.py`（idx130，记录类型分布：105 BOUNDARY、57 TEXT）→ `diag_dump.py`（idx134）→ 修正记录类型码 0x08=BOUNDARY/0x0C=TEXT/0x0D=LAYER/0x10=XY/0x11=ENDEL/0x19=STRING。
   - editor 写 `diag_short3.py`（idx140）→ run（idx142）→ 完整输出：
     - 标签：`vss!`/`vss` 在 TX_M1 y=-8000；`vdd!`/`vdd` 在 TX_M1 y=8000；**4 个 "vdd" 标签错位在 y=-16000（vss 区）** at x=(116000,84000,52000,20000)，出现在 TX_M1..TX_M5 每层（=20 个错位标签）。
     - 边界形状：L316-L320 各 5、TX_M1..TX_M5 各 16；**跨越 y=0**：L318 2 个 (Y=-400,400)、TX_M1..TX_M5 各 4 个 (Y=-18000,2000~) = 共 ~40 个跨 y=0 候选短路形状。
   - run_commands `/usr/bin/perl -v`（5.026003）+ `perl -e 'if($x =~ /\${met}_pin/)'`（**复现致命错误**：`Unescaped left brace in regex is illegal here ... m/\${ <-- HERE met}_pin/`）+ `head -1 rscalc.log`（idx144/145）。
4. **idx146 最终根因报告**：
   - **根因 #1（主因）**：vdd 与 vss 在版图中物理短路。铁证链：`lvnt.log:131 Short node=1` + `0_merge.node` 节点名 `vdd&vss`（`&`=TX_SEPARATOR）+ `rsb.log Shorted net ... net=vdd`（vdd 变单节点网络无电阻可算）+ GDS 40 个 boundary 跨 y=0；物理位置：4 个 "vdd" 标签错位 y=-16000（vss 区深处）经 TX_ATTACH TX_M1→M1 把 vdd 网名附到 vss 区金属；L318 2 小形状穿 y=0；TX_M1~TX_M5 形状从 y=-18000 延伸到 y=2000~18000。
   - **根因 #2（次因）**：`CheckRscalcShort` line 236 `\${met}` 花括号未转义 → Perl 5.26 致命 → 短路自检在执行任何检查前就崩溃，安全网失效；`runrsc` 用 `system()` 调它不因失败终止 → 流程继续到 lvnetextract2/rsbuild。
   - **为什么 ForceShortNet/ForceShortNetALL 无效**：两者处理同一网络内部自短路，vdd-vss 是跨网络短路。
   - **失败链**：CheckRscalcShort 崩溃 → 短路未报 → lvnetextract2 成功但 `Short node=1`(vdd&vss) → rsbuild 失败不建 RSDB_vdd → rsnodeinfo 找不到 RSDB_vdd/vdd.rvn → 无阻值数据。
   - **修复方向**：①修版图（移走 y=-16000 的 4 个 vdd 标签或修跨 y=0 形状）②修 CheckRscalcShort line 236 `\${met}`→`\$\{met\}` ③绕过（只算 vss 或 pwrNets 只含 vss）。

## gold 依赖 → A-disqualified → B-档 synthesized L1-boundary

gold（vdd/vss 物理短路诊断）依赖 live 文件：`/rundata/train/AI_Virtuoso/ver/rscalc/e0014566/testpg1/{lvnt.log,testpg1.gds,lvextract/*}` + `/apps/cad/bin/CheckRscalcShort` 在 hfeg0plg58 上。`.75` 沙盒不可达 hfeg0plg58 的 `/rundata` → **A-disqualified**。→ **B-档 synthesized L1-boundary**：纯离线多产物解析（GDSII 二进制 + log + perl 静态扫），不执行任何 EDA 工具。

## 合成方案（与现有 rscalc case 正交）

- 现有：r12 RsCalcMesh（mesh）、r74 RsCalcFlowOrch（流编排）、r77 RsCalcCkPtAudit（checkpoint 审计）。
- **本案新子主题**：rscalc 失败根因诊断 —— vdd/vss 物理短路检测（GDS 跨 y=0 形状 + 错位电源标签 + 0_merge.node 含 `&` 合并节点）+ CheckRscalcShort perl 未转义花括号 bug 检测。涉及 **GDSII 二进制解析**（shard C 首次）+ perl 正则静态分析 + 多 log 字段抽取，与现有 case 无重叠。
- 资产 A 忠实复刻真实 testpg1 结构（vdd/vss、5 metal、4 错位标签×5 TX 层=20、L318 2 跨 y=0 + TX 各 4=22 跨 y=0、perl bug line 236）。
- 隐藏 B（avdd/avss、6 metal、6 错位×6 层=36、33 跨 y=0、perl bug line 239）/ B2（vcc/gnd 干净：无 `&` 合并、0 错位、0 跨 y=0、perl 已修）/ B3（pvdd/pvss 短路存在但 perl 已修：9 错位、11 跨 y=0、无 perl bug）击穿 always-short / always-bug / 硬编码单一答案。

## 候选筛选记录

- 候选 1（按 mc）：ypzheng 1792570431387_vdqlw mc=335（576 schematic+566 netlist+65 hspice）→ schematic/sim 域，非 shard C，跳过。
- 候选 2：xinqiaoz 1789895888597_x1ulx mc=330（440 calibre）→ physical_verify，但 xinqiaoz 已多次用（r81），且本 shard 想补 layout_virtuoso（16 case，欠代表）。
- 候选 3：e0014566 1786015275938_i4wto mc=298（264 virtuoso+25 calibre）→ **layout_virtuoso + NEW 用户 + rscalc 短路诊断新子主题** → 选定。
- jason17w 1791944224191_6i6lk mc=328（1470 netlist+1 virtuoso）→ netlist 域，跳过。

## 12-assertion spec → 14 条断言（k=14=k_check≥8 GATE PASS）

①[a] zip 恰 1 个 diag_rscalc_short.py + py_compile + UTF-8 无 NUL
②[b] 跑 B exit0 + stdout 合法 JSON + 顶层键齐全
③[c] B short_confirmed == oracle（0_merge.node 含 `&`）
④[d] B merged_node == oracle（精确合并节点串）
⑤[e] B lvnt_short_warning == oracle（lvnt.log Short node=N≥1）
⑥[f] B rsbuild_error_net == oracle（rsb.log net=X）
⑦[g] B rsnodeinfo_missing_rvn == oracle（RSDB_X/X.rvn）
⑧[h] B misplaced_labels 计数 == oracle + 每条含 x/y/layer
⑨[i] B crossing_shapes_count == oracle（GDS 跨 y=0 形状数）
⑩[j] B perl_bug.detected/line/unescaped_brace == oracle
⑪[k] B2（干净）short_false + misplaced 0 + crossing 0 + perl_bug false + root_cause none
⑫[l] B3（短路+perl 修）short_true + misplaced>0 + crossing>0 + perl_bug false + secondary none
⑬[m] A↔B 结构 guard：错位计数不同 + merged_node 不同 + A 上跑通 → 击穿 fake_print_expected
⑭[n] 确定性：B 跑 3 次 md5 一致
