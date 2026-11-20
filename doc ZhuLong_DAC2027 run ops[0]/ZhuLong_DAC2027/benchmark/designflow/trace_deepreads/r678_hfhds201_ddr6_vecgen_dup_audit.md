# r678 — hfhds201 DDR6 vecgen 去重审计 + 远程 infra-block 复核

**轮次**: r678 (2026-11-17, shard A)
**结论**: 0 case。hfhds201 可读 A-domain 候选全部与 shard B 已造 case 碰撞；`next` peek 的真正 fresh 候选全在远程机（SSH denied）。

## 一、hfhds201 (.75 本机) A-domain 候选逐项核对

直接扫 `ssh_eda_search_20261116_072610/summary.tsv` 取 hfhds201 + A-keywords(verdi/vcs/synopsys/verilog/sv/rtl/sdc/innovus/pt_shell/...) + mc≥10，按 mc 降序，与 shard A 台账 + 4-shard 已造 case 交叉：

| session | user | mc | keywords 摘要 | 状态 | 碰撞 case (shard B) |
|---|---|--:|---|---|---|
| 1791611498731_wg5u2 | zjqiao | 738 | netlist/cmos/schematic/lvs (C-domain, verilog:33 仅过 A 滤) | 跨域 C | — |
| 1794723288564_svmca | jzeng | 575 | drc/.gds/calibre/pex (C-domain) | IN_LEDGER_A (r675 已造 AutoViaV4M4M5FillAnalyze) | — |
| 1794732178509_huu52 | jzeng | 572 | drc/.gds/calibre/pex (C-domain) | FRESH 但跨域 C | — |
| 1793672454901_bg39v | tongfanl | 550 | analog/verilog/pyaether | IN_LEDGER_A | — |
| 1794378055746_1s79t | mike | 479 | analog:2580/verilog:2450/netlist:967 (mixed, mike 多为 C/analog) | FRESH 跨域 | — |
| 1793866097938_fl4rh | mike | 427 | netlist/verilog/schematic/analog (mike mixed) | FRESH 跨域 | — |
| 1790849679042_bjkmi | tongfanl | 417 | analog/verilog:964/sv:674 (DDR6 vecgen) | FRESH, 4.2MB>2MB | topic 与 WriteDqPsdMapping/StimOp2 同簇 (待核) |
| 1794734620660_00p77 | jzeng | 416 | drc/.gds/rtl/pyaether (C-domain) | IN_LEDGER_A (r656 AutoViaV4Diagnose) | — |
| 1794473890903_7aypg | zjqiao | 414 | netlist:4657/verilog:97 (netlist 主, C-domain) | FRESH 跨域 C | — |
| 1793243267055_5hjg7 | zjqiao | 414 | 同 7aypg (netlist 主) | FRESH 跨域 C | — |
| 1794474782925_5ityn | zjqiao | 404 | 同 7aypg | FRESH 跨域 C | — |
| 1791526663956_p64wo | tongfanl | 403 | analog:4036/drc:2298/verilog:124 (C-domain drc 主) | FRESH 跨域 C | — |
| 1791796775106_b1w28 | tongfanl | 344 | verilog:1084/sv:285 (DDR6 vecgen) | FRESH | **dup → WriteDqPsdMappingExtract-001 (B)** — b1w28 U#0 = "整理 DQSEL_LH 未定义时 write task dq→PSD0DQ/PSD1DQ mapping 表(1P12/1P6/2P6/2P3)"，与 B 的 WriteDqPsdMappingExtract-001 同题 |
| 1793935018992_a75vy | dsgao | 313 | drc/netlist/synopsys (C-domain drc 主) | FRESH 跨域 C | — |
| 1794307198596_wimgg | jzeng | 288 | drc/calibre/lvs (C-domain) | FRESH 跨域 C | — |
| 1791792142076_m5mka | tongfanl | 262 | verilog:1314 (DDR6 vecgen) | FRESH | **dup → DdrVecgenDQSELH-001 + WriteDqPsdMappingExtract-001 (B)** — m5mka U#0="DQSELH 和 DQSEL_LH 作用关系"，U#1="DQSEL_LH 未定义时 write dq→PSD mapping 表"；两问均已被 B 造 |
| 1790998236503_95kx2 | tongfanl | 256 | verilog:1220 (DDR6 vecgen) | FRESH | **dup → StimOp2MisMatchDiag-001 (B, session 95kx2 完全相同)** — 95kx2 U#0="Load_Mode OP2 设 1 但 WTM002 激励 OP2 不为 1，为啥"，B 已用同一 session 造 StimOp2MisMatchDiag |

### 关键发现
tongfanl 在 hfhds201 上的 DDR6 dscqa.vecgen_local 系列会话（DQSELH / DQSEL_LH / write-dq-PSD-mapping / Load_Mode-OP2 / stimulus 抽取）已被 **shard B** 系统性造题：
- `EDA-Eval-DesignFlow-DdrVecgenDQSELH-001` (B, session zm0zw, tongfanl)
- `EDA-Eval-DesignFlow-WriteDqPsdMappingExtract-001` (B)
- `EDA-Eval-DesignFlow-StimOp2MisMatchDiag-001` (B, session 95kx2, tongfanl)
- `EDA-Eval-DesignFlow-LoadModeOpTruncDiag-001` (B, session 1550c, tongfanl)

shard A 不重复造（🚫 不改/不碰 B 的 jsonl，🚫 跨 shard 重复题）。其余 hfhds201 FRESH 候选要么跨域 C（zjqiao netlist/LVS、jzeng DRC、dsgao DRC、mike analog），要么 >2MB（bjkmi 4.2MB 单轮不可合成）。

## 二、`next` peek 真正 fresh 候选全在远程机

`trace_ledger.py --shard A next` 的 peek 列表（已排除 4-shard 台账）18 条，逐条查 host：
- v593e → hfeg0pkn004 (t0002614)
- hasla → hfeg0pkn002 (zqzhan)
- jr0o3 → hfeg0pkn005 (ronghu)
- bih9j → hfeg0pfn058 / hfeg0pjn109 / hfeg0pkn002 (thomasz)
- i0cnz → hfeg0pgn099 / hfeg0pkn003 (mwxi)
- fdrqq → hfeg0pgn111 / hfeg0pgn116 / hfeg0pkn001 / hfeg0pkn002 (zxtu)
- f1pj5 → hfeg0pkn001 (jingc)
- 1e0xa → hfeg0pkn001 (sagequan)
- cn4bl → hfeg0pkn001 (steveny)
- kubzy / ibwba → hfeg0pkn040 / hfeg0pkn051 (zhililu)
- … 其余同类

**全部在远程机**（hfeg0pkn*/hfeg0pfn*/hfeg0pgn*/hfeg0pjn*），**无一在 hfhds201**。承 r647/r651/r654 MEMORY：ssh 到这些远程机全 `Permission denied`（pyAether whoami=t0002997 非 e0031982，.75 仅对 697/698 台免密的反向不成立——本 sandbox 身份 e0031982 gid=555(guest) 无远端 ~/.cline 读权限）。

## 三、判据

- **不是"无候选"**：mc≥5 pool 仍有 ~2309 fresh（`next` peek 18 条为证）。
- **是"可达 fresh 全 dup 或跨域"**：本机 hfhds201 可读的 A-domain FRESH 候选 3 条（m5mka/b1w28/95kx2）全与 shard B 已造 case 同题；其余 hfhds201 FRESH 跨域 C。
- **远程 fresh infra-block**：peek 列表 18 条全在远程机，SSH denied 不可深读。

按 2026-11-15 令「mc≥5 扩池自动止损判据 = mc≥5 候选里有无能忠实还原用户意图且能写可判分 check() 的任务」：mc≥5 候选**存在**（18 条 peek），但**当前全部不可达**（远程 infra-block）。本 round 0 case 的根因是 **infra-block + dedup-collision**，非"池枯竭"。

## 四、下一步建议（不本轮执行）
1. 请运维确认 e0031982 sandbox 身份能否加读远端 ~/.cline 权限（或换 t0002965/t0002997 身份跑 ssh_eda_search 抓取已存 messages.json 到 .75 本地缓存供只读）。
2. 若远程持续不可达，shard A 可考虑：(a) 接受跨域 C 候选按 A-domain 关键词命中的子片段造（如 zjqiao netlist 含 verilog:97 的数字子片）；(b) 等 11-18+ 新扫描快照。
3. 本审计已记录，下轮 `next` 仍会 peek 远程 18 条；若仍 infra-block，按 auto-stop 连续 3 轮 0 case 后将 shard_mc.A 改回 10 并转 WAVEVIEW / 论文维护。
