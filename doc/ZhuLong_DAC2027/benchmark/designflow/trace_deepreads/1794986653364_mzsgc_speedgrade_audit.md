# trace_deepread: 1794986653364_mzsgc — witterfu @ hfeg0pkn005 (speedgrade audit)

- **session**: 1794986653364_mzsgc.messages.json
- **user / host**: witterfu @ hfeg0pkn005 (ip 10.129.32.75 / 0.0.0.0 masked in summary)
- **mc**: 106 (keywords: netlist:974; hspice:317; schematic:113; pdk:112; ...)
- **agent**: lead, 192 msgs, 823KB messages.json (new cline dir format: sessions/<sid>/<sid>.messages.json)
- **scan snapshot**: ssh_eda_search_20261120_145529 → summary_1120_reconstructed.tsv
- **pool context (r945 pre-claim)**: mc-matrix `python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1120_reconstructed.tsv` → mc≥10 pool=2072 touched=1764 fresh=308; candidates_mc10.tsv curated subset 全 ledgered (cross-shard 4-ledger dedup → 0 fresh); 重建 fresh B-spice (spice_total≥20) → 116 fresh; dedup-by-user 选 witterfu (spice_total=317, NEW-user, 无 prior case)。

## 用户真实意图（trace-faithful）

session 演化经过 3 个 sub-task：

### sub-task 1 (msg[0]–msg[177]): sp 仿真文件 model/PVT 改写
用户 msg[0] 原话：
> `.lib '/apps/imctf/extpdk/HL22/22HK_V0P5_0D10_for_vodka/model/0.0.6/hspice/model.sp' Top_tt`
> 上面是新的model文件，下面路径下的sp仿真文件需要你把原来旧的pvt文件注释掉，然后更新为上面新的sp文件，同时下include的pvt文件路径你也copy一份放到下面文件夹中：/home/witterfu/Downloads 同理改成新的pvt文件形式，然后原来sp文件里include新的文件,新的sp文件也保存在/home/witterfu/Downloads路径里面

msg[23] 用户补充：旧 pvt 文件 = wck_DCA.SP 里的 `.inc '/rundata/ddgot/V0/simdir/finesim/workdir/jiayinh/simulation/sim_WCKIB_test/hspiceD/PVT/new_corner.sp'`；旧 sp 文件目录 = `/proj/ddgot/V0/workdir/witterfu/simulation/wck/dca/12800`。

agent 探索文件系统 → 找到 wck_DCA.sp (11627B, Model 段含 `.lib '.../model_thick.sp' TT_vodka` + `.inc '.../new_corner.sp'`) → 改写为 wck_DCA_17600.sp + 本地 new_corner.sp 存 Downloads/dca/new/ → 进一步生成 RDCA 版 (msg[167] 用户确认数据方向对调 + 使能位对调)。

### sub-task 2 (msg[178]–msg[185]): drate 一致性核对
用户 msg[178] 原话：
> /proj/ddgot/V0/workdir/witterfu/simulation/wck/dca/new 这个路径下的sp文件和run文件的速率你帮我检查一下有没有对应错误，就是17600 14400 12800 这些

agent 核对：sp 文件 `.param drate` 与文件名速率全一致；6 个正式 run 脚本对应正确；4 个 `~` 备份脚本错误指向 17600。

### sub-task 3 (msg[186]–msg[191]): speedgrade 分档核对 ← **本 case 取此意图**
用户 msg[186] 原话：
> 帮我检查一下现在我需要改变speedgrad的分档位，12800要给100，14400要给101，看一下sp是不是修改好了

speedgrade = 3-bit 编码 [grd2 grd1 grd0]（`.param grd2=` `grd1=` `grd0=`，1=high speed, 0=low speed）。
agent 核对各 sp 文件 speedgrade：
- wck_DCA_12800.sp / wck_RDCA_12800.sp: grd2=1,grd1=0,grd0=0 = **100** ✓ (target 12800→100)
- wck_DCA_14400.sp / wck_RDCA_14400.sp: grd2=1,grd1=0,grd0=1 = **101** ✓ (target 14400→101)
- wck_DCA_17600.sp / wck_RDCA_17600.sp: 111 (17600 无 target)
- Rj_wr_17600.sp: 101 (anomaly vs DCA/RDCA 17600=111，但 17600 无 target)
- wck_DCA.sp (通用无速率后缀): 111

结论：12800/14400 的 4 个文件 speedgrade 全部已按要求改好。

## 本 case 设计

取 msg[186] 真实核对意图，交付纯 Python `speedgrade_audit.py`：给定 deck 目录 + target_map(rate→3bit)，审计每个 *.sp 的 grd2/grd1/grd0 编码 vs target，产出结构化 report.json。

- **A 档 trace-faithful**：prompt 用 msg[186] 用户原话 + 上下文（deck 目录、speedgrade 编码约定）。
- **A (visible)**: 8 个真实结构 sp 文件 (wck_DCA_12800/14400/17600, wck_RDCA_12800/14400/17600, Rj_wr_17600, wck_DCA) + target {12800:100, 14400:101}。
- **hidden B (anti-hardcode)**: 8 个异结构 sp 文件 (rates 10600/12800/15000) + target {10600:100, 12800:110, 15000:011}；planted mismatches at wck_DCA_15000.sp (010 vs 011) + wck_RDCA_12800.sp (010 vs 110)；wck_DCA.sp filename 无速率 → no_rate。
- **check()**: 19 条独立断言 (a..s)：脚本存在/编译/运行/report schema/文件数/字段齐全/encoded/filename_rate/drate/speedgrade_match/status/summary 6 项/mismatch 集合/anti-hardcode/4 negatives/3-seed 确定性。
- **NEG 4/4 FAIL**: naive_empty / print_only(灌 A 报告) / core_removed(全 ok) / hardcode_a(返回 A 报告)。
- **自验**: ref PASS 19/19；NEG 4/4 FAIL；3-seed sha256 一致（check 内 condition s）。

## case 落库

- case_id: EDA-Eval-DesignFlow-SpeedgradeAuditGen-001
- domain: spice_sim, layer: L1, k=19 (a..s)
- cases/B 473→474, B.jsonl 473→474 (auto-regen build_jsonl --shard B)
- ledger_B case 635→636, spice_sim 479→480
