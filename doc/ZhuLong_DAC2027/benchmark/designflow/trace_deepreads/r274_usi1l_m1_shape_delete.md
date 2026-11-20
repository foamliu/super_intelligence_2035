# 深读笔记 · 1782818092421_usi1l (e03179 @ hfeg0pkn002/10.129.2.11)

- **trace**: 1782818092421_usi1l.messages.json (116KB, 46 msgs, 1 real user turn)
- **user**: e03179 — SEEN (有 case in ledger_C); agent=lead calibre/SKILL layout 编辑
- **mc/tools**: tot=307, 254 cellview + 39 dbGet + 18 skill + 10 schematic + 4 virtuoso (cron 口径); 真实 session 以 SandBox_MCP_Server__run_code (lang=skill, host=virtuoso) + RAG_MCP_Server__search_apis 为主
- **workspace**: cellview = TECHLIB_test/CT_Mark_P/layout (dbu=1000); 真实共 3 shapes 含 1 个 M1; 产物写 /home/e0025768/devops/bundle/ (共享 devops 目录)
- **claimed + 出 case**: r274 (2026-11-09)，EDA-Eval-DesignFlow-M1ShapeDelete-001

## 用户真实意图（U#0 提出需求，未给根因 → A-faithful eligible，本案做 B 档）
- U#0 逐字：「删除当前版图在所有M1的图形。统计删除图形的数目，并保存到本地的当前目录下的一个文件中。使用skill语言生成代码并执行。」
- 单轮闭环，无后续细化。提出需求，未给根因/修复方案 → A-faithful eligible。

## assistant 真实产物（SKILL，Virtuoso run_code 真跑，多次迭代）
- cellview = geGetEditCellView() → TECHLIB_test/CT_Mark_P/layout (db:0x1ee7491a)
- 关键 SKILL（最终版 msg 25/29）：
  ```skill
  allShapes = cellview~>shapes
  m1Shapes = setof(s allShapes s~>lpp && car(s~>lpp) == "M1")   ; 按 layer 名过滤
  count = length(m1Shapes)
  foreach(shape m1Shapes dbDeleteObject(shape))                  ; 删除
  outPort = outfile("./deleted_m1_count.txt")
  fprintf(outPort "Number of M1 shapes deleted: %d\n" count)     ; 写统计文件
  close(outPort)
  ```
- 真实跑结果（msg 24）："Cell: CT_Mark_P View: layout / Total shapes: 3 / M1 shapes found: 1 / Deleted 1 M1 shapes"
- 文件内容（msg 34）："Number of M1 shapes deleted: 0"（msg 24 已删 1，msg 25/29 二次跑 M1 已空 → 0）
- 早期尝试 techGetLP(techId, list("M1" "drawing")) 失败（techId=nil，TECHLIB_test 无 tech file），改用 `setof + car(lpp)=="M1"` 按 layer 名直接过滤成功。

## 为何 B 档重定义为「离线 layer-filter DELETE+COUNT+PERSIST」(L1)
- 真实 Virtuoso/OA cellview 不可沙盒复现（geGetEditCellView/dbDeleteObject 需真实 OA session）。
- 但核心算法纯数据操作：给定 shape 列表 → 按 layer=="M1" 过滤 → 删 + 计数 → 写文件 + 输出剩余清单。
- 重定义：离线 Python 脚本吃 layout_inventory.json → 按 layer=="M1" 过滤删除 + 计数 + 写 deleted_m1_count.txt + 输出 cleaned_inventory.json。check.py 在 hidden B 上 subprocess 真跑候选(L1+subprocess)，断言 ≥8 条件。

## B-track 参数化非硬编码
- hidden B（CXMT10G_LIB/PwrSwAmp_B/layout, dbu=2000, 15 shapes, M1 count=7 含 2 pin-purpose, 含两个同 bbox M2 id10/11, 含 A 没有的 M3/Poly）
- vs A（TECHLIB_test/CT_Mark_P/layout, dbu=1000, 3 shapes, M1 count=1 全 drawing）
- 不同 cellview/dbu/规模/层集/M1 计数，参数化非硬编码。

## DISTINCT from 现有 layout_aether 系
- r272 LayoutAnalyzeReport = die-bbox 并集 + per-(layer,purpose) 计数/面积 **统计报告**（无删除）
- r264 ScmosCrossProbeCsvGen = OA 实例图 → BFS 拼真实实例名 hierarchy **cross-probe CSV**
- r252 LayStructExtract / r238 LayoutFloorplanGen / r222 SchOaInventoryExtract / r253 PinListPortOrderExtract / r254 EmyCdlNetlistExtract
- 本案首次 ground on「按 layer-name 过滤 **DELETE** + **COUNT** + **PERSIST**(写文件+输出剩余清单)」：核心是删除操作（修改数据集）+ 计数 + 持久化，不是只读分析。

## 自验（r274）
- golden delete_m1_shapes.py 在 B 上 14/14 PASS ✓
- 3-run sha256 一致 (deleted_m1_count.txt f7a0db81... / cleaned_inventory.json 4708cd43...) ✓
- 5 negative 全 FAIL (SELFTEST_RC=0): empty_shell→c, print_expected_A→e(count=1≠7), core_deleted→e(0≠7), naive_no_filter→e(15≠7), wrong_layer→e(4≠7) ✓
- §4.9 三假 (empty/print/core) 全 FAIL ✓
- test==disk check.py sha 5544f7155da4 一致 ✓
- 断言闸门 k_rationale=k_check=14(a-n)≥8 GATE PASS ✓
- jsonl roundtrip (test 字段从 jsonl 读回跑 reference_submit.zip) PASS ✓

## 同批 peek 候选（r274，全 parked）
- 5gxno (colinxu, 90msgs) REJECT: 真实 user turn 仅 U#9「电源 pin 命名 VDD」过薄 schematic-pin 任务，余为 API-search/tool-result 噪声；schematic 域非 layout
- tatnx (e0014566, 217msgs) REJECT: RsCalc+AutoVia+PowerFill 电阻优化 flow（prompt_flow.md 预写 skill-execution）；重叠 r265 RscalcBsubPollRunner + r268 RscalcRtextRnodePlan
- 1uxza (johnl, 72msgs) REJECT: PrimeLib/DC-shell synthesis + .lib/.db 库表征 + rowred behavioral rebuild；synthesis 域非 pg_layout（innovus234 cron 计数=噪声）
- r75ux (laryu, 49msgs) REJECT: prose-how-to/知识问答（AND-metal-poly 含义、SVRF INTERNAL 语法、dbOpenCellViewByType 属性、LVS virtual-label 警告、SPF MOSFET 参数）；无计算性 build 交付
- 6bje0 (e0014566, 21msgs) 未细读 user turns，留 fresh 供下轮
