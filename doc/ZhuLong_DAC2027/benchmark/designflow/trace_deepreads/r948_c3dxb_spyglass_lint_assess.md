# r948 deepread — session 1795071099634_c3dxb (lorikx@hfeg0plg15, mc24)

- 选料来源: 16:4x 令 mc≥5 池造题第 3 条候选；/tmp/candidates_apure.tsv 266 strict A-pure
  → anti-join 4-shard 台账（4174 touched sids, .messages.json 后缀修正）→ 14 fresh pure-A
  (ak>=50, ck<=15%ak, top-kw 非 C) → c3dxb 排第 3（ak312/ck0, rtl:165;verilog:135;synopsys:12;
  netlist:8;bandgap:1）选为本轮 peek
- session 路径: `/home/lorikx/.cline/data/sessions/1795071099634_c3dxb/1795071099634_c3dxb.messages.json`
  （subdir 路径，ALIVE，134KB / 14 msgs）
- domain 归属: **digital**（rtl:165+verilog:135+synopsys:12 主导，SpyGlass lint 工程 → verification/digital，shard A 正确）

## 用户意图（逐字 U#0）

> 「请检查这个路径的文件/home/lorikx/1_TV1/CXTV1_FS001A/frontend/work/，是个lint项目，之前运行过，
> 单已经很久没更新，rtl更新过，你评估一下有哪些文件需要修改，能达到最新的版本运行lint，
> 那个路径你没有写的权限，所以你可以在FS_LINT文件夹下执行你需要做的事请」

任务类型: **评估型 produce-task**——评估一个旧的 SpyGlass lint 工程（只读路径），指出哪些文件
需要修改才能用最新版本跑 lint，产出落到可写 FS_LINT 文件夹。

## trace assistant 流（14 msgs，**未完成**）

- #1: 梳理任务 + 并行 list_allowed_files（lint 工程目录 + FS_LINT 可写目录）
- #3: 定位真实路径 `/proj/lacaa/TV1_TestChips/CXTV1_FS001A/frontend/work`（`/home/lorikx/1_TV1` 是软链）；
  从 `vcst_rtdb/spyglass` 确认是 **SpyGlass lint 工程**
- #5: read_files Makefile / lint.tcl / readme / design_rtl.list / design_rtl_top.list / ...（核心配置）
- #8: user「请继续任务」
- #9: 并行 list_allowed_files frontend 目录 + read_files vcst_rtdb/reports/run.log / vcst_command.log /
  vcst_session.log（上次运行情况）
- #12: 给出**部分状态**（非最终交付）:
  - 上次 lint 运行 2026-10-28 09:10（vcst_command.log）
  - 工具 VC Static V-2023.12-SP1
  - top = AMSGrp（AMS IP 组）
  - work/ 工程只 lint AMSGrp
  - ……（文本截断）
- #13: user「情急需」← **session 在此中断，assistant 未给出最终评估报告/交付**

## 判定: **不可造（incomplete trace，无 gold 交付）**

- trace 只有 14 条 msg，assistant 在 #12 刚给出部分状态（上次运行时间/工具版本/top 模块），
  #13 user 催「情急需」后 session 截断，**assistant 从未产出最终评估报告**（哪些文件需要修改、
  具体改什么、如何在 FS_LINT 下落地）。
- 无 gold 交付 ⇒ check() 无真实参照可锚定；强行 B档 synthesized 会变成「我臆造 gold」，
  违反 §4「判分有牙 + 真实 trace 溯源」精神（gold 须来自 trace 实际产物或可从 fixture 动态推导）。
- **parked**，理由 `incomplete_trace_no_gold`。下轮不重复捡。

## 真实项目信息（备查，若日后做 B档 reconstructed 可复用）

- 工程路径: `/proj/lacaa/TV1_TestChips/CXTV1_FS001A/frontend/work`
- 工程类型: SpyGlass lint（vcst_rtdb/spyglass）
- 关键文件: Makefile / lint.tcl / readme / design_rtl.list / design_rtl_top.list /
  vcst_rtdb/reports/run.log / vcst_command.log / vcst_session.log
- 上次运行: 2026-10-28 09:10, VC Static V-2023.12-SP1, top=AMSGrp
- 可写落地: `/home/lorikx/MY_SANDBOX/FS_LINT/`

## 本轮处置

- ledger c3dxb → **parked** (note: incomplete_trace_no_gold, 14 msgs, assistant 未交付最终评估)
- 本轮 0-case（质量闸门：无 gold 不造）
- 治理产出: ① shard_mc.A 10→5 落地（16:4x 令称已改实未改，本轮真正修正）
  ② A.jsonl 工作树被截断丢失 6 条已提交 case（r941/r943/+2/r946/r947）→ `git checkout HEAD` 恢复 439 行
  ③ r947 rtcv6 漏记 ledger → 本轮补记 case
