# attribution_prompt_patches.md — trace 驱动的系统提示补丁设计 (Task B)
> 规格: POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §3. 数据: 36.15 run1 trace (本线 attribution_3615_run1/).
> 纪律: 一次只加一条, 每条单独在 dev 上测 (79/79 train-dev 分层拆分); test 只最后验一次.

## 证据基础 (36.15 run1, 可复算: attribution_analysis_3615_vs_17.json)
- 漏斗: 158 -> code-gen 成功 29(18.35%) -> 通过 25(86.2%) -> overall 15.82%.
- 瓶颈 = code-gen 完成率 18.35%, 不是完成后的判分能力.
- codegen.log 工具调用拒绝 1295 次, 其中 **run_commands 拒绝 1042(80.5%)** (传 string 而非 array); 双 MCP 工具混淆 (把 submit_and_exit 参数传给 eda_flow__open_session).
- submit_and_exit 仅 334 次 (vs .17 6000+), submit 风暴已大幅缓解, 但仍 37 次被拒 (格式错).

## 候选补丁 (按 ROI 排, 一次只加一条)

> ✅ **模板已起草** (2026-11-14 wake503): 每个 pN = `eval_sys_prompt_template_old.md`(36.15 baseline 沙盒提示) + 该补丁的**单一**约束块 (非累积), 落 `run/attribution_prompt_p{0,1,2,3}_*.md`. 设计为**单变量**: round1 各 `--patch pN` 单独 vs `--patch baseline` 在 dev(79) 上测**边际效应**; round2 (选择阶段) 对通过门槛的补丁另建累积组合模板 (如 p0+p2) 再测. 由 `bpt_attribution_prompt_dev_eval.sh` 驱动, `--dry-run` 已在 .17 验证通过 (5 臂 × 79 题, 模板/split/任务数正确).

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
- **round1 (单变量, 各补丁 vs baseline)**: `--patch p0` / `p1` / `p2` / `p3` 分别在 dev(79) 上 3 seed, 各自 vs `--patch baseline` (3 seed). 测每条补丁的边际 Pass@1 增量与 submit 报错率降幅.
- **round2 (累积选择)**: round1 通过门槛 (>= +3pp 且 submit 报错率降 >= 10pp) 的补丁, 按 ROI 叠加 (P0 最高 ROI 先选): 建累积组合模板 (如 p0+p2) 在 dev 上再测; 一次只加一条增量.
- **终局**: dev 选出的累积组合 -> test(全 158) 5-run + McNemar 对 15.82%(/18.99% 订正后) 基线检验.
- ⚠️ 累积组合模板 (如 `attribution_prompt_p0p2.md`) 尚未起草, 待 round1 选定后再建 (避免提前预设组合).

## ⚠️ 纪律
- 一次只加一条 (否则又回到多变量同时变、无法归因).
- 不改 benchmark / check.py / 题面 / 不挑题 / 不删失败样本.
- 不引用未完成 run (36.15 仅 run1 可用, 5-run 仍跑).
- 反作弊钩子常开并报 cheat.
