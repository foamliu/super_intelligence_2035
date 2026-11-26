# deepread ui4hv — ruisongs xrun DLCSMD stale compile-cache (debug-Q&A, r849 case)

## trace
- session: 1792571741703_ui4hv
- user: ruisongs  host: hfeg0pfn090  ip: 10.129.33.216  domain: digital  mc: 52
- 48 msgs, agent=lead, subdir-path ALIVE 267KB (flat-path NOFILE, r528 path-bug 第N例)
- 旧判(2026-11-14)'sim log debug Q&A+cache-clear infra' REJECT (not produce-task) → 11-15 debug-Q&A 合法, 复活

## 用户原话 (4 user turns)
- U#0: `/proj/drvqa/V0/simdir/verilog/ruisongs/verilog.ddr5.drvqa.0929net/test/dca_mrw_clksync_1021_1.x8_9200 怎么解决log的问题`
- U#1: `我看package没有改动`
- U#2: `那现在是不需要修改，直接重新run就可？`
- U#3: `清缓存不会影响其他人吧？是否只会影响本用户的工作区`

## agent 分析过程 (trace 可见)
1. list_allowed_files dca_mrw_clksync_1021_1.x8_9200/ → A_Pattern_Sim.v, config, ncsdfc.log 等
2. read agent-policy.json (run_approved_command/profiles, writableRoots=/home/ruisongs)
3. check_log.py 扫 xrun.log (5.66MB / 101942 行) → `*E,ELBERR` elaboration error
4. scan_log.py grep error → L101937 `xrun: *E,ELBERR: Error (*E) or soft error (*SE) occurred during elaboration (status 1), exiting.`
   L101934 `xmelab: *E,DLCSMD: Dependent checksum verilog_package worklib.ddr5_package:sv (VST) doesn't match with the checksum that's in the header of: module worklib.real_wl_gen:sv (VST).`
5. invest_dlcsmd.py 查源文件 mtime: ddr5_package.sv mtime=2026-09-14 (未改), real_wl_gen.sv 路径缺失, ddr5_tasks.sv mtime=2026-10-20
6. find_caches.py 找 compile-cache: build_file/noregression_noarray.x8/xcelium.d/worklib (mtime 10-21 14:16), test/noregression.x8/xcelium.d
7. read rerun.sh / sync.sh (vsim --msierun -d "...TEST_9200" -sr dca_mrw_clksync)
8. 结论: DLCSMD = Xcelium 增量编译缓存(worklib)过期, package 重编 checksum 与 cached module header 不符 → 非 source bug, 清 xcelium.d/worklib 重 run; 缓存属主 ruisongs (uid 201211) = 本用户私有, 不影响他人

## 关键事实 (checkable gold)
- tool: xrun (xrun(64) 23.09-s003)
- failing_step: xmelab (elaboration)
- primary_error_code: DLCSMD
- elaboration_error_code: ELBERR
- stale_package: ddr5_package (verilog_package, 源码 mtime 2026-09-14 未改)
- mismatched_module: real_wl_gen (module, header checksum 不符)
- dlcsmd_count: 1 (单条 DLCSMD 行)
- root_cause_class: stale_compile_cache (增量编译缓存过期, 非 source bug)
- source_modification_needed: False (package 未改, 清缓存重 run 即可)
- cache_paths: xcelium.d/worklib, test/noregression.x8/xcelium.d
- cache_is_user_local: True (属主 ruisongs, 单一 owner = run owner, writableRoots=/home/ruisongs)
- package_unchanged: True (U#1 用户确认 + mtime 证据)

## 判定: 可造 → r849 落库
- 形态: debug-Q&A, specificity-oracle (具体错误码/package/module/根因类/处置), refuse-to-hallucinate (B 不同 package/module)
- A档不可行: /rundata/drvqa/ /proj/drvqa/ 对 e0031982 评测沙盒账号在内网机不可达 (cadmin 组权限, 同 r844 jeij7/r845 l4tre/r846 iyyzq/r848 5szsv 模式); trace agent read_files/run_approved_command 完整返回 xrun.log 报错行+源文件 mtime+cache listing, gold 完整可见
- → B档 synthesized reframe: 忠实于 trace DLCSMD 报错结构 (xmelab *E,DLCSMD ... verilog_package worklib.<PKG>:sv (VST) doesn't match ... module worklib.<MOD>:sv (VST) + *E,ELBERR exit), 自包含小型 fixture
- fixture A (可见, 反硬编): package=ddr5_package, module=real_wl_gen, build=build_file/noregression_noarray.x8, owner=ruisongs (忠实 trace 真实值)
- hidden B (判分, 结构不同): package=lpddr5_specdef, module=dqs_osc_ctrl, build=build_file/noregression_array.x16, owner=wenzhud, 不同日期/size
- check 15 条独立断言 (k=15/15 ≥8): ①zip含analyze_dlcsmd.py非空壳 ②py_compile ③B上exit0+合法JSON ④failing_step=xmelab ⑤primary_error_code=DLCSMD ⑥elaboration_error_code=ELBERR ⑦stale_package=B(lpddr5_specdef) ⑧mismatched_module=B(dqs_osc_ctrl) ⑨dlcsmd_count=1 ⑩root_cause_class=stale_compile_cache ⑪source_modification_needed=False ⑫cache_is_user_local=True ⑬recommended_action提及清xcelium/worklib缓存+re-run ⑭package_unchanged=True ⑮反硬编:跑A产出A的ddr5_package/real_wl_gen(击败硬编B stub) + 3seed打乱B日志非DLCSMD行count/package/module稳定
- 自验: ref PASS 15/15 + 3 neg(empty→①/print_expected→⑮硬编B/核心del→⑨)全FAIL + §4.9(a)(b)(c)三假提交全FAIL + neg_hardcoded_A→⑦FAIL
- jsonl test 字段 sha == disk check.py sha byte-identical (f411b150...)
- A.jsonl 419→420, cases/A +1, ledger A ui4hv parked→case (case 407→408, parked 278→277)

## 同批深读的其他候选 (r849)
- uqvno (zhengc, mc120, digital, "where setup/hold defined+give datapath" analysis-Q&A): 旧判 REJECT 复活候选, 但 10.129.8.104 sessions dir 仅剩 11-19 swt49, uqvno(11-12)已被 rotation 删除, subdir-path 亦无 → 不可造(NOFILE rotation蒸发), parked
- 7oy74 (thomas1w, mc39, digital, "循环8次log只有7次" debug): subdir ALIVE 291KB/43msgs, agent 找到 irun.log 有 8 个"Sorted fail addresses" header (col_test2/col_test3 交替, total 5→10→15→20→25→30→32→32), 用户前提"只有7次"待核; 留下轮深读
- pits0 (johnl, mc52, digital, "看下仿真激励在哪里" analysis): subdir ALIVE 314KB, DDR5 drcoa TM_Processmonitor pattern 定位; 留下轮深读
