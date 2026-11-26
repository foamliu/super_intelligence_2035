# r464 · B 域 1109 池 fresh 全种群 kw 扫描 + 8ifjh deepread

> 承 r463（4 deepread 全跨域）→ 本轮把 **17 个 truly-fresh B-containing 候选**做**全种群 kw-profile 扫描**（非抽样），并 deepread B-signal 最强的 8ifjh（hspice:8，本批最高 B-kw 计数）。

## 1. 全种群 kw 扫描（17 truly-fresh，非抽样）

口径：`candidates_mc10_classified.tsv` domain 含 B 的 22 条 − r462 case(zm0zw) − r463 parked(tvc27/721uj/lvack/xtqpe) = **17 truly-fresh**。逐条判 B-keyword 是否主导（top-3 kw 含 spice-term 且 B-kw 占比 ≥30% 为 B-dominant；对照 r462 真 B case zm0zw kw=`analog:1007` 主导）。

| slug | mc | top-1 kw (count) | B-kw max | 判定 |
|:--|--:|:--|--:|:--|
| 5laiw | 79 | drc:94 | hspice:2 | C physical_verify (DRC) |
| xbtsx | 77 | drc:92 | hspice:2 | C physical_verify (DRC) |
| x2l1c | 39 | drc:50 | hspice:3 | C physical_verify (DRC/cmos) |
| 9xlnc | 31 | pyaether:184 | hspice:5 | A eda_other (pyaether) |
| zy2q7 | 29 | netlist:237 | hspice:5 | D schematic_netlist |
| 4u64s | 27 | aether:74 | hspice:3 | A/C layout_aether |
| u4vj2 | 26 | netlist:92 | hspice:2 | D schematic_netlist |
| xusb9 | 25 | drc:65 | hspice:2 | C physical_verify (DRC) |
| 8exxf | 24 | aether:133 | hspice:4 | A/C layout_aether |
| mtvpv | 24 | drc:51 | hspice:2 | C physical_verify (DRC) |
| fct93 | 24 | netlist:152 | hspice:5 | D schematic_netlist |
| bse5r | 24 | netlist:125 | hspice:1 | D schematic_netlist |
| **8ifjh** | 18 | netlist:82 | **hspice:8** | **D schematic_netlist**（本批 B-kw 最高，deepread 见 §2） |
| 1k7pk | 15 | aether:442 | hspice:7 | A/C layout_aether |
| ed6ve | 12 | drc:252 | hspice:2 | C physical_verify (DRC) |
| opiso | 12 | synopsys:26 | hspice:4 | A digital/verification |
| xliaq | 10 | virtuoso:21 | spectre:1 | C layout_virtuoso |

**结果：17/17 非 B-dominant**。B-kw 最大值 = 8ifjh hspice:8（占 total kw 18 中的 8 = 44%？但 netlist:82 是 top-1，hspice 非 top-3；按 top-3 主导判据仍非 B）。无一条有 zm0zw `analog:1007` 式 B-spice 主导 profile。0 B-only（22 全 multi-shard：16 A+B+C+D / 3 A+B+C / 3 B+C+D）。

## 2. 8ifjh deepread（B-signal 最强，hspice:8）

- session: `1783660701986_8ifjh` (e0025730 @ hfeg0plg49/10.129.8.86), 35 msgs, mc=18
- **user 首句**：`<user_input mode="act">启动业务场景: 版图规划</user_input>`（Layout Planning）
- agent 探索 `/home/e0025730/lvlshft/` 项目 + `.cline/skills/lvlshft/SKILL.md` + `sense-margin` skill，读 `.empyrean/aether.rc`/`window.rc`/aether logs，`search_codebase` lvlshft/版图规/layout.plan
- **deliverable**：版图规划（layout planning）场景驱动，agent 全程读 layout/skill/aether config，**0 SPICE sim invoke（无 .TRAN/.MEAS/.alter/sim run）**
- kw `netlist:82;schematic:23;hspice:8` — netlist/schematic 主导（netlist parse/transform = D schematic_netlist 或 C layout），hspice:8 来自 netlist/schematic 文件内 mention（非 sim drive）
- **判定**：D schematic_netlist / C layout，**非 B spice_sim/characterization**（不满足 r461 drive-sim 判据）

## 3. 累计 deepread 跨域统计（r462-r464）

| 轮 | slug | mc | deepread 结论 | 域 |
|:--|:--|--:|:--|:--|
| r463 | tvc27 | 88 | DRC/LVS kw 主导 | C |
| r463 | 721uj | 58 | Calibre LVS rule-file difflib 对比 | C |
| r463 | lvack | 10 | HSPICE fail/pass FSDB 波形对比 wavecompare | D waveform |
| r463 | xtqpe | 18 | Cline workspace/工作目录配置 Q&A | A eda_other |
| r464 | 8ifjh | 18 | 启动业务场景版图规划(lvlshft/sense-margin) | D/C layout |

**5/5 deepread 全跨域**，与 17/17 kw-population 扫描一致（0 假阴性——kw 非 B-dominant 的，deepread 也非 B）。

## 4. 结论

B 域 1109 池 mc≥10 fresh=15（>0，**非池枯竭**，依 2026-11-11 令 §4 不下池枯竭结论），但 **17/17 fresh 候选 kw 非 B-dominant + 5/5 deepread 跨域 = 质量枯竭**（quality-exhausted not quantity-exhausted，同 shard A threshold_eval）。根因 = B keyword filter「出现即入池」非「主导」（r463 已立论，本轮升种群级证实）。修法须前移到 filter（@A 裁定），不建议降 mc<10（同 shard A finding mc≥5 wrong-shard 主导）。本轮 0 case（P-004 纪律禁造 mislabel case），8ifjh parked，fresh 16→15。
