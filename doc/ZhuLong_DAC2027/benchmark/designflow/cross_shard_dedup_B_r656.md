# Cross-shard dedup audit — shard B reaudit pool (r656, 2026-11-16)

## 背景
r618 意图审计把 191 条旧 parked 候选重判为「可造」（11-15 用户令·候选池重审）。
r642 已发现 2 条 cross-shard false-positive（jhdvn=D MBistAnalyze-001、qzva9=D IVCurveRegionClassify-001），从 191 中剔除。
r619-r655 据此「复活池」变现 37 条 case。

## 本轮 (r656) 动机
取复活池下一候选时，逐条核对 12 条带 deepread 笔记的「可造」候选，发现**除 68gc9(v5icx 等 B 自身已造) 外几乎全部属于其他 shard**——说明 r618 reaudit 未做跨 shard ledger 对账，191 数高估。

## 方法（逐条对账，可复算）
对 `pool_reaudit_B.tsv` 全部 191 条「可造」：
1. slug 取 `session_file` 5 字符码；
2. 查 `trace_ledger_{A,C,D}.tsv` 中 `status==case`（**列 5**，非列 4——r656 修正了 r642 脚本的列索引 bug）的 slug→case_id 映射；
3. 查 `trace_ledger_B.tsv` 自身 case（列 5）+ r619-r655 显式 done 列表；
4. 查主 `EDA-Eval-DesignFlow.jsonl`（4 shard 合并）`metadata.trace_source.session_file` slug。

## 结果
**9 条 cross-shard false-positive**（已在 A/C/D ledger 标 case，B reaudit 误判可造）：

| slug | 真属 shard | 已造 case_id | B 池旧判定 |
|---|---|---|---|
| cr42l | D | PrimeLibFlowAnalyze-001 | consulting: k库流程 explanation |
| ty6oq | C | VirtuosoStartupDiag-001 | consulting: pcell script organization |
| q9aja | A | WaveviewModuleUpdate-001 | prior-rejected consulting |
| 6rvi0 | C | DRCReportIpAudit-001 | DRC report consulting |
| 8zuer | D | DQTXStim-001 | consulting: 学习分析sp文件 |
| fi203 | C | InnovusProjLogDiag-001 | innovus project analysis |
| 5i5bo | D | TwoStepOcNetlistAudit-001 | feishu doc fetch consultation |
| tdt0k | D | PowerSupplyHierInventory-001 | 电源 explanation consultation |
| 6kot7 | C | SVRFDeckCatalog-001 | calibre doc study note |

## 处置
- `pool_reaudit_B.tsv`：上述 9 行 `新判定` 由「可造」改「不可造」，`拟造任务形态` 写 cross-shard 原因 + 真属 shard + case_id（**不删行**，保留作口径变迁证据）。
- 191 可造 → **182 真可造**。
- MEMORY `🔍 候选重审` 行更新：191 → 182（新增 9 cross-shard false-pos，r642 的 2 条 + 本轮 9 条 = 11 条累计剔除）。

## 修正后的真·可造池口径
- 182 真可造 − B-ledger 已 case(r619-r655 37 条 + 历史) − 显式 done ≈ **135 真正未造**
- 其中 **B 域(spice_sim/characterization) 80 条**（form 分布：Q&A/咨询 39 / how-to 12 / explain 12 / debug-Q&A 10 / analysis 7；mc>0 的 45 条，mc=0/空 35 条）
- 顶层 mc 候选（均无 deepread 笔记，需 .75 新深读）：2ze9s(mc83) / gxlr2(mc71) / m40h5(mc60) / d06uu(mc51) / oue4a(mc49) / hasla(mc41) / 0l5zn(mc37) / qo7xn(mc35)

## 列索引 bug 修正记录
r642 脚本把 ledger `status` 当作列 4（实为 `domain`），导致 cased_other/cased_b 漏匹配。
正确列序：`[0]session [1]user [2]host [3]mc [4]domain [5]status [6]case_id [7]date`。
本轮脚本用列 5 判 `case`、列 6 取 case_id，复算 B-ledger cased=349 / A+C+D cased=1001 / 主 jsonl cased slug=1257。

## 结论
复活池**未枯竭**（80 条 B 域 clean 候选），但**所有高 mc 候选均无 deepread 笔记**——下轮 r657 应从 2ze9s/gxlr2/m40h5 取一条走 .75 ssh/scp 新深读 → 合成。本线 MEMORY「191 误杀复活」口径自此修正为 182。
