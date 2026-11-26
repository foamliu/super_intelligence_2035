# r678 deepread: qinqinl / r00t7 — SPF Sa_BLa↔PreEq 耦合排序

**session**: 1792499259030_r00t7 · user: qinqinl · host: 10.129.8.134 · mc35 · domain: physical_verify
**fetched**: 245 msgs / 24 user turns / 102 tool_use (editor writes + python-runner)

## 用户意图演进（真实原话）

- **U#3** 「可以帮我分析spf数据吗」→ 引出 SPF 分析主线
- **U#15** 「附件是spf数据」→ 用户提供真实 SPF 附件 (msaq_E 提取)
- **U#55** 「所有Sa_BLa与PreEq的coupling 帮我sorting出来」→ 核心需求
- **U#69** 「所有Sa_BLa需要排序，例如 `C17487_4,XI_msax256_cp00.XI_CXSA_1x4_0<48>.Sa_BLa<0>` 首先按照 cp00-cp* 顺序；然后每个cp里`<48>`这个需要排序，最后`<0>`这个需要排序；Sa_BLa按照顺序分别与PreEq coupling帮我sorting出来」→ **三级排序规格**：block(cp00..cp*) → CXSA idx `<48>` → Sa_BLa bit `<0>`
- **U#95** 「pracL cp07 后边；pracR在cp08前边」→ **自定义 block 序**：cp00..cp07, pracL, pracR, cp08..cp15
- **U#105** 「重新覆盖一下」
- **U#111** 「把Sa_BLb和preEq的也按同样的方式sorting一下放到csv文档里」
- **U#121** 「整合成一份csv」
- **U#143** 「作曲线图处理下这个数据 横轴是sa_bla 纵轴是sa_bla与preeq的coupling值」
- **U#167** 「Sabla是不是应该有4496个 帮忙check 下」→ **count check** (真实 4496)
- **U#179** 「帮忙修正这个，把缺失的那一个加进去，相当于preeq CC为0」→ **缺失 net CC=0 要求**
- **U#190** 「Sabla / Sablb 的total loading 按照order sorting 出来」
- **U#204** 「cn*bl*<*>和preEq的coupling sorting」
- **U#219** 「可以把没有与preEq耦合的也加上吗 按cnbl顺序来，耦合显示为0」→ 第二个 net 家族 (cn*bl) 同样的缺失 CC=0
- **U#215** 「交付清单里可以把.csv 和对应的脚本以及内容都列出来吗」→ **deliverable = CSV + 脚本**
- **U#235** 「帮我把面的.csv 整理成excel吧. 分成四个sheet」→ 最终交付含 xlsx

## 助手工具链（关键产物）

assistant 写了一族脚本（均在 /ai_sandbox/drgqx/V0/agentdir/qinqinl/）：
- spf_analyze.py / spf_verify.py / spf_final.py — SPF 解析 + union-find over breaker resistors
- **spf_bla_preeq_sorted2.py** — Sa_BLa↔PreEq 层级排序 → CSV（最终版，含 BLOCK_ORDER cp00..cp07→pracL→pracR→cp08..cp15 + 缺失 net CC=0 + count check 4496）
- spf_blb_preeq_sorted.py — Sa_BLb↔PreEq
- spf_ab_merge.py — A/B 合并
- spf_ab_total_loading.py — total loading
- spf_cnbl_preeq_sorted.py — cn*bl↔PreEq（含 declared-but-uncoupled CC=0，U#219）
- spf_check_sabla.py — count check (4496)
- make_excel.py — 4-sheet xlsx

判分环境不可跑真实 StarRC/SPF（无 .75 上 msaq_E 大文件 + union-find breaker R 依赖真实数据）→ **reframe 为纯 stdlib spf_coupling_sort.py**：保留核心语义 = parse DSPF `*|NET`/`*|C`/`*|CC`/`*|ENDNET` + 提取 Sa_BLa↔PreEq* 耦合和 + 三级排序 (block_order/cxsa/bit) + 缺失 net CC=0 + count guard + CSV。

## 选料判定

VIABLE produce-task ✓：用户多次明确提出 produce-task（写脚本生成排序 CSV），有明确交付物、明确排序规格、明确缺失处理要求、明确 count check。判分有牙（结构化 CSV + 数值 + 排序序 + 守卫 + 确定性 + 防硬编 B≠A）。C 域 physical_verify（pex/SPF 耦合分析，post-PEX physical verification）。

## 其他本轮 peek 候选（均 park）

| session | user | 判定 | 理由 |
|---|---|---|---|
| bjy3l | xinqiaoz | teeth-fail | U#0 diff DrcPatternCheck.py + goodExisting/badMissing=-1 含义解释, prose Q&A 无 runnable gold |
| 57yk9 | xinqiaoz | off-C | U#0 为 docs/proposals 加 index.md, 通用文档索引非 C 域 |
| ylbw0 | thqu | teeth-fail+off-C | U#0 Simvision 保存波形(D 域 waveview) + U#11 打开 aether layout GUI-op |
| s97z0 | jialeshan | off-C | U#16 完善邮件后缀 C++ 代码, 非 EDA physical |
| n8ozx | jcgu | thin | U#0 加载 skill + U#7 DRC testpattern, 意图模糊 |
| 0ufar | miccao | teeth-fail | U#0 总结 Argus 工具包开源库+LVS 算法脉络, open-ended prose |
