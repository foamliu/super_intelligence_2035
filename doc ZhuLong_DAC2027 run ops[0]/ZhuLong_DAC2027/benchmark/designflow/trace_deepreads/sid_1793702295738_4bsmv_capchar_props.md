# Deepread — 4bsmv (owench@hfeg0pkn002, mc=14, characterization)

**Session**: 1793702295738_4bsmv.messages.json · 76 msgs · 492KB · 10.129.2.11
**Domain**: characterization (MOS 电容 Cgg) · shard B
**Task turn (A-faithful, msg#58, verbatim)**：「新建一个Capacitance2文件夹 然后根据/home/owench/G5vsV1/test_yaq/Capacitance计算一下相关性质 能在已有功能的基础上计算Ceff Cch Cgd0这三个性质吗？」
（= clean 提出需求轮：给源目录+目标+3 个性质名，无根因/无方案）

## 用户轮序列
- #0「分析一下这个目录 Capacitance」(vague)
- #14「这个工作目录都能计算得到什么数据」
- #34「Ceff Cch Cgd0这些性质怎么做？」
- #44「结合 NewDCTest 能计算 Vtsat-Idsat, Vtsat-Idoff, Idsat-Idoff, Vtsat-Ceff, Vtsat-Cch, Vtsat-Cgd0吗？」
- #58 ★clean task: 新建 Capacitance2 + 计算 Ceff/Cch/Cgd0
- #72/#74 follow-up 解释（非任务）

## 工作目录 /home/owench/G5vsV1/test_yaq/
- Capacitance/: 4 份 Cgg 数据 ntn_V1/ntn_G4BCIP/ptn_V1/ptn_G4BCIP (1297/1297/973/973 行)
  - 格式: `Corner devicevt temp w l freq Vg Cg Cd Cb`
  - ntn: w=0.21u l=0.045u; ptn: w=0.63u l=0.045u
  - corners ss/tt/ff, temps -40..130 (步10), 多 vt, Vg 扫 9 点 [-0.82..0.82]
- ncggfix.sp (HSPICE Cgg 网表模板，权限拒)
- NewDCTest/: DC 参数 (Vtsat/Idsat/Idoff) — 用于 msg#44 关联量(本 case 不用)

## 金标准 (msg#71 接受结果)
assistant 新建 Capacitance2/ 含：
- compute_properties.py (128行): 积累区法
  - Cgd0 = Cd(积累)/W; Cch = Cg(积累)-2*Cd; Cox = Cch/(W*L); EOT = eps0*3.9/Cox; Ceff = 梯形积分(Cg over Vg区间)/区间
  - 积累区: NMOS 取 Vg 最负(max_neg), PMOS 取 Vg 最正(max_pos)
  - DATASETS 4 文件 × dtype × mode × Ceff 区间(NMOS [0,0.82], PMOS [-0.82,0])
- properties_report.csv (144 行, 13 列)
- README.md

## Case 合成 (EDA-Eval-DesignFlow-CapCharProps-001, characterization A-faithful L2)
- 交付: 通用 compute_properties.py <data_dir> <out_csv>
- assets A: 4 份 Cgg 数据(忠实复现真实格式+数值, ss/tt × -40/40, 2 vt × 9 Vg → ~73 行/文件)
- hidden B: 不同 geom(ntn 0.42u/0.06u, ptn 1.26u/0.06u) + corners ff/tt + temps -20/60 + 电容×1.8 → 强制泛化防硬编码
- reference: compute_properties_ref.py + check.py k=14 断言(独立重算 B + 跨输入护栏 A + 积累方向 + dtype 感知)
- self-verify: ref 14/14 PASS, 5 negatives 全 FAIL, §4.9 三假全 FAIL
- jsonl_B line 93, mark --status case
