# deepread: 1793704285912_k2x6m — TM_FsPgm DQ-switch block 适配还原

- **trace**: `1793704285912_k2x6m` · user `daiweilu` (lu4zi) @ `10.129.32.83` · mc from scan
- **domain**: digital (LPDDR5 testmode pattern) — A shard
- **agent**: lead · 124 msgs (63 user / 61 assistant) · 9 user text turns
- **tools**: read_files×18, editor×15, run_approved_command×13, list_allowed_files×5, search_codebase×1
- **deepread 轮次**: r575 (fresh-deepread, scp 855KB messages.json 到 .75 workdir 解析)
- **判定**: **可造** (r567 type-(a) 单聚焦 capability, 与 r574 TmBusToggleAnalyze-001 同用户同域同型)

## 用户真实意图（按 trace 原文）

1. **#1 (主任务)**: 把 `tm_fuse_backend_6400.run` 中最后执行的 `TM_FsPgm` 替换成 `TM_FsPgm_new`，结果 dq 全=x。给两个 .v 路径 (`TM_FsPgm.v` / `TM_FsPgm_new.v`)，要排查。
2. **#2**: "TM_TDQEN不是没有clear吗"（Q&A）
3. **#3**: 在 `tm_fuse_probe.run` 中替换成 new 又不报错（对比线索）
4. **#4 (produce 核心)**: "可以帮我做一版适配的new吗" → 要一个适配 backend 的 `TM_FsPgm_adapt.v`
5. **#5**: "part3有什么用？我看代码一直在重复"（Q&A）
6. **#6**: "为什么backend配置多环境会影响dq？我不是全定成dq0了吗"（Q&A 根因）
7. **#7**: "probe跑entrymode1并不会报错"（线索）
8. **#8**: "分析一下backend.run的结构，每一块在做什么，模式怎么确定"（Q&A 结构分析）
9. **#9**: "lpddr5.tdqswitch = 1'b1; // 开 TDQ 切换 这个是否会和我锁dq0冲突"（Q&A 冲突确认）

## assistant 工具链与关键产物

agent 写了一组 Python 脚本（editor 创建于 `/home/daiweilu/`）逐步定位 + 合成：
- `diff_tm.py` — diff `TM_FsPgm.v` vs `TM_FsPgm_new.v`，定位差异（new 把 DQ 切换块用 `/* */` 注释掉 + 加了 `LatchDq = "dq0"` 锁）
- `find_helpers.py` / `grep_td.py` / `scan_tm.py` / `find_funcs.py` — grep/扫描 task/case/LatchDq 结构
- **`build_adapt.py`** → **`build_adapt2.py`**（最终版）— 读 `TM_FsPgm_new.v`，按行索引 `setline()` 做 6 类编辑：
  1. task 重命名 `TM_FsPgm_new` → `TM_FsPgm_adapt`（L1/L2/L8）
  2. 还原 `/*if(entry_mode==1)begin ... end*/` → `if(entry_mode==1)begin ... end`（L11/L25）
  3. 还原 `/* case(LatchDq) //load input ... endcase*/`（L54/L62）
  4. 还原 part2 `/*case(LatchDq) //clear input ... endcase*/`（L234/L252）
  5. 还原 `/*case(LatchDq) //clear uotput ... endcase*/`（L318/L326）
  6. 还原 part3 `/* case(LatchDq) ... */`（L345/L563，含 L357 pattern_name）
  7. 删除 `LatchDq = "dq0";` 锁行（L29）
  - 预检 `chk{idx: frag}` 用 assert 锚定行内容
- **`verify_adapt.py`** — 校验产物：注释深度平衡(EOF depth==0) + 关键还原存在且 active（`task TM_FsPgm_adapt` / `if(entry_mode==1)begin` / `case(LatchDq)` 不带 `/*`）

## 根因（agent 推断）

`TM_FsPgm_new.v` 为适配 probe.run 把 DQ 切换测试模式块全部 `/* */` 深注释 + 锁 `LatchDq="dq0"`；但 backend.run 需要 DQ 切换（多环境），直接用 new → dq 全 x。适配 = 还原所有 DQ 切换块 + 解锁 + 重命名避免与旧 task 重复定义。

## 可造性判断

**可造**（r567 type-(a) 单聚焦 capability）。固化能力 = **"testmode pattern DQ-switch 深注释块还原 + task 重命名 + dq-lock 解除"** 结构化转换器。不依赖私有 `/proj` 路径（B 档合成输入 .v 即可）。

## B 档合成计划（供下轮交付，DEBT）

**case_id 候选**: `TmDqSwitchAdaptRestore-001` (digital, L1-B, k≥12)

**ref 解 `tm_dqswitch_adapt_ref.py`**（结构化，非行索引）:
- 读输入 `tm_spec.v`（Verilog task，含若干 `/* ... */` 深注释 DQ-switch 块 + 一个 `LatchDq="<val>"` 锁行）
- 正则/状态机扫描 `/* ... */` 块，识别"含 `case(LatchDq)` 或 `if(entry_mode==1)` 的块" → 去掉外层 `/*` 与 `*/`（保留块体）
- task 头重命名：`task <OldName> (` → `task <NewName> (`（NewName 由输入指定，≠ OldName）+ `begin:<OldName>_task` → `begin:<NewName>_task` + 内部 `$sformat(pattern_name,"%0s<OldName>"...)` → `<NewName>`
- 删除 `LatchDq = "<anyval>";` 锁行
- 校验注释深度平衡（EOF depth==0，不能留下半截 `/*`）
- 输出 `tm_adapt.v` + JSON 报告 `{task_renamed, blocks_restored:[{loc,kind}], lock_removed, comment_balance_ok, lines}`

**check.py 断言 (k≥12)**（全独立可 FAIL，跑 hidden B）:
① 输出 .v 存在且非空
② task 头已重命名为 NewName（含 `task <NewName> (`）
③ `begin:<NewName>_task` 存在，OldName 的 begin 不再存在
④ pattern_name $sformat 含 NewName
⑤ ≥N 个 DQ-switch 块已还原（`case(LatchDq)` 出现且其前无 `/*` / 同行无 `*/`）
⑥ `if(entry_mode==1)begin` 块已还原（前无 `/*`）
⑦ `LatchDq = "..."` 锁行已删除（grep 不命中）
⑧ 注释深度平衡（自验 depth==0 at EOF）
⑨ 旧 task 名 OldName 在 task 头位置不再出现（避免重复定义）
⑩ 块体内容保留（还原后 `case(LatchDq)` 与 `endcase` 配对数 == 输入块数）
⑪ 确定性（3 seed 同输入 → sha256 一致）
⑫ 反硬编码（A≠B：A 的 OldName/NewName/锁值/块数 与 B 全异，硬编 A 者在 B 上 FAIL ⑤/②/⑦）

**hidden B** `tm_spec_B.v`: OldName=`TM_DqSweep`/NewName=`TM_DqSweep_adapt`, 锁 `LatchDq="dq_all"`, 4 个深注释块（entry_mode randcase + 3 个 case(LatchDq): load/clear-in/clear-out），块体信号名/分支与 A 全异。与 A（OldName=`TM_FsPgm_new`/NewName=`TM_FsPgm_adapt`, 锁 `dq0`, 5 块）结构同、取值全异。

**negatives** (≥3): naive_passthrough(原样输出)→⑤/⑦; print_expected(只打印期望串)→①; lock_not_removed→⑦; rename_skipped→②; half_block_uncomment(只去 `/*` 不去 `*/`)→⑧。

**自验**: ref selftest 12 PASS + negative_selftest 全 FAIL + §4.9 三假提交 FAIL + 3x sha256 一致 + jsonl roundtrip。

## 不可造风险

低。唯一风险 = 合成 .v 输入需保证注释块语法合法（`/* */` 配对）以使 comment-balance 断言有意义；ref 用状态机而非行索引，对 B 的不同行布局鲁棒。与 r574 同用户同域，方法论已验证（r574 k=16 PASS）。

## ledger

- session `1793704285912_k2x6m` → claim (本轮)
- 状态: deepread 完成, **synthesis DEBT** (下轮交付 TmDqSwitchAdaptRestore-001)
- 不 park（可造）；下轮 mark --status case --case-id TmDqSwitchAdaptRestore-001
