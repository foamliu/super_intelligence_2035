# Deepread: 1794553984282_g5ise (e0039602 / hfeg0pkn003, mc=225)

> trace-faithful A档候选 · domain=eda_other (verilog-LLM-trans automation)
> 扫描源 ssh_eda_search_20261114_184938, verilog-strong口径(verilog count≥50, any position), 4-shard ledger 未收录
> 深读+合成轮: r537 (2026-11-14). 1.1MB / 155 msgs, 无 DEBT.

## 1. Trace 元数据
- session_file: `1794553984282_g5ise.messages.json` (subdir layout: `sessions/1794553984282_g5ise/1794553984282_g5ise.messages.json`)
- size: 1,115,427 bytes (1.1MB) · mtime 2026-11-13 16:33 · 文件 ALIVE
- user: e0039602 · host: hfeg0pkn003 (10.129.2.12)
- 155 msgs / 90 user / 65 assistant / **13 real user inputs** / 77 tool_use
  - tool_use 分布: editor=31, read_files=20, run_approved_command=16, list_allowed_files=10
- keywords: verilog:785; netlist:204; drc:66; lvs:11; cadence:8; rtl:7; systemverilog:3; waveview:2

## 2. 真实任务流 (13 real user inputs, 按主题归并)

### 主题 A — 项目对比 (U0, analysis)
- U0: "对比这个项目和/home/e0039602/Documents目录下2.2copy的区别"
  → agent 创建 _tmp_compare_22_232.py 做目录/文件 diff

### 主题 B — LLM 重试逻辑修改 (U1-U6, 核心produce-task)
- U1: "告诉我现在代码的大模型调用出错重试逻辑是什么"
- U2: **核心修改**: "修改502 503 504错误的重试逻辑，现在是只重试一次，如果失败就直接跳过，或者超过10分钟也直接跳过，跳过后将没生成的打印到log，然后再设置时间上限20分钟，再对他们进行重试，最后只有这两波都没生成出来的再报错"
  → 两波重试: 第一波 max_transient_retries=1 + 10min, 第二波 max_transient_retries=None + 20min
- U3-U6: "继续" + 抱怨慢

### 主题 C — 编译检查流程 (U7, analysis + U9, question)
- U7: "流程里不是还有一波编译检查吗，你这一系列操作在编译检查前吗，解释编译检查如果查出来错了会如何调用模型修改"
- U9: "代码是边跑边写入resultmap的，编译发现没过重写才通过，代码会修改resultmap吗"

### 主题 D — 生成策略修改 (U8, produce-task)
- U8: "现在是每次生成3个让ai评审3选1吗，改为对同一个model生成两次，让他2选1"
  → parallel_worker.py: max_workers=3→2, range(3)→range(2)

### 主题 E — 流程重构 (U11, 核心produce-task)
- U11: "当第一波弄完后，你就先编译修改完，这样闭环一次，然后再开始处理第一波没跑出来的"
  → run.py: 第一波后先 _xrun_verify() 编译检查，再跑第二波；移除全局后置编译

### 主题 F — 清理 (U10, U12, produce-task)
- U10: "把不属于项目流程的一次性脚本全都删掉"
- U12: "gen_diff.py gen_diff_io.py compare_versions.py _analyze_netlist.py都干嘛的，对流程有影响吗"

## 3. 涉及文件 (均在 /home/e0039602/Documents/verilog_lib_trans_v2.3.2copy/)
1. **run.py** — 主入口, 两波重试 + 逐波编译闭环 + consume_pass/_xrun_verify/write_module重构
2. **src/agent_client.py** — LLM 客户端, 新增 max_transient_retries 参数 + trans_retries 计数器
3. **src/parallel_worker.py** — 并行 worker, 3→2 候选 + max_transient_retries 透传
4. _tmp_*.py — 一次性对比/分析脚本 (后被删除)

## 4. 合成结果 (r537 交付)
- **archetype**: verilog-llm-trans-retry-refactor (eda_other, L1 离线 Python, A档 trace-faithful)
- **case_id**: EDA-Eval-DesignFlow-VltRetryWave2-001
- **核心交付**: 修改自包含的 trans_runner.py，实现 4 项改动：
  1. generate() 新增 max_transient_retries (瞬时错误次数硬上限)
  2. generate_candidates() 从 3-pick-1 改为 2-pick-1 + 透传 max_transient_retries
  3. translate_modules() 两波重试 (第一波严格 max_transient_retries=1, 第二波宽松 None+20min)
  4. 逐波编译闭环 (第一波后编译检查, 不再全局后置)
- **可见 A**: trans_runner.py (pre-modification) + task_brief.md
- **隐藏 B**: 不同 module 列表 + 不同失败模式 (hidden_manifest.json)
- **check ≥13 断言** (k_check=k_rationale=13):
  a zip valid / b max_transient_retries 签名 / c retries=1→harderror / d retries=0→immediate harderror / e retries=None→retry until success / f 2 candidates / g failed_wave1 字段 / h wave1 skips transient / i wave2 retries / j per-wave compile / k 3-seed determinism / l not hardcoded (B scenario) / m degradation (original fails)
- **negative**: 原始未修改代码缺 max_transient_retries + failed_wave1 → 条件 b/g/h 失败
- **取材**: 从 session editor tool_use 提取 agent_client.py / parallel_worker.py / run.py 的实际改动模式，自包含化为单一 trans_runner.py
- **验证**: check.py 在正确解上 13/13 PASS, 在原始代码上 FAIL (条件 b)
