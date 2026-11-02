WAITING: 0 (本轮交付 StimPWL-001；DEBT: 1 — djml8 deepread 未合成 → EDA-Eval-DesignFlow-PFDdeadZone-001，下轮先合)
SHARD: B (spice_char)
DOMAINS: characterization, spice_sim

- **PHASE**: shard B 在跑 case。负责 domain: characterization, spice_sim
- 每轮做 1 条 case：trace_ledger.py --shard B next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_B.jsonl → 日报
- 📊 trace 覆盖率：9/1001 = 0.9%（covered=9 / target=1001, mc≥300）；已动 13：case 9 · deepread 2 · parked 2
- 🎯 通过率: 0/0（刚启动，未实跑 cline）
- 🧾 断言: k_rationale=k_check=15 ✓（今日 3/30 达标，RsCalcAutoVia-001 k=14 + SramSNM-001 k=14 + StimPWL-001 k=15）

## 流水
- 2026-11-02 15:25 shard B 启动；parked ukkn7（ERC 域误入）；claim+深读 m2vah（e0014566，rscalc+autovia 电阻降低流，mc=975）。
- 2026-11-02 16:0x 交付 EDA-Eval-DesignFlow-RsCalcAutoVia-001（characterization, A档 faithful, L2）：交付 6 文件（gen_rscalc/gen_autovia agent 生成器 + common/rscalc/autovia 配置 + prompt_flow.md），14 条断言（k=14=k_check≥8 ✓），隐藏 B 配置值全不同防硬编码，subprocess 真跑生成器校验内联；ref PASS + 3 negative FAIL + §4.9 三假提交 FAIL。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（现 11 行）。
- 2026-11-02 16:0x 交付 EDA-Eval-DesignFlow-SramSNM-001（spice_sim, B档 synthesized, L2）：6T SRAM butterfly SNM (RNM/WNM/hold) vs cell-VDD 的 HSPICE 表征 harness。trace-faithful 子任务（e0030760 f0vya，mc=410，真实 trace agent 用未镜像 B 曲线致 RNM=0 的 bug）。自包含 level-1 半单元（反相器+access+1e6 负载），扫 VDD，每点 hold/read/write 三条件各 2 VTC deck，镜像 B 曲线 [(qout,qin)] 构造 butterfly，求最大轴对齐内接正方形（Seevinck，公共 q 网格 eye-height）。隐藏 B (W=1.5u/L=0.5u, vto=0.4, kp_n=300/kp_p=100, Rl=5e5, vdd=[0.80,0.70,0.60]) vs 可见 A 全不同。.75 HSPICE 真跑取 GT：B hold 0.3321/0.2407/0.1544, rnm 0.2871/0.2128/0.1357, wnm 0.2342/0.1740/0.1138。14 条断言（k=14=k_check≥8 ✓）。.75 selftest PASS：ref 14/14，3 negs(naive_copy/always_pass/ref_no_core) 全 FAIL，§4.9 三假提交(空壳/print-expected/ref-no-core)全 FAIL，额外 hardcode-expected 假提交被跨输入条件 k 击穿。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（现 12 行）。DEBT 清零。
- 2026-11-02 16:25 深读 djml8（wnyu, mc=401, 996 hspice）：PLL PFD 死区表征——扫 ref/fb 相位偏移 [-400:20:400]ps，每点 tran 测 avg(v(up)-v(dn))，死区=avg≈0 的相位窗（≈复位路径延时）；多 corner(0.82/0.85/0.88 × TT/SS/FF/FS/SF)。真实 trace 用 FineSim + CXMT foundry PFD_rvt 网表（不可移植）。计划 EDA-Eval-DesignFlow-PFDdeadZone-001（spice_sim, B档, L2）：自包含 level-1 tri-state PFD（2×DFF+AND 复位，MOS 门级），死区宽度随门延时（W/L,VDD）缩放→跨输入守卫。已 mark deepread，claim 保留；合成留待下轮（先 .75 建网表确认死区 GT，再写 check.py）。深读笔记：designflow/trace_deepreads/djml8_pfd_deadzone.md
- 2026-11-02 16:3x 交付 EDA-Eval-DesignFlow-StimPWL-001（spice_sim, B档 synthesized, L2）：trace 13fwy（thqu @ hfeg0plg99, mc=211）从 WaveView SPICE PWL 导出(si1/si2/si3.sp)抽 LPDDR5 ddgoa R_NegVssIdd_opt_qyh 输入激励。交付 gen_stimulus.py（读 si1/si2/si3.sp + signal_map.json → stimulus.sp + report.json，内嵌 toy testbench 跑 HSPICE 量半 VCC 翻转时刻）。15 条断言（k=15=k_check≥8 ✓）：结构/编译/真跑 hspice/8 V 源(7 设计输入)/忠实 PWL 点数搬运/紧凑 pwl/DC 2.71/翻转时刻≈GT/跨输入 A≠B/确定性。隐藏 B 翻转时刻整体偏移(GrEn 10n→25n 等)+PWL 点数不同(40→50/36→44/32→38)。.75 HSPICE 真跑自验：ref 15/15 PASS（GrEn 翻转 A=10n/B=25.05n 与 GT 吻合）；3 negative(naive_hardcode/always_dc/truncated) 全 FAIL；§4.9 (a)空壳/(b)print-expected/(c)删 hspice 核心 三假提交全 FAIL（ref-no-core 被真跑条件 d/e/m/n 击穿）。备注：真实 si*.sp 属 ddgoa 项目组权限不可读(permission denied)，资产按 WaveView PWL EXPORT 原格式合成（故 B档 synthesized）。已 mark case，追加 EDA-Eval-DesignFlow_B.jsonl（第 13 行）。
- 📦 体积：MEMORY_B≈1.2KB
