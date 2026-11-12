# Deepread — 1788767715720_znoyb (rongjiez @ hfeg0pkn014 / 10.129.2.14)

- mc=25, keywords: netlist:119;synopsys:41 (D-domain-dominant, dratio=0.74)
- kanban log: `/home/rongjiez/.cline/apps/kanban/sessions/1788767715720_znoyb.jsonl` (3.03MB, 4 turns, 117 tool calls)
- workspace: `/home/rongjiez/jira_dev/mpqa/mp_1/scripts/` (runModelQA.pl original 137KB, runModelQA_new.pl refactored 61KB)

## 真实任务（4 轮，逐字还原自 chat_reasoning + chat_done.text）

### Turn #0（核心 produce-task）
重构 `runModelQA_new.pl` 中的 `summary_all_results` 和 `generate_report` 函数，修复 post-simulation 结果解析与报告生成：
- **原代码** (`runModelQA.pl`): 读 `ModelQA_<ts>/vth` 和 `ModelQA_<ts>/ioff` 等子目录下的 `.md0` 文件，提取 `total` 和 `normalized` 值，存入多层 hash `$hash_sim{$dev}{$corner}{$temp}{$vth_flag}{$cond_idx}{$vol_param}{"total"/"normalized"} = $sim_value`，生成 `MPQA_total.report` 和 `MPQA_normalized.report`。
- **重构后** (`runModelQA_new.pl`): `summary_all_results` 返回**扁平数组**（非 hash）——每个元素按 cfg device 列表的一个唯一 `(device, w, l, nf)` 组织；同一 `ntn w l nf` 来自多条 cfg 行（如 vth + ioff）的数据**flatten 进一个 entry**；每个 entry 含 `pvt` hash：`corner_temp → {vth, ion, ioff, cgg} → {SimCondition, total, normalized}`。`generate_report` 产**宽表**（一行一个 `(device, corner, temp)`，Vth/Ion/Ioff 并排），动态列 `Device, Width(um), Length(um), nf, Corner, Temperature, ...`。
- 用户原话（重构自 reasoning）：把 `summary_all_results` 改成返回 array（不是 hash），按 cfg device 格式 flatten，同一 `ntn w l nf` 数据归一条，pvt 里挂各 PVT 条件下的 vth/ion/ioff SimCondition 和值，最终 report 类似 `MPQA_total_new.report`。

### Turn #1：头部框格式 + SimCondition 列移末尾
- 头部改成带 `*` 边框的框（`* MPQA report *` 居中，框宽按最长行动态算，标签对齐）。
- 列序：值优先，SimCondition 移到末尾。

### Turn #2：Temperature 右侧加 Vdd 列 + pvt_key 三段解析 + vtgm 类型支持
- pvt_key 从 `corner_temp` 改为 `corner_temp_vdd` 三段，sort 按 corner/temp/vdd 数值排序。
- 支持 `vtgm` 类型（`_type_prefix`/`_unit_label`/`change_print_value` 三处 helper 加 vtgm，`%.3f` 格式，单位 V）。

### Turn #3：main 里的配置/命令行参数移到全局变量
- `parse_options`/`getSSD`/`getPVT` 直接设全局标量（`$cfg`/`$model`/`$scale`/`$pvt` 等），`main` 简化，函数调用不再传 `$opt`/`$ssd`/`$pvt`。

## 关键数据格式（逐字读自 rongjiez workspace）

### `.md0`（FineSimPro .measure 输出）
```
* FineSimPro V-2023.12-1  (Compiled on ...)
* Copyright(c) 2003-2024 Synopsys, Inc.
* Generated at Mon Sep 21 16:42:28 2026
* Hostname: hfeg0pgn023, Username: rongjiez
* Input File: /home/.../vth/nrvt_ckt_w1.060u_l0.130u_nf1_c1.sp
* Title: ""
 factor_nrvt_ckt_w1.060u_l0.130u_nf1 =  2.5000e-02
 gmmax_nrvt_ckt_w1.060u_l0.130u_nf1 =  1.7320e-04    at=  6.4000e-01
 vtgm_nrvt_ckt_w1.060u_l0.130u_nf1 =  6.4000e-01
 idgm_nrvt_ckt_w1.060u_l0.130u_nf1 =  3.6511e-05
 vth_slope_nrvt_ckt_w1.060u_l0.130u_nf1 =  4.0420e-01
     temper =  2.5000e+01
     alter# =  1.0000e+00
```
- ion 子目录: `nrvt_ckt_w1.060u_l0.130u_nf1_ion = 7.2406e-04` + `..._ion_normalized = 7.9892e+02` + `temper`/`alter#`
- ioff 子目录: `..._ioff = 5.4998e-10` + `..._ioff_normalized = 6.0685e-04`
- **文件名**: `<dev>_w<W>u_l<L>u_nf<NF>_c<CORNER_IDX>.md0`（corner 1-indexed）
- **multi-temp**: 同一 .md0 多个 alter block，每个 block = (meas value + normalized + temper + alter#)
- **key 模式**: `<dev>_w<W>u_l<L>u_nf<NF>_<measname>` = value（suffix 形式，ion/ioff 一致；vth 子目录用前缀 `vtgm_<dev>` 形式，本 case 合成时统一用 suffix 形式）

### `input_new.cfg`
```
## spice model
model = /apps/imctf/models/cxmt10G3_DDR5/v0.1p4/Model_v0d1p4_pinus_ddr5.sp
## corner
corner = tt/ss/ff
## voltage
vdd = 1.2/1.3
vpp = 2.2/3
## temperature
temperature = -10/25/98
## device shrink factor
shrink = 1
## device port name
port_name = d/g/s/b
## device parameter
device	ntn	 w=1.640u l=0.180u nf=1  vtgm=0.05/sweep(0,vdd,0.01)/0/0  ...  ioff=vdd/0/0/0
device	ptn	 w=1.640u l=0.180u nf=1  ...
```
- device 行: `device <dev> w=<W>u l=<L>u nf=<NF> <meas_type>=<bias_spec> ...`
- bias_spec = `va/vb/vc/vd`（对应 port_name d/g/s/b 的电压），可带 `,extract <电流阈值>` 后缀
- SimCondition = `V<d>/<g>/<s>/<b>=<va>/<vb>/<vc>/<vd>`，`vdd` 用 cfg 名义电压替换

### 报告（MPQA_total.report，长表；重构后 MPQA_total_new.report，宽表）
长表（原）: `Device Width Length nf Corner Temperature SimCondition ParamType ParamName SimValue Unit`（一行一个 meas）
宽表（重构目标）: `Device Width Length nf Corner Temperature Vdd Vtgm(V) Ioff(pA) ... VtgmSimCondition IoffSimCondition`（一行一个 (dev,corner,temp,vdd)，各 meas 并排）

## 合成设计（B-grade L1，纯 stdlib）

**核心机制**（faithful to Turn #0）: parse `.md0`（key=value + multi-alter）→ 按 `(device, w, l, nf, corner, temp)` 聚合各 meas type 的 total/normalized → emit 宽表 JSON 报告。

放弃（非自包含/纯格式）: 头部框格式（Turn #1 纯格式）/ Vdd 列加列（Turn #2 纯格式）/ 全局变量重构（Turn #3 纯软件工程）/ Vth 提取公式（vtgm/vth_slope/idgm/gmmax → 0.389 的 extract 逻辑依赖模型阈值电流，非自包含）/ Perl→Python 移植（语言无关，机制同）。

**SUT**: `modelqa_md0_pvt_aggregate.py <run_dir> <cfg> -o <out_json> [--report <out_txt>]`
- 解析 cfg: model/corners/temps/vdd/port_name/devices(meas types + bias spec → SimCondition)
- 扫 `<run_dir>/<meas_type>/*.md0`，文件名 → (dev,w,l,nf,corner_idx)，内容 → 多 alter block (temp, total, normalized)
- 聚合 → JSON: `{model, corners, temps, vdd, entries:[{device,w_um,l_um,nf,corner,temp,measurements:{<type>:{total,normalized,sim_condition,unit}}}]}`
- 纯 stdlib（os/sys/re/argparse/json/math），禁 subprocess/socket/numpy/pandas/eval/exec

**A（visible）**: prompt + task_brief + run_A/(vtgm|ioff|idsat)/*.md0 + cfg_A。devices ntn/ptn w=1.640u l=0.180u nf=1，corners tt/ss，temps -10/25，vdd 1.2。12 .md0 文件，8 聚合 entry。
**B（hidden, 不进 SUT 沙盒）**: run_B/ + cfg_B。devices ndio/pdio w=0.8u l=0.06u nf=1，corners ff/tt，temps 98/0，vdd 1.3。与 A device 名/几何/corner/temp/vdd/数值全不相交。
**C（嵌入 check.py，反硬编码）**: run_C/ + cfg_C。devices nsw/psw w=2.0u l=0.1u nf=2，corners tt/ff，temps 0/98，vdd 1.25，meas types vtgm/ioff（无 idsat，测 SUT 对不同 meas 集合的泛化）。与 A/B 全不相交。
**negative**: empty.py（空 run_dir）/ print_only.py（只 print 期望串）/ core_removed.py（删聚合核心）/ hardcode_A.py（硬编码 A 数值，B/C 必 FAIL）。

**check.py 16 条件 a-p**: 独立 oracle（o_parse_md0/o_parse_cfg/o_sim_condition 不 import SUT）+ subprocess 真跑 SUT on B/C/empty/negatives + 3-seed sha256。

## 维度正交论证（非 dup）
vs dntvx(1789031505860) = cfg device 行 sweep 展开（输入侧），本 case = .md0 结果聚合（输出侧），机制不同。
vs x6taw(1793337530823)/dfv2z(1793174136126) = ron_linmc#4.md0 单 meas type mismatch 抽取，本 case = vth/ion/ioff 多 meas type PVT 聚合 + wide report，机制不同。
vs OpenWaveFmt-001(7fcir) = ModelQA idvd/idvg 子目录 WaveView 波形格式，本 case = .md0 key=value 文本解析，机制不同。
vs SpiceMeasGroupExpand-001(#539) = .meas deck 生成（输入侧 expand），本 case = .md0 结果聚合（输出侧），机制不同。
vs IddMeasPostProcess-001(#518) = .meas 结果后处理但单 .mt0 单 meas，本 case = 多 .md0 多 meas type 多 alter PVT 聚合，机制不同。
→ 非 dup ✓

## fresh-sid 确认
znoyb 不在 4-shard ledger（2610 sids）也不在 D.jsonl（343 sids）→ truly fresh ✓。rongjiez 在 ledger user（经 l06an #538），但 znoyb session 本身 fresh ✓。
