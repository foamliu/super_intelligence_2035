# jrjm6_sp_temp_param_alter.md — trace deepread · shard B · 2026-11-10

## trace source
- session: `1793240429367_jrjm6.messages.json` · user `ghyang` · host `hfeg0plg93` (10.129.8.225) · mc=62
- mtime: 2026-11-04 (sid 1793240429367 ms epoch)
- keywords: `netlist:239; hspice:45; drc:16; synopsys:2; lvs:1` — netlist+hspice dominant → spice_sim
- 137 msgs / 70 user turns (cline pi session)

## session arc (produce-tasks)
| U# | 任务 | 类型 |
|---|---|---|
| U#0 | 分析 run7.sh 是不是可运行程序 | consultation |
| U#5 | 复制 *-40.sp，文件名删去 -40 | produce-task (file rename) |
| U#11 | 对比 sim_p1a3 vs sim_p2a4，复制并改激励引用 | produce-task (stimulus sub) |
| U#21 | tt 后缀三文件中 ss 改成 tt | produce-task (corner sub) |
| U#26 | sim_p1a3/p2a4 的 meas 部分按 case5 改 | produce-task (meas edit) |
| U#32 | sim*.sp 的 meas 部分按 Vcsl 后缀目录改 | produce-task (meas edit) |
| **U#39** | **温度参数化：`.temp -40c`→`.temp {ptemp}`，删旧 .alter，加 ptemp=25/45/98/130 四组 .alter** | **produce-task (本 case 选料)** |
| U#49 | 改 run-all，bsub 替换为 15 组文件 | produce-task (batch gen) |
| U#56 | 按 sim_p1a3_pl3_ff.sp 前三行改其他 sim*.sp | produce-task (header template) |
| U#62 | 整合 sim_p1pl3_ss130*.mt0，取两组数据列成表 | produce-task (mt0 agg) |
| U#69 | pvcsl→0.88V，注释 pvblh，改 include 路径 | produce-task (param edit) |

## U#39 详情（本 case 金标准来源）
- 用户原话：「现在的 sim*.sp 文件中有两句跟温度相关的是-40度，我想把这两处替换成参数，把这个参数定义在靠前的位置先取值-40，然后把后面的.alter都删掉，改成这个温度参数25、45、98、130的四组alter」
- assistant 流程：read sim*.sp 头/尾 → 列 corner 目录 → 写 `/home/ghyang/refactor_temp_alter.py`
- 真实金标准脚本 `refactor_temp_alter.py`（2260B，已从 trace msg#87 editor new_text 提取）：
  1. `.temp -40c` → `.temp {ptemp}`（硬编码 -40c）
  2. 截断首个 `.alter` 到 EOF（删旧 pvcsl 扫描 alters）
  3. 追加 4 个 `.alter` + `.param ptemp=25/45/98/130`
  4. `.param ptemp=-40` 已在文件靠前，保留不动
- 真实 .sp 资产在 `/proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_corner/` — e0031982 无权限读（Permission denied），按 trace 中 read_files 显示的结构 B-synthesized 资产（`.param ptemp=-40` 靠前 + `.temp -40c` + `.alter` pvcsl sweep + `.meas tran` + `.subckt`）

## case 合成
- **EDA-Eval-DesignFlow-SpTempParamAlter-001** · spice_sim · B-synthesized · L1 · k=14
- 资产 A=sample.sp（YiotwPump subckt，3 pvcsl alters，temp=-40c）
- 隐藏 B1=hidden_b1.sp（DDGClk subckt，4 pvcsl+load alters，temp=-40c）
- 隐藏 B2=hidden_b2.sp（VcslSense subckt，2 vdd alters，temp=-25c，反硬编码）
- reference=sp_temp_param_ref.py（泛化版：找任意 `<N>c` 温度，非硬编码 -40c）
- check.py 14 断言 a-n（zip/编译/B1 跑出/`.temp {ptemp}`/无 -40c/`.param ptemp=-40` 保留/旧 alter 清空/.alter=4/ptemp=25,45,98,130/DDGClk 保留/.meas≥3/.tran 保留/B2 -25c 泛化/B1≠B2 交叉泛化）
- 自验: ref PASS 14/14 + 6neg 全 FAIL + §4.9 三假(empty_shell→d / only_print→c / ref_core_deleted→c)全 FAIL
- 断言门: k_rationale=k_check=14≥8 ✓；test 字段与盘上 check.py 字节同步 ✓
