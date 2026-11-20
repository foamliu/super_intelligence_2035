# 深读笔记 — 1792736016983_y42xz (NoOverlap pcell layer-name 解析)

- **session**: 1792736016983_y42xz.messages.json
- **user / host**: yzwang @ hfeg0pkn001 (10.129.2.10)
- **mc**: 48 | **domain**: layout_virtuoso | **工具信号**: dbcreaterect:131 + drc:114 + pdk:61 + cellview:25 + virtuoso:10
- **文件路径**: `/home/pdk/yzwang/06_AI_workspace/test7/{NoOverlap.il, NoOverlap.il_bk, NoOverlap.il_bkk}`
- **总 msgs**: 39 | **真实 user prompts**: 2

## 用户意图（逐字原文，仅 key/token 掩码）
- P0 (msg#0): "我在/home/pdk/yzwang/06_AI_workspace/test7放了一个文件叫NoOverlap.il的pcell脚本，这个pcell的参数只有两个layer名称，我先在遇到的问题是当layer为M1_drawing，也就是一个下划线的时候，pcell可以正常显示，当Layer名称是M1_prohibit_cmp，也就是两个下划线的时候，pcell会报错，请你帮我修改这个代码。"
- P1 (msg#26): "请分别解释NoOverlap.il中第26行的语法和作用，NoOverlap.il_bk中第26、27行的语法和作用，NoOverlap.il_bkk中第26-29行的语法和作用。"

## pcell 结构（三变体共同，差异仅在 layer 名解析行）
`pcDefinePCell(list(ddGetObj("PDK_QA_PCELL") "NoOverlap" "layout") list((layer1 string "RLDEV_mark2")(layer2 string "RLDEV_mark1")))`：
- mark 层: `lpp01=list("OPC01" "mark1")`(高亮), `lpp02=list("OPC02" "mark1")`(边框), `lpptext=list("text" "drawing")`(标签)
- 3 bad 重叠对: pair1 A11=l1 rect(1:1 2:2)+A12=l2 rect(1.5:1 2.5:2)+A13=dbLayerAnd(lpp01,A11,A12); pair2 A21=l1 rect(4:1 5:2)+A22=l2 rect(4.2:1.2 4.8:1.8)+A23=lpp01 rect(4.2:1.2 4.8:1.8); pair3 A31=l2 rect(4:1 5:2)+A32=l1 rect(4.2:1.2 4.8:1.8)+A33=lpp01 rect(4.2:1.2 4.8:1.8)→dbMoveFig 三者 +(2.5:0 "R0")
- bad 边框: lpp02 rect(0:0 8.5:3); 标签: sprintf("  Check - %s cannot overlap with %s" layer1 layer2) at 0:2.5
- 2 good 不重叠对: good1 A41=l1 rect(10:1 11:2)+A42=l2 rect(11:1 12:2)(边相切); good2 A51=l1 rect(13.5:1 14.5:2)+A52=l2 rect(15:1 16:2)(有间距)
- good 边框: lpp02 rect(9:0 17:3); 标签 at 9:2.5

## 三变体 layer 名解析（核心差异 — bug 与两种 fix）
| 变体 | 行号 | 代码 | 行为 |
|---|---|---|---|
| `NoOverlap.il` (BUG) | 26-27 | `l1 = parseString(layer1, "_")` `l2 = parseString(layer2, "_")` | 按**每个**下划线拆: `M1_drawing`→`("M1" "drawing")` 合法 2 元 pair ✓; `M1_prohibit_cmp`→`("M1" "prohibit" "cmp")` 3 元非合法 pair → dbCreateRect 报错 ✗ |
| `NoOverlap.il_bk` (fix-A) | 26-27 | `rexCompile("_")` `l1 = parseString(rexReplace(layer1, " " 1))` | rexReplace x_index=1 只换**第一个** `_` 为空格, 再 parseString 默认空白拆: `M1_prohibit_cmp`→`"M1 prohibit_cmp"`→`("M1" "prohibit_cmp")` 2 元 ✓ |
| `NoOverlap.il_bkk` (fix-B, 干净) | 26-29 | `idx1 = nindex(layer1 "_")` `l1 = list(substring(layer1 1 idx1-1) substring(layer1 idx1+1))` | nindex 找第一个 `_` 位置, substring 切: layer=首 `_` 前, purpose=首 `_` 后(保留剩余下划线): `M1_prohibit_cmp`→`("M1" "prohibit_cmp")` ✓ |

## assistant 诊断与 fix
- msg#6 助手定位根因: `dbCreateRect` 的 layer 参数接受 name string / number / `list(layer purpose)` pair; 原代码 `parseString` 拆 `_` 在层名本身含下划线时既不必要又错误; `dbCreateRect`/`dbLayerAnd` 直接接受完整 `"layer_purpose"` 串。
- msg#8/21 fix: `l1 = layer1; l2 = layer2`(直接用全名, 不拆)。
- msg#15 因 `/home/pdk/yzwang/...` 不在 writableRoots(`/home/yzwang`), 不能直接写; 用户选 copy-edit-copy-back; 助手 copy 到 `/home/yzwang/NoOverlap.il` 编辑, 给 `cp` 命令回写。
- msg#26+ 用户问三变体行号语法, 助手查 `rexCompile/rexReplace/nindex/substring/parseString` API 文档解释。

## trace 末尾
用户问三变体行号语法解释(P1), 助手查 API 文档作答; **无用户明确接受最终落盘产物** → 不适用 A-档(faithful), 取 **B-synthesized**(grounded on 真实 NoOverlap.il 三变体 + 真实 bug + 真实 pcell 结构)。

## 与既有 case 的 DISTINCT
- r207 QaWidthPatternGen(kenwang e7fdl, width-rule QA pattern 12 形族 good/bad PASS_HIGH/BOUNDARY/FAIL_LOW + 45° 菱形 + 口字环) — 亦 QA pattern generator, 但测 **width rule + 12 形族几何**, 与本案 **overlap rule + layer/purpose 名解析(首下划线切分)** 互补不重叠。
- r206 DupViaPriorityCheck(yqlu maglj, duplicate-via 优先级) / r201 CentroidPlaceAudit / r199 HierCellPatternFind — 主题不同。
- 本案首次 ground on **SKILL pcell layer/purpose 名按首下划线切分 + NoOverlap QA pattern(bad 重叠对 dbLayerAnd 高亮 + good 不重叠对 + mark 层)**, 暴露 parseString-on-every-underscore bug。

## 合成方向
SUT 写离线 Python `nool_overlap_pcell_gen.py`, CLI 1 参 `<config.json>`: 按**第一个**下划线解析 layer/purpose(purpose 保留剩余下划线), 报告 buggy all-underscore 拆分结果(all_underscore_parts), 计算 bad/good 矩形对的 axis-aligned 交集(apply per-pair move), 输出 JSON manifest(lib/cell/view/layers/mark_layers/bad_pairs/good_pairs/borders/labels/summary)。资产 A=真实 RLDEV_mark2/RLDEV_mark1 + 真实 pcell 坐标; 隐藏 B=多下划线 MT2_via1_via2/M1_prohibit_cmp + 重参数化坐标(击穿 buggy 拆分 + 硬编码 A); B_broken=无下划线名 M1drawing(优雅退化哨兵)。判分 16 条 ①–⑯ a–p, k_check=16=k_rationale。
