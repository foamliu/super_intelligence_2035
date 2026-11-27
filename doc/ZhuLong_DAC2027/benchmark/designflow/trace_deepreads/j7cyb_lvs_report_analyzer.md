# deepread: j7cyb — ARGUS LVS report analyzer SKILL

- **trace**: 1795673548048_j7cyb (oshen@hfeg0plg54, mc=869, analog_context)
- **file**: 1.5MB, 61 msgs (36 user / 25 assistant)
- **fetched**: .75 ssh→hfeg0plg54, per-session subdir `/home/oshen/.cline/data/sessions/1795673548048_j7cyb/1795673548048_j7cyb.messages.json`

## 用户真实意图

oshen（模拟版图工程师，DDGOA 项目）两步：
1. 读取一份 8308 行 ARGUS HLVS 报告 `RWEccbufv2New_DDGOA_plan5_Rev28.lvs.rep` 并解读失败原因。
2. 扫描 `/rundata/empy/oshen/` 下**所有** `*.lvs.rep`，把失败原因归纳成一个 **SKILL**，让用户以后直接把 report 喂给 skill 就出诊断结论。

## 助手工作流

1. 读完报告：ARGUS LVS 2025.06.sp1.hf9，顶层 `RWEccbufv2New_DDGOA_plan5_Rev28`，**FAIL**，"Numbers of instances not equal"，110 个子 cell 全 PASS，问题在顶层连接；6 条 discrepancy（3 layout-only: X32 nor2GFx2 / X37,X38 aoi21PFx1；3 source-only: XI_BlcNor2GFx2_DP_1 BlcNor2GFx2_DP / XI1,XI57 nand2PFx1）；cell 选型不同步（nor2GFx2 vs BlcNor2GFx2_DP，nand2PFx1 被合并成 aoi21PFx1）。
2. 调 skill-creator 拿规范；尝试 python-runner/shell-runner/SandBox 执行扫描脚本——**全不可用**（policy 拒绝 / 沙箱未启动）。
3. 改用 list_allowed_files + read_files 手工扫 `LVS_fail_check/` 下约 200 份 `*_FAIL_report.txt` 摘要，覆盖 19 个 cell 家族。
4. 归纳 **7 类错误**：ports/nets/instances 数不等 > Extra pins not floating > Connectivity errors > Missing layout names > Property errors；**3 种失败范围**：仅顶层（3 个 FAIL section，最常见）/ 少量子 cell（5~15，同一 IP 反复挂）/ 全层级（>50，CDL/hcells 版本错位）。
5. 关键陷阱：**目录名带 `_pass` 实际可能 FAIL**（命名是人工标记不可信）→ result 只认 TOTAL RESULTS 区块。
6. 创建 SKILL：`/home/oshen/.cline/skills/lvs-report-analyzer/SKILL.md` + `references/report-anatomy.md`（5 section 解剖）+ `references/failure-catalog.md`（7 类错误 + 真实案例 + 3 种范围）。

## case 合成（task_id=LvsRepDiagnoseProduce-001, LIVE-NA, judge_layers=[L0,L1]）

synthesized-reframe：把"读报告→出诊断"的解读逻辑固化为通用解析器 `analyze_lvs_report.py <report> <out.json>` + hidden-B 反硬编码。

- **A**(visible) `report_A.lvs.rep`：顶层 RWEccbufv2New_DDGOA_plan5_Rev28，FAIL，"Numbers of instances not equal"，6 discrepancy（3 layout-only + 3 source-only），top-only scope，2 mismatch pairs。
- **hidden B**(token-structurally 不同) `report_B.lvs.rep`：顶层 SaCtrlArray_S5，FAIL，**2 类错误**（ports not equal + Connectivity errors，A 只有 1 类），4 discrepancy（≠6），few-subcells scope（2 failed hcells，A 是 top-only），cell 类型全换（invx2/nand3x1/dlyinv/oai22x1 vs nor2GFx2/aoi21PFx1/BlcNor2GFx2_DP/nand2PFx1）⇒ A 硬编码器在 B 全错。
- **reference**：`analyze_lvs_report.py` 通用 ARGUS 报告解析器（section banner 定位 + 正则，不靠行号，不硬编码任何 cell/net 名）。
- **check.py 16 conds(a-p)**：独立 GT 解析器(二次独立实现)复算 A/B 报告 → 比对候选 diag：a zip+py ②b py_compile ③c A 运行 exit0+合法 JSON ④d A result==FAIL ⑤e A error_categories 匹配 GT ⑥f A n_discrepancies==6 ⑦g A layout_only==3 ⑧h A source_only==3 ⑨i A X32/nor2GFx2/coord/pins.Y==237 ⑩j A XI_BlcNor2GFx2_DP_1/BlcNor2GFx2_DP/pins.Y==net73 无 coord ⑪k A scope==top-only+top_failed+failed_hcells=[] ⑫l A mismatch_pairs 含 nor2GFx2<->BlcNor2GFx2_DP ⑬m B 运行 exit0+合法 JSON ⑭n B error_categories 含 ports+connectivity(B 专属) ⑮o B n==4+scope==few-subcells+failed_hcells==2(B 专属 ≠A) ⑯p 反硬编码源码无 A 专属 token。
- **LIVE-NA**：deliverable=Python 解析脚本，check 跑候选(subprocess)+独立 GT 复算断言，无真实 EDA 工具二进制依赖（ARGUS LVS 不在 .75，报告=纯文本结构化解析判分）。
- **自验全绿**：ref check.py on reference_submit.zip → PASS 16/16 + negative_selftest 4neg ALL-FAIL distinct first-fail{c,d,g,n}(§4.9 trio full: empty→c/print_only→n/core_deleted→d + extra: hardcode_a→g) + SKIP_RUN=1 eval/run_one.sh workdir leak 自检通过(无 check.py/reference/hidden 泄漏) + 3-way sha sync(disk==JSON test==metadata.check_sha256=70955777...) + k_check=16=k_rationale=16 + 框架 auto-build jsonl D 601 case 含本条。
