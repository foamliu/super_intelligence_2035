# trace_deepread: 1792031875998_68gc9 — FineSim si.out 内存爆炸根因诊断

**session**: 1792031875998_68gc9  **user**: kli  **host**: hfhds201 (10.129.32.75)
**mc**: 40  **domain**: spice_sim  **trace**: 213 msgs / 111 user-turns (8 real) / 1.9 MB
**subdir**: /home/kli/.cline/data/sessions/1792031875998_68gc9/1792031875998_68gc9.messages.json

## 用户真实意图 (8 real user turns)
1. U0: 对比两个 si.out 判断仿真时间变长原因 + memory 为什么变大
2. U17: 能否通过读 netlist 找到多的 signal / 多出来的 .ic 节点
3. U42: 对比另一对 si.out 查找前者 memory 巨大导致仿真退出
4. U62: 两个仿真网表完全相同, 查找具体 memory 爆炸原因
5. U73: 继续
6. U79: "Total memory usage peak=38698.2 MB" 与 "Peak memory usage for simulation Peak Virtual Memory=1383493.4 MB" 区别 + 为什么 Peak 这么大
7. U80: 继续
8. U89: 对比 si.out vs si.out_bk (更新了 nodeset), memory 有 improve 吗

## 助手工具链
list_allowed_files / read_files 读 si.out → grep ended/memory/peak → 读 netlist.presim/netlist.log/netlistFooter → editor 写 Python 脚本 (analyze_netlist.py / analyze_netlist2.py) count .nodeset/.IC/.probe 模式 → run_approved_command 跑脚本 → 读 finesim.elog/spf.list

## 关键发现 (来自助手分析)
### 1. 仿真时间 + 内存增幅 (20261013 ref vs 20261014 problem, TT/0.94V/25C)
- Elapsed: 19174s → 27280s (+42%)
- Peak Memory: 32892 MB → 62485 MB (+90%)
- ref host hfeg0pjn035 (zjqiao) vs problem host hfeg0pjn029 (dandans)

### 2. memory 爆炸根因 (.nodeset + finesim_ignore_floating_node)
- `.nodeset V(XIctop.XI_Array8G_*.XI_Array1G_*.XI_m512Meg_*.s*<*>)=0v` + `.nodeset V(XIatop_*.XI_Ary8G_A_*.XI_Ary1G_G*.XI_m512Meg_B*.s*<*>)=0v`
- 展开匹配 25952256 节点 (12976128 + 12976128)
- `finesim_ignore_floating_node="*"` → 所有浮空节点加 gdcpath(1e-16 mho) 保留在矩阵
- `.probe v(*)` 命中 27942233 节点
- probed signals: ref 1953240 → problem 8968057

### 3. Total memory vs Peak memory for simulation
- `Total memory usage: peak=38698.2 MB` = PrimeSim 内部 malloc/new 堆 (电路 DB/矩阵/模型缓存/状态向量)
- `Peak memory usage for simulation: Peak Virtual Memory=1383493.4 MB, Peak Resident=1382393.2 MB` = OS VmPeak/VmHWM (含 mmap FSDB 波形/临时文件/共享库/线程栈)
- 差 35 倍: Measure 后处理 mmap 整个 FSDB 波形 (897万 probed x 51万 timepoints) 全扫描 → resident ~= virtual
- subckt_pt num_part=3726599 num_net=3636983, time points=510961, measure=322 (meas_crc_alert.sp)

### 4. nodeset 更新改善 (si.out_bk SS OOM vs si.out FF 成功)
- 删 `.nodeset` (25952256 → 0) + 删 `finesim_ignore_floating_node="*"`
- probed signals 27.9M → 1.95M (-93%)
- OOM → 仿真成功

## 合成决策
- form: debug-Q&A → 产出生成式根因诊断报告 JSON (siout_memory_diagnosis_report.json, 12 顶层键)
- A 档 trace-faithful: TT/0.94V/25C, .nodeset + finesim_ignore_floating_node 机制
- hidden B cross-input: SS/0.94V/-40C, .IC 通配符展开 (18472931) + .probe v(*) (22403817) → 7240183 probed → OOM, peak virtual 942188.6 MB
- check.py 25 断言 (a-y): zip/compile/B-doc/真跑/确定性/12 键/corner cross-input/peak virtual cross-input/expansion_matches cross-input/expansion_kind cross-input/root_cause cross-input/A-leak guard(14 token)/memory_metrics 区分 malloc vs VmPeak-mmap/recommendations/conclusion/confidence/evidence/sim_time cross-input/possible_causes cross-input
- 4 negatives: empty-shell→h / print-only→h / hardcode-A→l cross-input corner / deleted-core→k missing keys
- ref 通用解: A/B 双跑确认 (A=TT/nodeset/25952256/1.38e6, B=SS/ic/18472931/9.42e5)
