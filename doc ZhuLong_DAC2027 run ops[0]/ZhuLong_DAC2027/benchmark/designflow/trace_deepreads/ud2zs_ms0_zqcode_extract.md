# 深读 ud2zs — HSPICE .ms0 测量提取脚本 (zqcode_lin)

- session: `1793781925131_ud2zs.messages.json`
- user: clarawu @ hfeg0pkn004 (10.129.2.13)
- mc=81, nmsgs=132, nuser_text=5, model=GLM-5.2
- keywords: hspice:136 netlist:118 schematic:104
- 资产可读性: /proj/m2701/V0_DDR4/workdir/clarawu/... **permission-denied** (e0031982 无读权限) → B-grade synthesized
- domain: schematic_netlist / waveform (HSPICE .ms0 测量文件解析提取)

## 用户意图（5 个 user turn）

- U0 (msg#0): "linux用哪个命令可以查看我能用的任务队列" — 无关开场（admin），非 produce-task
- **U1 (msg#2): "@/proj/.../Ron_global/Ron_global.ms0 帮我写个脚本，功能和@/proj/.../extract_zqcode_lin.py一样"** — **主 produce-task**：写脚本功能同参考 extract_zqcode_lin.py，处理 Ron_global.ms0
- U2 (msg#72): "把写好的脚本复制到/proj/.../extract_zqcode_lin.py" — 续：复制到目标
- U3 (msg#85): "我希望它用相对路径（比如在 Ron_global/ 上级目录运行时用 Ron_global/Ron_global.ms0）" — 续：改相对路径
- **U4 (msg#101): "帮我写一个脚本，提取@/proj/.../sim_MC/Ron_linMC.ms0中rpu_50和rpd_50的标准差，脚本功能类似@/proj/.../extract_ron_mismatch_all.py，写好的脚本复制到.../extract_ron_mismatch_all.py"** — **第二 produce-task**：MC 标准差提取

## 选定任务 = U1（extract_zqcode_lin.py）

更丰富：多行 .ms0 列式格式解析 + 22 列表头跨行累积 + 64 记录跨 7 物理行重组 + closest-to-target 行选取 + 双输出文件。断言点多。

## .ms0 格式（PrimeSim HSPICE 列式多行，msg#34/_dbg2 调试输出）

- 第 1 行: `$DATA1 SOURCE='PrimeSim HSPICE' VERSION='V-2023.12-SP1-1 linux64' PARAM_COUNT=7`
- 第 2 行: `.TITLE '...sim environment settings...'`
- 表头跨 7 物理行，从 `index` 行开始累积 token 直到出现末列 `alter#`
- 22 列: `index zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpu_20 rpu_50 rpu_75 rpd_20 rpd_50 rpd_75 rpu_lin20 rpu_lin50 rpu_lin75 rpd_lin20 rpd_lin50 rpd_lin75 temper alter#`
- 每条数据记录跨 7 物理行（每物理行约 3 token），跨行累积 token 直到凑满 22 个 = 1 条记录
- 457 物理行 → 64 条记录

## 参考脚本行为（agent msg#9 总结 + msg#3/6 读取参考）

- 原 extract_zqcode_lin.py 处理 `.md0`（每行一条记录，`parts=line.split(); len==len(headers)`）
- 功能：找 rpu_50 最接近 **230.0** 的行 = PU；rpd_50 最接近 230.0 的行 = PD
- 输出 pu_zqcode_lin / pd_zqcode_lin：
  - 去掉 `index` 列
  - `alter#` 替换为文件名标签（如 `Ron#0.ms0`）
  - PU 输出列: `zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpu_50 rpu_lin20 rpu_lin50 rpu_lin75 alter#`
  - PD 输出列: `zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpd_50 rpd_lin20 rpd_lin50 rpd_lin75 alter#`
  - 对齐宽度、格式一致

## 真实结果（msg#38/41/50/51）

- 解析 64 records 成功
- **PU**: index=23, zq=010110 (zq5=0,zq4=1,zq3=0,zq2=1,zq1=1,zq0=0), zqdec=22, rpu_50=230.7, rpu_lin20=0.8903, rpu_lin50=1.003, rpu_lin75=1.269
- **PD**: index=16, zq=001111 (zq5=0,zq4=0,zq3=1,zq2=1,zq1=1,zq0=1), zqdec=15, rpd_50=229.7, rpd_lin20=0.9542, rpd_lin50=0.9985, rpd_lin75=1.058
- 脚本 266 行，py_compile OK
- 后续 U2 复制到 sim 目录，U3 改相对路径 `Ron_global/Ron_global.ms0`（在 stimulus_file_global_corner_test/ 目录下运行）

## U4 第二任务（extract_ron_mismatch_all.py，备选/参考）

- Ron_linMC.ms0: 单行一条记录，500 MC 样本，7 列 `index rpu_50 rpd_50 rpu_lin50 rpd_lin50 temper alter#`，无 `std` 汇总行
- 自算样本标准差 (ddof=1, statistics.stdev)，mismatch% = 6*std/230*100
- 输出 RON_mismatch.csv: File,RON_PU_mismatch,RON_PD_mismatch,rpu_50_std,rpd_50_std,rpu_50_mean,rpd_50_mean
- 结果: rpu_50 mean=230.8107 std=1.641218 PU=4.2814%; rpd_50 mean=229.8602 std=1.327652 PD=3.4634%
- 工具 .lis sigma: rpu=1.642 rpd=1.329（确认 ddof=1）

## 合成计划（B-grade synthesized）

- 选 U1 extract_zqcode_lin.py 为主任务
- A: 合成 Ron_global_A.ms0（22 列 6-bit zq, 64 记录, TARGET=230, PU idx=23 rpu_50=230.7, PD idx=16 rpd_50=229.7，复刻真实数值结构）
- 隐藏 B: Ron_global_B.ms0（不同维度反硬编码：7-bit zq (zq6..zq0, 25 列), 48 记录, TARGET=240, PU idx=31 rpu_50=240.3, PD idx=22 rpd_50=239.8, 列名/记录数/目标/最佳值全不同）
- 候选写通用 extract_zqcode_lin.py (--ms0/--target/--out-pu/--out-pd/--label CLI) 解析多行 .ms0 → 找 closest-to-target PU/PD → 输出两文件
- check() 跑 B (subprocess)，断言输出结构 + PU/PD rpu_50/rpd_50/zqdec/zq-bits/label + 反硬编码跨输入 A + 3-seed 确定性
