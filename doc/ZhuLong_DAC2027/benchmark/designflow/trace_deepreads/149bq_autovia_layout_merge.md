# Deepread: 1783342909947_149bq — autovia via-cell → layout merge integration (layout_virtuoso)

- **session**: `1783342909947_149bq.messages.json` · user `e0014566` · host `hfeg0plg49` (10.129.8.86) · mc=10 · nmsg=24 · 115KB
- **cwd**: `/home/e0014566/test_power_analysis_4/`（real Virtuoso AutoVia flow 目录；与 `test_power_analysis_3/` 同脚本）
- **domain**: layout_virtuoso（AutoVia 生成 via cell 后，把 via cell instance 调入原 layout 生成新 layout；SKILL `dbOpenCellViewByType`/`dbCopyFig`/`dbCreateInst`/`dbSave`）
- **selected round**: U#2 (msg 4) — clean 提需求轮（提出目标，no rootcause/fix from user）。U#0="hello" / U#1="what is the model of you" 噪声，不进 prompt。

## User intent (U#2 逐字, A-档 seed)
```
经过调整，这个run_autovia_agent.il 终于可以准确跑出结果了。addViaToLayout.il 这个脚本的功能是将autovia得到的via cell 调入到 原本的layout 中，形成一个新的layout。请将这个脚本的调用添加到run_autovia_agent.il中来，完成将生成的via cell调入原来的输入layout, 生成一个新的layout的目的。顺便加一个配置参数，保存新生成的layout.
```
用户只提目标（把 addViaToLayout 的调用加进 agent 流程 → 生成新 layout + 加保存配置参数），未给根因/修复方案 → 干净 A-档 seed。

## Agent flow (msg 5–23)
1. read_files(run_autovia_agent.il + addViaToLayout.il) + run_commands(ls test_power_analysis_4)
2. read_files(run_autovia_config.il + run_autovia_nogui.il 1-100/100-300/300-500/500-700) — 通读 nogui 全 603 行
3. run_commands(ls test_power_analysis_3 + diff _3 vs _4 nogui/agent) — 发现两目录脚本相同，agent 从 _3 load，addViaToLayout.il 只在 _4
4. **关键设计决策**：用户要求"加 addViaToLayout.il 的调用"，但 `RunAutoViaNoGui()` 里 `strminLib`/`readOnlyCellList` 是 `let` 局部变量，单独 `load(addViaToLayout.il)` 拿不到这些值 → agent 选择**把 merge 逻辑直接 inline 进 RunAutoViaNoGui() 末尾**（而非 load 外部脚本）。
5. editor 三步改 `run_autovia_nogui.il`：
   - 改 load config 路径 `_3 → _4`（环境修正，非核心）
   - `let` 变量列表加 `outLibName outCellName srcCV dstCV viaMasterCV`
   - 在 `RunAutoViaNoGui()` 末尾 `t` 之前插 merge block
6. config 加 `outLibName="austin"` / `outCellName="layout_austin6_autovia"`
7. msg 20-23 编辑出过乱（重复插入），读取 588-615 修复（trace 在 msg 23 仍在修，但 gold 结构清晰）

## 真实 gold（人工复核 tp3 vs tp4 diff）
对 `run_autovia_nogui.il` 的 3 处核心增量（排除 VCO 环境修正 512-535 那段无关 bolt-on）：
1. **let 新变量**（line 54）：`outLibName outCellName srcCV dstCV viaMasterCV`
2. **默认回退**（line 98-99）：
   `if(outLibName == nil || outLibName == ""    then outLibName = libName)`
   `if(outCellName == nil || outCellName == ""  then outCellName = strcat(cellName "_autovia"))`
3. **merge-layout block**（line 594-693，在末尾 `t` 之前）：
   - guard `if(readOnlyCellList && length(readOnlyCellList) >= 1 then ... else printf("No via cells, skipping") )`
   - `srcCV = dbOpenCellViewByType(libName cellName viewType "" "r")` 打开原 layout 只读
   - `unless(ddGetObj(outLibName) dbCreateLib(outLibName))` 建输出库
   - `dstCV = dbOpenCellViewByType(outLibName outCellName viewType "maskLayout" "w")` 建目标 cellview 写模式
   - foreach `srcCV~>shapes`/`~>labels`/`~>vias`/`~>pins`/`~>blockages` → `dbCopyFig(fig dstCV)`（5 类对象全拷）
   - foreach `srcCV~>instances` → `dbCreateInst` / `dbCreateInstArray`（array 用 numInst）
   - foreach `readOnlyCellList` → `viaMasterCV = dbOpenCellViewByType(strminLib viaCellName "layout" "" "r")` + `dbCreateInst(dstCV viaMasterCV viaCellName list(0 0) "R0")`（via cell 放原点 R0）
   - `dbSave(dstCV)` / `dbComputeBBox(dstCV)` / `dbSave` / `dbReopen(dstCV "r")` / `dbClose`
config 增量：`outLibName`/`outCellName` 两参数。

## A-档 disqualified → B-档 synthesized L1-boundary
gold 依赖 live Virtuoso + OA 库 + 真实 layout.oa → 在线后端判分机不可达 → A-档不可行。降为 B-档 synthesized L1-boundary：把"修 SKILL 脚本"转成"写 Python 生成器 `autovia_merge_gen.py`，读原 nogui 模板 + 原 config，产出加了 merge block + 新 config 参数的 modified nogui + modified config"。判分静态验 SKILL 结构（Virtuoso layout API 调用齐全且接 config）+ 生成器在 hidden B 上 subprocess 跑通（B 不同 lib/cell → outLibName/outCellName 派生值不同，杀硬编码 A）。

## 正交性
- ≠ AutoViaGen-001（同 flow，但做 config inlining：load→inline 参数；其模板已是 post-merge 708 行）
- ≠ AutoViaPFAudit-001（audit autovia/powerfill instance 是否删干净）
- ≠ RsCalcAutoVia-001 / RsCalcAgentGen-001（rscalc 阻抗计算 agent）
本案 = autovia flow 的 **via-cell → layout merge 集成**（dbCopyFig/dbCreateInst 把 via cell 调入原 layout 生成新 layout + 保存配置），首次覆盖"layout 对象全量拷贝 + via 实例化"子主题。
