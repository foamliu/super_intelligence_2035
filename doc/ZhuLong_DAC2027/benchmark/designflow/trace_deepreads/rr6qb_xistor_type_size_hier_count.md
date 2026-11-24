# trace_deepread: 1795411956334_rr6qb — XistorTypeSizeHierCount

- **session**: 1795411956334_rr6qb.messages.json
- **user**: shushengz @ hfeg0pkn004 (10.129.2.13)
- **mc**: 306 · **domain**: schematic_netlist (schematic + analog + cmos + transistor)
- **keywords**: schematic:1107; cellview:780; analog:390; cmos:339; dbget:92; virtuoso:71; dbopencellviewbytype:71; transistor:70

## 用户原始意图
1. (msg 0) 统计 `/proj/dejoa/V0/libs/dejoa_digital/DoutFIFOTopM6/schematic` block 内 ntn_m/ptn_m/ntk/ptk 管子类型、数量和尺寸。
2. (msg 210) 在 `/proj/dejoa/V0/libs/dejoa_top/LP6TOP/schematic` 找 ntn_m/ptn_m/ntk 器件数量和比例。
3. (msg 254-286) 加载/运行 SKILL 脚本 (count_mos_types_v2.il, analyze_block.il, analyzeDevices)。
4. (msg 292) 找使用 ntn_m cell 对应的完整 hierarchy 路径。

## Agent 实际行为
- 检索 SKILL API: dbOpenCellViewByType, cv~>instances, inst~>master~>cellName, vfoGetParam(w/l), pcdbInstMasterCell 等。
- 写 SKILL 脚本 count_mos_types.il / count_mos_types_v2.il / analyze_block.il: 用 dbOpenCellViewByType 打开 schematic, foreach inst in cv~>instances, 按 cellName==ntn_m/ptn_m/ntk/ptk 过滤, 取 inst~>w / vfoGetParam(inst "w"), 递归 _traverseCv 下钻子 cell, 打印实例名/W/L/所在 cell。
- SKILL 沙箱不可用 → 回退用 `strings` 解析 OA 二进制 (sch.oa / layout.oa) 提取器件引用与 W/L。
- 发现: fifolatch_scmos 含 ntn_m (MN1 W=10u L=0.18u 等), DoutFIFOTopM6/layout 有 I_ntn_m_217~220; ptn_m/ntk/ptk 在该 block 未直接实例化 (在其他 block 中)。
- LP6TOP: ChanMid/layout 有 6 个 ntn_m flatten 实例 (I_ntn_m_0/3/466/468/470/472); ptn_m/ntk/ptk 0 实例。

## 关键 SKILL 代码模式 (count_mos_types_v2.il)
```skill
cv = dbOpenCellViewByType("dejoa_digital" "DoutFIFOTopM6" "schematic" "" "r")
foreach(inst cv~>instances
  cellName = inst~>master~>cellName
  when(member(cellName list("ntn_m" "ptn_m" "ntk" "ptk"))
    w = inst~>w  unless(w w = vfoGetParam(inst "w"))
    l = inst~>l  unless(l l = vfoGetParam(inst "l"))
    ...
  )
  ; descend into non-primitive sub-cells
  subCv = dbOpenCellViewByType(libName cellName viewName "" "r")
  cnt = cnt + _traverseCv(subCv)
)
```

## 造题映射
- 真实场景: Virtuoso SKILL 遍历 OA schematic cellview 统计 MOS 类型/数量/尺寸 + 层次路径 + 比例。
- 评测化: 以 CDL 网表形式给出相同层次结构 (DoutFIFOTopM6 → fifolatch_scmos / DOutFIFOx4M6 / DqOutMux1 / SparePtk), 要求脚本层次化展开统计 ntn_m/ptn_m/ntk/ptk 的数量(调用次数×M=倍数)、唯一 W/L 尺寸集合、ntn_m:ptn_m 最简比、每管层次化路径, 输出 JSON。
- case_id: EDA-Eval-DesignFlow-XistorTypeSizeHierCount-001 (shard D, schematic_netlist)
- 区别于 HierSpiceMosCount-001: 后者仅做三层调用次数相乘计数; 本 case 增 W/L 尺寸提取 + 层次路径 + 比例 + M= 倍数, 13 断言。
