# 深读 1794825699351_mxlxx — xxchen@hfeg0plg19 (mc=341, physical_verify)

**session**: `/home/xxchen/.cline/data/sessions/1794825699351_mxlxx/1794825699351_mxlxx.messages.json` (1.32MB, 261 msgs)
**扫描 kw**: drc:756;.gds:155;pdk:7;pex:5;rtl:4;gdsii:4;dbcreatepath:3;dbcreatelabel:2
**工具**: editor 45 / read_files 36 / run_approved_command 27 / list_allowed_files 17

## 真实任务（U#9 逐字原文，produce task）
> ### 新增function: width_length
> 1) LDR 描述：CoreM0C_W_001_01Min - M0C and M0C_markcore width when M0C and M0C_markcore length >=390um >=0.390
> 2）manual qa GDS 参考：无，可参考 space的，允许根据shapeFeature进行额外补充
> 3）config 配置: QACELL CoreM0C_W_001_01 width_length M0Cx 0.39 {ref_length 390}
>    VIRLAYER M0Cx M0C;CORE,M0C;ADDM0C,M0C;markcore
> 4）LDR解释: 基于length检查width宽度, condition: 必须满足length的最小值
> 5）参数: ref_length = pattern的长边的condition条件
> 6) 其他要求: pattern的一边是平的，另一边带有垂直方向的短leg；其他pattern可自由发挥。

U#165 追加（验证）: "读取QA.gds，分析当前pattern是否符合要求"
U#177/U#195 追加（框架bug修复）: 单layer规则不需要 l1×l2 笛卡尔积遍历，区分单/双layer

## 产出（agent 完成）
- `QA_Pattern_tool/function/width_length/simple/width_length.py` — function entry (width_length_context + draw_trace helper)
- `function/width_length/simple/good_pattern/1/long_trace_rule.py` — good1: 长走线 on-rule (length=ref_length, width=value, 平底+顶部垂直短leg)
- `function/width_length/simple/good_pattern/2/short_narrow_passes.py` — good2: 短走线 length-gating 通过 (length<ref_length, width<value)
- `function/width_length/simple/bad_pattern/1/long_narrow_trace.py` — bad1: 长走线 off-rule (length=ref_length, width=value-step, highlight rect)
- `manual/width_length.md` + `update_history.md` (entry 36)
- 框架修正 `script/config_parser.py` + `cell_builder.py`: 单层(无 `->`)时 `single_layer=True`，layer2 轴折叠为 1 组，消除多子 VIRLAYER 的 l1×l2 冗余 (entry 37)
- 临时验证: `temp_script_run/verify_width_length.py` / `analyze_width_length_gds.py` (gdspy 读 GDS 校验几何)

## 判分子问题（用于 benchmark case）
width_length QA pattern 生成本身 = 纯 Python 离线判分：给定 config(ref_length/value/layer/purposes)，生成 .qap manifest 含 good1/good2/bad1 三图案，check.py 从多边形顶点 bbox 独立复算 length/width 校验规则不变式 + 工程师要求(平底+垂直leg) + hidden B 反硬编。

## case
`EDA-Eval-DesignFlow-WidthLengthQaPatternGen-001` (physical_verify / width_length_qa_pattern_gen, k=12)
