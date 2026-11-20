# 深读笔记 — m2vah (1785810906841_m2vah)

- **trace**: `1785810906841_m2vah.messages.json` · 1.96MB · 573 msgs (296 user / 277 assistant) · 285 tool_use (run_commands 182 / read_files 41 / editor 38 / SandBox_MCP_Server__run_code 23)
- **user**: e0014566 / hfeg0plg58 (10.129.2.10) · match_count 975 · keywords virtuoso:1628 .gds:411 netlist:180 cellview:119 calibre:67
- **domain**: layout_virtuoso（扩量，第 2 条；首条为 cgqd1=LayoutVirtuoso-001）

## 用户意图（11 条 substantive user msg，5 阶段）

1. **(idx0)** 给两个 skill（virtuoso-rscalc-runner 算电阻 + virtuoso-autovia-runner 优化版图），要求：①分析两 skill ②梳理配置，相同含义参数提共有的 common.config（避免重复配置出错）③构建工作流「算电阻→调 autovia 优化版图→降低电阻」，得到电阻明显降低的新版图 ④写进 prompt_flow.md ⑤上步输出=下步输入 ⑥电阻降幅目标 + 最大迭代次数写到配置文件
2. **(idx38)** 先别搞整体 flow，先分别跑两个工具看是否正常
3. **(idx129)** 把 common.config 里的 powernet 挪到 rscalc.config（不公用）
4. **(idx145)** 两个工具的 powernet 支持为空→自动获取全部 power net，固化逻辑
5. **(idx265)** autovia 只发现一个 powernet？为什么 rscalc 发现多个？分析
6. **(idx273)** 看下 flow 流程需不需要改，行就直接跑
7. **(idx369)** **关键修正**：优化电阻是所有点位的电阻都要优化，不是只优化最大的电阻
8. **(idx401)** 再完整跑一遍 flow
9. **(idx501)** autovia 只能在低层金属找 via 插入位置？是确定的还是跟参数有关
10. **(idx525)** 再引入 powerfill 工具（virtuoso-powerfill-runner），放到 autovia 后面：算电阻→autovia→powerfill→算电阻 构成循环迭代；共用配置提到 common.config；上步输出=下步输入

## 核心技术逻辑提炼

### 配置体系（最终演化形态）
- **common.config**（共有，单一真相源）：`process` `project` `libName` `cellName` `viewName`（两工具共享）+ `targetReduction` `maxIterations`（**流控参数，不 inline 进 SKILL**）
- **rscalc.config**（RsCalc 专用）：`pwrNets`（**不共享**，RsCalc 读 RTEXT label 无 `!` 后缀如 `vdd`）、`version`、`runDir`、`metalOption`、`parallel` 等
- **run_autovia_config.il**（AutoVia 专用）：`pwrnets`（**不共享**，AutoVia 读 GDS TEXT label 带 `!` 如 `vdd!`）、`strminLib`、`runDir`、via 选择（viaCT/viaV5…）、`outLibName`/`outCellName`、`coreNum`
- **演进**：初版把 pwrNets 放 common.config 共享 → 用户指出不公用 → 拆到各自 config → 进一步发现两工具 net 名格式不同（RTEXT 无 `!` vs GDS TEXT 带 `!`）→ pwrNets/pwrnets 终不共享，各自带空值自动检测逻辑
- **run_powerfill_config.il**（PowerFill 专用，后期加入）：`workDir` `powerName` `strminLibCfg` `runMode` `speedMode` `convertToPcell` `outLibName`/`outCellName`

### 配置生成器（gen_<tool>_agent.py，三个同构）
- `parse_config(path)`：正则 `^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s*$`，跳过 `;;` 注释与空行 → ordered dict {var: value_str}
- `merge_params(common, config)`：① common 按 `COMMON_NAME_MAP` 映射 ② overlay 工具 config ③ `pop` 掉 `FLOW_KEYS={targetReduction, maxIterations}`
  - RsCalc `COMMON_NAME_MAP={}`（同名）
  - AutoVia `COMMON_NAME_MAP={project:projName, viewName:viewType, pwrNets:pwrnets}`（早期含 pwrNets，后期 pwrNets 不共享故不再映射）
  - PowerFill `COMMON_NAME_MAP={viewName:viewType}`
- `generate_agent_script`：把 nogui .il 里的 `load("...PLACEHOLDER...")` 块替换为 inline `    var = value` SKILL 赋值块；尾部 hint 替换为 `RunXxxNoGui()` 自动启动
- 产出 self-contained .il（无 load()），可 `virtuoso -nograph -replay` 批跑

### .rvn 电阻结果格式（RsCalc 输出）
- 路径：`<rscalc runDir>/<cellName>/RSDB_<net>/*.rvn`
- 每行逗号分隔；首行 `LV+RSView` 为表头（跳过）
- **列 12（0-idx 11）= 电阻值**（Ohm）
- **检查点 key = `cols[2]_cols[3]_cols[4]_cols[5]`**（net_layer_x_y，跨迭代不变）
- 解析（verify_flow.py / final_report.py 实证）：
```python
for rvn in glob(run_dir/RSDB_*/*.rvn):
    for line in f:
        if line.startswith('LV+RSView'): continue
        cols = line.split(',')
        if len(cols)<12 or not cols[11].strip(): continue
        key = '_'.join([cols[2],cols[3],cols[4],cols[5]])
        points[key] = float(cols[11])
```

### 收敛判定（**用户 idx369 关键修正：所有点位**）
- **每**个检查点 p：`R_i(p) <= R_0(p) * (1 - targetReduction)` 才算该点收敛
- **整体收敛 = 全部点收敛**（不是只看最大电阻点；最慢改善的点决定收敛）
- 迭代上限 `maxIterations`；每次 `outCellName = "<orig>_opt<i>"`（不覆盖）
- baseline R0 = 原始 layout 的 per-point R

### flow 编排（prompt_flow.md）
- Step0：从 common.config 读 targetReduction/maxIterations/origCellName
- Step1：RsCalc 跑 baseline（cellName=origCellName）→ 解析 R0(per point) 存 baseline_rpoints.csv
- Step2：for i in 1..maxIterations：sed 改 common.config 的 cellName=currentCell + run_autovia_config.il 的 outCellName=`<orig>_opt<i>` → gen+launch autovia → gen+launch rscalc on opt cell → 解析 R_i(per point) → 全点收敛则停
- 数据流：AutoVia 写 merged layout 到 outLib/outCell → 成为下轮 cellName（**唯一链式衔接点**）；RsCalc 写 .rvn → 编排器判收敛

## 真实结局（final_report.py 实证）
- baseline `testa` 18 检查点 → opt1 → opt2：**所有 18 点电阻完全不变**（AutoVia 插的 via 不落在任何 IR-drop 路径上）→ 0/18 收敛
- iter3 无新 via 插入机会（DRC exhausted）→ 停
- best_cell = testa_opt2（R 与 baseline 相同）
- 这是个「优化无效」的真实结局，说明判分必须能识别「全点不变 ⇒ 不收敛」

## 牙齿识别（用于判分）
1. 配置解析：`;;` 注释 + `var = value`（值带引号/nil/t/数字）
2. 配置合并：common 先（按 name map）→ tool overlay → drop FLOW_KEYS
3. **name map**：autovia project→projName / viewName→viewType（pwrNets 后期不映射）
4. **FLOW_KEYS 不 inline**：targetReduction/maxIterations 只进流控不进 SKILL
5. .rvn 解析：col 11 = R，key = cols[2-5]，跳过 LV+RSView
6. **全点收敛语义**：ALL points R_i <= R0*(1-tr)（非仅 max 点）
7. 迭代计数 <= maxIterations
8. 数据流链式：outCell → 下轮 cellName

## .75 可用性
- Virtuoso batch 可跑（`virtuoso -nograph -replay`，需 `env -u ARGUS_HOME _CXMT_SH_PROJ_WRITE_CHECK=1 OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x LD_PRELOAD=/usr/lib64/libstdc++.so.6`）
- RsCalc 单跑 ~180s+，多迭代 × pi 实跑超本轮预算 → 本轮 case 判分走「候选脚本在隐藏 .rvn 树上 subprocess 真跑 + 结构化断言」（L2 真跑候选），Virtuoso 实跑留 L3 升级

## 选料结论
- 选 m2vah（975，layout_virtuoso 域扩量第 2 条）：多工具编排 flow（rscalc+autovia+powerfill 迭代）+ 配置合并去重 + .rvn 电阻解析 + 全点收敛判定，可构建有牙自验 case
