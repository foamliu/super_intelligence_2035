# r610 deepread — xxchen vpabb (corner-to-corner space bad pattern 2 fix)

- session: 1794531720896_vpabb
- user: xxchen @ hfeg0pkn001 (10.129.2.10)
- mc: 184 (drc:420, .gds:101, pdk:5, dbcreatepath:2)
- agent: lead
- msgs: 109 / 2 user_input
- tools: read_files 24, editor 12, run_approved_command 11, list_allowed_files 7, ask_question 1
- ledger: r547 parked "xxchen known-reject modify-existing" → r610 revive (2026-11-15 令: modify-existing 现合法 = B类误杀)

## UI#0 (idx0): setup
`阅读AGENTS.md / 阅读PROJECT.md` (context bootstrap)

## UI#1 (idx10): 核心 produce-task (原文)
```
### QA pattern debug: PW_S_008_00_c
QACELL  PW_S_008_00_c  space  Pguardring->NMOS_thin  0.4  {layer1width 3.0} {layer1length 5.0} {w 2.0} {l 1.0} {layer2_device ACTIVE} {auxRegion CORE}
产生的bad pattern 2 的 space 属于 corner to corner 的距离 明显大于0.4，
记住通用：按照EDA工具corner之间的距离只计算欧几里得圆弧形，corner同斜边一样使用2倍的grid误差来设置bad pattern.
```
→ 提需求（指出根因 corner-to-corner + 给通用规则 corner=2x grid），未给修复代码 = A档合格 produce-task modify-existing。

## 根因（agent 诊断）
- NMOS_thin ACTIVE bbox 1.16×2.0 (in_x0=-0.58, in_x1=0.58, in_y0=-1.0, in_y1=1.0)
- 旧 pattern2.py: `off=0.5*l1w=1.5`, `pw_x0=-0.58+1.5=0.92` 完全越过 ACTIVE 右缘 0.58
- → 无水平重叠，最近点 = ACTIVE 右上角 ↔ PWx 左下角 corner-to-corner
- 旧 `s_bad=value-checkStep=0.4-0.0001=0.3999` (vertical gap) 不再控制，实测 `sqrt(0.34²+0.4²)≈0.525>0.4` → bad 图形不报 DRC 错

## 修复 (pattern2.py 重写)
- 控制量 = corner-to-corner 欧几里得距离 `target = value − 2×grid`（通用规则：corner 同斜边用 2x grid）
- `off=0.5*l1w`, `dx=(in_x0+off)-in_x1` (X 分离)
- clamp: `if dx>=target: dx=0.5*target` (X 单独超距不可解时)
- `dx=snap(dx)`, `dy=snap(sqrt(target²−dx²))`
- PWx@(in_x1+dx, in_y1+dy)，角距恒 <value (violation)
- highlight 围 corner gap; update_history.md + lessons.md 记通用规则

## 验证 (qa_pattern_tool exit 0, 34 cells)
| cell | bad p2 角距 | 判定 |
|------|-----------|------|
| PW_S_008_00_c | 0.3998 < 0.4 | 真违规 (原~0.525) |
| PW_S_008_00_p | 0.6148 < 0.615 | 真违规 |
| PW_S_012_00_c | 0.3998 < 0.4 | 真违规 |
| PW_S_012_00_p | 0.8117 < 0.812 | 真违规 |

## B档 reframe
- 源码在 xxchen 私有 workdir (沙盒不可达) → asset_fidelity=synth
- 参数化 `corner_space_pattern_gen.py <config.json> <out_report.json>` (stdlib only)
- constraint-pattern-gen 子型 (承 r608 EncloseSide1PatternGen)，corner-space 变体
- 输入A: PW_S_008_00_c value=0.4 no-clamp
- 隐藏B: PW_S_008_00_p value=0.615 no-clamp
- 隐藏B2: PW_S_013_00_c value=0.3 clamp 触发 (dx=0.34>=target=0.2998)
