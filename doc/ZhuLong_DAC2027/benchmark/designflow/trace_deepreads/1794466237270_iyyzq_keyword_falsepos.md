# Deepread: 1794466237270_iyyzq + 关键词假阳性调查 (2026-11-14 shard A)

## 结论先行
本轮在 mc>=10 候选池（11/13 快照 ssh_eda_search_20261113_131349）为 shard A
(digital/verification/pnr_signoff/eda_other) 选料时，**所有"未进任何 shard 台账"
的候选经深读均为关键词假阳性**——即 summary.tsv 的 keywords/tools 计数把 EDA
工具名命中在了脚本数据串 / 知识库引用 / 目录列表里，而非真实工具执行。真实高 mc
的数字/签核 flow 已被 4 个 shard 台账（共 3046 条去重 session）消耗殆尽。

## 调查方法
1. `trace_ledger.py --shard A next` 拿到 awk 候选式（mc>=10 + shard A keywords）。
2. 在 .75 跑 3 个递进过滤脚本（find_candidates / find_tool_digital / find_signoff），
   分别按 keywords 列、tools 列(真实工具调用词边界)、强签关工具(synthesis/dc_shell/
   pt_shell/primetime/icc2/voltus/... count>=8)筛 mc>=10 候选。
3. 把候选 sid 与 4 shard 台账并集（3046，已 strip .messages.json/.json）比对，留"clean"。
4. 对每个 clean 高 mc 候选 scp messages.json → 解析对话流深读。

## 三个 clean 候选深读（全部判 false-positive，已 parked）

### ① 1794386548710_l4tre  mc=575  xinqiaoz@hfeg0pkn002  -> parked
- summary keywords: pdk:1226 drc:306 calibre:235 lvs:128 rtl:101 .def:6
- 真实任务：维护 `genReleaseNote.py`（PDK QA release-note 生成器）——删 .bak 备份、
  修改 HTML 表头换行、修空内容字段、加默认收件人。87 次 run_approved_command 全是
  shell/python_generic_pdkqa 跑该脚本(--dry-run)或修代码。
- 假阳性来源：脚本数据/字符串里大量 calibre/drc/lvs/pdk 词。
- 判定：L1 Python 脚本维护，非 design_flow；无真实 calibre/LVS/DRC 执行。

### ② 1794206548447_artkz  mc=48  yihuig@hfeg0plg89  -> parked
- summary keywords: aether:128 virtuoso:87 drc:55 lvs:51 voltus:14 floorplan:16
- 真实任务：纯问答——"layout 完成 LVS/DRC 后还需要什么流程"、"这些流程在 aether/
  virtuoso 中用哪些工具实现"。agent 调 AskEDA 知识库（DeepSeek-R1-fp8 模型 disabled
  反复失败），最后凭知识 + Aether ref manual 拼文字答案。
- 假阳性来源：AskEDA skill references / Aether tool-qa ref 文档里的工具名词。
- 判定：信息检索问答，零工具执行，非 design_flow。

### ③ 1794466237270_iyyzq  mc=15  jerrychu@hfeg0pkn003  -> parked
- summary keywords/tools: innovus:10 lvs:8 pyaether:7 aether:7 calibre:6 netlist:6
- 真实任务：文本处理——用户贴 PDK corner 名单，要求 newline->space，以及写 sed
  one-liner 把 `ssgnp_0p675v_0c` 转成 `ssgnp_mos_varactor_dbc/TYPICAL/0.675/0`。
  agent 写 python 验证脚本测 sed，反复迭代 sed ordering bug。
- 假阳性来源：list_allowed_files 列出的目录名(innovus.cmd1/innovus.log/DRC/LVS)被
  计成 keyword。
- 判定：Linux/sed 文本处理，非 design_flow。

## clean 候选全量（mc>=10, tool-digital 过滤, 不在任何台账）
仅 8 条，全部 mc<=70 且为假阳性/极短：
1794386548710_l4tre(575, parked), 1794445658665_b6iql(91), 1794380399121_8dkdw(70),
1790151429785_t5h84(32), 1794466237270_iyyzq(15, parked), 1792046020511_0cn06(11),
1792042776292_jzove(10), 1792048349487_ry9f4(10) — 后 5 条 mc<=32 多为 aether/virtuoso
版图微操作，且 mc 太低难支撑 >=8 独立断言。

强签关工具(synthesis/dc_shell/pt_shell/primetime/icc2/voltus count>=8) clean 候选：
仅 5 条，全 mc<=48，多为短会话。

## 根因
shard A keyword 过滤词(verdi/vcs/innovus/.../rc/tcl/verilog/...)会在以下场景误命中：
(a) PDK/QA 报告脚本的数据串；(b) AskEDA/Aether skill ref 文档；(c) list_allowed_files
返回的目录/文件名；(d) `rc` 子串匹配 `drc`、`tcl` 匹配普通 tcl 脚本。tools 列同样基于
关键词扫描，无法区分"执行工具"与"提到工具名"。

## 建议（给后续轮 / 其他 shard）
1. 选料加一道"真实工具执行"判据：要求 session 里出现 `run_approved_command`/shell
   实际调用工具二进制(如 `calibre -drc`/`innovus -files`/`pt_shell -f`)，而非仅词频。
   可写个 probe 在 messages.json 里 grep 命令行。
2. 考虑放宽到 mc>=5 或对 clean 低 mc 候选做"真实 flow"probe 后再判。
3. 跨 shard 去重已用 4 台账并集(3046)；若要继续造 A 档 case，需换更精细的 domain
   识别（如 0.8B prefilter 的 is_design_flow 二分类 + 真实工具执行 probe）。
4. 本轮未交付 case（0 条 jsonl 增量）；3 条 false-positive 已 parked 进台账，避免重复捡。

## 本轮台账动作
- claim+parked: 1794386548710_l4tre (mc575, pnr_signoff->falsepos)
- claim+parked: 1794466237270_iyyzq (mc15, eda_other->falsepos)
- claim+parked: 1794206548447_artkz (mc48, pnr_signoff->falsepos) [注: artkz 用 claim?
  实际只 mark parked，未单独 claim——见 ledger]
