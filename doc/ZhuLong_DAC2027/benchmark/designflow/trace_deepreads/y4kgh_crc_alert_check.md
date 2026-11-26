# y4kgh deepread — CRC alert check false-error fix (zjqiao)

- sid: 1795080330727_y4kgh | user: zjqiao | host: hfeahpc505 (10.129.33.28) | mc=88 | domain: spice_sim
- messages.json: 1.35MB / 148 msg / 13 user turns. 经 .75 SSH cat 取回全文。

## 用户真实意图（trace-faithful 原话）
- msg0: `/home/coverage/DDR5/DRVQA/sim_setup/Compare/meas_crc_alert.sp` 是目前 CRC alert check 脚本，"分析一下为什么会出现有时候crc报假错的情况（假错的原因是有两个alert falg时，CRC Alert Pulse Width可以扩大两倍但是有时候识别不出来，还有就是CRC Alert Delay Time有时也会测量错误）"
- msg70/95/106/114/140: 给多个 primesim.CRC005_Dualbank_wrcrc_auto_disable_triggered_* 仿真结果目录让检验（不同 PVT/速率：FF1.3v110C / TT0.94v25C / SS0.94v-40C，8000/10400 Mbps）。
- msg130/132/134: Q&A 追问 tMergeMargin 分组逻辑、新脚本如何判双 flag 合并脉冲宽度。
- msg122: "我希望你的脚本不会把原来脚本能检测过的检测成fail"（不能引入回归）。

## 真实问题根因（assistant msg139/147 结论）
旧 `runCrcAlertChk.pl` 的 `tMergeMargin` 分组有 **margin 符号 bug**：把 4 对合并 flag 全部拆散 → 4 条 `(/1)` 假脉宽超限 + 7 条假负 delay（含 4 条 undef 配对）。

## 修复机制（核心 produce = `runCrcAlertChk_fix.pl` / `crc_alert_check.py`）
两条无交集合法窗口（首尾相接 21=20+1，一条实测脉宽只落一个窗）：
- **errNum==1（单脉冲）**: width ∈ [12, 20]·tck → PASS
- **errNum>=2（合并脉冲）**: width ∈ [21, 37]·tck → PASS
- **delay** ∈ [3, 13] ns → PASS
- errNum 只负责"选哪个窗"，脉宽始终实测（逃不掉）。

## 真实边沿用例（msg139 实测，直接做 check.py 断言依据）
| 用例 | 构造 | 期望 |
|---|---|---|
| A: 1 flag / 24tck | errNum=1, width=24tck>20 | **FAIL**（width） |
| B: 2 flag / 15tck | errNum=2, width=15tck<21 | **FAIL**（width） |
| B2: 2 flag / 20tck | errNum=2, width=20tck<21 | **FAIL**（width） |
| C: 1 flag / 1x | errNum=1, width∈[12,20] | **PASS** |
| D: 2 flag / 2x | errNum=2, width∈[21,37] | **PASS** |

## 真实数据（msg147 CRC002 FF1.3V 110C 8000Mbps tck=250ps）
8 个 CRC error flag 两两合并成 4 条 2x 脉宽脉冲（全部合规 PASS）：
- P1: 1.1468+1.1490µs (间距 2.2ns), delay 3.5ns, 宽 5.826ns=23.3tck ✓
- P2: 1.1713+1.1735µs, 3.5ns, 5.827ns=23.3tck ✓
- P3: 1.3458+1.3480µs, 3.5ns, 5.827ns=23.3tck ✓
- P4: 1.3703+1.3725µs, 3.5ns, 5.824ns=23.3tck ✓

## reframe harness-for-teeth
- 原 deliverable = one-off perl fix (`runCrcAlertChk_fix.pl`) 修 `tMergeMargin` 分组 + errNum 选窗。
- reframe → produce 参数化 `crc_alert_check.py`（任意 CRC flag 事件表 + tck + merge_margin + 窗口配置 → 结构化 JSON 报告：分组/errNum/实测 width_tck/delay/选窗/verdict/reason）。
- asset A = msg147 CRC002 真实 4 对 + 2 单 + 边沿 A/B（FAIL）。
- hidden B = 异 tck(0.2ns)/异 margin/异计数 + 边沿 B2/C/D + delay-fail + 3-flag 合并组（errNum=3 验 >=2 而非 ==2）+ anti-hardcode-A（组数/tck/计数全异）。
- 判分有牙：真跑候选于 B，独立 oracle 对账每条 verdict/errNum/window/width_tck；§4.9 三假 + hardcode-A + nodelay 全 FAIL。

## 真实性保真
非脱敏：user=zjqiao / host=hfeahpc505 / 路径 `/home/coverage/DDR5/DRVQA/sim_setup/Compare/meas_crc_alert.sp`、`/home/zjqiao/crc_alert_fix/`、仿真目录 `primesim.CRC005_Dualbank_wrcrc_auto_disable_triggered_*` 全保真进 prompt。窗口 [12,20]/[21,37]tck、delay [3,13]ns、tck=250ps、CRC002 4 对数据全从 trace msg139/147 提取。
