# Deepread: dasvf (junlingw@hfeg0pkn005) — partial, r1087 stop-loss

**trace_source**: user=junlingw, host=hfeg0pkn005(10.129.2.14), session=1795154851675_dasvf, mc=200
**domain**: schematic_netlist (d326 netlist/schematic, sim74)
**file**: .75:/home/junlingw/.cline/data/sessions/1795154851675_dasvf/1795154851675_dasvf.messages.json
**size**: 2.59MB, 6 msgs (netlist-heavy, large tool_result blobs — likely full SPICE netlists)
**ledger status**: claimed r1087 (next round: deepread + synthesize)

## r1087 关键发现（增益，下轮起生效）
1. **trace 文件在 .75 本地 /home/<user>/.cline/data/sessions/<slug>/<slug>.messages.json**，直接可读（无需 ssh 698 台机）。
   - 旧认知：需 ssh 到扫描记录的 host 取文件 → 错。扫描记录的 host（10.129.2.x 等）上这些文件不在 `sessions/<slug>.messages.json` 路径。
   - 正确路径：`/home/<user>/.cline/data/sessions/<slug>/` 是**目录**，内含 `<slug>.messages.json` + `<slug>.json`。
   - .75(hfhds201=10.129.32.75) 的 /home 有全部用户（adaml/adminai/.../junlingw/...），直接 `cat /home/<user>/.cline/data/sessions/<slug>/<slug>.messages.json` 即可。
2. **eda_flow open_session 可用**（r1085 已确认，r1087 复确认）：workdir=/proj/.../shardD_20261122-r1087_D-r1087-scan_0
3. summary.tsv 列数=6（data rows 缺 tools 列，header 7 列），脚本过滤须用 `len(p)<6` 非 `<7`。

## 候选池（mc5-200, D-pure, fresh on .75）
- dasvf (junlingw mc200 d326/sim74) — claimed r1087, 下轮合成
- 7q6sq (junlingw mc200 d326/sim74) — 同用户近邻 session，待查是否 dup
- nxmto (pdsong mc197 d324/sim13) — fresh, 下轮候选
- 1mmir (junxu mc297 d830/sim43) — fresh, junxu 已有 r1068 ogspt deepread
- xotrf (cliu mc276 d858/sim0) — fresh, D-pure 最强(d858/sim0)
- dhgd8 (jmgu mc275 d20/sim0) — fresh, d_sum 偏低

## 下轮计划
1. 深读 dasvf（2.59MB/6msgs，需解析大 tool_result）→ 合成 L1/L2 case
2. 若 dasvf 不适合，转 nxmto 或 xotrf（均为 .75 本地可读）
