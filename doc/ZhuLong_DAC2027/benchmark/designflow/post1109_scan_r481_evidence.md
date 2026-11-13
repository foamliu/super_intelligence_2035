# post-1109 daily-log 扫描证据 · r481 · 2026-11-13 09:1x

## 扫描口径
- 源：.75 `/home/t0002965/log/eda_trace_2026111{0,1,2,3}.log`（11-10~11-13，4 文件）
- B-marker grep: `hspice|finesim|siliconsmart|spectre|ngspice|simulator|spice|custom_sim`
- 5448 B-marker 行 → 1216 unique slug（NFS 同 home 多 IP 去重）→ 去重 1109 summary.tsv 3964 slug 后 **200 真新 slug** → mc≥10 共 **183**

## 4-shard ledger + main jsonl 去重
- ledgered base slugs: 2735（4 shard ledger 2732 + main jsonl 1171 trace_source，去重 2735；四式 suffix 归一 .messages.json/.messages.archive.json/.json/.jsonl + bare slug）
- ledgered 集合文件：`_ledgered_base_slugs_r481.txt`（本地）

## peek 3 个 fresh unledgered 候选
| slug | user | host | mc | keywords | peek 结论 | 处置 |
|---|---|---|---|---|---|---|
| 1794459781454_dgo3h | zhenglu | hfeg0pkn001(10.129.2.10) | 355 | pure hspice kw | **非 B mislabel**：PDK HL_hspice 模型库目录梳理 + localmc 解释 + 拒绝解密 .enc + 写 example_nrvt_dc.sp 使用指南；0 run_approved_command，hspice:355 全来自 read .lib 文件 | **parked**（同 r480 dyu61 型） |
| 1794448818017_fppmi | witterfu | hfeg0pkn005(10.129.2.14) | 372 | hspice:128 netlist:45 schematic:45 | **真 B**：检查 rj/psij jitter 仿真 deck 一致性（run 脚本 .sp 引用 / drate-vs-filename / corner 名），FineSim/HSpice 工作流真环节，56 msgs 546KB | **claimed** 下轮造题（DEBT:1） |
| 1794488730591_9lfys | e0024852 | hfeg0pkn003(10.129.2.12) | 205 | schematic:142 netlist:121 hspice:121 calibre:14 | 未 peek（留下轮） | defer |

## filter 过匹配率
- 3 peek 中 1 真 B = 33%；与 r464-r480 累计 13 peek 1 真 B（7.7%）同量级
- 根因：`hspice` keyword 命中所有「读 .lib/.sp 文件」的 PDK/layout/verification session，不只 spice-sim
- 建议：B-marker 加 spice-tool 密度门槛（≥35% 且绝对计数≥10）+ 正向信号（run_approved_command / editor-write-.sp）

## mc-matrix 证据（mc≥10 强制条款）
`python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1109.tsv`：
mc10 pool=777 / touched=777 / **fresh=0**（src=summary_1109.tsv，1109 池已切 r462）

## 结论
- 1109 池 mc≥10 B fresh=0（结构性 mined-out，r463-r480 多轮确认）
- post-1109 daily log 有 183 新 mc≥10 B-marker 候选，但 filter 过匹配 67-92%
- fppmi 是 post-1109 首个真 B 候选（claimed，下轮合成 case）
- 非池枯竭：unlock 路径 = post-snapshot daily-log 靶向扫描 + peek（r470/r479/r481 三轮实证有效）
