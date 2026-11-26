# 判分契约改造 · shard A 进度 (r1271 起 · 2026-11-26)

> 指南：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`
> 心跳格式：`CONTRACT: P1=<done>/<12> · P2=<n> L2.live · P3=<n>/<total> judge_layers`

## 总览 (r1271)

shard A 共 585 cases:
- **P1 (pilot 12)**: 4/4 done (FindPcells-001 / PyAetherCurDesignApi-001 / RtlDesignScenarioBoot-001 / -v2) — r1270 verify + check_live upload-robustness fix; ref L0+L1+L2.live all PASS on .75 (hfhds201, eda_flow MCP 秒级). 指南表标 A 的 PowerFillMergeGen-001 / RsCalcChkPtGen-001 实际在 cases/C/ (domain=layout_virtuoso ⇒ shard C, 已有 judge_layers=[L0,L1,L2.live]) — 指南表 shard 标 A 系误标, A 未碰.
- **P2 (扩展真 EDA case 到 L2.live)**: 0 done / 3 候选待做 (见下)
- **P3 (mock case 声明 judge_layers)**: 582/585 declared (577 [L0,L1] + 5 [L0,L1,L2.live]); 3 P2 候选留 undeclared

## P1 详情 (r1270)

| case_id | judge_layers | check_live | check_static | test↔check.py | ref L2.live |
|---------|-------------|-----------|--------------|--------------|------------|
| FindPcells-001 | [L0,L1,L2.live] | ✅ | ✅ | ✅ sync | ✅ PASS |
| PyAetherCurDesignApi-001 | [L0,L1,L2.live] | ✅ | ✅ | ✅ sync | ✅ PASS |
| RtlDesignScenarioBoot-001 | [L0,L1,L2.live] | ✅ | ✅ | ✅ sync | ✅ PASS |
| RtlDesignScenarioBoot-001-v2 | [L0,L1,L2.live] | ✅ | ✅ | ✅ sync | ✅ PASS |

r1270 修 check_live upload-robustness: FindPcells+PyAetherCurDesignApi 原 sess.upload(deliverable) 默认 remote_name=basename; 真实 eval 传 deliverable='submit.zip' 可过, 自验传 reference_submit.zip 致 unzip exit9; 改 sess.upload(deliverable,"submit.zip") 显式定名 (真实 eval 行为不变, 自验亦通). 未碰 _check_static_impl 断言.

## P2 候选池 (待做)

扫描所有 shard A case 的 check code (reference/check.py + inline test 字段), 按是否真调 EDA 工具分类:

### 强 P2 (check.py 经 subprocess 真跑 EDA 工具, 需 L2.live) — 3 条
| case_id | tools | size | 状态 |
|---------|-------|------|------|
| Digital-023 | vcs, verdi | 9803 | 待做 |
| InnovusLaunchDiag-001 | calibre, verdi, innovus | 14581 | 待做 |
| VcsMkfileSimDiagnoseProduce-001 | vcs, verdi | 10632 | 待做 |

### 假阳性 (pyAether/EDA 关键词出现在 stub 或 inlined log, 实为 mock) — 2 条 → 已归 P3
- DecoderSchemGen-001: check.py 用 StubAE 注入 sys.modules['pyAether'] (mock 判分), ae-api-call 指标系 StubAE.aeGetCurDesign 定义误匹配
- GgFlowReport-001: pyAether 出现在 inlined LOG_A/LOG_B 字符串 (候选 group_generate.py 的日志), check.py 自包含 subprocess mock

### text-only sim-keyword (hspice/finesim/virtuoso 仅出现在 netlist 文本/注释, 非 subprocess 调用) — 139 条 → 已归 P3

## P3 详情 (r1271)

- 声明 `judge_layers=["L0","L1"]` on **462** mock cases (commit `877b8523c`, EDA-Flow-Bench master)
- 行为保持: 框架对 `["L0","L1"]` + 旧式 `check()`/`check_static` 走 fallback, L2.live 不触发 → 与改造前 (空 judge_layers) 完全一致
- 回归验证: stash 原版 vs 声明后版, 同一 ref self-test 产出相同 verdict (FAIL 系 self-test env 不完整 hidden-B/assets, 非回归; judge_layers 声明本身纯 metadata, check.py 一字未改)
- 排除: 3 条真 EDA subprocess P2 候选留 undeclared (待 P2 加 check_live 后升 [L0,L1,L2.live]); 5 条已 L2.live 不动; 115 条 r1269 已声明不动

## 心跳

`CONTRACT: P1=4/4 done(A) · P2=0/3 L2.live (3 真-EDA 候选待做: Digital-023/InnovusLaunchDiag-001/VcsMkfileSimDiagnoseProduce-001) · P3=582/585 judge_layers declared`
