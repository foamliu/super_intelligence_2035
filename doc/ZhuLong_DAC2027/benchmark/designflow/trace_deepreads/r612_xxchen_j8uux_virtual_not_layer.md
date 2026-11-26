# deepread r612 — j8uux (xxchen @ hfeg0plg19, mc=468, physical_verify)

**session**: 1794636165058_j8uux.messages.json (2.2MB, 350 msgs, 183 user / 167 assistant)
**host**: hfeg0plg19 (10.129.x), user xxchen
**ledger status prior**: parked (r577 "known-reject xxchen top500-fresh drc-dominant")
**reaudit (r590)**: 可造 — 旧判 drc-dominant 现合法（2026-11-15 令）；xxchen 已知 produce-task 作者

## trace 结构

handoff/续会话（首条 user msg = auto Context summary，承接前一会话的 space_var connect overlay 修复）。

**真实 user_input（4 条有内容，其余 179 条为空/tool-result/skill-injection）**：

- **UI#1 (idx 61)** 「VIRTUAL解析错了：= NOT。boundry-NW,AVT → 两个 NOT 组 {sub:NW}、{sub:AVT;ARRAY}。注意 这里也是符合 layer;purpose 这种描述规则的。finalize阶段，realPW 上面就是只有 boudnry_rect 和（NW 或 AVT;ARRAY）层，不需要绘制PW;drawing层。check 值就是当前检查的 rule里面的 value值。临时层，可以保留，后续的一些流程，方便读取该临时层的形状和边框。」—— **核心 produce-task**（提需求 + 指出根因方向，但未给完整修复方案）
- **UI#2 (idx 83)** 「没有其他要修改的了，开始东西修改吧。」—— 批准开始
- **UI#3 (idx 202)** 「取反这个操作没有实现，你需要实现的效果是 0;0 层 + 8;0 层 图形刚好是 = bordlayer(4002;51) 层。但是你现在是 0;0 层 = 8；0 层。」—— 纠错：取反没实现（0;0 == 8;0，应为互补）
- **UI#4 (idx 293)** 「0;0和NW的取反关系反了，0;0层作为临时层，用于绘制原始的pattern绘制，按照正常的shape和space进行绘制。NW或AVT才是取反后层。」—— 纠错：0;0=原始pattern，NW/AVT=取反互补层

## agent 工具链

- list_allowed_files ×4 / read_files ×36 / editor ×74 / run_approved_command ×57 / ask_question ×4
- 读取 DRC_pattern_tool/0.5/device_rule1/ 下 space_var.py / config_parser.py / qa_config_deck / docs/superposition / tasks 等
- editor 修改 space_var.py（add_layer1/2_rect/polygon NOT 分支 + _draw_not_complement）+ 7 个文档（update_history/PROJECT/todo/lessons）

## 核心算法（gold = space_var.py 修改，在 xxchen 私有 workdir，沙盒不可达）

VIRTUAL NOT 取反操作：
- `boundry-NW,AVT;ARRAY` → 两个 NOT 组 {sub:NW}、{sub:AVT;ARRAY}（`;` 是 layer;purpose 名的一部分）
- temp layer `0;0` = 原始 pattern（正常 shape/space）
- sub layer NW=`8;0`、AVT;ARRAY=`10;7` = complement = boundry_rect − 0;0 shapes（`gdspy.boolean(boundry, 0;0, "not", precision=1e-7)`）
- NOT 性质：`0;0 ∪ sub == bordLayer(4002;51)` 且 `0;0 ∩ sub == ∅`
- 45° pattern：互补区与原始 pattern 共用斜边顶点，precision=1e-7 避免默认 0.001 重舍入留缝隙

## case 合成（B档 mock-behavioral reframe）

源码在 xxchen 私有 workdir（沙盒不可达）→ asset_fidelity=synth。
参数化纯 Python3 `virtual_not_layer_gen.py <config.json> <out_report.json>`（stdlib only）：
解析 virtual_spec（拆 boundary 名 + NOT 组，`;` 非分隔符）+ patterns（rect/polygon）→ temp_layer(0;0)=原始 pattern + sub_layers=complement（矩形精确减法 / 多边形面积守恒）+ verification（union/intersect/area_conservation/NOT 性质）→ 确定性 JSON(sort_keys)。

**输入 A** (PW_S_014_00_p, boundary 30×16, 2 rect, spec boundry-NW,AVT;ARRAY, NW=8;0/AVT;ARRAY=10;7)
**隐藏 B** (AN_S_007_03_c, boundary 40×20, 2 rect + 1 polygon(45°三角), spec boundry-PSDM,NSDM, PSDM=12;0/NSDM=14;0) — 不同 boundary/pattern/cell/sub_layer 反硬编
**隐藏 B2** (ISO_S_002_01_b, boundary 24×12, 3 rect, spec boundry-NW 单 NOT 组, NW=8;0) — 单组 vs 双组反硬编

**16 条 a-p**：结构2(a:zip+py_compile / b:B exit0+顶层键) + B pattern 2(c:count==3 / d:area==192) + B NOT 性质 3(e:complement_area==608 / f:union==800 / g:intersect==0) + B spec 解析 2(h:sub_layers==2 / i:code 匹配 map) + B 矩形减法 2(j:complement_rects 不重叠 / k:总面积==632) + B 多边形 1(l:polygon area==24) + B2 2(m:单 NOT 组 / n:complement_area==198+code==8;0) + 确定性 1(o:两跑字节一致) + 反硬编 1(p:B≠A boundary+B2≠B cell)。

自验 ref 16/16 PASS✓；3 neg(naive_empty/print_expected/deleted_core)全 FAIL✓ NEGATIVE_SELFTEST ALL-FAIL-OK✓；§4.9 (a)(b)(c)三假全 FAIL✓；embedded test==disk roundtrip✓；bool(check)=True✓；k=16≥8✓。

**新子型**：virtual-not-layer-gen（complement-geometry / layer-boolean-ops），C L1-portable-script 第 11 子型（r609 后再扩 1 子型，form 空间仍 expanding）。
