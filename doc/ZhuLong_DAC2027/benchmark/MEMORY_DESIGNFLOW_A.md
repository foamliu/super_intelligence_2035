WAITING: 1
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: shard A 新 case 合成阶段。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：trace_ledger.py --shard A next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_A.jsonl → 日报
- ⚠️ DEBT: 1 deepread 未合成 —— `EDA-Eval-DesignFlow-TimingECO-001`（1792572733650_pfubi，PrimeTime TimingECO flow，L2/L3）。深读+金标准+隐藏B 全部 .75 真跑验证通过；**下轮第一件事**：写 check.py(≥8 断言) + reference/ + negative/ + self-verify + 追加 jsonl + mark case。lib 已缓存 `/home/e0031982/teco_case_lib/core_typ.db`。
- 📊 trace 覆盖率：9/1001 = 0.9%（covered=9 · case 9 · deepread 1 · parked 1）
- 🎯 通过率: 0/0（A 档尚未实跑）· B 档目标 20–30%
- 🧾 断言: k_rationale=k_check 达标（断言债已清零，存量 9 条全达标）
- 📦 体积：TASK≈17KB / MEMORY≈待测

### 2026-11-02 shard A 轮 7：TimingECO-001 深读+金标准+隐藏B 验证 ✓（DEBT: check.py 待写，下轮首事）
- 选料：trace_ledger.py --shard A next → 在 .75 summary.tsv 按 shard A tools（dc_shell/primetime/innovus/voltus/genus/icc2/tempus/synthesis）排序找数字/PnR/verif 候选。pfubi(mc=153) 因首次 ssh 路径误判（session 是目录 `1792572733650_pfubi/` 含 messages.json，非直接文件）一度 parked，定位正确嵌套路径后重新 mark deepread。lond8/lorikx 同 host 6 节点全 MISSING（NFS 不一致）弃。最终选 `1792572733650_pfubi.messages.json`（e0046913/hfeg0plg52, mc=153, primetime:213 icc2:194）—— PrimeTime TimingECO flow 构建真设计流（agent=lead, 253msgs, 1.34MB）。claim domain=verification。
- 深读：scp 整条 messages.json 到 .75，解析 253 msgs。用户真实意图（USER[17/18]逐字）：模仿已建 STA_flow 结构（run/cshell + scr/编号tcl 1_setup..10_rpt + setup/data/sdc/log/rpt/session/patch），在 TimingECO_flow 构建 Top Timing ECO flow（signoff→ECO patch→re-signoff），demo 跑通。assistant 真跑 pt_shell 探针 v1-v5 找 lib cell（clk1b27/clk1a27/fdf1a3），editor 建完整 flow 11 个编号 tcl + run_eco.csh(选项化) + run_demo.csh(3阶段自检) + README。
- 金标准（.75 真跑 pt_shell U-2022.12-SP5 验证 2026-11-02 15:00）：A(eco_demo, 2-flop fdf1a3, period6.0/hold_unc0.50, corner tt0p8v25c) signoff HOLD_VIOL=4 SETUP_VIOL=0 → eco fix_eco_timing -type hold 插 4×clk1a27 buffer → re-signoff post.summary HOLD_VIOL=0 SETUP_VIOL=0 CLEAN；run_demo.csh exit0 打印 "TimingECO demo PASS"。教程库 core_typ.db(4.4MB) 已缓存 `/home/e0031982/teco_case_lib/core_typ.db`。
- 隐藏 B（.75 真跑验证 15:01，结构性不同）：eco_demo_B 3-flop 移位寄存器（vs A 2-flop），period4.0/hold_unc0.60，corner ss0p7v125c。B signoff HOLD_VIOL=6（vs A 4）→ eco 插 9×clk1a27 buffer（vs A 4）→ post.summary HOLD_VIOL=0 CLEAN。B 与 A 拓扑/违例数/buffer数/corner 全不同，击败硬编码 A。
- 已写本地 assets：data/eco_demo/eco_demo.vg + sdc/eco_demo.sdc + user_request.md(用户逐字) + hidden/eco_demo_B/{vg,sdc} + hidden_manifest.json。深读笔记 designflow/trace_deepreads/pfubi_timing_eco_flow.md（含 check.py 14 条断言设计 a-n + 5 负样本规划）。
- ⬜ DEBT（下轮第一件事）：写 reference/EDA-Eval-DesignFlow-TimingECO-001/check.py（14 独立标签 a-n，真跑 pt_shell on A+B）+ reference 解（gold flow scripts + reference_submit.zip）+ negative/(3§4.9假+2naive) + negative_selftest.py + 自验(ref PASS + 三假 FAIL) → 断言闸门(k=14≥8) → 追加 EDA-Eval-DesignFlow_A.jsonl → mark case → 日报。下轮：WAITING: 0（交付后）。
