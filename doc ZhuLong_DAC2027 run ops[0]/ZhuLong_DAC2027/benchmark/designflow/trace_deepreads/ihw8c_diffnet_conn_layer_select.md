# Deepread: 1793237820834_ihw8c — drcConnect bad2 diffNet conn_layer 选择逻辑修复

- **session**: 1793237820834_ihw8c.messages.json
- **user/host**: xxchen @ hfeg0pkn002 (10.129.2.11)
- **mc**: 189 (209 calibre + …)
- **domain**: physical_verify (drcConnect connectivity QA tool)
- **nturns**: 1 user turn (111 msgs total, 59 tool calls)
- **工具**: list_allowed_files / read_files / search_codebase / editor / run_approved_command (cline 受限 shell)

## 工具背景（drcConnect）

`/home/xxchen/workspace/small_tool/drcConnect/` 是一个 **Calibre DRC connectivity QA 工具**：按 `connectivity` 网表生成测试 GDS（`sameNet` 好单元 + `diffNet` 坏单元），跑两次 Calibre（sameNet 应 CORRECT / diffNet 应 INCORRECT），汇出 `sum.rep`。入口 `run.py config`（单段）或 `run.py config_multi`（多段，每段独立 subprocess）。

核心生成器 `0.3/connectivity/connectivity_check/gds_gen.py`：
- `gen_total(path, y, cell1, cell2)`：为一条 connectivity 路径画 good/bad pattern（按 `conn_datatype[layer]` 的 purposes 逐 datatype 画）。
- `bad2(path, cell2)`：在 diffNet 单元里画「额外坏块」——对每个 (layer, datatype) 若「未在用」则画一个独立浮动矩形，让 diffNet 检查它不会意外成网。

两个关键集合：
- `conn_layers`（config 字段）：设计里**声明的所有层**（多段共享），形如 `[['FPA', ['drawing','CLOSE','CMP']], ['BTSV', ['drawing']], ...]`，含 base 名 + `*arr2` 变体，55 项。
- `connectivity`（config 字段）：**本段实际连线网表**，形如 `[['FPA','FAM','TMA'], ['TMA','TDV','TCP','M1A'], ['FPA','FPZ']]`，只列参与本段导通网的层。
- `_connectivity_layers()` = `{layer for edge in state.connectivity for layer in edge}` = 本段实际用到的层集合。

## 用户原话（U#0，唯一需求轮）

> 脚本问题反馈：/home/xxchen/workspace/small_tool/drcConnect/ver/V2/0.2/arr1_cmos/run_1 为什么 diffNet 里面没有 BTSV_drawing 做连接测试？虽然我在 conn_layers 定义了 BTSV drawing，但是实际 connectivity 并没有用到 BTSV 层。所以 diffNet 里面应该是未出现在 connectivity 里面的都要用来测试是否会形成意外的连线。

用户**同时指出问题 + 给出修复方向**（「未出现在 connectivity 里面的都要用来测试」）→ A 档禁用，本案做 **B 档 synthesized**。

## assistant 诊断与修复（59 工具调用）

1. 探目录 → 读 `gds_gen.py` bad2 → 读 config（run_1/config: connectivity=`[['FPA','FAM','TMA'],['TMA','TDV','TCP','M1A'],['FPA','FPZ']]`, conn_layers 55 项含 BTSV, bottomLayer=`['FPA']`）。
2. 根因定位：旧 `bad2` 用 `layer_con`（= conn_layers 的层名列表）判「在用」——`layer2 in layer_con` 就跳过。BTSV 在 conn_layers ⇒ 被判「在用」⇒ diffNet 不画 BTSV_drawing，正是用户抱怨。
3. 真因：`conn_layers` 是**所有段共享的整批声明**，`connectivity` 才是**本段实际连线**。多段 run 中某段 connectivity 不含 BTSV 时，BTSV 仍应进 diffNet 测「意外成网」。
4. 修复 `bad2`：把「在用」判断从 `conn_layers` 成员改为 `_connectivity_layers()` 成员：
   ```python
   conn_layers_used = _connectivity_layers()
   for layer2 in state.lpps:
       check_dataType = conn_datatype.get(layer2, []) if layer2 in conn_layers_used else []
       for datatype2 in state.lpps[layer2]:
           if (layer2 not in conn_layers_used) or (datatype2 not in check_dataType):
               # 画 diffNet 坏块矩形
   ```
   规则：`(layer ∉ connectivity) ∨ (purpose ∉ conn_layers[layer])` ⇒ 进 diffNet 坏块。
5. 加 `_connectivity_layers()` helper；guard `conn_datatype.get(layer2, [])` 防 KeyError（旧 `layer_con` gating 保证存在，新逻辑不再保证）。
6. 验证：写 `_verify_btsv.py` 复现用户场景（conn_layers 含 BTSV，本段 connectivity 不含）→ BTSV_drawing 现在出现在 diffNet（GDS layer 579 / datatype drawing，1 矩形）。副作用分析：**146** 个新 (layer,purpose) 坏矩形（全是 conn_layers 声明但本段 connectivity 不用的层，含 BTSV），**0** dropped，3835 unchanged。sameNet 不动。
7. 回归：5 个现有 config 各起独立 subprocess 跑（避免 gdspy 共享库 sameNet 已存在 假阳性）→ 0 失败。
8. 写 `tasks/todo.md` + `tasks/lessons.md` 文档；清理临时脚本。

## run_1/config 关键字段（A 档资产 grounded）

```
connectivity = [['FPA', 'FAM', 'TMA'], ['TMA', 'TDV', 'TCP', 'M1A'], ['FPA', 'FPZ']]
conn_layers = [['FPAarr2', ['drawing','CLOSE','CMP']], ... 55 项 ..., ['BTSV', ['drawing']], ['BLV', ['drawing','SL']]]
bottomLayer = ['FPA']
connectOPC011 = ['CONNECT OPC011 FPA']
```
- `connectivity_layers(A)` = {FPA, FAM, TMA, TDV, TCP, M1A, FPZ}（7 层）
- `in_use` = conn_layers ∩ connectivity_layers = 这 7 层（都在 conn_layers 里声明）
- `declared_only` = conn_layers − connectivity_layers ≈ 48 层（含 BTSV、BLV、所有 *arr2 变体、NBP/M0A/MT3/M2A/M3A/HSP/PCA/PCB/CTM/V1A/V2A/HSV/HLP/M6/M5/M4/M3/M2/M1/PG/AT4/BM1/BLP/HLV/V5-V1/PC）

## 选料结论

- **A 档禁用**（用户轮给出修复方案）→ **B 档 synthesized**。
- **DISTINCT** from `EDA-Eval-DesignFlow-DrcConnScriptAudit-001`（同 drcConnect 工具，但 DrcConnScriptAudit 是审计 DFM PROPERTY OPC011 netid 统计机制；本案是 bad2 的 diffNet conn_layer 选择逻辑——conn_layers vs connectivity 集合差）。互补不重叠。
- **L1-boundary**（静态 config 分析，stdlib only，不跑 Calibre/gdspy）：SUT 解析 drcConnect 段 config（conn_layers + connectivity），按修复后的 bad2 规则计算 diffNet 坏块 manifest（哪些 (layer,purpose) 进 diffNet，哪些「在用」排除），输出 JSON。隐藏 B 换不同 connectivity（BM1→…→MT3 链）击穿硬编码；B2 干净守卫（全 conn_layers 都在 connectivity → 0 declared_only）杀 always-detect；B3 重载守卫（多数 conn_layers ∉ connectivity）杀 always-clean。
- **seed 强度**：真实 bug、完整诊断-修复-验证闭环、用户原话可作场景、config 可直接做 A 资产、规则可形式化为 ≥8 独立断言。
- xxchen 已 7 case（drcConnect 已 1 = DrcConnScriptAudit），本案为 drcConnect 第 2 case，角度互补。

## 案件设计要点

- **task_id**: EDA-Eval-DesignFlow-DiffNetConnLayerSelect-001
- **domain**: physical_verify；**track**: B-synthesized；**L**: L1-boundary
- **SUT 产物**: `diffnet_select.py <config> -o <manifest.json>`（stdlib only，CLI 2 参 + -o）
- **规则**（faithful to fixed bad2，universe=conn_layers）：`(layer ∉ connectivity_layers) ∨ (purpose ∉ conn_layers[layer])` ⇒ 进 diffNet_bad；否则 excluded（在用）。简化为 universe=conn_layers 时：declared_only 层的所有 (layer,purpose) 进 diffNet_bad；in_use 层的所有 (layer,purpose) 进 excluded。
- **manifest 顶层键**: declared_only_layers(sorted) / in_use_layers(sorted) / diffNet_bad(list of {layer,purpose}, sorted) / excluded(list of {layer,purpose}, sorted) / connectivity_edges / bottomLayer / summary{n_declared_only,n_in_use,n_diffNet_bad,n_excluded,n_total}
- **14 条 a–n**: 结构/stdlib/反硬编码/A gold(declared_only/in_use/BTSV∈/diffNet_bad/excluded/counts/edges)/B gold(≠A)/B2 clean guard/B3 heavy guard + 3-seed 确定性。
