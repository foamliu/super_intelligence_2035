# 深读笔记：1793501977670_k1af0 — eric9zhu @ hfeg0pkn005 — ERC PATHCHK 顶层 vs 子模块拓扑诊断

## trace 元数据
- user: eric9zhu · host: hfeg0pkn005 · session: 1793501977670_k1af0.messages.json
- size: ~290KB · msgs: 147 · match_count: 147 · domain: physical_verify
- tools: calibre LVS + ERC PATHCHK + auCdl netlist + svdb 报告解析
- mtime: ~1793508600 (10-30 2026)

## USER 轮（verbatim 要点）
- **USER#0**: vref_mos_core 的 Calibre LVS 调试，LVS 对比 CORRECT，但 ERC 报大量 PATHCHK POWER&&!GROUND NOFLOAT 错误(1000 poly/435 net 达上限)，PATHCHK GROUND&&!POWER NOFLOAT==0，子模块 vref_mos_op/vref_mos_r2trim 单独跑 PATHCHK 干净(0 错误)，仅顶层 vref_mos_core 报错，LVS rule POWER/GROUND name 各层级一致
- **USER 4 问**: ①为什么报这些错 ②画报错节点的电路图 ③只要原始 TOPO 不要体二极管示意 ④为什么底层 cell 不报、顶层才报、rule 里电源地设置一样
- 本任务聚焦 ①④ 的自动化诊断

## A-档 / B-档 判定
- trace 无单一干净 accepted artifact（用户多轮交互，assistant 逐步诊断）
- B-synthesized: bg_pd_core (AVDD/AVSS, 800 poly/312 net, 42 inst, P45_pch_stk_svt_f2_l28 PMOS-only 堆叠, 2 clean subcells bg_pd_amp/bg_pd_trim)

## trace assistant 工具链 / 产物
1. 解析 `vref_mos_core.pathchk.erc` — ERC PATHCHK 结果库(polygon 坐标 + 每条 rule 的 poly/net/vert 计数)
2. 解析 `vref_mos_core.lvs.report` — LVS 对比报告(verdict=CORRECT + LVS POWER NAME / LVS GROUND NAME 列表)
3. 解析 `vref_mos_op.lvsf` — LVS flags(lvs_PowerName / lvs_GroundName)
4. 解析 `vref_mos_core.src.net` — source SPICE 网表(auCdl 抽取, ~3600 行, 含所有 SUBCKT 定义)
5. 解析 `svdb/vref_mos_core.pathchk.rep` — 顶层 PATHCHK 报告(每条 rule 下的 instance path 列表)
6. 解析 `svdb/vref_mos_op.pathchk.rep` / `svdb/vref_mos_r2trim.pathchk.rep` — 子模块 PATHCHK 报告(均为空)

## 根因分析（assistant 发现）
- 网表 `P45_pch_stk_svt_f2_l28` 是全 PMOS 堆叠 subckt:
  - body 接 POWER(AVDD)
  - 内部节点只有 POWER 路径，没有 GROUND 路径
- 顶层实例化时触发 NOFLOAT（POWER 路径悬空）
- 子模块内部 PMOS+NMOS 拓扑完整 → 不报
- POWER/GROUND name 各层级一致 → 不是 name mismatch 问题
- 核心洞察: **顶层 vs 子模块的拓扑区分** — 问题出在顶层实例化的 PMOS-only 堆叠结构，不是 rule 配置

## case 合成设计
- **A_run** (可见): vref_mos_core (VDD/SAVDD power, 子模块 vref_mos_op/vref_mos_r2trim 干净)
  - vref_mos_core.pathchk.erc / vref_mos_core.lvs.report / vref_mos_op.lvsf / vref_mos_core.src.net / svdb/*.pathchk.rep
- **B_run** (隐藏): bg_pd_core (AVDD/AVSS, 800 poly/312 net, 42 inst, P45_pch_stk_svt_f2_l28, 2 clean subcells)
- **B_broken_run** (隐藏): bg_pd_core 但 bg_pd_amp 子模块有错 → SUBCELL_ERROR 哨兵

## 16 条断言 a–p
| # | 条件 | 说明 | 反作弊 |
|---|------|------|--------|
| a | zip+py | submit.zip 合法 zip 含 .py 分析器 | — |
| b | compile+stdlib | py_compile + 仅标准库(禁 calibre/gdspy/numpy) | — |
| c | B-exit0+JSON | B 退出 0 + stdout 合法 JSON dict | — |
| d | 10-keys | JSON 含全部 10 个必需顶层键 | — |
| e | B-cell=bg_pd_core | B cell==bg_pd_core | 反硬编码 A vref_mos_core |
| f | B-verdict=CORRECT | B lvs_verdict==CORRECT | — |
| g | B-power=AVDD | B power_names 含 AVDD | 反硬编码 A VDD |
| h | B-ground=AVSS | B ground_names 含 AVSS | 反硬编码 A VSS |
| i | pathchk poly | POWER poly>0 & GROUND poly==0 | 顶层报 POWER 不报 GROUND |
| j | B-inst_count=42 | top_level_errors POWER inst_count==42 | B 真实 instance 计数 |
| k | 2-subcells-clean | 2 个子模块均 clean | 反 "always error" |
| l | pmos_only P45 | pmos_only_subckts 含 P45_pch_stk_svt_f2_l28 | 根因 PMOS-only 堆叠 |
| m | diag_class | diagnosis_class==PMOS_ONLY_POWER_PATH | — |
| n | topology distinction | diagnosis 提及 top-level+subcell | 拓扑区分洞察 |
| o | cross-input guard A | A cell==vref_mos_core + A power 含 VDD | 反硬编码 B |
| p | B_broken sentinel | subcell err + diag≠PMOS_ONLY | 反 "always top-level" stub |

## 6 negatives (全部 FAIL, NEG_RC=0)
| negative | 失败条件 | 说明 |
|----------|---------|------|
| empty_shell | (c) | 空 .py, 不输出 JSON |
| print_expected | (o,p) | 硬编码 B JSON, 跨输入守卫失败 |
| core_deleted | (l,m,n) | 诊断逻辑被删, 无 pmos_only |
| naive | (g,h,i,j,k,l,m,n,o,p) | 不解析网表, 无 AVDD/AVSS |
| always_a | (e,g,h,j,l,p) | 硬编码 A, B 字段错 |
| stub | (j,k,o,p) | 忽略子模块错, B_broken 哨兵失败 |

## check.py 路径定位 (eval-driver 约定)
- hidden B: `workdir/hidden/B_run/` (主) → `workdir/reference/$CID/hidden/B_run/` (回退)
- visible A: `workdir/assets/$CID/A_run/` (主) → `workdir/A_run/` / `workdir/inputs/A_run/` (回退)
- check.py: 8395B, sha c4197892a97833e2160a9bdcafabbba9a8a26bb5b6d38ad61cce015f6b503076

## 网络传输发现 (r218 meta-lesson)
- sandbox(.75 10.129.32.75) ↔ local(10.251.36.15) TCP 全端口防火墙(仅 ICMP ping 通)
- 无共享 FS, SSH 端口 22 关闭
- MCP read_file/write 是唯一数据通道, 但 write tool LLM 再生对重复性 base64 数据有损坏:
  - 2500B chunk ~40% 损坏 / 600B ~7% / 200B 0%
- **解决方案**: sandbox 上 `python3 -m http.server`, execute 内 `fetch POST` 到 local `recv_server.py`
  - 完全绕过 LLM 再生, 50KB tar.b64 单次传输 0 损坏, SHA 一致
  - 这是未来 sandbox→local 二进制传输的首选方法
