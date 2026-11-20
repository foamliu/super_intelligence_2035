# 深读笔记 · trace 1792985372628_41ki8 · DRC connectivity script audit + DFM PROPERTY OPC011

- **session**: `1792985372628_41ki8` · user `xxchen` · host `hfeg0pkn005` · mc=146
- **tool 命中**: 381 calibre · 2 pyAether（calibre DRC/DFM 主导 = physical_verify seed）
- **规模**: 361 msgs · cwd `/home/xxchen`（connectivity/ 项目）· agent cline(lead)
- **正交性**: xxchen 现有 1 case = GDSBump2-001（skipper GDS bump，不同主题）；DFM PROPERTY OPC011/netid/sameNet/diffNet/.rdb/connectivity 主题在 shard C jsonl 无重复（仅 CCKDriverFind/ViaFillSvrfGen 远缘）⇒ 正交 ✓

## 用户真实意图（逐字原文）

- **U#0**（msg 0, ts 1792985373163）：「run_logic_notes 里提到了一个核心的命令 DFM PROPERTY OPC011 来统计netid的数量，从svrf_ur中找到DFM PROPERTY命令介绍，解释这个核心功能是如何实现的。 我已经把svrf_ur文档目录放到了当前agent启动路径下。」（纯意图：解释 DFM PROPERTY OPC011 netid 统计机制 → A-档合格 seed，用户未给根因/方案）
- **U#1**（msg 55）：「我在test目录下,使用了小case把中间运行结果也暴漏了出来， sameNet：connectivity/test/sameNet/sameNet.rdb diffNet: connectivity/test/diffNet/diffNet.rdb 你读取并整理到说明文档中，看到这个中间文档以及DFM PROPERTY 大部分人就懂了这个工具的原理。理解后加入到markdown和html说明文档中。」（扩展：把中间 .rdb 整理进说明文档）
- **U#2**（msg 80，**主交付需求**）：「把当前的drc connection脚本，run.py 的问题单独写成markdown格式+html格式。当前比较重要以及可优化的问题：1）TCP 不包含在呢。find_all_paths，抓不到TCP路径。2）metal具有上下层关系屏蔽via的情况不支持QA。3）SCONNECT 关系不在配置内。再详细列一个脚本改进plan。」（明确列出 3 个缺陷 + 要改进 plan → 这是本 case 的核心交付意图）
- **U#3**（msg ~later）：「优化html，请使用中文进行表述。」

> U#2 是"提出目标 + 明确缺陷清单"的用户轮（用户自己点出 3 个问题，但要求 agent 写成结构化文档 + plan）。本 case 取**正交子主题**：DRC connectivity 脚本（run.py）缺陷审计 + DFM PROPERTY OPC011 netid 机制解析，输出结构化 JSON 报告（机制 / 缺陷清单 / 改进 plan / 判定）。

## 对话流（assistant 工具链）

- **U#0 → A#1–#54**：list_allowed_files → search_codebase → read_files（run_logic_notes.md / run.py）→ run_approved_command（在 connectivity/svrf_ur/topics 里 grep DFM Property）→ editor（写 helper 解析 topic HTML）→ 读取 DFM Property topic / NETID() function page / DFM RDB page → read_files（run.py 的 process_net_file / pattern 生成段）。最终输出 DFM PROPERTY OPC011 机制解释：`DFM PROPERTY OPC011 netidnum = NETID()` 通过 `BY NET` 把同网多边形归并、用 NETID() 内建函数给每个 net 分配唯一整数 netidnum，结果写进 RDB（Results Database）的 netidnum 属性字段，run.py 再按 netidnum 分组做同网/异网连通性 QA。
- **U#1 → A#56–#79**：read_files（sameNet.rdb / diffNet.rdb，小 case 中间结果）→ editor 把 .rdb 解读整合进 markdown + html 说明文档（新增"中间结果"小节）→ run_approved_command 校验 HTML 标签平衡 / nav anchor。
- **U#2 → A#81–#239+**（**主交付，长 struggle**）：read_files（run.py 全文 + config）→ editor 写 problems 分析 markdown（覆盖 3 个问题 + 额外缺陷）→ 多轮 editor/run_approved_command 生成 html（反复遇到内容重复 / 标签不平衡 / 截断，最终用 Python generator 脚本 `tasks/build_issues_html.py` 一次性生成干净 HTML）。最终产出 `run_issues.md` + `run_issues.html`：① TCP 路径未在 `find_all_paths` 中（pass-transistor / 传输门对抓不到）② metal 上下层屏蔽 via 不支持 QA（上层 metal 遮挡 via 时连通性误判）③ SCONNECT 关系不在配置内（单向连接未覆盖）+ 改进 plan。
- **U#3**：html 中文化优化。

## 金标准（人工复核）

trace 末尾用户接受的结构化缺陷分析（run_issues.md/html）+ DFM PROPERTY 机制解释。本 case 金标准 = `drc_conn_audit_ref.py`：读取 run.py + sameNet.rdb/diffNet.rdb，输出 JSON 报告（mechanism/issues/plan/verdict/rdb_summary），缺陷检测对 3 个已知问题（TCP/find_all_paths、metal-via shield、SCONNECT）+ 改进 plan。断言只对事实（机制字段齐全 / 缺陷被检出 / clean 输入判 OK / malformed exit1 / 跨输入守卫无 A 专属 token / 确定性 / 反 naive），🚫 不对措辞。

## 选料口径

fresh-user (xxchen, 现仅 1 case) + 布局相关性精筛：纯 calibre (381) 主导，physical_verify 域。从 pick4 fresh-user（<=2 case）候选池 mc>=30 strong-ratio>=0.4 中选最高 mc 且首意图干净者；排除 e02141 TCAD（f6x1i/cpnbc = Sentaurus sdevice）、shwanlai Q&A 散问、miccao cv0pc（与 DRCHierLossAudit-001 同 calibre-drc-log-analysis skill 重复）、e0014566 r9m9l/60584/bu1r7（RScalc 主题已覆盖）/q3ks5（AutoVia 已覆盖）。41ki8 = DRC connectivity + DFM PROPERTY OPC011，主题在 shard C 无重复 ⇒ 选定。
