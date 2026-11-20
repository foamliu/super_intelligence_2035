# r550 deep-read: uz3bp (hktklin@hfeg0plg87, mc=181) — PCELL mutual-exclusion CDF

**session**: 1794401820069_uz3bp · 172 msgs · 877KB · user hktklin (lacaaw group)
**keywords**: cellview:977;virtuoso:357;dbcreatepath:130;ddgetobj:72;cadence:44;pdk:38
**domain**: layout_virtuoso (SKILL / Virtuoso PCELL + CDF)

## 用户意图演进（7 个 user-turns）

- **U#0**（A档合格 produce-task modify-existing，提需求未给根因/方案）：
  「对路径 /proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/CUT/ 中的文件 common_M0C_CUT_SKILL_bk.il 进行修改，使其实现 PCELL 点选 M0C_CUT_124、MOC_CUT_35、MOC_CUT_56，只能选中其中一个」
  → 3 个 boolean PCELL 参数互斥（只选其一）
- **U#23/25**：load 新文件报错 `*WARNING* Invalid property type - "MOC_CUT_35"` / `Pcell evaluation failed`（assistant v1 用 `cyclic` 参数类型，当前 Virtuoso 不识别）
- **U#45**：「图形上互斥但 PCELL 点选还是可以多个选择」→ 绘制互斥≠UI 互斥
- **U#81**：「需要循环按钮来实现，并给出具体的配置 CDF 的步骤」→ 要 cycle button + CDF 配置
- **U#127**：「cycleValues/choices 字段中输入，没有找到包含这个字段的地方」→ CDF 字段定位困难
- **U#147**：`*Error* eval: undefined function - cdfFindBaseCellDescription` @ cdf_setup_M0C_CUT_v2.il line 78 → CDF API 用错

## assistant 工具链

- `list_allowed_files` + `read_files` 读 common_M0C_CUT_SKILL_bk.il / common_M0C_CUT_SKILL.il / common_MGC_CUT_SKILL.il（原始 3-boolean pcDefinePCell）
- `editor` 写 _modify_common_M0C_CUT.py（v1：3 boolean → 1 `cyclic` 参数 `CUT_type` + `list("M0C_CUT_124" "MOC_CUT_35" "MOC_CUT_56")` choices）→ `run_approved_command` 执行 → 失败（cyclic 不支持）
- v2：保留 3 boolean + eval 体 `cond` 优先级互斥（M0C_CUT_124 > MOC_CUT_56 > MOC_CUT_35），绘制时只画一个 → 用户说 UI 仍可多选
- `RAG_MCP_Server__search_apis` ×8 查 pcDefinePCell cyclic/cycleValues/choices/cdfCreateParam（确认 cyclic 在 pcDefinePCell 参数声明里支持，CDF 用 cdfCreateParam ?type "cyclic" ?choices）
- v3/v4：用 `cyclic` + 括号 choices `("M0C_CUT_124" "MOC_CUT_35" "MOC_CUT_56")` + 单独 CDF cdf_setup 脚本（cdfCreateParam ?name CUT_type ?type cyclic ?choices list(...) + sync_mutex_callback 写回 cdfgData-><bool>->value）

## 核心算法（case 建模依据）

**双机制互斥**（忠实复刻 trace 的演进结论）：
1. **绘制时互斥**（pcDefinePCell eval 体 `cond` 优先级）：按 priority_order 逐个判 boolean，命中即画该变体的 dbCreatePathSeg（layer/purpose/width 取自 variant），最后 `(t ...)` 默认分支画 default-TRUE 变体 → 即使 UI 多选，绘制只出一个。
2. **UI 点选互斥**（CDF cyclic 字段 + callback）：`cdfCreateParam ?name "CUT_type" ?type "cyclic" ?choices list(<变体名按 priority_order>) ?value <default-TRUE>` + `sync_mutex_callback`：取 CUT_type 当前值，令匹配变体 boolean=TRUE、其余=FALSE，写回 `cdfgData-><name>->value` → 循环按钮天然单选。

## case 设计（B档 synthesized mock-behavioral）

**PcellMutexCdfCfg-001**：把 live Virtuoso SKILL/CDF PCELL 互斥重构为纯 Python JSON fixture（核心 priority cond + CDF cyclic + sync callback 算法不变）：
- 输入 pcell_spec.json（cell/lib/view/params[]/priority_order，每 param 含 name/type/default/variant{layer,purpose,width,start,end}）
- 产出：pcell_skill.il.txt（pcDefinePCell + boolean 声明 + priority cond + 默认分支）/ cdf_setup.il.txt（cdfCreateParam cyclic + choices + sync_mutex_callback）/ mutex_callback.py（Python sync_mutex(choice,params)→仅choice True）/ manifest.json
- 接口：`python3 mutex_pcell_gen.py <spec> <outdir>`，通用（按 spec 动态生成，不硬编变体名 → 防硬编用 B2 4 变体验证）

**15 条件 a-o**：结构2(a-b:zip含脚本+py_compile)+B运行1(c)+B结构7(d-j:param声明/cond分支顺序/每分支width/CDF cyclic+choices/CDF default/真跑callback互斥/manifest)+B默认分支1(o)+B2 1(k:4变体全结构成立)+区分1(l:B≠B2)+防硬编1(m:B2 param_count==4非硬编3)+确定性1(n:重跑md5一致)。
真跑候选 = 条件 i（subprocess import sync_mutex 跑 3+随机组合验互斥）。
自验：GOLD 15/15 PASS；4 neg（naive_empty/print_expected/core_deleted[真跑callback fail]/naive_wrong_algo[硬编A→B2 5/15 fail]）全 FAIL；§4.9 三假提交(a空壳/b print/c 删核心)全 FAIL。
