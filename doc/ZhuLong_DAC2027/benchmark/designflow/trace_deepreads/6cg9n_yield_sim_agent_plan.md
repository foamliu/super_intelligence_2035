# 6cg9n · Yield-Sim-Agent-Plan-Generator (r890)

- trace: `1795055679706_6cg9n` · user e0047547 @ hfeg0pkn003 · NEW-user #24 · mc107 · hspice-dominant
- pool: b_pool_1119 (209 spice-dominant mc≥10) · fresh vs 4-shard normalized ledger (`/tmp/ledger_all_norm.txt`, 3872 sids) · 38 fresh → 1118 池 0 fresh spice 证伪, 池未枯竭
- ledger: `trace_ledger_B.tsv` line 1565 `1795055679706_6cg9n → case (EDA-Eval-DesignFlow-YieldSimAgentPlanGen-001)`

## 意图深读 (139 msgs / hspice-dominant)

用户 e0047547 在 hfeg0pkn003 上要构建一个「良率仿真 AI agent」(`HighSigma` yield-simulation agent), 列了 5 项能力:
1. 自动读取 PDK 模型参数 + 工艺 corner 仿真设置
2. 调用 HSPICE/FineSim/Spectre 多仿真器
3. 解析 .meas/.mt0/.tr0 仿真结果
4. 用 AI 推断参数-良率关系 + 缺陷诊断
5. 输出 HTML 良率报告 + 可复用 skill

关键转折 (msg ~92): 用户说 **"先只把方案文档写好形成 html 放入 /home/e0047547/HighSigma，不要执行待确认后再执行"** — 即把可执行的 EDA 命令 deferred 到人工确认, 仅产出 plan/HTML 文档。

## 不可移植性诊断 (portability-reframe)

原 trace 是真实 GloryEX/HSPICE 环境 (/proj/pdk/... 真实 PDK + 真实仿真), 不可进 SUT 沙箱 (无 license/无 PDK/无仿真器)。但可移植核心是:
**spec JSON (agent 能力 + 仿真任务 + 角色 + depth 选项) → 参数化 HTML 良率仿真方案生成器**

reframe 形态: doc-Q&A/planning → produce 参数化 generator `yield_sim_agent_plan_gen.py`, 读 spec.json → 输出 self-contained HTML 方案文档 (含能力清单/仿真矩阵/角色职责/深度路径/skill 集成/数据归档结构)。harness-for-teeth: spec 必须结构化嵌套, generator 必须真渲染 (jinja-style 字符串拼接 + 真实 section 渲染), stub 必 FAIL。

## 落地

- case_id: `EDA-Eval-DesignFlow-YieldSimAgentPlanGen-001` (spice_sim domain, shard B)
- k_check = k_rationale = **16** (a–p), 断言覆盖:
  - a: HTML 生成且根 `<html>` 标签闭合
  - b: `<title>` 含 spec.agent_name
  - c: capabilities 渲染数 == len(B caps) 且每个含 name+desc
  - d: simulations 渲染数 == len(B sims) 且每个含 tool+corners+goal
  - e: roles 渲染数 == len(B roles) 且含 name+responsibility
  - f: depth_options 全渲染 (key/value)
  - g: skill integration section 存在 (B 是 MCP, A 是 skill)
  - h: data archival section 存在且含 B 路径
  - i: exec-claim 反断言 (HTML 不得出现 "已执行"/"已跑完" 等 exec-claim 子串 — 守住 "plan-only" 意图)
  - j: 反硬编码 A (HTML 不得出现 A-only 仿真器名 alps/silvaco, 不得出现 A-only 角色 "资深设计评审")
  - k: spec → HTML 一致性 (capabilities 数 == B spec 长度, 非硬编码)
  - l: banner 明确声明未执行仿真
  - m: py_compile generator 通过
  - n: determinism — 3 次运行 sha256 一致
  - o: anti-stub — 真实跑生成器 (非 print 静态文件)
  - p: HTML 含 spec 的全 5+ section (caps/sims/roles/depth/skill/data)
- §4.9 negatives (5): empty_gen / hardcode_A / ignore_spec / always_pass / core_deleted — 全 FAIL (NEG_RC=5/5)
- reference: `yield_sim_agent_plan_gen.py` 16/16 PASS, det 3-run sha256 一致
- asset A: `spec_A.json` (trace-faithful: 5 caps, 5 sims incl hspice/finesim/spectre/alps/silvaco, 3 roles incl 资深设计评审, skill integration)
- hidden B: `spec_B.json` (结构性反向: 6 caps 含 PDK-model-import, 4 sims 含 FineSim (无 alps/silvaco), 2 roles (无资深设计评审), MCP integration 非 skill, 不同 depth 路径)

## 关键修正

- 断言 [l] (exec-claim banner) 初版 false-positive: ref HTML banner 原文含 "不包含任何已执行仿真结果" → 子串 "已执行" 触发 EXEC_CLAIMS → 重写 banner 为 "未实际运行任何仿真" (去除 EXEC_CLAIMS 任一子串)。EXEC_CLAIMS = `["已执行","已完成仿真","simulation completed","已跑完","runs completed"]`。
- 重新生成时 generator 的 banner 须避免以上任一子串。

## 选料小结

mc107 hspice-dominant NEW-user e0047547 是 b_pool_1119 的 fresh spice 候选 (1118 池 0 fresh, 1119 池 38 fresh)。trace 139 msgs / ~1.2MB 可一轮闭环。形态: doc-Q&A/planning→produce-generator (harness-for-teeth 第二十八实证 + skill-creation/doc-Q&A→参数化 plan-HTML 生成器第二例, r889 simscan-skill-gen 之后)。
