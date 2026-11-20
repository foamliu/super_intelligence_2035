# r855 · 2026-11-20 · A-pure revival 续深读 3 条（11-15 候选池重审「12 待深读」第 4 轮）

**背景**：r854 DEBT(a) 12 待深读候选池续做。r854 指定优先 mss1b / 0g9n6 / mon3r。本轮 eda_flow session r855 开 + 三条 trace 检索 + 深读。

**检索教训（r823 subdir-path 复发，重要）**：cline 新格式把会话文件放进 `sessions/<id>/<id>.messages.json` 子目录，flat-path `sessions/<id>.messages.json` NOFILE 是 **path-bug 不是 rotation**。本轮 0g9n6/mon3r 都差点因 flat-path 误判 NOFILE，改用 `find <id>* -name '*.messages.json'` 才命中。mss1b 在 10.129.2.10 flat-path NOFILE、subdir ALIVE。**下轮检索一律先 `find ... -name '*.messages.json'`，禁用 flat-path 断言。**

## 1. 0g9n6 → 可造（defer 下轮合成）· B档 synthesized debug-Q&A

- **trace**：`1794557869660_0g9n6`，thomas1w，检索 IP 10.129.35.244 (hfeg0pgn145)；tsv 旧记 host=hfeg0plg98 有误（scan 实际 thomas1w 在 hfeg0pgn145/pjn178/pjn196/plg93 四机同 home）。messages.json 314116 B / 27 msgs，agent=lead。subdir-path ALIVE（flat-path NOFILE 假阴性）。
- **用户原话（U#0）**：「/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.1030/llog_1113/scan_allspeed.x16/ 仿真卡死，加了一些zero loop的检测，也没检查出来，帮我看下」
- **核心意图**：仿真卡死诊断 debug-Q&A。用户已自加 zero-loop 检测未命中，求助定位卡死原因。属 A 域 verification，debug-Q&A（11-15 令合法）。
- **agent 链**：list_allowed_files → read_files irun.log（尾部 43200+ 行）→ 读出 `*W,TRZDGOC` zero-delay gate oscillation → editor 写 diag_find.py/diag_grep.py/diag_log.py grep 全 log → read A_Pattern_Sim.v/A_Compare.rpt → 给出完整诊断（msg #26）。
- **gold（msg #26 完整诊断，specificity-oracle 可 tothy）**：
  1. 根因 = **门级组合逻辑零延迟振荡（zero-delay gate oscillation / combinational loop）**，**不是** TB「$time 不动」那种零环
  2. 仿真时间 **1914941946 ps（≈1.9149 ms）**
  3. pattern = **`BG_Act-Wr-RdAp`**（第 1 个随机跑到的）
  4. 抓到振荡的是 **ncsim 内建 `-gateloopwarn` → `TRZDGOC`**，**不是** 用户 TB 里加的 watchdog
  5. irun.log 证据行 43732：`ncsim: *W,TRZDGOC: Possible zero-delay gate oscillation detected` / `Time: 1914941946 PS + 8388605` / 行 43736 `drivers -active` → `None`
  6. `drivers -active=None` **不代表没问题**：组合环靠 tranif1/gate 连续驱动转，不算 active driver（过程块驱动源），故该命令在此无用
  7. 振荡**之前**已出问题：A_Compare.rpt 在 `BG_Act-Wr-RdAp` 一开跑就是 DQ 全 `1`/`x`、RDQS_t/c 相位错乱（如 `1914216208 ps DUT_DQ:1111111111111111 Exp_DQ:z`），约早 0.7ms；读坏 + 定环大概率同一功能问题两表象
  8. 用户检测漏检原因：watchdog 监视对象大概是「TB $time 不前进」，而振荡在 DUT 门级 delta 循环，ncsim 先触 delta-iter 上限报 TRZDGOC 把 sim 停回 prompt，watchdog 没轮到发声
  9. 下一步可执行：固定 seed=1389361932 跑单 `BG_Act-Wr-RdAp`；`run -until 1914941900ps` 打停 + 开 `fsdbDumpvars 0 TOP`；关 SDF（去 `USESDF`）单位延迟复跑判 SDF 伪环 vs 真功能环
- **B档可行性**：A档不可行——真实 irun.log 在 `/rundata/ddgoa/...` 属 ddgoa 项目组，e0031982@.75 ssh 10.129.35.244 Permission denied（非项目组），且 trace 内 agent 未 dump 完整 log（只读了片段）。B档 synthesized：合成 irun.log 尾段（含 TRZDGOC 行 43732 / time 1914941946 / BG_Act-Wr-RdAp / drivers -active None）+ A_Compare.rpt 片段（DQ 全 1/x）+ 用户 zero-loop watchdog 代码（合成，监视 $time）。任务形态忠实（仿真卡死求助 debug-Q&A）。
- **拟 check（≥12 条独立断言）**：①非空中文报告≥200 ②识别 TRZDGOC/零延迟门振荡为根因 ③报 1914941946 ps ④点名 pattern BG_Act-Wr-RdAp ⑤归因 ncsim -gateloopwarn 内建检测（非用户 watchdog） ⑥refuse-to-hallucinate：不把根因说成「TB $time 卡住」零环 ⑦引 irun.log 证据（TRZDGOC 行 / drivers -active None） ⑧解释 drivers -active=None 为何不等于无问题 ⑨提振荡前 DQ 读错（全 1/x）线索 ⑩给可执行下一步（run -until / FSDB / SDF on-off） ⑪anti-leak 不泄 B 独有 token ⑫确定性重解析稳定。hidden-B = 不同根因 irun.log（如 $time-stuck TB 无限循环 / license timeout / SPICE convergence），结构不同 judge-only。3 neg：empty→① / print_only_generic→② / core_del→②删 TRZDGOC+时间+pattern。参考解 = msg #26 改写。
- **裁决**：**可造，defer r856 合成**（gold 已就绪，B档 fixture 合成 + check.py + 3 neg + 自验 ≈ 30min，超 40min 单轮预算，质量闸门不可妥协）。

## 2. mss1b → 可造（defer）· B档 synthesized walk-through Q&A

- **trace**：`1792041543395_mss1b`，e0039102，检索 IP 10.129.2.10 (hfeg0pkn001)；tsv 旧记 10.129.2.11 有误。messages.json 295765 B / 30 msgs，agent=lead。subdir-path ALIVE。
- **用户原话（U#0）**：「/rundata/drgsa/V0/simdir/verilog/jason17w/regression/verilog.ddr5.drgsa.clean/ 带我读一下这个项目里的vcim文件和verilogrun文件，在哪个文件夹，具体内容逐行带我读？先vcim文件」
- **核心意图**：逐行 walk-through 解释 verilogrun 文件 + 定位 vcim 文件。digital 域，walk-through Q&A（11-15 令合法）。
- **agent 链**：list_allowed_files 全项目树 → 找 verilogrun（在 `build_file/noregression.x8/verilogrun` 和 `build_file/noregression_nosa.x8/verilogrun`，per-run xcelium/xrun 启动脚本）→ **全树 grep `vcim` 命中 0 次**（vcim 在项目里不存在）→ agent 卡在问「vcim 文件具体指什么」，session sigterm（msg #29 `code_sidecar_sigterm`），未读 verilogrun 内容、未给出 walk-through。
- **关键事实（trace #9 build_file 真实清单）**：`build_file/noregression.x8/` 含 `verilogrun`/`A_Pattern_Sim.v`/`A_Compare.rpt`/`A_Summary.rpt`/`sdf.cmd`/`probe.tcl`/`xrun.log`/`WOWTOP_1C2A.sdf.gz`/`xcelium.d` 等；`noregression_nosa.x8/` 同构。vcim 全树 0 命中。
- **A档不可行**：真实 verilogrun 内容在 `/rundata/drgsa/...` 属 drgsa 项目组，e0031982@.75 ssh 10.129.2.10 Permission denied；trace 内 agent 未读 verilogrun 内容（sigterm 在求助澄清前）。故「逐行读 verilogrun」部分无法用真实文件 ground。
- **B档可行性**：合成 verilogrun 脚本（realistic xcelium/xrun launcher：`+nctypdelays`/`+notimingchecks`/`-sdf`/`+ncsdf_nocheck_cell_type`/`-gateloopwarn`/`-f filelist`/`coverage_dir`/`fsdbDumpvars`）作 fixture A；项目树用 **trace #9 真实清单**（build_file/noregression.x8/* 真实，vcim 真实不存在）。任务形态忠实（逐行读 verilogrun + 找 vcim）。refuse-to-hallucinate gold：vcim 不存在（真实事实）。
- **拟 check（≥10 条）**：①非空中文 walk-through≥200 ②定位 verilogrun 在 build_file/noregression.x8/ ③正确报 vcim 不存在（refuse-to-hallucinate，不编造 vcim 文件/路径） ④逐行解释 verilogrun ≥N 个关键 flag（-sdf/+nctypdelays/-gateloopwarn/-f/coverage） ⑤引 verilogrun 具体行号 ⑥解释 xcelium/xrun 调用结构 ⑦anti-leak 不泄 B 独有 token ⑧确定性稳定 … hidden-B = 不同 verilogrun（不同 flag/结构）+ 不同项目树。注意：此 case 的「逐行读」部分是合成 fixture，gold 须据合成文件提炼（不是真实 verilogrun）；「vcim 不存在 + verilogrun 位置」部分是真实事实。
- **裁决**：**可造，defer**（B档 fixture 合成 + check 较 0g9n6 略繁——需合成可逐行解释的 verilogrun，下轮做；优先级次于 0g9n6，0g9n6 gold 已完整就绪）。

## 3. mon3r → 待深读（检索确认，未读内容）

- **trace**：`1792995847117_mon3r`，e13zhang，检索 IP 10.129.2.11 (hfeg0pkn002)；**tsv 旧记 user/host 字段空（数据漏填）**，scan 实际 e13zhang 在 hfeg0pkn002/pgn012/pjn200/plg15 四机。messages.json 213368 B，subdir-path ALIVE（`sessions/1792995847117_mon3r/1792995847117_mon3r.messages.json`）。
- **旧判**：SDF SDFCOM_NL warning debug troubleshooting，weak。
- **本轮**：仅确认检索可达（subdir），**未读内容**（40min 预算耗尽于 0g9n6/mss1b 深读 + 检索排坑）。下轮优先深读判 可造/不可造。

## 小结

12 待深读 → 本轮处理 3：**0g9n6 可造(defer) / mss1b 可造(defer) / mon3r 待深读(检索确认)**。剩 9 待深读未动。**A-pure「枯竭」证伪**：12 候选里已挖出 2 条可造（0g9n6 debug-Q&A gold 完整、mss1b walk-through B档可行），矿脉未死，下轮直接合成 0g9n6 即可产 case。

**DEBT 下轮**：(a) **合成 0g9n6 case（最高优先，gold 就绪）** (b) 合成 mss1b case (c) 深读 mon3r (d) 剩 9 待深读续做（选料前先全 shard 并集查重 + subdir-path 检索）。
