# Deepread: 56vki — space_PLUG → space `forbidden_inside` merge (DRC pattern tool)

- **session**: `1795758425756_56vki.messages.json` (xxchen @ hfeg0plg56, mc=1933)
- **trace_source**: user=xxchen, host=hfeg0plg56(10.129.35.75), session_file=1795758425756_56vki.messages.json, match_count=1933, real_task_summary="merge space_PLUG DRC pattern function into space via {forbidden_inside} switch + GUI bool-checkbox优化 + skill整合"
- **domain**: physical_verify (C shard) — keywords drc:7183 / .gds:280 / calibre:82
- **TOTAL_MSGS**: 1362 (>600 ⇒ 本轮深读 + 下一轮交付 case，依 TASK §3)
- **tool usage**: editor×327, run_approved_command×306, read_files×77, list_allowed_files×19, ask_question×5

## 1. 用户真实意图（user msgs 时序）

1. 阅读AGENTS.md / PROJECT.md（项目 onboarding）
2. **分析宇哲(yzwang)的 space_PLUG 新功能**（`/home/yzwang/workspace/DRC_pattern_tool/0.7/drcpv_develop/`），写分析报告，考虑合并进 space 函数（开关控制更多 pattern 类型）
3. 新增 function 依靠 skill 不是流水线脚本 → 查 skill 改 PROJECT.md
4. 方案C（合并方案）
5. 给出建议：space_PLUG 与 space 对比，新增 `{forbidden_inside True}` 参数实现，消除代码冗余
6. 参数默认不生效 `{forbidden_inside False}`；有些 rule 只需 bad pattern 不需 good；GUI 加 boolean 勾选按钮 → 编写合并方案
7. 把计划写到文档
8. **按计划执行合并**看效果
9. **优化 QA pattern GUI**：boolean 参数改勾选框（非下拉）；TOOL 页面参数名写死在 GUI
10. 一行 3 个勾选
11-14. **优化 QA pattern drcpv function: space**：virtual layer 生成、good/bad pattern 矩形、singular error mark 尺寸(check space value/1.414)
15. 整合 skill：create function skill + debug function skill → maintain function pcell

## 2. case 焦点（选 space_PLUG merge 子任务）

**交付定义**：修改 `drcpv/function/space/simple/space.py`，新增 `forbidden_inside` 开关：
- 默认(switch off/absent)：geometry 与 pre-merge baseline **逐位一致**
- switch on(`{forbidden_inside True}`)：追加 good 9,10（来自 `good_pattern_plug/`，45-deg ABUT<90 on-rule array）+ bad-only 101-105（来自 `bad_only_pattern/`）
- 每个 bad-only pattern **真的违反**(layer1 vs layer2 overlap>0 或 103/105 gap-0 contact) 且带 error mark(layer 4001)

## 3. 可行性（已实证）

- **drcpv tool 在 .75 上**：`/home/xxchen/workspace/DRC_pattern_tool/0.7/drcpv_develop/`（xxchen 在 hfhds201 也有 home，mtime Nov 27 18:26 = POST-merge 状态）
- **gdspy-based**（纯 Python，不依赖 calibre 许可证）→ L2.live 可跑
- **verify script 已存在**：`temp_script_run/_verify_space_merge.py` 完整端到端：
  - `run_cfg(ws,tag,text)` 调 `drcpv/script/qa_pattern_tool.py --config --layer-map --output --log`
  - `pat_nums(names,kind)` 解析 cell 名 `<kind>_<...>_p<N>`
  - `spec_split` / `spec_area` / `overlap_area`(gdspy.boolean "and") 验 bad-only 违反
  - 3 段 check：①default==baseline(gds_norm_sha) ②switch on→good[9,10]+bad[101-105] ③bad-only 真违反+err_mark
- **forbidden_inside 实现**：space.py L110-121(options.get 三拼写兼容) + L463-550(PLUG_GOOD_ROOT/BAD_ONLY_ROOT 追加)

## 4. case 设计草案（下一轮合成）

| 项 | 值 |
|---|---|
| task_id | EDA-Eval-DesignFlow-SpacePlugMerge-001 |
| mode | design_flow |
| domain | physical_verify |
| layer | L2.live（gdspy 真跑 on .75） |
| prompt | 真实场景：xxchen 在 drcpv tool 合并 space_PLUG 进 space 函数，加 forbidden_inside 开关（保留真实用户名/路径/工具） |
| attachments(A) | pre-merge space.py + good_pattern_plug/ + bad_only_pattern/ + layer.map + pattern_common.py + function_common.py + drcpv/script/qa_pattern_tool.py + _verify_space_merge.py 模板 |
| hidden(B) | 不同 layer(如 M1C;markcore->M1C;CORE) + 不同 value/params + 不同 pattern 编号子集 |
| reference | POST-merge space.py（.75 当前态） |
| check_live | 在 .75 跑 qa_pattern_tool on B：①default==baseline sha ②switch on→good/bad 编号集 ③bad-only overlap>0或103/105 gap-0 ④err_mark 4001 present ⑤exit 0 ⑥gdspy cell inventory |
| 断言数 | ≥8（default sha / good nums / bad nums / bad-only 真违反 / err_mark / exit code / cell inventory / switch off 不追加） |
| negatives | (a)空壳 space.py 不变 (b)只 print 期望 cell 名 (c)删 forbidden_inside 分支 (d)bad-only 不违反的 stub |
| judge_layers | ["L0","L1","L2.live"] |

## 5. 待办（下一轮）

1. scp drcpv tool 子集（space/simple/ + drcpv/script/qa_pattern_tool.py + pattern_common + function_common + layer.map）到 assets
2. 取 pre-merge space.py（从 git log 或 BASELINE_CFG 推导；current=POST-merge=reference）
3. 构造 hidden B config（不同 layer/value/params）
4. 写 check.py（非侵入 wrapper：_check_static_impl + check_static + check_live + check）
5. 自验：ref PASS + §4.9 三假 FAIL + negative_selftest
6. 落 cases/C/EDA-Eval-DesignFlow-SpacePlugMerge-001.json + 登记 live_eval_changes.tsv?（非 Lite-502 改造，是 NEW case，登 trace_ledger mark --status case）

## 6. stop-loss 意义

r1241 起止损 rationale「fresh C-domain produce-task 全 techlib-dep stdcell-layout 族」**被本 trace 推翻**：56vki 是 fresh non-techlib C-domain produce-task（DRC pattern tool 开发，gdspy 纯 Python，tool 在 .75），可造 L2.live case。下一轮交付 SpacePlugMerge-001 后，stop-loss 应解除或收窄到「fresh stdcell-layout techlib-dep 族」。
