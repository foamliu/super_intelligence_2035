# trace_deepreads/mah5p_sim_inc_missing_diag.md — 1794105806205_mah5p deepread

## trace
- session: `1794105806205_mah5p` (yanghao @ hfhds201, 72 msgs, 70% spice ratio)
- source: hfhds201 local `.cline/data/sessions/` (cron blind spot), FRESH since 2026-11-08 00:00 (mtime 11-08 10:51)
- discovered: 2026-11-08 12:1x rescan (eda_flow run_commands on .75, session t0002965_20261108-loopB_shardB-rescan-1108-1210_0)

## 用户轮 (A-faithful 选轮)
- **U#0 (逐字, prompt)**: `/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/yanghao/2_TsComp_post/result_post 下面的仿真为什么报错了`
  - 提出需求（"为什么报错"），🚫 无根因 / 无修复方向 → 符合 A-档选轮

## 金标准 (assistant msg#71 排查结论)
### 报错原因
- 9 个仿真 (1_pvt_130 / 1_pvt_m40 / 2_mc_130 / 2_mc_m40 / 3_ac / 4_ioff_130 / 4_ioff_m40 / 5_ADcomp_130 / 5_ADcomp_m40) **全部报同一个错误**，启动约 2 秒后解析网表阶段退出:
  ```
  ERROR! unable to read file 'AG_TS_1stStgComp.spf_RCC'
  (/rundata/commonIP/v1/lp5x/v0/simdir/anasim/yanghao/2_TsComp_post/Setting.sp:18)
  : No such file or directory
  ```

### 根本原因
- `2_TsComp_post/Setting.sp` 第 17~19 行:
  - 第 17 行: `.inc '/proj/commonIP/.../netlist'` — 绝对路径，正常
  - 第 18 行: `.inc 'AG_TS_1stStgComp.spf_RCC'` — **相对路径，文件不存在 → 报错**
  - 第 19 行: `.inc 'AG_TS_comp.spf_RCC'` — 同样不存在（修完 18 行还会报这个）
- 第 18、19 行用相对路径引用两个 post-layout 提取网表（`.spf_RCC` = PEX/LPE 输出的 SPF 寄生参数网表），FineSim 到工作目录 `2_TsComp_post/` 下找，但该目录下没有这两个文件。

### 三点确认（证据链）
1. **全项目范围内都找不到这两个文件** — commonIP 库、`/proj/ddgoa/V0/ver/pex/` 各用户目录、各 sim/work 目录均无 `AG_TS_1stStgComp*` / `AG_TS_comp*`，连对应 cell 目录都不存在（PEX 提取还没做）。msg#47/65/67 find 结果全空。
2. **当前测试台网表根本不用这两个子电路** — mengxind 的 `netlist.presim`（949 行）实例化的是 `TsCoreAFBiasIP`、`TsCoreAFAcompIP`、`TsCoreAlgDcompIP` 等，msg#55 grep `AG_TS_1stStgComp|AG_TS_comp` 结果为空。这两行 `.inc` 是从别的 block 模板带过来的残留。
3. **对比正常配置** — 同项目 `4_TsCore_post/Setting.sp` 引用提取网表用绝对路径: `.inc '/proj/ddgoa/V0/ver/pex/mengxind/TsCoreAlgFeIP_wow/TsCoreAlgFeIP_wow.spf_RCC'`

### 修复建议
- 方案 A（推荐）: 注释掉 Setting.sp 第 18、19 行 (`*.inc 'AG_TS_1stStgComp.spf_RCC'` / `*.inc 'AG_TS_comp.spf_RCC'`)，重新提交 runsim。
- 方案 B: 对 AG_TS_1stStgComp / AG_TS_comp 跑 PEX/LPE 提取生成 .spf_RCC，拷到工作目录或写绝对路径。

## assistant 工具链 (msg flow)
- msg#1-10: list_allowed_files + read_files 9 个 sim *.log → 全报同一 ERROR
- msg#12-20: list_allowed_files backup_spice/runsim/网表来源目录 → 找不到 .spf_RCC
- msg#23-27: 对比 4_TsCore_post/Setting.sp (绝对路径) + pex 目录搜索
- msg#41-51: run_approved_command (shell-runner) find_spf.sh → grep netlist.presim subckt/.inc
- msg#53-57: grep AG_TS_1stStgComp/AG_TS_comp in netlist.presim → 空 (未实例化)
- msg#63-71: 全项目搜索确认文件不存在 → 排查结论

## 可移植子技能 (L1)
- 输入: `<result_post_dir>` (各 sim 子目录 + *.log) + `<setting_sp>` + `<netlist_presim>`
- 解析:
  1. 各 sim *.log 的 `unable to read file 'X' (path:LINE)` ERROR → failed_sims + unified_error + missing_file + setting_sp_line
  2. Setting.sp `.inc` 行 (line_no / target / is_relative / filename)
  3. netlist.presim `.subckt` 名 + `X...` 实例化 (last token = 引用 cell)
- 交叉引用:
  - root_cause = {missing_file, setting_sp_line, path_type=relative, file_exists}
  - unused_includes = 相对 .inc 的 stem 不在 subckt/实例化中 (残留模板)
  - fix_suggestion = 注释掉出错 .inc 行
- 输出: 结构化 JSON (零硬编码，input-agnostic)

## case
- EDA-Eval-DesignFlow-SimIncMissingDiag-001 (spice_sim A-faithful L1, k=16)
- A = A_sim_post (真实重建: 9 sim 子目录 + A_Setting.sp + A_netlist.presim 949 行)
- hidden B = B_sim_post (结构不同: 6 sim {1_dc_125..6_mc_tt} + B_Setting.sp 缺 AG_XY_foobar.spf_RCC @ line 22 + B_netlist.presim 612 行)
- 判分 16 断言 (a-p): 含交叉输入守卫 (A→AG_TS_1stStgComp/line18 证泛化) + A-only 泄漏闸门 + 3 次幂等
- 自验: ref PASS 16/16 + 4neg FAIL distinct(e/b/c/f) + NEG_RC=0 + §4.9 三假 FAIL + 断言闸门 16==16≥8 + jsonl test sha roundtrip
