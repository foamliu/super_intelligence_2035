# 深读笔记 — 3duob (ellawu) Calibre SVRF DFM SPEC FILL via-fill 规则生成

## trace 元数据
- session: `1789520357933_3duob.messages.json` (1.23MB, 47 msgs, 195 msg-records)
- user: ellawu @ hfeg0pkn005 (10.129.32.x), host 10.129.8.235/hfeg0plg103 (共享)
- mc=335, tools: calibre:508 schematic:14 virtuoso:5 pyAether:3 (keywords cmos:3023 netlist:1320 aether:740 schematic:622 analog:178 hspice:76 pyaether:46 mixed-signal:45)
- agent: cline (lead), cwd /home/ellawu
- domain: physical_verify (Calibre SVRF DFM SPEC FILL 规则编写)

## 用户意图流 (逐字 USER 轮)
- USER#1 (msg#0 @1789520358360) **提出目标**：「DFM SPEC FILL SHAPE」
- USER#2 (msg#31) 原理问：「M1层金属和M2层金属上打孔的原理是什么」
- USER#3 (msg#33) 语法问：「在svrf中用DFM SPEC FILL对MA和M2层打孔怎么写」
- USER#4 (msg#35) **完整规则规格**：
  ```
  F 90:0(绘图)、90:16(平仓)、90:24(止损)
  精确版-V1尺寸:0.045微米×0.045微米,密封环区域除外
  Exact -V1尺寸2(矩形图案):0.045微米×0.09微米,
  最小值-V1至V1区间 密封环区域除外
  最小值-V1空间中与V1的欧式距离超过5个V1单位的相邻V1
  最小值-M1包围V1
  最小值-被M13D包围的V1。M13D定义:短线末端长度<0.108um
  Min-M1封装V1; M1线长介于0.108um至0.461um之间,且M1相邻长度≥0.476um
  最小值-M1包围V1,M1凸角对应V1角
  Min-M1凹角包围V1。
  最小值-M2包含V1
  ```
- USER#5-9 (msg#37/39/41/43/45) **参数确认**：M2 enclose V1 → 0.025 → 改 0.0025；V1-to-V1 space → 0.225；最终 M2 enclose=0.0025µm, M1 enclose=0.0025µm

> A-档 seed 候选：USER#1+#3+#4（提出目标 + 语法请求 + 完整规格，未给根因/修复）。但精确数值 (0.0025/0.225) 来自 USER#5-9 的确认，A-档不可自洽 → 走 **B-档 synthesized**：把全部确认值打包成 rule_spec.txt，要求 SUT 写生成器读规格产 SVRF deck。

## agent 工具链
- read_files：读用户提供的规则文本（无附件，纯对话）
- editor/run_approved_command：写 SVRF 规则迭代多版（v1 假设 spacing 0.09→STEP 0.135；vFinal 用确认值 0.225→STEP 0.270）
- 无真实 calibre 运行（纯规则编写/讲解）

## gold (人工复核 msg#46, vFinal)
最终 SVRF 规则文件 `calibre_M1M2_ViaFill.rule`，关键结构：
- `INCLUDE "/apps/imctf/runset/calibre/cxmtG5_CIP/current/common/calibre.layer"`
- 层声明：MA=MA_drawing, M2=M2_drawing, V1=LAYER 90 0, V1_flat=LAYER 90 16, V1_stop=LAYER 90 24, seal_ring=LAYER seal_ring_layer, block=OR PG_drawing AT4_DUMMY2
- 参数（用户确认）：V1_SIZE=0.045, V1_REC_Y=0.090, V1_SPACING=0.225, V1_STEP=0.270, V1_STEP_RY=0.315, M2_ENC_V1=0.0025, M1_ENC_V1=0.0025, M1_3D_LEN=0.108, M1_LEN_MIN=0.108, M1_LEN_MAX=0.461, M1_ADJ_LEN=0.476
- 候选区：cand = MA AND M2；cand NOT V1/V1_flat/V1_stop；cand NOT seal_ring；cand NOT block；SIZE cand BY -M2_ENC_V1；SIZE cand BY -M1_ENC_V1；AREA cand >= 0.005
- DFM SPEC FILL V1_fill_sq (FILL MODE FILL_OPEN_AREAS)：WINDOW SIZE 0.045 BY 0.045, STEP 0.270 BY 0.270, ORIGIN OFFSET 0.0225 0.0225
- DFM SPEC FILL V1_fill_rec：WINDOW SIZE 0.045 BY 0.090, STEP 0.270 BY 0.315, ORIGIN OFFSET 0.0225 0.0225
- V1_fill = V1_fill_sq OR V1_fill_rec；V1_merge = V1 OR V1_fill
- DRC 验证：M2_enc_v1_error=ENC V1_fill M2 < 0.0025；M1_enc_v1_error=ENC V1_fill MA < 0.0025；V1_spacing_error=EXT V1_fill < 0.225 OPPOSITE；M1 3D/line-mid/convex/concave checks
- GDS 输出：DFM RDB GDS "M1M2_ViaFill.gds" V1_fill 90 0 APPEND _vfill NOEMPTYDB（+ merge/errors）
- DRC SELECT CHECK x3

## B-档 synthesized 设计
- 交付物：`viafill_svrf_gen.py`（python 生成器，stdlib-only），读 `rule_spec.txt` + `layer_map.txt`，emit `calibre_<via>_<metal1><metal2>_ViaFill.rule`
- 接口：`python3 viafill_svrf_gen.py --spec rule_spec.txt --layermap layer_map.txt --out rule.rule`
- check.py：解 submit.zip → 找生成器 → subprocess 跑 A 规格产 A.rule → 解析断言 (a-t) → subprocess 跑 B 规格产 B.rule → 跨输入守门 (u)
- 不依赖 live calibre（纯 SVRF 结构/参数静态校验 + 生成器执行）
- hidden B：V2/M2-M3, 层 91:0/16/24, size 0.050, rect 0.050×0.100, space 0.250, enc 0.0030, M2_3D 0.120, M2 len 0.120-0.500, adj 0.520, block 不同 → 杀硬编码 A 的 90/0.045/0.225/0.0025/0.270

## 21 条断言（k=21，对应 check.py (a)-(u)）
①(a) zip 含 viafill_svrf_gen.py ②(b) 生成器 A 跑 exit0 产 .rule ③(c) A.rule 含 INCLUDE ④(d) V1 drawing LAYER 90 0 ⑤(e) V1 flat LAYER 90 16 ⑥(f) V1 stop LAYER 90 24 ⑦(g) MA+M2 层声明 ⑧(h) 候选区 MA AND M2 ⑨(i) 排除已有 V1 三子层 NOT ⑩(j) 排除 seal_ring ⑪(k) 排除 block(OR PG_drawing AT4_DUMMY2) ⑫(l) DFM SPEC FILL + FILL_OPEN_AREAS ⑬(m) 方形 WINDOW SIZE 0.045 BY 0.045 ⑭(n) 方形 STEP 0.270 BY 0.270(=size+space 计算非硬编码) ⑮(o) 矩形 WINDOW SIZE 0.045 BY 0.090 ⑯(p) 矩形 STEP 0.270 BY 0.315 ⑰(q) M2 enclosure DRC ENC<0.0025 ⑱(r) M1 enclosure DRC ENC<0.0025 ⑲(s) V1-to-V1 spacing DRC EXT<0.225 OPPOSITE ⑳(t) GDS 输出 DFM RDB GDS ㉑(u) 跨输入守门 B.rule: LAYER 91 0 + STEP 0.300 BY 0.300(0.050+0.250) + SIZE 0.050 + ENC<0.0030

## 备注
- 真实 agent 多轮迭代（v1 STEP 0.135 错 → vFinal 0.270 对），体现"参数需用户确认"过程；B-档把确认值前置进 spec，简化为单轮生成
- 无附件资产（trace 是纯对话）→ B-档自造 rule_spec.txt + layer_map.txt 作 A 输入
- gold 依赖 live calibre 运行验证 → 不可行（license/路径）→ 静态 SVRF 结构校验 + 生成器执行 = L1-boundary
