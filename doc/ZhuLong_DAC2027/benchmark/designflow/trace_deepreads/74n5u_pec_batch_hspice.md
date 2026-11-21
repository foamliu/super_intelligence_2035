# deepread 74n5u (e0039786 @ hfeg0pkn005, mc60) — PEC GUI batch GDS→netlist→pair SP→Hspice

**session**: `/home/e0039786/.cline/data/sessions/1794998436688_74n5u.messages.json` (68 msgs, 355KB)
**user 原话** (msg 0):
> 修改一下路径/home/e0039786/Desktop/DUT_lib/loop中的pec_gui.py，新增一个批量任务的功能，勾选后：可以对一批GDS进行抽网表和Hspice仿真；Browse GDS 和 Browse SP 可以选择多个GDS与SP文件，新增一个排序框，可以对选择的GDS和SP进行排序，gds抽网表的顺序将按照数字从小到大进行，GDS抽出的网表和排序数字相同SP文件进行配对，一起放入指定的路径下，等所有数字的dspf网表与sp文件都存入指定路径后，再调用指定路径下的run程序，批量提交Hspice 仿真任务。

## 真实意图
给已有的 Glory-PEX + Hspice GUI (`pec_gui.py`) 加「批量任务」：多 GDS 抽网表 → 按排序号(从小到大)与 SP 配对 → DSPF+SP 放入指定目录 → 全部放好后再调 run 程序批量提交 Hspice。

## agent 工具链（实测）
- `list_allowed_files` / `read_files` 读 pec_gui.py + 依赖 (pex_sim.sh, fix_inc.py, make_sp.py, comment_subckt.py)
- `editor` 增量改 pec_gui.py：STATE_KEYS 加 BATCH_*  / checkbox + `_build_batch_ui` / `_toggle_batch` 调用 / `on_save` 存 BATCH_* / 插入 batch 方法块 / 修注释 typo / 改 `_batch_remove_sel` 变量名
- `_syntax_check.py` (py_compile) 验证语法
- `_batch_logic_test.py` **headless 逻辑测试** (stub `_run_cmd_log` + Glory 抽网表 + fix_inc + run 程序)，验证：排序号配对、dspf+sp 放入 batch_dir、run 程序只在全部放好后调一次、cwd=batch_dir、失败 GDS 跳过删除

## 可测核心 (用于造题)
`_batch_worker(self)` + `_drop_pair(self,gds,sps,i)` 是批量逻辑核心，可 headless 测试（stub `_run_cmd_log`）：
- 按 index 顺序 (i+1 = 排序号 num) 处理每对 (gds[i], sps[i])
- 调 `pex_sim.sh` 抽网表 (env: NO_HSPICE=1, NO_PLACE=1, GDS_SRC, SP_SRC, COMMENT_SUB?, CLEAN_GDS?)
- rc!=0 或无 dspf → `_drop_pair` 删除该对 + 刷 GUI，跳过
- 找 `<base>_*.dspf` (mtime 最新) → 拷到 `batch_dir/<NN>_<dspf>` (NN=num, 2 位)
- 调 `fix_inc.py --sp s --dspf dspf_dst --out sp_dst` 改写 .inc 指向同目录 dspf → `batch_dir/<NN>_<spname>` (无 .sp 后缀加 _pair.sp)
- 全部放好后(placed>0) 才调 run 程序 (空则自动找 batch_dir/run*)，cwd=batch_dir
- gds/sp 数量不等 → 立即 FAIL 不调 run；placed==0 → ABORTED 不调 run

## 造题决策 (A 档 trace-faithful, L1 离线 Python)
- **case_id**: EDA-Eval-DesignFlow-PecBatchHspiceFlowGen-001
- **asset A** = 真实 pec_gui.py (577 行) 但 `_batch_worker` + `_drop_pair` 两方法体替换为 `raise NotImplementedError` (其余 UI/state/单 GDS on_run/_run_cmd_log 全保留)
- **hidden B** = B 版 headless 测试夹具 (异 gds/sp 名 + 异排序 + 异失败 GDS + 异 run 程序名)，anti-hardcode-A
- **reference** = 真实完整 pec_gui.py (POST, agent 产出)
- **判分** = headless 跑候选 pec_gui.py 的 `_batch_worker` on B (stub `_run_cmd_log`)，断言排序号配对/dspf 命名/SP .inc 重指/run 只调一次且 cwd/失败跳过删除/NO_PLACE+NO_HSPICE env/anti-hardcode-A/数量不等 fail-fast
- **k_check = k_rationale = 12** (a..l) ≥8 ✓

## 近重检查
- e0039786 既有 case: r928 SramSpecVecCoverage-001 (SRAM spec 向量覆盖) / r952 SramDctcoMetricsExtract-001 (SRAM DCTO metrics) — **意图不同** (本 case 是 PEC GUI 批量 GDS+Hspice 流)，非 near-dup ✓
- 同 PEC/Glory 主题无既有 B case ✓
