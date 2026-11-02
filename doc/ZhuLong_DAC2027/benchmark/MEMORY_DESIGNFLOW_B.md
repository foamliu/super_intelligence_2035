WAITING: 0
SHARD: B (spice_char)
DOMAINS: characterization, spice_sim

- **PHASE**: shard B 在跑 case。负责 domain: characterization, spice_sim
- 每轮做 1 条 case：trace_ledger.py --shard B next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_B.jsonl → 日报
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard B stats
- 🎯 通过率: 0/0（刚启动，未实跑 pi/cline）
- 🧾 断言: k_rationale=k_check=14 ✓（今日 2/30 达标，RsCalcAutoVia-001 + SramSNM-001）

## 流水
- 2026-11-02 15:25 shard B 启动；parked ukkn7（ERC 域误入）；claim+深读 m2vah（e0014566，rscalc+autovia 电阻降低流，mc=975）。
- 2026-11-02 16:0x 交付 EDA-Eval-DesignFlow-RsCalcAutoVia-001（characterization, A档 faithful, L2）：交付 6 文件（gen_rscalc/gen_autovia agent 生成器 + common/rscalc/autovia 配置 + prompt_flow.md），14 条断言（k=14=k_check≥8 ✓），隐藏 B 配置值全不同防硬编码，subprocess 真跑生成器校验内联；ref PASS + 3 negative FAIL + §4.9 三假提交 FAIL。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（现 11 行）。
- 2026-11-02 16:0x 交付 EDA-Eval-DesignFlow-SramSNM-001（spice_sim, B档 synthesized, L2）：6T SRAM butterfly SNM (RNM/WNM/hold) vs cell-VDD 的 HSPICE 表征 harness。trace-faithful 子任务（e0030760 f0vya，mc=410，真实 trace agent 用未镜像 B 曲线致 RNM=0 的 bug）。自包含 level-1 半单元（反相器+access+1e6 负载），扫 VDD，每点 hold/read/write 三条件各 2 VTC deck，镜像 B 曲线 [(qout,qin)] 构造 butterfly，求最大轴对齐内接正方形（Seevinck，公共 q 网格 eye-height）。隐藏 B (W=1.5u/L=0.5u, vto=0.4, kp_n=300/kp_p=100, Rl=5e5, vdd=[0.80,0.70,0.60]) vs 可见 A 全不同。.75 HSPICE 真跑取 GT：B hold 0.3321/0.2407/0.1544, rnm 0.2871/0.2128/0.1357, wnm 0.2342/0.1740/0.1138。14 条断言（k=14=k_check≥8 ✓）。.75 selftest PASS：ref 14/14，3 negs(naive_copy/always_pass/ref_no_core) 全 FAIL，§4.9 三假提交(空壳/print-expected/ref-no-core)全 FAIL，额外 hardcode-expected 假提交被跨输入条件 k 击穿。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（现 12 行）。DEBT 清零。
- 📦 体积：MEMORY_B≈0.9KB
