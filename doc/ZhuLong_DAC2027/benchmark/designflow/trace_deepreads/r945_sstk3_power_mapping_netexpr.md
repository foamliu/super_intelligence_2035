# Deepread: sstk3 — Virtuoso power-mapping net-expression (3-to-8 decoder)

**session**: 1787564069550_sstk3 (948 msgs / 3.0MB / 2026-08-24~26)
**user/host**: junxu @ hfeg0plg79 (also replicated on hfeg0plg17/hfeg0pkn005/hfeg0pjn200)
**match_count**: 1606 (virtuoso:2698 / schematic:2331 / cellview:1046 / dbopencellviewbytype:485 / ddgetobj:160 dominant)
**domain**: layout_virtuoso
**claimed**: r945 (fresh, not in any 4-shard ledger)

## 任务流（user 意图）

1. **U#0** `/virtuoso-cli 做一个三八译码器` — 用 stdcells_am 库（invx1 / and3x1）搭 3-to-8 decoder 原理图+符号。agent 写 SKILL 脚本 build_decoder.py，3 反相器 + 8 三输入与门（I0-I10），schCheck 0 错误，打开 schematic+symbol 窗口。完成（msg 77）。
2. **U#78** `参照其他电路的方式，power 使用 power mapping 的方式,而不是连线` — 把电源处理从显式连线改成 power mapping。**这是本 case 的核心意图。**
3. agent 调查 invx1 内部、BankLogic 电路，发现 power mapping = **net expression 属性**（`[@pin:%:globalNet!]`），类型 `netSet`。
4. **U#275** `所以你为什么还要设置 vcc 和 vss 的 power mapping` — 用户纠正：vcc/vss 直接连线，不该走 netSet。
5. **U#293** `vbp 和 vbn 不用吗？默认的不是 vbulkn 和 vbulkp 吗` — 用户问 bulk pin。agent 查证：invx1 symbol pin 叫 vbp/vbn（不是 vbulkp/vbulkn）；`inv` 内部单元（TECHLIB）的 pin 才叫 vbulkp/vbulkn，通过 net expression 映射到 vbp!/vbn!。cellview 级有 4 个 net expression：`[@vcc:%:vcc!]`/`[@vss:%:vss!]`/`[@vbp:%:vbp!]`/`[@vbn:%:vbn!]`。
6. **U#308** `你可以进入 BankLogic 这个电路以及它的子电路进行探索` — 深入探索 BankLogic power mapping 实际工作方式。
7. **U#349+** 后续转向 Python API 设计（instance properties / SchematicSession.open / check-save 拆分等）— 属于 virtuoso-cli 工具链开发，超出本 case 范围。

## 关键技术结论（power mapping 机制）

- **net expression 属性**：格式 `[@pinName:%:globalNetName!]`，例如 `[@vbp:%:vbp!]`。
- **属性类型必须是 `netSet`**（不是 `string`）—— schCheck 会报 "The type for the property 'vbp'...is not 'netSet'"。
- **vcc/vss（电源）**：直接连线到全局网络 vcc!/vss!，**不**设 netSet。
- **vbp/vbn（bulk）**：用 net expression 属性映射到全局网络 vbp!/vbn!（继承 cellview 级声明）。
- cellview 级 net expression 声明 + 实例级继承/覆盖。

## 合成决策（档B reframe fixture-driven）

真实任务要在 Virtuoso 里跑 SKILL 改原理图，但评测需离线可验。reframe 为：agent 写 `power_map_emit.py`，读 fixture JSON（library / convention{power_pins, bulk_pins, *_global_nets, *_handling} / instances[]），输出 power-mapping 赋值清单 JSON：bulk pin → netexpr_assignments（prop_type=netSet, net_expr="[@pin:%:globalNet!]", source=inherit），power pin → wired_pins（net=global, source=wire_direct）。

- env_A：stdcells_am，11 实例（I0-I10，invx1/and3x1），vcc/vss/vbp/vbn → vcc!/vss!/vbp!/vbn!。
- hidden B（check.py 内联生成）：CORELIB，8 实例（J0-J7，INVx2/NAND3x1/NOR2x1/AND2x1/OAI21x1），VDD/VSS/NBULK/PBULK → VDD!/VSS!/NBULK!/PBULK!。库名/pin 名/全局网络/实例名/cell/数量全异，反硬编。

## 子型正交

同 domain 已落库 case（VirtuosoDaemonReviewFix=daemon review-fix / VirtuosoCliNoInstanceJsonErr=错误诊断 / LayoutLabelArgOrderFix=label arg 顺序 / AetherLayerPurposeExplainer=Aether layer 用途）全正交。子型 "virtuoso_power_mapping_netexpr_emit"（power mapping net-expression 赋值清单生成）首例。
