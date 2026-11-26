# Deepread · 1793937421846_ip3nr · OscSpDeckMigrateInclude-001

**session**: `1793937421846_ip3nr.messages.json`
**user**: berylwu @ hfeg0plg100 (10.129.8.232)
**match_count**: 195 (schematic_netlist dominant)
**triage source**: r757 keyword-pretriage → r758 ssh-recovered peek → case
**case id**: `EDA-Eval-DesignFlow-OscSpDeckMigrateInclude-001`
**domain**: schematic_netlist
**L-level**: L1 (config-driven generator, offline, no live simulator)
**round**: r758 (2026-11-16)

## 用户真实任务（task初衷）

用户 berylwu 在做 DDR5/LPDDR5 oscillator 相关 SPICE 仿真（`Dlyrc_osc_compare_vdd2h.sp`，路径在 `/proj/commonIP/analog/v1/lp5x/v0/workdir/berylwu/simulation/berylwu_analog_worktb_Dlyrc_osc_sim_schematic_ALPS/Stimulus/`）。需要在新建副本上做两件事：

1. **model 路径全替换**：把所有 `.LIB '/proj/ddgoa/V0/model/current/...'` 改成 `.LIB '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/...'`（迁移到新工艺角 model 目录）。
2. **向每个 trimcode 的 .alter 块插 include**：在每个含 `.param trimcode=...` 的活动 .alter 块里插入一行 `.include ./common/Dlyrc_vint_alter_digital`，并在 `./common/` 下新建这个 include 文件（21 个 PVT .alter 块，每个 .alter 含 .LIB corner + .temp + .param pvcc + .TITLE）。

用户原话逐字（U#67，A 档 trace-faithful，已 mask 无敏感信息——原话本就无 key/token/password）：

> /proj/commonIP/analog/v1/lp5x/v0/workdir/berylwu/simulation/berylwu_analog_worktb_Dlyrc_osc_sim_schematic_ALPS/Stimulus/Dlyrc_osc_compare_vdd2h.sp这个文件，新建一个副本，且里面的model都 更新为/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/，并在每个trimcode的alter里都插入.include ./common/Dlyrc_vint_alter_digital，这个文件没有的话新建一个，.alter 1
> .LIB '/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/model.sp' tt
> ...（21 个 PVT alter 内容，9162 chars，附件 alter_include.txt 全文）

## 为什么是 produce-task（非 Q&A）

用户要的是**生成一个迁移后的 deck 副本 + 一个新建的 include 文件**，是 concrete deliverable，不是解释/分析/诊断。任务本质是「按规则变换 SPICE 文本 + 落地新文件」，属 produce 族。

## 为什么 case 设计成 config-driven generator（非 literal file-edit）

真实任务给的是具体 A 文件（Dlyrc_osc_compare_vdd2h.sp + Dlyrc_vint_alter_digital）。如果 case 让候选直接对 A 文件做字符串编辑，check() 只能验 A，无法在隐藏 B 上验（B 是不同 deck，候选拿不到）。所以 case 把任务抽象成「写一个通用 deck 迁移脚本 `migrate_deck.py`，接受 JSON config 描述 {source_sp, old/new_model_path, include_name, include_content, output paths}」，候选的脚本在 A 上能跑出 A 的迁移结果，在 B 上能跑出 B 的迁移结果——数据驱动可泛化。check() 只在隐藏 B 上跑候选脚本验证 14 条结构/语义/anti-hardcode 条件。

## 隐藏 B 变换（A→B 系统变换，§4.1）

| 维度 | A | B |
|---|---|---|
| old_model_path | `/proj/ddgoa/V0/model/current/` | `/proj/ddax/V0/model/current/` |
| new_model_path | `/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/` | `/proj/ddax/V0/model/current_L6_v1d0_Rev03/` |
| include_name | `Dlyrc_vint_alter_digital` | `Dlyrc_vint_alter_pvt` |
| n_trimcode_alters | 3 | 4 |
| n_pvt_alters (include file) | 21 | 15 |
| pvcc / temp 值 | A 原值 | 不同（系统偏移）|
| 注释路径（不应替换）| `/proj/ddjoc/...` | `/proj/ddxc/...` |

B 与 A 在路径前缀/ddgoa→ddax/版本号/结构数(trimcode 3→4, PVT 21→15)/取值上全不同，硬编码 A 字面者必在 anti-hardcode cond m 失败。

## 14 条 check 条件（a-n）

| cond | 检查 | 负样本击中 |
|---|---|---|
| a | zip 合法 + 含 migrate_deck.py | — |
| b | py_compile 通过 | — |
| c | `python migrate_deck.py config.json` exit 0 | empty(无脚本) 间接 |
| d | output_sp 存在且非空 | **empty→d** |
| e | old_model_path 零残留 | **hardcode_a→e** |
| f | new_model_path 计数 == 5 | **always_ok→f** |
| g | `.include ./common/<inc>` 行 == 4 | **deleted_core→g** |
| h | 每 include 在活动 trimcode .alter 块内 | — |
| i | 零注释 `*.include ./common/` 行 | — |
| j | output_include 含 15 个 .alter | — |
| k | output_sp 以 .END 结尾 | — |
| l | 结构标记保留 (.inc './../netlist'/.global/.tran/.meas tran) | — |
| m | anti-hardcode 无 A 独有串 | — |
| n | determinism 3x 字节一致 | — |

4 负样本 distinct first-fail: {d, e, f, g} = 4/4 distinct ✓。

## 自验结果

- `check.py` selftest: `SELFTEST PASS: reference solution satisfies all 14 conditions` ✓
- `negative_selftest.py`: 4 negatives all correctly FAIL, NEG_RC=0 ✓
- k_rationale = k_check = 14 ≥ 8 ✓

## trace_source 完整性

- user: berylwu（原始用户名，未 hash）
- host: hfeg0plg100 = 10.129.8.232
- session_file: 1793937421846_ip3nr.messages.json
- match_count: 195
- real_task_summary: 见 D.jsonl entry metadata.trace_source

源文件（source.sp / alter_include.txt）经 trace tool_result 恢复（.75 /proj 权限不可直读），全文 verbatim 入 assets。

## 未做

- 未跑 pi/cline 实测（本轮预算耗于 infra 恢复 + 建题 + 自验）
- 未造 i8spy/ccy1n（r757 第十四批 keyword-pretriage 另两条强候选，defer 至 r759）
