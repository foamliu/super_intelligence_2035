# deepread: 1793947529316_ie8du (declanzh @ hfeg0plg97) — Mt0FolderAggStat-001

## trace 概况
- session: `1793947529316_ie8du.messages.json`，382 msgs，1.06 MB，mtime 2026-11-06 08:18（started 06:45 Z）
- user: declanzh；host: hfeg0plg97；summary.tsv match_count=172；tools 以 394 hspice 占绝对主导（纯 spice_sim）
- 数据源快照：`/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv`
- 候选来源：本轮 532 un-ledgered spice mc≥30 池（归一化 ledger diff 发现，纠正前轮"池尽"误判）→ 按 spice 工具计数排序 → ie8du 为 spice-dominant 第 1（394 hspice, ratio=1.00）

## 用户轮（前 6 轮，逐字）
- U#1/U#2 (msg[0]/[1]): 仅贴路径 `/rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103`（无指令，作 context）
- **U#3 (msg[2])**: `core1103 路径 + 帮我把这个文件夹下后缀为.mt0的文件数据汇总到一个文档，并给出每个参数的最大/最小值` ← 提需求，未给根因/修复 → A-合规
- **U#4 (msg[24])**: `按绝对值/换算成mA为单位` ← 表达目标 → A-合规
- **U#5 (msg[66])**: `再优化一下这个输出表格， ieff是电流效率，再除以100以百分比展示，对应文件这一栏只保留#数字就可以` ← 表达目标 → A-合规
- **U#6 (msg[122])**: `在此基础上，数据只保留小数点后2位，单位统一放到最左侧，去掉温度这一栏` ← 表达目标 → A-合规
- U#7 (msg[210]) 起进入新子任务（a23 delay_fall/rise、a7 vth 分组），与本 case 无关

## 金标准（用户实际接受的产物）
- 最终脚本在 msg[203]（U#6 细化后、U#7 新子任务前的最后一版 core1103 脚本，header: "mA单位 + 绝对值 + ieff% + 短文件名 + 2位小数 + 无温度列"）
- 解析：每个 .mt0 一行 5 列 `i_vfsbln / i_vwlp_fsbln / ieff. / temper / alter#`（单位 A / °C），跳过 `$`/`.`/`i_vfsbln` 开头行，取首个 5-float 行
- 输出 `core1103_mt0_summary.txt` 三节：
  1. 全局统计（基于绝对值 |min|/|max|；电流 mA=A×1000，效率 %=A×100；含对应文件 #alter 与原始带符号 A）
  2. 按温度(temper)分组（|min|/|max|/均值 + 原始带符号 A）
  3. 全部数据明细（alter, iv(mA), |iv|, iw(mA), |iw|, ie(%), |ie|, 文件）
- 数值 2 位小数；文件列 = `#alter` 编号；明细表无温度列
- 真实数据：77 个 .mt0，i_vfsbln 7.7241e-03~1.5693e-02，i_vwlp_fsbln -5.0686e-02~-2.5280e-02，ieff 3.0186e-01~3.1187e-01，temps -40/85/130

## case 合成
- **EDA-Eval-DesignFlow-Mt0FolderAggStat-001**（spice_sim / faithful / L1 / k=17）
- prompt = U#3+U#4+U#5+U#6 逐字；task_brief 只写交付接口（argv[1]=数据目录，输出 core1103_mt0_summary.txt）
- 资产 A：`core1103/` 24 个合成 .mt0（真实文件已被集群清理，按 trace 文档化格式与量级合成，temps -40/85/130）
- 隐藏 B1：`core1103B/` 18 个 .mt0（temps -40/25/85/125，量级不同）；B2：`core1103B2/` 12 个（反硬编码，量级再不同）
- reference: `mt0_summary_ref.py`（msg[203] 泛化为 argv[1]）
- check.py：17 条独立断言（b..r）——zip/可运行/三节/4 个 |min|+|max| 真值(mA 与 ieff%)/文件数/文件标签 #alter/温度档全覆盖/明细节行数/反硬编码 B2 真值且≠B1。真跑候选（subprocess 在 B1/B2 上执行）。
- 自验：ref PASS 17/17 + 3neg(naive_empty/hardcoded_a/no_compute)全 FAIL + §4.9 三假(empty shell/only-print/ref core-deleted strict)全 FAIL
- sha/断言门：k_rationale=k_check=17≥8 ✓；jsonl B 222→223

## 备注
- 真实 .mt0 已被集群清理（/rundata 为仿真临时区），故资产为合成（按 trace 文档化格式 + 真实量级区间），track 仍标 faithful（任务说明逐字 + 金标准=trace 真实接受脚本），与既有 Mt0PvrefAbsGroupStat-001 等做法一致
- ie8du 同 session 另有 a23 delay / a7 vth 子任务，可作后续 case 备选（不同 produce-task）
