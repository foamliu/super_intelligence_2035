# Deepread: 1794790691672_mv4xp — FineSim postsim 诊断 (hung + diverged)

**session**: 1794790691672_mv4xp · **user**: zlhou @ hfeg0plg52 (10.129.35.68) · **mc**: 16 · **domain**: spice_sim
**trace**: 312KB / 27 msgs / 2 user turns · **claimed**: r869 (2026-11-19)
**DEBT**: r869 deepread 完成，合成 deferred 到 r870（r869 预算被 MEMORY 瘦身消耗）

## 真实任务（用户原话逐字）
- U#0: 「查看目录 /proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/autosim/RESULT/postsim/1024X72M4B4C1_420/sf_0p6v_125c/CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS 下的文件，这个目录中提交的仿真跑了三天还没动静，看看是什么原因」
- U#16: 「再看一下 /proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/autosim/RESULT/postsim/1024X72M4B4C1_420/fs_1p02v_m40c/CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS 中的仿真，看看有什么错误」

**两角后仿诊断**：1024×72 SRAM (CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS) postsim，两个 PVT corner。
- sf_0p6v_125c (slow/0.6V/125°C)：**HUNG** — 跑 3 天无进展
- fs_1p02v_m40c (fast/1.02V/-40°C)：**FAILED** — 发散

## agent 工具链
list_allowed_files → read_files(job_info.json/.sp/.log/submit_bsub.log/.elog) → editor check_sim_job.py → run_approved_command (bjobs -l 查 LSF job CPU) → read_files(.log 尾部/.sp deck/.mt0/.err0)

## agent 诊断结论（verbatim 关键）
### Sim1 (sf_0p6v_125c, job 2663681) = HUNG
- job_info.json: status=RUNNING, start_time=2026-11-13 16:59:56
- bjobs -l: 累计 CPU 625 秒（64h），CPU 效率 0.02%，峰值 6.35%；MEM 16.2G(峰值31.7G)；NTHREAD=7，PGID 下 5 PID
- .log 卡在 line 470 "expand probe" 阶段：`.tran 10ps 30n` 全网表后仿；`.probe v(*) level=11` 匹配 **5,195,412 节点**；post-layout .spf（_420.spf:5783953 / :17660698 千万行引用）
- 无 .fsdb，measure/ 空 → DC/tran 未真正开跑
- 返工史：job 2654708 (11/13 16:10) 快速失败 `ERROR! can't be found .lib entry 'sf_diode_bjt_res_fs' (sp:79)`；2663681 越过该错但卡死
- 根因方向：分布式并行握手/partition 死锁（finesim_parallel=distributed + finesim_accelerate=3 + 5M probe + 千万行 SPF），非计算中
- 处置：bkill 2663681；减小 probe 范围；去 distributed 先单机验证；核对 finesim_threads=32 vs bsub -n 16 不一致

### Sim2 (fs_1p02v_m40c, job 2663691) = DIVERGED
- job_info.json: status=**FAIL**, 错误 `CXN4...FS.log: ERROR! time step too small (diverged)`
- .log 尾部：
  ```
  Starting DC Initialization ...
  WARNING! DC not converged
  End of DC Initialization
  WARNING! dc min val (-81408.4)  at node port:xtop.vdd:1282753 might be abnormal
  WARNING! dc max val (1.60371e+06) at node xtop.xbkt.xbkt_l.xarrayl.xr4.xc64.xiw0b1.bt:6 might be abnormal
  Starting Transient Analysis ...
  ERROR! time step too small (diverged).
         diverged at node: "xtop.vdd:1608177" / 1608198 / 1608292 / 1608236 ...
      finished at 2ps (tstop = 30ns) by error
  ```
- 跑了 1h44m, 74771 CPU 秒, 31GB MEM（与 Sim1 对比：真在算）
- 网表规模：694,480 MOSFET / 16,566,102 R / 45,979,805 C；5,195,417 probe / 534 measure
- 30,554 条 `layout-only device gate node '...:t2' is floating` 警告
- .mt0: 534 measure 全 error；.err0: 72 向量比较错 (q[71:0] sim=0 expected=1)
- 根因：DC 不收敛（vdd 节点非物理 -81408V/+1.6e6V）→ transient 从非物理态起步 → Newton 发散 → time step too small @ 2ps；floating gate (30554) 加剧
- 处置：解 DC 收敛（查 floating gate SPF 连接）；gmin 1e-13→1e-9；finesim_method gear→trap；.ic 种子 vdd/vss；先跑 DC+短 tran(1ns) 验证

## reframe 计划（r870 合成 · harness-for-teeth · Q&A/diag → produce）
**case 名**：EDA-Eval-DesignFlow-FineSimPostsimDiag-001
**真任务形态**：诊断 FineSim postsim 状态/错误（hung vs diverged vs completed）
**reframe driver**：harness-for-teeth（Q&A/diagnosis → produce 可复用诊断脚本）
**produce**：`finesim_postsim_diag.py`(--simdir/--outdir argparse)，解析 sim 目录的 job_info.json + wave/*.log + *.sp，分类状态并提取错误：
  - 解析 job_info.json: status / start_time / cpu_time / error
  - 解析 .log: 阶段标记(expand probe / Starting DC / Starting Transient) + "DC not converged" + "time step too small (diverged)" + diverged node + "gate node ... floating" 计数 + probe 节点数 + dc min/max val abnormal
  - 解析 .sp: .option finesim_parallel / finesim_threads / GMIN / finesim_method / .probe / .tran tstop
  - 分类: HUNG_AT_INIT (status=RUNNING + log 卡 expand probe + 无 tran 起 + CPU效率<1%) / DIVERGED (status=FAIL + "time step too small" + DC not converged) / COMPLETED (status=PASS + .fsdb + measure 有值)
  - 输出 diag_report.json {classification, error_type, diverged_node, cpu_efficiency_pct, probe_count, floating_gate_count, dc_abnormal_voltages, stage_frozen, remediation_hints}
  - 纯 python 无 EDA 二进制 → layer=L1
**asset A** (format-faithful)：design_A 目录 = 两个 corner 子目录(sf_0p6v_125c=HUNG, fs_1p02v_m40c=DIVERGED)，各含 job_info.json + wave/*.log(verbatim 关键行) + *.sp(verbatim options) + submit_bsub.log — 按 trace msg verbatim 重建（真实 /proj/lacaa 权限/PDK 敏感，按 agent 读到的内容重建）
**hidden B** (结构性差异 7 维度)：不同设计名(ROM2K×16 vs SRAM1024×72) / 不同 corner(tt_1p1v_25c=COMPLETED + ss_0p9v_85c=HUNG_AT_DC) / 不同 error_node / 不同 probe_count / 不同 floating_gate_count / 不同 .option 值 / 不同 stage_frozen；B2=anti-stub(COMPLETED 角，0 err)
**check** (真跑候选在 hidden B+B2, k≥14): a 无泄漏 b py_compile c argparse齐全 d 跑B产 diag_report.json e JSON结构 f B ss 角分类=HUNG_AT_DC g B tt 角分类=COMPLETED h B diverged_node == B 特有 token i B floating_gate_count == B 值(非A) j B cpu_efficiency < 1% for hung k B probe_count == B 值 l report 引用 B 特有 token(ROM2K/非A token) 防 hardcoded-A m anti-stub B2 COMPLETED 角 0 err n 代码实质≥25行+argparse+不硬编A o 确定性3次一致
**5 negatives**: empty_shell / print_expected / hardcoded_a / core_deleted / no_classify_stub — 全 FAIL
**asset_fidelity**: A=format-faithful（.log/.job_info/.sp 按 trace verbatim 内容重建；真实文件 PDK/权限敏感）
**track**: faithful · **domain**: spice_sim · **tier**: B · **layer**: L1
**k_check = k_rationale** (≥14, 对齐 §4.3 ≥8 + §4.9 三假提交回归)

## r870 首件指令
1. 用本 deepread 合成 FineSimPostsimDiag-001
2. assets/ + reference/ + hidden/ + negative/ 走既有 casemaking 流程
3. 自验 ref PASS + 5 neg FAIL + §4.9 (a)(b)(c) 三假提交 FAIL
4. 追加 EDA-Eval-DesignFlow_B.jsonl + ledger_B mark 1794790691672_mv4xp --status case --case-id EDA-Eval-DesignFlow-FineSimPostsimDiag-001
5. trace 312KB 已 scp 到 .75 session workdir (default_designflow-B_shardB-r869_0/mv4xp.messages.json)，r870 可重 scp 或复用
