# trace_deepreads/7bout_calibre_layer_map.md — shard C r820

## trace
- session: `1790149772146_7bout` (yzwang @ 10.129.2.10, mc=29, 22 msgs / 13 user / 9 assistant)
- keywords: calibre:224; gdsii:144; dbget:32; rtl:12; aether:12; pyaether:9; lvs:3; drc:2
- source: ssh+scp from `~/.cline/data/sessions/1790149772146_7bout/1790149772146_7bout.messages.json` (100KB) ✓

## 用户真实意图（4 轮逐字）
- U#0: 「y0_drawing 在系统里定义的是 207_0，并且被定义成 datatype，我用 `WITH TEXT VSH "S2" y0_drawing` 不可以抓出 VSH 层上用 y0_drawing 打的 S2 label，但 `WITH TEXT VSH "S2" 207` 却可以抓出来，这是为什么？」
- U#1: 「`y0_drawing` 在 calibre.layer 里定义的是 datatype 而非 texttype，我想知道用 207 是怎么绕开的」
- U#2: 「VSH 是另外一个层，y0 的定义是 `LAYER MAP 207 DATATYPE 0 8148` / `LAYER y0_drawing 8148`」
- U#3: 「如果用的 207 的话，那也是用的 datatype 而不是 texttype，那 207 怎么被识别为文字的」

## assistant 关键解释（末轮 msg21）
- GDSII 中 BOUNDARY/PATH 用 `datatype`，TEXT 用 `texttype`，**两个独立 2-byte 字段**
- `LAYER MAP 207 DATATYPE 0 8148` 只映射图形，**不映射文字**
- 没有 `LAYER MAP 207 TEXTTYPE ...` 规则时，GDS layer 207 上的 TEXT 元素走**默认 fallthrough** → Calibre 内部层号 = GDS 层号 = 207
- 所以 `WITH TEXT VSH "S2" 207` 能找到 TEXT（落在 Calibre 207），`WITH TEXT VSH "S2" y0_drawing`（=8148，只有图形）找不到
- 两个 `207` 数值相同但处于不同命名空间（GDSII 源端层号 vs Calibre 内部层号），但默认 fallthrough 让它们恰好相等

## 档 B reframe
- A 档 gold = free-text markdown 概念解答，无 ≥8 硬断言牙（print-only stub 打印同形 markdown 即 PASS 违反 §4.9）→ reframe
- 抽离算法核心成纯 stdlib `calibre_layer_map_resolver.py`（CLI `<calibre_layer.txt> <gds_elements.json> <out.json>`）
- 算法：解析 LAYER MAP DATATYPE / LAYER MAP TEXTTYPE / LAYER name 规则 → 对 BOUNDARY/TEXT 元素解析到 Calibre 层号（无规则则默认 fallthrough = GDS 层号）→ 回答 WITH TEXT 查询
- visible A = yzwang 真实 calibre.layer（LAYER MAP 207 DATATYPE 0 8148 / LAYER y0_drawing 8148 / LAYER VSH 200）+ 4 元素 + 2 查询
- hidden B = 数字实现流程 M1 层文件（LAYER MAP 305 DATATYPE 0 9001 / LAYER MAP 305 TEXTTYPE 0 9002 / LAYER shape_purpose 9001 / LAYER label_purpose 9002 / LAYER M1 100）—— **显式定义 TEXTTYPE 规则**，exercise A 中不可达的 texttype_rule 路径

## case 落库
- `EDA-Eval-DesignFlow-CalibreLayerMapResolver-001` (physical_verify, L1, 档 B, k_check=16, 子型 calibre-svrf-layer-map-text-resolver)
- 16 断言 a-p，含交叉输入 A 验证 trace 核心洞察（q1=0/q2=1，e3→207 default_fallthrough）
- 自验：ref PASS 16/16；4 negative 全 FAIL distinct (a/c/f/e)；§4.9 三假全 FAIL；确定性 2x md5 一致
