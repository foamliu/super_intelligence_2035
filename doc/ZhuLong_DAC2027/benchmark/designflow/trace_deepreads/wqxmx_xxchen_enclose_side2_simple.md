# Deepread — wqxmx (xxchen@hfeg0pkn003, mc=251)

- **session**: `/home/xxchen/.cline/data/sessions/1794970621235_wqxmx/1794970621235_wqxmx.messages.json` (846KB, 158 msgs)
- **scan**: `drc:788;.gds:76;rtl:16;pdk:5;dbcreatelabel:4;dbcreatepath:1` → pure C-domain physical_verify/drc+gds
- **cwd**: `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`
- **agent**: PDK 专家（AGENTS.md 定义），policy-engine enforcing

## 真实任务（MSG 7，自含子任务）

用户 xxchen 贴 QACELL 规则行：
```
QACELL CoreM0C_ENC_006_00    enclose_side2     M0C_FINAL_CORE->PC      0.026    {lay1size 1.0x3.0} {lay2size 0.08x0.104} {excludeRegion PG} {check45dgree False}  {enclose_side1 0.025}
```
提出三点优化要求：
1. 当前 `enclose_side2` 只支持 device rule，需新增 **simpleRule**（layer-based）支持，借鉴 device rule pattern。
2. 支持**自动识别 lay1size 和 lay2size 的长短边**。
3. `check45dgree False` 跳过 45-degree pattern。

## 规则语义（manual/enclose_side2.md，MSG 10）

**adjacent side2 / LDR 判据**："PW enclose mos AA 两边不能同时不满足该 rule"。
- 只在某相邻两边（角点）**同时**包覆 < value 时判违规。
- 单边不足但相邻边达到 value（"单边补满足"）→ good。
- good: 矩形四面环绕(good1)、45 度角切(good2)、exclude 器件变体(good3/4)、单边补满足(good5)。
- bad: 双邻边不足(bad2)、角切不足、L 形凹角、双台阶、半边露切(bad6)。

## agent 工具链（MSG 0-65）

读 AGENTS.md/PROJECT.md → list_allowed_files → read manual/enclose_side2.md → read device enclose_side2.py → read enclose/simple/enclose_simple.py + good_pattern/1/pattern1.py → read enclose_short/simple/enclose_short.py + good_pattern → read function_common.py / pattern_common.py / classify_rule_type.py / plugin_loader.py → grep qa_config_device.txt for side2 cfg → grep sizes → read manual_html → **edit enclose_side2/simple/enclose_side2_simple.py**（多次 edit，MSG 55-67 新建并迭代）。

## 产物（MSG 65 final enclose_side2_simple.py）

`Side2SimpleContext` + `_parse_lay_size(options, key, default)`：
- 解析 "{key WxL}" → (short, long)，`return (a,b) if a<b else (b,a)` 自动排序（要求 #2）。
- inside = layer2 (PC) rect sized from lay2size（short×long），outside = layer1 (M0C_FINAL_CORE)。
- simpleRule（layer-based，非 device）（要求 #1）。
- Pattern 库 mirror device 版：good1(全 value)/good2(L/R=value,T/B=side1 PASS)/bad1(全 side1)/bad2(L+B short)/bad3(45° 切角, **check45dgree False 跳过**, 要求 #3)/bad4(T+R short)/bad5(T+L short)。
- enclose_side1 floor：每边 >= side1。
- check45dgree 用 to_bool 解析，False 时 bad3 不入 list。

## case 合成（EncloseSide2SimpleGen-001，physical_verify/drc_pattern_enclose_side2_simple）

- **离线 Python 合成**（real gdspy env 不可达），交付 `enclose_side2_simple_gen.py` 读 config.json 输出 patterns.json（JSON list）。
- **判分设计**：公开 config_a(trace verbatim: value 0.026/lay1size 1.0x3.0/lay2size 0.08x0.104/side1 0.025/check45dgree False/excludeRegion PG → 6 patterns bad3 跳过) 给 SUT 开发；隐藏 config_b(value 0.040/lay1size 2.0x0.5 反序/lay2size 0.2x0.1 反序/side1 0.020/check45dgree True/excludeRegion 空 → 7 patterns) 主判分；隐藏 config_c(value 0.020/lay1size 0.8x1.6/lay2size 0.12x0.06 反序/side1 0.015/check45dgree False/excludeRegion NW → 6 patterns) cross-input anti-hardcode guard。
- **k=15 全闸门通过**：ref PASS + 4neg(empty cond3/print_only cond4/hardcode_a cond5/delete_core cond13)全FAIL distinct + §4.9 三假全FAIL + k一致(15==15) + 真跑 subprocess + hidden B/C + 反硬编 cross-input + 独立临时目录 + 泄漏隔离 + 决定性。
- check() 独立重算每边包覆量（layer2_rect bbox vs layer1_polys bbox），验证 good(无相邻对同时<value)/bad(>=1 相邻对同时<value) + side1 floor + highlight + 45° gating + 对角边。
- **区别**：C 域 physical_verify DRC pattern 子型 enclose_side2 adjacent-side2 simple-rule 首例，与 EncloseSide1PatternGen / EncloseShort3DPatternGen / WidthLengthQaPatternGen 产物/断言/trace 全不同（本 case 解析 lay1size/lay2size 长短边 + LDR adjacent-side2 相邻边判据 + check45dgree 45° 跳过）。
