# trace_deepread: fxbe5 — ypzheng SPICE postsim .map signal-hierarchy trace

- **session**: 1794899351856_fxbe5 @ ypzheng / hfeg0plg103 (10.129.8.235)
- **scan**: ssh_eda_search_20261123_064315, mc=96, keywords: cmos:787;netlist:618;schematic:67;analog:42;pex:10;hspice:9
- **size**: 108 msgs / 505 KB messages.json (agent=lead)
- **shard/domain**: D / schematic_netlist

## 用户真实意图

- U0: 「直接告诉我 cm0_ts_AsyncEn 这个信号在哪里，hierarchy 是什么」(SPICE postsim 网表目录)
- U40: 「我说的是 cell 的 hierarchy，你给一个 ddgoa_cmos_digital 我去哪找？」
- U64: 「cm1_ro_RowRedSaveBankN 这个信号的作用是什么，结合电路解释」
- U102: 「进一步深入分析」(晶体管级真值+完整布尔链)

## agent 工具链与关键产物

1. list_allowed_files 枚举 /rundata/ddgoa/V0/simdir/finesim/workdir/edwinyan/simulation/Netlist_SpfBa_20261031PM
2. read_files / run_approved_command 读 netlist_org / netlist.postsim / ddgoa_top_WOWTOP_config_SpfBA.netlist.map
3. editor 写 Python 脚本: grep 信号 + 解析 .SUBCKT/.ENDS 嵌套 + 解析 .map 文件 parent-child-P|N|I-signal-idx 格式 + 追踪 instance chain

## .map 文件格式 (finesim postsim)

`<parent_cell> <child_cell> <P|N|I> <signal_name> <idx_or_mapped>`
- P = child 把 signal 作为端口引出, 第5字段 = port_idx (整数, 如 27/1426/221)
- N = child 内部 net, 第5字段 = 该 net 在父 cell 中对应的名字 (常同名)
- I = 实例定义, 第5字段 = 实例 label

## cm0_ts_AsyncEn .map 记录

```
ddgoa_cmos_digital  AynscAddressCnt  P  cm0_ts_AsyncEn  27
ddgoa_cmos_digital  ControllerM5     P  cm0_ts_AsyncEn  1426
ddgoa_cmos_digital  CMCenterR        P  cm0_ts_AsyncEn  221
ddgoa_cmos_top      ChanMid          N  cm0_ts_AsyncEn  cm0_ts_AsyncEn
```

hierarchy: ddgoa_top→ddgoa_cmos_top→ddgoa_cmos_digital→{AynscAddressCnt(source), ControllerM5, CMCenterR}; ChanMid 在 ddgoa_cmos_top 下作为内部 net

## reframe → EDA-Eval-DesignFlow-PostsimMapSignalHierProduce-001

**内核**: 解析 finesim postsim `.map` 文件 (parent/child/P|N|I/signal/idx) + `.SUBCKT` 头, 对目标信号输出结构化 hierarchy: port_cells / internal_cells / instance_records / source_block / hierarchy_chain / n_subckts / n_port_cells / n_internal_cells / n_instances.

**A** (可见): 8 个 .SUBCKT (topA/digitalA/AsyncAddrCntA/ControllerA/CMCenterA/ChanMidA/invNx1/bufNx1), .map 4 P + 1 N + 3 I for sig_A_async_en, target=sig_A_async_en. oracle: source=AsyncAddrCntA, chain=[topA,digitalA,AsyncAddrCntA], n_subckts=8, n_port=4, n_int=1, n_inst=3.

**B1** (hidden): 8 个 .SUBCKT (topB/analogB/LatchedCompB/ClkGateB/BiasCtrlB/RefBufB/invNx1/bufNx1), .map 4 P + 1 N + 3 I for sig_B1_cur_ref. oracle: source=BiasCtrlB, chain=[topB,analogB,BiasCtrlB], n_subckts=8, n_port=4, n_int=1, n_inst=3.

**B2** (hidden): 5 个 .SUBCKT (topC/digC/LeafAX/LeafBY/invNx1), .map 3 P + 1 N + 1 I for sig_C_dcc_en. oracle: source=LeafAX, chain=[topC,digC,LeafAX], n_subckts=5, n_port=3, n_int=1, n_inst=1.

**check.py 12 条**: ①zip+.py+compile ②B1 exit0+JSON+10 keys ③B1 port_cells 集合 ④B1 internal_cells 集合 ⑤B1 source_block ⑥B1 hierarchy_chain ⑦B1 n_subckts(反A=8) ⑧B1 port_idx 多重集(反A={3,0,0,0}, B1={4,0,1,2}) ⑨确定性3次md5 ⑩anti-hardcode-A B1 cell名/signal与A不相交 ⑪B2 exit0+oracle匹配+B2≠A ⑫B1 instance_records 集合.

**§4.9 三假**: empty_shell→① / print_only→③ / core_removed→③. 全 FAIL ✓.

**自验**: REF 12/12 PASS + 3 负样本全 FAIL + round-trip 从 case JSON 抽 test 重跑全 PASS ✓.

**与已有 case 区别** (kernel_disjoint_from): r1200 WlToggleClassify(Verilog 叶 cell 驱动+top→leaf, 非 SPICE .map) / r1091 WlHierarchyTraceProduce(SPICE WL bottom-up positional, 非 .map top-down P|N|I) / r1213 DqBusStimulusGen(SPICE 层次 path+dc 激励, 无 .map) / HierNetTrace-001(SPICE HSPICE X positional+glob, 无 finesim .map 工件) / NetlistHierarchyExtractQA-001(SPICE 列数守恒表, 非信号→owner cell 映射).
