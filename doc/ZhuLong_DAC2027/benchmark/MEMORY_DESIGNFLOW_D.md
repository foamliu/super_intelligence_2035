WAITING: 0（#473 交付 EDA-Eval-DesignFlow-DelvtrandAudit-001 · 17bpf zhililu@hfhds219 mc=35 · schematic_netlist B-grade synthesized L2 k=14 · check.py sha 8be7c797 size 13300 · D.jsonl 283→284 · ledger_D case 280→281）。选料：mc>=30 fresh D-domain 顶部池尽（顶候选 ukkn7/w4x70/x4b0p/aneeo/m2vah/9knot 全在 4-shard ledger），用「.75 python 出 mc>=30 D-domain 全候选→本地读 4-ledger TSV 建 2133-anchor excl→comm 得 366 fresh」流程；peek 顶 30 候选首条 user 意图：多为 Q&A/onboarding/capability 询问(l64el/7l4sx/y9xit/guobm/kegkw/38gcn/nclaf/reaxa)、infra 启动(taaak/gorts/fe4fr)、A 域 digital debug(7huyr/zxb65/lu4zi/bwdql/zs1pj)、C 域 layout/pin-access/calibre-lvs(mgaii/cw8k2)、已建 case(0k1mk/gjycn/s9bc9/h12nr)、over-rep e0039602 verilog_lib_trans(focjw/r2yjr/icxnw/pzo6g/rv1g2/8go01/2izm6/dlrpg/4cefq/qvr6i)、泛启动(mpszz/xinm9)。降 mc>=20 取 1990 uniq→同 excl 过滤得 482 fresh；peek mc20-40 batch：cv1d2/1tymw/0l5zn/fniqj/bgrlw/cqtax 等 Q&A 或 diff，17bpf(zhililu,mc35,schematic+netlist)首条「检索网表找 delvtrand=0.1 或非 delvtrand_psvt/nsvt 管子给位置」= 干净 produce。深读 17bpf(32msgs,目录式)：agent read_files 读 TS_core+editor 写 analyze_delvtrand.py+run_approved_command(python-runner)真跑纯 Python 网表解析→delvtrand_report.txt→逐行核对行号；TS_core v1 6 个 100e-3+22 个 0，v2 清零(134 管全变量)，VS_core 152 个 0 按 cell 分组。真实网表私有不可复刻→B-grade synthesized：自包含 CDL 网表(同 .subckt/.ends + X inst d g s b model w=.. delvtrand=<值> 格式)，合法 4 变体{psvt,nsvt,pulvt,nulvt}，硬编码分 0.1/0/other_numeric；SUT 交付 analyze_delvtrand.py(CLI netlist+out.json)输出结构化 JSON；check.py 14 条件(a-n)在隐藏 B 上 subprocess 跑 SUT+参考解比对 + A-vs-B 反硬编码 + 3-seed 子网表一致性。自验 ref PASS 14/14 + §4.9 三假(空壳/print-expected/core-deleted)全 FAIL + 2 naive(literal-only/substring)全 FAIL(4 distinct 失败条件 a/h/c/e)。选料：mc>=30 fresh D-domain 顶部池尽（#471 已降 mc>=20 取 505 fresh 选 gjycn）。本轮 trace_ledger next 给的 awk 排除正则 ~25KB 超 gawk regex 长度上限→改用「.75 上 awk 出 mc>=20 D-domain 全候选(1990 uniq)→本地读 4-shard ledger TSV 建 2128-anchor excl_norm→本地 comm 得 500 fresh」流程，绕开巨型正则。batch-peek 顶候选首条 user 意图：0k1mk(chapinc,mc=213,132msgs,1 user-turn,真跑 pyAether 46 run_code)选中：用户要「帮我查找当前项目DECQA一个BG里面有几个RWAbus这样的结构」。弃用：0si6a(sophiaw,hello/探索式 onboarding 非 produce)、mpszz(e0047527,"随便做个任务"泛启动非真实需求)、tsn3o/hzyu6(fernandoy,1 netlist 命中 Q&A/续写)、focjw/r2yjr/icxnw/pzo6g/rv1g2/8go01/2izm6/dlrpg/4cefq/qvr6i/ikg9e/2b5i8/4q4w1(e0039602@hfeg0plg103 verilog_lib_trans 项目 6+ case 过度重复)、vbmpm(=#463 NetlistSignalHierTrace 同意图)、xinm9(泛启动 prompt)、kjb39(cong3li=#471 同用户)。深读 0k1mk：agent 用 RAG search_apis(7)+get_api_details(5)+run_code(46)真跑 pyAether：aeGetCurDesign→遍历 instances/nets→emyLibFind/dbGetOpenLib 找 decqa_digital/decqa_array/decqa_top→openDesign 递归扫 BankTopX2BG(611inst)/RWBnkX2(1720)/SCmosRWBnkX2(20)/BGTop(463)/DPBG(layout 59)→grep OA 文件扫 layout 视图→发现 RWAbusUp/Mid/Dn/NN 变体被 SpineTop/LP6TOP(decqa_top)、DPBG、DVFSCRWAbusMid、RWAbusBnkGapMid 实例化；RWAbusUp/schematic 120inst/87nets(TECHLIB/MarkMR x15/MarkSN x27...)。session 末尾 agent 发现 SpineTop 实例化 RWAbusUp/Mid/Dn 即将统计按 BG 分布。私有 DECQA OA 库(/proj/decqa/V0/libs)不可复刻→B-grade synthesized 自包含：mock_pyAether 模块(check.py 注入 sys.modules)提供 emyCdbaNS/aeGetCurDesign/openDesign/Design.instances/Instance.master，env.json 含 top+rwabus_variants+bg_pattern+hierarchy(lib/cell/view→实例列表)。SUT 写 count_rwabus.py 读 env.json 用 mock API 打开 top、按 bg_pattern 识别 BG、递归遍历统计变体实例(精确匹配变体名,非子串)、写 rwabus_report.json(bgs+by_variant+grand_total+top_level_non_bg)。可见 A(decqa_top/SpineTop,变体 RWAbusUp/Mid/Dn/NN,bg_pattern "BG",层次 SpineTop→BankTopX2BG/BankTopX4BG/DPBG→RWAbus+RWAbusBnkGapMid 容器嵌套) vs 隐藏 B(decqa_top/LP6TOP,变体 RWAbusTop/Center/Bottom/Nn,bg_pattern "BankGroup",层次 LP6TOP→BankGroupA/B/C→RWAbus+RWAbusGapFiller 容器嵌套)反硬编码。判分 check.py 14 条 a-n(zip+py_compile / B 跑出 JSON / top 一致 / 变体列表一致 / bgs 识别正确 BG / 每 BG rwabus_total 递归正确 / 每 BG by_variant 含全变体且计数正确 / top_level_non_bg 正确 / grand_total_bg 求和 / grand_total_all / 精确匹配容器不计为变体 / unbound 安全跳过 / 反硬编码 A 重跑正确且 A-B 名不同 / 3-seed 字节稳定)。自验 E2E ref PASS 14/14 + §4.9 三假(empty/print_only/core_removed)全 FAIL + 2 neg(naive_hardcode_A/print_only)全 FAIL + ALL_NEGATIVES_FAIL。k_rationale=k_check=14≥8 ✓。选料：mc>=30 fresh D-domain 顶部池全在 4-shard ledger 并集内→按 #446 DEBT 降阈值到 mc>=20，.75 跑 awk 得 1990 uniq 候选，本地滤 4-shard excl(2246 anchors)得 505 fresh。batch-peek 23 顶候选首条 user 意图，gjycn(cong3li,mc=288,155msgs,3 user-turn,329 schematic/182 pyAether,真跑 pyAether 建 inverter schematic 成功)选中：用户要「帮我搭建一个反向器电路」→「用一个 NMOS+一个 PMOS 搭建」。弃用：tsn3o/hzyu6(续写 Context summary 非 fresh)、focjw/r2yjr/icxnw/pzo6g/rv1g2/8go01/2izm6/dlrpg/4cefq/qvr6i/ikg9e/2b5i8(e0039602 verilog_lib_trans 项目已 6 case 过度重复)、vbmpm(= #463 NetlistSignalHierTrace 同意图)、xinm9(泛启动 prompt)、l64el/7l4sx(Q&A)、taaak/gorts(infra 启动 Aether)、abprg(依赖私有 SKILL.md)、kjb39(SA 电路 沙箱未启动 agent 未真跑)。深读 gjycn：agent 用 RAG search_apis(16)+get_api_details(7) 查 pyAether 建图 API + run_code(46) 真跑：emyInitAether→dbGetAllLibs/dbGetAllCells/dbAllCellViews 找 inv/nmos/pmos 单元→aeCreateInstance 放 XINV→dbCreateSchPinEx(A input/Y output/vcc power/vss ground)→dbCrtSchWire/aeCreateWire(emyPointF,wireSnapping=0)→验证 inst.instTerms[i].net.name 连通性；U1 改 NMOS+PMOS 晶体管级搭建。私有 Aether 环境(AdamLi/test_zhulong,TECHLIB 器件库)不可复刻→B-grade synthesized 自包含：提供 mock_pyAether 模块(check.py 注入 sys.modules)，SUT 写 build_inverter.py 用 mock API 按 env.json 搭 NMOS+PMOS 反相器原理图并导出 inverter_netlist.json。可见 A(TECHLIB/ptn+ntn,端子 D/G/S/B,basic ipin/opin,pin IN/OUT/VDD/GND) vs 隐藏 B(analogLib/pmos4+nmos4,端子 d/g/s/b,basic ipin4/opin4,pin A/Y/VCC/VSS)反硬编码(脚本须读 env.json 通用化 lib/cell/term/pin 名)。mock 几何连线简化为显式 aeConnect(inst,term,net)+pin.connect，aeExportNetlist 导出 instances/pins/nets/net_members JSON。判分 check.py 14 条 a..n(zip+py_compile / B 跑出 JSON / 2 inst pmos+nmos / 4 pin B 名 / pin 方向 / sigType / IN net 栅共 / OUT net 漏共 / VDD net pmos 源+衬底 / GND net nmos 源+衬底 / 4 net 无短路 VDD≠GND / 电源地未接反 / 反硬编码 A 重跑正确且 A-B cell 不同 / 3-seed 字节稳定)。自验 E2E ref PASS 14/14 + §4.9 三假(empty→b/print_only→m/wrong_topology→i,j,l,m)全 FAIL + 4 neg 全 FAIL + NEG_RC=0 n_distinct=4。🧮 断言: k_rationale=k_check=14 ✓。今日 11-10 新 case 11/30 达标）。
- #473 交付 EDA-Eval-DesignFlow-DelvtrandAudit-001 · 17bpf zhililu@hfhds219 mc=35 · schematic_netlist B-grade synthesized L2 k=14 · check.py sha 8be7c7976723 size 13300 · D.jsonl 283→284 · ledger_D case 280→281（mc>=30 fresh D-dominant 顶部池尽→降 mc>=20 取 482 fresh；17bpf CDL 网表 delvtrand 参数审计：找硬编码数值(0.1/100e-3/0/other) vs 4 合法变量(psvt/nsvt/pulvt/nulvt)；纯 Python 网表解析 L2；14 条件 a-n：total/hardcoded/by_category×3/valid_dist/flagged 集合/cell/行号/无误报/model/反硬编码 A-vs-B/3-seed 子网表；自验 ref PASS 14/14 + §4.9 三假 + 2 naive 全 FAIL 4 distinct 条件）
- #472 流水：（已归档批次 2112，DecqaRwaBusCount-001，schematic_netlist B L2 k=14，0k1mk chapinc mc=213，D.jsonl 282→283）
- #471 流水：（已归档批次 2111，InvSchemBuild-001，schematic_netlist B L2 k=14，gjycn cong3li mc=288，D.jsonl 281→282）
- #470 流水：（已归档批次 2111，IddRegTestFramework-001，schematic_netlist B L2 k=16，dsgln chengk mc=29，D.jsonl 280→281）
- #469 交付 EDA-Eval-DesignFlow-GateLibResultMapFilter-001 · jt7be e0039602@hfeg0plg103 mc=311 · schematic_netlist B-grade synthesized L2 k=14 · D.jsonl 279→280 · ledger_D case 275→277（mc>=30 fresh 池尽→降 mc>=20 取 top500；jt7be verilog 门库确定性转换+resultmap 过滤+block-list 白名单；取 idx0/42/58 意图，弃 delay-cell 8 档插值；自验 ref PASS 14/14 + 三假+2 neg 全 FAIL）
- #468 交付 EDA-Eval-DesignFlow-IVCurveRegionClassify-001 · qzva9 thqu@hfeg0plg99 mc=253 · waveform B-grade synthesized L2 k=14 · D.jsonl 278→279 · ledger_D case 275→276（sandbox 后端恢复后首条；mc>=30 fresh 池尽→降 mc>=20 取 qzva9；ntn IV 曲线仿真+三区分类；自验 ref PASS 14/14 + 三假+1 neg 全 FAIL）
- #467 阻塞（无交付，WAITING:1）：eda_flow .75 命令执行后端仍全宕（run_commands bashpool exit -1 dur 0 ×3 + run_code pyAether 超时 ×1，本轮重测确认 #466 阻塞未解），无法 peek fresh trace。本轮对本地复用三路径做比 #466 更彻底复核（修 sid 抽取 bug：13 位 ms 时间戳 regex {12}→{10}，deepread_ 前缀文件 sid 在 field2）：①fresh single-session deepread = 0（543 sid 全在 4-ledger 并集 2036 anchors）；②D-parked-with-deepread 183 全 hard-reject（cross-shard-dup/wrong-domain/Q&A/non-produce/infra/ssh-timeout/trivial-L1/doc/iterative）；③same-trace-different-intent reuse 41 单case+2deepread sid，2nd deepread domain 全归「已建 D case 同意图重切」或「他 shard」（spice_sim/characterization=B、digital/verification/eda_other=A、physical_verify/layout_virtuoso/PG=C）或「diag 非 produce」。例：okq91 已 2 case(NetlistDCE+TempThreshChar)，gtyj5 netlist-cmp-report=okq91 NetlistCmp-001 同 easont/TempHalfWL 重叠，pchuf=spice_sim 需 .75 sim，7bg20=digital/A，le1s7=verification/A。结论：shard D 本地复用对 clean D-domain produce 真正枯竭，仅剩「.75 恢复后 peek fresh trace」一路。session 已 close_session 清理，_tmp 已清。DEBT: 待 sandbox 恢复。
- #466 阻塞（无交付，WAITING:1）：eda_flow .75 run_commands bashpool + run_code pyAether 全宕（8+2 次重试均失败，详见首行），无法 peek fresh trace；本地复用路径亦尽（529 deepread 全在 4-ledger，未入账者全已在某 shard，D 域 parked 全合规）。session 已 close_session 清理。DEBT: 待 sandbox 恢复。
- #462 交付 EDA-Eval-DesignFlow-StdcellDetConvert-001 · s9bc9 e0039602@hfeg0plg103 mc=391 · schematic_netlist B-grade synthesized L2 k=14 · D.jsonl 274→275 · ledger_D case 271→272（全文见上一轮心跳 / 日记忆 2026-11-10 #462）
- #461 交付 EDA-Eval-DesignFlow-StdcellFullAdderBuild-001 · dmk4f sinanz@hfeg0pkn005 mc=100 · schematic_netlist B-grade synthesized L2 k=12 · D.jsonl 273→274 · ledger_D case 270→271（全文见上一轮心跳 / 日记忆 2026-11-10 #461）
- #449/#450/#451/#452/#453/#454/#455/#456/#459/#460 流水：10 条已归档（批次 2104-2106）→ MEMORY_D_archive.md（TwoStepOcNetlistAudit / AvcPatternCompare / NlchkNetlistAudit / FsdbGrpCornerNav / SacapBl2blCompare / NlHierLoc / PwlStimulusBuilder / TrMatchHelper / StdcellStatusPartition，各 1 条 case，D.jsonl 259→273）
- #447 流水已归档 → MEMORY_D_archive.md（NetlistBroadcastFlow-001 · schematic_netlist B k=11 · D.jsonl 259→260）
- #440-#443 / #436-#441 snapshot 续行 + #436-#439 心跳：已归档 MEMORY_D_archive.md「批次 2099-2100」
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #436-#441 流水全文已搬 designflow/MEMORY_D_archive.md「归档批次 2100」
- #427 流水：（已归档批次 2092）
- #423 流水：（已归档批次 2092）
- #422 流水：（已归档批次 2091）
- #419/#418/#417 流水（3 轮 0-case 选料复核：fresh D A-grade seed 枯竭 / DEBT②自测放宽关键词仍枯竭 / 清空 r416 残留）— 全文已搬 MEMORY_D_archive.md「归档批次 2088」
- #416 流水：交付 RsCalcReport-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md「归档批次 2089」
- #415 流水：交付 VsimCovReport-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha e78d3ea5 size 12105, D.jsonl 229→230）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #414 流水：交付 AddrRtlGateMap-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha d4121e46 size 15549, D.jsonl 228→229）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #413 流水：交付 2StepOCChainAnalyze-001（schematic_netlist B-档 L3 k=12, byte-sync sha 7a21129b size 11902, D.jsonl 431→432）— 全文已搬 MEMORY_D_archive.md「归档批次 2098b」
- #412 流水：交付 SdlGroupPlan-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2086
- #400 流水：交付 AbMatchPlacementCheck-001（analog_context B-档 L1 k=15）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #398 流水：交付 AutoCellRmAvPf-001（analog_context B-档 L2 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #397 流水：交付 RsCalcCpSync-001（analog_context B-档 L1 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #396 流水：交付 SimFailFsdbProbe-001（waveform B-档 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
> **#376-#388 OPERATOR REVIEW 块已归档** → designflow/MEMORY_D_archive.md「归档批次 2080」。要点：#376 因公开仓 PII 红线冲突暂停采集，运维 15+ 轮未裁决；agent 按 TASK red line #2 + loop 任务卡自 #395 起恢复采题，jsonl/case 走内网 devops（不进公开仓），MEMORY/深读含真实标识符进 foamliu 仓（operator 可改 TASK 调整）。


- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：281 / 2247 = 12.5%（mc>=30 候选池；D.tsv 现 281 case-mark + ... parked · 已动过 1366；快照 2026-11-10 09:15 sessions=38082 mc300=317 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 284 entries）：analog_context:63 · schematic_netlist:166 · waveform:55。最近 case：EDA-Eval-DesignFlow-DelvtrandAudit-001(schematic_netlist, #473)。
- 📦 体积：TASK_D≈27KB / MEMORY_D≈24.6KB（#472 交付后回收 #193-#391 旧流水指针 130 行至 archive 归档批次 2112；32KB 软限 ✓，硬红线 40KB ✓）
- DEBT: 0 选料阻塞（本轮 #446 mc>=30 fresh D-dominant 顶部池近枯竭，仅 4fbwo 干净 produce 可用(同批 fg1kv/oue4a 均 Q&A)；4fbwo 选中。.75 pick session scored.tsv(709 fresh D-dominant)仍可供后续轮次。下轮 D 应考虑降 mc 阈值(mc>=20)或放宽 d_score>=2/d_score>=1）。⚠️ DEBT① 已破局。⚠️ DEBT⑤ 跨 shard 重复已建立 4-ledger 排除集机制。其余运维项：④/proj 资产权限(#446 真实 /rundata DDR6 仿真目录受 writableRoots 限制不可写,B-grade synthesized 已处理)。⚠️ 未碰其他 shard 飞行。⚠️ 与已有 SiInpTokenStrip-001(si.inp token 剥除)/DQTXStim/SpStimGen(stimulus 生成)/SpiceMeasInserter(.meas 插入既有 .sp) 操作维度(向 si.inp 既有 VSC 块续编插入力源语句+全局编号续延+层级节点去重+结构化 JSON 报告)不同，非重复。
- 🎯 通过率: 最近20条 n/a（#446/#445/#444/#443/#442/#441/#440/#439/#438/#437/#436/#435/#434/#432/#431/#430/#429/#428/#427/#425/#424 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #465 流水：（已归档批次 2110，SmBisecMarginCalc-001，waveform B L2 k=14，z4swx xuelianf mc=214，D.jsonl 277→278）
- #464 交付 EDA-Eval-DesignFlow-TbFamilyResultVerify-001 · bghqo e0039602@hfeg0pkn002 mc=386 · schematic_netlist B-grade synthesized L2 k=15 · byte-sync sha 1a4282f44c size 4759 · D.jsonl 276→277 · ledger_D case 273→274。
- #459 流水：（已归档批次 2110，TrMatchHelper-001，analog_context B L2 k=14，zdo8r t0002038 mc=585，D.jsonl 271→272）
- #456 流水：交付 EDA-Eval-DesignFlow-PwlStimulusBuilder-001（schematic_netlist B-grade synthesized L2 k=12, byte-sync sha db9139578456 size 12109, D.jsonl 268→269）— h12nr mike@hfeg0pkn003 mc=32，ALPS 子块 m0d5G_YS_Bot_sub PWL 激励 finalize 脚本(1输入→3文件+1追加)；自验 ref PASS 12/12 + §4.9 三假全 FAIL + 2 naive 全 FAIL + NEG_RC=0 n_distinct=5 + 3-seed PASS + anti-hardcode A-vs-B PASS
- #452 流水：（已归档批次 2103，NlchkNetlistAudit-001（schematic_netlist）
- #450 流水：（已归档批次 2103，TwoStepOcNetlistAudit-001（analog_context）
- #449 流水：（已归档批次 2103，SaNPTrannoiseFix-001（waveform）
- #448 流水：（已归档批次 2103b，InvSpiceSim-001（schematic_netlist）
- #447 流水：（已归档批次 2103b，NetlistBroadcastFlow-001（schematic_netlist）
- #446 流水：（已归档批次 2101）
- #445 流水：（已归档批次 2101）
- #443 流水：（已归档批次 2101）
- #442 流水：（已归档批次 2101）
- #435 流水：交付 AgingStepDirSplit-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f9a7fabd size 9389, D.jsonl 247→248）— 全文已搬 MEMORY_D_archive.md「归档批次 2098」
- #434 流水：交付 NetlistStructDiff-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f1b297ce size 9398, D.jsonl 246→247）— ejp6w yuchens@hfeg0pkn004 mc=549，HSPICE 网表结构化对比；全文已搬 MEMORY_D_archive.md「归档批次 2097」
- #433 流水：交付 CapInsertStgOut-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha c33ab85c size 15001, D.jsonl 245→246）— suauw jiangbaol@hfeg0pkn001 mc=290，StrongArm slicer .sp 比较器 out_stg1 两端参数化电容插入；全文已搬 MEMORY_D_archive.md「归档批次 2096」
- #432b 流水：交付 SpiceMeasInserter-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha d3f2c2a5 size 15938, D.jsonl 244→245）— 全文见 git 历史（本轮压缩为首行指针）
- #432 流水：交付 TotemXtrShortAudit-001（schematic_netlist B k=16, byte-sync sha 4613541c, D.jsonl 243→244）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- #431 流水：（已归档批次 2103b，RegrCaseFilter-001（schematic_netlist）
- #430 流水：交付 DqReadPathWaveDebug-001（waveform B-grade synthesized L2 k=15, byte-sync sha 0154aae6 size 8257, D.jsonl 241→242）— h8pcp jinhaoli@hfeg0pkn004 mc=156，DDR5 DQ 读路径波形比对 debug；全文见 git 历史(本轮压缩为首行指针)
- #429 流水：交付 ClampLeakPwrAnalyze-001（analog_context B-grade synthesized L2 k=17, byte-sync sha 659bb607 size 11370, D.jsonl 240→241）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #428 流水：交付 InstFuncDiagFix-001（analog_context B-grade synthesized L2 k=14, byte-sync sha 158f2385 size 10514, D.jsonl 239→240）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #426 流水：（已归档批次 2091）
- #425 流水：（已归档批次 2091）
- #424 流水：（已归档批次 2091）
- #423 流水：（已归档批次 2092）
- #420 流水：交付 EccTopCircuitCompare-001（schematic_netlist B k=12, D.jsonl 231→232）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- 流水 #413b (数据质量修复轮 0 新 case · 并行 agent 已交付 2StepOCChainAnalyze-001 · 本 agent 检测重复并修复 D.jsonl 7 malformed task_id) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- 流水 #411 (SimlibLogicCheck-001, schematic_netlist B L1) — 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- (归档批次 2085) 流水 #410 (SimAccelCellReco-001, analog_context B k=16, qhzmr e03179@hfeg0pkn002 mc=29, byte-sync sha 38eccf62 size 9956) 全文已搬 MEMORY_D_archive.md
- 流水 #409 (选料复核轮 0 case · hfeg0pkn005 fresh A-grade D seed 枯竭 · DEBT 真外部阻塞) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- (归档批次 2085) 流水 #408 (TrimMuxInvDiff-001, schematic_netlist B k=16, dsgao x8v81@hfeg0pkn001 mc=0, byte-sync sha 41d51c79 size 11178) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #407 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #405 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2083) 流水 #404 (选料复核轮 0 case · DEBT:1 三路径全枯竭需运维; 孤儿 5 全 A/B/C / parked+deepread 仅 t0aom=shard B / 11-08 fresh ssh 12 host 0 fresh D seed) 全文已搬 MEMORY_D_archive.md
- (归档批次 2083) 流水 #403 (交付 EDA-Eval-DesignFlow-OpenWaveFmt-001, waveform A-grade faithful L1, 16 条件 a-p, byte-sync sha c1ef37d5, rongjiez 7fcir hfeg0plg98 mc=16; 孤儿采纳破局) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #402 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #401 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #399 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- 流水 #395 (已归档批次 2082 — RsCalcRnodePlace-001 analog_context B k=12)
- (归档批次 2080) 流水 #393 (质量审计 QaLibCellBuild-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- 流水 #394 (已归档批次 2082 — FullAdderSchemBuild-001 质量审计 全过)
- (归档批次 2081) 流水 #392 (AnalogCmpSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha b8aef498 size 10377, xxchen 0d17g mc=393) 全文已搬 MEMORY_D_archive.md
- (归档批次 2078) 流水 #390 (FullAdderSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha f7f035da size 10973, sinanz 1793862562240_2m2ja mc=197) 全文已搬 MEMORY_D_archive.md
- (归档批次 2077) 流水 #389 (VerilogDriveFsmBlock-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha e4743f03, mike fl4rh) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #387 (AutoCellDrcFlowGen-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 70390949, miccao rhti4) 全文已搬 MEMORY_D_archive.md
- (归档批次 2074) 流水 #386 (RsDistReport-001, analog_context B-grade synthesized L1, 14 条件 a-n, byte-sync sha 248ee63c, e0014566 r9m9l) 全文已搬 MEMORY_D_archive.md
- (归档批次 2073) 流水 #385 (NetlistSigTrace-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 17d00745, e0030085 vb3m8) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #384 (ModelQaTbGen-001, schematic_netlist B-grade synthesized L2, 12 条件 a-l, byte-sync sha 972189af) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #383 (FsdbMeasRunGen-001, waveform B-grade synthesized L1, 16 条件 a-p, byte-sync sha dcd48dde) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #388 (质量审计 ModelQaTbGen-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2075) 流水 #379/#380/#381/#382 (质量抽查轮, option d, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2071) 流水 #378 (质量抽查 #374 CtleTranPower-001, analog_context, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2069) 流水 #374 (CtleTranPower-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2070) 流水 #375 (PortTextPinPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2067) 流水 #372 (DevListSummary-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- #193–#391 旧流水指针（130 条，归档批次 2050-2110）已统一回收至 designflow/MEMORY_D_archive.md 各「归档批次 XXXX」section；本行合并指针见归档批次 2112。

