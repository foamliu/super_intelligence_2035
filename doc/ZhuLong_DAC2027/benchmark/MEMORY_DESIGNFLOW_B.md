WAITING: 0
SHARD: B (spice_char)
DOMAINS: characterization, spice_sim

- **PHASE**: shard B 在跑 case。负责 domain: characterization, spice_sim
- 每轮做 1 条 case：trace_ledger.py --shard B next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_B.jsonl → 日报
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard B stats
- 🎯 通过率: 0/0（刚启动，未实跑 pi/cline）
- 🧾 断言: k_rationale=k_check=14 ✓（今日 1/30 达标，RsCalcAutoVia-001）

## 流水
- 2026-11-02 15:25 shard B 启动；parked ukkn7（ERC 域误入）；claim+深读 m2vah（e0014566，rscalc+autovia 电阻降低流，mc=975）。
- 2026-11-02 16:0x 交付 EDA-Eval-DesignFlow-RsCalcAutoVia-001（characterization, A档 faithful, L2）：交付 6 文件（gen_rscalc/gen_autovia agent 生成器 + common/rscalc/autovia 配置 + prompt_flow.md），14 条断言（k=14=k_check≥8 ✓），隐藏 B 配置值全不同防硬编码，subprocess 真跑生成器校验内联；ref PASS + 3 negative FAIL + §4.9 三假提交 FAIL。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（现 11 行）。
- 📦 体积：MEMORY_B≈0.6KB
