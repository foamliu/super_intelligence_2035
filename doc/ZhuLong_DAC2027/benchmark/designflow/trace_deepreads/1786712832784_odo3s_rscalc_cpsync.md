# deepread: 1786712832784_odo3s — RsCalc checkPoints 配置同步

- **user**: e0014566
- **host**: hfeg0pkn001 (10.129.x), scp 经 eda_flow run_commands(e0031982 身份) 到 .75 workdir
- **session_file**: 1786712832784_odo3s.messages.json (1.18MB / 324 msgs / 167 user msgs)
- **match_count**: 334 (tools: 596 virtuoso · 60 calibre · 27 skill · 15 hspice · 15 cellview · 4 pyAether · 3 schematic · 2 dbCreateInst · 1 ascii)
- **domain**: pg_layout (RsCalc = virtuoso power-net resistance check-point flow)
- **track**: A-档 faithful

## 真实任务（UI#0 逐字）
`/home/e0014566/test_RScalc/test_skills_5/rsclac.config 同步 checkPoints 过来`
- 纯需求：只给目标（同步 checkPoints），未给根因/修复 → A-档 seed 合格。
- UI#31 为后续 handoff（"read the prompt_flow.md and do the job in it"），与 UI#0 无关，不用。

## trace 关键步骤
1. agent read source `/home/e0014566/test_RScalc/test_skills_5/rscalc.config`：checkPoints = 51-tuple list（3 个 pwrNet vdd1!/vss!/vcc!，4-element `("net" x y "layer")`）。
2. read target `/home/e0014566/test_layout_rscalc_flow_14/rscalc.config`：**结构不同**——process/project/libName/cellName/viewName 已拆到 common.config，本文件只保留 RsCalc-specific 参数；`checkPoints = nil`。
3. search_codebase `checkPoints` / `CXMTGetCheckLayerName` 找语义。
4. editor 改 target：`checkPoints = nil` → `checkPoints = list(... 51 tuples ...)`。
5. diff 验证：`-73: checkPoints = nil` → `+75: checkPoints = list(...)`。
6. 写 `/tmp/verify_config.py` 校验：tuple count=51、vdd1!=17、nets={vcc!,vdd1!,vss!}、checkPoints 长 1700 chars。

## gold（用户接受后的产物）
- 用户未显式 accept，但直接进入下一任务（UI#31 handoff）= 隐式接受。
- gold = 当前 target rscalc.config（checkPoints 已同步，其余 target 结构 / common.config 拆分 / pwrNets / gdsFile / 所有 `;;` 注释 / 行序 逐行不变）。
- 真实 source/target config 经 eda_flow ssh 从 hfeg0pkn001 读到 .75（e0031982 对该机可读）→ A-档 faithful 可行。
- pristine pre-edit target = 当前 target 把 checkPoints 行回退为 `checkPoints = nil`（从 trace diff 重建）。

## 合成
- deliverable: `rscalc_cpsync.py`（Python3 标准库），CLI `python3 rscalc_cpsync.py <source> <target> <output>`。
- 核心：source→target 的 `checkPoints` 字段同步；保留 target 全部其余字段/`;;`注释/顺序/空行 byte-for-byte。
- 难度点：① nil / 单行 list / 多行 list(续行 paren balance) 三态值处理 ② target 已有 old 值(单/多行)→整段替换 ③ target 无 checkPoints→插在 `;; Check points` 注释块后 ④ source 多行 list 重排到单行 ⑤ rogue net(不在 source pwrNets)stderr 告警但仍写出 ⑥ 只同步 checkPoints，pwrNets 等其它字段不动。
- 隐藏 B/B2/B3/B4 + A 交叉校验，15 条独立断言（check.py CONDITIONS a-o）。
- negative: naive_cp / always_print / core_deleted / empty_stub 全 FAIL；三假提交(a空壳/b只print/c删核心)全 FAIL。

## 与既有区别
- DummyQaCliNoConfig = CLI-over-config 合并优先级；本案 = source→target **单字段同步 + 结构保真**（不合并、不覆盖 target 其余字段）。主题/断言独立。
- 既有 pg_layout case（PGSplitNTN-001）= PG net 分裂；本案 = RsCalc checkPoints config 同步，pg_layout 域 6→7。
