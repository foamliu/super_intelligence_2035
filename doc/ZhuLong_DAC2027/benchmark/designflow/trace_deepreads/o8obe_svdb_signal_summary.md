# Deepread: o8obe — shunlinp LVS svdb SEM-to-schematic signal localization summary (analog_context)

- **Trace**: shunlinp @ hfeg0pkn003 (ip 10.129.2.13), session `1793068312241_o8obe.messages.json`, mc=27, keywords `lvs:845;svdb:542;sem:318;schematic:197`.
- **Size**: ~67 msgs / 4 substantive user turns (rest tool_results). act 模式调用 python-runner 批量解析 JSON。
- **Tool chain**: list_allowed_files, run_approved_command (python-runner)×N, read_files — assistant 遍历多个 `result_*` 文件夹下 `defect_*/query_result.json`，逐个解析并统计定位到的信号，产 `signal_summary.md`/`csv` 报告。

## User intent (verbatim, A-faithful)
- **U#0**: "当前文件夹下有多个子文件夹，每个里面包含了我们使用lvs svdb从gds到sch定位的信号信息，请你逐个看下，并统计下定位到的信号有哪些。" — SEM2SCH_LOC 物理调试流程，GDS→schematic 信号定位结果汇总。
- **U#1**: 任务扩展 — "请把给定目录下的其他几个 result_... 文件夹下的 defect case 命中的信号也各自统计下，分别形成报告。" — 多文件夹遍历 + per-folder 报告。
- U#0+U#1 = clean produce-task (proposes goal + 扩展 spec)；trace 末用户隐含接受（全 act 无 reject）。

## Real accepted result
- assistant 用 python-runner 逐个 `query_result.json` 解析（字段 defect_id / class_name / net_group / hit_count / signals），按 result_* 文件夹分组统计：per-folder defect_count / unique_signal_count / signal_families / total_hit_points，产 `signal_summary.md` + `signal_summary.csv`。
- 原 SEM2SCH_LOC 私有 svdb 数据不可复现（shunlinp 主机私有 GDS/svdb，沙盒无法 scp）⇒ **B-grade synthesized reframe**（合成 result_M0ETC_A 可见输入 + 隐藏 B，同结构不同信号名/数值/文件夹名）。

## Case decision: EDA-Eval-DesignFlow-SvdbSignalSummary-001
- domain=analog_context, track=B (synthesized; trace-faithful prompt), layer=L2 (subprocess 真跑候选 python 脚本), design=B.
- Deliverable: `outputs/submit.zip` 内含 `summarize_signals.py`，接受 `--root <dir> --output signal_summary.json`，遍历 `result_*/defect_*/query_result.json` 汇总信号。
- check.py: **17 conds** (a, a2, b, c, d, d2, e-o)；判分时框架换隐藏 B（4 个 result_* 文件夹：M212CMP_B / M112CMP_B / result_empty_B2 / result_zero_B3，不同信号名/数值）subprocess 真跑验证。
  - a: zip 含 summarize_signals.py ｜ a2: 解压后脚本能定位 ｜ b: py_compile 通过 ｜ c: `--root/--output` exit 0 ｜ d: signal_summary.json 生成 ｜ d2: JSON 含 folders 数组 ｜ e: B 上 4 个 result_* 全识别 ｜ f: M212CMP_B defect_count==3 ｜ g: unique_signal_count==8 ｜ h: unique_signals 集合精确匹配 oracle ｜ i: signal_families 集合精确匹配 ｜ j: M112CMP_B hit/no_hit defect_count==1/1 ｜ k: M212CMP_B total_hit_points==88000 ｜ l: 反硬编码源码无 A 侧信号名 ｜ m: empty B2 不崩溃 defect_count==0 ｜ n: zero B3 no_hit_defect_count==2 total_hit_points==0 ｜ o: 确定性重跑 byte-identical.
- **Anti-hardcode**: A 用 `vss!/vwlp!/vap2!/vcc!/CslMsaq0/CslMsaq1`（可见）；B 用 `vdd2h!/vkb!/WLeL1/WLoL8/BlaMsaq52/vintlp!/NCS7/PCS7`（隐藏，全异）。cond l 源码扫描 A 侧标识符 leakage。
- **Self-verify**: REF PASS 17/17 ✓ / negative_selftest NEG_RC=0 (3 neg + 4 degen 全 FAIL) ✓ / k_rationale=k_check=17≥8 ✓.
- ledger_D: o8obe → case (2026-11-15 05:11).

## r676 exhaustion refutation
- r676 报「D 池 archetype-exhaustion，剩余可做≈0」基于 `find` 超时未定位 session 文件（P-002 路径问题）。本轮 re-triage 发现 **54 fresh mc 10-29 D-purity candidates**（session 文件在 `<sid>/<sid>.messages.json` 子目录，非 sessions 根平铺），refutes r676 exhaustion claim。o8obe 即来自这批 fresh 池。
