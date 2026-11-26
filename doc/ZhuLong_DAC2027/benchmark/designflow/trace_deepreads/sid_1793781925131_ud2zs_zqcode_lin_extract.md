# 深读笔记 — sid 1793781925131_ud2zs (clarawu@hfeg0pkn004)
## 主题: zq-code 提取脚本(.ms0 多行格式) · spice_sim A-档 L1

**trace 源**: clarawu@hfeg0pkn004, session 1793781925131_ud2zs.messages.json, 132 msgs, 418KB, spice_c=104 (hspice=104), mc=118

### 用户轮(verbatim)
- USER#0: "linux用哪个命令可以查看我能用的任务队列" (trivial linux 问题, 非 A-档任务)
- **USER#2 (A-档任务, 逐字原文)**: "@/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_DqFinalDrv_Ron_1029/hspiceD/schematic/netlist/stimulus_file_global_corner_test/Ron_global/Ron_global.ms0 帮我写个脚本，功能和@/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_DqFinalDrv_Ron_1029/hspiceD/schematic/netlist/stimulus_file_global_corner/extract_zqcode_lin.py一样"
  - 纯需求轮✓ (给目标+方法, 未给根因/修复)
- USER#3: "把写好的脚本复制到/.../stimulus_file_global_corner_test/extract_zqcode_lin.py" (接受产出的脚本)

### assistant 工具链
1. read_files 读 ref_extract_zqcode_lin.py (单行 .md0 版) + Ron_global.ms0
2. 发现 .ms0 是 PrimeSim HSPICE 列式多行格式: 表头跨 7 行, 每条数据记录也跨 7 物理行(每行 3 列 token), 共 22 列
3. editor 写 extract_zqcode_lin_ms0.py (因 policy writableRoot 限制写到 /home/clarawu/)
4. run_approved_command 跑 → "No valid data" (首次 parse 按 .md0 单行逻辑失败)
5. 写 _dbg_ms0.py 调试 → 发现表头也跨行, 只有 4 列被识别
6. 修复 parse_file: 累积跨行 header token 直到 'alter#', 再累积数据 token 成 22 列记录
7. 重跑 → "parsed 64 records" ✓, 输出 pu_zqcode_lin + pd_zqcode_lin
8. _dbg2_ms0.py 交叉核对: PU=index23 zq=010110 zqdec=22 rpu_50=230.7; PD=index16 zq=001111 zqdec=15 rpd_50=229.7 ✓
9. cleanup_tmp.sh 清理调试文件

### .ms0 格式逆向 (PrimeSim HSPICE V-2023.12-SP1-1)
- line 0: `$DATA1 SOURCE='PrimeSim HSPICE' VERSION='V-2023.12-SP1-1 linux64' PARAM_COUNT=7`
- line 1: `.TITLE '...'`
- line 2-8: 表头 7 行 (4+3+3+3+3+3+3 = 22 tokens)
  - index zq5 zq4 zq3 | zq2 zq1 zq0 | zqdec rpu_20 rpu_50 | rpu_75 rpd_20 rpd_50 | rpd_75 rpu_lin20 rpu_lin50 | rpu_lin75 rpd_lin20 rpd_lin50 | rpd_lin75 temper alter#
- line 9+: 数据记录, 每条 7 物理行 (4+3+3+3+3+3+3 = 22 values)
- 22 列: index, zq5..zq0, zqdec, rpu_20, rpu_50, rpu_75, rpd_20, rpd_50, rpd_75, rpu_lin20, rpu_lin50, rpu_lin75, rpd_lin20, rpd_lin50, rpd_lin75, temper, alter#
- 真 trace: 457 行 → 64 条记录, temper=-40, alter#=1

### 脚本功能 (extract_zqcode_lin_ms0.py)
1. parse_file: 累积跨行 header 直到 'alter#', 累积数据 token 成 22 列记录
2. find_best_row: PU = rpu_50 最接近 230.0; PD = rpd_50 最接近 230.0
3. write_output: 输出 pu_zqcode_lin + pd_zqcode_lin (tab-separated, zq 位重命名 zqpu/zqpd, rpu_lin/rpd_lin, alter#=文件名标签)
4. 输出格式: 表头行 + 1 数据行, int 列宽 6, float 列宽 12 (3 位小数)

### 金标准 (真 trace 产物)
- PU: zq=010110, zqdec=22, rpu_50=230.700, rpu_lin20=0.890, rpu_lin50=1.003, rpu_lin75=1.269, alter=Ron#0.ms0
- PD: zq=001111, zqdec=15, rpd_50=229.700, rpd_lin20=0.954, rpd_lin50=0.999, rpd_lin75=1.058, alter=Ron#0.ms0

### case 合成 (EDA-Eval-DesignFlow-ZqCodeLinExtract-001, spice_sim A-faithful L1)
- task = USER#2 verbatim
- 交付 = 通用 python 脚本, 接受 <ms0路径> [输出目录], 输出 pu_zqcode_lin + pd_zqcode_lin
- A = 合成 .ms0 (32 records, zqdec 0-31, temper=-40, alter=1)
- hidden B = 合成 .ms0 (24 records, zqdec 0-23, temper=25, alter=2, 不同 rpu/rpd 分布)
- reference = extract_zqcode_lin_ms0_ref.py + check.py k=14 断言 a-n
- negative = 5 stub (naive_empty/print_only/hardcode_B/wrong_target/single_line_parse)
- 自验: REF PASS 14/14 + 5 neg ALL FAIL + §4.9 (a)(b)(c) ALL FAIL
- 断言闸门: k_rationale=14 == k_check=14 ≥ 8 ✓

### 候选重建 (本轮 fresh rescan + daily log diff)
- fresh rescan 03:00→03:35: hfhds201 0 new + pkn001/002/004/005 reachable but 0 new (deep night)
- 11-07 00:01 daily log diff vs ledger B: 85 strict spice-dom (mc≥30,sp≥10,ratio≥.35), 61 in-ledger, **24 NOT-in-ledger**
- scout top candidates: 4fq1p(consulting)/op0br(dup McRonMismatch)/mntzu(rootcause)/gsmj2(consulting)/2q4mg(consulting)/ud2zs(CLEAN A-档✓)
- park 7 rejects (g7b4c/7qatl/iq1bu=lvyy rootcause dup, 4fq1p/mntzu/gsmj2/2q4mg=consulting/rootcause)
- 选 ud2zs (clarawu, mc=118, sp=104, hspice=104) claim + deepread + 合成 + 交付
