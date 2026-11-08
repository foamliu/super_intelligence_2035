# deepread — 1792399658249_w4b6q · mt0 亚稳态诊断

- **trace**：e0029495 @ hfeg0pkn002，session 1792399658249_w4b6q.messages.json（147KB, 2 msgs）
- **域**：spice_sim（characterization of DQ flip-flop metastability）
- **A-faithful 选轮**：U#1 逐字「分析这份mt0文件，看看是否发生亚稳态」+ 附件 mt0（HSPICE .mt0, 140KB）。提出需求，无根因/修复方向 → A档 ✓

## trace 流（无 assistant 响应被 snapshot 捕获）
- msg[0] role=user：`<user_input mode="act">分析这份mt0文件，看看是否发生亚稳态` + 附件 `01_coarse_bracket.mt0`（指向另一 session rkgop 的 upload）
- msg[1] role=user：同 prompt + 附件 `mt0`（本 session upload，140KB，`/home/e0029495/.cline/data/sessions/1792399658249_w4b6q/uploads/mt0`）
- 无 assistant msg（snapshot 早抓或会话中断）。companion .json：0 msgs。

## 真实 mt0 结构（dfqd1 manual three-method）
- 格式：HSPICE `$DATA1` 多块，每块 = 1 characterization 工作点（alter#）。
- 66 块，8 个 unique .TITLE（dfqd1 manual three-method v20261014 系列 + c full-dff + isolated slave）。
- 列 schema（55 列，block 0）：`clk50 d50 delta_obs q50 tcq q_imin q_imax q_start q_dead q_end q_pm q_probe q_pp q_raw_min q_raw_max q_dw_min q_dw_max q_post_min q_post_max ax_imin ax_imax ax_start ax_dead ax_end ax_pm ax_probe ax_pp ax_raw_min ax_raw_max ax_dw_min ax_dw_max ax_post_min ax_post_max b_imin b_imax b_start b_dead b_end b_pm b_probe b_pp b_raw_min b_raw_max b_dw_min b_dw_max b_post_min b_post_max b_lo_f b_hi_r b_lo_r b_hi_f b_lo_f2 b_hi_r2 temper alter#`
- 数据行跨多物理行（HSPICE 4 值/行），单逻辑行 = ceil(55/4)=14 物理行。
- "failed" token = 该测量在该工作点未决（measurement timeout/non-resolution）。
- 块级统计：63/66 块含 failed；failed 列计数：b_lo_f2=61, b_hi_r2=58, b_hi_f=57, b_lo_f=35, q50=29, tcq=27, b_hi_r=27, b_lo_r=2。
- **critical = tcq（clock-to-Q）+ q50（Q 输出值）**：tcq 27/q50 29 failed → DQ 输出在那些工作点未决 → **亚稳态发生**。

## 金标准（依 A档 rule 4「断言只对事实」）
无 assistant trace → 不从 trace 答案反推；mt0 内容是确定性事实。
- 解析多块 .mt0 → 每块映射 token→列 → 计 failed_signal_counts。
- metastability_detected = (tcq failed≥1) OR (q50 failed≥1)（critical 输出未决）。
- 报告 8 键：n_blocks / blocks_with_failures / blocks_clean / total_failed_measurements / failed_signal_counts / critical_signals_failed / metastability_detected / metastability_evidence。

## 合成（沿用 NetlistStructDiff-001 A-faithful 惯例：忠实复刻真实结构合成 A/B）
- A（可见）：19 块（3 clean sanity + 15 metastable coarse-bracket + 1 A_ONLY_MARKER clean），tcq=12/q50=13 → TRUE。
- hidden B：14 块（5 clean + 9 仅 b_* failed，无 tcq/q50）→ FALSE（测 agent 区分 critical vs 非 critical）。
- check.py 14 断言（a-n），ref PASS 14/14，4 negative 全 FAIL，3 假提交全 FAIL，k=14==14≥8 ✓。
- 落库 EDA-Eval-DesignFlow_B.jsonl 193→194，ledger 195→196 covered。

## 备注
- 本轮独立重扫（rescan_1109_0431.md）从前轮漏网的 6 候选中捞出 w4b6q；另 5 候选主机归档不可达。
- w4b6q 是该 user (e0029495) 首次进入 shard B 覆盖。
