# Deepread — 1791869784917_1r058 (e0014566 @ 10.129.35.82)

- **mc**: 23 ; **keywords**: cellview:147;schematic:33;virtuoso:16;transistor:16;mosfet:4;analog:3;pyaether:2;techfile:1
- **agent**: lead ; **msgs**: 22 ; **size**: 83.6 KB
- **domain (shard D)**: schematic_netlist

## 用户意图（原文）
> 请返回高亮当前的mos管，使用virtuoso skill的API接口，我需要你使用run code 工具执行

单一明确意图：在 Virtuoso 原理图编辑器中，用 SKILL API 把当前打开的原理图里所有 MOS
晶体管高亮出来，并通过 run code 工具执行该 SKILL 代码。

## agent 工具链
1. `RAG_MCP_Server__search_apis`（lang=skill）检索：schHiHiliteLabel / geGetSelSet /
   geIsValidHilightObject / hiSetTextHighlightColor / geAddHilightFig / geAddHilightPath /
   geAddHilightPolygon / geCreateHilightSet / gePushHilightStack / geGetCurrentWindowHilightSet /
   geCreateWindowHilightSet。
2. `RAG_MCP_Server__get_api_details` 拉详情：geGetSelSet / geAddHilightFig /
   geCreateHilightSet / gePushHilightStack / hiGetCurrentWindow / geGetEditCellView。
3. `SandBox_MCP_Server__run_code`（lang=skill, host=virtuoso）执行主程序 →
   `Highlighted MOS count = 0`（沙箱无打开窗口，`hiGetCurrentWindow()` 为 nil，但代码无语法错误可加载）。
4. `SandBox_MCP_Server__run_code` 跑自检 `hiClassifyMOS(termList)` →
   nmos4(GDSB)/pmos_rf(GDS)/nch(SDGB) 判 MOS；nd2(INAB-OUT)/inv(IN-OUT-VDD-VSS)/resistor/cap/BJT 排除。

## 关键产物（用户接受的最终 SKILL 代码）
```skill
procedure( hiIsMOSInst(inst)
  let( (terms)
    terms = nil
    when( and( inst inst~>cellView )
      terms = mapcar( lambda( (nm) upperCase(nm) ) inst~>cellView~>term~>name )
      and( member("G" terms) member("D" terms) member("S" terms) )
    )
  )
)
procedure( hiHiliteMOSInCurrentSch()
  let( (win cv hs sel insts mosList n)
    win = hiGetCurrentWindow()
    unless( win ... return(0) )
    cv  = geGetEditCellView(win)
    insts = cv~>instances
    mosList = setof( inst insts hiIsMOSInst(inst) )
    hs = geCreateWindowHilightSet(win) / gePushHilightStack
    foreach( inst mosList geAddHilightFig(hs inst~>dbId) )
    printf("Highlighted MOS count = %d" n)
  )
)
```
判定核心：**MOS = 端子名集合(大写)含 G∧D∧S**（按端子集，不按 cell 名子串，能正确区分
nmos4/pmos4/nch/pch/nch_rf/pmos_rf 与 nand2/nor2/inv/resistor/cap/BJT/diode）。

## 造题方式（B 档 synthesized）
真实 trace 的产物是 SKILL 脚本（用户接受），但 SKILL 无法在判分器里 subprocess 跑出有牙断言。
为满足「真跑候选 + 反硬编码隐藏 B」的判分铁律，把交付件做成可离线判分的 Python 工具
`hilite_mos.py`，它既(a)对原理图实例清单做 MOS 分类，又(b)生成可在 Virtuoso CIW 直接使用的
高亮 SKILL 脚本——SKILL 仍是用户面向的最终产物，Python 分类逻辑与 SKILL 的 `hiIsMOSInst`
判定逻辑一致（G/D/S 端子集）。

- **输入 A**（SUT 可见）：`schematic_fixture_A.json`（10 实例：M0/M1/M5/M2 为 MOS，余为非 MOS）
- **隐藏 B**（不进沙箱）：`schematic_fixture_B.json`（11 实例：N0/P0/N1/P1/N2 为 MOS，余 6 为非 MOS）
- **判分**：check.py 14 断言 a–n（subprocess 跑 `--classify B` 验分类 + 跑 `--generate-skill` 验 SKILL
  结构 + 反硬编码 A/B 实例名）。
- **退化/负样本**：空 zip、print-only、copy-A、hardcode-A、name-substr 全 FAIL。

case_id: `EDA-Eval-DesignFlow-SchematicMOSHilite-001` (schematic_netlist, L1, B synthesized)
