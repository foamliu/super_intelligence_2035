# 深读笔记：1793620820813_7qn0b — DFT env 梳理（parked）

- **trace**: `1793620820813_7qn0b` · user `e0045128` @ `hfeg0pkn005` (10.129.2.14) · mc=84 (57 netlist + 27 synthesis) · 60 msgs · clide `lead`
- **台账**: shard A，claim→parked（真实文件不可达 + L1-ish）
- **域**: verification（DFT/ATPG/LEC）

## 用户轮

- USER#1 (msg0) 逐字: 「这是一个`/rundata/lacaa/V0/simdir/DFx/POST_April/WORK/keyangCao/TV_1/FS/DFT/`做DFT 的env，请帮我梳理一下」= clean 提需求（梳理 DFT env 目录结构 + 状态）→ A档②合格。
- USER#2-4: 后续概念 Q&A（SOCV STA / ATPG STIL / Tessent TAM），非任务。

## 金标准（助手 msg 45 结构化总结）

6 阶段 DFT env（1.bscan/2.mbist/3.dft/4.syn_scan/5.ATPG/6.LEC，Univista DFX 框架，设计 `pa_cpu_merged_top`，工艺 `FSP51H204L6W35T6`，角点 `ssgnp_cworst_ccworst_v0p675_0c`，DC/Formality 2023.12-SP5，Univista 2025.06.P2，Tespert 260621_os7）。运行结果：ATPG stuck TC=97.51%、transition TC=90.77%、LEC Verification SUCCEEDED（17655 passing / 0 failing）。

## 为何 parked（不合成）

1. **真实文件不可达**: `/rundata/lacaa/.../DFT` 从 .75 与 10.129.2.14（e0031982 身份）均 permission denied（归 keyangCao）。trace 中 `read_files` tool_result 全空（权限），仅 `list_allowed_files` 目录树 + `_dfx_scan.py` 解析输出（msg 27/31/36）+ 助手总结（msg 45）被捕获。→ 无法用真实 attachments 做 A 档⑥。
2. **L1-ish**: 任务本质是「读配置文件 + 解析日志 → 结构化报告」，候选不跑 EDA 工具，属 L1 静态解析（TASK §5 新建 case 只做 L2/L3）。
3. **B 档合成成本高**: 须从 trace 重建 6 阶段 TASK_VARS/formality.log/ATPG coverage.rpt（304KB dump，零散），+ ≥8 断言结构化报告字段 + B 异构 bundle + 5 negatives，工作量超单轮预算。

→ parked，不优先。若日后需要 verification 域 B 档补牙可回捡，但需先解决真实文件访问（su e0045128 或 keyangCao 授权）。
