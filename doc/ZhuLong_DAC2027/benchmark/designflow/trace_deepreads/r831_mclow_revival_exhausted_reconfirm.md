# r831 — mc5-9 A-pure revival 矿脉枯竭再确认（11-19 新扫描证据）

日期：2026-11-20 05:0x（shard A，0-case 治理轮）
扫描源：`ssh_eda_search_20261119_172105/summary.tsv`（44935 行 / 5694 dedup mc≥1 / mc10=3997 / mc5=4417 / 692 hosts）

## 目的
r826 曾用 11-13 扫描判「r528 A-pure revival 矿脉采样至枯竭」。本轮用 **11-19 新扫描** + subdir-path liveness 复测，验证结论是否仍成立。同时回应 2026-11-15 用户令「mc≥5 扩池」的止损判据：mc≥5 候选里有没有能忠实还原用户意图、且能写出可判分 check() 的任务。

## 一、fresh 高 mc A-pure 池（mc≥10，shard A 关键词）
`awk ... $6 ~ /verdi|vcs|innovus|primetime|.../` 按 mc 降序取 top-8，全 shard 台账查重：

| session | mc | user@host | keywords 摘要 | 台账状态 |
|---|---|---|---|---|
| ukkn7 | 1627 | e0031668 | aether/virtuoso/drc/netlist | **case** Verification-001 (seeded) |
| w4x70 | 1575 | haoyut | verilog/netlist/cmos | **case** SpefAnnotAudit-001 |
| x4b0p | 1508 | xinqiaoz | drc/calibre/pdk | **case** CalVcoEnvWorkaround-001 (r570 revived) |
| aneeo | 1348 | e0014566 | drc/virtuoso/gds | parked (4.5MB/1605msgs too large, layout C) |
| m2vah | 1082 | e0014566 | virtuoso/drc/gds | **case** RsCalcAutoVia-001 (char B) |
| aftvk | 1034 | jieran | pyaether/lvs/drc | parked (layout shardC) |
| 9knot | 986 | vincelu | verilog/cmos/netlist/lvs/hspice | parked (char C, SiliconSmart) |
| 20fct | 974 | miccao | skipper/lvs/calibre | parked (r785 REJECT trace-end-gold 未满足) |

**结论**：fresh 高 mc A-pure 全部已入台账（case 或 parked 有理由），无未 claimed 可造料。与 r760/r761/r826 一致。

## 二、mc5-9 A-pure revival 候选 subdir-path liveness 复测
r820 发现：r528「file-deleted」是假阴性——文件在 `sessions/<sid>/<sid>.messages.json` 子目录。本轮抽查 3 条 r794-ALIVE 但未深读的候选：

| session | user@host | flat | subdir | size | msgs | agent | 深读判定 |
|---|---|---|---|---|---|---|---|
| n907k | meng1l@10.129.2.13 | NOFILE | **ALIVE** | 17.8KB | 3 | lead | U#0=Verilog FullChip 模块例化粘贴（DDR CK_t/CK_c/CS/CA ifdef PROJECTNAME 连线），无明确指令，意图模糊。thin → weak |
| vqefw | e0029495@10.129.2.10 | NOFILE | **ALIVE** | 14.2KB | 6 | lead | U#0=「siliconsmart你知道userguide在哪」=doc-search Q&A。11-15 reaudit doc-search 已合法，但单路径答案难写出 toothy self-contained check + hidden-B 反硬编。weak |
| c41bm | e0041392@10.129.2.12 | NOFILE | **ALIVE** | 305.7KB | 6 | lead | 6 msgs 大内容但交互轮次太薄，非 substantive 多轮任务。weak |

**subdir-path revival 矿脉第 N 次复证 ALIVE**（path-bug 非 true 枯竭），但**实质性 case 料已耗尽**：r828 s59t7(ZtypeWave)/r829 dqi7d(SentaurusTcad) 是最后两条 substantive 料；剩余 ALIVE 候选要么交互太薄（3-6 msgs）、要么意图模糊/非 EDA/单路径 doc-search 难判分。

## 三、结论
- **fresh mc≥10 A-pure**：枯竭（11-19 扫描再确认，top-8 全入台账）。
- **mc5-9 A-pure revival**：subdir-ALIVE 仍多（path-bug 假阴性），但**可造 substantive 料耗尽**——剩余候选 thin/weak/难判分。
- **2026-11-15 mc≥5 扩池止损判据**：mc≥5 候选里「能忠实还原用户意图 + 能写出可判分 check()」的料，在本轮抽样中未发现新料（最后两条已在 r828/r829 落库）。
- 不强行造 weak case（守任务初衷：不为凑数造非真实意图/无牙判分的题；守 §4.3/§4.6 硬闸门：incomplete 不进 jsonl）。

## 四、处置
- 3 候选 ledger parked note --force 更新（subdir-ALIVE + weak 理由，防他 shard 重捡）。
- 本轮 0 case，governance 轮。
- 下轮方向建议：① 接受 A-pure 枯竭，转纯 governance/audit/waveview 协作 ② 若运维开新全量扫描扩池再探 ③ phantom-revival bug 模式 code-fix（build_jsonl.py source-missing guard，r828/r916 两例）。
