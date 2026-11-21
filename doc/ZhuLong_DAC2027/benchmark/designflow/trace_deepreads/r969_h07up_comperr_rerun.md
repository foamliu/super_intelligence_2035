# r969 — h07up CompErrRerunGen (jkxu @ hfhds209)

## Trace
- session: 1795177578887_h07up.messages.json (jkxu @ hfhds209, mc=165, A-pure verification 域)
- trace ALIVE: /home/jkxu/.cline/data/sessions/1795177578887_h07up/...messages.json, 735KB / 188 msgs
- scp'd full trace to eda_flow workdir for deepread

## User intent (verbatim, 3 turns)
- U#0: 「vsim_report ... --genrerun 是生成需要rerun的job命令，看下能否扩展下 抓取 存在编译错的job 然后生成rerun 脚本；log.reg.1118/24Gb/Legacy 比如这个下面的」
- U#142: 「速度有点慢，是因为全量搜索xrun.log全文导致的吗」
- U#174: 「还是很慢，直接搜索xrun.log 最后10行看没有 *E这个关键字就好来」

## Session主线
jkxu 维护 DDR5 回归平台 verilog.ddr5.drcpa.post_2nd_rev。已有 perl `bin/vsim_report`
(--genrerun 生成 rerun job)。用户要扩展它抓**编译错误** job。agent 用 editor 改 perl
vsim_report.v2: 递归 walk log 目录找 xrun.log → 滑窗读最后 N 行 → grep `*E` → 生成 rerun
脚本。用户两次催性能后明确「只看最后 10 行 *E」。agent perl -c 校验 → cp 部署 vsim_report。

## Case reframe (§5 produce-task, B档 trace-faithful)
交付通用 `find_comperror_jobs.py <log_dir> <output_rerun.sh>` (stdlib-only):
- 递归遍历 log_dir, 每个含 xrun.log 的目录 = 一个 job
- 滑窗读 xrun.log **最后 10 行** (禁止 .read()/.readlines() 整文件)
- 含 `*E` 标记 → 编译错误 job → 进 rerun 列表
- 早期 *E (不在最后10行) 不计; *W/*F 不计 (只抓编译错误)
- 输出 bash rerun 脚本 (shebang + `cd "<job>" && bash run.sh` per flagged job, 排序)

## Assets
- A = reg_dir_A.tar.gz (3 job: job_A1_basic_read 编译错误[最后10行含*E] / job_A2_write_test
  早期*E第5行不在最后10行[PASSED] / job_A3_refresh 仅*W), 可见附件
- hidden B = check.py 内联 _build_b (4 job: job_B1_mrs_cal 编译错误 / job_B2_zqcal clean /
  job_B3_train 早期*E+tail *F / job_B4_preshape 编译错误), 期望 2 flagged

## check.py (18 断言, k=18)
①zip+script≥150B ②py_compile+stdlib ③argv读路径无硬编码 ④A exit0+非空 ⑤A shebang
⑥A flag job_A1 ⑦A 不flag job_A2(早期*E) ⑧A 不flag job_A3(仅*W) ⑨A count=1 ⑩B exit0+非空
⑪B flag job_B1 ⑫B flag job_B4 ⑬B 不flag job_B2(clean) ⑭B 不flag job_B3(早期*E+*F) ⑮B count=2
⑯反硬编码(B无A名) ⑰确定性 ⑱B cd行数=2

## Self-verify
- reference PASS 18/18
- NEG-a (§4.9a empty) FAIL ①
- NEG-b (§4.9b print-expected, hardcode A job) FAIL ③
- NEG-c (§4.9c core-deleted, flag all) FAIL ⑦

## 选料注
- r969 mc≥10池 (shard_mc.A=10). 扫描 ssh_eda_search_20261121_151844/summary.tsv 39300行
  A-keyword awk 过滤 → 3197 A-kw 候选 → Python A-pure 过滤 (A_sum>non_A AND A_sum>0.4*total
  AND A_sum≥20) → 549 A-pure sids → 交叉 4-shard ledger → 57 fresh.
- top fresh (mc desc): w4x70(haoyut mc1576) 已cased; 40uq0(mos_compara B/D); ppl5a/fieju
  已cased; 86t8o/jzlbn/ve67l/lond8/xt9ag/evxj6/eoxs4/8ylkn/1yqtd/qv6pl/yk8qc/k7668 已cased;
  06htj/3s3zx/2ntgh/jr2g5/n1tmq/nphvz parked.
- e02141 cluster = Sentaurus TCAD (wrong-shard), 排除.
- xzcak/ibtdi (rose3wang mc144, verilog壳子from pin table) = DUP of existing
  VlogShellWrapGen-001 (line 375, 同 rose3wang efuse pin-table, session l3qi7) → parked.
- h07up (jkxu mc165, 扩展 vsim_report 抓编译错误 rerun) = clean A-domain verification
  produce-task, 3-turn 用户意图清晰 (含 tail-10 性能约束), selected.
- 其余 fresh (cozge/77z85/3ieaa/or2tj/2cfmj/j3gn0 等) 多为 analysis/Q&A 或 TCAD, 不适合
  produce-task.

## ⚠️ 工作树脏状态处理
- 发现工作树 A.jsonl 被 revert 到 433 (HEAD 有 440, 丢 r963-r968 共7 case) + EfusePinShellGen/
  LdoRefLoadStepStimGen 等 committed assets 被删。`git restore benchmarks/EDA-Eval-DesignFlow/`
  恢复到 HEAD (440), 再 append 本 case → 441.
