# 深读笔记 · 4v4nf · FineSim Write→DQ 时序测量 perl 脚本

- session: `1791600745476_4v4nf` (wenwenl @ hfeg0plg74, mc=122, 295 msgs, 1.07MB, mtime 2026-10-10 13:21)
- 注意：同 suffix 的 `1793184099494_4v4nf`(Oct 28) 已被前轮 ledger+parked（"session file GC'd on plg74, unreachable"）；本 `1791600745476_4v4nf`(Oct 10 原始会话) 仍在盘上可达，前轮误登晚时间戳版本而放弃。本轮经 11-05 重扫令 strict 过滤（spice≥10 且 ratio≥0.35，按 `<count> <toolname>` 对解析）→ 6 un-ledgered 命中，本条为最高 mc 且为 produce-task → claim+mark case。

## 用户轮（逐字，仅 2 条 text 轮，余 293 条为 assistant 工具链）
- **U#0 (msg#0, 1791600745895)**：「xieyige perl jiaoben yonglai duqu finesim fangzhen de jili yiji fangzhen zhihou de .fsdb wenjian; cong jili wenjian zhong huode write mingling, cong.fsdb wenjian huode dq boxing, ranhou celiang write mingling dao dq diyigexiajiangyan de jiange he write mingling dao dq diyigeshangshengyande jiange」（拼音逐字，按红线 #2 不脱敏）。→ 即「写一个 perl 脚本读取 FineSim 仿真记录与 .fsdb 波形；从记录获 write 命令、从 .fsdb 获 DQ 波形，测 write 命令到 DQ 第一个下降沿/上升沿的间隔」。**提需求未给根因/修复 → A 合规 ✓**（但本 case 因 .fsdb→.vec 预导出重构，落 B-synthesized 档）。
- **U#1 (msg#294, 1791609605853)**：给出记录文件路径 `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/log/stimulus_wenwenl/odt_sti_allspeed_20260917/ODT002_PerBank_WrNTWr_Offset_SC0_WPre_4s2t_WPst_2p5_RPre_2s2t_RPst_2p5_tCH_50_2b16g_BL0_11600_FF_WRNOPAD.X2P3_11600/stimulus.list`（在会话末尾才给路径，assistant 此前已自主构建通用脚本）。

## assistant 工具链（293 msgs）
- msg#1: 探针 — `which perl/fsdbreport/fsdb2vcd`、find FSDB.pm、find .fsdb/.pl/.tcl（确认环境无 fsdbreport/fsdb2vcd/FSDB.pm）。
- msg#12: find `/apps` 下 `wv`/`fsdbreport`/`FineSim`（Synopsys wv 在 /apps/synopsys/SRB/wv/T-2022.06-SP1/bin/wv）。
- msg#74 起：用 `editor` 工具（共 91 次）增量构建 `/home/wenwenl/work/measure_wr_to_dq.pl`，逐步：默认配置(WV_PATH) → GetOptions → 解析 stimulus(.v/.list) → wv 导出 CK_t/CK_c/CS/CA/DQ .vec → read_vec_file → 在 CK_t 上升沿采样 CS+CA 解码 Write 命令 → 对每个 Write 在 DQ 找第一下降沿/上升沿算间隔 → print_summary(min/max/avg)。
- msg#88: `rm -f measure_wr_to_dq.pl`（清理重写）。
- msg#289-293: 语法校验 + 整理 `measure_wr_to_dq_final.pl`，msg#293 给出最终总结（6 步：读激励/读 FSDB/检测 CK 上升沿/解码 Write/测间隔/出报告）。
- **金标准** = `/home/wenwenl/work/measure_wr_to_dq_final.pl`（perl，用 Synopsys wv 从 .fsdb 导出数字 .vec，再解析测量）→ **已被 GC 清理**（work/ 下无 measure_wr_to_dq*.pl，前轮晚时间戳版本亦 GC'd）。

## case 合成（B-synthesized L1）
- 因金标准 .pl 已 GC 且依赖 Synopsys wv+.fsdb（L2，判分器难独立复跑），按 trace 文档化算法离线 L1 复刻：把 .fsdb 的 DQ 波形预导出为数字 .vec 文本（`<time_ns> <0/1>` 跳变），仿真记录整理为 stimulus list（`WRITE <time_ns> <bank> <addr>`）。
- reference `wr_dq_meas_ref.pl`：解析 stimulus list 的 WRITE 时刻 → 解析 DQ .vec 提取上升沿(0→1)/下降沿(1→0) → 对每个 Write 时刻 w 找 w 后第一上升沿/下降沿，间隔=边沿−w → 输出 report.txt（write_count / write[i] time rising_interval falling_interval / summary rising|falling min max avg）。已在 .75 自验：A(3 writes) 与 B(4 writes) 报告值与手算一致。
- check.py 13 断言(a-m)：zip 唯一 .pl / perl -c / B 运行 exit0+report / B write_count=4 / B W0 rising1.5 falling2.0 / B W1 rising1.2 / B W2 falling1.6 / B summary rising min1.0 max1.5 / B summary falling avg1.8 / B W3 rising1.4 / 交叉输入守卫 B2 exit0+count3 / B2 W0 rising1.8(≠B 反 only_print_B)。
- negative_selftest：ref PASS + 6 fakes（naive_empty/hardcoded_a/no_measure/empty_shell/only_print_B/ref_core_deleted）全 FAIL，NEG_RC=0。§4.9 三假（empty_shell→b / only_print_B→m / ref_core_deleted→e）全 FAIL。
- jsonl B 225→226，k_rationale=k_check=13≥8 GATE PASS，test 字段与盘上 check.py 字节同步。
