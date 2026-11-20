# Trace deepread — 3pn6a (revival #48, r668)

- **session**: `1791437695704_3pn6a.messages.json`
- **user / host**: thomasz @ hfeg0pkn002 (operating on qilongw's simulation)
- **mc / domain**: 24 / spice_sim
- **form**: debug-Q&A → 根因诊断报告 (root-cause diagnosis)
- **trace size**: 104256 B, 14 msgs, 1 substantive user turn
- **旧判定**: parked "Q&A code-comprehension reject" (2026-11-11) → r618 reaudit 复活 → r668 变现
- **trace 文件位置**: 子目录 `1791437695704_3pn6a/` 下（非根 .messages.json，host 端 find 校验 OK）

## 用户原话（msg[0]，verbatim）

> /proj/ddgoa/V0/workdir/qilongw/simulation/work_qilongw_BCTK_RowRed_schematic_ALPS/sim1/simresult/ff-40.log
> 看下这个log，最后产生的波形打不开，报错说波形不完整

## 助手工具链

1. `read_files` 读 ff-40.log 全文（带 ` N | ` 行号前缀）
2. `run_commands` 被禁（"Raw shell tool run_commands is disabled; use run_approved_command"）
3. `run_approved_command` 被 policy 拒（"Approved script owner mismatch"）
4. `list_allowed_files` 列 simresult 目录（root=/rundata/ddgoa/V0/simdir/finesim/...）
5. `get_agent_policy_status` 查策略
6. `read_files` 读 ff-40.log 57-232 行 + ff-40.elog
7. `read_files` 读 ff130.log 270-310 行 + tt25.log 270-310 行（对比 3 corner）
8. 给出结构化结论

## 关键证据（从 trace read_files tool_result 逐行还原）

ff-40.log 尾部（283-291 行附近）：
```
16.00us (100.0 %) at Thu Oct  8 01:36:18 2026 (22m 33s)
    finished at 16us
Fatal error: tlist file size should not be zero.
scope_blk_cnt: 2, var_blk_cnt: 19
Notify Synopsys support to assist with this problem.
Fatal error: fd_slist file size should not be zero.
vc_blk_cnt: 355963
    output file './simresult/ff-40.fsdb'
    # time points: 281822
End of Transient Analysis
...
FineSim Successfully Completed at Thu Oct  8 01:36:25 2026
```
中间（80% 之后）：
```
SyncControl_Lock(): failed, fd:10, errno:116, message:Stale file handle.
```
头部：
```
Command line: finesim -i ff-40.sp -o ./simresult/ -np 8
Working Directory: /rundata/ddgoa/V0/simdir/finesim/workdir/qilongw/simulation/work_qilongw_BCTK_RowRed_schematic_ALPS/sim1
include: </proj/ddgoa/V0/workdir/qilongw/sim_setup/FinesimOption.sp>  ← /proj 路径
```

ff130.log 尾部：同样 `tlist/fd_slist zero` + `SyncControl_Lock errno:116 Stale file handle`，vc_blk_cnt:356538, time points:270084, finished at 17us, output ./simresult/ff130.fsdb。

tt25.log 尾部：同样 `tlist/fd_slist zero`，但 sync 是 `SyncControl_Unlock errno:37 No locks available`，vc_blk_cnt:265917, time points:326345, finished at 24us, output ./simresult/tt25.fsdb。

## 根因（agent 结论 + 我的判定）

波形「不完整/打不开」**不是网表/仿真数值/设计问题**，而是**文件系统（NFS）写入失败**导致 fsdb 没有正常收尾：
- 瞬态本身 100% 跑完（finished at 16us）
- fsdb 落盘/收尾阶段报 `tlist file size should not be zero`(scope_blk_cnt:2,var_blk_cnt:19) + `fd_slist file size should not be zero`(vc_blk_cnt:355963) —— tlist/fd_slist 是 fsdb 的 scope/变量树头部索引，报 zero = 头部索引残缺，而 vc_blk_cnt(波形值块)很大 ⇒ 波形值数据有但头部索引没写全
- `SyncControl_Lock errno:116 Stale file handle`(ESTALE) + tt25 里 `SyncControl_Unlock errno:37 No locks available`(ENOLCK) ⇒ NFS 陈旧句柄/锁失效
- Working Directory 走 `/rundata/...`，用户打开 `/proj/...`，两者同一棵树经 NFS 挂载 ⇒ 7 小时长仿真期间 NFS 抖动
- 3 个 corner 尾部一字不差重复同样错误 ⇒ 系统性，非设计

## 建议修复

把 FineSim `-o` 输出指到计算节点本地盘/本地 scratch（local $TMPDIR / /scratch），仿真结束后再把 *.fsdb 拷回 /proj 归档；检查 NFS 挂载稳定性（stale handle / nfslock / actimeo）；当前 fsdb 头部残缺，不建议当有效结果，应重跑。

## 造题决策

- **A 档 trace-faithful**：用户原话 + A primary.log（ff-40.log 从 trace read_files 逐行 strip ` N | ` 前缀还原）+ A ff130.log/tt25.log（trace 尾部片段 verbatim）
- **hidden B 叠加 cross-input guard**：合成 ss125/tt85/ff150 三个 corner，vc_blk_cnt/time_points/sim_end_time/corner 名/sync operation 全部不同于 A，但根因结构（NFS fsdb 写失败）一致
- **判分**：19 断言，含 8 条 cross-input value guard（sim_end_time / vc_blk_cnt / fsdb_file / time_points / affected_corners，每条 A≠B）+ A-leak guard（12 个 A token 禁现）+ 真跑 subprocess + 确定性 3 rerun + 4 假提交回归
- **case_id**: EDA-Eval-DesignFlow-FsdbNfsIncompleteDiag-001
- **自验**: ref 19/19 PASS（本地 + $JUDGE 布局双验）+ 3 negs(空壳/print-only-A/deleted-core)全 FAIL + hardcode_b 因隐藏 B 不可见而排除
