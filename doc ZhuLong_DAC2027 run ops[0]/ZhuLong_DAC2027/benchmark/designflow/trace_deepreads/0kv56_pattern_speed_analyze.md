# deepread: 1793172758983_0kv56 — PatternSpeedAnalyze (jascperc @ hfeg0pkn001)

- **session**: `1793172758983_0kv56` (462 msgs, 1.78MB, directory format)
- **user**: jascperc (new — no prior cases in any shard)
- **host**: hfeg0pkn001 [10.129.2.10], also hfeg0plg80 [10.129.8.120]; autofs /home readable from .75
- **match_count**: 160 (verilog:3287 keyword, pure digital)
- **agent**: lead (cline)
- **domain**: digital (verilog pattern simulation analysis)

## Real task (U#0, single-turn produce-task)
用户要求对两个 dvprog 目录下的 `pattern_simulation_*.avc` 文件统计验证了哪些 speed（频率）、每个 speed 多少支，并按文件 mtime 的 MCU 周做每周统计，输出 html 和 md 报告。具体规则：
- speed = avc 文件名倒数第二个下划线字段（如 `..._10667_011.avc` → 10667）
- 每个 .avc 要检索对应同名文件夹；文件夹只有 irun.log 的不算合法 pattern（需有 A_Compare/ncsim 等结果）
- 按周统计，周序号按实际 MCU 周标记，给图例（折线/柱状）
- 中文翻译成英文避免乱码

两条路径：
1. `/rundata/iejoad/V0/simdir/verilog/e0033105/verilog.pim.iejoad.PTE_20260624_1/dvprog/`
2. `/rundata/iejoad/V0/simdir/verilog/e0033105/verilog.pim.iejoad.PTE_20260624/dvprog/`

## Agent 行为
- IDX0 用户给 task + 详细规则（speed 提取、合法性判定、周统计、输出格式），未给 root-cause → A-faithful produce-task。
- Agent 用 list_allowed_files / run_approved_command(python-runner/shell-runner) 探查目录，写 `pattern_analysis.py`。
- 受 cline editor 6000-char new_text 限制 + heredoc 复杂度，反复 insert/rewrite 文件，多次出现 duplicate/corruption，挣扎 460 轮才完成数据扫描逻辑（pa_final_v3.py 扫到 1158 avc / 152 valid），但报告 HTML/MD 生成部分因编辑器大小限制未完整追加，最终以 chat 内 markdown 总结交付（IDX461）。
- 最终结果：PTE_20260624_1 主目录 146 valid + avc/ 3 + PTE_20260624 avc/ 3 = 152 valid，全 10667 MHz；1000 个 9600 pattern 因 only-irun.log 被排除；5 周 W34/W38/W42/W43/W44。

## 合成判定
- A-faithful：用户给 task + 规则，未给 root-cause → A档（非 B档）。
- deliverable = Python 分析脚本 + 报告（非私有路径文件）→ 沙盒可行。
- 验证规则明确、可机器判分（speed 提取 / folder 合法性 / 周分组 / 递归扫描）→ 适合 design_flow check(deliverable, workdir)。

## 合成方案：EDA-Eval-DesignFlow-PatternSpeedAnalyze-001 (digital L1-A, k=12)
- SUT 写 `pattern_speed_analyzer.py`（纯 stdlib CLI `--dirs DIR [DIR...] --out OUTDIR`），递归扫 *.avc，speed=倒数第二下划线字段，合法性=同目录同名文件夹存在且含除 irun.log 外结果文件，按 mtime ISO 周分组（W{week}-{year}），输出 html/md/summary.json。
- A（可见）：A_dvprog/ 3 个 .avc（主目录 2 + avc/ 1），2 valid / 1 only_irun_log，speed {10667:2}。
- B（隐藏，check 内生成、确定性 mtime）：6 个 .avc，3 speed(10667/9600/8400)，4 valid / 1 only_irun_log / 1 no_folder，speeds {10667:3,8400:1}，weeks {W38-2026:1,W42-2026:2,W45-2026:1}。
- 12 断言：①zip 含脚本 ②纯 stdlib ③B 退出 0 ④三报告文件非空 ⑤total_valid==4 ⑥speeds{10667:3,8400:1} ⑦weeks==ISO oracle ⑧only_irun_log skip==1 ⑨no_folder skip==1 ⑩递归 avc/ 计入 ⑪跨输入守卫 A==2valid ⑫9600 跳过+total_avc==6。
- 自验：ref SELFTEST PASS 12/12；3 fake-submit(empty/print/garbage)全 FAIL；3 negative(wrong-speed-field/no-irun-exclusion/non-recursive)全 FAIL。

## 资产
- assets/EDA-Eval-DesignFlow-PatternSpeedAnalyze-001/A_dvprog/（7 文件，含 avc/ 子目录）
- reference/EDA-Eval-DesignFlow-PatternSpeedAnalyze-001/check.py + pattern_speed_analyzer_ref.py
- A.jsonl 253→254
