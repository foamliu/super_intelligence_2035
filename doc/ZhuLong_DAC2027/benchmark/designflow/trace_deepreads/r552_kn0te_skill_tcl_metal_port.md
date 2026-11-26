# r552 deep-read — kn0te (SKILL→Tcl metal-layer port)

- **trace**: 1792478058523_kn0te · hongyuy@hfeg0plg73 (10.129.8.111) · mc=103
- **keywords**: pyaether:169;aether:140;dbget:36;virtuoso:11;drc:10;rtl:2;dbopencv:2;cadence:1
- **msgs**: 67 (small, 239KB)
- **domain**: layout_aether (Aether Tcl layout script port)

## 意图演进
- U#0 (msg0): 用户提供一段 Virtuoso SKILL 脚本 `changeSelectedMetal(toLayer)` —— 金属层次快速切换工具：geGetSelSet 取选中图形 → foreach → member 校验 objType ∈ {rect,polygon,path,pathSeg} → 改 fig~>layerName/purpose → 计 changed/skipped；附 `changeSelectedMetalToLayer(keyNum)` (1→M1,2→M2,3→M3) + hiSetBindKey("Layout","1"/"2"/"3")。说明"这是一个金属层次快速切换的脚本"。
- U#1 (msg2): "请你帮我把它制作为skill文件，存放路径为/home/hongyuy/Desktop" → assistant editor 写 `changeMetalLayer.il`（增强版 SKILL：加 leGetLayerByName 层存在校验 + dbSaveGeometries Undo + via 类型 + unless 空选警告）。
- U#2 (msg14): **"能不能做成tcl文件我用的是aether软件"** = **produce-task author-new-script**（SKILL→Aether Tcl 移植，提需求未给根因/方案）→ assistant editor 写 `changeMetalLayer.tcl`（Aether Tcl 版）。
- U#3 (msg61): "这个脚本的作用是什么" = Q&A
- U#4 (msg63): "怎么使用" = Q&A
- U#5/U#6 (msg65/66): "没有作用" = 用户反馈 Tcl 在 Aether 里不生效（可能 aeGetSelSet/techFindLayer/dbChangeLayer API 名不准）。

## assistant 产物
- `changeMetalLayer.il` (msg9, SKILL 增强版)
- `changeMetalLayer.tcl` (msg49, Aether Tcl 移植版) —— 核心产物：
  - `proc changeSelectedMetal {toLayer}`: `aeGetSelSet` 取选中 → validTypes=[rect polygon path pathSeg via] → 空选 puts Warning return 0 → `techFindLayer $toLayer` 校验层存在(空则 return -1) → foreach fig: `emyFigGetTypeName` 取类型 → lsearch 校验 → `emyObjectGetProp` 取 oldLayer/oldPurpose → `dbChangeLayer -shape $fig -layer $toLayer -purpose $newPurpose` → incr changed/skipped → puts "Done. Changed X skipped Y" → return changed
  - `proc changeSelectedMetalToLayer {keyNum}`: switch 1→M1/2→M2/3→M3/default "" → 调 changeSelectedMetal
  - bindkeys: `geSetScriptBindKey "changeSelectedMetalToLayer N" "Ctrl+N"` (N=1,2,3) catch 包裹
  - 可选菜单: aeCreateMenuItem/aeCreateMenu/aeInsertBannerMenu (catch 容错)

## A档判定
- U#2 = produce-task（提需求"做成tcl文件我用aether"，未给根因/修复方案）✓ A档合格
- U#0 给出源 SKILL（=任务输入，非根因/方案）；U#5/6 "没有作用"是事后反馈非任务说明

## case 建模（B档 synthesized mock-behavioral）
- 把"SKILL→Aether Tcl 金属层切换移植"重构为参数化生成器：读 spec.json {purpose, supported_types, bindkeys{key:layer}, bindkey_prefix, out_file} → 生成 changeMetalLayer.tcl
- 可见输入 A: original_skill_script.il.txt (U#0 原始 SKILL) + input_spec.json (M1/M2/M3, drawing, 5 types, Ctrl+1/2/3) + task_brief.md
- 交付: submit.zip 含 metal_layer_port.py (生成器) 
- hidden B: layers M5/M6/M7, bindkeys 5/6/7, purpose drawing, 5 types
- hidden B2: layers MT1/MT2, bindkeys 1/2, purpose pin, types [rect,path]
- check: 跑生成器 on B+B2 → 解析生成 Tcl 结构（proc changeSelectedMetal / aeGetSelSet / validTypes==B.types / techFindLayer 层校验 / dbChangeLayer 改层 / changed/skipped 计数 / 空选 return 0 / changeSelectedMetalToLayer key→B.layers 映射 / geSetScriptBindKey B.keys 绑定 / purpose==B.purpose / B2 不同层+purpose+types 非硬编 M1/M2/M3）
