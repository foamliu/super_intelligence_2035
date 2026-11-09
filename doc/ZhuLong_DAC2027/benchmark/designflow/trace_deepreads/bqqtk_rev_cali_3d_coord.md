# bqqtk_rev_cali_3d_coord.md — trace 深读笔记

**sid**: 1794221449278_bqqtk  
**user@host**: e0046686@hfeg0pkn001 (10.129.2.10)  
**size**: 1.28MB, 231 msgs  
**tools**: editor×114, run_approved_command×56, read_files×52, list_allowed_files×22  
**kw**: 7 (spice marker 偏低但 domain=characterization lib_timing 反标，finesim workdir)

## 选轮判定
- **U#0** (msg0): 「autosim_script/rev_cali_tools反标的后端脚本中:使用的lib_timing_tools抽timing需要按照（i_slew，c_slew，q_load）的三维坐标形式传递，再去匹配template table，然后抽值；传递索引和传递值均可，传递值的时候需要做插值，当前优先用索引传递，值传递时先保持精确匹配，插值算法后续再做；需要先做下i，c，q与table的关系梳理...先梳理这个关系，再看怎么开发；参考lib：/home/e0046686/new/tmp_scan_data/lib」
  - = **produce-task**（提需求：三维坐标抽 timing，先梳理关系再开发），未给根因/未给修复方案 → **A-faithful 合格** ✓
- **U#126** (msg126): 「当前优先将后端脚本对应增加3维坐标兼容完成，UI侧先不改动」= scope-directing（后端优先 UI 暂不动），非根因/修复，作 hint 不进 prompt
- 231 msgs phase 1 (msgs 0-227) 完整闭环，msg227 agent 生成 patch + apply.sh，msg230 全 PASS

## 金标准（trace msg227-230 用户接受的产物）
agent 在 mirror `/home/e0046686/zhulong_scratch/rev_cali_3d/autosim_script/` 修改 3 文件：
1. **lib_timing_tools/extract_lib_timing.py** (+186 行): 新增 3D 坐标投影
   - `AXIS_POS = {"i":0, "c":1, "q":2}` + `_VAR_AXIS`（related_pin_transition→c, input_net_transition/input_transition_time→i, total_output_net_capacitance→q）+ `_CLOCK_PINS=("CLK","CLKR","CLKW")`
   - `axis_for_var(var, pin_is_clock)`: constrained_pin_transition→c(clock)/i(data), else _VAR_AXIS
   - `template_def_for_entry(entry, tmpl_idx)`: 按 dimension+variable 语义 fallback 解析模板（CONSTRAINT→constraint_template_7x7, CLK_TRAN→mpw_template_7x0）
   - `project_coord3(entry, tmpl_def, point, use_vals)`: 3D 点投影到表的 1-2 个轴，返回 (coord, coord_val, axes)；1D 表补 0 成 2 元组
   - `extract_timing()`: 3-tuple 点走 project_coord3 投影，2-tuple 点走 legacy 直查表
   - CLI `--coord`/`--coord-val` 支持 2 或 3 值，range 0..6
2. **rev_cali_tools/rev_cali.py** (+41 行): `parse_coord` 支持 1/2/3 值
   - 3D: coord_index "i,c,q"→[(i,c,q)], coord_val "x,y,z"→[(x,y,z)]
   - legacy 单值补 0 成 2 元组（**msg213 bug fix**: 原 `if len(vals)<3` 致 2 值被多补 0 变 3 元组，改为 `if len(vals)==1: vals=[vals[0],0.0]`）
   - range check `any(not (0<=v<=6) for v in idxs)` 抛 ValueError
3. **rev_cali_tools/test_rev_cali.py** (+37 行): 10 项测试含 3D 集成用例

**验证**: test_rev_cali.py 10/10 PASS, final_validate.py PART1（4 lib 3D API 回归）+ PART2（端到端 dry-run）全绿。patch 文件 + apply.sh 交付。

## 关键技术事实（用于 check.py 断言）
- k-lib constraint_template_7x7: var1=constrained_pin_transition(data→i), var2=related_pin_transition(→c) → axes=(i,c)
- k-lib mpw_template_7x0: var1=constrained_pin_transition(clock→c) → axes=(c,)，1D 补 0
- 3D (i,c,q) 投影: constraint 取 (i,c), mpw 取 (c)，q 对这两种表不消费
- 对角线 (n,n,n)==legacy 2D (n,n): constraint axes=(i,c)，q 不消费，故 (n,n,n)→(n,n)==(n,n)
- coord_val 精确匹配（无插值），coord_index 直查
- msg213 bug: 单值 "3" 应补成 (3,0) 2 元组，不是 (3,0,0) 3 元组

## 资产获取
- 原始 /rundata 文件权限拒（e0031982 非 owner）
- 从 .75 ssh 读 mirror 修补后文件 + .patch 文件 + 4 real lib（/home/e0046686/new/tmp_scan_data/lib 可读 lacaa 组）
- mirror gold 文件 reverse-apply .patch 重建原始 V2 版
- 资产用忠实缩减重建：保留真实 API surface（load_map/parse_lib/select_value/extract_param/extract_timing/CLI）+ 真实 3D 函数，parser 简化为正则版（能解析 mini-lib 格式）
- mini_k_A/B.lib 手工合成（k-lib 风格，cell/index/timing 值 A≠B），mini_map_A/B.map 从真实 lib_timing_map_1p.map 缩减（clkh/clkl/tcyc→CLK, tdsr/tdsf→D）

## case
- **EDA-Eval-DesignFlow-RevCali3DCoord-001**: characterization, A-faithful, L1, k=15
- 可见 A: prompt=U#0 逐字 + extract_lib_timing.py(V2) + rev_cali.py(V2) + mini_k_A.lib + mini_map_A.map + task_brief.md
- 隐藏 B: mini_k_B.lib（cell SRAM_B, index 15-75, 不同 timing 值）+ mini_map_B.map + gold_extract_lib_timing.py + gold_rev_cali.py
- check.py 15 断言(a-o): zip 结构 + axis_for_var×5 + project_coord3×3 + extract_timing 端到端 B×3seed + 对角线×3seed + parse_coord×4
- 自验: ref PASS 15/15 + 3 neg(stub/original/coredeleted)全 FAIL + §4.9 三假(stub/printexpected/empty)全 FAIL + byte-sync sha 4d98988c
