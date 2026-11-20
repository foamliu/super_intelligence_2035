# 深读：sid_1792669757550_90kyw (colinxu / hfeg0pgn041)

- source: `/home/colinxu/.cline/data/sessions/1792669757550_90kyw/1792669757550_90kyw.messages.json` (694KB, 170 msgs, 4 user_inputs)
- tools: cellview 372 / netlist 14 / schematic 269 / calibre 2 → layout_aether dominant
- user: colinxu (fresh-ish; 3 prior ledger C entries)

## 4 个用户轮（A-档 seed 候选）
- UI#0 `<user_input mode="act">帮我在开启的cell view中添加一个label用于测试</user_input>` ← **提出需求+目标，无根因/修复 = A-档 seed ✓**
- UI#46 `帮我用各种保存api测试保存是否正常`
- UI#93 `现在尝试各种删除api看看能不能删掉这个label？`
- UI#128 `现在我改变了policy策略，请重新尝试删除` ← 用户给出"修复动作"（改 policy），按 A-档规则不得作任务说明；但前 3 轮可作 seed。本轮 case 取 UI#0 为主任务说明，UI#46/93/128 的产物作为 gold 的事实链。

## assistant 工具链（161 entries, 95 tool_use）
RAG search_apis/get_api_details 探 API → editor 落脚本 → SandBox_MCP_Server__run_code (pyAether) 自测 → 反向验证。

### 关键 gold 事实（逐字从 run_code 输出）
**Label 创建**：
- `dbCrtLabel(cv, emyPointF(x,y), textName, height)` 在 schematic/symbol/layout view 创建 label
- 反向验证：`emyObjectIsLabel(obj)` → True
- `aeGetCurDesign()` 返回当前激活 `emyDesign` (db:0x...)
- 创建的 label 文本：`SAVE_TEST_OBJ`(最早, 保存测试), `NET_DEL_TARGET`, `DEL_STRATEGY_TARGET`, `AE_DEL_TARGET`, `DETACH_TARGET`

**保存 API（7 个，全成功）**——独立测试库 `save_test_lib` / cell `save_cell` / schematic view，含 1 label：
| API | 调用 | 返回 |
|---|---|---|
| `dbCheckAndSaveDesign(cv)` | check+save | `True` |
| `dbSaveAll()` | save all | `True` |
| `daSave()` | da save | `True` |
| `aeSaveDesign()` | ae save | `True` |
| `aeCheckAndSaveDesign()` | ae check+save | `None`（文档无返回声明，正常）|
| `aeSaveAsDesign(cell, lib)` | save as | `True` |
| `sseGuiCheckAndSave()` | gui check+save | `True` |

**持久化反向验证**：只读重开 `dbOpenCVByType(...,"r")` + `dbShapeQueryEx(cv)` 返回 tuple，object_count==1（即 label 落盘）

**删除 API + Policy guard（核心发现）**：
- 删除 API：`dbDelete(obj)`, `aeDeleteObj()`(配合 `aeSelectObject`/`aeDeselectObject`)
- **Policy guard**：`/home/colinxu/.cline/plugins/agent-policy.json` 的 `runCodeGuard.destructiveActionsForDeny` 含 `sandbox_delete`，deny 正则 `(?:ae|db)Del\w*\(|[dD]elete\w*\(` → **所有删除类 API（dbDelete(/aeDeleteObj(/aeDel*/任何 Delete*(）在 run_code 沙箱中直接 DENY（非等待审批）**
- `run_approved_command` (python-runner) 环境是 Python 3.7.1，**无 pyAether**（`No module named 'pyAether'`），无法承载 EDA 删除
- → policy-before 下：沙箱内**无法实际删除** label（删除代码已交付，供真实 Aether 运行）

**Policy 变更（UI#128 后）**：
- `destructiveActionsForDeny` 从 `["sandbox_delete", ...]` → **`[]`（空数组）**
- 删除 API 不再被 deny
- `dbDelete(label)` → `True`（第一次）；对已删对象再调 → `False`（幂等，不报错）
- `aeSelectObject(label)` → `True`；`aeDeleteObj()` → `True`；label 计数 1→0
- 持久化验证：删除后保存，只读重开 label count==0

**其他删除相关 API**（检索到，部分测试）：
- `dbSubFigFromNet(fig, net)`：把 fig 从 net 摘除（对象仍在，断连接）→ True
- `dbDetachFig(child)`：detach（attach 后）
- `leGuiDelLabelByInstance` / `leGuiPartialDelete`：GUI 交互命令，无参沙箱难测
- `dbPurgeCV`：内存 purge，非对象删除
- `dmDelete`
- label 文本获取：`emyTextGetText(s, emyString())` 返回 True，文本写入第 2 参数；label `.text` 属性

**cv.shapes**：返回 tuple of shape objects；`emyObjectIsLabel(s)` 判 label；`dbShapeQueryEx(cv)` 查对象

## A-档资格判定
- UI#0 逐字原文可作任务说明（提出需求+目标，无根因/修复）✓
- 但 gold 依赖：live Aether + 私有 save_test_lib + policy 文件 + 跨调用沙箱状态保留 → **A-档 disqualified（live-tool 依赖，无法离线复刻金标准）**
- → **B-档 synthesized L1-boundary**：合成 manifest（API 测试记录）+ Python3 stdlib 诊断器（解析 manifest → 判定 label 创建/保存覆盖/持久化/policy-guard/policy-change/删除结果/label 计数迁移/verdict）

## 与既有 case 区别
- r68 APRRoutePrecondDiag = pyAether APR doLogicRouter 路由前置条件诊断（placement+route error 推进）
- 本案 = pyAether label add/save/delete API 测试 + policy-guard 破坏性操作拦截 + policy-change 重试诊断
- 主题/断言独立：保存 API 覆盖、policy 正则 deny、policy-change 状态迁移、label 计数 1→0、幂等删除——与路由 case 无重叠

## case id
`EDA-Eval-DesignFlow-LabelApiPolDiag-001` (layout_aether, B-档 synthesized, L1-boundary)
