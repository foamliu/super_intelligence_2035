# attribution_prompt_patches.md — trace 驱动的系统提示补丁设计 (Task B)
> 规格: POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §3. 数据: 36.15 run1 trace (本线 attribution_3615_run1/).
> 纪律: 一次只加一条, 每条单独在 dev 上测 (79/79 train-dev 分层拆分); test 只最后验一次.

## 证据基础 (36.15 run1, 可复算: attribution_analysis_3615_vs_17.json)
- 漏斗: 158 -> code-gen 成功 29(18.35%) -> 通过 25(86.2%) -> overall 15.82%.
- 瓶颈 = code-gen 完成率 18.35%, 不是完成后的判分能力.
- codegen.log 工具调用拒绝 1295 次, 其中 **run_commands 拒绝 1042(80.5%)** (传 string 而非 array); 双 MCP 工具混淆 (把 submit_and_exit 参数传给 eda_flow__open_session).
- submit_and_exit 仅 334 次 (vs .17 6000+), submit 风暴已大幅缓解, 但仍 37 次被拒 (格式错).

## 候选补丁 (按 ROI 排, 一次只加一条)

### P0-tool-format (本轮 trace 新发现, 最高 ROI)
- 要点: 在工具清单段加硬约束 —— `run_commands` 的 `commands` 必须是字符串数组, 每元素一条完整 shell 命令 (禁把多条拼成一个字符串); `read_files` 的 `files` 必须是对象数组; 区分两个 MCP server: `pyAether_MCP_server`(:8090)=API 文档检索 (search_apis/get_api_details/run_code), `eda_flow`(:18891)=沙盒会话 (open_session/run_commands/run_code/...), 两者工具参数不互通, 禁把 submit_and_exit 的 summary/verified 传给 eda_flow 工具.
- 针对失败: run_commands 格式错 1042 + 双 MCP 混淆 (code-gen 完成率低的主因).
- 预期影响: 完成率 18.35% -> 显著上升 (若 run_commands 拒绝砍半, 完成率有望 +10pp 以上); 因完成题质量 86.2%, pass 率有望 +8~15pp.
- 依据: 1295 拒绝里 80.5% 是 run_commands, 直接吞掉模型 turn 预算导致超时/未生成 .py.
- 成本: 0 (改提示文本). 优先级: P0 最高.

### P1-degenerate-guard (spec §3 P1, 针对 .17 残留模式)
- 要点: 提交前必须回读验证 —— 创建类用 get/query 反查数量并打印实际值; 空实现 / 只 return None / 只 print 不建对象 => 禁止 submit.
- 针对失败: degenerate pass (旧 .17 60.63%; 36.15 已大幅缓解但仍需防回退).
- 预期影响: 防止 P0 提完成率后退化提交回潮; +1~3pp.
- 成本: 0. 优先级: P1.

### P2-submit-storm (spec §3 P2)
- 要点: submit_and_exit 每任务 <=2 次; 提交前必须已 run_code 跑通或写明无法验证原因; 连续 2 次被拒 => 停下重读报错原文再改, 禁止原样重提.
- 针对失败: submit 风暴 (.17 13699 次/91.77% 报错; 36.5 已降到 334 但 37 次被拒).
- 预期影响: 释放 turn 预算给真正生成代码, 间接提完成率; +2~4pp.
- 成本: 0. 优先级: P1.

### P3-retrieval-landing (spec §3 P3)
- 要点: search_apis 命中的 API 必须在最终代码出现并经 get_api_details 核过参数; source=bm25_fallback 结果不得直接当 API 名.
- 针对失败: 检索未落地 (.17 overlap 5.7%, 333 API 仅 19 进代码).
- 预期影响: 提完成题的判分通过率 (86.2% -> 更高); +2~5pp.
- 成本: 0. 优先级: P2.

## train/dev 分离 (spec §3 step 4)
- 158 题按 难度+域 分层拆 79 train / 79 dev. 补丁在 dev 上选 (3 seed), 门槛 >= +3pp 且 submit 报错率降 >= 10pp 才进下一轮.
- test = 全 158 题, 仅最后 5-run 验一次, McNemar 对 15.82% 基线检验.

## 顺序建议
1. 先 P0-tool-format (单变量, 直接打 80.5% 的拒绝源) -> dev 测.
2. 叠加 P2-submit-storm -> dev 测.
3. 叠加 P1-degenerate-guard -> dev 测.
4. 叠加 P3-retrieval-landing -> dev 测.
5. dev 选出的组合 -> test 5-run + McNemar.

## ⚠️ 纪律
- 一次只加一条 (否则又回到多变量同时变、无法归因).
- 不改 benchmark / check.py / 题面 / 不挑题 / 不删失败样本.
- 不引用未完成 run (36.15 仅 run1 可用, 5-run 仍跑).
- 反作弊钩子常开并报 cheat.
