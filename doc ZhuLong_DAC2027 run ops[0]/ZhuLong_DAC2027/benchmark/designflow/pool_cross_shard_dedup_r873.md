# r873 candidate pool cross-shard dedup finding · 2026-11-18

## 发现

r873 选料时发现 **mc-matrix `未动过(可做)=94`（mc≥10）口径仅对 D 台账去重，未做 4-shard 互斥去重**。

按 r549「4-shard 台账互斥」规则，对 `candidates_mc10.tsv` (2664 行) 做 **ALL-shard ledger 去重**（A+B+C+D 共 3644 normalized sessions）后：

| 口径 | mc≥10 fresh |
|---|---|
| D-only dedup（mc-matrix 当前口径） | 94 |
| **ALL-shard dedup（真实可做）** | **9** |

差异 85 条 = 已被 A/B/C 某 shard ledger 占用的 session（D mc-matrix 未排除）。

## 9 条真正 fresh D-dominant (d_ratio≥0.5, mc≥10) 清单

| mc | d | a | b | c | dr | user | ip | session | 处置 |
|---:|--:|--:|--:|--:|---:|---|---|---|---|
| 13 | 64 | 0 | 0 | 4 | 0.94 | e0014566 | 10.129.35.82 | 1791983835884_0pzfe | **dup of r869 TopCellNameQuery-001**（同 user 同 prompt「请返回当前top cell的名称」） |
| 26 | 25530 | 121 | 0 | 1602 | 0.94 | xinpengc | 10.129.33.229 | 1791945700586_w4ghz | 文件可能巨大（d=25530 netlist hits），40min 预算不可解析 |
| 12 | 55 | 0 | 0 | 4 | 0.93 | e0014566 | 10.129.35.82 | 1791983444226_u9tql | **dup of r869 TopCellNameQuery-001**（同 user 同 prompt） |
| 25 | 82 | 0 | 0 | 10 | 0.89 | thomasz | 10.129.33.184 | 1792320716721_4prf6 | 未深读（预算不足） |
| 22 | 480 | 9 | 0 | 51 | 0.89 | e0010438 | 10.129.32.46 | 1794555791754_tjfdb | 未深读 |
| 22 | 16 | 5 | 0 | 8 | 0.55 | m1wang | 10.129.8.122 | 1793792294539_8qf3i | 未深读 |
| 21 | 83 | 0 | 0 | 68 | 0.55 | miccao | 10.129.32.47 | 1793171161917_18qtv | 未深读 |
| 24 | 54 | 0 | 0 | 51 | 0.51 | katief | 10.129.2.13 | 1794483638699_uegln | 未深读 |
| 16 | 5 | 0 | 0 | 5 | 0.50 | yongk1li | 10.129.2.11 | 1793270028637_x6my1 | 未深读 |

## 排除的高 mc 假阳性（keyword 误分类）

`candidates_mc10.tsv` top-by-mc 中 e02141 三 session（kqydq mc=133, m8srw mc=122, 9d0eh mc=88）经 deepread 实为 **Synopsys Sentaurus TCAD** 工艺/器件仿真 deck（`nonlocalpath` / `Electrode` / `File` 块 / `sdevice` / `GAA process`），**非 D 域**（netlist/schematic/waveform/analog）。keyword filter 把 Sentaurus deck 的 netlist-样语法误计为 `netlist:` hits。

## r873 候选处置全清单

| 候选 | user | 处置 | 理由 |
|---|---|---|---|
| bme92 | my7li | deepread → 不可造 | 14.9MB archive 多 chunk + 概念 Q&A 无结构化交付物（详见 `bme92_dqtool_capability_qa.md`） |
| dswuv | e0047722 | cross-shard dup | **A 已 cased WvSineWaveAnalyze-001**（同 user 同 prompt「使用tcl代码，帮我画一个正弦波」），A ledger 2026-11-09 已 park dswuv 为 dup |
| kqydq | e02141 | keyword false-positive | Sentaurus TCAD deck 检查（NonlocalPath / Tunneling / GAA process），非 D 域 |
| m8srw | e02141 | keyword false-positive | 同 e02141 Sentaurus TCAD |
| 9d0eh | e02141 | keyword false-positive | 同 e02141 Sentaurus TCAD |
| 0pzfe | e0014566 | dup | 同 r869 TopCellNameQuery-001 prompt「请返回当前top cell的名称」 |
| u9tql | e0014566 | dup | 同 r869 TopCellNameQuery-001 prompt |
| w4ghz | xinpengc | 推迟 | d=25530 文件可能巨大，40min 预算不可解析 |
| 4prf6/tjfdb/8qf3i/18qtv/uegln/x6my1 | 各 | 推迟 | 9 真实 fresh 中未深读的 6 条，留待下轮 |

## 建议（供 shard A mc-matrix 改进 + 下轮选料）

1. **mc-matrix 改 ALL-shard 去重**：当前 mc-matrix `未动过` 口径仅对 D ledger 去重，虚高 85 条；建议 `trace_ledger.py --shard D mc-matrix` 改为对 4-shard ledger 并集去重，否则「94 fresh」数字误导造题节奏。
2. **Sentaurus TCAD keyword 降噪**：e0211 三 session 占 top-by-mc 3 席但全为 Sentaurus TCAD，建议 D keyword filter 加 Sentaurus 降噪词（`sdevice`/`sprocess`/`Sentaurus`/`TCL deck`/`pdbSet`/`fset`），或 A 接收 Sentaurus TCAD 为 eda_other 域。
3. **下轮选料优先**：4prf6 (thomasz, mc=25, d=82, dr=0.89) 与 tjfdb (e0010438, mc=22, d=480, dr=0.89) 是 9 fresh 中最干净的 D-dominant（d 高、c 低噪声），下轮优先 deepread。
