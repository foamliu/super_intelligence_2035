# r1106 deepread — a9yov (junxu@hfeg0pkn005, mc=65, characterization)

session: `1795137755682_a9yov.messages.json` (407 msgs / 1.32MB) on 10.129.2.14 (hfeg0pkn005)
user: junxu · domain: characterization (DRAM array spice_sim/char)

## 真实任务（用户意图）

DRAM array（`V0_ArrayG5` / `dlgot`）characterization：array 由若干 `XImsax512` SAQ
block 串联构成，中间夹一个 `XImsax320` 边界 block。每个 block 有 `Csl<idx>` 位、
`Io<g>` I/O group 端口、`EqIo`/`RdEn`/`WrEn`/`RwEnN` 控制端口。老 deck 前 8 个 `EqIo`
的 `.meas` 定义了 `Io→EqIo` 对应规则 + 每 eqio 采样的 5 个 CSL bit。

用户要：梳理 `Csl bit ↔ EqIo/RdEn/WrEn/RwEnN` 对应关系（`RdEn/WrEn/RwEnN` 与 `EqIo`
同号、"同理"）。难点 = `XImsax320` 边界 block 横跨两个 `EqIo`，bit 按 `Io` group 分属
不同 eqio，必须按 bit 级拆分。

## 对话流关键节点

- U#1 会话压缩继承上下文（tCCD measure pipeline）
- U#4 「为什么 csl 测量项只有一个，eqio→csl 只有 8 bit？csl 应有 44 bit；不同 csl 对应
  不同 eqio，rden/wren/rwenn 同理，先梳理对应关系」← 核心意图
- U#5-8 用老 deck 映射关系，老 deck = 现在的 .sp 前面内容；老 deck 没这些信号但和 eqio 类似
- U#9 翻另一会话 oc1gr 拿对应关系
- U#10-12 看 netlist，io 跟 csl 对应 → 推出 csl 跟 eqio 等的对应
- U#14 「516/551/586/589 应对应 eqio7, io7 和 io8」← 边界 4 bit 线索
- assistant 写 7+ python/shell 脚本（derive_final_map.py / verify_final_map.sh /
  probe_gap_516.sh / probe_msax320.sh）解析 netlist、交叉验证映射

## 最终对应关系（assistant 推导）

- io→eqio 规则（从 deck `.meas`）：io0/1→eqio1, io2/3→eqio3, io4/5→eqio5,
  io6/7/8→eqio7（分水岭，3→1）, io9/10/11→eqio10, io12/13→eqio12, io14/15→eqio14,
  io16/17→eqio16
- 8 个 XImsax512 block（csl 0-128 / 129-257 / 258-386 / 387-515 / 596-724 / 725-853 /
  854-982 / 983-1111）各管一个 eqio
- XImsax320 边界 block：bits 516/551/586/589，io=[8,9]，eqio=[7,10]；io8→eqio7,
  io9→eqio10 → 516/551→eqio7, 586/589→eqio10（横跨两个 eqio）
- 每 eqio 采 5 bit（如 eqio16: 0/63/64/127/128）

## reframe

`saq_csl_eqio_mapper.py <netlist.sp> <old_deck.sp> <out.json>`：解析 netlist 的 BLOCK
行 + deck 的 `.meas`/`sampled_csl` 行，推导完整 bit→{eqio,rden,wren,rwenn} 映射 +
boundary 拆分。L1 纯 Python，无 EDA 依赖，domain=characterization。

## case 落库

`EDA-Eval-DesignFlow-SaqCslEqioMapDeriveProduce-001`（cases/B/，k=11 a-k）
- A：junxu 真实结构（8 msax512 + 1 msax320 边界 4bit 拆 2-2，8 eqio 1/3/5/7/10/12/14/16）
- hidden B：6 msax512（100bit csl range）+ 1 msax320b 边界 6bit 拆 3-3，8 eqio
  2/4/6/8/10/12/14/16（eqio 8/10 仅边界无 sampled_csl，per_eqio_sampled 仅 6 键）
- check.py 11 条：a(zip+compile) b(B exit0+JSON) c(9顶层键) d(io_to_eqio精确)
  e(total_bits/n_blocks/n_eqio) f(blocks精确) g(**boundary eqio_split 核心齿**)
  h(bit_map全bit精确) i(per_eqio_sampled+gap_bits) j(anti-hardcode A token)
  k(3-seed确定性)
- 3 negs：neg1_empty(→a) / neg2_print_only(→b) / neg3_core_removed(边界当单eqio→g/h)
- 自验：REF 11/11 PASS ✓; negative_selftest 3/3 FAIL ✓; 3-seed ✓
- k_rationale=11==k_check=11 ✓

## 台账

a9yov claim→mark case ✓（covered 572→573）

## 备注

- 真实 netlist 文件（/shprojruns/dlgot/.../netlist）已被清理不可访问，故用 config 驱动
  生成器 `gen.py` 产出同构 synthetic netlist+deck+oracle，结构忠实复刻 trace 推导的
  对应关系（同 8 eqio、同分水岭 io6/7/8→7、同边界 4bit 拆分）
- B 与 A 五重异构：block 数(6/8)、csl range size(100/129)、边界 bit 数(6/4)+拆分(3-3/2-2)、
  eqio 编号(偶 2..16 / 奇 1..16)、per_eqio_sampled 键数(6/8)
