# r466 — B 域 fresh=15 独立复算 + relabel 恢复路径审计 + 新扫描机会量化

> 轮次：r466（2026-11-13 01:30 loop shard B）
> 目的：① 独立复算 mc-matrix fresh=15（验 mc-matrix 口径，闭合「fresh=15 是真值还是 dedup 假象」）；② 审计是否存在「B-dominant session 被非 B shard 造为 case」的可 relabel 恢复路径；③ 量化 post-1109 新扫描机会。
> 结论：fresh=15 独立复算命中（与 mc-matrix 完全一致）；**relabel 恢复路径不存在**（10 个 B-dominant-in-non-B case 的 B-kw share 全 ≤24% 多为 <15%，系多域 borderline 非 mislabel；强 B-dominant 高 mc session 全在 ledger_B）；新扫描是唯一高杠杆解锁路径，已量化。

## 1. fresh=15 独立复算（cross-shard + main ledger，`_norm_sid` 口径）

复算脚本口径与 `trace_ledger.py mc-matrix` 完全对齐：
- 读 4 shard ledger（`trace_ledger_{A,B,C,D}.tsv`）+ main ledger（`trace_ledger.tsv`），共 **2893 个 norm slug**（与 mc-matrix `touched=2894` 一致，差 1 为表头/空行）。
- summary_1109.tsv 经 shard B keywords 过滤（`hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim`）+ slug 去重（取 max mc）。
- `_norm_sid`：剥路径 + 剥 `.messages.json/.messages.archive.json/.archive.json/.json` 后缀 → 纯 slug。

| 量 | mc-matrix（官方） | 本轮独立复算 |
|:--|--:|--:|
| pool (mc≥10) | 777 | 777 ✓ |
| fresh (cross-shard) | 15 | **15 ✓** |

**闭合点**：r434 报「per-shard dedup 高估 fresh」；本轮用 cross-shard + main ledger + `_norm_sid` 复算得 15，与 mc-matrix 完全一致 ⇒ **fresh=15 是真值，非 dedup 假象**。早先手算得 151/339 系未对 ledger col0 做 `_norm_sid`（col0 混存 bare slug 与 `.messages.json` 全名）导致的 r434 式匹配漏（伪 fresh），已修正。

## 2. relabel 恢复路径审计（B-dominant session 被非 B shard 造为 case？）

方法：pool (mc≥10) 中 B-dominant（B-kw share ≥30% 或 top-3 含 spice-term）且在非 B shard 为 `case`、且不在 ledger_B 的 session。

**结果：10 个，但全 borderline，非 mislabel**：

| slug | mc | user | B-kw share | 非 B shard | dom | case_id |
|:--|--:|:--|--:|:--|:--|:--|
| gb4mi | 87 | thqu | 41/399=10% | D | waveform | SxWaveAvgSum-001 |
| 8sxsc | 80 | wenwenl | 99/1236=8% | D | waveform | Wr2dqEdgeMeas-001 |
| 4j4es | 72 | jinsongl | 14/335=4% | C | physical_verify | ErcSchMarkNetDump-001 |
| a6f6r | 35 | jinsongl | 24/226=11% | D | analog_context | NmosBulkVoltCheck-001 |
| ruk0m | 29 | jinyuli | 17/215=8% | D | waveform | ClkOscStim-001 |
| dsgln | 29 | chengk | 46/331=14% | D | schematic_netlist | IddRegTestFramework-001 |
| i1s8t | 22 | chengk | 16/210=8% | D | analog_context | IddLeakRank-001 |
| eypbp | 18 | joeyl | 19/80=24% | D | waveform | PwlConvert-001 |
| fy1dp | 14 | yifansun | 15/90=17% | D | waveform | PlsInStimGen-001 |
| kb9ob | 11 | junlingw | 11/85=13% | D | schematic_netlist | PwlDecodeStimGen-001 |

- B-kw share 全 ≤24%，多数 <15% ⇒ spice 在这些 session 里是**次要 signal**，top-1 kw 非 spice（netlist/schematic/waveview/drc 等）⇒ D/C 作 waveform/schematic/physical_verify case **可辩护**，非 B 域 mislabel。
- 强 B-dominant 高 mc session（如 vaiob mc=508 B=910/2652=34%、6nte7 mc=102 B=757/1281=59%、13fwy mc=211 B=669/3711=18%）**全在 ledger_B**（case 或 parked），未错配到非 B shard ⇒ r465「6/6 high-mc spice-dominant 全 ledgered」成立。
- **结论**：relabel（把非 B shard 的 B-dominant case 划回 B）**不构成 B 解锁路径**——可 relabel 的 10 条全 borderline（B 次要 signal），relabel 后仍是跨域弱 case，不增真 B-dominant material。**r465「三选一（新扫描 / filter-主导 / 接受饱和）」refine 为仍成立，relabel 排除。**

## 3. 新扫描机会量化（post-1109 daily trace log）

经 eda_flow `.75` `run_commands` 只读核查（session `shardB-r466-scansync`，已 close）：

- `.75:/home/t0002965/log/` 下 `ssh_eda_search_*` 扫描目录**最新仍为 `20261109_224902`**（1109 池），**无 11/10+ 新扫描** ⇒ 1109 池已 4 天 stale。
- 但 daily trace log 持续生成至 11/13，post-1109 累积：

| 日期 | eda_trace log 行数 | 字节 | hspice/spectre/finesim/custom_sim 提及数（B signal 代理） |
|:--|--:|--:|--:|
| 20261110 | 2981 | 493415 | 1346 |
| 20261111 | 2545 | 411646 | 1202 |
| 20261112 | 2880 | 465190 | 1376 |
| 20261113 | 3087 | 493334 | 1524 |
| **合计** | **~11493** | — | **~5448** |

- 11/13 log 头部：`qualifying sessions: 3083`（当日新增 trace-worthy session ~3083）。
- **解读**：4 天 post-1109 累积 ~11.5K 新 qualifying session + ~5.4K B-signal 提及，**但无 ssh_eda_search 扫描把它们落入 summary.tsv** ⇒ 新扫描是比 filter-主导更高杠杆的 B 解锁路径（filter-主导只能从 0 真 B-dominant fresh 里挑 ~0-3；新扫描才有新强 signal）。r465 建议获硬数字支撑。

## 4. 本轮结论与 0-case 依据

- **mc-matrix 证据**（`python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1109.tsv`）：mc≥10 pool=777/touched=762/**fresh=15**（>0，**非池枯竭**，依令 §4）。
- **fresh=15 真值已独立复算闭合**（§1）；r464 已种群级证实 17/17 fresh 全跨域（B-kw ≤8 非 top-3，`r464_B_quality_exhaustion_population.md`）；r465 证 high-mc 真 B material 已 mined-out（6/6 ledgered）。
- **relabel 不解锁**（§2）；**filter-主导预期 ~0-3**（r464）；**新扫描最高杠杆**（§3 量化）。
- P-004 纪律 ⇒ 禁造 mislabel ⇒ **0 case**。无新 park（r464 已 park 最强 8ifjh，剩 14 更弱，种群级已证跨域，不逐条 deepread）。

## 5. 建议（discuss r466 已发）

1. **@A 或用户（新扫描触发，0.3h，最高杠杆）**：post-1109 4 天 ~11.5K 新 session + ~5.4K B-signal 提及未扫入；触发新 `ssh_eda_search_YYYYMMDD` 扫描是 B 复产 case 的首选路径。
2. **@A（B-4 下线仍 pending，0.2h，block 论文 §0）**：本轮实测 4 case（FinesimIgnoreGen/NetlistViewSpiceldSwap/LatchFFNetlistMatch/VsimEnvFileKeep-001）仍在 B.jsonl 275 行，\Ntasks 1189→1179 脚注阻塞。
3. **@A（P-004 board 更新，0.1h）**：补「relabel 排除（10 borderline 全 B-share ≤24% 可辩护）+ 新扫描量化（~11.5K/~5.4K）+ fresh=15 独立复算闭合」。
