# r1111 deepread — xx9v7 (e03101) LPDDR6 verilog simdir 三文件夹同名文件内容 diff

- **session**: `1795435315844_xx9v7.messages.json` @ `hfeg0pgn145` (user `e03101`)
- **match_count**: 15 (verilog:919; analog:289; netlist:28; cmos:7 — 96% A-verification)
- **trace**: 35 msgs / 265 KB; subdir path `sessions/<sid>/<sid>.messages.json`
- **A-domain verdict**: verilog+systemverilog dominant (verilog:919 >> analog:289, > C=0), pure A-verification ✓

## 用户真实意图（trace-faithful）

用户 e03101 给出 3 个 LPDDR6 verilog simdir 文件夹：
- `lpddr6_tb_1119`（第一个，参考）
- `decqa`（第二个）
- `lpddr6_tb`（第三个）

原话：「帮我比对第一个文件夹内的所有内容和第二和第三个文件夹内的全部同名文件之间内容是否有差异」。

即：递归遍历每个文件夹，按相对路径（relpath）配对同名文件，对「两边都存在」的文件比较内容是否相同；同时报告只在一侧存在的文件。参考文件夹（dir1）分别与 dir2、dir3 比对，产出两组对比。

## assistant 工具链

1. `list_allowed_files` 列 3 个目录（/proj/decqa/... 被 sandbox 解析为 /rundata/decqa/... 可读根）。
2. 写 `compare_dirs_v2.py`（md5 递归比对）→ 首次跑 SIGKILL（输出 11k+ only-ref/only-oth 行把 stdout 撑爆 + 第二组比对未完成）。
3. 改 `compare_dirs_v3.py`：报告写文件 + stdout 只打印 compact 摘要 → 跑通：
   - dir1 vs decqa：common=11109, identical=11106, **different=3**（`config/tbconfig` netlistversion 行；`probe.tcl` -packed 值 400000→297523；`top.sv` `.sys_temp` 端口注释 vs 接通）
   - dir1 vs lpddr6_tb：common=3276, identical=3274, **different=2**（`A_Pattern_Sim.v` 整体重写 214→27 行；`pevave_tasks.sv` 延时表成片改写 + CK 延时 `#(2.3*t_val)`→`#(30)`）
4. 写 `diff_detail.py`（difflib unified_diff 展开那 5 个差异文件）→ 修两个 bug（漏 `import os`；bytes 未 decode 成 str）→ 输出逐文件 diff 摘要。
5. 给用户中文总结：同名文件之间确有差异，与 decqa 差异极小（3 文件配置层小改），与 lpddr6_tb 差异集中在 A_Pattern_Sim.v / pevave_tasks.sv（另一套简化/改版实现）。

## 造题（B档 synthesized）

真实 `/rundata/decqa` 工程树沙箱不可达 → 按 trace-faithful relpath 结构 + 同类内容差异合成。

- **A（SUT 可见）**: `dir1_A`(10 files)/`dir2_A`(7)/`dir3_A`(8)，LPDDR6 主题，复刻真实差异类型（tbconfig netlistversion / probe.tcl -packed / top.sv sys_temp 端口 / A_Pattern_Sim.v 整体重写 / pevave_tasks.sv 延时表改）。
  - dir1 vs dir2：common=4, identical=1, different=3, only_ref=6, only_oth=3
  - dir1 vs dir3：common=6, identical=4, different=2, only_ref=4, only_oth=2
- **hidden-B（判分用）**: `dir1_B`/`dir2_B`/`dir3_B`，DDR5 主题，同结构不同 token，A/B 判别 token 零相交。
- **deliverable**: `compare_simdirs.py`（通用三目录同名文件内容 diff 器）。
- **check**: 跑 hidden-B 验 16 断言（zip+py_compile+exit0 JSON+pairs 结构+两组 pair 的 common/identical/different count 与 file set 全对 oracle+anti-hardcode A token 不泄漏/B token 必现+determinism 3x md5）。**JUDGE_CONTRACT 新契约：check() `return True`/`return False`**（非 raise/None）。
- 自验：ref PASS 16/16；§4.9 三假（empty/print-only/core-deleted）全 FAIL；neg_selftest 4/4 ALL_FAIL_OK。
