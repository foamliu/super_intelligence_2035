# trace_deepreads/1794221449278_bqqtk_coord3d_proj.md — shard B 深读

**session**: `1794221449278_bqqtk.messages.json` · user `e0046686` · host `hfhds201` (10.129.32.75)
**mtime**: 2026-11-10 08:22（仍在写） · **242 msgs / 1.3 MB** · spice_kw=530 · **domain: characterization**
**fresh-window**: 11-05 重扫令 path(d) — snapshot 20261109_224902 cutoff 11-09 22:54 之后的 fresh session（mtime 11-10 08:22）

## 用户意图（U#0，逐字原文，A-faithful 合规：提需求 / 未给根因 / 未给方案）
> `autosim_script/rev_cali_tools` 反标的后端脚本中:使用的 `lib_timing_tools` 抽 timing 需要按照（i_slew，c_slew，q_load）的三维坐标形式传递，再去匹配 template table，然后抽值；传递索引和传递值均可，传递值的时候需要做插值，当前优先用索引传递，值传递时先保持精确匹配，插值算法后续再做；
> 需要先做下 i，c，q 与 table 的关系梳理；一个三维坐标对应到某个 template table 时，只需要取三维坐标中的两个或者其中一个，且不同 template table 取的坐标或者坐标对可能不同；根据传入的（i_slew，c_slew，q_load）坐标，确定每个 template table 取哪 1 个或者 2 个值，组成新的坐标（对）或值（对），根据这个坐标（对）或值（对）再从 lib 中抽取 timing；
> 先梳理这个关系，再看怎么开发；参考 lib：/home/e0046686/new/tmp_s

- U#1 (msg 126): "当前优先将后端脚本对应增加3维坐标兼容完成，UI侧先不改动"（refinement of scope）
- U#2 (msg 231): "继续"

## assistant 工具链（关键产物）
1. 读 4 个参考 lib（`/home/e0046686/new/tmp_scan_data/lib`：tmpl 库 1p/2p/sp + k 库 1p）的 `lu_table_template` 定义，梳理 variable_1/variable_2 与 i/c/q 的关系：
   - **tmpl 库** CONSTRAINT: var1=related_pin_transition(**c**), var2=constrained_pin_transition(**i**)，c 轴 0.01~0.07ns / i 轴 0.05~0.35ns **两轴扫描值不同**
   - **k 库** constraint_template_7x7: var1=constrained_pin_transition(**i**), var2=related_pin_transition(**c**)
   - CLK_TRAN / mpw：1-D var1=related_pin_transition(**c**)
2. `prototype_coord3.py`（`/home/e0046686/zhulong_scratch/`）：实现 3D→各 table 轴投影，5 项检查（A-E）在 4 lib 上验证，ALL PASS
3. 改 `extract_lib_timing.py`（`+约 90 行`）：
   - `AXIS_POS = {"i":0,"c":1,"q":2}`
   - `_VAR_AXIS = {related_pin_transition:c, input_net_transition/input_transition_time:i, total_output_net_capacitance:q}`
   - `axis_for_var(var, pin_is_clock)`: constrained_pin_transition → clock pin 时 c / data pin 时 i
   - `template_def_for_entry(entry, tmpl_idx)`: 按 template 名 + 维度 + variable 语义 fallback 解析
   - `project_coord3(entry, tmpl_def, point, use_vals)`: 投影 3D 点到表实际轴；1-D 表补齐成 2 元组；不可映射 var 抛 ExtractTimingError
   - `extract_timing` 对 3 元组走 project_coord3，2 元组 legacy 直查（向后兼容）
4. 改 `rev_cali.py` `parse_coord`：3 段 "i,c,q" → 3D 点；保留 1/2 段 legacy（1 段补 0）；4 段 ValueError；索引 0..6
5. 改 `test_rev_cali.py`：新增 3D 用例（"1,2,3" 从非法移到合法 + 3D 集成 dry-run）
6. `final_validate.py`：4 lib 回归 + rev_cali 端到端 dry-run + CLI 冒烟，全绿
7. `make_patch.sh`：生成 patch + 一键应用脚本（项目目录本会话只读）

## 金标准（= trace 末尾 assistant 实际产物）
- `/home/e0046686/zhulong_scratch/rev_cali_3d/autosim_script/lib_timing_tools/extract_lib_timing.py`（1164 行，含 3D 投影）
- `/home/e0046686/zhulong_scratch/rev_cali_3d/autosim_script/rev_cali_tools/rev_cali.py`（652 行，含 3 段 parse_coord）
- 关键洞察：**非对角点上轴序决定结果**——tmpl 库 (c,i) 与 k 库 (i,c) 对同一 3D 点 (i=2,c=5) 给出不同值；对角点 (3,3,3) 两序一致（向后兼容验证点）；mpw/clkh 1-D 只取 c，与 i 无关。

## 本 case（B-synthesized L1 复刻）
- `EDA-Eval-DesignFlow-Coord3DProj-001`（characterization / synthesized / L1, k=14）
- 把 3D 投影逻辑抽成自包含：最小 `extract_lib_timing.py`(BEFORE 2D) + `rev_cali.py`(BEFORE 2D parse_coord) + `example.lib`(两种轴序) + `map.txt`
- check.py 用 3 随机种子生成隐藏 B lib（tmplB var1=c/var2=i；klibB var1=i/var2=c；badvarB var1=temperature），inline oracle 算期望值，断言 3D 投影/轴序/1-D 补齐/向后兼容/错误处理
- 自验：ref PASS 14/14 × 3 seeds + 4 neg（naive_before/hardcoded_a/only_print/ref_core_deleted）全 FAIL + §4.9 三假（empty/only_print/core_deleted）全 FAIL
