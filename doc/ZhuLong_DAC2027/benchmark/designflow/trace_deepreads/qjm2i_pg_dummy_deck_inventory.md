# trace deepread — 1792564977442_qjm2i (ellawu @ hfeg0pkn005, mc=195)

- session: `1792564977442_qjm2i.messages.json` (1.80MB, 304 msgs, 62 user turns)
- keywords: drc:6937; calibre:412; .gds:17; gdsii:6; aether:6; pyaether:2; cmos:2
- tools used: read_files / editor / list_allowed_files / run_approved_command (cline built-ins, no MCP run_code — offline rule-deck authoring)
- uploads (real attachments): `G5_AA_PG_dummy_fill_for_Logic.rule` (209KB calibre SVRF/TVF deck, 2106 lines) + `G4C_AA_PG_dummy_fill_Flow.md` (25KB flow doc)

## 用户真实意图
ellawu 是长鑫存储 (ChangXin Memory) 的 calibre rule deck 工程师，在维护 G5 AA/PG dummy fill deck（G4plus 逻辑单元自动加 AA/PG dummy 的 calibre 工具 deck）。首轮逐字原话：

> 「对比一下两个deck对生成dummy长度和BLK之间关系」
> （附 G5_AA_PG_dummy_fill_for_Logic.rule + G4C_AA_PG_dummy_fill_Flow.md）

随后整条 trace 是对 deck 的 SVRF/TVF 语义的深入问答与改写：dummy 被 BLK 削短导致长度不一致（U#1）、BLK 的定义（U#2/U#3）、`SETLAYER MOS_AA_Insert_Hori_PG_drc2_*` 窄脖颈 (SINGULAR) 切割逻辑（U#5–U#42）、横边提取 / CONVEX EDGE / DFM PROPERTY（U#16–U#26）、斜对角 dummy 距离（U#44–U#57）。属 pg_layout + physical_verify 域（PG dummy fill rule deck authoring）。

## deck 关键结构（事实，check.py 对账用）
- TVF 格式：`#! tvf` / `namespace import tvf::*` / `VERBATIM {`；Copyright ChangXin Memory Technologies,Inc
- 9 个 `set PG_Dummy*` 参数（真实值）：Vert_Width=0.211, Hori_Width=0.192, MinWidth=0.163, Dummy2_PG_Space=0.234, MinArea=0.110, MaxSpace=0.294, MinSpace=0.234, PGLineEnd_MinSpace=0.234, MinLength=0.675
- BLK 块（L301–324）：`BLK_poly / BLK_dummy / BLK_diff / BLK_diff_for_hori / BLK / BLK_for_hori`，复合层 `BLK = OR BLK_diff BLK_dummy BLK_poly`（L323）
- 横向 PG dummy 链：`MOS_AA_Insert_Hori_PG_t1 → drc1 → drc2_*`（drc1 定义 L822；drc2 子层 35 个，含 SINGULAR 窄脖颈切割 _2_singular_region / _3、Zig/NoZig、minStep/Step）
- 全 deck 457 SETLAYER，10 条含 SINGULAR

## case 取材（B-synthesized, L1-boundary）
trace 是交互式问答/改写（无单一受用户接受的产物文件），故取 A-档 faithful 的「用户逐字首问 + 真实附件 deck」为场景，合成一个可机械判分的 L1 任务：写一个 SVRF/TVF deck inventory 解析器，提取头部/PG_Dummy 参数/BLK 复合层/横向 drc1 定义/drc2 子层/SINGULAR 层/SETLAYER 计数，输出 JSON。资产 = 真实 G5 deck 的忠实浓缩版（保留真实参数名、真实 BLK/drc1/drc2 结构、真实 SINGULAR 处理）。隐藏 B = 重新参数化（值全改）+ BLK→BLKX + hori-PG 前缀改名 + 删 2 条 SINGULAR；probe = 第三组值（原名）。判分对 B/probe 跑解析器断言 15 条，反硬编码。

## 选用理由（去重）
- DISTINCT from r192 FloatingPinGen(ellawu layout_virtuoso 浮动 pin) + r189 DeleteM1Shapes(e03179)：本 case 是 calibre SVRF deck 解析（pg_layout/physical_verify），不是版图操作
- pg_layout 是 shard C 最薄弱域（r195 前 29 条），本 case 补 pg_layout（29→30）
- 模型公平对比：与 pi 同 deepseek-v4-pro-cloud
