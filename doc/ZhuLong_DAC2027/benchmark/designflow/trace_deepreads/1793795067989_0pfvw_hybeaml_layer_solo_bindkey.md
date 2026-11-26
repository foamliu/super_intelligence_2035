# trace_deepread — 1793795067989_0pfvw (hybeaml @ hfeg0plg88) — Aether 版图层次切换快捷键脚本

## 元数据
- sid: `1793795067989_0pfvw`，user `hybeaml`，host `hfeg0plg88`，mc=76
- keyword profile: `aether:732;schematic:52;dbget:41;cellview:29;virtuoso:27;drc:22;pdk:15;mixed-signal:15`
- status: **completed**（44 msgs，单 user goal-turn + 后续工具结果轮）
- layout-affinity score: 834.8（mc≥15 widen 池，fresh non-ledgered）
- domain: **layout_aether**（Aether Tcl/SKILL 脚本，版图层次显示控制 + bindkey）

## 用户 goal-turn（U#0 逐字）
> 「给我一个aether平台的脚本，版图中切换显示层次，快捷键1，显示M1层，快捷键2显示M2层」

- 附件：**无**（U#0 无 attachment）
- §A 选轮规则：U#0 = 提出需求（"给我一个脚本…切换显示层次"），用户未指出根因/未给修复方案 → 合格 A 档 seed。

## assistant 链路（真实 gold）
1. 触发 aether-tool-qa skill → 检索 Aether Reference Manual Part XI (Script)。
2. 搜索 layer display / bindkey API（多次 search_codebase 0 命中 → 改读 reference 全文）。
3. 定位关键 API（part_XI_Script.md line 11003+）：
   - `aeSetLayerVisible -layer <l> -purpose <p> -isvisible <0|1>` — 设置单层可见性
   - `aeSetAllLayerVisible -isvisible <0|1>` — 设置所有层可见性
   - `aeSetActiveLayer -layerName <l> -purpose <p>` — 设当前激活层
   - `aeSetLayerSelectable -layer <l> -purpose <p> -issel <0|1>` — 设置层可选性
   - `aeSetBindKey -action <proc> -key <key>` — 绑定快捷键
4. 写出 `layer_solo.tcl`（Tcl 脚本，146 行）至 `/ai_sandbox/drcpa/V0/agentdir/hybeaml/layer_solo.tcl`：
   - `proc showOnlyLayer {layerName purpose}`：`aeSetAllLayerVisible -isvisible 0`（隐藏全部）→ `aeSetLayerVisible -layer $layerName -purpose $purpose -isvisible 1`（目标可见）→ `aeSetLayerSelectable -issel 1`（目标可选）→ `aeSetActiveLayer -layerName $layerName -purpose $purpose`（设为当前层）→ puts 提示
   - `proc showAllLayers {}`：`aeSetAllLayerVisible -isvisible 1`（恢复全部）
   - per-layer procs `showM1..showM6` → 调 `showOnlyLayer "M<n>"`
   - `aeSetBindKey -action "showM1" -key "1"` … `showM6 -key "6"`，`showAllLayers -key "0"`
   - puts 加载完成 banner（按键功能表）
   - 注释含使用方法（CIW source / proc.menu / 手动命令参考）
5. 用户接受（session status=completed，单 goal-turn 无纠正）。

## gold 关键结构（layer_solo.tcl 核心）
```tcl
proc showOnlyLayer {{layerName "M1"} {purpose "drawing"}} {
    aeSetAllLayerVisible -isvisible 0
    aeSetLayerVisible -layer $layerName -purpose $purpose -isvisible 1
    aeSetLayerSelectable -layer $layerName -purpose $purpose -issel 1
    aeSetActiveLayer -layerName $layerName -purpose $purpose
    puts ">>> 显示层次切换: $layerName ($purpose)  [其他层已隐藏]"
}
proc showAllLayers {} {
    aeSetAllLayerVisible -isvisible 1
    puts ">>> 恢复所有层可见"
}
proc showM1 {} { showOnlyLayer "M1" }
...
aeSetBindKey -action "showM1" -key "1"
...
aeSetBindKey -action "showAllLayers" -key "0"
```

## case 改造（A档 faithful → 通用生成器题）
- 真实 gold 硬编码 M1-M6 + key 1-6 + 0=restore，只对 A 有效。
- 改造为「通用生成器」题：候选写 `gen_layer_solo.py <config.json> <out.tcl>`，读 config（layers[{name,key}], purpose, restore_key）生成 Aether Tcl 快捷键脚本。
- A（可见）= config_A.json（M1-M6, key 1-6, restore 0, purpose drawing）+ prompt(U#0 逐字) + task_brief(交付接口)。
- B/B2/B3（hidden，结构不同非改名）：
  - B: Metal1/Metal2/Metal3, key a/b/c, restore r, purpose drawing
  - B2: M1/M2, key 1/2, restore 0, purpose **pin**（不同 purpose）
  - B3: AA/PP/CT, key 1/2/3, **restore_key=null**（无恢复键）
- check 跑候选 gen_layer_solo.py on B/B2/B3，解析生成 out.tcl，验 aeSetBindKey/aeSetLayerVisible/aeSetAllLayerVisible/aeSetActiveLayer/aeSetLayerSelectable 调用与 config 一致 + 跨输入守卫（B 的 a/b/c/Metal1-3 反硬编码 M1/1）+ 结构（hide-all before show-target）+ restore 语义（B 有 r, B3 无）。
- L1 静态 + subprocess（不启动 Aether，纯 Tcl 文本解析）。

## 可达性
- session 文件 `/home/hybeaml/.cline/data/sessions/1793795067989_0pfvw/*.messages.json` 经 .75 NFS 可读（pyAether user t0002997）。
- gold `layer_solo.tcl` 在 `/ai_sandbox/...` 权限不可读，但完整内容在 messages.json 的 editor 工具调用 + 文件读结果中已捕获（msg [37]/[42]）。
