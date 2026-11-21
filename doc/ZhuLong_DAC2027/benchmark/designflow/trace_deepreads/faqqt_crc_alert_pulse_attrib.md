# faqqt — CRC Alert Pulse-Attribution Checker (deepread)

**Session**: 1795080052098_faqqt · zjqiao @ hfhds234 (10.129.32.100) · mc=105 · spice_sim
**Date**: 2026-11-22 (r986)
**Source**: live `/home/zjqiao/.cline/data/sessions/1795080052098_faqqt/1795080052098_faqqt.messages.json` (1.28MB, 133 msgs)

## 用户真实意图（9 条 user 消息）

zjqiao 维护 DDR5 DRVQA 仿真流的 CRC Alert 时序检查（`meas_crc_alert.sp` FineSim .meas + `runCrcAlertChk.pl` 判定）。**假错根因**：两个 CRC error flag 离得近时电路合成一个 2x 宽度 Alert 脉冲，原判定脚本 `tMergeMargin` 分组有缺陷（`margin=间距-0.1ns`，`间距>margin` 几乎永远成立 → 该合并的对被拆散），导致：
1. 2x 脉宽被当单脉冲比 [12,20]tck → 必超 20 → 误报 `pulse width out of range (/1)`；
2. 拆散后第二个 crcerr 配错位 Alert → 负/undef delay → 误报 `delay out of range`。

U0 分析根因；U3-U7 给 8+ 个真实 sim 目录要 agent 用新脚本复检是否假错；U8-U9 要解释旧 tMergeMargin 分组为何失败 + 新算法如何处理双 flag 合并。Agent 交付修复版 `runCrcAlertChk.pl`（469 行，脉冲归属算法）+ validate.py（12 场景回归）+ recheck.py，8 真实案例全 Pass、零回归。

## 关键产物结构

- `.meas` 测三类：`crcerrN`（alert_flag rise 时刻）、`AlertN`（Alert_n fall 时刻）、`AlertpwN = <pw> targ=<end> trig=<start>`（脉宽，trig=fall=start）。失败测量输出 `= error`。
- spec：tck=PERIOD；TD∈[3,13]ns；单脉冲 PW∈[12,20]tck；合并 2x PW∈[21,37]tck。
- 原 bug：`groupCrcErr` 按 crcerr 间距 + tMergeMargin 分组（margin 计算错）。
- 修复：**按实际脉宽 pw_tck 判单/合并**（不看 crcerr 间距），单消耗 1 个 crcerr、合并消耗 2 个，delay=Alert fall−第一个 crcerr。

## reframe

form = `crc_alert_chk.py` Python 参数化 CRC alert 检查器（pulse-attribution by pw_tck，produce，A-faithful，layer L1，纯 Python 文本处理无 EDA 二进制）。A=合成 .mt0（FF 6400Mbps 4 合并对）；hidden B=合成 .mt0（SS 10400Mbps 7 对+1 单，timing 全异 anti-hardcode-A，含 `=error` 失败行）。check.py 12 条 a-l。核心齿：④pulse-attribution by pw_tck NOT tMergeMargin + ⑤merged vs single spec + ⑨error-line skip。反 neg_core_removed(tMergeMargin buggy) + neg_print + neg_empty。

## 候选筛选
r985 triage 留 faqqt 为 "not peeked (recovery cost)"。本轮直读 live session（未清，无需 .snapshot 恢复）。zjqiao 新用户（无 concentration risk），netlist:687 dominant，非 near-dup（现有 Mt0Xxx 系列是 aggregation/stats/extraction，无 CRC alert pulse-attribution + judgment 形态）。
