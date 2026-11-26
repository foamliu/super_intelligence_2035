# trace_deepreads/8cgph_verdi_license_checkout.md

## 元信息
- session: 1794388710536_8cgph
- user: e0045128 @ 10.129.2.14
- mc: 7 (keywords: synopsys:16;netlist:7;aether:3;synthesis:2;pyaether:1 — A-pure ratio 0.62, primary = synopsys/netlist)
- size: 56757 B / 13 msgs
- ssh ALIVE: 是 (r726 ssh 验证)
- domain: verification (Verdi = Synopsys waveform debugger; license 检查阻塞 verification)
- 选料路径: candidates_mc5.tsv → A-pure filter (a_kw regex, ratio>=0.5) → 16 fresh → ssh probe 8 → 选 8cgph (57KB, 最小之一, Verdi 启动错误诊断意图清晰)

## 用户对话流 (3 轮 user input)
- **U#1 (msg[1], ts=1794388711197)**: 「当起verdi时，报下面的error」+ 贴 Verdi 启动 banner:
  `logDir = /proj/lacaa/TV1_TestChips/CXTV1_FS001A/exchange/dig2pd/Datain_20261103_DBC/01_netlist/verdiLog`
  `Version R-2020.12 for linux64 - Nov 19, 2020`
  `rcfile = /apps/synopsys/verdi/R-2020.12/etc/novas.rc`
  `guiConfFile (read/write)= .../novas.conf`
  `[ERROR] Could not checkout Verdi license. Use verdi -licdebug for more information.`

- **U#2 (msg[3], ts=1794389331197)**: 「你帮忙跑verdi -licdebug」

- **U#3 (msg[11], ts=1794390055173)**: 贴 verdi -licdebug 完整输出 (A 档资产 = 本日志原样, 见 assets/verdi_licdebug_A.log):
  12 台 license server (全 12000 端口):
  - hl04, hl05, hl06, hl07, hl08 → Verdi feature: `FlexNet Licensing error:-8,544` (Invalid (inconsistent) license key)
  - hfds4 → Verdi feature: `-5,147` (No such feature exists)
  - hfrdap200, hfrdap201 → Verdi feature: `-97,121` (The desired vendor daemon is down)
  - hfrdap166, hfrdap167, hfrdap168, hfrdap169 → Verdi feature: `-10,147` (Feature has expired)
  - VERDI-ULTRA feature 在所有 12 台: 多数 `-5,147` (No such feature), hfrdap200/201 `-97,121`
  - 末行: `[SCL] 11/11/2026 17:38:01 PID:42082 Client:hfeg0plg56 Checkout denied Verdi 2020.12` + 第二行 VERDI-ULTRA

## 助手流水线 (msg[2], msg[4-10], msg[12])
- msg[2]: 识别为 License 获取失败 (非 Verdi bug), 给排查步骤: (1) `verdi -licdebug` 看详细 (2) `echo $SNPSLMD_LICENSE_FILE` / `$LM_LICENSE_FILE` (3) `lmstat -a -c $SNPSLMD_LICENSE_FILE` + `telnet/nc` 测端口
- msg[4-10]: 用户要求「你帮忙跑verdi -licdebug」后, 助手查 agent-policy (enforcing, profileIds=python-runner/shell-runner), 列 /home/e0045128 下 allowed files (看到大量 core.* 文件 — Verdi 之前 crash 过), 写 `run_verdi_licdebug.sh` 诊断脚本 (whoami/hostname/license env vars/command -v verdi/verdi -licdebug), 但沙箱无 Verdi 二进制 + 无 license env
- msg[12]: 收到用户贴的真实 licdebug 输出, **逐 server 分类**:
  | Server | FlexNet 错误 | 含义 |
  | hl04–hl08 | -8,544 | Invalid (inconsistent) license key (key 与数据不匹配, license 文件被改 / hostid 错) |
  | hfds4 | -5,147 | No such feature exists (license 里没 Verdi) |
  | hfrdap200/201 | -97,121 | vendor daemon down (lmgrd 在跑但 snpslmd 没起) |
  | hfrdap166–169 | -10,147 | Feature has expired |
  VERDI-ULTRA: 全 -5 或 daemon 挂, 基本都没有.
  **根因总结**: license 基础设施全坏 (key 坏/过期/没此 feature/daemon 挂) — 两个层面: (1) license 文件/授权本身有问题 (2) SNPSLMD_LICENSE_FILE 指错 server 集合.
  **建议动作**: (1) echo 环境变量确认 server 列表 (2) lmstat/lmdiag 逐 server 查可用 Verdi (3) 分层定位: 若某 server 能拿 → 环境变量指错; 若全拿不到 → 找 license 管理员修 key/续期/补 feature/起 daemon.

## 真实交付意图 (用户想要什么)
用户想要**诊断 Verdi license checkout 为什么失败 + 怎么修**, 不是只跑命令. 真实交付物 = 一份按 server 分类 + 根因 + 修复的结构化诊断报告.

## produce-task 化 (case 设计)
- **脚本**: `diagnose_verdi_license.py <verdi_licdebug_log> <output_json>` 通用解析任意 licdebug 日志
- **核心能力**: FlexNet 错误码 → category → root_cause → remediation 的**规范映射表** (14 类 + ok), 不是 hardcode A 的 4 类
- **A 档资产**: verdi_licdebug_A.log (msg[11] 原样, 12 server x 2 feature = 24 块, 4 类错误码 -8/-5/-97/-10)
- **隐藏 B**: 9 server (8 fail + 1 ok), 故意含 A 没有的 5 类错误码 (-1 cannot_connect / -9 invalid_host / -18 version_not_supported / -25 not_enough_licenses / -88 system_clock_set_back) + 1 台 Checkout successful (测 ok 分类, 反「永远报错」)
- **判分「牙」**: B 的 5 类新错误码 + ok server — 候选必须用规范 FlexNet 表分类, 不能 hardcode A 的 4 类; ok server 不能被塞进任何错误类
- **check.py**: 15 条独立断言 (a-o), 自验 ref PASS 15/15, 4 negatives 全 FAIL

## 关键设计决策
1. **block 边界**: licdebug 日志每个 (feature, server) 块以 `FlexNet Licensing checkout error: <msg>` (失败) 或 `FlexNet Licensing checkout: successful.` (成功) 开头 — 这才是 block starter, 不是 `Feature:` 行 (第一版 parser 误把 Feature 当 starter, 导致无 Feature 行的 ok 块被合并到上一块)
2. **feature_version 规范化**: SCL 行的版本是 `Verdi 2023.12` (无 R- 前缀), Verdi banner 是 `Version R-2023.12` — feature_version 取 banner 的 R- 规范形式, SCL 版本仅作 fallback
3. **client/feature_requested 从 SCL 取**: 第一条 SCL 行 = 主 feature (Verdi, 非 VERDI-ULTRA); client = hfeg0plg56 (A) / hfeg0plg99 (B)
4. **overall_verdict 4 态**: no_license_data (0 server) / all_servers_available (全 ok) / license_infrastructure_failure (0 ok 有失败) / partial_availability (有 ok 有失败) — B = partial_availability (1 ok + 8 失败)
5. **dominant_blocker** = 失败类计数最多的 category (B: cannot_connect x2)

## 自验结果 (r726)
- reference_submit.zip: check.py 15/15 PASS
- 4 negatives 全 FAIL @ 各自首失败断言:
  - neg_empty → a (无脚本)
  - neg_print_expected → k (B 输出含 A 字面量 hfeg0plg56/hl04/R-2020.12) + l (缺 B 字面量) + c (servers=1≠9) + e (无 ok server)
  - neg_core_deleted → d (全 unknown_error, 9 台 category 全错) + f + g
  - neg_no_ok_classify → e (ok server 被塞 vendor_daemon_down) + d (srv-lic-09 category 错)
- §4.9 三假提交 (neg_empty / neg_print_expected / neg_core_deleted) 全 FAIL ✓
- k_check == k_rationale == 15 (a-o) ✓
- e2e: 从 A.jsonl 提取 test 字段跑 check.py → ref PASS 15/15 ✓
- A.jsonl: 372 → 373

## 台账
- session 1794388710536_8cgph: claim → case (EDA-Eval-DesignFlow-VerdiLicenseCheckoutDiagnose-001)
- A.jsonl 372 → 373 (本 case)
- trace 覆盖率: 373/2907 = 12.8% (+1)
