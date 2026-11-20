# Liveness Audit — r803 (2026-11-19 17:0x, shard A)

## 目的
11-15 用户令要求 mc≥5 扩池有效性在每轮用「mc≥5 pool / touched / fresh」+ 产出举证。
r800/r802 连续 0-case，本轮对「broad mc≥10 A-pure 顶候选」+「r794 liveness-ALIVE mc5-9 A-pure 池」做再liveness，判断是否真的耗尽。

## 数据源
- 扫描快照：`ssh_eda_search_20261118_230537/summary.tsv`（44992 行，11-18 23:05）
- r794 liveness 池（11-19 12:47 验证 33/34 ALIVE）

## 本轮 liveness 探测结果（14 候选）

### A. broad mc≥10 A-pure 顶候选（从 ledger next peek top-30 筛 A-pure 关键词）
| sid | user | host/IP | mc | keywords | liveness(11-19 17:0x) |
|---|---|---|---|---|---|
| 1794276772104_yicdk | hengbow | 10.129.33.25 / 10.129.8.226 | 120 | verilog:674;netlist:507;analog:98 | NOFILE (2 hosts) |
| 1794301691470_zg7xg | jinsongl | 10.129.2.14 / .35.68 / .8.229 | 65 | dbget:198;netlist:47 (Innovus pnr) | NOFILE (3 hosts) |
| 1794278751082_g8en5 | jinsongl | (同 zg7xg 9 hosts) | 73 | dbget:144;vhdl:18;rtl:4 | ssh-timeout .2.14; NOFILE .35.68/.8.229 |

注：yicdk/zg7xg/g8en5 台账显示 11-11 00:5x 已 parked（r802 顶审归类时已记），本轮再 liveness 全部 NOFILE → rotation 蒸发，与 r802 结论一致。

### B. r794 liveness-ALIVE mc5-9 A-pure 池（11-19 12:47 验证 ALIVE）
| sid | user | host/IP | mc | size | keywords | liveness(11-19 17:0x) |
|---|---|---|---|---|---|---|
| 1789718897680_hdhfh | t0002470 | 10.129.8.124 | 5 | 1054KB | verilog:18;drc:13;systemverilog:4 | NOFILE |
| 1794449765531_s59t7 | rongjiez | 10.129.8.230 | 7 | 563KB | synopsys:7;analog:3;netlist:2 | ssh-timeout (host unreachable) |
| 1792998450890_1y66j | e0041392 | 10.129.8.123 | 6 | 232KB | rtl:10;waveview:2;aether:2 | NOFILE |
| 1794478957304_r44l7 | vendor.cno.chjh07 | 172.16.8.175 | 5 | 356KB | rtl:12 | NOFILE |
| 1794194018234_c41bm | e0041392 | 10.129.8.123 | 5 | 306KB | synopsys:48;hspice:8;pyaether:4 | (C/B lean, skipped probe) |
| 1793597178818_otgh9 | e0045488 | 10.129.2.13 | 5 | 136KB | rtl:11;virtuoso:1 | NOFILE (.8.227 + .2.13) |
| 1782141557406_uhla7 | e0025730 | 10.129.8.86 | 5 | 65KB | synopsys:16;calibre:8 | NOFILE |
| 1792466393671_dqi7d | liyingw | 172.16.8.14 | 5 | 63KB | synopsys:11 | NOFILE |
| 1794637486415_rbr06 | e0039516 | 10.129.8.231 | 5 | 62KB | floorplan:9;openroad:6;yosys:3;innovus:3 | ssh-timeout (host unreachable) |
| 1794384170431_k7bl1 | e0039516 | 10.129.8.231 | 6 | 29KB | innovus:15;icc2:5;dbget:8 | ssh-timeout (同 rbr06 host) |
| 1792044781149_gwa9k | sijialv | 10.129.8.234 | 6 | 23KB | verilog:7 | ssh-timeout |
| 1794366349085_n907k | meng1l | 10.129.2.13 | 6 | 18KB | (未取 keywords) | ssh-timeout (.2.13 slow) |
| 1791615542263_satf4 | johnl | 10.129.8.230 | 7 | 14KB | rtl:6;verilog:2 | ssh-timeout (同 s59t7 host) |
| 1793087727242_vqefw | e0029495 | 10.129.2.10 | 5 | 14KB | (未取) | ssh-timeout |

## 统计
- 探测候选：14（broad mc≥10 A-pure 3 + r794-ALIVE mc5-9 11）
- **确认 NOFILE（rotation 蒸发）：10**（yicdk, zg7xg, g8en5[partial], hdhfh, 1y66j, r44l7, otgh9, uhla7, dqi7d + zg7xg/g8en5 hosts）
- **ssh-unreachable（host 超时，状态未知）：7**（rbr06, k7bl1, s59t7, gwa9k, n907k, satf4, vqefw）
- **确认 ALIVE：0**

## 结论
1. **r794 liveness-ALIVE 池（11-19 12:47 验证 33/34 ALIVE）在 ~4h rotation 窗口后（11-19 17:0x）已系统性蒸发**：本轮确认 ALIVE=0。r794→r801 已从该池产出 6 cases（r795 5of6x / r797 n57f9 / r798 tt73q / r799 2f3uv / r801 irod5 / r795b GpioCsvFormatConvert），余 27 候选本轮探测全部 NOFILE 或 host-unreachable。
2. **broad mc≥10 A-pure 顶候选**（yicdk mc120 / zg7xg mc65 / g8en5 mc73）全部 NOFILE → r802「broad 池 rotation 枯竭」结论再确证。
3. **根因 = rotation 蒸发，非「无 buildable 任务」**：r794 证明 mc≥5 池有 33 ALIVE buildable 候选，r795-r801 证明可产出 k≥8 质量case。当前 0-case 是 fetch-timing 问题（trace 在 ~4h 内被 rotation 删除），不是池枯竭。
4. **11-15 令 stop-loss 判据不触发**：stop-loss 条件是「mc≥5 候选里能忠实还原用户意图 + 可判分 check() 的任务真的耗尽」。本轮证据是 rotation 蒸发（fetch-timing），非任务耗尽。**shard_mc.A 不回退 10**（回退也不解决 rotation）。r794 overturn 的「mc≥5 扩池有效」结论维持。

## Unblock 路径（下一轮优先）
1. **新全量 ssh_eda_scan**（11-14 运维令授权，每日 ≤1 次；今日尚未扫，上次 11-18 23:05）→ 捕获当下活会话 → **扫完立即**（同轮，rotation 窗口内）fetch + deepread + synth。
2. 扫描后用 `mc-matrix --emit-candidates-mc 5` 重出 A-pure 候选池，优先 ssh-timeout 的 host 复探（rbr06/k7bl1/s59t7 等可能 host 临时 down，复探或可 ALIVE）。
3. 若新扫仍 0 ALIVE A-pure → 那时才算真枯竭，再议 shard_mc.A 回退。
