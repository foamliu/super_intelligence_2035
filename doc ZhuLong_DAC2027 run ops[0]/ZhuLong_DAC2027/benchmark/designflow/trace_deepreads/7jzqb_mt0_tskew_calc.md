# trace_deepread: 7jzqb Mt0TskewCalc-001

## trace_source
- user: reedchen
- host: hfeg0plg49 (10.129.8.x, plg 独立子网)
- session: 1792139236507_7jzqb.messages.json (2.67MB, 911 msgs, 466 user turns, spice_cnt=2294)
- domain: spice_sim

## peek 策略修正（DEBT 清偿）
- 上轮（06:1x）peek 因大文件 ssh json.load/grep 超时(90s/50s)未完成
- 本轮修正：scp 候选 session 到 .75 workdir（1.3-2.7MB，scp 3-4s/台）→ 本地 python3 解析 user turns（182ms 完成 5 个文件）→ 无超时
- scp top 5 plg 候选：5tdum(mike plg05 1.57MB) / 7jzqb(reedchen plg49 2.67MB) / f0jns(crystalh plg49 1.70MB) / 1hq6h(rongjiez plg49 1.32MB) / 16izn(e03179 plg15 1.40MB)

## 用户轮分析（<user_input mode="act"> 真实需求轮）

### 7jzqb（选定）
- **U#0 (msg#0)**: "/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ReedChenWork_Dbus_tball_0929_Rev0_schematic_ALPS/sim_vintcore_normal/output/output_SS_9V-40C.mt0.csv 请你用脚本帮我处理一下这个csv文件，这个文件有PP 和 WP 两组数据，每组数据又分为Tr和Tf两份，先将所有数据向1.5ns取余，然后你需要找到Tr和Tf各自的最大值和最小值，然后用公式： Tskew = max(tf_slow,tr_slow) - min(tf_fast,tr_fast)得到PP 和 WP 两组数据的Tskew"
  - **A-faithful ✓**: 提出需求（处理 CSV 计算 Tskew），无根因/无修复方案
- U#45 (msg#45): "你算的不太对，WP和PP 是两种情况，应该得到两种Skew，修改一下你的脚本，另外写清楚你的脚本该怎么用"
  - 纠正轮：PP 和 WP 是两种独立情况，各算各的 Tskew（非 combined cross-group skew）
- U#65 (msg#65): 扩展需求（注释换英文 + 递归批量 + PVT 解析）→ 新任务，不入 prompt
- U#223 (msg#223): 扩展需求（3 倍数据 L1/L2/L3 三级）→ 新任务，不入 prompt

### 其他 4 候选 peek 结果
- **5tdum (mike plg05)**: U#0 pinyin "这个路径下有很多目录，每个目录下有个 si.inp 文件，帮我写个命令，我要删掉 si.inp 中 T_mBistOsc 字符串" → CLEAN A-faithful（简单 sed 任务，spice_sim，留作未来候选）
- **16izn (e03179 plg15)**: U#1 "方案二的仿真路径是/proj/dscqa/...，帮我查看下哪些cell可以直接替换" → CLEAN A-faithful（VAM cell 替换，characterization，留作未来候选）
- **f0jns (crystalh plg49)**: U#0 "如何选择stdcell的vth" / U#1 "linkecc的mimic 是匹配哪里的电路" → 知识问答 vague，需更深 peek 判断
- **1hq6h (rongjiez plg49)**: U#0 "...这个脚本执行后报错：[LSF-Control]: smallslot is dedicated..." → 用户已指出根因（LSF 报错）→ A-档 reject

## assistant 工具链（7jzqb U#0→U#45 闭环）
1. read_files + list_allowed_files → 读 mt0.csv 头部
2. run_approved_command (python-runner) → 分析列结构（24578 cols, epp000-epp127/ewp000-ewp127, 48 Tr + 48 Tf per prefix, 1 data row）
3. editor → 写 analyze_mt0.py → run_approved_command → 分析列名格式
4. editor → 写 tskew_calc.py → run_approved_command → 首版输出（combined Tskew PP=slow/WP=fast=165.5ps）
5. U#45 纠正 → editor 修 tskew_calc.py → run_approved_command → **最终 PP=83ps / WP=296.5ps** ✓

## 金标准算法
- **文件格式**（FineSim .mt0.csv）：
  - Line 1: `$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0`
  - Line 2: `.TITLE '.option PARHIER = LOCAL'`
  - Line 3: 列名行（逗号分隔，右对齐，如 `     epp000_r01,     epp000_r02, ...,     epp000_f01, ...,     ewp000_r01, ...`）
  - Line 4: 数据行（逗号分隔，单位秒，如 `4.1936e-09, 7.1936e-09, ...`）
- **列分类**：`epp<N>_r<M>` = PP Tr(rising), `epp<N>_f<M>` = PP Tf(falling), `ewp<N>_r<M>` = WP Tr, `ewp<N>_f<M>` = WP Tf
- **算法**：
  1. 解析 $DATA1/.TITLE 头 + 列名行 + 数据行
  2. 按前缀(epp/ewp)+后缀(_r/_f)分类列
  3. 全部值 mod 1.5ns (1.5e-9 秒)
  4. 每组(PP/WP): Tskew = max(Tf_max, Tr_max) - min(Tf_min, Tr_min)
  5. 输出 PP Tskew 和 WP Tskew（分开，非 combined）

## 通用化
- ref script: `tskew_calc_ref.py` — 通用 FineSim .mt0.csv 解析器 + Tskew 计算
- A 资产: `output_TT_0.9V25C.mt0.csv` (4PP+4WP × 6Tr/6Tf = 96 cols, PP Tskew=150ps/WP=300ps)
- hidden B: `output_SS_0.92V-40C.mt0.csv` (6PP+6WP × 8Tr/8Tf = 192 cols, PP Tskew=199.8ps/WP=450.1ps)
- check.py 13 断言(a-m): zip 含 1.py / py_compile / CLI args / B exit0+非空 / 键齐全 / PP Tskew 正确 / WP Tskew 正确 / mod 已应用 / PP/WP 分开 / Tr/Tf 分离 / A 泛化 / A/B 不泄漏 / 3x 幂等

## 自验结果
- ref PASS 13/13 ✓
- 4 negative 全 FAIL（distinct: f/k/f/g）✓
- §4.9 三假（empty FAIL d / print-expected FAIL k / naive FAIL f）✓
- 断言闸门 k=13==13≥8 ✓
- jsonl test==disk sha 6900f1ff7a4b ✓
