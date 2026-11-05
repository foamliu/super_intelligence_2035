# trace_deepread: 1786534284539_1o5rd — layout editability diagnostic

- session: `1786534284539_1o5rd` · user `e0014566` @ `hfeg0plg58` · mc=128
- agent: cline lead · 62 msgs (35 user / 27 assistant)
- tools: SandBox_MCP_Server__run_code×13 (Virtuoso SKILL) · run_commands×12 · read_files×4 · RAG_MCP_Server__search_apis×1 · get_api_details×1 · ask_question×1
- domain: **layout_virtuoso** (Virtuoso SKILL cellview editability probe + OA lock forensics)
- claimed: r130 shard C · case-id `EDA-Eval-DesignFlow-LayoutEditDiag-001`

## 真实任务（用户原话意图轮）
- USER#1 (idx=0, 逐字意图): 「看下这个layout, 可编辑吗？可以修改里面的内容吗？」
- USER#2 (idx=9): `auto_austin_case1/Array16G_B/layout` (指定目标 cell)
- USER#3 (idx=35): 「现在再看看」(锁状态变化后复查)
- 纯意图轮（提目标，不指根因/不教修复）→ A-档 eligible；但 gold = live Virtuoso 锁取证，沙盒不可复现活跃锁场景 → B-档 synthesized L1-boundary。

## gold 工作流（agent 8 次迭代探针，最终隔离根因）
1. read open `dbOpenCellViewByType(... "r")` → 成功：bBox `((-17884.13 -14767.0)(17884.13 100.524))`，32971 shapes / 37 inst / 16039 terms / 0 labels。
2. edit open `dbOpenCellViewByType(... "a")` → `isEditable=nil`。
3. write probe `dbCreateLabel` on `RDL/drawing` → 对象返回但 `parent=nil`（写入被拒）。
4. 排查层有效性：换 `M2/pin`（确认有 shape 的真实层）→ 仍 `parent=nil` → **不是层问题**。
5. `dbPurge` 后重开 "a" → 同一缓存对象地址 `db:0x1ec14a1a`，仍 `isEditable=nil`（**cache stuck**）。
6. `geOpen(?mode "edit")` → window 返回成功，但 cellview 仍 `isEditable=nil`（**不是打开方式问题**）。
7. **决定性控制实验**（idx 52-57）：在 `test_lib` 用 `dbOpenCellViewByType("test_lib" "scratch_edit_test" "layout" "" "a")` 新建全新 scratch cell → **可编辑、写入成功** → 证明 session 具备编辑能力 → Array16G_B 的只读不是 session-wide，是 per-cell。
8. OA 锁取证：磁盘 `layout.oa.cdslck` + `layout.oa.cdslck.RHEL30.hfhds201.114607` → 持锁 hfhds201:PID114607（用户自己的进程）；时间线 19:27 上锁→19:50 短暂消失→19:52 续锁→19:55 仍在 → **活跃锁**（非僵死）。

## 根因判定（gold 结论）
**LOCKED_BY_OTHER**：hfhds201 上活跃 Virtuoso 会话（PID 114607）以编辑模式持有该 cell 的 OA 锁并续锁；磁盘权限正常、session 有编辑能力、层有效。修复动作：协调关闭 hfhds201:114607 后再编辑；**不可强删活跃锁**。

## 失败模式（agent 走的弯路 → 教学点）
- 混淆「cellview isEditable=nil」与「session 只读」：前 6 次探针都只测目标 cell，无法区分 per-cell lock vs session-wide readonly；直到第 7 次在别的库新建 scratch cell 才隔离。
- `dbPurge` 无法清掉已缓存的只读 cellview（对象地址不变）→ 不能靠 purge 修。
- `geOpen` vs `dbOpenCellViewByType` 打开方式不是根因（两者都 isEditable=nil）。
- SKILL code 经 MCP 传输 >~2000 字节后 `\n` 被序列化为字面 `\n` 文本 → 探针必须 compact（<2KB）。
- 活跃锁 vs 僵死锁判别：cdslck 持有进程是否存活 + 锁文件 mtime 是否持续刷新。

## 教学点（合成 case 的核心）
**根因隔离靠控制实验**：当目标 cell `isEditable=nil`，必须在另一个可写库新建 scratch cell 做对照——
- scratch 可编辑 + 目标有活跃 cdslck → **LOCKED_BY_OTHER**（协调关 holder，禁强删）
- scratch 可编辑 + 目标无锁 + 磁盘权限可写 + 同一缓存对象地址 → **CACHE_STUCK**（purge 失败，需重启 session / 换副本）
- scratch 可编辑 + 目标无锁 + 磁盘权限**不可写** → **LIB_READONLY**（修目录权限）
- scratch 可编辑 + 目标有锁但 holder 进程**已死** → **STALE_LOCK**（可强删锁文件）
- scratch **也**不可编辑 → **SESSION_READONLY**（整个 session 没编辑权）
- 目标 isEditable=**true** + write probe parent=nil + 层不在 valid_layers → **INVALID_LAYER**（层 purpose 对无效）
- 目标 isEditable=true + write parent≠nil → **WRITABLE**

7 个根因类别 + 报告结构 + 控制实验字段 → ≥8 条独立断言。

## 资产设计（B-档 synthesized L1-boundary）
- 交付：`classify_editability.py`（单文件 Python，CLI `<bundle.json>` 或 `<bundle_dir>`），读「诊断 bundle」（read/edit/write/lock/scratch/lib_perm/valid_layers 字段），输出结构化报告（VERDICT/ROOT_CAUSE/RECOMMENDED_ACTION/CONFIDENCE + 退出码 0=有定论/2=INCONCLUSIVE/1=格式错）。
- A 资产：1 个真实 bundle（LOCKED_BY_OTHER，对应 trace 的 Array16G_B 场景）+ prompt.md + task_brief.md。
- hidden B：≥5 个不同根因 bundle（WRITABLE / STALE_LOCK / SESSION_READONLY / LIB_READONLY / INVALID_LAYER / CACHE_STUCK），结构上与 A 不同（不同 cell 名 / shape 数 / 锁 holder）→ check.py 只跑 B。
- 不真跑 Virtuoso（沙盒不可复现活跃锁）；candidate 是离线分类器，对**已捕获的探针 bundle** 做根因分类。

## trace 完整结论引用
见 messages idx=33（首版结论）+ idx=61（复查结论，含锁时间线 + 7 项探针表 + 根因 + 修复动作）。
