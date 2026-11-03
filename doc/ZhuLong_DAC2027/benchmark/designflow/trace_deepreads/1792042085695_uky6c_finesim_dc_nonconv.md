# uky6c — FineSim DC 不收敛诊断 (t0002441)

- trace: `1792042085695_uky6c.messages.json` @ hfhds201 (== .75 本机, 本地可读), user `t0002441` (EDA 平台管理员, devops/eda_platform_admin), mc=136
- size 1.27MB / 82 msgs (50 user / 32 asst) / tools: list_allowed_files, search_codebase, read_files, RAG_MCP_Server__search_apis (49 tool_use, 全是 doc 检索, 无 netlist 编辑 / 无 FineSim 实跑)
- 单条 user_input: 「Finesim仿真报DC不收敛的错误, 可能的原因及解决方案有哪些?」(Q&A 咨询, agent 查 FineSim 官方文档 /apps/synopsys/finesim/{201809-doc, P-2019.06-SP2-4/doc} 后系统整理答案)
- sibling: `1792042544705_d1cg3` (同 user 同 prompt, 68 msgs, 同一问题第二次问) — 取 uky6c (首轮) 为 trace_source
- agent 最终答案 (FineSim V-2023.12-1 DC 收敛选项全集, 烤进合成 case 的 fixer 知识库):
  - `.option finesim_dcalg=[0|1|2|3|4]` (SPICE 模式): 0=自动依次尝试, 1=Damped Newton (gmin ramping), 2=Stepping gmin/src, 3=Source stepping, **4=Pseudo-transient (最鲁棒)**
  - `.option finesim_pro_dcalg=[0|1]` (Pro 模式): 0=精度优先(三步: Pre-Init + GPT + DC), 1=性能优先
  - `.option finesim_dceffort=[1|2|3]`: 增大 DC 迭代上限 (500/1000)
  - `.option itl1=value` (默认 200): DC 迭代上限
  - `.option gmin=value` (默认 1e-12; FinFET 1e-15 自动 ×1e-3): 增大 gmin 提升收敛性但降精度
  - `.option finesim_auto_gmin_scale=[0|1]` (默认 1): FinFET 自动 gmin 缩放
  - `.nodeset` / `.ic` 破亚稳态
  - `.option reltol/vntol/abstol` 松弛容差

## 合成 case 设计 (EDA-Eval-DesignFlow-FineSimDcConvFix-001, spice_sim, B档 synthesized, L2)

**子技能 (distinct vs 已有 B FineSim case)**:
- gvm3g = FineSim 'can't find model'(`.model ./` 语法) → 去 `./` 前缀
- hk622 = FineSim 'no reference ckt'(X 实例引用 .subckt 缺失) → 注入 spf include
- cllpy = FineSim 'cannot open include'(RCC 路径) → 重排 var_osc
- **本条 = FineSim DC 不收敛(非线性/双稳态/无 nodeset) → 注入 DC 收敛选项 (`.option finesim_dcalg=4` + `gmin` + `itl1` + `.nodeset`)** (第四种 FineSim 失败模式 + 不同修复动作, distinct ✓)

**候选 fixer.py** (CLI <assets_dir> <out_dir>):
1. 跑 FineSim 原始 B dut.sp → 解析 .log 找 DC 不收敛标记 (`non-converg` / `dc convergence failed` / `did not converge` / `pivott` / `gmin ramping` 失败)
2. 注入 DC 收敛选项 (name-agnostic, 紧跟 `.option` 块后): `.option finesim_dcalg=4` + `.option gmin=1e-10` + `.option itl1=500` + `.nodeset <双稳态节点> 0`
3. 重跑 FineSim → 验证 DC 收敛 (`Successfully Completed` + 无 non-converg)
4. 写 diagnosis.json (orig_status, missing/convergence_error, fix_applied[]) + fix_report.json (fixed, rerun_status)

**核心陷阱烤进 check.py (≥8 条 a-n)**:
- (c) fixer.py 含 DC 不收敛日志解析标记 (证明真解析 log, 非硬编)
- (d) name-agnostic — 不含 A/B 节点名/模型名字面量
- (e) fixer 真跑 FineSim (subprocess)
- (f)(g) B diagnosis 含 convergence_error==True 且 fix_applied 含 dcalg/gmin/itl1/nodeset 中 ≥2 类
- (h) 判分器独立重跑 FineSim 于 B dut_fixed.sp 得 'Successfully Completed' 且无 'non-converg'
- (i) sanity 判分器跑原始 B dut.sp 必含 'non-converg' (bug 确实存在, 防 always-pass)
- (j)(k) B 收敛后提取 DC op (v(q)/v(qb) 等) 匹配真值 (跨输入守卫)
- (l) 跨输入守卫 |B-A|/A>5% (naive_hardcode_a 硬编 A 值 → B 击穿)
- (m) fix_report.fixed==true 且 rerun_status=='Successfully Completed' (naive_no_rerun 删核心 rerun 击穿)
- (n) 判分器重跑产真实 FineSim 输出文件

**A/B GT (.75 真跑 FineSim, 待 license 恢复)**:
- A: 双稳态交叉耦合反相器对 (SRAM 单元, 无 .nodeset) → orig DC non-converge → fixed dcalg=4 收敛 → op q=0/qb=vdd (或镜像)
- B: 不同 sizing/VDD/拓扑 (如 3 级反相器环形振荡器 + 无 .nodeset, 或 Schmitt 触发器) → orig non-converge → fixed 收敛, 跨输入 op/拓扑全不同

## ⚠️ 本轮阻塞 (真外部)

1. **FineSim license outage on .75**: `finesim test_nofix.sp` → `WARNING! no valid license(-8)! License to run is temporarily unavailable. Waiting for license to check in` (FineSimPro V-2023.12-1, hfhds201, 2026-11-04 06:29). 同 1fgo2 ledger 记录的 "run_code queue jammed" / FineSim 不可用阻塞。本 case 必须用 FineSim (trace 的选项 `finesim_dcalg` 等 FineSim 专有, HSPICE 无 1:1 对应)。
2. **HSPICE 移植尝试 (备选) 失败**: 在 .75 HSPICE V-2023.12-SP1-1 实测 3 种 DC 非收敛触发器 (t1 交叉耦合反相器 gmin=0, t2 floating-gate amp gmin=0, t3 高增益 3 级开环 gmin=0+reltol=1e-9+itl1=50) — **全部 `dc convergence successful`** (HSPICE 自动 symb=1 / gmin handling, 太鲁棒)。HSPICE DC solver 难以快速逼出 non-convergence, 需更多拓扑迭代 (Schmitt / 高增益比较器 / 更极端 itl1) 超本轮预算。

→ 本轮交付: deepread + case 设计 + .75 触发器实测 (实质性工作, 非只深读)。case 未合成、未进 jsonl、未 mark case。DEBT:1。
→ 下轮第一件事: **交付 uky6c case**。先重试 FineSim license (若恢复 → 立即合成 A/B + fixer + check + selftest + jsonl); 若仍 down → 构造可靠 HSPICE non-convergence 触发器 (Schmitt 触发器 / 高增益开环比较器无 .nodeset + gmin=0 + 极低 itl1) 移植, 或换 FineSim P-2019.06-SP2-4 版本试 license。

## 台账
- uky6c → deepread (2026-11-04 06:33)
- d1cg3 sibling 不另 claim (同 prompt 同 user, uky6c 已代表)
