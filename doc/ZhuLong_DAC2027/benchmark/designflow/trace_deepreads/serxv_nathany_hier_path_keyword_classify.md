# deepread: serxv — hierarchy path report keyword classification

- **session**: `1794899388341_serxv` (nathany@hfeg0plg95, mc=72, 162 msgs, 550KB)
- **cwd**: `/home/nathany` (agent sandbox); target file on `/proj/drcoa/V0/workdir/peipei/`
- **trace domain**: physical_verify (hierarchy path report analysis)
- **claimed**: r1052 (shard C), marked case `EDA-Eval-DesignFlow-HierPathKeywordClassify-001`

## 真实任务流

nathany 拿到 DDR5 TOP 设计的 MOS 实例层级路径报告
`/proj/drcoa/V0/workdir/peipei/DDR5TOP_pc60MOSinstance_hierarchy_path.rpt`
(465,126 条数据条目, 格式 `##Target_Cell\tPath` 表头 + 每行 `<cell>\t<path>`,
path 为点分隔层级如 `TOP.XI_Channel.XI_BCenter.XI_BCenterCA.XI_Controller.XI_D_ColAdrCtrl`)。

三轮递进分析请求:

### 请求 1 (msg 0): 统计 Controller 关键词条目
- 用户: "检索以下路径，统计文件中每个条目中的关键词Controller涉及到条目总数"
- agent 写 `analyze_controller.py` (python-runner), grep + 正则匹配
- 结果: **120,884** 条 (25.99%), 全在 `XI_Channel.XI_BCenter.XI_BCenterCA.XI_Controller` 下
- Top 子模块: XI_D_ColAdrCtrl(24072) / XI_C_APCtrl(23968) / XI_C_CmdDec(15242) / XI_D_WrLatencyCtrl(12322)

### 请求 2 (msg 24): 分别统计 Mrrlfsr / Ras / Cas
- 用户: "分别将Mrrlfsr及Ras及Cas相关到条目进行相同统计"
- agent 写 `analyze_keywords.py` → `analyze_final.py`, 修正正则边界 (Ras/Cas 初始 `(?<=\.)` 过严返 0, 改为简单子串)
- 结果 (case-insensitive):
  - **Mrrlfsr**: 16,854 条 (匹配 `MrrLfsr`), 全在 `XI_C_MrrLfsrDqGen_New_0` 下
  - **Ras**: 95,872 条 (32 个 `XI_R_RasBnkLogic` 实例 × 2996), 99% 为 `XI_R_RowPreDec`
  - **Cas**: 32,332 条 (32 个 `XI_D_CasBnkCtrl` 实例 × 904), 67.5% 为 `XI_D_PracCmdCtrl`
  - 三者**零交叠** (Jaccard 0%)
  - 至少一个: 145,058 (31.19%)

### 请求 3 (msg 70): IO_ / D_ 归类 + 排除规则
- 用户: "分别统计文件中'IO_'和'D_'相关到条目，若同一条目中同时存在D_和IO_则归类为IO_，若同一条目中同时有Controller和D_则不归类为D_"
- 规则:
  1. IO_归类: 条目含 `XI_IO_` → IO_
  2. D_归类: 含 `XI_D_` 且**不含** `XI_IO_` 且**不含** `Controller`
  3. 优先级: IO_ > D_ (overlap 归 IO_)
  4. 排除: Controller+D_ → 不归 D_
- agent 写 `io_d_core.py` → `io_d_detail.py` (editor 多轮故障, python-runner 限制, 最终成功)
- 结果:
  - 总条目: 465,126
  - IO_ 全集: 50,846 (含 XI_IO_)
  - D_ 全集: 374,264 (含 XI_D_)
  - Controller: 120,884
  - D_ ∩ IO_: 42,200 → 归 IO_
  - D_ ∩ Controller: 52,222; D_ ∩ Controller ∩ ¬IO_: 52,078 → 从 D_ 排除
  - D_ ∩ IO_ ∩ Controller: 144
  - **归类**: IO_ 50,846 (10.93%) / D_ 279,986 (60.19%) / 其他 134,294 (28.88%)
  - 验证和: 374,264 = 42,200 (→IO_) + 52,078 (Controller排除) + 279,986 (D_) ✓
- IO_ parent: XI_IO_DqIoTop(24320) / XI_IO_DqsIo(6480) / ...
- D_ parent: XI_D_DQBYTELOW_1(55374) / XI_D_DQBYTELOW_0(55374) / XI_D_BDPTierX16_772(14754) / ...

## 关键观察
- 这是**纯离线 Python** 任务 (无 EDA 工具, 无沙盒, 仅文件解析 + 集合运算 + 统计)
- 核心可计算意图: **hierarchy path keyword 分类器** (pattern 子串匹配 + priority_order + exclusions + parent module 分布)
- agent 经历多次 editor/python-runner 故障 (文件已存在需 old_text, args 不生效, 中文非 ASCII 被 sandbox 拒), 最终用 python-runner + 多脚本拆分完成
- 真实数据规模 465K 条, 但任务逻辑与规模无关 → 可用小规模合成数据测试

## case 合成 (HierPathKeywordClassify-001)
- **reframe**: 通用化关键字族 (sample_a 用 IO_/D_/Controller 同 trace; hidden B 用 ANA_/DIG_/Clock 不同族 + 不同规模)
- **deliverable**: `classify_hier_keywords.py <report> <config> <output>` 纯 stdlib
- **判分**: check.py 独立 oracle (不同实现, 集合+不同控制流) 重算 B 输出逐字段比对
- **k=13**: zip/compile/run/total/raw/classified/percentage/unclassified/overlaps/exclusion/parent/determinism/B2-anti-hardcode
- **反硬编**: hidden B2 (27 条, 异于 B 的 67 条) + hardcode_b 负向 (硬编 B 输出, B2 必 fail cond m)
- **区别**: C 域 physical_verify 子型 hier-path-keyword-classify 首例, 与 DrcResultsItemCollect-001(per-cell results 解析) / DrcDeckStructureAudit-001(deck 结构审计) 产物/断言/trace 全不同
