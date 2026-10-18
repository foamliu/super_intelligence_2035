# ZhuLong（DAC 2027）论文数字重测审计

> 日期：2026-10-18 · 审计对象：`ZhuLong_DAC2027/DAC2027/6_exp.tex` + `zhulong_results.md`
> 结论：论文数字的问题分三类——**① 必须新跑（GPU）**、**② 只需重算/重分析（CPU）**、**③ 只需披露/限定**。不要把「legacy 与 fresh 混用」当成单纯缺数据；它直接影响效应量和显著性。

---

## 1. 审计总表

| # | 位置 | 数字 | 当前证据 | n | 状态 | 建议动作 | 优先级 | 成本 |
|:--|:--|:--|:--|:--:|:--|:--|:--:|:--|
| 1 | `tab:main-ablation` Full | **81.4 ± 1.5** | 陈熙元 5-run `[82.9,81.0,81.6,79.1,82.3]`（用户裁定论文锚点） | 5 | ✅ | 不重测；所有 Δ/p 以此为准 | — | — |
| 2 | `tab:main-ablation` RAG | **72.2 ± 1.6** | 5-run | 5 | ✅ | 不重测 | — | — |
| 3 | `tab:main-ablation` w/o Sandbox | **72.2 ± 1.6** | 与 RAG 同一 5-run 集 | 5 | ✅ | 不重测 | — | — |
| 4 | `tab:main-ablation` w/o Self-Expl | **77.3 ± 2.9** | 陈熙元 5-run；**刘杨干净 r1=83.5%（n=1）** | 5 vs 1 | ⚠️ **冲突** | 若保留 −4.1 pp：补 5-run 对账；若 83.5 成立，效应符号翻转 | **P1** | ≈7.5h GPU |
| 5 | `tab:main-ablation` w/o Retrieval | **81.0 ± 4.5** | 5-run；已标 ns | 5 | ✅（方差大） | 不重测；保持 `−0.4 pp, p=0.81` 方向性 | — | — |
| 6 | `tab:omega` (N) Pure LLM | **10.5 ± 1.9** | legacy 5-run（10-02/03） | 5 | ⚠️ legacy | 与 fresh (H) 混表；至少加 legacy 脚注；余力再重测 | P2 | ≈7.5h GPU |
| 7 | `tab:omega` (L) name-only | **82.8 ± 1.0** | legacy 5-run（10-02） | 5 | ⚠️ **legacy/fresh 混用** | 非单调 `(L)>(H)` 依赖此值；建议 5-run 重测或标 legacy | **P1** | ≈7.5h GPU |
| 8 | `tab:omega` (H) RAG | **72.2 ± 1.6** | fresh 5-run | 5 | ✅ | 不重测 | — | — |
| 9 | `tab:ablation-harness` (N') | **73.3 ± 2.2** | legacy 5-run `[72.2,70.3,73.4,75.9,74.7]` | 5 | ⚠️ **legacy 核心臂** | **重测 5-run（同时补成本）**；N'<B<F 唯一 legacy 点 | **P0** | ≈7.5h GPU |
| 10 | `tab:ablation-harness` (B) | **78.1 ± 1.3** | fresh 5-run（10-15~16） | 5 | ✅ 准确率 | 不重测准确率；成本见 #14 | — | — |
| 11 | `tab:ablation-harness` (F) | **81.4 ± 1.5** | fresh 5-run | 5 | ✅ | 不重测 | — | — |
| 12 | `tab:ablation-harness` Mean read-backs | 12.1 / 27.6 / — | (F) 5-run；(B) **r1 单轮**；(N') trace 丢失 | 5/1/0 | ⚠️ n 不一致 | 脚注已改 `(B) n=1`；B 5-run 见 #14 | P0/P1 | 见 #14 |
| 13 | `tab:readback-cost` (F) | 12.1 / 2.22 / 3.4 | 5-run 均值（timeout range 1–6） | 5 | ✅ | 不重测 | — | — |
| 14 | `tab:readback-cost` (B) | **27.6 / 4.25 / 13** | **r1 单轮**（13 = readback_binary r1 timeout） | **1** | ⚠️ **n=1** | 先从 5 个 fresh batch 的保留 trace 提取；无 trace 再补 5-run | **P0** | CPU / ≈7.5h GPU |
| 15 | `tab:readback-cost` (N') | **— / — / —** | trace 在存储迁移中丢失；墙钟受 license/端口故障污染 | 0 | ❌ **缺失** | **重测 5-run 并保留 trace**，同时补 Pass@1 与成本 | **P0** | ≈7.5h GPU |
| 16 | `tab:phi-bound` k10/k3/k1/lagged | 77.7/69.1/63.8/73.0 | 各自 5-run；Converged/gen-fail 齐全 | 5 | ✅ | 不重测 | — | — |
| 17 | `tab:phi-bound` unbounded | **81.4 ± 1.5** + Converged **99.1** + gen-fail **10.4** | **Pass@1 来自陈熙元 81.4 集；99.1/10.4 来自刘杨 82.1 集** | 5+5 | 🔴 **两套 run 混用** | 从 81.4 集重算 Converged/gen-fail；否则不能贴 81.4 标签 | **P0** | CPU |
| 18 | `tab:phi-bound` p/CI | 各臂 p 与 95% CI | 很可能以刘杨 82.1 unbounded 为对照 | 5 | 🔴 **对照集可能错** | 用与 #17 同一 unbounded 集重算 McNemar/bootstrap | **P0** | CPU |
| 19 | `tab:llm-comparison` GLM-5.2 | 83.3 ± 3.1（+1.9 ns） | 5-run | 5 | ✅（ns） | 不重测；`ZL.glm-5.2` n=1 是另一 CLI/SDK，不入表 | — | — |
| 20 | `tab:llm-comparison` DeepSeek-V4-Flash | 60.1 ± 5.5 | 5-run retest（−p 4 / maxTokens 16384） | 5 | ⚠️ 显著性未重算 | **重算** McNemar/bootstrap；现 `***` 是旧 pooled 分析继承 | **P1** | CPU |
| 21 | `tab:llm-comparison` Kimi / Doubao | 77.0 ± 1.6 / 63.8 ± 1.4 | 5-run | 5 | ✅ | 不重测 | — | — |
| 22 | `tab:cross-language` Full SKILL | 60.3 ± 6.7 | 5-run；备注「可能要重测」；低于 w/o Self-Expl 61.5 | 5 | ⚠️ 可疑 | RQ3 只依赖 full top / pure LLM bottom；中间排序披露即可 | P2 | ≈7.5h GPU |
| 23 | `tab:cross-language` RAG SKILL | 33.9 ± 10.6 | 5-run，方差大 | 5 | ⚠️ 不稳定 | 披露 directional；不重测也支撑主结论 | P2 | — |
| 24 | `tab:cross-language` w/o Retrieval Tcl-Innovus | 61.8 ± 34.6 | 5-run，方差极大 | 5 | ⚠️ 不稳定 | 论文已标 directional；保持，不重测 | P2 | — |
| 25 | `tab:cross-language` Pure LLM | 10.5/33.2/2.9/20.0 | 5-run（PyAether 为 legacy） | 5 | ⚠️ legacy PyAether | 只需披露；重测收益低 | P2 | — |
| 26 | Error analysis | 17 gen-fail / 12 exec-fail（8 L4 / 4 L3） | 单条代表性 trace（81.6%） | 1 | ℹ️ 定性 | 不重测；若修 wrong-save-path，计数会变，需注明 representative | P3 | — |
| 27 | `ZL.glm-5.2` r1 | `[TBD·in-progress]` | 09:38 启动，n=1 | 1 | 🟠 跑中 | 不重测；完成后 provisional 回填，不入论文表 | — | — |

> 备注：`w/o Sandbox` 与 `RAG` 数值相同不是笔误——两者都是「检索可用、执行器关闭」的同一配置。

---

## 2. 必须新跑（GPU）的清单

| 顺序 | 臂 | 目的 | 轮数 | 预计 | 依赖 |
|:--:|:--|:--|:--:|:--:|:--|
| 1 | **S1.readback_none (N')** | 补 Pass@1 + mean `run_code` / wall / timeout / Converged / gen-fail | 5 | ≈7.5h | ZL.glm-5.2 r1 结束、GPU 空闲 |
| 2 | **S1.readback_binary (B) 成本** | 把 27.6/4.25/13 从 n=1 升到 5-run | 0（有 trace）/5 | CPU 或 ≈7.5h | 先查 `output_evaluation/2026_1015_*` 的 trace |
| 3 | **S1.omega_low (L)**（可选） | 消除 `(L)` legacy 与 `(H)` fresh 混用；验证非单调 | 5 | ≈7.5h | 优先级低于 N'/B |
| 4 | **C1.wo_selfexp**（可选） | 对账 77.3±2.9（陈） vs 83.5（刘 n=1） | 5 | ≈7.5h | 若论文保留 −4.1 pp 结论 |

**总 GPU 预算**：必做 1+2 ≈ 7.5–15h；可选 3+4 ≈ 15h。当前 36.15 上 ZL eval 占 4 端口/8 并行，先排队，不打断。

---

## 3. 只需重算/重分析（CPU，零 GPU）

1. **`tab:phi-bound` unbounded 行**：从陈熙元 81.4 集的 trace 重算 `Converged` 与 `Mean gen-fail`；若 trace 不可得，则把该行改成与 82.1 集一致，并明确标注「此表 unbounded 使用 82.1 集」——**不能继续把 81.4 的 Pass@1 和 82.1 的 Converged/gen-fail 拼在一行**。
2. **`tab:phi-bound` p/CI**：确认 McNemar/paired bootstrap 的对照 unbounded 集；与上一条统一。
3. **Flash retest 显著性**：对 60.1±5.5 的 5-run retest 重算 McNemar/CI，替换继承的 `***`。
4. **B 成本 5-run 提取**：优先从 `2026_1015_*` 五个 batch 的保留 trace 解析；若 trace 存在，这一步零 GPU。
5. **任何以 82.1 为基准的 Δ**：全部改为对 81.4 重算（例如 lagged 的 −9.1 pp 应改为约 −8.4 pp，若论文正文引用了该差值）。

---

## 4. 只需披露/限定（不重测）

- `(N)` Pure LLM 10.5 与 `(L)` 82.8 是 legacy；`(H)` 72.2 是 fresh。至少加脚注；`(L)` 是非单调结论的关键，建议优先升级为重测（见 §2-3）。
- SKILL 的 Full 60.3 / RAG 33.9 / w/o Retrieval 39.0 中间排序不稳定；RQ3 的主结论（Full top、Pure LLM bottom）仍成立。
- Tcl-Innovus w/o Retrieval ±34.6，论文已标 directional，保持。
- Error analysis 是单条代表性 trace，不是总体统计；文中已用 "representative trace"。
- `ZL.glm-5.2` n=1 是 CLI/SDK 对照，不是论文表；不要与 83.3±3.1（cline 3.0.51）混用。

---

## 5. 无反馈臂 `(N')` 成本重测的价值判断

**值得排队，理由三条：**

1. **补齐成本阶梯**：现在 `(F)` 有 5-run 成本、`(B)` 只有 n=1、`(N')` 完全缺失。补 `(N')` 5-run 后，Table 7 才能从「两档 + 一个空洞」变成完整的三档成本证据。
2. **检验一个可能反直觉的结论**：legacy 日志里 `(N')` 的 timeout 计数约为 `[1,0,0,0,0]`（r1=1；r3–r5=0；r2 只记 8 fail/0 exec_err），**低于** `(F)=3.4`、`(B)=13`。这暗示无反馈 agent 可能「不迭代、早提交」——**成本不一定随观测变窄而单调上升**。如果重测确认，论文应把结论从「fidelity↓→cost↑」改成「accuracy 单调、cost 非单调（无反馈反而少搜索）」，这反而更有意思、更抗审稿。
3. **刷新唯一 legacy 的核心臂**：`(N')` 的 73.3±2.2 是 10-02/03 的旧 harness；当前 harness 已加 V3 文档、自探索、反作弊 hook、预算 hook。重测同时把 N'<B<F 的排序从「legacy + fresh 混用」升级为同一 harness 的 5-run 对照。

**风险**：若 N' 成本确实低于 B/F，论文原「收敛成本随保真度下降而上升」的措辞必须限定为「在 B→F 区间成立；N' 因不搜索而成本低但准确率最低」。这是可发表且更诚实的表述，不应为了维持单调而隐去 N'。

**预算**：5-run × 158 题 × 8 worker ≈ 7.5h GPU + ~0.5 天 CPU 解析；在 ZL eval 结束后排队。

---

## 6. 建议的最小可交付集

若时间紧，按以下顺序做，收益/成本最高：

1. **P0-CPU**：`tab:phi-bound` unbounded 行 + p/CI 重算（零 GPU，修掉最硬的内在不一致）。
2. **P0-GPU**：`(N')` 5-run（准确率 + 成本 + trace 保留）。
3. **P0-CPU/GPU**：`(B)` 成本 5-run（先查 trace；没有才跑）。
4. **P1-CPU**：Flash retest 显著性重算。
5. **P1-GPU（可选）**：`omega_low (L)` 5-run；`w/o Self-Expl` 5-run。



