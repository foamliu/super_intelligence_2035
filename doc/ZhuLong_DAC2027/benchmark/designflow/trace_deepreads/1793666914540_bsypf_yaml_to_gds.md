# Deepread — 1793666914540_bsypf (e0047488 @ hfeg0pkn002, mc=98, layout_aether)

- **session**: 1793666914540_bsypf, 127 msgs, 733KB messages.json
- **user**: e0047488 (NEW), host hfeg0pkn002 (10.129.2.11)
- **keywords**: .gds:124; drc:123; aether:96; gdsii:46; pyaether:43; techfile:20
- **tools**: 41 pyAether; 2 dbCreateRect; 1 cellview

## 用户原始意图（逐字）
> 我从windows端迁移来一个项目QA pattern，项目目的是通过LLM的语义理解能力支持，自动解析design rule规则，设计相应的验证DRC翻译的QA pattern。目前的问题是，项目端的输出是json文件，位于out目录下，其形式是内部包含一系列layer构成的图形的坐标。我需要设计一个脚本文件，可以将其对接到Aether软件中，将其画成.gds的layout文件，请你帮我分析

（注：实际输出为 YAML，位于 `QA_pattern_repo/out/input_DR_m1/`，文件名 `good_*.yaml` / `bad_*.yaml`）

## 项目结构（assistant 探索）
- `/home/e0047488/QA_pattern_repo/` — DRC QA Pattern 智能生成器
- `out/input_DR_m1/` — good_*.yaml / bad_*.yaml（每文件含多层图形坐标）
- `out/drafts/reviewed/` — 规则草稿 YAML
- `skill/scripts/spec_engine.py` — 规则引擎（write_rule_v7: apply_directions + LayoutPlacer.place_all + abs_shapes）
- `skill/scripts/drc_qa/{config,shapes,geometry,layer_loader}.py`
- `viewer/scene_api.py`

## YAML 输出格式（真实，从 good_M1.W.3.yaml / bad_M1.W.3.yaml / good_M1.EN.1.1.yaml 等读取）
```yaml
common:
  grid: 0.0001
  layers:
    M1: {layer: 20, datatype: 1}
    SEALRING: {layer: 179, datatype: 1}
    TDV: {layer: 62, datatype: 1}
    V0G: {layer: 51, datatype: 1}
    M1A: {layer: 20, datatype: 2}
    OCCD_FM: {layer: 178, datatype: 2}
    OCOL_S: {layer: 178, datatype: 1}
  label: {layer: 888, texttype: 888}
rule_name: M1.W.3
kind: good          # 或 bad
layer: M1
type: WIDTH         # WIDTH / SPACE / EN_ASYM / Area / DENSITY
constraint: <= 0.25
waive_regions: [SEALRING]
defaults: {angle: 0, shape: rect}

good:               # 或 bad:
  critical:         # 场景类别 (critical / good_1g / premise_unsat / bad_1g / bad_30pct)
    W: 0.25
    areas:
    - direction: '0'        # '0' 或 '90'
      origin: [0, 0]
      bbox: {w: 0.35, h: 0.5}
      shapes:
      - layer: M1
        gds: {layer: 20, datatype: 1}
        type: rect           # rect (xy=[x0,y0,x1,y1]) 或 polygon (xy=[x0,y0,x1,y1,...] 扁平)
        xy: [0, 0, 0.25, 0.4]
        purpose: drawing
      labels:
      - type: label
        text: M1.W.3 critical
        xy: [0.125, 0.43]
        gds: {layer: 888, texttype: 888}
```

**关键观察**：
- shape.type 全部为 `rect`（input_DR_m1 样本中无 polygon，但 assistant 设计支持 polygon：xy 扁平列表）
- 一个 area 可含多 shape（多 layer，如 EN 规则 M1+V0G，premise_unsat 含 SEALRING+M1 或 TDV+M1）
- 一个 category 可含多 area（如 premise_unsat 4 areas）
- 一个 YAML 含多 category（good: critical/good_1g/premise_unsat；bad: bad_1g/bad_30pct）
- label.gds 用 {layer, texttype}（非 datatype）
- 坐标为绝对坐标（µm），grid 0.0001

## assistant 工具链 / 尝试
1. list_allowed_files + read_files 探索项目结构、读 YAML、spec_engine、drc_qa/*
2. SandBox_MCP_Server__run_code 试 pyAether sandbox → **Connection refused**（sandbox 未起，10.129.8.229:33092）
3. 选 gdstk 方案（纯 Python GDS 库），写 `yaml_to_gds.py`：层级 Cell <rule>_<kind> → <category> → shapes，支持 rect/polygon/label，合并或分文件输出
4. editor 多次编辑（文件 >6000 字符限制，分块 insert/replace，多次 path 校验失败、重复块清理）
5. 试装 gdstk：pip3 ImportError → python3 -m pip 网络不通（DNS 失败）→ 检查 wheels/（无 gdstk wheel）→ **Python 3.6.8，无 gdstk，无网络**
6. 决定改写为**纯 Python GDSII 写入器**（仅 struct + pyyaml），但 editor 输入超限、删文件失败（python-runner 加载旧文件触发 gdstk import guard），session 在 msg 126 中断

## 用户最终接受产物
**无** —— session 在 assistant 改写纯 Python GDSII 写入器过程中结束，未产出可运行脚本，用户未明确接受最终 artifact。

→ 不适用 A-档（trace-faithful），取 **B-synthesized**：grounded on 真实 YAML 格式 + 真实项目结构 + 真实坐标，合成"YAML → GDSII 版图转换器"任务。

## 与既有 case 的 DISTINCT
- r213 InvLayoutGen（layout_aether, gdspy config-driven CMOS 反相器 GDS 生成）：参数化器件版图
- r207 QaWidthPatternGen（layout_virtuoso, SKILL→Python manifest，无 GDS）：width-rule 形族生成
- r211 NoOverlapPcellLayerParse / r212 SwitchGatedSpacePatternGen（layout_virtuoso, SKILL pcell 解析）：SKILL 脚本分析
- **本案首次 ground on "QA-pattern YAML → GDSII 版图转换器"**：通用 JSON/YAML 描述 → 二进制 GDSII 渲染（hierarchical cell top→category→shapes + SREF + 多 layer/datatype + label texttype + rect 闭合多边形），与器件版图/形族 manifest/SKILL 解析互补不重叠。

## 合成方向（B-synthesized）
- **任务**：写 `yaml_to_gds.py`，CLI `<input_dir> <output.gds>`，读目录下所有 `*.yaml`，产出单个 GDSII（hierarchical：top cell `<rule>_<kind>` → category cell `<rule>_<kind>_<category>` 含 shapes+labels → top cell SREF 各 category cell）
- **资产 A**（SUT 可见）：真实 e0047488 YAML 4 文件（M1.W.3 good/bad + M1.EN.1.1 good/bad，多 layer M1/V0G/SEALRING/TDV，多 category critical/good_1g/premise_unsat/bad_1g/bad_30pct，多 area，rect）
- **隐藏 B**（check 跑）：重参数化 4 文件（M2.W.5 good/bad + M2.EN.2.2 good/bad，layer M2:30/V1G:52/SEALRING2:180/TDV2:63，重参数化坐标 + 加多 area + 加 1 polygon area 测 polygon 支持），击穿硬编码 A
- **判分**：subprocess 跑候选 on B → gdspy 读 GDS → 16 条断言（zip/compile/run/gds 可读/top cell 名/SREF 数/category cell 名/rect bbox+layer/多 layer area/label text+layer+texttype/label xy/rect 5 点闭合/area 迭代 shape 数/跨输入守卫 A/多文件/额外 layer 渲染/坐标精度）
- **环境**：.75 sandbox 有 gdspy 1.6.13（r213 验证），SUT 可用 gdspy 或纯 Python 写入器；check.py 用 gdspy 读回校验
- **k=16 ≥8 ✓**
