# Shard B 契约改造记录（contract_reform_B.md）

> 本文件记录 shard B（spice_sim / characterization）判分契约改造进度。
> 优先级：P1 > P4(只读分析) ≈ P2 > P3。

## 总览

- **P1（pilot 12 case）**：N/A — pilot 12 case 全在 shard A/C/D，B 无 P1 工作。
- **P2（扩展 L2.live）**：见下方 P4 分析结论。B 600 case 全为 self-contained mock/static 判分，
  无 case 判分本质依赖 .75 真跑 EDA → **P2 候选 = 0**（r1258 初判 + r1264 P4 本质问复核一致）。
- **P3（mock case 声明 judge_layers）**：✅ 600/600 完成（r1258，全 B case metadata 加
  `judge_layers=["L0","L1"]`，纯 metadata 增量，未碰 test/prompt/assets；框架旧式 check() 回退兼容）。

---

## P4 实跑适合性分析 (r1264 · 2026-11-26)

本 shard Lite-500 case 数: 130（B Lite 集，eval/cases_lite.txt ∩ cases/B/）

### 判定方法

逐 case 读 case JSON 的 `prompt` + `test`（check.py 快照），用 P4 核心一问判定：

> 「如果 candidate 的输出能让 check.py 的文本断言全过，但 EDA 工具实际跑不起来/结果全错，
>   这个 pass 算不算数？」

并辅以自动化信号扫描（subprocess / hspice / finesim / pyAether / mock-body / 真二进制调用 /
`/rundata` 依赖），对 19 条「引用 hspice/finesim 但无 `_ensure_*` mock 标记」的疑似 case 逐条深查
`subprocess.run([...])` 调用对象（是真调 simulator binary 还是只跑 candidate `.py`）。

### 结论分布

| 档位 | 数量 | 说明 |
|------|------|------|
| T1 适合实跑 | 0 | 无 case 判分本质依赖真实 EDA 执行产物（详见下方论证） |
| T2 可选增强 | 1 | LisMeasExtract-001（已有 real-hspice 路径+fallback，可在 .75 启用真跑） |
| T3 不适合 | 129 | 保持 mock/static 判分，不改 L2.live |

### T1=0 的论证

B shard 130 条 Lite case 全部遵循同一设计范式 —— **「自包含可复现子技能」harness**：

1. **prompt 明示 foundry PDK / 真模拟器在 eval 环境不可用**，要求 candidate 把真实 trace 中的
   「可复现子技能」抽成 self-contained harness（deck 生成器 / 解析器 / 诊断器 / 表征流脚本）。
2. **check.py 的判分对象是 candidate 产物的结构正确性**，不是「在真实 PDK 上跑出某条波形」：
   - 63 条 `script_only`：subprocess 跑 candidate `.py`，断言其输出（CSV/JSON/deck 文本）结构。
   - 47 条 `sim_mock`：check 内嵌 deck-driven mock（`_ensure_hspice`/`_ensure_finesim` 安装 stub
     到 PATH），mock 按 candidate deck 内容返回 .75 上真跑捕获的 GT `.mt0` 值。mock 对 deck 结构
     的校验（pin order / `.measure` / `.param` / `.tran`/`.dc` spec）比 bare syntax check 更严。
   - 19 条疑似「real_eda」：18 条经深查确认 `subprocess.run` 只跑 candidate `.py`，hspice/finesim
     字样仅出现在任务描述 / 注释 / 被解析的 deck 文本里，**无一条真调 simulator binary**。
3. **核心一问回答**：对 sim_mock 类，若 candidate deck 能过 mock 的结构断言但真 hspice 会因语法
   报错 —— 该 pass 仍算数，因为任务意图是「harness 正确实现了表征/解析流」（arc 枚举 / conditioning /
   measure 语法 / pin order），mock 已忠实校验这些；真 hspice 跑不起来是环境问题（GLIBCXX / PDK 缺失），
   非 harness 正确性问题。对 script_only 类，candidate 产物是脚本/文本，根本不涉真跑 → 文本判分够用。
4. **mock 忠实性**：47 条 sim_mock 的 GT 值全部来自 .75 真跑捕获（check.py 注释明示
   `Embedded ground truth (from .75 HSPICE ref runs)`），mock 是真模拟器的功能等价物 ——
   即使改 L2.live 真跑，结果与 mock 一致，判分结论不变 ⇒ 无判分增益。

⇒ **B shard 无 T1 case，P2 候选 = 0**。与 r1258 初判一致；P4 本质问复核覆盖全量 130 条（非仅关键字池），
未发现漏判。

### T1 清单（优先改造顺序）

无。

### T2 清单

| case_id | domain | 可加什么 L2.live 辅助断言 | 工作量 |
|---------|--------|--------------------------|--------|
| EDA-Eval-DesignFlow-LisMeasExtract-001 | spice_sim | check.py 已有 `_run_hspice_b()` 真跑路径（`subprocess.run([hsp,"-i",stimB.sp,...])` + `ran_real` 标志 + pre-captured `.lis` fallback）。eval host 无 hspice → 走 fallback。改 L2.live 可在 .75（hspice 在 PATH）启用真跑路径，产 fresh `stimB.lis` 替代 fallback。**但**：判分对象是 candidate 对 `.lis` 的解析正确性，`.lis` 内容真跑/fallback 等价 → 判分结论不变，仅增强「输入数据真实性」。低判分增益。 | S(<1h) |

**T2 自决结论**：LisMeasExtract-001 改 L2.live 判分增益极低（输入数据等价，非判分依赖），
本轮 **不改**，保持 mock/static 判分。若后续需示范 B shard L2.live 通路可单独立项。

### T3 不适合（129 条 · 不逐条列出）

构成：63 script_only + 47 sim_mock + 1 text_only + 18 疑似 real_eda（经深查确认只跑 candidate `.py`）。
共同特征：判分对象 = candidate 产物结构（脚本输出 / deck 文本 / 诊断报告），mock/embedded-GT 忠实
复现真模拟器结果，真跑无判分增益。保持现有 `judge_layers=["L0","L1"]`（P3 已声明）。

---

## 下一轮计划

- P4 分析已完成（T1=0 / T2=1 自决不改 / T3=129）→ B shard 契约改造全闭合（P1 N/A · P2=0 · P3 ✅ · P4 ✅）。
- 无 P1/P2/P3/P4 待办。回归 Lite 轮转抽检 re-verify（holding 模式），待 zhulong 重建 trace_ledger
  next 通路或扩 mc≥5 池注入新料后再造新题。
