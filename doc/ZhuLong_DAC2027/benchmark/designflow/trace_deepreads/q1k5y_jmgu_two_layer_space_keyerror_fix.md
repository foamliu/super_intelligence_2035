# 深读笔记 — 1794900718018_q1k5y (jmgu@hfeg0plg58, mc=114)

## 真实 trace 溯源
- session_file: `1794900718018_q1k5y/1794900718018_q1k5y.messages.json`（目录式 sessions/）
- user: jmgu / host: hfeg0plg58 (10.129.35.82) — 同 home 在 .75 NAS 共享
- match_count: 114 (keywords: drc:301;pdk:134;.gds:74;techfile:38;calibre:15;rtl:7;gdsii:5;.def:4;skipper:1;binary:1)
- 日期: 2026-11-17 ~ 11-19；253 msgs (144 user / 109 assistant)，1.68MB
- domain: physical_verify（drc/pdk/gds/techfile dominant）
- lead agent: deepseek-v4-flash

## 项目背景
jmgu 的 qa-pattern-engine 技能（`/home/jmgu/.cline/skills/qa-pattern-engine/`）基于 35H DBC
工艺的 M3（DRM 称 Mxa）设计规则生成 QA pattern GDS。引擎结构：
- `scripts/run_patterns.py` 顶层入口
- `config/engine_config.json` 层号/grid/unit 配置
- `library/` 15 个脚本家族（same_layer_space / two_layer_space / width_bar / enclosure_via / ...）
- 工作目录 `/home/jmgu/.cline/skills/dr-rule-parser/_m3_work/`
- `calls_v6.json` 112 条规则调用（去重，引擎输入）
- `parsed_mxa/rules.jsonl` 200 条 DRM 解析规则（参数 VERBATIM）
- 输出 `/rundata/lacaa/TV1_DBC/ALS_PDK/drc/jmgu/aiqa/output/`
- `_m3_work/final_verify.py` GDS 二进制原始记录解析（grid/层号/cell 命名校验）

## 用户意图（U#0 交接提示词，单轮主任务）
jmgu 把"收尾执行"任务以交接提示词形式交给下一个 agent：
> 当前卡点：引擎运行到 two_layer_space 家族（CS.1.1.7/1.1.8 等 ladder 模式规则）时报
> KeyError: 'space'。原因：library/two_layer_space.py 的 build() 把
> space = float(p["space"]) 放在 ladder/forbidden 分支判断之前，ladder 模式的 params
> 没有 space 键。
> 修复方法：把该行删除，将 else 分支的 _variant_plan(space, op, grid) 改为
> _variant_plan(float(p["space"]), op, grid)（与 same_layer_space.py 的 build 结构对齐）。

剩余步骤：① 检查/修复 two_layer_space.py ② 跑 run_patterns.py（预期 112 条全 [OK]）
③ 跑 final_verify.py（预期 [PASS]）④ 归档 calls.json ⑤ 交付总结。

已确立约定（勿推翻）：grid=0.0001um；GDS unit=1e-6 precision=1e-10；MINP=y轴 NMINP=x轴；
层号 MxaA(93,482)/MxaB(93,483)/DMxaA(93,490)/DMxaB(93,491)/V2(92,481)/M3_mark1(93,51)/...；
cell 命名 {RULE}_{good|bad} rule_id 前缀 M3.；CS 同色规则 A/B 双色都画。

## agent 实际执行（A#0-A#3+）
1. 并行收集上下文（policy/关键文件在位）
2. `grep -n 'space = float' two_layer_space.py` 确认 line 133 bug 仍在（前序补丁未落盘）
3. 对比 `same_layer_space.py` 正确结构（build() 无预提取行，else 分支内联 float(p["space"])）
4. editor 删除 line 133 `space = float(p["space"])`，else 分支改 `_variant_plan(float(p["space"]), op, grid)`
5. `check_script.py` 验证修复后脚本
6. 跑 `run_patterns.py --calls calls_v6.json --out output/` → 112 条全 [OK]，GDS: M3_qa.gds
7. 跑 `final_verify.py` → [PASS]（grid 0.0001 精确、坐标格点对齐、层号白名单、78+ cell 命名 M3_*）
8. 复制 calls_v6.json → output/calls.json 归档
9. 交付总结

## 关键产物（用于 case reframe）
- **buggy two_layer_space.py**：build() line 133 `space = float(p["space"])` 在 `if p.get("ladder")`/`elif p.get("forbidden")` 分支判断之前 → ladder/forbidden params 无 'space' 键 → KeyError
- **fixed two_layer_space.py**（= reference solve.py）：删除预提取行，else 分支内联 `float(p["space"])`
- **同目录 same_layer_space.py** 是结构参考（184 行，build() 无预提取）
- engine_core 的 `snap(v, grid)` 与 `pair_figure(p, ctx, ori, space)` 是仅有的两个外部依赖，可离线 mock

## 跨 shard 串台检查
- 4-shard ledger: q1k5y 全空（A/B/C/D 均 0）→ session-level fresh
- C.jsonl: jmgu 已有 1 case（DrcQaPatternPlanGen-001 r951 dhgd8 session，不同 session 不同子型）
- 子型 `two_layer_space_ladder_keyerror_fix`（family 脚本 build() 分支前预提取键导致 ladder 模式 KeyError，对齐同目录 reference 家族结构修复）**首例**，与既有 C case 正交

## case 合成（r972）
- task_id: EDA-Eval-DesignFlow-TwoLayerSpaceLadderKeyErrorFix-001
- domain: physical_verify / slug: two_layer_space_ladder_keyerror_fix
- A 输入: two_layer_space_buggy.py + engine_core_mock.py + calls_A.json(6 条 normal/ladder/forbidden/CS/orientation) + task_brief.md
- 隐藏 B: calls_B.json(6 条，layer 名/space 值/ladder items/forbidden ranges/layer_pairs 全不同于 A)
- check.py: 14 条独立断言 a-n，注入 mock engine_core 导入 SUT 脚本，在 B 上跑 build()
- ref solve.py PASS 14/14；3 neg（naive_stub/echo_buggy/print_only）全 FAIL；buggy 版本 FAIL（c/e/f/g/j）
- C.jsonl 570→571
