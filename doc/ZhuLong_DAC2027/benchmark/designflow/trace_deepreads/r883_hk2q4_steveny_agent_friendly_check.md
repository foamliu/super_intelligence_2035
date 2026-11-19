# deepread: 1794892256265_hk2q4 — steveny @ hfeg0pnd001 (CAD team, agent-friendly CAD source)

- sid: 1794892256265_hk2q4
- user: steveny / host: hfeg0pnd001 (10.129.32.189) / mc=202
- keywords: netlist:1670; aether:736; hspice:396; schematic:249; pyaether:177; verilog:173; cellview:104; virtuoso:57
- trace: 249 msgs (110 assistant, 139 user), 992KB, 2026-11-17

## 用户真实意图（verbatim）

steveny 是 **CAD team 成员**，讨论 CAD 源码对 agent 是否友好，最终要做出可分发的 skill + 评分器给 CAD tools owner：

- U[2]「导一个网表为什么要四个cad tools」
- U[3]「这些源码对agent 友好吗？或者说怎样的源码或是工具，是对agent友好的？我们讨论一下」
- U[4]「我就是cad team的成员，准备做4，但是需要给出清晰到需求，并附带培训，因为大家不知道"好"是怎样的，也不知道怎么做好」
- U[5]「裸except会有什么问题？」
- U[6]「很棒，我感觉需要做成skill，然后发给cad tools owner，你怎么看」
- U[7]「注意，skill是给cad tools owner用和看到，注意内容」
- U[8]「提交到git」

## agent 实际做了什么

agent 实读 465 个 PyAether `.py` + 615 个 SKILL `.il`，量化出 CAD 源码「对 Agent 中等偏不友好」的反模式分布（250/465 零输出文件、254 处裸 except、1193 处 os.system、843 处 global、137 文件 GUI/逻辑混在一起、单文件最大 4060 行、`ln -snf aether.rc` 被 25 文件用来切状态）。交付两件东西：
1. `contexts/eda_agent/agent_friendly_guideline.md` — 规范 + 培训讲稿，六条硬底线（P0-1 入口结构化返回 / P0-2 查算写分离 / P0-3 禁裸 except + shell 统一执行器 / P0-4 配置显式化禁软链切状态 / P1-5 GUI 与逻辑分层 / P1-6 命名与规模 ≤800 行），每条都引用团队自己的代码当反面教材。
2. `tools/eda_agent_friendly_check.py` — 只读评分器，扫 `--root` 度量六条规则，`--json` 可接 CI。

## 合成决策（harness-for-teeth reframe 第二十四实证）

真实任务形态 = doc-search + Q&A + how-to + skill-creation（按 2026-11-15 重审令全部合法）。判分要"有牙"⇒ reframe 成 **produce 参数化静态分析器**：SUT 看 `src_a/`（真实结构样例树）+ `expected_result_A.json`（A 的标准答案），产出 `eda_agent_friendly_check.py`，在**没见过的 hidden B**（不同子目录 pex/sim/cfg/gui/util/skill vs A 的 se/hi/ut/le，不同文件名，不同模式密度，9/11 metrics 不同）上跑出 JSON，判分独立复算 7 个关键计数逐一核对 + score 六条 verdict 口径 + 反硬编码 A + 确定性 + 反 stub。

- domain: spice_sim（CAD 源码是 hspice/netlist 导出工具链）
- layer: L1（纯文件 os.walk + re 静态分析，无 EDA 仿真）
- k_check = k_rationale = 15(a-o)，5 neg 全 FAIL，ref 15/15 PASS E2E
- asset A = format-faithful（真实 Aether `python_ae/` 子目录 se/hi/ut/le + SKILL `.il`，反模式 + 正面样板 `export_hspice_good.py`）
- hidden B = 结构性反向（pex/sim/cfg/gui/util/skill 子目录，命名方向相反，密度不同）
- 关键修正：行锚定正则 `except:`/`global ` 必须用 `re.MULTILINE`，否则多行文本匹配不到（常见坑，写进 task_spec 提示）
