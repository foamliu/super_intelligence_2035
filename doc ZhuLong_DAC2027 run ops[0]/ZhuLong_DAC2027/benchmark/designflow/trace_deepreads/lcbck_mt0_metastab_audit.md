# 深读 · lcbck · e0029495 @ 10.129.2.11 · spice_sim · 2026-11-11 13:3x

## trace_source
- user: e0029495 / host: 10.129.2.11 (hfeg0pkn002) / session: 1792399702966_lcbck
- mc=10, 128616B / 14 msgs / 6 tool_use
- 附件真实路径: /home/e0029495/.cline/data/sessions/1792398577598_rkgop/uploads/01_coarse_bracket.mt0（30 行 PrimeSim HSPICE .measure 输出）

## USER#0（逐字，唯一自然语言 prompt）
`分析这份mt0文件，看看是否发生亚稳态` + attached `01_coarse_bracket.mt0`
其后 13 条全 assistant/tool_result（单 prompt 闭环）。

## assistant 工具链
1. read_files(01_coarse_bracket.mt0) → 读到 30 行 .measure 输出
2. list_allowed_files(uploads/, /home/e0029495) → uploads 仅此一 mt0
3. search_codebase(dfqd1/coarse_bracket/delta_obs) → 超时无果（无配套网表）
4. editor(create /home/e0029495/tmp/analyze_mt0.py) → 写 55 列解析 + 工程单位 + 派生量脚本
5. run_approved_command(python-runner analyze_mt0.py) → exit 0，输出 55 列名↔值映射
6. （最终）出「mt0 文件亚稳态分析报告」：VDD≈0.75V、delta_obs=-2.72ps（数据超前时钟打入采样孔径）、tcq=90.28ps、q_end/ax_end/b_end 均满摆幅收敛（resolved）、q_dead=0.7062（94.2%VDD，未满摆幅⚠）、ax/b 的 pm/probe/pp≈0.3547V（47.2%VDD 中间电平缓慢爬行⚠）、b_lo_r/b_hi_r/b_lo_f2=failed。结论：本 coarse bracket 点 **未发生持久亚稳态**（三方法末态均满摆幅），但 dead 探针点未完全分辨，需细扫描确认。

## mt0 结构（55 列）
$DATA1 + .TITLE 'dfqd1 manual three-method v20261014: shared manually edited coarse bracket'
列名（13 行 header）：clk50 d50 delta_obs q50 | tcq q_imin q_imax q_start | q_dead q_end q_pm q_probe | q_pp q_raw_min q_raw_max q_dw_min | q_dw_max q_post_min q_post_max ax_imin | ax_imax ax_start ax_dead ax_end | ax_pm ax_probe ax_pp ax_raw_min | ax_raw_max ax_dw_min ax_dw_max ax_post_min | ax_post_max b_imin b_imax b_start | b_dead b_end b_pm b_probe | b_pp b_raw_min b_raw_max b_dw_min | b_dw_max b_post_min b_post_max b_lo_f | b_hi_r b_lo_r b_hi_f b_lo_f2 | b_hi_r2 temper alter#
数据（15 行）：3.000e-09 ... 0.749999939 ... 0.7062 ... 0.3547 ... failed ... 25  1

## case 设计（A-faithful，spice_sim，L1 offline-parse）
- **ID**: EDA-Eval-DesignFlow-Mt0MetastabAudit-001
- **prompt**: USER#0 逐字 + 框定交付 `mt0_metastab_audit.py`（CLI `<mt0> <out_dir>`）+ `metastab_audit.json`
- **A（SUT 可见）**: 真实 01_coarse_bracket.mt0（resolved/无持久亚稳态）+ task_brief.md
- **B（hidden）**: 合成变体 mt0 — 同 55 列结构，但 q_end/ax_end/b_end 均停在中间电平 0.5V（NOT resolved），q_dead=0.5V，tcq=5e-9（亚稳态延长 55×），delta_obs=-0.5ps，b_lo_r/b_hi_r/b_lo_f/b_hi_f 全 failed，alter#=3 ⇒ **metastability_detected=true**（与 A 的 false 反向）
- **check.py**: 解 zip → 跑 `mt0_metastab_audit.py <B.mt0> <out>` exit0 → 解析 metastab_audit.json → ≥12 断言（结构键/VDD 推断/delta_obs 符号/tcq 量级/三方法 resolved 判定/metastability_detected=true for B/dead_point 偏差/failed 列容错/temper+alter#/worst-method/三假 FAIL）
- **判分核心**: SUT 必须正确 (a) 解析 55 列含 "failed" 字符串容错 (b) 从 q_end/ax_end/b_end 推断 VDD+resolved (c) 对 B（末态不收敛）判 metastability_detected=true (d) 出结构化 json
- **难点**: parse-bound（55 列名跨 13 行、数据跨 15 行、含 "failed" 字符串与浮点混合）—— 印证 B r389「spice_sim hard part 在 parse 不在工具链深度」

## 自验要点
- ref 跑 B 必须 PASS 全部断言（metastability_detected=true）
- ref 跑 A 应判 metastability_detected=false（交叉验证脚本对两向都正确）
- 4 neg（empty/print/hardcodeA/coredeleted）全 FAIL
- §4.9 (a)空壳 (b)只print期望串 (c)删核心 全 FAIL
- 断言门 k_rationale == k_check ≥ 8

## 价值
本轮独立重核 mc10.fresh=36（前轮称「全非 spice-dominant」）推翻该结论：lcbck spice-ratio=0.341 仅因 mt0-parse session 的 hspice keyword 计数低（parse-bound 特性）被 0.35 启发式滤掉，实则 CLEAN spice_sim produce-task。⇒ 印证 B r389 讨论发言「spice-ratio 滤波对 parse-bound spice 域系统性低估」，也说明 11-05 重扫令仍必要（前轮 0-case 结论过紧）。
