# 深读笔记：1792491091764_qk0vo — Innovus 启动就绪诊断（eda_other）

## trace 元数据
- session_file: `1792491091764_qk0vo.messages.json`（cline v3 目录式，33 msgs / 90KB）
- user: `pdong` / host: `10.129.8.230`（机器名 hfeg0plg98）/ match_count: 49 / 工具计数: innovus 359 主导 → **eda_other**（环境/工具启用诊断，非 PNR flow 本身）
- 时间：2026-10-20 18:11 ~ 2026-10-21 08:40（跨天，session status=failed exit_code=1，因发现真因后用户未再回复）
- model: deepseek-v4-flash / agent: zhulong（lead）
- 已 claim 台账（shard A，domain=eda_other）。

## 用户意图（逐字原文，A 档选轮判定）
- 真实用户轮只有 #0（初始需求）+ #12「你确定吗」。
- #0 原文：「帮我调查下如何启用innovus module avail 是有的难道需要bsub吗」
- **A 档选轮规则判定**：#0 用户给出的是**症状 + 一个猜测（bsub）**，未指出根因、未给修复方案 → 符合 A 档「提出需求」轮规则。但本条做 **B 档（synthesized）**：原话过短且含猜测，合成场景化 prompt 更利于判分接口稳定；真实意图保留为「诊断 innovus 为何 module avail 有却跑不起来，是否真需要 bsub」。

## 真实任务（一句话）
用户在 RHEL8 登录节点上 `module avail` 能看到 innovus 多个版本，但 `module load innovus/2231_s119_os7` 后执行 `innovus` 直接报 `libssl.so.10: cannot open shared object file`。需诊断能否在当前节点启动 innovus、根因是什么、是否需要 `bsub` 切到 CentOS7 计算节点。

## 真实诊断结论（金标准，已从 trace #11/#16/#20/#29 逐条复核）
1. **module avail** 列出 6 个版本：23.35 / 2114_ISR4_os7 / 2139_ISR9_os7 / 231_os7 / 2137_ISR7_os7 / 2231_s119_os7。
2. **module load** 成功，`which innovus` → `/apps/cdsmgr/cadence_tools/innovus/INNOVUS2231/tools.lnx86/bin/innovus`（rc=0）。
3. **innovus -version** rc=127，stdout：`.../innovus/bin/64bit/innovus: error while loading shared libraries: libssl.so.10: cannot open shared object file: No such file or directory`。
4. **OS**：`Red Hat Enterprise Linux release 8.10 (Ootpa)`（RHEL8）。
5. **系统 libssl**：`/usr/lib64/libssl3.so` + `libssl.so -> libssl.so.1.1.1k` + `libssl.so.1.1 -> libssl.so.1.1.1k` + `libssl.so.1.1.1k`（**只有 openssl 1.1，没有 libssl.so.10**=openssl 1.0.x，那是 CentOS7 时代的库）。
6. **ldd 真因**（#29 sec 4）：
   - `libjvm.so / libmlpack.so.3 / libarmadillo.so.9 / libfvengine.so / libzmq-0dcb31d9.so.5.2.4 => not found`（一组 ML 相关缺失库）
   - **libstdc++ 污染**：`/apps/imctf/cad/ai/agent/eda_agent/eda-agent-20261016-154840/lib/libstdc++.so.6: version 'GLIBCXX_3.4.26' not found` —— eda-agent 自带的 libstdc++ 通过 LD_LIBRARY_PATH 抢占，导致 GLIBCXX 版本不匹配。
7. **最终判定**：innovus 2231 **无法在当前 RHEL8 登录节点启动**，根因双重：①RHEL8 缺 libssl.so.10（openssl 1.0 兼容库）②eda-agent 的 LD_LIBRARY_PATH 污染 libstdc++。**修复建议**：`bsub -Is -q <queue> -R "centos7"` 切到 CentOS7 计算节点（该节点有 libssl.so.10 + 干净 libstdc++），或装 `compat-openssl10` 并 `env -u LD_LIBRARY_PATH`。
8. **agent 第一轮（#11）误判**：先说「不需要 bsub，直接 module load 就行」→ 用户「你确定吗」(#12) → agent 重测后发现 libssl.so.10 缺失 (#20/#22)，最终修正结论为「需要 bsub 到 CentOS7 节点」。这个**先错后纠**的过程是真实 trace 的关键难度信号。

## 合成 case 设计（EDA-Eval-DesignFlow-InnovusLaunchDiag-001，B 档，domain=eda_other，L2）
- **交付**：`outputs/submit.zip` 含 `check_launch.py`——一个启动就绪诊断脚本，读「证据目录」（fixed-name 文本 fixtures，模拟 module avail / which / exec / ldd / os_release / lib_search / env_ldpath / module_show 的真实命令输出），输出**结构化 JSON 报告**。
- **A（SUT 可见）**：qk0vo 真实证据（innovus 2231 / RHEL8 / libssl.so.10 缺失 / libstdc++ 污染）。
- **B（隐藏）**：结构/取值不同的另一场景（calibre 2024.4 / RHEL 9.3 / libncurses.so.5 缺失 / 无 LD 污染）——check.py 只跑 B。
- **判分**：check.py 在独立临时目录解 zip，subprocess 执行 `check_launch.py --evidence-dir <B> --module calibre --version 2024.4_u2024.10`，解析 JSON，断言 17 条（a–q，见 check.py CONDITIONS 表），含三假提交回归 + 3-seed 随机化。
- **test_rationale**：17 条断言（k_rationale == k_check == 17 ≥ 8）。

## 关键难度点（case 区分模型能力的地方）
1. **不能只看 module avail/which 成功就判 launchable**——必须真跑 `<bin> -version` 并解析 rc + error 文本。
2. **missing_libs 要双源**：exec error 里的 `libXXX.so.N: cannot open` + ldd 的 `=> not found`，取并集。
3. **lib_provider_mismatch** 要交叉验证：exec 报缺的 lib 是否真不在系统 lib_search 里（libssl.so.10 vs libssl.so.1.1）。
4. **ldpath_pollution** 要识别 ldd 里来自非系统路径、带 `GLIBCXX_x.y not found` 的 libstdc++ 行——这是 trace 里最隐蔽的真因。
5. **verdict + recommended_action** 要据因给出「换 CentOS7 节点 / 装 compat 包 / 清 LD_LIBRARY_PATH」之一，不能空泛。
