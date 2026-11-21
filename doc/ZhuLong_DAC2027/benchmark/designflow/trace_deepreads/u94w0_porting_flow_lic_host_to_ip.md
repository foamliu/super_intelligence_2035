# u94w0 deepread — porting_flow skill, flashlvl license host->IP rewrite

## trace meta
- session: u94w0.messages.json (scp'd to .75 workdir `e0031982_20261121-shardC_DF-C-r922_0`)
- user: jcgu @ hfeg0plg81, mc=299
- dominant keywords: lvs:1138; calibre:423; virtuoso:303; aether:285 → physical_verify
- 500 msgs / 17 typed user_inputs

## real task (U#0..U#16)
jcgu 维护自建 `porting_flow` SKILL：5 步版图迁移 tkinter GUI 启动器
(config → Origin LVS → Smash pcell → LVL → Virtuoso LVS)。
GUI 由 skill 用非交互 `bash -lc` 拉起，启动后用户在 GUI 里点步骤按钮跑各步。

## 5 个调试子任务（全部 fixture 候选）
- U#1: GUI 保持 + skill 启动后退出 (bsub 改造)
- U#3: step2 LVS 没跑起来（bsub -K exit 0 但无 CORRECT/INCORRECT marker）
- U#5: step2 LVS exit 1 with lsf_submit.err
- U#9: **step3 LVL flashlvl license checkout 失败** ← 本 case 抽取
- U#10/11: step4 strmout virtuoso GDS export error
- U#13/14: step5 si -batch netlist CDL export error (LD_PRELOAD)
- U#15/16: 清理脚本 + skill 改名

## 本 case 选 U#9 的根因（trace msg 146-209 验证）
- 同一条 `flashlvl -CONTROLFILE ... -cpu 16` 命令在交互 terminal 能跑、在 GUI 里 fail
  with 'Failed to obtain the version of license server'。
- 诊断：GUI 由 `bash -lc` 非交互拉起，该 context 里 python `getaddrinfo` /
  `socket.gethostbyname` 解析不了内网 license server 主机名
  (hl01=10.129.62.139 / hl02=10.129.62.140 / hfds2=172.16.8.102 / hfds1=172.16.8.101
  / iccd02 / icce01)，但 `getent ahosts` 能解析成 IP。
- flashlvl 的 FlexLM 客户端用未解析的 hostname 连 license server → checkout 失败。
- DISPLAY 同类问题此前已用 'host->IP' 方案修好（`_resolve_host_ip` 已存在）。
- assistant 的修复：在 `porting_flow.py` 启动清理块里把 license env vars
  的 `port@host` token 用 `getent ahosts` 解析成 `port@IP`，写入 `os.environ`。
  注：launch_porting_flow.py 里写一次会被 `bash -lc` 的 module 重新 source 覆盖，
  所以必须在 porting_flow.py 启动后（module 加载完之后）再写一次才生效
  （msg 195-209 的关键发现）。

## 抽取的 2 个独立 bug（fix-the-bug fixture）
- bug A scope：`LICENSE_ENV_VARS` 只含 `EMPYREAN_LICENSE_FILE`，漏 `LM_LICENSE_FILE`
  和 `TOOL_LICENSE_FILE` → flashlvl 的 FlexLM 客户端读 LM_LICENSE_FILE 仍见 host-form
  → checkout 仍失败。
- bug B resolver：`_resolve_host_ip` 用 `socket.gethostbyname`，而
  `socket.gethostbyname` 正是在 `bash -lc` context 里解析不动内网名的元凶 →
  重写静默 noop，原 `port@host` token 被保留 → 同一个 bug 没修。

## A 档为何不可行 → B 档 reframe
- live workspace 在 hfeg0plg81 上 READ-ONLY，e0031982 远程无读权限；
- flashlvl/Calibre/Virtuoso 需要 license + grid + DISPLAY，SUT 沙盒都没有；
- reframe 为 self-contained fix-the-bug fixture：env_A.tar.gz 里 buggy licenv.py
  + porting_flow.py stub + spec + sample env + getent shim_A + run.py；
  SUT 交付修好的 licenv.py + 原 porting_flow.py + report.json。
- 判分器用 env_B (hidden，不同 hostname licA..licF / 不同端口 27000,1717 /
  不同 IP 192.168.50.x) + getent shim_B 真跑 licenv.rewrite_license_hosts_to_ip。

## fixtures
- env_A.tar.gz: buggy licenv.py + porting_flow.py + spec.json + license_env_A.json
  + getent_shim_A.sh + run.py (4662 bytes)
- hidden/env_B.tar.gz: license_env_B.json + getent_shim_B.sh + hidden_manifest.json
- reference/solve.py: 字符串模板写 fixed licenv.py + copy porting_flow.py
  + report.json
- reference/check.py: 16 teeth (a-p) — 结构/AST/反硬编码源码 + 真跑 B 验三变量
  + 3-seed 字节一致
- reference/negative/: 4 neg + 2 §4.9 stubs (empty_stub/only_print/delete_core)
  全 FAIL distinct (tooth d / l / i / f / i / i)

## 自验
- ref solve.py 产 gold submit.zip → check.py PASS 16/16
- 6 negatives 全 FAIL distinct
- §4.9 (a)(b)(c) 三假全 FAIL distinct: empty_stub→d / only_print→l / delete_core→i
- 3-seed tooth p PASS
- roundtrip sha256 disk==jsonl==re-read = 39fd7ee5d1fa4cf23748c65f8da3283f7345f34f979b9115564954bd9fcddea4
- k_rationale = k_check = 16 ✓ (≥8)

## 落库
- append C.jsonl 569 → 570
- trace_ledger.py --shard C claim+mark u94w0 → case (EDA-Eval-DesignFlow-LicHostToIpRewrite-001)

## lessons
- (a) 同一类 'host->IP' 修复可拆成多个独立 bug (scope + resolver)，每个有独立
  失败模式 + 独立区分齿，check.py 16 teeth 中 5 个核心修复齿 (h/i/j/m/n) 直接对应。
- (b) getaddrinfo vs getent 是 agent/sandbox context 的经典坑：socket API 解析不动
  内网名但 NSS (getent) 能——gold fix 必须用 getent，fixture 友好（无需 license/grid）。
- (c) 多步 trace (5 step porting flow) 单步抽取仍能造高质量 case：U#9 一个子任务
  足够独立 + fixture 友好 + 真实意图清晰；剩余 U#3/U#5/U#10/U#13 是后续候选。
- (d) 反硬编码三层：B 用不同 hostname set (licA..licF) + 不同端口 (27000/1717) +
  不同 IP 段 (192.168.50.x)，hardcode_A neg 必 FAIL tooth i/k/o。
- (e) AST-level 检查 vs substring：tooth i 用 AST 防止 docstring 文本误中
  'socket.gethostbyname' 字符串——必须用 ast.Attribute 节点检查，不能 grep。
