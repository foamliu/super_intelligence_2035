# deepread: 1794537233423_6c5ev — tongfanl @ hfhds206 — bjobs SUB_CWD 重复投递检测

**session**: 1794537233423_6c5ev.messages.json
**user/host**: tongfanl @ hfhds206 (10.129.32.80)
**mc**: 12, keywords: netlist:364 (finesim 矩阵仿真 netlist dump 命中)
**size**: 453KB / 28 real user turns / OpenCode-style schema (messages[].content list, user_input mode=act)
**domain**: eda_other (集群作业管理 / 仿真流编排)

## 真实对话流（real user turns）

- **U#0 (核心 produce-task)**: 给一个 bjobs dump 文件路径
  `/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_SpfBA_20261106PM_DDR6TOP_PowerFill_V0d9_Rev02_t01_COMPRESS_Aging_THB_1008hr_step2/222`
  原话「这个文件中有没有目录路径完全一致的 job」。agent 初始试 list_allowed_files → 报 "Path is not a directory"（该路径是文件不是目录）；试 run_commands → 被 Agent Policy 拦（"Raw shell tool run_commands is disabled; use run_approved_command"）；试 shell-runner → "requires filePath"。最后用 editor 写 **check_dup_jobs.py** + python-runner 执行。
- **U#4-5**: agent editor 创建 `/home/tongfanl/check_dup_jobs.py`，python-runner 跑出结果：107 行 / 1 表头 / 106 作业记录 / **6 组 EXACT DUP PATH**（前 3 组各 2 个 RUN，后 3 组各 1 RUN + 1 PEND）。
- **U#6 (produce-task #2)**: 给三条 RDBI/LTOL/HTOL 路径「帮我检查下，三个文件夹下的内容是不是都指向 /rundata/.../Aging_HLTOL_RDBI_1008hr_step1」→ agent 写 **check_symlinks.py**（检查 source folder 的 symlink 是否指向 target folder 内）。
- **U#9-10**: agent 编辑 check_symlinks.py（isdir→exists，加 kind=dir/file/missing），重跑。
- **U#11 (produce-task #3)**: 「帮我看下对应的 42hr 的三个文件夹有没有 link 到 .../Aging_HLTOL_RDBI_42hr_step1」→ 复用 check_symlinks.py 改 TARGET。
- **U#14 (produce-task #4)**: 「..._brs/ 是忽略了 PSD0（si.inp）后跑得，和 ..._step1/ 对应。看下这两个文件夹有无问题」→ agent 写 **compare_rdbi.py / compare_rdbi2/3/4.py / dump_siinp.py**，对比两文件夹，聚焦 finesim_ignore PSD0/PSD1 在 si.inp 中的差异。最终（U#24）发现 brs 把 PSD0↔PSD1 交换了（35 ignore，brs PSD0=2/PSD1=31 vs tgt PSD0=32/PSD1=1）。
- **U#25-26**: 「？」×2（催促/收尾）。

## agent 工具链

editor×N（写 check_dup_jobs.py / check_symlinks.py / compare_rdbi*.py / dump_siinp.py）+ run_approved_command(python-runner)×N。被 Agent Policy writableRoots(仅 /home/tongfanl) 限制，所有产物写 /home/tongfanl/。

## A-faithful 判定

**合格**。用户给的是「文件路径 + 是非问题（有没有目录路径完全一致的 job）」，agent 自行决定写脚本解析 bjobs dump、按 SUB_CWD 精确分组。用户未给：表头检测规则、短行跳过、分组算法、输出格式、trailing-slash/大小写处理。这些是 agent（及 SUT）要自己定的 HOW。

## deliverable 可行性

deliverable = 写 `/home/tongfanl/check_dup_jobs.py`（私有 home）+ 读私有 `/rundata/dscqa_sim/` dump → **.75 SUT 沙盒 INFEASIBLE**（Permission denied 私有路径）→ **B 档合成**：自包含 bjobs dump 文件（A 可见 + B 隐藏），SUT 交 bjobs_dup_cwd_detect.py，纯 stdlib CLI。

## 合成 case

**EDA-Eval-DesignFlow-BjobsDupCwdDetect-001**（eda_other L1-B，新 archetype = bjobs-submission-cwd-duplicate-detector）
- SUT 交 bjobs_dup_cwd_detect.py（纯 stdlib CLI --input/--out/--json）：检测表头(JOBID 开头) + 跳过空行/短行(<6 字段) + SUB_CWD 取最后列拼接 + 按精确字符串分组 + 报告 count>1 组 + JSON 输出。
- A = bjobs_A.txt（1 前导注释 + 表头 + 15 作业 + 1 短行 + 1 空行，3 重复组，1 trailing-slash 近重诱饵）。
- B = hidden/bjobs_B.txt（表头在首行 + 24 作业 + 2 短行 + 2 空行，4 重复组[RDBI 3-job / LTOL 2-job RUN+PEND / THB 2-job / HLTOL_42 2-job]，1 大小写近重诱饵 aging_B vs Aging_B，drcoa_B 前缀/runscript_B*/B 用户，与 A 零名重叠）。
- 核心 trap：⑪大小写诱饵不被合并 ⑧PEND 保留 ⑨短行跳过 ④表头在首行 ⑫跨输入守卫 ⑮3-seed 打乱顺序稳定。
- check.py 16 条件(a-p)独立，subprocess 真跑 B + 解析 JSON。k_rationale=k_check=16 ✓。
- 自验 ref SELFTEST PASS 16/16；5 neg(naive_empty/print_only/hardcoded_a/core_removed/no_header_skip)全 FAIL；§4.9 3fake(empty/garbage/print_string)全 FAIL。

## 区别于已有 case

区别于 XrunLogStatusCheck（xrun 日志行级 fatal/done/noise 分类 + .shm 交叉校验）：本 case 是 bjobs 作业列表按 SUB_CWD 精确去重分组，不涉及日志分类或波形。新 archetype。
