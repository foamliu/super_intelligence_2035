# r468 B · 换池后首次实测：1109 fresh=15 全跨域，r465/r466「新扫描解锁 B」假设证伪

**日期**：2026-11-13 02:1x · **shard**：B · **触发**：loop task card 派 1 case；顶部 11-12 换池令已完成(r462) ⇒ 回落造题；mc-matrix fresh=15 但需验证域纯度。

## §0 换池落地确认（11-12 令验收）

`designflow/summary_stats.json` 实读：
- `mc_matrix.src` = `designflow/summary_1109.tsv` ✓（已切）
- `pool_switch.done_at` = `2026-11-12T23:44+08:00`，`pool_switch.by` = `shard B`
- `mc10_fresh_B_new_1109` = 22（直接目标达成：1105 fresh(B)=0 → 1109=22）
- `scan_sha256` = `a3a374ad5bcaa79f1b82ceeb3ab560e8a703450640b8ad4c11fc6fbb0bec3c07`
- 产物齐备：`summary_1109.tsv`（763376B/3964 行）、`mc_matrix_1109_{A,B,C,D,ALL}.txt`、`candidates_mc10.tsv`（777 行）、`summary_1109_build.log`、`_scan_1109_raw.tsv`

⇒ **11-12 换池令已完成**，本轮不再做换池运维，回落正常造题。

## §1 mc-matrix 实跑（本轮）

```
python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1109.tsv --json
```
- mc≥10 pool=777 / touched=762 / **fresh=15**（与 r466/r467 一致，非池枯竭，依令 §4）
- mc≥5 fresh=42 / mc≥15 fresh=12 / mc≥20 fresh=11 / mc≥30 fresh=4

## §2 fresh=15 独立复算 + B-share 逐条量化（本轮新增）

口径：cross-shard（4 shard ledger + main `trace_ledger.tsv`）+ `_norm_sid`（剥 `.messages.archive/.messages.json/.json` 后缀）。
- ledger 排除 sid 集合：main 1373 + A 440 + B 1358 + C 712 + D 1554 → unique 2950
- candidates_mc10.tsv 777 行 → fresh（not in 2950）= **15**（与 mc-matrix 一致）

B-kw = {hspice, finesim, siliconsmart, spectre, ngspice, simulator, spice, custom_sim}；B-share = sum(B-kw count) / sum(all kw count)。

**15 fresh 全部 B-share ≤6%**：

| mc | B% | session | user | top-3 kw |
|--:|--:|--|--|--|
| 12 | 6% | 1792042227278_opiso | e0040594 | synopsys:26/verilog:8/drc:8 |
| 25 | 3% | 1792215350755_xusb9 | colinxu | drc:65/aether:7/pyaether:5 |
| 24 | 3% | 1792573529929_8exxf | zhukaic | aether:133/netlist:6/hspice:4 |
| 24 | 2% | 1783666402453_fct93 | e0025730 | netlist:152/schematic:57/analog:7 |
| 24 | 2% | 178763792290_mtvpv | e0025730 | drc:51/netlist:38/lib.defs:2 |
| 39 | 2% | 1789462115306_x2l1c | yongk1li | drc:50/cmos:46/netlist:18 |
| 27 | 2% | 1793238915568_4u64s | e0040367 | aether:74/pyaether:36/skipper:15 |
| 29 | 2% | 1782871301636_zy2q7 | e0025730 | netlist:237/schematic:75/analog:8 |
| 31 | 1% | 1794190541511_9xlnc | steveny | pyaether:184/waveview:60/verilog:38 |
| 10 | 1% | 1793085517442_xliaq | colinxu | virtuoso:21/cellview:19/pyaether:14 |
| 77 | 1% | 1789710184698_xbtsx | yongk1li | drc:92/netlist:25/lvs:16 |
| 79 | 1% | 1789717846934_5laiw | yongk1li | drc:94/netlist:25/lvs:16 |
| 15 | 1% | 1792481875871_1k7pk | zhukaic | aether:442/netlist:106/hspice:7 |
| 12 | 1% | 1794224136412_ed6ve | e0043936 | drc:252/netlist:44/waveview:8 |
| 24 | 0% | 1783316151876_bse5r | e0025730 | netlist:125/schematic:74/rtl:15 |

**0 条 B-dominant**（无一条 top-1 kw 为 spice-term；最高 B-share 仅 6%）。

## §3 touched 段高 B-share 不对称对照

touched（已 ledger）段含大量高 B-share session，全部已 case/seeded/parked：
- ebmf3(chapinc, mc97) hspice:406 → B-share **90.7%**
- k1vy6(hauserz, mc131) spectre:223 → B-share **86.1%**
- vdeyi(e0025768, mc65) hspice:361 → B-share **85.7%**
- zd8iu(shanliny, mc54) hspice:461 → B-share **91.1%**
- zju83(yh1yang, mc24) hspice:63 → B-share **94.0%**
- yg26n(shanliny, mc26) hspice:52 → B-share **98.1%**

fresh 段 B-share ≤6% vs touched 段 B-share 可达 90%+ 的**强不对称** ⇒ B-keyword 过滤池里真 B-dominant session 已被前 418 case + 940 parked 挖完，剩下的 fresh 是 keyword 过滤误纳的跨域 session。**非 dedup 假象**（r466 已闭合），是 keyword-filter 池在 B-dominant 子集上的真枯竭。

## §4 结论：r465/r466「新扫描解锁 B」假设被 1109 数据证伪

- r465「三选一」第 1 项 = 新扫描；r466 量化「~11.5K 新 session + ~5.4K B-signal 已积累未扫入」⇒ 新扫描是 B 解锁首选路径。
- **但 1109 池已在 r462 切换落地**——这就是一次「新扫描」（相对 1105）。结果：fresh 0→15 涨了，**域纯度没涨**（0 B-dominant）。
- ⇒ 「新扫描解锁」假设**证伪**：问题不是 scan 太旧，是 scan 的 keyword 提取 + shard-B 过滤 pipeline 不再能从新增 session surface B-dominant 材料。spice 仿真器关键词命中的新 session 多是 netlist/schematic 上下文顺带提 spice，非 spice 仿真任务。
- **unlock 重定向**：scan-freshness → keyword/filter-pipeline
  - (a) 收紧 shard-B 过滤为「spice-term top-1 或 share≥30%」而非「$6 含任意 spice-term 即纳入」
  - (b) 扩 scan keyword 词表抓 SiliconSmart/custom_sim（r467 char 盲点）
  - (c) 或接受 spice-sim interactive cline session 在 698 机 corpus 已饱和

## §5 对论文影响（建议，不越权改）

- 论文若声称 spice_sim / characterization 域覆盖，§5 Threats 须注明「域内 case 经 keyword 过滤获取，filter 在高 mc 段对 B-dominant session 已饱和（1109 池 fresh B-share ≤6%），低 fresh 增量多为跨域误纳」。
- 与 r467 characterization scan 词汇盲点合并：B 域两子域覆盖边界 = spice 滤池饱和 + char 工具词盲点，均为 cline-trace-based benchmark 的结构性覆盖限制。

## §6 本轮裁决

- **0 case**：mc10.fresh=15>0（非池枯竭，依令 §4）但 15/15 全跨域 B-share≤6%，P-004 禁造 mislabel ⇒ 0 case。
- **discuss r468**：P-004 @B OPEN ⇒ 当轮必须表态；新证据 = 换池后首次实测 + unlock 机制重定向。
- **DEBT: 0**。
