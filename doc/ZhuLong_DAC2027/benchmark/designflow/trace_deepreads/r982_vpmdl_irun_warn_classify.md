# r982 — 1795153452622_vpmdl — irun.log 告警分类去重报告生成

## trace 来源
- session: `1795153452622_vpmdl.messages.json`
- user: lein @ hfeg0pkn005, mc=86
- keywords: netlist:733;verilog:536;analog:33;lib.defs:22;systemverilog:13;schematic:7;binary:4;primetime:3;synthesis:1
- A-domain 归因: netlist 数最高但用户实际在做 irun.log 仿真告警分析 (verification), 非 netlist/spice 主导; 归 A-pure verification。
- 选料来源: `_a_dom_cands_r963.tsv` 420 候选 × 4-shard ledger 交叉得 38 fresh; 严格 A-domain 过滤后高 mc fresh 多为 C/B/D-dominant (drc/hspice/analog/netlist 主导), guomings 6 siblings (ewjfi/le2ke/m2iag/5d3vo/60khu/1862w) 全是 r971/r975 slice_interface dram1sc 任务的 dup/parent → REJECT; vpmdl 是仅余的 A-pure verification fresh 高 mc 候选。

## 用户意图 (U#92 逐字)
> /rundata/decqa/V0/simdir/verilog/lein/1113/1103_lp6tb/test_log/refresh_short.x24/irun.log
> 分析这个日志文件中的告警信息 然后分类列出所有告警信息 注意 不要重复

(注: U#0 是 UNDIDN ISO_LATION 诊断 = r964 ff8hl 同任务 dup, 已跳过; U#63 SDFNSB 告警 Q&A 是本任务的上下文铺垫; U#92 是独立的告警分类去重 produce-task。)

## trace gold (#93-#109)
agent 写 Python 脚本解析 irun.log, 提取每条 `*W,<CODE>:` 告警行 (trace 中实际 106,266 条 *W 告警, 33 类码, TRTDECAY 占 10万+), 按码去重, 统计每类出现次数, 捕获每类首例 + 出处分组, 按**发出工具/主题**分类 (SDF 反标类 / 端口连接类 / 代码质量类 / 运行时类 / 工具性能类), 输出 markdown 报告 (33 码 + 每码次数/说明/出处示例)。

## 本 case 提炼 (produce-task)
通用 `classify_warnings.py <irun.log> <output.json>`: 解析 Xcelium 日志, 提取 `*W,<CODE>:` 告警行, 按 CODE 去重, per_code{count,tool,first_example}, 按**行首工具前缀** (ncvlog/ncelab/ncsim/irun) 分组 by_tool{count,codes}, 输出结构化 JSON。
- 工具分类规则 (确定性、通用): 正则 `^(\w+)\s*:\s*\*W,` 提取行首工具; trace 的语义主题与工具一一对应 (SDF→ncelab, 端口→ncvlog/ncelab, 代码质量→ncvlog, 运行时→ncsim, 工具→irun), 故 by_tool 分类忠实于 trace 语义。
- 去重: unique_codes 按字母序, 每码一个 per_code 条目, first_example=该码首次出现整行原文。

## A / hidden B
- A (可见): irun_A.log, 59 行 / 52 告警 / 12 码 (SDFNSB/SDFINF/SDFNEP/CUVMPW/BNDWRN/CSINFI/FAAOP1/VARIST/INTWID/TRTDECAY/PRPASZ/BADPRF), 跨 irun/ncelab/ncsim/ncvlog 四工具。
- B (隐藏): irun_B.log, 66 行 / 61 告警 / 12 码; 10 个 B-only 码 (SDFNSC/SDFNEN/SDFNDP/CUVWSB/BNDMEM/CUVWSP/INTOVF/REALCV/IGNFMT/PRFRTNEV) + 2 共享码 TRTDECAY(B=25≠A=15)/BADPRF(1)。B 由 check.py 内联构建 (避免路径耦合)。

## check.py 18 断言
zip+py_compile+stdlib / exit0+JSON有效+5键 / total_warnings=61 / total_lines=66≠total_warnings / unique_codes精确12码 / num_unique一致无dup / TRTDECAY=25反硬编码A的15 / SDFNSC=7 B-only泛化 / by_tool[ncsim]=26 / by_tool[ncvlog].codes精确6码 / SDFNSC.tool=ncelab / INTOVF.first_example含CODE / A-only 10码不泄漏 / 无伪造码 / 3次md5确定性 / 输出≥400B非空壳 / per_code覆盖全12码拒core-deleted。

## 自验
- ref PASS 18/18 (本地 + 输出结构正确)
- 3 negatives 全 FAIL: neg_empty (无产出) / neg_print_only (硬编码A值, B计数/码不符 + 非结构化JSON) / neg_core_deleted (skeleton在但核心提取删除, total_warnings=0/unique_codes空)
- §4.9 三假 (a空壳/b print-only/c core-deleted) = 上述 3 negatives, 全 FAIL ✅
- A.jsonl 442→443 · ledger vpmdl claimed→case · eda_flow session r982

## 选料注
mc≥10 池 (shard_mc.A=10, summary_stats shard_mc.A=10); r963 _a_dom_cands_r963.tsv 420 A-domain 候选 × 4-shard ledger (约 4500+ sids) 交叉得 38 fresh; 严格 A-domain 归因后 (排 drc/hspice/analog/netlist 主导) 高 mc fresh 仅 vpmdl (lein mc86, verification) 可做, guomings siblings 全 dup r971/r975。与 r966 yk8qc (同 lein 用户, refresh smoke-run) 无 intent-dup (不同 session 不同子任务: irun 告警分类去重 vs refresh.run 冒烟脚本裁剪)。
