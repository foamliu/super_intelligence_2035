# 深读笔记 — trace `1792400027384_ahjnv`（zhukaic @ hfeahpc503, mc=397）

- **用户/主机**：zhukaic @ hfeahpc503（10.129.33.26），cline lead agent + deepseek-v4-flash
- **session 文件**：`/home/zhukaic/.cline/data/sessions/1792400027384_ahjnv/1792400027384_ahjnv.messages.json`（5696 行 / 667 KB）
- **工具命中**：hspice=484, netlist=226, schematic=16, pyAether=5, calibre=1（spice-dominant）

## 真实任务（用户原话两轮）
1. `读取skill，路径为/home/zhukaic/aether_skill/ota_skill/ota_2stg.md`
2. `立即执行`

skill 文件 `ota_2stg.md`（2275 B）定义了完整规格：作为资深模拟 IC 工程师，设计**二级米勒补偿运放**，通过修改 `ota_2stg_netlist.sp` 的 W/L（finger 尺寸限制 max=7.8u/min=200n，如 w/l=10u/2u nf=1 超限→改 nf=2），调用 `runsim.sp` 提交单次仿真，3 次迭代机会（允许并行 2 仿真），根据每轮 gain/PM/gbw 反馈明确给出下次改的器件名+W/L；用完 3 次未达标可把偏置电流调到 4-8uA 再试一次。**验收**：gain>60dB / PM>60° / gbw>1MHz。输出 txt 报告（Trial Summary / Measured Performance / Next-Step Recommendation）。

## 真实流程（assistant 工具链 + 产物）
- 关键文件路径（`/home/zhukaic/aether_skill/ota_skill/`）：
  - `ota_2stg.md`（skill）、`ota_2stg_netlist.sp`（2265B，电路网表，**permission denied** 不可读）
  - `ota_2stg_sim.sp`（1297B，testbench：`.inc` option.sp + netlist，`.param pvdd1=1.8 pvcc=1.025`，`.op/.tran 10p 10u`，**`.LSTB stb mode=single vsource=v0`** + `.ac DEC 20 0.1 10G`，`.probe ac LSTB(DB:stb) LSTB(P:stb)`，`.meas ac GAIN max LSTB(DB:stb)` / `PM find LSTB(P:stb) when LSTB(DB:stb)=0` / `GBW when LSTB(DB:stb)=0` / `f_3db when LSTB(DB:stb)='GAIN-3'` / `gain_margin find LSTB(DB:stb) when LSTB(P:stb)=0`）
  - `runsim.sp`（74B）：**`bsub -q fqueue3_analog hspice -i ota_2stg_sim.sp -mt 4 -o ./ota_2stg_sim/`** ← LSF 集群提交
  - `ota_2stg_netlist_optimized.sp`（2033B，最终调好的网表，可读）：gen config `bias=8uA r1=800k c1=3pF inp_nf=1 inp_L=3u load_L=8u out_L=1.0u c0=5.0pF`，二级米勒结构（PMOS diff pair M2<0-3> + current mirror load M0/M1 + tail M3 + NMOS diff M0/M1 + second stage M7/M8 + miller C1 + r0/r1 feedback + cg1-8 parasitics），模型 `ptn`/`ntn_m`（CXMT foundry）
  - `report.txt`（6314B，最终报告）、`ota_2stg_sim/`（已有仿真数据）、iter1_a/b、iter2_a/b、iter3_a/b、final_a..h、tune_X1 等迭代文件夹
  - 大量辅助脚本：`analyze_sim.py`、`poll_sim.py`、`extract_iter*.py`、`gen_netlist.py`、`export_sim_results.py`、`submit_iters*.sh`、`check_jobs*.sh` 等

## 不可移植性（为何取子技能做 B 档 synthesized）
- `bsub -q fqueue3_analog` = LSF 集群队列，.75 沙盒无集群
- foundry 模型 `ptn`/`ntn_m` + `.inc '/proj/dscqa/V0/simdir/hspice/zhukaic/common/option.sp'` + corner 文件 `volt.sp`/`corner.sp`（ttt）+ `.param cthin/cthick/cgatein/capo` 均在 hfeahpc503/dscqa 项目，.75 不可达
- `.LSTB` loop-stability testbench 是 HSPICE 专用反馈环路稳定性测量；自包含 level-1 运放用开环 `.ac` + vdb/vp 即可等价测 gain/PM/gbw

## 取的子技能（本 case）
**开环 AC 表征 + 规格合规判定**：给定自包含 level-1 二级米勒运放 DUT `.subckt OPAMP` + spec（gain_min/pm_min/gbw_min），构建 HSPICE `.ac` testbench，`.meas` 提取 gain_dc/gbw/phase@unity/f3db/gain_margin，派生 PM=180+phase、gain_margin=-gm，判定规格合规。两个 SPICE gotcha 烤进任务：① deck 第一行是 title，`.inc` 不能是第一行；② HSPICE `m`=毫不是兆。可复现、有区分度（B 不同 sizing/规格→verdict 翻转）、防硬编码（跨输入守卫 A≠B）。

## GT（.75 HSPICE 真跑，固定 A/B）
- A（vto=0.50, kp_n=120/kp_p=50, ib=20u, cm=1p, load=500f, spec gain≥30/pm≥60/gbw≥1M）：gain_dc=39.1471dB, gbw=4.5470MHz, phase=-98.1058°, PM=81.8942°, f3db=49.6426k, gm=17.8662dB → verdict=**pass**
- B（vto=0.45, kp_n=150/kp_p=60, ib=10u, cm=0.5p, load=1p, spec gain≥35）：gain_dc=24.1997dB, gbw=3.6419MHz, phase=-95.4953°, PM=84.5047°, f3db=223.078k, gm=18.6523dB → verdict=**fail**（gain 24.20<35）

## 自验（.75）
- ref `gen_opamp_ac_char_ref.py` → check.py 14/14 PASS
- negative_selftest：empty_shell(2/3)、print_expected(12/14，被 d method + m 跨输入击穿)、ref_no_core(4/14，被 d/e-j/k/m 击穿) → NEG_RC=0
- §4.9 三假提交（空壳/print-expected/ref-no-core）全 FAIL
