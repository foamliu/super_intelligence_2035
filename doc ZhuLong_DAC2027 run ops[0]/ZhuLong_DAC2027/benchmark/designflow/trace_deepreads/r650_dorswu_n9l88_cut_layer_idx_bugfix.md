# r650 深读 · dorswu @ hfeg0pkn004 (10.129.2.13) · session 1792465550373_n9l88

- **trace_source**: user=dorswu, host=hfeg0pkn004 (10.129.2.13), session_file=1792465550373_n9l88.messages.json, match_count=137
- **keywords**: dbget:153;pyaether:87;pdk:49;dbopencv:31;cellview:24;techfile:22;cadence:20;rtl:16
- **size**: 1.55 MB, 389 msgs, 23 real user turns
- **pool_reaudit_C.tsv 旧判定**: weak: 用户指出脚本 layer/purpose 解析 bug=debug 轮
- **pool_reaudit_C.tsv 新判定**: 可造 → 本轮 r650 复活造题

## 用户原话（A 档选轮 · 逐字）

**U#0**（提出需求型，未给根因/方案 ⇒ A 档合规）：
```
<user_input mode="act">/home/ylxing/Temp/HReplaceCellViatoTechViaa.py
帮我看一下这个脚本的问题，"layer：AT4，purpose：PCH" 识别成 "layer:PC"</user_input>
```
> 注：路径中有 typo（`ViatoTechViaa`），实际文件为 `/home/ylxing/Temp/HReplaceCellViatoTechVia.py`（agent 在 A#1 read 失败后 A#5 修正读到了）。

**U#26**（生成修正副本）：
```
<user_input mode="act">帮忙生成一份已修正的完整副本放在可写目录</user_input>
```

后续 U#59–U#300 是更复杂的 LICON 类型分发（AT4.NCH/PCH/PG.NCH/PG.PCH → LICON_NCH/PCH/PG，需顶层 `dbGetTrueOverlaps` 查询）、PC.drawing 孔数/尺寸保留、LICON_PG `layer1EnclosureChoice=NONE` 等迭代——属 trace 中演化的更大任务，**本轮 case 聚焦 U#0 + U#26 的 clean seed：cut-layer index 解析 bug 修复**。

## Bug 定位（assistant A#19 editor call 揭示）

原始 `_find_cut_layer_idx`：
```python
def _find_cut_layer_idx(shapes, keywords):
    """Find the index of the cut layer in sorted unique shapes by matching LPP name"""
    for i, s in enumerate(shapes):
        lpp_str = str(s.lpp)
        for kw in keywords:
            if kw in lpp_str:          # <-- BUG: substring match
                return i
    return None
```
`CUT_LAYER_KEYWORDS = ["PC", "V1", "V2", "V3", "V4", "V5", "V6"]`

**Bug**: `if kw in lpp_str` 是子串匹配。lpp 串格式 `'<layer>.<purpose>'`（如 `AT4.PCH` / `PC.drawing`）。`"PC" in "AT4.PCH"` 为 True（"PC" 是 purpose "PCH" 的前缀），导致 `AT4.PCH` 被误识别为 PC cut layer。同理 `"V1" in "V10.drawing"` 为 True。

## Gold 修复（assistant A#19 new_text）

```python
def _find_cut_layer_idx(shapes, keywords):
    """... LPP string format is '<layerName>.<purpose>'. Match keyword against
    LAYER NAME only, as an exact whole-token match. A substring match on the
    whole string is wrong: 'PC' in 'AT4.PCH' is True ..."""
    kw_set = set(keywords)
    for i, s in enumerate(shapes):
        lpp_str = str(s.lpp)
        # rsplit from the last '.' so layer names that themselves contain a dot
        # (e.g. 'SH.MM') are still matched correctly.
        layer_name = lpp_str.rsplit('.', 1)[0] if '.' in lpp_str else lpp_str
        if layer_name in kw_set:
            return i
    return None
```

## 验证用例（assistant A#21 自建 check_cut_match.py）

| lpp_str | OLD(buggy) | NEW(fixed) |
|:--|:--|:--|
| AT4.PCH | PC | None ✓ |
| PC.drawing | PC | PC ✓ |
| M1.drawing | None | None ✓ |
| AT4.drawing | None | None ✓ |
| V10.drawing | V1 | None ✓ |
| V1.drawing | V1 | V1 ✓ |

## B 档 mock-behavioral reframe 设计

承 r642 ViaEncChoiceR90Force mock-behavioral 模式；新子型 `cut-layer-idx-bugfix`：
- 真实 `HReplaceCellViatoTechVia.py`（pyAether/OA via 替换脚本，不可达沙盒+权限不可读）→ 合成紧凑可运行 mock `buggy_script.py`（保留 `CUT_LAYER_KEYWORDS` + `Shape.lpp` + `find_cut_layer_idx` 子串 bug + try/except pyAether mock 兜底）作 asset A。
- deliverable = 修正后的 `cut_layer_match.py`（纯 stdlib），保留 try/except pyAether 兜底以在沙盒无 pyAether 时可运行。
- check() 用 hidden B（不同 shape 列表 + 边界用例 V10/PCD/SH.MM.dotted）subprocess 跑候选模块，断言 `find_cut_layer_idx` 返回索引；AST 结构断言无 `kw in lpp_str` 子串比较残留；负样本（子串 bug 原版 / always-None / always-0）必 FAIL。
- distinct vs r642=via-enclosure-choice-r90-force / r634=nonascii-sanitize：本 case=cut-layer-name whole-token 匹配修复（debug-fix-parse-bug 子型）。

## 真实性溯源

- session_file: 1792465550373_n9l88.messages.json（dorswu @ 10.129.2.13）
- 用户原话 U#0/U#26 逐字保留（仅路径 typo 保留原样）
- bug 代码 + gold fix 来自 trace 内 assistant 的 editor 调用（A#19）
- 验证用例表来自 trace 内 assistant 自建的 check_cut_match.py（A#21）
