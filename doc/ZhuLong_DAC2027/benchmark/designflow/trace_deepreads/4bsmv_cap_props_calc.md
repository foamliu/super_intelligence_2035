# 深读笔记 · 1793702295738_4bsmv · owench@hfeg0plg57 · mc=14 · analog_context

## 任务原文（用户轮，逐字）
1. "/home/owench/G5vsV1/test_yaq/Capacitance 分析一下这个目录"
2. "这个工作目录都能计算得到什么数据"
3. "Ceff Cch Cgd0这些性质怎么做？"
4. "结合/home/owench/G5vsV1/test_yaq/NewDCTest 能计算 Vtsat-Idsat, Vtsat-Idoff, Idsat-Idoff, Vtsat-Ceff, Vtsat-Cch, Vtsat-Cgd0吗？"
5. **"新建一个Capacitance2文件夹 然后根据/home/owench/G5vsV1/test_yaq/Capacitance计算一下相关性质 能在已有功能的基础上计算Ceff Cch Cgd0这三个性质吗？"** ← produce-task 轮
6. "/home/owench/G5vsV1/test_yaq/Capacitance中的计算逻辑是怎么样的？"
7. "这里$devicevt这个变量在哪里定义的？"

## 会话结构
76 msgs, 2 turns, 单一 produce-task（msg 5），其余为 Q&A 探索。assistant 最终创建 Capacitance2/ 目录含 README.md + compute_properties.py(5318B) + properties_report.csv(145行)。

## 真实资产（可达 via ssh 10.129.35.77）
Capacitance/ 目录：
- ntn_V1 (1297行, NMOS Cgg), ntn_G4BCIP (1297行, NMOS), ptn_V1 (973行, PMOS), ptn_G4BCIP (973行, PMOS)
- 数据格式：`Corner devicevt temp w l freq Vg Cg Cd Cb`
- corners: ss/tt/ff；devicevt: ntn_lvio/ntn_lv/ntn/ntn_m (NMOS), ptn_lvio/ptn_lv/ptn (PMOS)
- temps: -40..130 step 10；W/L: 0.21u/0.045u (NMOS), 0.63u/0.045u (PMOS)
- Vg sweep: -0.82..0.82 (NMOS), -0.82..0.82 (PMOS)
- compute_props.py (已有，积累区法提取 Cgd0/Cox/Cch/EOT/Ceff)
- analyze_summary.py, derive_demo.py (分析脚本)
- extract_data, run (csh 仿真脚本), ncggfix.sp (SPICE deck, 权限拒)

## 金标准（Capacitance2/compute_properties.py）
- 积累区法：NMOS 取 Vg 最负（积累区），PMOS 取 Vg 最正
- Cgd0 = Cgs0 = Cd(acc) / W  [F/m]
- Cch = Cg(acc) − 2·Cd(acc)  [F]（本征沟道电容 = Cox·W·L）
- Cox = Cch / (W·L)  [F/m²]
- EOT = ε0·εox / Cox  [m]（ε0=8.854e-12, εox=3.9）
- Ceff = (1/ΔVg)·∫Cg dVg（梯形积分，全 Vg 范围）
- 输出 CSV：file,dtype,corner,vt,temp,w,l,vg_acc,cgd0_fFperum,cch_fF,cox_fFperum2,eot_nm,ceff_fF

## 合成设计（CapPropsCalc-001, B-grade synthesized L2, k=13）
真实 ntn/ptn 数据可达但为 136KB/102KB 大文件 → 合成小数据集（A/B/C 不相交）：
- **A（可见）**：ntn_V1_A (NMOS, 3 corners × 1 vt × 18 temps × 13 vg = 702行) + ptn_V1_A (PMOS, 702行)
  - W/L: 0.21u/0.045u (NMOS), 0.63u/0.045u (PMOS)
  - Cgd0=0.259 fF/um, Cox=13.35 fF/um² (NMOS); Cgd0=0.348, Cox=13.25 (PMOS)
- **B（隐藏，check.py 用）**：ntn_V2_B + ptn_V2_B (3 corners × 2 vts × 8 temps × 13 vg = 624行 each)
  - W/L: 0.30u/0.05u (NMOS), 0.50u/0.05u (PMOS); Vg: -0.90..0.90
  - Cgd0=0.285, Cox=14.20 (NMOS); Cgd0=0.372, Cox=14.10 (PMOS); 含 2 vts (ntn_lv, ntn_m)
- **C（反硬编码，嵌入 check.py）**：ntn_V3_C + ptn_V3_C (1 corner × 1 vt × 2 temps × 13 vg = 26行 each)
  - W/L: 0.15u/0.04u (NMOS), 0.80u/0.04u (PMOS); Vg: -0.75..0.75
- A/B/C 文件名(ntn_V1_A vs ntn_V2_B vs ntn_V3_C) + W/L + Vg 范围 + corners/vts 完全不相交

## SUT 契约
- 交付：outputs/submit.zip，含 compute_cap_props.py
- 用法：python compute_cap_props.py <data_dir> --out <csv_path>
- 纯 stdlib，禁 numpy/pandas/scipy/subprocess/eval/exec/socket/urllib/requests/calibre/pyaether/aether + 禁 B 字面量
- 读取 data_dir 下 ntn_*/ptn_* 文件，按 (file,corner,vt,temp,w,l) 枚举，输出 13 列 CSV

## check.py 13 条件 a-m
独立 oracle（regex 解析 + dict-keyed 查找，与 ref list-filter 结构不同）：
a zip结构+无禁用token/eval/exec/B字面量 / b py_compile / c B退出0+CSV头+行数 / d Cgd0逐行(1e-9 rel) / e Cch逐行(1e-15 abs) / f Cox逐行(1e-3 rel) / g EOT逐行(1e-9 rel) / h **Ceff逐行梯形积分(1e-12 abs) 核心条件** / i 积累区Vg选择(NMOS=min,PMOS=max) / j 反硬编码C数据集结果匹配 / k 3-seed sha256 / l CSV列顺序精确 / m 行数精确

## 自验
ref SUT PASS 13/13 + 3 negative(empty_shell/print_only/hardcode_a)全 FAIL + §4.9 三假(empty_zip/wrong_name/non_zip)全 REJECTED + 3-seed sha256 一致

## 维度正交
既有 D analog_context cap case：
- SpfMosCapRatio-001(#513 SPF net-cap/MOS-gate-cap ratio + cox.csv Cggi 查表)
- SpfCapResAnomaly-001(#509 SPF *|NET cap + R<k>电阻段求和 + outlier)
- PexNodeCapExtract-001(#492 PEX node 对地+耦合 cap 提取)
本 case = Cgg 仿真数据 + 积累区法提取 Cgd0/Cch/Cox/EOT/Ceff（MOS cap model 参数提取），机制/产物全不同非重复
