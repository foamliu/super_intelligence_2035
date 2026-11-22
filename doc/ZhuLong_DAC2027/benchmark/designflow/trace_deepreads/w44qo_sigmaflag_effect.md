# trace_deepread: w44qo — PrimeSim sigmaflag 生效判定 (ynbai @ hfeg0pkn004)

- **session**: `1794816151495_w44qo` (ynbai @ hfeg0pkn004, mc=6, scan ssh_eda_search_20261122_172249)
- **size**: 30,292 bytes / 6 messages (2 user, 3 assistant, 1 tool result)
- **keywords**: hspice:12;pdk:10;netlist:6;synopsys:4;aether:3;virtuoso:1;transistor:1;mosfet:1;.spi:1 (clean B-spice, hspice dominant)
- **fetched via**: `scp hfeg0pkn004:/home/ynbai/.cline/data/sessions/1794816151495_w44qo/1794816151495_w44qo.messages.json` (e0031982 identity from .75, passwordless)

## User intent (U0, msg_mwiz7281_1)

> primesim仿真，手动给网表内部分管子后添加sigmaflag，该sigmaflag setting是否可以生效，是否需要加primesim option，例如XMM1 Y A vcc! vbulkp! ptn_lv w='WP' l='LP' nf='nfP' sigmaflag=6

用户在 PrimeSim Monte Carlo 失配仿真里手动给网表实例挂 `sigmaflag=6`，问两件事：
1. 这种实例级 `sigmaflag` 是否生效？
2. 是否需要额外加 PrimeSim option（如 `+simflag` / `+mismatch`）来启用？

## Assistant 行为

- msg2 (assistant): thinking + 调用 `ask-eda` skill 检索 EDA 知识库
- msg3 (tool result): AskEDA 返回（doc: primesim_user_guide.pdf, score 0.91），结论：sigmaflag 是模型参数；生效条件是模型支持实例级覆盖 + .MC 分析存在 + VARIATION 类型匹配；`+simflag`/`+mismatch` 不是 PrimeSim 标准命令行选项
- msg4 (assistant): 综合 AskEDA + 自身知识给出中文长答：
  - 表格分类：标准 BSIM4/BSIM3 PDK 实例级 sigmaflag ✅ 生效；宏模型可能不暴露接口 ❌
  - 不需要 `+simflag` / `+mismatch`（非 PrimeSim 标准选项）
  - 需要 `.MC` 分析语句（如 `.MC 1000 TRAN VARY MISMATCH`），无 .MC 则 sigmaflag 不生效
  - 失配仿真需 `.MC` VARIATION=MISMATCH 或 BOTH
  - sigmaflag 常见值含义表（0/1/2/3/6）
  - 验证方法：`primesim -soacheck <input.spi>`

## 关键产物

**纯 Q&A session，无脚本/netlist/文件产物**。assistant 只输出文字答案，未读取/修改任何用户文件。

## Reframe 决策（L1 Python 复刻）

跟 r1066 (rrx5s → ProbeCovAnalyzerProduce-001) 同模式：把用户的信息需求程序化。

**case = EDA-Eval-DesignFlow-SigmaflagEffectAnalyzerProduce-001**

实现 `sigmaflag_effect_analyzer.py <spec.json> <netlist.sp> <out.json>`：
- 解析 netlist 找带 `sigmaflag=` 的 X-instance
- 查 spec 的 `instance_sigmaflag_supported_models` 判 model 是否支持实例级覆盖
- 查 `.MC` 语句（present + VARIATION 类型）
- 判 variation 兼容性（MISMATCH 兼容 {MISMATCH,BOTH}；PROCESS 兼容 {PROCESS,BOTH}；BOTH 仅兼容 BOTH）
- 扫非标准选项（`+simflag` / `+mismatch`）
- 输出 per-instance verdict + summary

**A (visible)**: ynbai 真实场景 — XMM1 (ptn_lv, sigmaflag=6) + XMM2 (ntn_lv, sigmaflag=3) + .MC VARY MISMATCH + supported=[ptn_lv,ntn_lv] → all_effective
**hidden B (anti-hardcode)**: 五重异构 — XQ1/XQ2/XQ3 (pmos_25/nmos_25) + sigmaflag 2/6/6 + .MC VARY BOTH + supported=[pmos_25]（**排除 nmos_25** → XQ2 not_effective）→ summary "partial"（2 effective / 1 not_effective）。核心齿：XQ2 的 not_effective 反 naive "always effective"。

check.py 13 条 (a-m)：zip+compile / B exit0 / 顶层键精确 / n_instances==3 / per-instance 键 / sigmaflag_value==oracle / model_supports==oracle / mc_present+variation==oracle / verdict==oracle(独立复算) / n_eff+n_not==oracle / summary=="partial" / anti-hardcode(A 名缺席+B 名在场+nonstd==False) / 3-seed sha256 一致

3 negs: neg_empty(空壳→a/b) / neg_print_only(硬编 A report→d/f/h/j/k/l 6 齿) / neg_core_removed(真解析 B 但跳 model check 永远 effective→g/i/j/k 4 齿)。§4.9 三假齐 FAIL ✓。

自验：REF 13/13 PASS ✓；negative_selftest 3/3 FAIL ✓；3-seed 确定性 ✓。

## trace_source metadata
- user: ynbai (real, unmasked per AGENTS.md §1.2)
- host: hfeg0pkn004
- session_file: 1794816151495_w44qo
- match_count: 6
- scan_snapshot: ssh_eda_search_20261122_172249
- real_task_summary: 见 B.jsonl entry metadata
