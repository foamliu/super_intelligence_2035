# Deep-read — r237 / sk6cg / Calibre-Argus DRC Log 拆解报告

- **shard**: C (physical_verify)
- **session**: `1789699671032_sk6cg.messages.json`
- **user / host**: joelchen (NEW user, not in saturation list) / hfeg0plg37 (10.129.32.47)
- **match_count**: 274 (drc:1410;pdk:987;lvs:740;analog:519;calibre:282;cmos:131;aether:46;pex:22)
- **agent**: lead, 146 msgs
- **case_id**: `EDA-Eval-DesignFlow-DrcLogTeardownReport-001` (L2, B-synthesized, 18 条断言)

## 用户真实意图

joelchen 反复执行一套《Calibre/Argus DRC Log 拆解报告》workflow（用户把 skill spec 整段贴 5 次，msg 5/72/94/99/127；msg 56/76/144 是带附件/换文件的 "对这份 log 生成报告" 指令）。给定一份 DRC 运行 log，产出**四模块简化报告**：
1. 各大步骤时间占比 + cumulative 操作类别（WITH WIDTH/EDGE TOPOLOGICAL/SIZE/BOOLEAN/CONNECT）分布
2. CONNECT 建立时间（REAL/NETS/EPINS + cumulative）+ 冗余检查（近空层/冗余路径/DISCONNECT 后重做 + deck 语句行号）
3. 图形计算 Top-N（REAL TIME 排序，含 expr/RuleCheck/HGC/FGC/FEC/log行号 + VHC=F hierarchy 失效判断）
4. deck 优化建议（改前/改后 + 预估节省 + 优先级）

边界：只做时间+规模分析；输入必须真实存在（不存在→报错停止）；每条结论带 log 行号/grep 命令；log 截断/无 TOTAL CPU TIME→注明"无法确认"不编造。

## assistant 工具链

- `skills`(load skill) → `list_allowed_files`(找 log) → `read_files`(定向读片段) → `run_commands`(grep/awk/sed 统计) → `editor`(msg 139 写 calibre_drc2_report.md)
- 全程遵守"禁止整体读大 log"边界，用 grep -n / awk / sed -n 定向提取
- 在 calibre_drc2.log（单标准单元 aoi21CSx1，2 核 REAL=1s，2417 rulechecks）上正确判定**无瓶颈/无冗余/VHC=F>99% 但 HGC=0**（数据量≈0 而非层次失效），唯一非零 cumulative 是 DENSITY(0/2)。交付 calibre_drc2_report.md（5KB，四模块齐全 + 分析方法/复核命令小节）。

## 关键陷阱（skill spec 自带 11 条验收标准 + 10 条已知陷阱）

- ELAPSED TIME 是累计值，不能当单步耗时排序（用 REAL TIME）
- 操作归属 rule 要从操作行**往后**找最近 COMPLETED（向前找会归到上一个 rule）
- VHC=F = 放弃层次压缩=扁平执行（不是"有压缩"）
- CONNECT 冗余要看 deck 语句内容（BY 层 NETS、重复路径、DISCONNECT 后重做），不只看耗时
- cumulative `CPU=a/b` 中 a 是子类、b 是总计
- 退化场景：log 截断/字段异常→注明不编造

## 合成资产设计（为何合成 log）

真实 calibre_drc2.log / rundrc.log 都是单标准单元 1s trivial run（全部 cumulative=0），argusDRC.log_case1/case3 是 Argus 自有格式（无 MODULE COMPLETED/(HIER)/Cumulative 行）。为了能真正检验 11 条验收标准（需要有非零 cumulative、有 CONNECT 冗余、有 VHC=F+HGC>0 的层次失效、有可排序的 Top-N），合成两份有瓶颈的 Calibre DRC-H log：
- **A** (rundrc_A.log, 98 行): 16 核 REAL=12876s, CONNECT 主导(cumulative 2210), 三类冗余全有(近空层 NETS=3 + DISCONNECT M1 后重做 + M1 多路径), VHC=F=0.667, top1=M1_SIZE_002 REAL=2640
- **B** (rundrc_B.log, 85 行): 32 核 REAL=8421s, WITH WIDTH 主导(3120), 无冗余, VHC=F=0.20, top1=NW_WWIDTH_021 REAL=3120 — 与 A 在规模/瓶颈类别/冗余/层次全不同（杀硬编码）
- **B2** (rundrc_B2.log, 80 行): B 截断版（砍掉 EXECUTIVE MODULE COMPLETED 及之后所有 TOTAL 行）→ 验退化处理（degraded=truncated）

generator(`log_factory.py`)+parser(`drc_log_model.py`)同源，保证 check.py 真值与 log 一致。

## 交付接口抽象

真实交付是 Markdown 报告（calibre_drc2_report.md）。为可机器校验，抽象为脚本化交付：`python3 <script> <log> -o <report.md>`，报告末尾内嵌 ` ```evidence ` JSON 块（结构化数字）。check.py 解析 log 真值 + 解析 evidence JSON，18 条独立断言校验四模块 + 反硬编码 B + 退化 B2 + 缺失路径 + 3-seed 确定性。

## 自验

- golden.py（自包含参考解）通过 check.py --self：18 条全 PASS（含 B 反硬编码、B2 截断退化、缺失路径退出 2、3-seed sha256 稳定）
- 5 个 negative 全 FAIL：empty_shell(<300B)/print_expected(A total_cpu 不符)/core_deleted(totals=None)/naive_hardcode_a(通过全部 A 检查，**专门**在 B total_cpu 触发反硬编码断言 ⑭)/stub_no_evidence(无 evidence 块)
- §4.9 三假(empty/print-expected/core-deleted)全 FAIL
- test 字段 == 磁盘 check.py 字节相等
- 断言闸门：test_rationale 以"18 条断言：①"开头，①..⑱ 共 18 个圆圈标记 == k_check=18 ≥ 8
