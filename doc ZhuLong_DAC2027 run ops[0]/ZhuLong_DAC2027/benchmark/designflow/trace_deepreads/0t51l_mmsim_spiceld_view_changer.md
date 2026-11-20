# trace_deepread: 0t51l — yuankong @ .75 (hfeg0pkn047) — schematic_netlist

- **session**: `1793867708362_0t51l.messages.json` (mc=93, 58 msgs)
- **user**: yuankong (also has dup session `1793865966161_rkdu8`, 30 msgs, identical U#0–U#2)
- **domain**: schematic_netlist (DDR5 m384_Meg netlist + mmsim.ini config view-bind)

## 对话流（user 意图 → assistant 工具链 → 关键产物）

- **U#0**「/proj/drcpa/V0/libs/drcpa_top/DDR5TOP/config_SpfBA_trans/mmsim.ini,记住这个路径文件先不分析，它是抽网表到配置文件」— setup（识别 mmsim.ini = 抽网表配置）
- **U#2**「/proj/.../Netlist_SpfBA_20261104PM/netlist 这是网表文件，先不分析」— setup（识别 netlist 文件）
- **U#4**「%28drcpa_array\\m384_Meg\\schematic%29.Imarray_0="schematic;;;" … 在配置文件中除了指定到msa是schematic的，其余都是spiceld的，找出他们在网表哪一行」— 定位任务（在 mmsim.ini [InstBind] 中 view=schematic 的实例，找出其在 netlist 的行号）。assistant 写 find_schematic_insts*.py 经 4 轮迭代：发现网表实例带 `X` 前缀（`XImarray_N`），多行 `+` 续行，最终定位 8 个 schematic 实例（Imarray_0/1/34/35/36, Imsaq_0/34/35）于 .SUBCKT m384_Meg 块内（L255355–L268044）。
- **U#29**「Self=drcpa_top.DDR5TOP.config_Vcap_trans … 你说的对这个才是它的配置」— 用户确认正确配置是 config_Vcap_trans（非 SpfBA_trans），[InstBind] 中 m384_Meg schematic 名单 8 个，与磁盘一致。
- **U#36** ★「**我想让你帮我写个脚本可以把指定路径下的netlist的Imsaq_1和Imarray_2从spiceld改成schematic，并在代码后面加上\*\*\*ky_halfdensity方便备注**」— **A-faithful produce-task**（纯提需求，未给根因/修复）。assistant 经多轮 inspect_netlist_*.py / map_inst_models.py 摸清规律：spiceld 实例引用的 subckt 名带 `_spiceld` 后缀（如 `array11Meg_E_CCR_spiceld`），schematic 实例引用不带后缀（如 `array11Meg_E_CCR`）；"spiceld→schematic" = 去掉 subckt 引用末尾 `_spiceld` 后缀。Imsaq_1 引用 `msaq_O`（无后缀，存在歧义，trace 末尾 assistant 询问确认，未完成脚本）。

## A-faithful 合规性
- U#36 = 提出需求（写脚本改视图+加备注），非根因/修复轮 → A-faithful ✓
- 真实 /proj netlist + mmsim.ini permission-denied 不可附加 → **B-grade synthesized**（资产 A 为合成 SPICE netlist，金标为通用视图变换脚本）
- trace 末尾用户未明确接受结果（assistant 询问 Imsaq_1 歧义）→ 金标取通用正确解（去掉 `_spiceld` 后缀），断言对事实（结构/后缀/计数/marker），不对措辞

## 合成要点
- 资产 A netlist_A.sp：.SUBCKT m384_Meg 块含 Imarray_N / Imsaq_N 实例（多行 `+` 续行，续行末尾 token = subckt 名）；schematic 无后缀 / spiceld 带 `_spiceld` 后缀；target = Imarray_2（array11Meg_E_CCR_spiceld）+ Imsaq_1（msaq_O_spiceld）；marker = `***ky_halfdensity`
- 隐藏 B netlist_B.sp：m512_Meg 块，target = Imarray_5（blk_E_CCR_spiceld）+ Imsaq_3（senseq_O_spiceld），marker = `***ky_fullspeed`，非目标 spiceld = Imarray_6/Imsaq_4
- 隐藏 B2 netlist_B2.sp（cross-input guard）：m256_Meg 块，target = Imarray_7（tile_E_CCR_spiceld）+ Imsaq_5（senseq_E_spiceld），marker = `***ky_highspeed` — 反 hardcode-B / print_only
- 金标 change_view.py：CLI `<netlist> <inst1> <inst2> <marker>`，定位 X<inst> 块（含 + 续行），去掉续行末尾 subckt 名的 `_spiceld` 后缀，末尾追加 marker 行，stdout 输出
- check.py 14 条件 a-n（zip/import、py_compile、B exit0、两 target 剥离、非目标保留、schematic 不变、marker 末尾唯一、实例计数、head 节点不变、恰为后缀剥离、B2 跨输入、sys.argv、确定性）

## 教训
- spiceld/schematic 视图在 SPICE 网表中以 subckt 引用名 `_spiceld` 后缀区分，是 schematic_netlist L1 可验好范式
- 多行 `+` 续行结构：subckt 引用是续行块最后一行最后一个 token；脚本法须按 `X` 前缀+`+` 续行切分实例块
- B2 cross-input guard 用不同 target/marker/subckt 名 + 不同 block，是反 print_only/hardcode-B 的关键
