# deepread — sid 1793793264370_yr754 · reedchen · hfeg0plg93 · mc=36 · analog_context

## 真实任务（用户原话，msg0）
> 「/proj/ddgoa/V0/workdir/stephens/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0_stephens_schematic_ALPS/out_spf_t04 我现在有一批 vm 的数据，control_mc_spf_t04.sp 这个是数据产生的仿真激励文件，我希望你帮我整理数据，做成一个表格，要求统计每个 PVT corner 下面（数据以 alter 区分）统计的 vmlh 和 vmhl 最大最小平均这些统计数据」

## 对话流（99 msgs: 53 user / 46 assistant）
1. msg1-22 assistant 探索：agent-policy 可读根 `/`，定位真实路径经 symlink → `/rundata/ddgoa/V0/simdir/finesim/workdir/stephens/simulation/.../output_spf_t04/`（注意目录名是 `output_spf_t04` 非 `out_spf_t04`）。
2. msg20-23 读 stimulus.sp：base corner + 16 `.ALTER` 块，每块 MC sweep `monte=300`，measure `VMLH`/`VMHL`。输出在 `VM_RST0.mt0.csv`。
3. msg25-32 写探针脚本解析 .mt0.csv：
   - HDR1 `$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=1`
   - HDR2 `.TITLE '...'`
   - HDR3 列头 `mc_index, vmlh, vmhl, temper, alter#`
   - data rows 4213；unique alter# 14 个（1-14），每 corner 300 行（alter14=261）+ 52 空/汇总行
   - **汇总行格式**：`avg     1.4632e-01,     1.2544e-01,     2.5000e+01,     1.0000e+00,` —— 标签与 vmlh 合并在第1列，alter# 在第4列、第5列空。
4. msg33-40 写 analyze_vm_t04.py：解析→按 alter# 分组 MC 行（跳过 avg/std/min/max）→map alter→PVT corner→算 max/min/avg/std→输出对齐表格。msg38 修 cross-check（FineSim 把 label 与首值合并在同列）。
5. **金标准输出**（msg36/40）：
```
Corner                          n |  vmlh_min vmlh_max vmlh_avg vmlh_std |  vmhl_min vmhl_max vmhl_avg vmhl_std
TT@25C/PVCC=0.680V            300 |    0.1171   0.1806   0.1463   0.0099 |    0.0948   0.1560   0.1254   0.0101
SS@-40C/PVCC=0.820V           300 |    0.1179   0.1863   0.1476   0.0109 |    0.0898   0.1526   0.1216   0.0104
...
```
14 corners: TT/SS/FF × {-40,25,130}C × 多档 PVCC。

## 合成计划（VmMcStatOrganize-001）
- **parser-pattern**（同 FinesimLisOrganize r609 风格），纯 stdlib SUT `vm_mc_organize.py <mt0.csv> <sp> <outdir>` → report.json/csv/txt。
- 三族 disjoint：
  - A(visible,12 corner×60 MC,资产给 SUT)
  - B(hidden,10 corner×80 MC,判分主跑,corner 集/取值与 A 不同)
  - C(cross-input,9 corner×50 MC,反硬编码,scaled)
- .sp 每块 `.TEMP` + `.param PVCC=.. pcorner='..'`，corner 名 `<pcorner>@<temp>C/PVCC=<vcc>V`。
- check.py 14 cond a-n：zip 结构/py_compile/无泄漏/A 运行/A stat/B 运行/B corner 数/B vmlh stat/B vmhl stat/B n(汇总排除)/C 反硬编码/确定性 3-seed/CLI/corner 名格式。
- 自验：ref 14/14 PASS + 4 neg ALL FAIL + §4.9 三假 ALL FAIL。
- **注意真数据文件无法访问**（permission denied，owned by stephens），故全部合成（合规：§4.1 B 必须与 A 不同，金标准=trace 末尾用户接受的对齐表格格式）。
