# Deepread: kjutt — .sp deck .lib-token + .inc spf-include rewriter (elianaz)

## trace_source
- user: elianaz
- host: hfhds201 (10.129.32.75 / .75; session file reachable via 10.129.32.100 shared home)
- session_file: 1795071277084_kjutt.messages.json
- match_count: 63 (hspice=21; netlist=463; spectre=20; sch=0 → pure spice/netlist)
- domain: spice_sim
- size: 309KB / 142 msgs / 71 user / 71 assistant
- agent: lead, deepseek variant

## 用户原话（verbatim, 6 substantive turns）
- U0: 「我想把某个目录下所有.sp后缀文件中的.lib行，比如后面这样
  `.lib '/proj/drcpa/V0/model/current_D5_v0d9_rev01/model.sp'`
  `.lib '/proj/drcpa/V0/model/current_D5_v0d9_rev01/incFile_lp'`
  current_D5_v0d9_rev01可能是任意字符，将其替换成为我想要的名称，我能在terminal键入。然后在这些sp文件中识别.inc的网表，必须包含spf字段，识别内容并显示，相同的合并显示，对每一个spf网表给出替换提示，输入y即为替换，n即为保持，若我输入y，则继续让我输入替换的名称，terminal键入」
- U10: 「某个目录设为当前目录」(target = CWD, not hardcoded)
- U17: 「在运行时输出乱码，改成英语」(English output)
- U36: 「识别spf网表时不识别被注释的行」(skip full-line comments * / // ;)
- U48: 「删除输出的 Example: .lib '.../model/current_D5_v0d9_rev01/model.sp' -> token = current_D5_v0d9_rev01。改为输出识别到的model/后面的名称」(display detected token = name after /model/)
- U59: 「不要判断y或者n了，直接输入替换的内容，若不换按回车跳过」(direct input replacement, Enter=skip)

## 真实 agent 交付（final replace_lib_and_inc.py, 已逐字抓取 8KB）
两步批处理工具，target=CWD 下所有 *.sp（非递归）：
- **Step 1 .lib token replace**: regex `(\\.lib\\s+'[^']*?/model/)([^/]+)(?=/)` 捕获 `/model/<token>/` 中的 token；collect_model_tokens 去重列出；input 新名；replace_lib_tokens 用 `re.subn(r"\\1"+re.escape(new_token))` 全文替换；跳过全行注释 (*, //, ; 开头)。
- **Step 2 .inc spf identify+replace**: regex `\\.inc\\s+'([^']+)'` 收集所有 .inc 路径，仅保留含 "spf"(case-insensitive) 的；去重合并 + 记录每个出现的文件 basename；逐个 input 新名（Enter=keep）；replace_inc_networks 用 str.replace 精确替换旧串。
- 输出全英文；目录不存在 → exit 1；无 .sp → exit 0。

## 造题方向（reframe → produce, L1, 纯 Python 文本正则替换无 EDA 二进制）
交互式 input 不适合 design_flow 判分（check 需确定真跑）。**reframe 成参数化非交互工具** `sp_lib_inc_rewriter.py`，CLI:
```
python3 sp_lib_inc_rewriter.py <directory> <spec.json> [--report <report.json>]
```
spec.json schema:
```json
{
  "lib_new_token": "<new token after /model/>",   // null/空 = skip step1
  "inc_replacements": [ {"old": "<.inc spf path>", "new": "<new path>"} ]  // 空 = skip step2
}
```
行为逐字对齐 trace final: 同 regex、同注释跳过、同 spf 大小写不敏感、同去重合并、同精确串替换。输出 report.json（n_files / lib_tokens_detected[] / lib_replaced{count,files} / inc_spf_unique[] / inc_replaced[{old,new,count,files}]）。

## A / hidden B（anti-hardcode 五重）
**A (visible)**: dir_A/ 含 4 个 .sp:
- deck_A1.sp: 2 条 .lib (/model/current_D5_v0d9_rev01/...), 2 条 .inc spf (top.spf + bank0.spf), 1 条 .inc 非 spf (model.sp), 1 条 *注释 .lib, 1 条 //注释 .inc spf
- deck_A2.sp: 1 条 .lib (同 token), 1 条 .inc spf (top.spf 重复→合并), 1 条 ;注释 .inc spf
- deck_A3.sp: 无 .lib 无 spf (干扰)
- notes.txt: 非 .sp (不应扫)
spec_A: lib_new_token="current_D6_v1d0_rev02", inc_replacements=[{old:".../top.spf",new:".../top_v2.spf"},{old:".../bank0.spf",new:".../bank0_v2.spf"}]

**hidden B (结构同, 取值/命名全异)**: dir_B/ 含 5 个 .sp:
- deckB_alpha.sp: 3 条 .lib (/model/revC3_pex_ttyp/... 不同 token + 不同 model 文件名 model_core.sp/model_corner.sp), 3 条 .inc spf (macro_x.spf + io_y.spf + analog_z.spf), 1 条 .inc 非 spf, 2 条不同注释样式 .inc spf
- deckB_beta.sp: 2 条 .lib (同 token), 2 条 .inc spf (macro_x.spf 重复 + analog_z.spf 重复→合并)
- deckB_gamma.sp: 1 条 .lib (不同 token revC3_pex_ffast → 验多 token? 不,trace final 只统一替换一个 token; B 用单 token 一致), 1 条 .inc spf (io_y.spf)
- deckB_delta.sp: 无 .lib 有 1 .inc spf
- sub/leaf.sp: 子目录 (不应扫, 非递归)
spec_B: lib_new_token="revD4_pex_final", inc_replacements=[{old 3 unique spf→new 3}]

anti-hardcode-A: B 无 current_D5_v0d9_rev01 / top.spf / bank0.spf / deck_A / dir_A token; A 侧 marker 0 出现于 B 输出。

## check.py ≥8 独立条件（draft, k=12）
① zip 内含 sp_lib_inc_rewriter.py 且 py_compile 通过
② 跑 B exit 0 + report.json 合法
③ B 5 个 .sp 中 4 个被处理（sub/leaf.sp 子目录不扫，notes 非 .sp 不扫 → 非递归）
④ B 所有 .lib /model/<token>/ 行 token 替换为 spec_B.lib_new_token (revD4_pex_final)，count==B 中 .lib 行数
⑤ 注释行 .lib 不被替换（保留原 token）— 反 naive 全局正则
⑥ B 所有非注释 .inc spf 行被替换为 spec_B 对应 new，spf 大小写不敏感（含 SPF/.SPF 变体）
⑦ 注释行 .inc spf 不被替换 — 反 naive 全局替换
⑧ .inc 非 spf 行保留不变 — 反 over-replace
⑨ report.inc_spf_unique 去重合并正确（重复 spf 只列一次 + 记录多文件）
⑩ report.lib_tokens_detected == [B 的原 token]（display name after /model/）
⑪ anti-hardcode-A: B 输出 + 源码无 A 侧 5 marker (current_D5_v0d9_rev01/top.spf/bank0.spf/deck_A/dir_A)
⑫ 3-seed determinism: 重跑 B out_sha256 一致

核心齿: ⑤⑦ 注释跳过（反 naive 全局正则/替换会误伤注释行）+ ⑧ 非 spf .inc 保留（反 over-replace）+ ④ token 精确（/model/ 后第一段，非整路径）。

## negatives（draft, ≥3 + §4.9 三假）
- neg_empty: 空脚本 → ② FAIL
- neg_print_only: 只 print report 不改文件 → ④⑥ FAIL (文件未变)
- neg_core_removed: 裸 copy 不做替换 → ④⑥ FAIL
- neg_global_replace: 无脑 str.replace(token) 全文替换（不跳注释、不区分 spf）→ ⑤⑦⑧ FAIL
- neg_recursive: 递归扫子目录 → ③ FAIL (sub/leaf.sp 被误处理)

## distinct check
- vs SpDeckModelStripMigrate-001 (r983 willz): 那个 strip 模型引用（删 .lib model 行），本 case 替换 /model/ 后的 token + 识别/合并/替换 spf include。完全不同操作。
- vs SanadjRblDeckSweep (r1002): 那个 deck 参数化生成，本 case 既有 deck 批编辑（lib+inc 重写）。不同。
- vs AiiloadReorgGen: 那个 PWL iload 重组，本 case .lib/.inc 重写。不同。
- B.jsonl 现有 lib/inc 相关 case 均为 strip/migrate/extract，无 "token replace + spf identify-merge-replace" 组合。

## INFRA 注
- elianaz live session 可读（309KB），经 eda_flow ssh+scp 到 .75 workdir 解析；final replace_lib_and_inc.py 仍存于 /home/elianaz/AI_agent/（10.129.32.100 共享 home）已逐字抓取。
- 候选筛选: 本轮 r1005 fresh-pool 大面积 peek（13 候选），前 12 均不可造（near-dup 4 / wrong-domain 6 / unproduceable 2），kjutt 是唯一 viable distinct 突破口。fresh B-spice 池被 joeyl-WCKTOP / zjqiao-CRCalert / e0039786-DBCvaractor 三 near-dup family + 大量 sch-dominant/env-how-to 噪声覆盖。
- **DEBT**: 本轮 r1005 因 40-min 预算不足做满 §4.9 8条+3neg+hidden B+anti-hardcode+3seed+self-verify，仅完成 deepread + claim。case 合成待 r1006（ETA 下轮 40-min 全量投入合成，deepread 已写好可直接动手）。
