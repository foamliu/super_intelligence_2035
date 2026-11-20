# 深读：55ms0 — RNODE/RTEXT 覆盖审计 + 放置（pg_layout）

- **session**: 1785932055598_55ms0 / user=e0014566 / host=hfeg0pkn001 / mc=297
- **tools**: calibre 124 + virtuoso 109 + cellview 68 + dbGet 8（pyAether 2）= shard-C dominant ratio 0.93
- **size**: 747KB / 123 msgs / 3 UI
- **domain**: pg_layout（PowerFill + RNODE/RTEXT 电源网络电阻探针）

## 用户原话（逐字）
- UI#1 (idx=0): `帮忙分析一下layout:  austin_rscalc2/testa/`
- UI#2 (idx=22): `为啥 PowerFill 是  dummy fill, 不降电阻？辛苦仔细看下代码，帮忙排查一下，这个不符合预期，预期是要降低电阻的，看看是不是哪里配置有问题。` ← **A-档 seed 候选**（提出 concern 未给根因/修复）
- UI#3 (idx=50): `所以是不是我 RNODE 点打少了，在原本layout中该打RNODE的地方没打？辛苦帮忙打上合适的RNODE` ← 用户给假设（RNODE 打少了）→ 违反 A-档选轮规则

## trace 真实根因排查（agent 66 次工具调用）
1. **UI#1 分析 layout**：agent 探 `test_layout_rscalc_flow_5/`，发现 RsCalc→AutoVia→PowerFill 三段 flow，baseline+iter1+iter2 三轮。`.rvn` 文件 md5 三轮**逐字节相同**→电阻零改善。
2. **UI#2 PowerFill 排查**（agent 自我纠错）：
   - 初判"PowerFill 是 dummy fill"→**错**。深读 `genPowerFill.py` + DRC deck `10G4plus_PowerFill_GUI_fast.rule` = "DRAM PowerFill Rule File"，有 `output non-floating metal` + `remove floating` 逻辑 = 真正连接电源网的 power rail fill。
   - 关键警告 `Label vdd! at location (200,1.5) is unattached and has been ignored` → vdd! pad (200,1.5) 标签未附着。
   - fill 在 GDS layer 210:0 (y3 drawing)，stream-in 用 `noYLayer_layer.map` 丢弃 Y-layer → 但 `cxmt_layout_convertYlayerToPcell(PG.gds)` 从 PG.gds 重新读 Y-layer 转 via pcell insert 到 fill cell（`Total Run insert Pcell Time: 0.4m`）→ fill cell 非空，有 V1 via pcell + M1-M5/y3 形状（FastXOR xor.rule.summary 证实）。
   - **真实根因**：不是 PowerFill 是 dummy，而是 **RTEXT/RNODE 放置不足**：
     - Layout bbox `(0.88,-5.35)→(310,15)`，M5 大 rail `(100,0)→(300,8)`
     - vdd RTEXT **只有 1 个**：M1 (10.525,-2.075)
     - vdd! pin at (200,1.5) 有 M1-M5 pin + mark label，**但没有 RTEXT** → RsCalc 不知道第二个电源入口
     - 现有 RNODE 全在 x≈2-24，**x>24 完全盲**（大 M5 rail x=100-300 无探针）
3. **UI#3 加 RNODE**（gold）：agent 用 SKILL `query_layout.il` 实地查 layout → 写 `add_rnode.il`：
   - 加 RTEXT at (200,1.5) 第二电源 pad
   - 加 RNODE 沿大 M5 rail 间隔放置
   - 共加 18 个标签 → Virtuoso SKILL 执行 → 重跑 RsCalc baseline → 35 check points

## gold 依赖
`add_rnode.il` SKILL 脚本 + `query_layout.il` 依赖 **live Virtuoso + OA + austin_rscalc2 私有库**（e0031982 无权访问）→ **A-档 disqualified → B-档 synthesized L1-boundary**。

## 合成方案（L1-boundary，离线 Python）
**rnode_cov_audit.py**（Python3 标准库 re/json/argparse/collections/math）：
- 输入：layout figure inventory 文本（FIG 行 + config 头：LAYOUT_BBOX/POWER_NETS/RTEXT_PURPOSE/RNODE_PURPOSE/PAD_LAYERS/RAIL_SPACING）
- 解析 FIG：layer/purpose/type(rect|label|pin)/net/text/bbox
- 每个电源网：
  - RTEXT labels（purpose=RTEXT, type=label, text=net）→ (x,y) 列表
  - RNODE labels（purpose=RNODE, type=label, text=net）→ (x,y) 列表
  - rail rects（type=rect, net=net, purpose=drawing）→ union bbox（x-span/y-span）
  - power pads（type=pin, net=net, layer∈PAD_LAYERS）→ pad centroid 列表
- 审计：
  - missing_rtext：pad centroid 无共址 RTEXT（tol）→ 缺 RTEXT
  - rnode_gap：rail x-span 内按 RAIL_SPACING 设 target_x，无现存 RNODE 在 tol 内 → gap placement
  - blind_region：rail 段完全无 RNODE
- 放置计划（确定性）：
  - missing_rtext → 加 RTEXT at pad centroid（text=net, RTEXT_LAYER）
  - rnode_gap → 加 RNODE at (target_x, rail_y_mid)（text=net, RNODE_LAYER）
- 输出 JSON：config / nets{rtext_count, rnode_count, rail_xspan, rail_yspan, pads, missing_rtext, rnode_xs, rnode_gaps, blind_regions, placement_plan} / summary{total_missing_rtext, total_rnode_placed, total_placed} / verdict(NEEDS_FIX|OK)

## 与既有 case 区别
- PFMergeAudit-001 = power fill merge bug（dbCopyFig 丢 net/pin/重复 label）
- RsCalcMesh-001 / RsCalcCfgSync-001 / RsCalcFlow-001 = RsCalc 配置/mesh/flow
- 本案 = **RsCalc RNODE/RTEXT 探针覆盖审计 + 放置计划生成**（探针盲区 + 缺电源 pad 标签），主题/断言独立

## 14 条断言（a-n）
a. deliverable zip 存在 + 解压 + rnode_cov_audit.py 可编译
b. JSON 结构齐全（config/nets/summary/verdict）
c. 每个电源网 rtext_count + rnode_count 正确
d. rail_xspan / rail_yspan = union of rail rects（边界数值）
e. missing_rtext 正确识别缺 RTEXT 的 pad（count + xy）
f. rnode_gaps 正确计算（gap 区间数 + 起止）
g. placement_plan 含每个 missing pad 的 RTEXT（net/layer/xy 正确）
h. placement_plan 含每个 gap 的 RNODE（count + xs 落在 gap 区间内）
i. RNODE 间距 ≈ RAIL_SPACING（连续 placed xs 差值在容差内）
j. placed xy 全部 unique（无重复放置）
k. 所有 placed xy 落在 LAYOUT_BBOX 内（不越界）
l. verdict = NEEDS_FIX 当存在 missing/gap；OK 当全清
m. 确定性：B 跑 3 个随机种子 md5 一致
n. 交叉守卫：B 用不同 net 名（PVDD!/PVSS! 非 vdd!/vss!）→ 杀硬编码 net
