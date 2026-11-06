WAITING: 0
SHARD: C (physical_layout)
DOMAINS: layout_aether, layout_virtuoso, pg_layout, physical_verify
round: 181
📊 trace 覆盖率：177/1511=11.7%（r181 交付 DrcPatternPlan-001 physical_verify；ledger 314:case 177·parked 137·claimed 0；jsonl C 176 行(43 well-formed+133 legacy)；mc30 池 target 1511；layout_aether 43·layout_virtuoso 40·pg_layout 24·physical_verify 67）
🎯 通过率: shard C 累计 176 case 已落 jsonl（pi/cline 实跑数见 cline_eval_status.jsonl，B 档目标 20–30%）
🧾 断言: k_rationale=k_check ✓（176/176 达标；r181 新增 15 条 ①–⑮）
📦 体积：TASK≈24KB / MEMORY_C≈30KB
🛠 DEBT: 0（r181 新交付无新债）


- **轮(181) 已交付 EDA-Eval-DesignFlow-DrcPatternPlan-001（physical_verify, A-档 faithful, L1-boundary）✓** —— trace=1790078216880_4g0i9（lizwen @ hfeg0pkn003, mc=241, 156 msgs; 用户「NW*产生pattern」用 pyAether 生成 DRC 测试版图 drc_pattern_gen.py）。**跨 shard 查重**: 合并 4 shard ledger 排除；.75 跑无排除 awk 取全候选 1480 行(mc>=30,shard C tools)→本地去重+排除 313 C-ledger→fresh 759，按域(physical_verify 616/layout_aether 96/layout_virtuoso 47)；选 4g0i9(lizwen NW* DRC testpattern 生成真跑 pyAether+calibre，单焦点 pattern 规划，physical_verify 域)。**用户原话逐字**: U1`NW*产生pattern`(纯需求 A-档 seed) + U5`read the prompt_flow.md and do the job`。**真实产物**: drc_pattern_gen.py(544 行 pyAether)读 test_deck_new + drc_rules_spec.json，fnmatch 查询→规则 spec→pattern_constraints.coordinates_hint→dbCrtRect 画 PASS/FAIL 版图。L2(live pyAether/Aether)被沙盒阻塞→**L1-boundary**：DRC 测试版图规划器 **drc_pattern_planner.py**(纯 stdlib json/re/os/sys/fnmatch/hashlib)：parse_test_deck→fnmatch 匹配→spec enrichen→parse_coords`(\\w+):\\s*\\((x1,y1,x2,y2)\\)`→resolve_layer(LAYER_SUB PERI→BORD/GATE→PG/DIF_ALL→AT4/PSUB→BORD;伪标签 Rect1/M1_rect1 回退规则首层;phys 表无则原样)→compute_spacing/extension/enclosure→plan JSON(query/cell_name 去通配符/matched_rules/rules[pass+fail rects[src_layer,draw_layer,bbox]+computed_geom_value+param_value]/pattern_count)。A(可见)=真实 test_deck 24 规则+spec 9 规则+layermap,query `NW*`→NW_S_014_00_c(spacing,NW,core,2.9,pass 2.95/fail 2.50)+NW_S_014_00_p(spacing,NW+PERI,peri,3.0,pass 3.05/fail 2.80);隐藏 B=同 deck/spec,query `M1_S_008*`→M1_S_008_00(M1,0.195,pass 0.20/fail 0.15)+M1_S_008_01(0.215);隐藏 B2=query `PG_EXT_031*`→PG_EXT_031_00_c/00_p(extension,GATE+DIF_ALL,0.296/0.195)。B 与 A 查询/层/规则类型/数值全不同。判分 **15 条 ①–⑮**(check.py 自包含:deck+spec+layermap 内联于 assets/hidden): ①(a)zip+py+plan_A ②(b)py_compile+stdlib 无 pyAether ③(c)plan_A matched==[NW_S_014_00_c,NW_S_014_00_p] ④(d)cell_name==NW ⑤(e)每规则 pass+fail≥2 rect ⑥(f)NW_c pass 2.95>2.9/fail 2.50<2.9 ⑦(g)NW_p pass 3.05>3.0/fail 2.80<3.0 ⑧(h)层解析 NW→NW/PERI 非 None ⑨(i)B(M1_S_008*)重跑 exit0+plan_B ⑩(j)plan_B matched==[M1_S_008_00,01] cell==M1_S_008 ⑪(k)M1_00 pass 0.20>0.195/fail 0.15<0.195 ⑫(l)M1 rect draw_layer==M1 ⑬(m)B2(PG_EXT_031*)matched==[PG_EXT_031_00_c,p] type extension ⑭(n)B2 GATE→PG/DIF_ALL→AT4 ⑮(o)反硬编码 plan_B 无 NW_S_014+sha256 一致+plan_B≠plan_A。ref PASS 15/15;5 negative(fake_empty→c/fake_print_expected→j/fake_core_deleted→c/naive_hardcode_a→j/naive_no_layer_resolve→n) NEG_RC=0;§4.9 三假全 FAIL;jsonl test 字段 sha 199350ec0a68==disk check.py ✓;k=15=①–⑮≥8 GATE PASS。详细见 designflow/trace_deepreads（4g0i9 inline）。

- **轮(180) 已交付 EDA-Eval-DesignFlow-WlAdjFind-001（layout_aether, A-档 faithful, L1-boundary）✓** —— trace=1793078082560_sax5x（miccao @ hfeg0plg36, mc=153, 165 msgs, ~1.2MB; 用户把 Virtuoso SKILL find_adjacent_wl.il 请求转 python、virtuoso API 改 aether API）。**跨 shard 查重**: 合并 4 shard ledger(1604 anchors)排除；.75 跑无排除 awk 取全候选 1480 行(mc>=30,shard C tools)→python 去重 935 +排除 1604→fresh 355，按域分类(physical_verify 95/layout_aether 102/layout_virtuoso 43/mixed 115)；layout_aether 42 是次低覆盖域，选 sax5x(miccao SKILL→aether 翻译单焦点，layout_aether 域)。**用户 2 轮原话逐字**: ①`/home/miccao/work/python/find_adjacent_wl.il 你能转成python格式么，virtuoso API改成aether API`(纯需求 A-档 seed) ②`我不小心把你的脚本弄丢了，帮我在生成一遍，名字带个后缀2`(同目标重表达)；agent 读 .il + RAG 查 aether API(dbShapeQueryEx/dbGetTrueOverlaps/goaLayer/dbResize/dbCopyFig/techFindLayer) + editor 写 find_adjacent_wl.py(302行)/find_adjacent_wl_2.py(281行)。**源 .il 算法**: wlFindAdjacent=按 WL label bbox 用 dbGetOverlaps 认领顶层 M1 shape→grown-bbox(±half) record sort by x1g→sweep i<j(rj.x1g>ri.x2g break;不同 net + grown x/y overlap)→wlShapeClose grow-and-AND 精确验证(grow 各 half→dbLayerAnd 非空⇔space≤thresh)→按 alphalessp 排序 netA/netB key→seen[key]++ 首个记 sample point(grown-overlap 区中点)→报告 netA\tnetB\tclose spots\tsample x\tsample y。WL 命名 sec<S>m<M>wl[oe]<B>,pattern ^sec[0-9]+m[0-9]+wl[oe]<[0-9]+$([oe]小写,`<`字面无`>`),thresh 0.182。**源 .il 笔误**: sweep y-check `nth(3 j)` 应为 `nth(3 rj)`→按文档化方法的意图逻辑修正。L2(live Virtuoso/Aether+OA)被沙盒阻塞→**L1-boundary**：相邻 wordline 查找算法纯 python 移植 **wl_adjacent_find.py**(纯 stdlib json/re/sys)：读 layout JSON→claim-by-label→grown-bbox record sort→sweep+grow-and-intersect 精确验证→去重计数+首个 sample→报告。A(可见)=Array16G_T_wlA 水平 WL runs,thresh 0.182,6 nets/9 shapes(含 1 decoy 无 label),3 相邻对(sec0m0wle<0|sec0m0wlo<0 2 close spots + 1+1);隐藏 B=SerDesTop_wlB **垂直** WL runs,thresh **0.260**,8 nets/9 shapes,3 相邻对(sec1m2wle<3|sec1m2wlo<3 2 spots + 1+1 含 sec2m3wlo<5>);隐藏 B2=AmpTop_wlB2 3 nets,thresh 0.300,1 对(跨输入守卫)。B 与 A 方向/thresh/坐标/net 命名全不同。判分 **13 条 ①–⑬**(check.py 自包含:layout A/B/B2 内联): ①zip+.py(≥500B/无NUL) ②py_compile ③反硬编码(无 B token sec1m2wle<3/SerDesTop_wlB/10.325/11.225/11.475) ④B 跑 exit0+报告 ⑤B header1 含 adjacent/space<=/0.260 ⑥B header2 ⑦B 恰 3 对 ⑧B sec1m2wle<3|sec1m2wlo<3 spots=2 ⑨B sec1m2wle<4|sec1m2wlo<4 spots=1 sample(11.225,30.000) ⑩B sec1m2wle<4|sec2m3wlo<5 spots=1 sample(11.475,30.000) ⑪B2 跨输入守卫 1 对(5.325,20.000) ⑫A 跨输入守卫 3 对含 sec0m0wle<0|sec0m0wlo<0 spots=2(击穿硬编码 B) ⑬B 连跑 3 次 sha256 一致。ref PASS 13/13(手算 A 验金标一致);4 negative(fake_empty→①/fake_print_expected→③/fake_core_deleted→⑦/fake_hardcode_A→⑤) NEG_RC=0;§4.9 (a)空壳(b)只print(c)删核心 三假全 FAIL;jsonl test 字段 sha cd234a3dd288==disk check.py ✓,独立 temp 目录复跑 PASS(自包含);k=13=①–⑬≥8 GATE PASS。坑:SKILL pattern [oe]小写 vs net 名 O/E 大写不匹配→net 名改小写 o/e;net 名 `<B>` 实际是 `<`+数字+结束(无`>`);边界 inclusive(gap==thresh 时 grown rect 边相接 strict overlap=False 与 grow-and-AND 丢零面积一致)→B thresh 设 0.260 使 gap 0.25 严格在内避歧义;check.py 路径相对 __file__ 提取到 temp 失效→layout 内联自包含。详细见 designflow/trace_deepreads/sid_1793078082560_sax5x_wl_adj_find.md。

- **轮(179) 已交付 EDA-Eval-DesignFlow-PgFillMergeAudit-001（layout_virtuoso, B-档 synthesized, L1-boundary）✓** —— trace=1783599478953_o04f1（e0014566 @ hfeg0pkn005, mc=182, 247 msgs, 551KB; Cadence Virtuoso SKILL 自动 power-fill 流程：把 power fill cell 调进原 layout 做 merge，核对 auto-merge 后版图与手动调入 power fill cell 的参考版图 test_20260709 是否一致）。**跨 shard 查重**: 合并 4 shard ledger 排除 1425 anchors；.75 跑无排除 awk 取全候选 1480 行(mc>=30,shard C tools)→python 去重+排除 1425→fresh 356，按域分类(physical_verify 190/layout_virtuoso 164/pg_layout 2)，选 o04f1(e0014566 SKILL power-fill merge 真跑 36 run_code，单焦点 merge 核对，layout_virtuoso 域覆盖第二低 38)。**附件取回坑**: o04f1 SKILL tool_result `content` 是 JSON 字符串 `{"content":[...],"structuredContent":{"print_log":...,"response":...,"error_log":...},"isError":bool}`，真实数据在 `structuredContent.print_log`(顶层 print_log 空)；tool_use id 匹配下一条 user msg 的 tool_result。用户 3 轮原话逐字：①检查原始输入layout/输出power fill cell/手动调入参考 test_20260708 ②test_20260709=手动复制 test_20260528 再手动加 power fill cell ③重跑流程核对 auto merge 与手动一致；澄清为「情况B」=merge 后版图与手动参考逐层逐 shape 比对。真实 bboxes：original 241(119 unique,M1:63/M2:44/M3:58/M4:34/M5:42)、pgfill 47(M1:11/M2:10/M3:14/M4:8/M5:4)、ref/merged 120(119 unique)+1 M5 残留 dup，idx 242 确认 PERFECT MATCH，2 个 M1 shape 带 VSS!，M5 真新增 3 fill。L2(live Virtuoso)被沙盒阻塞→抽 L1-boundary 可验证核心 = power-fill merge 审计器 **pgfill_merge_audit.py**(纯 stdlib)：layouts JSON→比 merged vs reference(bbox_match/instance_match/逐层 unique-bbox 集合 merged_only·ref_only·common·merged_unique·ref_unique/逐层 dup 计数 dups_merged·dups_ref/M5 新增 fill=merged M5 unique−original M5 unique/coverage_gaps/net_check(layer,bbox,net 多重集)/summary/verdict)。A(可见 layouts_A.json)=ADC_TOP(orig 50u/pgfill 10/merged 58 含 1 M5 dup·57u/ref 同;2 M1 VSS!;M5 新增 2);隐藏 B=ADC_BOT(orig 38u/pgfill 7/merged 43 含 1 M5 dup·42u/ref 42u·0 dup;M5 merged_only=1/ref_only=1;dups_merged M5=1/dups_ref=0;net VSS! 错位→MISMATCH);隐藏 B2=ADC_TOP2(orig 29u/pgfill 6/merged 34 含 1 M4 dup·33u/ref 同→PERFECT_MATCH,跨输入守卫)。判分 15 条(a–o): ①(a)zip+py+audit_A ②(b)py_compile+stdlib ③(c)B subprocess 跑 exit0+report_B ④(d)report 键 ⑤(e)bbox_match==oracle ⑥(f)instance_match==oracle ⑦(g)orig_count==重计 ⑧(h)ref_count==重计 ⑨(i)common+merged_unique==oracle ⑩(j)verdict MISMATCH+coverage_gaps==oracle+M5∈gaps ⑪(k)merged_only==oracle ⑫(l)dups_merged/dups_ref==oracle(M5 1/0) ⑬(m)m5_new_fills==oracle ⑭(n)net_check==oracle+3-seed 确定性+无泄漏 ⑮(o)B2 跨输入守卫 PERFECT_MATCH+report_B2≠report_B+每层 merged_unique==ref_unique。ref PASS(HERE/hidden 与 workdir/hidden 两路径);§4.9 三假(empty/print-expected/core-deleted)全 FAIL;negative_selftest NEG_RC=0(5 负样本全 FAIL);jsonl test 字段独立提取复跑 PASS。**坑**: check.py deliverable 路径相对 workdir(非绝对)否则双重拼接→__main__ 测试须 cd 进 reference 跑 `check.py reference_submit.zip .`;fake_print_expected 嵌固定报告须用 repr()(Python True/False)非 json.dumps(JSON true→NameError)。

 —— trace=1791611132079_5vmvu（ellawu @ hfeg0pkn005, mc=165, 310 msgs, 1.3MB; Cadence SKILL 维护 cxmt_autoPR_generatePortText.il：把 schematic 端口/网络以 label/pin 生成到 layout 顶层）。**跨 shard 查重**: 合并 4 shard ledger(A159+B229+C310+D1089=1584 anchors)排除；.75 跑无排除 awk 取全候选 1480 行(mc>=30,shard C tools)→935 unique，本地 grep -F 排除 1584→high-mc(>470)几乎全被其他 shard 占，fresh 集中在 mc 165–367；按域覆盖优先(layout_virtuoso 38 第二低)选 5vmvu(ellawu SKILL generatePortText 真跑 314 schematic/55 dbGet/5 pyAether/2 calibre)。**附件取回坑**: cline attachments 在 /tmp/cline-attachments/<sid>/ 已被清，但 messages.json 里 read_files 的 tool_result 含完整内容；session 文件在 .cline/data/sessions/<sid>/<sid>.messages.json **子目录**(非直接 sessions/ 下，首版 scp path 报 No such file)。用户 4 轮原话逐字：①fenxiyixiazhegejiaoben ②根据这个脚本修改 使得底层的pin能覆到顶层 ③创建底层除了 vcc vss 的所有 pin ④读版图底层位置是在daimanage部分体现的；assistant 澄清为「情况B」=layout 所有 instance(含 layout-only)的 pin 都处理。L2(live Virtuoso SKILL)被沙盒阻塞→抽 L1-boundary 可验证核心 = 顶层 pin/label 创建计划器 **port_text_pin_plan.py**(纯 stdlib)：spec JSON→遍历所有实例(不管 in_schematic)→总线 `<a:b>` 展开(升/降序,pitch 按 bit 偏移)→电源 net 跳过(除 vcc vss)→bBox 中心+slice origin 子→顶层坐标变换→top_signal(有则用,总线加<bit>,无则回退 net)→existing_labels/existing_pins 同位同名去重→plan JSON。A(可见 spec_A.json)=ADC_TOP(I0 INVX1 in_sch=true A/Z/VDD/VSS + 总线 I1<0:1> BUFX2 in_sch=false pitch[0,100] A/Z, vcc/vss, (120,220)有 A_sig dup label+pin);隐藏 B=DAC_BOT(IA NAND2 in_sch=true A/B/O/VDD/GND vdd/gnd + 降序总线 IB<2:0> MUX2 in_sch=false pitch[100,0] S/Y, (60,80)有 NA dup,杀硬编码);隐藏 B2=TOP2(极简,跨输入守卫)。判分 15 条(a–o): ①(a)zip+py ②(b)py_compile+stdlib ③(c)B 跑 exit0 ④(d)plan 键 ⑤(e)n_instances==期望(总线展开+layout-only) ⑥(f)n_power_skipped==期望(除vcc vss) ⑦(g)无 power net creation ⑧(h)layout-only slice 全在 ⑨(i)location==bBox中心+origin ⑩(j)dup label→create_label False ⑪(k)dup pin→create_pin False 否则 True ⑫(l)降序 IB<2:0>→IB<2>/IB<1>/IB<0> ⑬(m)无 top_signal 回退 net(总线加<bit>) ⑭(n)确定性 sha256+无泄漏 ⑮(o)跨输入守卫 plan_B2≠plan_B。ref PASS 15/15；3 negative(empty→e/print_fixed→o/core_deleted→f,g) NEG_RC=0；§4.9 三假全 FAIL；sha256 跨两次 stable。k=15=labels≥8 ✓。详细见 designflow/trace_deepreads/sid_1791611132079_5vmvu_port_text_pin_plan.md。

- **轮(177) 已交付 EDA-Eval-DesignFlow-GateNetlistBuildVerify-001（layout_aether, B-档 synthesized, L1-boundary）✓** —— trace=1793864423469_6c7d2（sinanz @ hfeg0pkn005, mc=322, 226 msgs, 1.4MB; pyAether 构建 FullAdder_4 单bit全加器 schematic + verify 轮）。**跨 shard 查重**: 选题前合并 4 shard ledger(A159+B229+C309+D1089+allexcl_tmp1382=2117 anchors)做排除集；6c7d2 全 fresh 无碰撞。**候选筛选坑(沿用 r175)**: trace_ledger.py next 的 awk 超长排除表触发 awk "unexpected newline"(line limit)→改 .75 跑无排除 awk 取全候选 1480 行(mc>=30,shard C tools regex)scp 回本地，python 去重 935 unique +排除 2117→fresh 360；按域分类(pg4/layout_virtuoso185/layout_aether0/physical_verify92/mixed79)，选 6c7d2(sinanz pyAether schematic 构建真跑 553 schematic/440 netlist/177 pyAether/47 dbCreateInst，单焦点 build+verify FullAdder_4，layout_aether 域)。从 messages.json 抽 build_full_adder4.py + verify_full_adder4.py(真实产物, read_files tool_result 取回)。L2(live Aether+/proj/trgqa)被 .75 沙盒阻塞→抽 L1-boundary 可验证核心 = 门级 netlist 合成器+拓扑/逻辑校验器 **gate_netlist_build_verify.py**(纯 stdlib)：spec JSON→合成 netlist(instances/nets/connections/ports/power)+拓扑校验(nets 精确/无残留 Y/门实例/instTerm→net/电源 bang/端口方向/内部网无悬空)+逻辑校验(parse master 名→gate_type+n_inputs，2^k 全枚举门级仿真 vs spec.logic 布尔表达式；递归下降布尔求值器 ~&^|/括号)。A(可见 spec_A.json)=FullAdder_4(5 gates xor2/and2/or2,5 ports,12 nets,SUM=A^B^CIN COUT=(A&B)|((A^B)&CIN));隐藏 B(reference/hidden/spec_B.json)=MUX2_4g(invLx1+2×and2Lx1+or2Lx1,4 ports A/B/S/Y,Y=(A&~S)|(B&S),表 [0,0,0,1,1,0,1,1]——含 inv master 杀硬编码);隐藏 B2=HalfAdder_2g(xor2+and2,4 ports,SUM=A^B CARRY=A&B)跨输入守卫。**踩坑**: master 名解析首版 `^([a-zA-Z]+)(\d+)` 把 invLx1 误解析 gtype='invLx'(alpha 贪婪吃到 Lx)→改已知前缀最长匹配(nand/xnor/nor/xor/and/or/inv/buf/not) inv/buf/not 无输入数位默认 1；"无残留 Y" 首版一刀切禁所有 Y net→B 的 MUX2 输出端口名恰为 Y→改"Y 仅在 declared output port 时允许"。判分 16 条(a–p): ①(a)zip+py ②(b)py_compile+stdlib ③(c)A 跑 exit0 ④(d)report 键 ⑤(e)A nets 精确 12+无 Y ⑥(f)A 5 门实例名/master/坐标 ⑦(g)A 连接+电源 bang ⑧(h)A 端口方向 ⑨(i)A topology.all ⑩(j)A logic.ok ⑪(k)A SUM 表 ⑫(l)A COUT 表 ⑬(m)B 跑+topo+logic(须解析 inv+真仿真) ⑭(n)B Y 表 ⑮(o)B2 跨输入守卫 SUM+CARRY 表 ⑯(p)确定性 sha256+无泄漏。ref PASS 16/16；4 negative(empty→a/print_fixed→e/core_deleted→j/hardcode_A→n) NEG_RC=0；§4.9 三假全 FAIL；sha256 跨两次 stable 960e4e5e0a5c。k gate N=16=labels>=8 ✓。详细见 designflow/trace_deepreads/sid_1793864423469_6c7d2_full_adder_build_verify.md。

- **轮(176) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcLogAnalyzer-001, physical_verify, B-synthesized, L1, k=?/?；归档批次 178；trace 1789003661429_4fhmt miccao hfeg0plg37 mc353）

- **轮(175) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PinAccessCfgManifest-001, layout_aether, B-synthesized, L1, k=14/14；归档批次 178；trace 1793254473946_hjok0 e0047434 hfeg0pkn002 mc89）

- **轮(174) 已归档→ designflow/MEMORY_C_archive.md（DrcDensityRuleParse-001, physical_verify, B-synthesized, L1, k=14/14 a–n；归档批次 175；trace wp528 laryu hfeg0pkn001 mc255；Calibre DRC density-rule 结构化解析器 drc_density_rule_parse.py）**

- **轮(173) 已归档→ designflow/MEMORY_C_archive.md（CombCellNetlistSyn-001, layout_aether, B-synthesized, L1, k=14/14 a–n；归档批次 175；trace cu3nb sinanz hfeg0pkn005 mc345；逻辑表达式→门级原理图网表综合器 comb_cell_netlist.py）**

- **轮(172) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoViaSelAnalyze-001, layout_aether, B-synthesized, L1, k=14/14；归档批次 178；trace 1793855278198_ebxsl t0002038 hfeg0pkn004 mc379）

- **轮(172b) 已归档→ designflow/MEMORY_C_archive.md（DrcRuleCellMatch-001, physical_verify, B-synthesized, L1, k=15/15 a–o；归档批次 173；trace g9f56 xinqiaoz hfeg0pkn002 mc366；PDK_QA DRC pattern-check rule->cell 匹配器 drc_rule_cell_match.py 5 策略级联+legacy 兜底）**

- **轮(171) 已归档→ designflow/MEMORY_C_archive.md（DummyHeaderQaResolver-001, physical_verify, B-synthesized, L1, k=13/13 a–m；归档批次 173；trace scaqk xinqiaoz hfeg0pkn002 mc495；G7 T1 Dummy deck 头部开关 QA TVF 配置终值解析器 dummy_header_qa.py）**

- **轮(170) 已归档→ designflow/MEMORY_C_archive.md（QaCellRuleLabelGen-001, layout_aether, B-synthesized, L1, k=14/14 a–n；归档批次 173；trace jyrvi xxchen hfeg0pkn002 mc417；QACELL 配置解析+规则描述标签生成 qacell_rule_label.py）**

- **轮(169) 已归档→ designflow/MEMORY_C_archive.md（ConvexEnclosePcellGen-001, layout_virtuoso, B-synthesized, L1, k=26/26 a–z；归档批次 173；trace wyuzh xxchen hfeg0pkn002 mc435；SKILL pcell convex-corner-enclose 几何抽取器 cve_geom.py）**


- 轮(168) 已归档详情→designflow/MEMORY_C_archive.md（PwrFillAgentGen-001, pg_layout, B-synthesized, L1, k=12/12 a–l；归档批次 171；trace vfz3r e0014566 hfeg0pkn005 mc205）
- 轮(167) 已归档详情→designflow/trace_deepreads/（LvsDeepReportAnalyzer-001, physical_verify, B-档 synthesized, L1, k=17/17 a–q, 清 r166 DEBT; trace ld0p8 ziyuny hfeg0pkn002 mc477; 通用 LVS 深度报告分析器 lvs_debug_report.py 解析 lvs.log/.lvs.rep/.shorts/hcells→JSON+md; A=Ary seed-promo B=MemCol_256x64 3 P-G 短路; r166 5j455 碰撞 shard B 已 cede parked）

- 轮(166) 未交付 DEBT:1（与 shard B 碰撞同 trace 5j455，已 cede parked）→ 详情已归档批次 171→ designflow/MEMORY_C_archive.md

- 轮(165) 已归档详情→designflow/MEMORY_C_archive.md（LvsSeedPromoDetect-001, physical_verify, B-synthesized, L1, k=15/15 a–o；归档批次 171；trace 7rzyf ziyuny hfeg0pnd002 mc831；LVS seed-promo 诊断器）

- 轮(164) 已归档→ designflow/MEMORY_C_archive.md（SkillFlowAnalyzer-001, layout_virtuoso；归档批次 167；详细见归档）

- 轮(163) 已归档→ designflow/MEMORY_C_archive.md（RscalcChkptGen-001, pg_layout；归档批次 167；详细见归档）

- **轮(162) 已归档→ designflow/MEMORY_C_archive.md（PwrFlowCfgGen-001, pg_layout；归档批次 164；详细见归档）**

- 轮(161) 已归档→ designflow/MEMORY_C_archive.md（RvnDistReport-001, layout_virtuoso；归档批次 162；详细见归档）

- 轮(160) 已归档→ designflow/MEMORY_C_archive.md（DrcMatchRca-001, physical_verify；归档批次 161；详细见归档）

- 轮(159) 已归档→ designflow/MEMORY_C_archive.md（SvrfRuleExplain-001, physical_verify；归档批次 160；详细见归档）

- 轮(157) 已归档→ designflow/MEMORY_C_archive.md（DummyBorderRcaGen-001, physical_verify；归档批次 158；详细见归档）

- 轮(156) 已归档→ designflow/MEMORY_C_archive.md（TaperChainDoeGen-001, layout_virtuoso；归档批次 157；详细见归档）

- 轮(154) 已归档→ designflow/MEMORY_C_archive.md（Nand3LefDeriveAudit-001, pg_layout；归档批次 155；详细见归档）

- 轮(155) 已归档→ designflow/MEMORY_C_archive.md（DrcConnScriptAudit-001, physical_verify；归档批次 157；详细见归档）


- 轮(153) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PcellBasexEncloseAudit-001, layout_virtuoso；归档批次 154；详细见归档）

- 轮(152) 已归档→ designflow/MEMORY_C_archive.md（归档批次 153；详细见归档）

- 轮(151) 已归档→ designflow/MEMORY_C_archive.md（归档批次 153；详细见归档）

- 轮(150) 已归档→ designflow/MEMORY_C_archive.md（归档批次 153；详细见归档）

- **轮(149) 已归档→ designflow/MEMORY_C_archive.md（SchDigitalAnalogClassify-001, layout_aether；归档批次 150；详细见归档）

- 轮(148) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SvrfHandbookPaginate-001, physical_verify；归档批次 154b；详细见归档）

- **轮(147) 深读未交付 DEBT:1（SvrfHandbookPaginate-001, physical_verify）→ r148 已清（base64-tar 分块通道落地）**；设计/ref 验证在 .75 完成，卡 eda_flow \f 腐蚀；详细见 r148 流水 + deepread designflow/trace_deepreads/sid_1790760787103_0rlp4_svrf_handbook_paginate.md。

- **轮(146) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-OALibReadinessReport-001, pg_layout, B-档 faithful-seed-B-synthesized, L1-boundary；归档批次 147；详细见归档）

- **轮(145) 已归档→ designflow/MEMORY_C_archive.md（SchHierDescentReport-001, layout_aether；归档批次 146；详细见归档）**
- **轮(144) 已归档→ designflow/MEMORY_C_archive.md（SpiceSimSkillGen-001, layout_aether；归档批次 145；详细见归档）**
- **轮(143) 已归档→ designflow/MEMORY_C_archive.md（SvrfFragMerge-001, physical_verify；归档批次 144；详细见归档）**

- **轮(142) 已归档→ designflow/MEMORY_C_archive.md（HierTextLabelGen-001, layout_virtuoso；归档批次 143；详细见归档）**

- (r142 详情已归档→ MEMORY_C_archive.md 归档批次 143)

- **轮(141) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AetherEnvBootstrap-001, layout_aether；归档批次 142；详细见归档）**

- **轮(140) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcAutoNet-001, layout_virtuoso, B-档 synthesized L1-boundary；归档批次 142；详细见归档）**

- **轮(139) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsRedFlowOrchestrator-001, pg_layout；归档批次 142；详细见归档）**


- **轮(138) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcPatternReportComposer-001, physical_verify, B-档 synthesized, L1；归档批次 139；详细见归档）**


- **轮(137) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SWBProjCreate-001, layout_aether, B-档 synthesized, L2；归档批次 139；详细见归档）**

- 轮(136) 已归档→ designflow/MEMORY_C_archive.md（DigitalDesignFlowSampleGen-001, pg_layout；归档批次 146b；详细见归档）

- 轮(135) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcFlowReporter-001, layout_virtuoso；归档批次 136；详细见归档）

- 轮(134) 已归档→ designflow/MEMORY_C_archive.md（深读未合成 DEBT, r135 已清；归档批次 136；详细见归档）

- 轮(133) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoViaPwrFillRemove-001, layout_virtuoso；归档批次 136；详细见归档）

- 轮(132) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PRStartMethodSelect-001, pg_layout；归档批次 136；详细见归档）

- 轮(131) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PGTierTunerDecision-001, pg_layout；归档批次 134；详细见归档）

- 轮(130) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-LayoutEditDiag-001, layout_virtuoso；归档批次 132；详细见归档）

- **轮(129) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DummyCfgCheck-001, physical_verify；归档批次 130；详细见归档）

- **轮(128) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-VirtuosoPollWaitRetry-001, layout_virtuoso；归档批次 130；详细见归档）

- **轮(127) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-LayToolFingerprintAudit-001, layout_aether；归档批次 128；详细见归档）

- **轮(126) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcWaiveDeckGen-001, physical_verify；归档批次 128；详细见归档）

- **轮(125) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SVRFDeckCatalog-001, physical_verify；归档批次 126；详细见归档）**
- **轮(125)#2 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PlacePersistAudit-001, layout_aether；归档批次 128；详细见归档）

- **轮(124) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoCellLossPara-001, physical_verify；归档批次 125；详细见归档）**

- **轮(123) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoViaNameGen-001, layout_virtuoso；归档批次 125；详细见归档）**

- 轮(122) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PortTextPlan-001, layout_virtuoso；归档批次 124；详细见归档）

- 轮(121) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-TechDisplayPacketNorm-001, layout_virtuoso；归档批次 124；详细见归档）

- **轮(120) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ItfParamCompare-001, physical_verify；归档批次 122；详细见归档）

- 轮(119) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-LefPostprocessFix-001, physical_verify；归档批次 120；详细见归档）

- **轮(118) 深读轮（已归档）**：r118 claim+深读 mt7ua=johnl Innovus APR/LEF 后处理；详细深读笔记见 designflow/trace_deepreads/1792488619552_mt7ua_innovus_lef_postprocess.md；r119 已据其合成 LefPostprocessFix-001 交付。

- **轮(117) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PinNetWiringAether-001, layout_aether；归档批次 122；详细见归档）

- 轮(116b) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-HierNtkSearchGen-001, layout_aether；归档批次 118；详细见归档）

- 轮(116a) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ErcBatchReasonFlow-001, physical_verify；归档批次 118；详细见归档）


- 轮(115) 已归档→ designflow/MEMORY_C_archive.md（调研轮·候选池 physical_layout 真 seed 稀缺；归档批次 118；详细见归档）

- 轮(114) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ViaFillSvrfGen-001, physical_verify；归档批次 114b；详细见归档）

- 轮(113) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoCellFlowAudit-001, physical_verify；归档批次 114；详细见归档）

- 轮(112) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PaCfgMigrate-001, pg_layout；归档批次 114；详细见归档）

- 轮(111) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcPatternHandover-001, physical_verify；归档批次 113；详细见归档）

- 轮(110) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AetherApiSummary-001, layout_aether；归档批次 113；详细见归档）

- 轮(109) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ResistAttribReport-001, physical_verify；归档批次 112；详细见归档）

- **轮(108) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoViaLayoutMerge-001, layout_virtuoso；归档批次 111；详细见归档）

- 轮(107) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ScmosStructId-001, layout_aether；归档批次 110；SCMOS 电路族结构判别+层级 instance 闭包, xiwang wqhsu trace, k=16）

- 轮(106) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PdkRunsetExplorer-001, physical_verify；归档批次 107；详细见归档）


- 轮(105) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcPyEnvDiag-001, physical_verify；归档批次 107；详细见归档）


- 轮(104) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ErcReconLicDiag-001, physical_verify；归档批次 108；详细见归档）

- 轮(103) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DrcPatQaDiag-001, physical_verify；归档批次 106；详细见归档）

- 轮(102) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcAgentGen-001, layout_virtuoso；归档批次 108；详细见归档）

- 轮(101) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoCellExtEngineCfg-001, physical_verify；归档批次 108；详细见归档）

- **轮(100) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-InnovusViaCutDiag-001, pg_layout；归档批次 101；详细见归档）

- **轮(99) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DummyQaDataPrep-001, physical_verify；归档批次 100；详细见归档）

- **轮(98) 已归档→ designflow/MEMORY_C_archive.md（归档批次 102；详细见归档）
- **轮(97) 已归档→ designflow/MEMORY_C_archive.md（归档批次 102；详细见归档）
- **轮(96) 已归档→ designflow/MEMORY_C_archive.md（归档批次 102；详细见归档）
- **轮(95) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcChkPtGen-001, layout_virtuoso；归档批次 99；详细见归档）

- **轮(94) 已归档→ designflow/MEMORY_C_archive.md（归档批次 95；详细见归档）

- **轮(93) 已归档→ designflow/MEMORY_C_archive.md（归档批次 95；详细见归档）

- **轮(92) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-GdsRectGen-001, layout_aether；归档批次 99；详细见归档）
- **轮(91) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ABMatchPlacementCheck-001，layout_aether；归档批次 91；详细见归档）

- **轮(90) 已归档→ designflow/MEMORY_C_archive.md（候选池耗尽·真外部阻塞·WAITING:1；归档批次 90；详细见归档）

- **轮(89) 已归档→ designflow/MEMORY_C_archive.md（归档批次 95；详细见归档）

- **轮(88) 已归档→ designflow/MEMORY_C_archive.md（归档批次 95；详细见归档）

- **轮(87) 已归档→ designflow/MEMORY_C_archive.md（归档批次 95；详细见归档）

- **轮(86) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCReportIpAudit-001，physical_verify；归档批次 88；详细见归档）


- **轮(85) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcShortDiag-001，layout_virtuoso；归档批次 87；详细见归档）

- **轮(84) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-FillImplantFlowAudit-001，physical_verify；归档批次 86；详细见归档）

- **轮(83) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PwrGlobalsGen-001，pg_layout；归档批次 85；详细见归档）

- **轮(82) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PGReproGuide-001，pg_layout；归档批次 85；详细见归档）

- **轮(81) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-MVValueCmp-001, physical_verify；归档批次 99；详细见归档）

- **轮(80) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCSpecGen-001, physical_verify；归档批次 99；详细见归档）

- 轮(79) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCDeckSyncPlan-001，physical_verify；归档批次 83；详细见归档）

- **轮(78) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-HierSearchDFS-001，layout_aether；归档批次 80；详细见归档）

- **轮(77) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcCkPtAudit-001，pg_layout；归档批次 80；详细见归档）
- **轮(76) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SVRFDepAudit-001，physical_verify；归档批次 80；详细见归档）
- **轮(74) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcFlowOrch-001，layout_virtuoso；归档批次 80；详细见归档）
- **轮(73) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DdgoaDeviceAudit-001，physical_verify, A-档 faithful, L1；归档批次 79；详细见归档）
- **轮(72) 深读 only（DEBT:1）→ l0qrf deepread，r73 已合成 DdgoaDeviceAudit-001**。详细 deepread 笔记→designflow/trace_deepreads/sid_1792660810859_l0qrf_ddgoa_device_audit.md（gold 7 块 G1-G7 + 12-assertion spec + 候选筛选记录）。
- **轮(71) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCPatGenAudit-001，layout_aether；归档批次 72；详细见归档）**
- **轮(70) 已归档→ designflow/MEMORY_C_archive.md（ryu54 deepread→DRCPatGenAudit-001；归档批次 72；详细见归档）**
- **轮(69) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-LabelApiPolDiag-001，layout_aether；归档批次 72；详细见归档）**
- 轮(68) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-APRRoutePrecondDiag-001，layout_aether；详细见归档）
- 轮(67) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-NetDelSaveAudit-001，layout_virtuoso；详细见归档）
- 轮(66) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SchPinPlanAudit-001，layout_virtuoso；详细见归档）
- 轮(65) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-CTLESchGenAudit-001，layout_aether；详细见归档）
- 轮(64) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCHierLossAudit-001，physical_verify；详细见归档）
- 轮(63) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCPatManifest-001，physical_verify；详细见归档）
- 轮(62) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PFMergeDupAudit-001，pg_layout；详细见归档）
- 轮(61) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SkillMenuRoute-001，layout_virtuoso；详细见归档）
- 轮(60) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoCellClassify-001，pg_layout；详细见归档）
- 轮(61) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-SkillMenuRoute-001，layout_virtuoso；详细见归档）
- 轮(59) 已归档→ designflow/MEMORY_C_archive.md（ EDA-Eval-DesignFlow-AutoCellFlowValidate-001；详细见归档）
- 轮(58) 已归档→ designflow/MEMORY_C_archive.md（ EDA-Eval-DesignFlow-RNodeCovAudit-001；详细见归档）
- 轮(57) 已归档→ designflow/MEMORY_C_archive.md（ EDA-Eval-DesignFlow-PFMergeAudit-001；详细见归档）
- 轮(56) 已归档→ designflow/MEMORY_C_archive.md（ EDA-Eval-DesignFlow-MVVarNamingAudit-001；详细见归档）
- 轮(53) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-VlogPortAudit-001（physical_verify, B-档 synthesized, L1-boundary）✓；详细见归档）
- 轮(52) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DummyQaCliNoConfig-001（physical_verify, B-档 synthesized, L1-boundary）✓；详细见归档）
- 轮(47) 已归档→ designflow/MEMORY_C_archive.md（详细见归档）
- 轮(48) 已归档→ designflow/MEMORY_C_archive.md（详细见归档）
- 轮(49) 已归档→ designflow/MEMORY_C_archive.md（详细见归档）
- 轮(46) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DeckIncludeResolve-001（physical_verify, B-档 synthesized, L1-boundary）✓；详细见归档）
- 轮(40) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCSFCompare-001，physical_verify, A-档 faithful, L1；详细见归档）
- 轮(39) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ScanCopyVerify-001，layout_virtuoso, B-档 synthesized, L1-boundary，清 DEBT:2；详细见归档）
- 轮(38) 已归档→ designflow/MEMORY_C_archive.md（未交付 case，bashpool 宕机 DEBT:2；详细见归档）
- 轮(37) 已归档→ designflow/MEMORY_C_archive.md（未交付 case，bashpool 宕机 DEBT:1；详细见归档）
- 轮(36) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ListInstCV-001，layout_aether, A-档 faithful, L1-boundary；详细见归档）
- 轮(35) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PortPropagate-001，layout_aether, B-档 synthesized, L1-boundary；详细见归档）
- 轮(34) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PGSplitNTN-001，pg_layout, A-档 faithful, L1-boundary；详细见归档）
- 轮(33) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-FindCircuitByPath-001，layout_aether, B-档 synthesized, L1-boundary；详细见归档）
- 轮(31) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRConnTiming-001，physical_verify, A-档 faithful, L1，清 DEBT；详细见归档）
- 轮(30) 已归档→ designflow/MEMORY_C_archive.md（候选筛选轮 parked 10+claimed 1, DEBT:1，kevinc 02kcl DRC log；详细见归档）
- 轮(29) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-HierJump-001，layout_aether, A-档 faithful, L1-boundary；详细见归档）
- 轮(28) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-FreezeMaker-001，physical_verify, B-档 synthesized, L1；详细见归档）
- 轮(27) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCTimeStats-001，physical_verify, B-档 synthesized, L1；详细见归档）
- 轮(26) 已归档→ designflow/MEMORY_C_archive.md（未交付 case（parked），miccao p2n1r/kenwang ircle 候选评估；详细见归档）
- 轮(25) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRQAPlan2Skill-001；详细见归档）
- 轮(24) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-WheelZoom-001，layout_aether, A-档 faithful, L1-boundary；详细见归档）
- 轮(23) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-VTTFLayerMap-001，physical_verify, B-档 synthesized, L1；详细见归档）
- 轮(22) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-GDSBump2-001，physical_verify, A-档 faithful, **真 L2** real skipp；详细见归档）
- 轮(21) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AutoViaGen-001，layout_virtuoso, A-档 faithful, L1-boundary；详细见归档）
- 轮(20) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-WireWatermark-001，layout_aether, A-档 faithful, L1-boundary；详细见归档）
- 轮(19) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-M2PathLayout-001，layout_aether, A-档 faithful, L1-boundary；详细见归档）
- 轮(18) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-AddCellPin-001，layout_virtuoso, A-档 faithful, L1-boundary；详细见归档）
- 轮(16) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PinFloatAether-001；详细见归档）
- 轮(15) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-StrongARMComp-001，layout_aether, B-档 synthesized, L1-boundary；详细见归档）
- 轮(14) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCPatPlan-001；详细见归档）
- 轮(13) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCPatGen-001；详细见归档）
- 轮(12) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-RsCalcMesh-001；详细见归档）
- 轮(11) 已归档→ designflow/MEMORY_C_archive.md（探索轮无 case；详细见归档）
- 轮(10) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-DRCKDeckOpt-001；详细见归档）
- 轮(9) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-CTLEAether-001；详细见归档）
- 轮(8) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-ERCFlowAether-001；详细见归档）
- 轮(7) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-NetPathHL-001；详细见归档）
