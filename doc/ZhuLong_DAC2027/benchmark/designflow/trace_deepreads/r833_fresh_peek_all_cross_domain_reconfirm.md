# r833 选料轮 — fresh peek 全跨域再确认（A-pure 枯竭续证）

**日期**: 2026-11-20  **shard**: A  **轮次**: r833  **类型**: 0-case 选料轮

## 背景

r832 完成 11-15 用户令的意图审计 + 候选池重审（26 题全 keep，pool 无新增误杀可复活）。
本轮按任务卡做 1 条 case：`trace_ledger next` → 深读 → 合成。

## 选料过程

`trace_ledger.py --shard A next --n 8` 给出 fresh peek（不在 4-shard 台账并集 3953 条里的 sid）。
扫描源 `summary_stats.json.scan_path` = `ssh_eda_search_20261119_172105/summary.tsv`（11-19 21:37 落盘，44935 行 / 5694 dedup mc≥1）。

在 .75 上 awk 取 peek 候选的 mc/user/host/keywords：

| sid | mc | user | host(首) | dominant keywords | 判域 |
|---|---|---|---|---|---|
| nrep6 | 228 | thqu | hfeg0plg96 | netlist:1096 mosfet:68 pyaether:55 schematic:53 cmos:52 | **D** schematic_netlist |
| 7l4sx | 171 | e0017906 | hfeg0plg96 | cellview:301 aether:217 drc:206 netlist:133 lvs:56 | **C** layout/physical_verify |
| v593e | 82 | t0002614 | hfeg0pkn004 | aether:346 netlist:295 schematic:114 mixed-signal:51 verilog:41 | **C/D** aether/netlist 主导 |
| ibwba | 48 | zhililu | hfhds219 | netlist:604 spectre:210 maestro:202 virtuoso:190 pex:106 | **B** spice/characterization |
| frxg5 | 54 | hswang | hfhds211 | netlist:179 verilog:115 drc:81 synopsys:16 hspice:12 | 表面 A-plausible → 实际 **B** |
| jr0o3 | 44 | ronghu | (多 host) | netlist:90 transistor:36 .cdl:33 lvs:27 schematic:21 | **C** lvs/netlist |
| hasla | 41 | zqzhan | (多 host) | drc:2662 netlist:2246 analog:24 hspice:17 verilog:6 | **C** drc/netlist 绝对主导 |
| kubzy | 29 | tzhi... | (多 host) | netlist:178 aether:167 schematic:83 lvs:31 pex:20 floorplan:10 | **C** layout_aether |
| f1pj5 | 27 | jingc | (多 host) | aether:144 mixed-signal:18 floorplan:18 pyaether:16 | **C** layout_aether |
| 1e0xa | 23 | sagequan | (多 host) | analog:30 calibre:16 hspice:15 rtl:10 aether:7 | **C/B** analog/calibre |
| mk098 | 21 | yazhuok | (多 host) | schematic:414 netlist:103 hspice:72 mosfet:22 | **D/B** schematic/spice |

## frxg5 深读（唯一 A-plausible 表象候选）

- **liveness**: flat-path NOFILE，subdir `sessions/1791787377751_frxg5/` ALIVE（path-bug revival 第 N 例，r528 矿脉已关后仍偶现）
  - `1791787377751_frxg5.messages.json` 249305 B / 16 msgs / agent=lead，mtime Oct 12
- **首用户意图（原话）**:
  > 我现在的工作目录是 /proj/drcoa/V0/simdir/finesim/drcoaF/RunFile/Vcap/Aging_Sim，帮我查看该目录下的 matrixrun_aging 脚本，并分析关于 aging 部分的代码
- **真域判定**: **finesim aging 仿真脚本分析** → spice_sim / characterization = **B 域**
  - scan kw verilog:115 + synopsys:16 把它推进 A 候选池，但真实意图是 finesim（SPICE）aging 分析，verilog/synopsys 命中是脚本里的边角关键词噪声
  - 第 N 次复证 MEMORY 反复结论：scan keyword 域判定不可靠，必读首用户意图 + assistant 工具链
- **类型**: analysis-Q&A（脚本分析，11-15 reaudit 后合法类型），但 B 域 → defer to shard B
- **判分可行性**: 单脚本 aging 部分分析，ground-truth 需脚本原件；B 线若认领可造（toothy check 需脚本结构断言），非 A 任务

## 结论

**fresh peek top-11 全跨域（B/C/D），无 A-pure 可造料**。

- A-pure 枯竭本轮再确认（r760/r761 首证 → r824 mc≥8 终证 → r826 r528 revival 矿脉关 → r831 mc5-9 续证 → r832 审计 → r833 fresh peek 全跨域再证）
- 守任务初衷第 1 条（任务形态=用户意图）+ shard 纪律（只做 A 域）：不为凑 1-case 把 B/C/D 意图强造进 A
- 守 §4.3/§4.6 硬闸门：不造无牙判分 / weak case
- 跨域候选不在 A 台账 claim（避免 4-shard 互斥锁死 B/C/D），留各真域 shard 自取

## 未 claim 候选（供 B/C/D 参考，不在 A 台账）

- **B 可取**: frxg5(hswang mc54 finesim aging 分析) / ibwba(zhililu mc48 spectre/maestro/pex) / 1e0xa(sagequan mc23 analog/hspice) / mk098(yazhuok mc21 schematic/hspice)
- **C 可取**: 7l4sx(e0017906 mc171 cellview/drc/lvs 高 mc) / jr0o3(ronghu mc44 lvs/netlist) / hasla(zqzhan mc41 drc:2662/netlist:2246 极高 mc) / kubzy(mc29 aether/lvs/pex) / f1pj5(jingc mc27 aether/floorplan)
- **D 可取**: nrep6(thqu mc228 netlist:1096 高 mc) / v593e(t0002614 mc82 netlist/schematic)

## 产出

- A.jsonl 不变（415）
- cases/A 不变
- 台账 A 不变（未 claim 跨域候选）
- 本 deepread 笔记
- MEMORY_A r833 一行 + daily_A 追加

## DEBT

- (a) 接受 A-pure 枯竭，产能转 governance/audit/waveview 协作
- (b) 运维可考虑开新全量扫描扩池（11-19 扫描已 28h+），或 mc 阈值再探
- (c) discuss r834 due（r830+4，本轮不欠）
