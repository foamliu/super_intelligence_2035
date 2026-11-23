# 深读笔记 — e0t69 (shanliny @ hfeg0plg53, mc=45, schematic_netlist)

**session**: 1794910943730_e0t69.messages.json (155 msgs, 7.0MB)
**用户真实意图**: 修复 rc_viz_gui.py 的 history 记录功能(所有功能都要记入历史, 不只 viz/extract) + 优化超大 DSPF 网表(10GB)解析性能(现 5MB 卡顿). 不改变程序功能.
**附件**: rc_viz_gui.py(2369行 GUI), rc_viz_tool2.py(RC分析CLI), HD1P_..._dspf.TYPICAL_-40(5MB DSPF样例)

## assistant 行动链
1. 读 uploads 副本 vs /home/shanliny 真实副本(md5一致, GUI 2369行, 96核/2TB内存)
2. 读全 GUI: 发现只 run()(viz)+run_extract() 记历史, 交互预览/批量R不记; parse() 逐行读全文件进内存(10GB必OOM)
3. tool2 改造: 加 mmap+多进程分节并行解析引擎
   - parse() → _parse_full(全量兜底) + parse 分派器
   - find_net_range(netname): 字节级正则定位 *|NET 分节字节范围
   - _scan_data/_scan_range: 多进程并行扫各分节
   - _prepare_scan_params, _resolve_silent, _find_net_range_fuzzy
   - extract_net_with_cap 改分节范围定位
4. GUI 改造:
   - _record_history: 全功能(viz/preview/batch/extract)记录, 按(kind,vars)去重, 原子写+备份恢复, _hist_label 区分4类
   - shortest_path/segment_resistances: 预构建邻接免重建
   - detect_sep: 加快速路径
   - net_scan: 改分节定位调度器(原实现兜底)
   - scan_all_coords: 多进程包围盒扫描(新返回契约+缓存)
   - _toggle_global_pos: 新返回契约+缓存
5. 验证:
   - _zh_test1: 24个net分节=全量解析等价(含 BLPCHB_D 修复——*|P 端口行不应终止分节)
   - 8对R逐位一致, extract逐字节一致
   - CLI端到端: 新版小文件路径与原版输出完全一致; 强制分节模式R值与路径报告一致; 5MB提速1.17s→0.61s
   - GUI冒烟: DISPLAY连不上→Xvfb(Verdi自带)→Xvfb启动失败(最终未跑成GUI, 但CLI全部通过)

## 可离线判分内核(本case抽取)
DSPF 1.3 解析 + RC 图构建 + 等效电阻(导纳矩阵法):
- *|S(node x y) → rc_nodes; *|I(node dev term ... x y) → dev_ct; R n1 n2 r → rlist; C n1 n2 cap → clist
- total_cap = sum(C where n2=="0"); 耦合电容(n2!="0")计入clist但不计入total_cap
- build_graph(rlist) → adj; eff_resistance(na,nb): 节点导纳矩阵G, nb接地, na注入1A, solve V, Req=V[na]
- 与 r1208 waive/r1210 设计清单/r1209 Verilog层次追踪全不相交

## hidden B 设计(design=HIDDEN_B_RCNET)
- 2 net: VDD_ROUTE(3 *|S节点, 2 *|I端子 TA/TB, 5电阻含 Rpar 并联支路, 3对地C), CLK_TREE(2节点, 1端子 CLKIN, 2电阻, 2对地C)
- 跨net耦合电容 Ccouple(VDD_ROUTE:2, CLK_TREE:2, 0.2e-15) → 计入total_capacitors=6 但不计入total_ground_cap
- Req(TA,TB): 主链 Rdrv1(10)+Rmid1(10)+Rmid2(10)+Rrcv1(10)=40 并联 Rpar(10) 跨 n1-n3 → 10||(10+10)=6.6667 → Req=10+6.6667+10=26.6667Ω
- total_ground_cap = 0.5+0.7+0.3+0.4+0.5 = 2.4e-15 F
- VDD_ROUTE.ground_cap = 0.5+0.7+0.3 = 1.5e-15 F
- 与 A(SAMPLE_A_RC/SIG_A+SIG_B/4电阻/串联5+5+5链Req=15Ω/3电容) 结构性不相交

## k_check 草案 → 定稿 16 条(见 cases/D JSON test_rationale)
a-h(i) 结构+解析, j-m 计数+电容, n 等效电阻, o 确定性, p 反硬编码
