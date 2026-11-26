# z4swx deepread · spice_sim · 2026-11-10 12:0x

## trace source
- sid: 1794206448451_z4swx · user: xuelianf · host: hfeg0pkn002 · mc=214
- session_file: /home/xuelianf/.cline/data/sessions/1794206448451_z4swx/1794206448451_z4swx.messages.json (873KB / 242 msgs)
- snapshot summary.tsv: ssh_eda_search_20261109_224902/summary.tsv row
- keywords: cmos:368;netlist:40;synopsys:34;mosfet:26;pex:18;lib.defs:2;hspice:2 (spice_kw=3, keyword pool)

## user turns (10 user turns, 7 user requirement turns)
- U#0: "请阅读一下下面这个文件夹 /rundata/sim_cloud/CRG/cyzhu/ACA/DRGQA_5SEC_SM/REVC/19_test_msak_new_model/normal_CMOS0831_ArySPF_POR_byBL_sweep_SenCC_cap/C_SenCC_0aF/group1_BL0_00101010/RESULT/" → consultation (read folder)
- **U#1: CLEAN produce-task** ✓ "请写一个程序，取出同时带有关键词 D1 和关键词 bisec_mt0文件内第4行第1列的数据记为vtarget_D1，按照公式 (0.93*1000-vtarget_D0*1000)*0.156-36.43 来计算的到 SM1；取出同时带有关键词 D0 和关键词 bisec_mt0文件内第4行第1列的数据记为vtarget_D0，按照公式 vtarget_D0*1000*0.156-37.69 来计算的到 SM0；输出文件的格式如下：directory,SM1,SM0 ./C_SenCC_0aF/group1_BL0_00101010,..." — 提需求/表达目标，未给根因或修复方案 ✓
- U#2: "不是的，就写在这个路径下面就好了" → 路径澄清 (refinement)
- U#3: "请用 python 或者 bash 在该路径下写这个程序" → 工具选择 (refinement)
- U#4: "计算的不太对" → 反馈 (bug report)
- U#5: "SM1 (0.93×1000 − vtarget_D1×1000) × 0.156 − 36.43 / SM0 vtarget_D0 × 1000 × 0.156 − 37.69" → 公式纠正 (refinement: SM1 用 vt1 不是 vt0)
- U#6: "请增加一个设置，不在terminal 中显示，只显示在输出文件csv内，另外增加两列输出，原来的第一列保持不变，第二列变为 vtarget_D1,第三列为 vtarget_D0,第四列为SM1,第五列为 SM0" → refinement (5 列, 不打印终端)
- U#7: "再增加一个设置，输出结果只保留到小数点后三位" → refinement (3 位小数)
- U#8: "请将base_Dir 进行优化，直接搜索当前路径下的，不需要制定路径" → refinement (cwd 自动)
- U#9: "请参考这个路径下面的文件result_summary.sh来修改搜索的文件夹路径，采用相同的在前面自定义目录名的方式" → refinement (DIRS 数组)

## 选轮判定
- A-档选轮规则：只取「提出需求/表达目标」的用户轮；U#1 是 CLEAN produce-task。
- 但金标准 = 用户最终接受的 calc_sm.py 融合了 U#5-9 的细化（5列/3位小数/cwd/公式纠正）。U#1 单独的 spec（3列 directory,SM1,SM0）与金标准（5列）不一致 → A-档 prompt 仅给 U#1 会导致 spec 不完整。
- 裁定：做 **B-档 (synthesized)** — task_brief 融合全部细化后的完整 spec（5列 CSV、3位小数、cwd 自动、缺D1跳过），prompt 保留 U#1 原话+背景说明。

## gold standard
- assistant 写的 /home/xuelianf/calc_sm.py（已 scp 提取，2156B）：
  - extract_vtarget(bisec_file): lines[3].strip().split()[0] → float (第4行第1列)
  - 遍历 cwd 下 C_SenCC* → group* → RESULT/Input_D0.bisec_mt0 + Input_D1.bisec_mt0
  - SM1 = (0.93*1000 - vt1*1000)*0.156 - 36.43；SM0 = vt0*1000*0.156 - 37.69
  - 输出 CSV: directory,vtarget_D1,vtarget_D0,SM1,SM0（3位小数），写文件不打印终端
  - 缺 D0 或 D1 的 group 跳过
- 真实 /rundata sim 树在 pkn002 上 e0031982 可读（已 scp sample），但为 B-synthesized 造可控资产：复刻 bisec_mt0 格式（4行 $DATA1/.TITLE/header/data，line4 col1=vtarget 科学计数法），用已知 vtarget 值造 A/B1/B2 树。

## bisec_mt0 格式（sample, real）
```
$DATA1 SOURCE='PrimeSim SPICE' VERSION='U-2023.03-SP1' PARAM_COUNT=1
.TITLE '*****************PVT*******************************************'
        vtarget        maxvout         temper         alter#
     3.5254e-01     9.2925e-01    -4.0000e+01     1.0000e+00
```
line4 col1 = vtarget (e.g. 0.35254)

## case 合成
- EDA-Eval-DesignFlow-BisecMt0SmCalc-001 · spice_sim / synthesized / L1 / k=14
- deliverable = calc_sm.py
- 资产 A (sample_tree): 2 C_SenCC, 3 group (可见格式样本)
- 隐藏 B1: 5 valid group + 1 missing-D1 (skip) → 期望 5 行
- 隐藏 B2: 5 valid group, 不同 vtarget 值 (反硬编码)
- check.py 14 断言 a-n，独立重算期望值（非硬编码），subprocess 真跑候选在 B1/B2
- 自验: ref PASS 14/14 + 6neg NEG_OK + §4.9 三假 FAIL-OK + 断言门 k=14≥8 ✓ + test 字段字节同步 ✓
