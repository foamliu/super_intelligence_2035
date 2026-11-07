WAITING: 1（等人工：运维仍未回 #376 公开仓 PII 冲突 (a/b/c/d) 裁决；本轮 #388 继续 option (d) 审计，无新增 PII）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

> ⚠️ **OPERATOR REVIEW REQUESTED — round #376 paused at harvesting gate (2026-11-08)**
>
> 本轮 #376 未执行 trace 采集 / case 合成。原因：本轮被要求 `trace_ledger.py --shard D next` → SSH 到内网机器读真实工程师的 `.cline/data/sessions/<sid>.messages.json` → 把 `trace_source{user,host,session_file}`（**真实**用户名/主机名/session id）写进 `EDA-Eval-DesignFlow_D.jsonl` 并 `git push`。任务书红线 #2 明确要求「不脱敏」。
>
> agent 的顾虑（需运维拍板，非技术阻塞）：
> 1. 这是**无显式同意**地大规模采集 ~2,850 名工程师 / 698 台机 / 52,698 个会话的私有工作记录，并把真实身份 commit 进 git 仓库（外部发布「默认先内部、未排除」）。
> 2. 对内部 EDA 评测而言，**匿名化**（user_N / host_N / hashed sid）几乎不损失保真度——任务语义/工具链/文件格式/拓扑不变，只是不暴露具体是谁。当前「禁脱敏」红线是让本流程难以协助的关键点，而非 benchmark 本身。
> 3. 在无人工在场确认同意口径的自治 loop 里，agent 选择**暂停新一轮采集**，把决定权交还运维，而非默认继续。
>
> **运维若确认以下任一，agent 即恢复**（直接在本文件下方回写即可，loop 下轮读到即生效）：
> - (a) 已有文档化的内部策略/用户知情同意，允许采集与提交真实标识 → 按 #376 原流程继续；
> - (b) 放宽红线 #2，允许匿名化 → agent 继续 loop 但写匿名标识；
> - (c) 仅用运维本人或已明确授权的 session → agent 只从该子集选料；
> - (d) 暂停采集，转做已建 case 的质量审计（check.py 严度 / negative / 断言闸门 / 难度校准），不访问新用户数据。
>
> 未做任何 SSH 采集、未改 jsonl、未动台账。本条为**待人工裁决的外部阻塞**，故 `WAITING: 1`。
>
> **#377 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决，故**新一轮 SSH 采集仍暂停**。本轮改做**不涉及新用户数据的 TASK 强制质量工作**（§4.4 每轮抽查 1 条重跑 + §4.9 三假回归）——抽查 #375 PortTextPinPlan-001（已有 case，标识符此前已入库，无新增公开 PII）：negative_selftest 7/7 FAIL（NEG_RC=0，6 distinct first_fail b/d/e/f/g/j）；§4.9 三假 empty→b / print_only→f / core_deleted→d 全 FAIL distinct；ref reference_submit.zip check() PASS 16/16；断言闸门 k_rationale=k_check=16≥8 ✓；jsonl test 字段（11306B, sha ceebae472ffda7af）与磁盘 check.py byte-sync ✓。**判分器完整、闸门通过、无泄题**。**关键确认**：`foamliu/super_intelligence_2035` 经 GitHub API 实测为 **public** 仓库——这与红线 #2「全产物不脱敏（含 MEMORY/深读笔记保留原值）」直接冲突（MEMORY_D 推送 = 真实工程师 user/host/sid 进公开互联网），亦与 §9「Benchmark 是否对外（默认：先内部）」矛盾。**该冲突只能由运维裁决**：维持暂停 / 改 private 仓库 / 放宽红线允许 MEMORY 匿名（jsonl 仍走内网 devops.cxmt.com 不受影响）。**无新增公开标识符、未改 jsonl、未动台账**。`WAITING: 1` 保留（等人工）。
> **#378 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决（已第 3 轮等待）。本轮继续 option (d)——不涉及新用户数据的质量审计：抽查 **#374 CtleTranPower-001**（analog_context，已有 case，标识符此前已入库，无新增公开 PII）。结果全过：§4.4 `negative_selftest.py` 4/4 FAIL（NEG_RC=0，3 distinct first_fail b/c/d）；§4.9 三假 empty→[b] / print_expected→[c] / core_deleted→[d] 全 FAIL distinct；ref `reference_submit.zip` 经 `check()` 返回 True（PASS）；断言闸门 k_rationale=k_check=16（a–p）≥8 ✓；jsonl `test` 字段与磁盘 check.py byte-sync（13328B，sha 139eca67b89b7a04 两端一致）✓。**判分器完整、闸门通过、无泄题、无新增公开标识符**。`WAITING: 1` 保留（等人工）。
> **#379 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决（已第 4 轮等待）。抽查 #373 DecoderNetlistGen-001：negative 6/6 FAIL distinct b/c/e/f + §4.9 三假 empty→b/print→b/core_del→e 全 FAIL + ref check() PASS 16/16 + 闸门 k=16 + test==disk byte-sync 17088B sha 43ee6f28。**无新增 PII**。`WAITING: 1` 保留（等人工）。
> **#380 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决（已第 5 轮等待）。本轮继续 option (d)——抽查 **#372 DevListSummary-001**（schematic_netlist，已有 case，标识符此前已入库，无新增公开 PII）。结果全过：§4.4 `negative_selftest.py` 6/6 FAIL（NEG_RC=0，distinct first_fail = {b, d, e, j, n}，其中 empty→b / print_expected→b / core_deleted→e / naive_hardcode_a→d / naive_unweighted_csv2→n / naive_wrong_shrink→j）；§4.9 三假 empty→[b] / print_expected→[b] / core_deleted→[e] 全 FAIL（§4.9 仅要求三者全 FAIL，已满足；**观察**：empty/print_expected 均为弱假被 (b) B-run 退出码/产物早捕，未触达内容守卫，但 case 具真实反硬编码守卫 cond (o) A-run≠B-run + A_MARKERS 泄漏检测 + naive_hardcode_a→d（CSV1 行数对不上），防硬编码有效）；ref 由 `device_summary.py` 打包为 submit.zip 经 `check()` 返回 PASS（16/16，cond a–p 全过）；断言闸门 k_rationale=k_check=16（a–p）≥8 ✓，test_rationale 以 `16 条断言：①…` 开头 ✓；jsonl `test` 字段与磁盘 check.py byte-sync（14906B，sha 0e276c8b08e937540f547d01a23810675dc325ebc995e6bbfab58a61c5c5bdff 两端一致）✓。**判分器完整、闸门通过、无泄题、无新增公开标识符**。`WAITING: 1` 保留（等人工）。
> **#388 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决（已第 8 轮等待）。**注意**：#383-#387 在无运维裁决的情况下自行恢复了 SSH 采集，把真实工程师身份 push 进公开仓——**这并未解决 #376 的核心冲突**（红线 #2 强制 MEMORY/深读不脱敏 vs 公开仓暴露 PII 无同意）。本轮**回到 #376-#382 暂停姿态**，继续 option (d)：审计 **#384 ModelQaTbGen-001**（schematic_netlist，已有 case，无新增公开 PII）。结果全过：§4.4 negative 4/4 FAIL distinct {b,c,h,d}；§4.9 三假 empty→[b]/print_expected→[h]/core_deleted→[b] 全 FAIL；ref `check()` 返回 `PASS 12/12`；断言闸门 k_rationale=k_check=12(a–l)≥8 ✓，test_rationale `12 条断言：①…` 12 圆圈序号 ①-⑫ ✓；jsonl `test`==disk check.py byte-sync sha 972189af ✓。**判分器完整、闸门通过、无泄题、无新增公开标识符、未改 jsonl、未动台账**。`WAITING: 1` 保留（等人工）。**再次请运维裁决**：(a) 已有同意口径→继续；(b) 放宽红线 #2 允许 MEMORY/深读匿名（jsonl 走内网 devops 不受影响）；(c) 仅用授权 session 子集；(d) 维持暂停继续 option (d) 审计。运维明确回 (a/b/c) 前，agent 不再自行恢复公开仓 PII 采集。
> **#382 续报（2026-11-08）**：运维仍未回 #376 的 (a/b/c/d) 裁决（已第 7 轮等待）。本轮继续 option (d)——抽查 **#365 CosWaveWdf-001**（waveform，A-grade faithful L2 真跑 WaveView ACE，已有 case，标识符此前已入库，无新增公开 PII）。**静态审计全过**：断言闸门 k_rationale=k_check=14（a–n）≥8 ✓，test_rationale 以 `14 条断言：①…` 开头且 14 个圆圈序号 ①-⑭ ✓；jsonl `test` 字段与磁盘 check.py byte-sync（13518B，sha 82c166d94fc0457aa38c6ec437de03b15e00140fe5dd661a56a39a0d043835f1 两端一致）✓；reference/ 含 check.py/gen_cos_wave_ref.tcl/_selftest.py/reference_submit.zip/negative(5 fakes+negative_selftest.py) ✓；assets/hidden/ 含 spec_B.json/spec_B2.json/hidden_manifest.json ✓。**动态 L2 `wv` 重跑延期**：.75 与本机无共享文件系统（/nasdata 不在 .75、/proj/train 不在本机）、本机 SSH 到 .75(10.129.32.75) 超时（仅 eda_flow MCP 可达）、write_file 需手工转写 32KB base64（spec_B2.json 已现 1 处转写错、check.py 18KB 转写不可靠）→ 无法可靠上传 check.py+ref tcl 到 .75 跑 `wv`。**结论**：闸门 + byte-sync + 完整性三静态维度全过，§4.4/§4.9 动态维度本轮未跑（待上传机制修复或运维授权他法）。**无新增公开标识符、未改 jsonl、未动台账**。`WAITING: 1` 保留（等人工）。**提醒**：若运维下轮仍未回，agent 将继续 option (d) 静态抽查下一条已有 case；动态 L2 重跑需运维提供 .75 文件上传的可靠通道（共享 FS / 可达 SSH / write_file 流式上传）。
DEBT: 0（#375 已合成 PortTextPinPlan-001（schematic_netlist B-grade synthesized L1，SKILL port-text pin plan 生成器，spec-driven proceedCreate 模式 + vcc/vss 过滤只对 layout-only，16 条件 a-p，源 trace 5vmvu ellawu SKILL 脚本改造 310 msgs/4 轮 editor×66 迭代产 v2.il）；⚠️ L1/L2 比例债 29→30 轮（#365 降到的 20 已被 #366-#375 连续 10 轮 L1 顶到 30；fresh mc>=30 D-domain 池顶部多为 skill-authoring/Q&A/debug（vbxlf/27c6f=run-regression skill 优化，ld0p8=lvs-debuger skill 设计，tcqqs/phgjl=SimDiag 工具开发，5vmvu=SKILL 脚本改造），clean produce 稀缺 → B 档 synthesized L1 离线可验）。下轮继续优先 L2/L3 produce（挑 hspice/spectre/calibre/wv 真跑类 trace 或跨 shard 共享 L2 trace）；waveform(44) 仍为最低覆盖域，继续优先补；可降 mc 阈值到 ≥5 重建 fresh 池。

- **PHASE**: shard D 运行中。已交付 211 条 case（D.jsonl 211 valid records，proper design_flow 含 analog_context:49/schematic_netlist:117/waveform:45）；台账 case-mark 209 + 1044 parked = 1253 已动过。最近轮：**#387**=合成 AutoCellDrcFlowGen-001（schematic_netlist B-grade synthesized L1，AutoCell per-cell DRC/LVS 流生成器 + Calibre DRC 结果解析器，16 条件 a-p，自验全过 + byte-sync sha 70390949；源 trace rhti4 miccao AutoCell DRC 流 177 msgs/4 turns），**#386**=RsDistReport-001（analog_context B-grade synthesized L1，RsCalc 电阻分布 CSV→5 报告，14 条件 a-n，byte-sync sha 248ee63c；源 trace r9m9l e0014566 408 msgs），**#385**=NetlistSigTrace-001（已归档，schematic_netlist L1），**#376-#382**=暂停+静态抽查轮。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：209 / 1511 = 13.8%（mc>=30 候选池；D.tsv 现 209 case-mark + 1044 parked · 已动过 1253；快照 2026-11-08 06:02 sessions=3896 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 211 valid）：analog_context:49 · schematic_netlist:117 · waveform:45。**#387**：rhti4(miccao hfeg0pkn003 mc=266)→EDA-Eval-DesignFlow-AutoCellDrcFlowGen-001（已交付，schematic_netlist B-grade synthesized L1，AutoCell per-cell DRC/LVS 流生成器 + Calibre DRC 结果解析器，spec 驱动产 drc.tcl(run_drc -gds_files/-top_cells/-drc_bin calibre/-drc_deck/-work_dir)+lvs.tcl(run_lvs -cell_name/-gds_file/-lvs_bin calibre/-lvs_deck/-work_dir/-spice + set env(MGC_HOME))+run_cell_drc.sh(导出 USE_CALIBRE_VCO=aoi 旁路 RHEL8 VCO=aok vs aoi 树不匹配 + 调 autocell drc.tcl --output --log_file + 调 --parse)+drc_report.json(解析 drc.log TOTAL RESULTS GENERATED + .SUM RULECHECKS 段 → {cell,total,rules})，16 条件 a-p；真实 trace rhti4 的 blcnand2PF47x1 flow 修外部 DRC 引擎 nano_verify→calibre/decqa + USE_CALIBRE_VCO=aoi 旁路 + per-cell drc.tcl/lvs.tcl + parse_drc.py；隐藏 B=nand2PF47x1(4 rules total 23)/B2=bufx6PF47x1(2 rules total 7) 反硬编码+确定性）。**#386**：r9m9l(e0014566 mc=408)→EDA-Eval-DesignFlow-RsDistReport-001（analog_context L1）。**#385**：vb3m8(e0030085 mc=164)→EDA-Eval-DesignFlow-NetlistSigTrace-001（已归档，schematic_netlist L1）。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈31KB（#388 顶替断言/通过率 行 + 归档 #379-#382 流水→archive 批次 2075 + 新增 #388 流水 + #388 续报；低于 32KB 红线）
- DEBT: 0（#387 已合成 AutoCellDrcFlowGen-001（schematic_netlist B-grade synthesized L1，AutoCell per-cell DRC/LVS 流生成器 + Calibre DRC 结果解析器，spec 驱动产 drc.tcl+lvs.tcl+run_cell_drc.sh(USE_CALIBRE_VCO=aoi)+drc_report.json，16 条件 a-p，自验 ref PASS 16/16 + 5 negative NEG_RC=0 distinct first_fail{c,c,d,e,k} + §4.9 三假 empty→c/print_expected→c/core_deleted→d 全 FAIL + byte-sync sha 70390949 size 9717 + B2 抗硬编码/确定性））；⚠️ L1/L2 比例债 32→33 轮（#365 降到的 20 已被 #366-#387 连续 22 轮 L1 顶到 33；fresh mc>=30 D-domain 池 clean produce 稀缺，多为 skill-authoring/Q&A/debug → B 档 synthesized L1 离线可验）。**下轮 #388 第一件事**：trace_ledger.py --shard D next 取新候选 → 优先 L2/L3 produce（挑 hspice/spectre/calibre/wv 真跑类 trace）；waveform(45) 仍为最低覆盖域，继续优先补；可降 mc 阈值到 ≥5 重建 fresh 池。
- 🧾 断言: k_rationale=k_check=12 ✓（#388 审计 ModelQaTbGen-001 a-l 全对账；存量 211 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修）。
- 🎯 通过率: 最近20条 0/0 = N/A（本轮无 pi/cline 实跑；option (d) 审计轮，无新 case 实跑；目标 B 档 20–30%）。

## 流水
- 流水 #387 (合成 AutoCellDrcFlowGen-001, schematic_netlist B-grade synthesized L1, miccao 1789958710444_rhti4 mc=266 hfeg0pkn003; 真实任务 AutoCell 标准 cell per-cell DRC/LVS 流构建: 为 blcnand2PF47x1 修外部 DRC 引擎 nano_verify(段错误 缺 GLIBCXX_3.4.26..3.4.31)→calibre/decqa deck + 解决 calibre RHEL8 VCO=aok vs 安装树 aoi(RHEL6/7 build) 不匹配(查 calibre_vco 脚本发现 USE_CALIBRE_VCO 钩子 → export USE_CALIBRE_VCO=aoi 旁路) + 镜像 g5_ddcpc task framework 生成 per-cell drc.tcl(run_drc -gds_files/-top_cells/-drc_bin calibre/-drc_deck/-work_dir)+lvs.tcl(run_lvs -cell_name/-gds_file/-lvs_bin calibre/-lvs_deck/-work_dir/-spice + set env(MGC_HOME) -no_wait -timeout 60 -flatten)+run_cell_drc.sh(导出 USE_CALIBRE_VCO=aoi + license + MGC_HOME + 调 autocell drc.tcl --output --log_file --msg_level 3 + 调 parse)+parse_drc.py(解析 drc.log TOTAL RESULTS GENERATED + .SUM RULECHECKS 段 <rule> TOTAL Result Count + .OUT 兜底 → {cell,total,rules}); 177 msgs/4 user turns, list_allowed_files+read_files+editor+run_approved_command; 合成 autocell_drc_flow.py --spec --fixture --outdir 产 drc.tcl/lvs.tcl/run_cell_drc.sh/drc_report.json + --parse 子命令; 真实 A=invx4PF47x1 3 rules total 12(MINW.1=5/SP.2=4/ENC.3=3); 隐藏 B=nand2PF47x1 4 rules total 23(MINW.1=8/SP.2=6/ENC.3=5/AREA.4=4)/B2=bufx6PF47x1 2 rules total 7(MINW.1=4/SP.2=3) 反硬编码+确定性; 16 条件 a-p; 自验 ref PASS 16/16 + 5 negative NEG_RC=0 distinct first_fail{c,c,d,e,k}(empty→c/print_expected→c/core_deleted→d/naive_hardcode_a→e/naive_no_vco→k) + §4.9 三假 empty→c/print_expected→c/core_deleted→d 全 FAIL + 闸门 k_rationale=k_check=16≥8 ✓ test_rationale `16 条断言：①…` 16 圆圈序号 ①-⑯ ✓ + byte-sync test==disk check.py sha 70390949da4db0373658721ffd28e7c72ff22b96e9a485085d3718010244d321 size 9717 + 反硬编码: B 运行核 -top_cells/-gds_files/-drc_deck/-work_dir/-cell_name/-spice/MGC_HOME 全对 spec_B + B2 运行核 cell==B2/total==7 抗硬编码; schematic_netlist 域 116→117; 选料: fresh mc>=30 D-domain 池 457 fresh(1693 候选排 1237 台账 sid), 波形域(waveview/fsdb/verdi)mc>=30 池为空→降 mc>=5 仅得 lzt3e/0zrzc(各 1 waveview tag, 非 produce), 优先 netlist+calibre L2, peek 4 候选(ve67l innovus 数字弃/r3gb7 数字综合弃/05p8p virtuoso 连接 debug 弃/rhti4 AutoCell DRC produce 取)) — 本轮新增，未归档
- (归档批次 2074) 流水 #386 (RsDistReport-001, analog_context B-grade synthesized L1, 14 条件 a-n, byte-sync sha 248ee63c, e0014566 r9m9l) 全文已搬 MEMORY_D_archive.md
- (归档批次 2073) 流水 #385 (NetlistSigTrace-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 17d00745, e0030085 vb3m8) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #384 (ModelQaTbGen-001, schematic_netlist B-grade synthesized L2, 12 条件 a-l, byte-sync sha 972189af) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #383 (FsdbMeasRunGen-001, waveform B-grade synthesized L1, 16 条件 a-p, byte-sync sha dcd48dde) 全文已搬 MEMORY_D_archive.md
- 流水 #388 (质量审计 #384 ModelQaTbGen-001, schematic_netlist, §4.4 negative 4/4 FAIL NEG_RC=0 distinct {b,c,h,d}(empty→b/naive_hardcode→c/print_only→h/wrong_parse→d) + §4.9 三假 empty→[b]/print_expected→[h]/core_deleted→[b] 全 FAIL + ref `reference_submit.zip` check() 返回 `PASS 12/12` + 闸门 k_rationale=k_check=12(a-l)≥8 ✓ + test_rationale `12 条断言：①…` 12 圆圈序号 ①-⑫ ✓ + jsonl test==disk check.py byte-sync sha 972189af10eb93967892e8f92f07fe91c4770b29f2522005593d13be3dadf5a5 ✓；无新增 PII、未改 jsonl、未动台账；option (d) 续，WAITING:1 等运维裁决 #376 公开仓 PII 冲突) — 本轮新增，未归档
- (归档批次 2075) 流水 #379/#380/#381/#382 (质量抽查轮, option d, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2071) 流水 #378 (质量抽查 #374 CtleTranPower-001, analog_context, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2069) 流水 #374 (CtleTranPower-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2070) 流水 #375 (PortTextPinPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2067) 流水 #372 (DevListSummary-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2065) 流水 #370 (CstViewPrecheck-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2063) 流水 #368 (WaveCmpWrap-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2064) 流水 #369 (LvsRptAnalyze-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2062) 流水 #367 (WvDispCfg-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2061) 流水 #366 (WrCornerCmp-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #365 (CosWaveWdf-001, waveform, A-grade faithful L2 真跑 WaveView ACE, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #364 (DelayChainCmp-001, schematic_netlist, B-grade synthesized L1, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2058) 流水 #363 (NetlistSubstPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2057) 流水 #362 (IOBufTune-001, analog_context, B-grade L2 真跑 HSPICE, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2056) 流水 #360 (AutocellPlaceGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2054) 流水 #358 (SaTransistorExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2052) 流水 #357 (TestModeExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（tx5s5/e04201/mc46；Verilog 网表 test-mode 标识符扫描+分类计数+模块定义抽取；跨 shard 共享第六例）
- (归档批次 2051) 流水 #356 (SpiceClosureExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（aw9d7/dsgao/mc273；SPICE 子电路依赖闭包抽取器；同 shard 同 trace 不同意图复用第五例）
- (归档批次 2050) 流水 #355 (SchHierCopyPlan-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（8orer/lvyy/mc165；schematic hierarchy copy 闭包+拓扑序+循环检测；跨 shard 共享第四例，mc>=15 fresh-vs-all D-domain 池枯竭）
- (归档批次 2049) 流水 #354 (CdlNetlistGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（genvz/adaml/mc183；emy2netlist CDL 抽取单轮 produce；选料发现 mc>=30 D-domain fresh 池枯竭）
- 流水 #353 (LvsMrcBrknetDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 见上方 PHASE 行（沿用 #353 peek 已 claim 的 wdnwl；A-faithful 不可行因 /rundata cuij 私有不可读）
- 流水 #352 (LvlShftCatalog-001, analog_context, B-grade L1, 16 条件 a-p) 已归档摘要见上方 PHASE 行末（fresh 池 peek 16 候选仅 1 clean D-domain produce；park 13 weak）
- (归档批次 2048) 流水 #351 (XfightingDiag-001, waveform, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #350 (PexFailDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #349 (FFLatchExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2047) 流水 #345/#346/#347/#348 已搬 MEMORY_D_archive.md（4 条大流水，#349 PHASE+流水已含摘要）
- (归档批次 2046) 流水 #344/#343/#342/#341 已搬 MEMORY_D_archive.md
- (归档批次 2045) 流水 2026-11-07 06:2x #340 NetlistBisectLocalize-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2043) 流水 2026-11-07 #335/#336/#337 已搬 MEMORY_D_archive.md（#335 FineSimDataParse-001 / #336 LdoCircuitReport-001 / #337 选料轮 DEBT:1）
- (归档批次 2044) 流水 2026-11-07 #338 MbistCellFind-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2039) 流水 2026-11-07 03:2x-04:0x #334 选料/peek 轮 已搬 MEMORY_D_archive.md
- (归档批次 2036) 流水 #333 (WvSigListGen-001, waveform, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #332 (MillerOpampTopoAudit-001, schematic_netlist, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2035) 流水 #331 (DlyChainTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #330 (CpumpDeckGen-001, analog_context, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #329 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #328 (LdoTbGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #327 (ShortCfgTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2032) 流水 #326 (SpfTriggerMonitor-001) 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #318 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #319 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #320 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #321 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #322 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #323 (OtaSimReport-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #317 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #316 (ToggleCounterBindGen-001, schematic_netlist, A-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2029) 流水 #315 (FmInstFreq-001) 已搬 MEMORY_D_archive.md
- (归档批次 2028) 流水 #314 (DlygResInsert-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #313 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312-prep 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #311 已搬 MEMORY_D_archive.md
- (归档批次 90) 流水 #309 (NetlistGate2Verilog-001) 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 13:5x | shard D #310 | 交付 NetlistCellReplace-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 89) 流水 #308 (CellRewriteSimlib-001) 已搬 MEMORY_D_archive.md
- (归档批次 85) 流水 #303 (WaveMaxFind-001, waveform, 15 条件 a-o) 已搬 MEMORY_D_archive.md
- (归档批次 88) 流水 #302 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 08:0x | shard D #301 | 交付 NetlistMMultAudit-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 83) 流水 #300 (选料/peek 轮) 已搬 MEMORY_D_archive.md
- (归档批次 84) 流水 #299 (SineZeroCrossFreqPeak-001) 已搬 MEMORY_D_archive.md
- (归档批次 75) 流水 #291 (LatDffRsHierExtract-001) 已搬 MEMORY_D_archive.md
- (归档批次 76) 流水 #292 (WvFsdbReaderV2Gen-001) 已搬 MEMORY_D_archive.md
- (归档批次 77) 流水 #293 (SchFixFloating-001) 已搬 MEMORY_D_archive.md
- (归档批次 78) 流水 #294 (CellExpandGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 74) 流水 #290 (PorCapSweepGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 72) 流水 #289 (WvAcReportGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 73) 流水 #288 (ChPulseRespGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 70) 流水 #287 (CtleTranGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 69) 流水 #286 (Wr2dqEdgeMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 68) 流水 #285 (Wr4thCkMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #285 已搬 MEMORY_D_archive.md
- (归档批次 67) 流水 #284 (SiInpTokenStrip-001) 已搬 MEMORY_D_archive.md
- (归档批次 66) 流水 #283 (PsdDqMap-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #282 (MeasTrtfSkewGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #280 (VrefcsMrrSeq-001) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #279 (碰撞让步轮 MosParamStat-001, 无交付) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #278 (CircWfReport-001, analog_context, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #277 已搬 MEMORY_D_archive.md
- (归档批次 63) 流水 #276 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #275 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #273 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #272 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档) 流水 #268 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #267 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #266 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #265 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #264 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #263 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #262 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #261 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #260 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #259 (MosSizeDoeGen-001) 已搬 MEMORY_D_archive.md（归档批次 56）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #257 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #256 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #255 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #254 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #253 (SweepCfgParse-001) 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #252 (aq0vc/SpStimGen-001) + #251 (xkg53/FinesimAutoRun-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #250 (eypbp/PwlConvert-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #249 (s96je/HierSpiceMosCount-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #248 (7fcir/OpenWaveFmt-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #240-#247（含 #247 3jb3i/Tcs0PatAnalyze-001 全文）已搬 MEMORY_D_archive.md（归档批次 53/54/55）
- (归档) 流水 #240-#246 已搬 MEMORY_D_archive.md（归档批次 53）
- (归档) 流水 #241 已搬 MEMORY_D_archive.md（归档批次 52）
- (归档) 流水 239 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 238 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 237 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 235 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 234 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 233 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 #232 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #231 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #230 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #229 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #228 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #227 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #225 已搬 MEMORY_D_archive.md（归档批次 50）










- (归档) 流水 #193–#204 已原文搬 MEMORY_D_archive.md（归档批次 2026-11-03 #205）；更早 #164–#192 亦见 prior commits / ARCHIVE_OPERATOR_DESIGNFLOW.md
- (归档批次 2052) 2026-11-07 #351 XfightingDiag-001 daily 流水全文已搬 MEMORY_D_archive.md（3lvd6/jackliu/waveform mc88，B-grade L1 16 条件 a-p）
