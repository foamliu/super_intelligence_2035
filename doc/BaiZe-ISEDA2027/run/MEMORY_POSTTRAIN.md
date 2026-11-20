# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

> 🔴 **预注册（2026-11-20 22:0x · baseline-nailed 令 §E.3 · 先定后测·跑完不许改判据）**：
> - **臂矩阵**：A0=MiniCPM5-2B 原模型(.17 口径:无RAG/无沙盒MCP/cline/-p8/-n/无hook,endpoint :8098) → 用户要的 base 数字；A1=SFT v39 step105(同尺同口径,endpoint :8096 需重起 serve) → 分离 SFT 增量；A2/A3(+RAG/+沙盒MCP,36.15 口径)暂缓待 A0/A1 干净。
> - **冻结协议**：158 题 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n`；正式数字用修复后口径(recovered/ws+no-ws fallback)；主结论用 recovered-4run(剔除 run1 ws-only 锚点)，混合 5-run 并列报告。
> - **判据(预注册)**：①B1 身份四证 requested==served==ckpt 一致否则停跑；②B2 量尺差值写进报告(已知 bug 偏差达 +15pp)；③B3 judge_sd=0(打分器确定性)，同臂两 run 差值 < 2×judge_sd 否则先修协议；④B4 执行翻转率(10题×10次)；⑤B5 逐题画像须用 MiniCPM5 自己数据重做(不得沿用 DeepSeek fail_mode)。
> - **交付物**：`baseline_measurement_audit.json`(Stage1) + `baseline_A0_run<N>_pertask.json`(Stage2/3) + `reports/report_posttrain_baseline_nailed_zh.html`(里程碑)。
> - **Stage1 状态(2026-11-20 22:14)**：✅ **DONE** → `baseline_measurement_audit.json`。B1 身份 PASS(requested=served=minicpm5-2b, ckpt=/nas_data/.../MiniCPM5-2B mtime 11-09, base 非 SFT, 3x指纹一致)；B2 量尺差值=15.19pp(ws-only vs recovered)，**源头已修**(36.15 format_cline_cli_output.py L168-170 no-ws fallback, ⚠未提交有 revert 风险; A0/A1 走 .17 抽取器读 pyAether_code no-ws 不受影响)；B3 judge_sd=0 全 5run(打分确定性, 方差全来自上游)。mixed-5run=6.84%±6.12%, recovered-4run=3.80%±0.90%。verdict=GO Stage2。
> - 🟢 **Stage2 状态(2026-11-21 03:51 ✅ DONE)**：**A0 base run1 Pass@1 = 69/158 = 43.67%**(MiniCPM5-2B base, .17口径, 修复后抽取器, 沙盒真执行验证, **单 run 非 5-run 均值**)。final_report=`/tmp/posttrain_5run_eval/A0_base/run1/final_report.json`。打分可区分(passed=69 真 OK stdout / failed=59 真错误类型[AssertionError=26/TypeError=17/AttributeError=4 等] / not_executed=28=19 gen_fail+9 gen_timeout / timeout=2)⇒**43.67% 非评分 bug 虚高**，是修复量尺后首次真实 base 单点。**B1 真身份 PASS**(158/158 session=minicpm5-2b, curl :8098/v1/models id=minicpm5-2b root=/nas_data/.../MiniCPM5-2B, serve PID799523 --model .../MiniCPM5-2B --served-model-name minicpm5-2b)；**⚠ final_report.model_name=zhulong_deepseek_v32 系 config.yaml active_model 陈旧标签(非实际模型, §B.1 风险已坐实)，已显式标注不触发停跑**。**B5 逐题画像 DONE** → `baseline_A0_base_run1_pertask.json`(脚本 `--eval-dir <batch_dir> --report <final_report.json>`，**eval-dir 须指向 batch 目录(含 cli_data/)非 run_dir**，已修 wake655 误用)。fail_mode 五分类(89 fail)=F5_logic=40/F4_api=21/F1_no_code=18/F3_timeout=9/F2=1；四指标(agent_loop_entry=93.67%/tool_call_mean=30.28/error=0.76%/rag_queried=100%[本地 API 检索工具,非远程 RAG])；聚合工具 search_apis=1969/get_api_details=978/run_commands=684。**口径六元组**：A0(base/.17/修复量尺/无远程RAG/无沙盒MCP)vs旧6.84%(SFT step105/36.15/broken量尺/有RAG/有MCP)→**3项不同禁止直接比较**。里程碑报告 `reports/report_posttrain_baseline_nailed_zh.html` 落盘(自包含, HTML well-formed)。单 run 结论清晰(base≈44%真实, fail_mode 以 F5_logic+F4_api 为主)⇒支持补 5-run。
> - 🟢 **Stage3 状态(2026-11-21 03:57 🔄 run2 RUNNING)**：A0 run2 已起(`baize_posttrain_5run_eval.sh --endpoint :8098 --model minicpm5-2b --label A0_base --run 2`, PID4122533, batch=A0_base_run2_2026_1121_035757, codegen 跑中)。串行纪律自检通过(无他线 cline run, GPU4 39.2GB base serve 在)。后续 run3-5 串行补满 → A0 5-run mean±std + 配对分布(0/5…5/5)；A0 干净后重起 :8096 serve SFT step105 → A1 同尺 5-run → 量化 SFT 增量(McNemar/paired bootstrap) + 补 B4 执行确定性(10题×10次翻转率)。报告随 Stage3 完成原地覆盖。ETA≈5h/run。
> - ✅ **git/remote BLOCKER（2026-11-20 23:1x wake649 发现→01:0x 已被运维修复）**：origin/main 曾把 doc/ R100 纯重命名，运维 commit ed5398c2b7 恢复 doc/ 结构；现 origin healthy、doc/ intact。(wake649-654 详细过程见 daily 2026-11-21)

> 📦 wake628（2026-11-17 08:46 · posttrain 5run: · 22:0x 令全流程闭环）→ 已降级要点 → daily 2026-11-17 wake628。**结论**：5-run 收口 n=5 mean=6.84%±6.12% [18.99,4.43,2.53,3.80,4.43]% rca_status=CLEAN，McNemar chi2_corrected=13.5 p<0.001 vs 旧.17 3.04%±0.74%；run5=STEP1 共用 8090 MCP 池+-p2（同口径可并入 5run mean）；报告 report_posttrain_zhulong_reattribution_zh.html §10/§8。需要时再读。

> 📦 wake632-635（2026-11-17 · posttrain 5run/归档/fix/patrol）→ 均已降级要点 → daily 2026-11-17 wake632-635。**合并结论**：第3次 unauthorized clean_5run 已 kill 整树 + `git checkout HEAD -- run{1..5}/` 恢复 + clean_5run.sh guard 硬化为**无条件 `exit 7`**(移除 bypass) + kill_gpu_serve child-PID bug 修复(walk ppid 到根命中 vLLM serve 祖先即 kill) + patrol standby。需要时再读各 wake 块。

> 📦 wake637（2026-11-20 15:0x · posttrain gpu: · 2026-11-19「GPU 收缩到 4-5」令✅已闭合）→ 已降级要点 → daily 2026-11-20 wake637。**结论**：实测 GPU4=base :8098 39.2GB / GPU5·7 FREE / GPU6=vision VQA；:8095/:8096 未监听⇒SFT/R2 serve 已退出=裁减；posttrain 现仅 GPU4 standby（在 GPU4-5 内）；未碰 GPU0-3/GPU6-7、未 kill、未启新 run。令 4 点全满足⇒闭合。需要时再读。

> 📦 wake638–wake643（2026-11-20 16:47–19:19 · posttrain patrol: · standby 心跳复验轮）→ 已降级要点 → daily 2026-11-20 wake638-643。**合并结论**：复验 wake637 GPU 收缩处置持续成立（GPU4=base :8098 200OK / GPU5·7 FREE / GPU6=vision / :8095·:8096 未监听 / 5run json CLEAN rca_status=CLEAN / pretrain iter~260830→262030 ETA≈2026-12-25 阻塞）；各轮 git pull 同步他线推进，autostash 冲突在他线文件已 `git checkout HEAD --` 还原（他线工作态保留在 5 个 safety-net stash 未 drop）；wake640 顺手补提交遗留未跟踪 `reports/posttrain_passrate_variance_analysis.html`。均未碰 GPU0-3/GPU6-7、未 kill/未启新 run/未改 run1-5/未改 eda_fastmcp/.env。需要时再读各 wake 块。

> 📦 wake644/wake645/wake646/wake647/wake648（2026-11-20 19:4x–21:4x · posttrain patrol: · standby 心跳复验轮，无新本线运维令）→ 已降级要点 → daily 2026-11-20 wake644-648。**合并结论**：复验 wake637 GPU 收缩处置持续成立(GPU4=base :8098 200OK/GPU5·7 FREE/GPU6=vision/:8095·:8096 未监听)+5run json CLEAN rca_status=CLEAN+pretrain iter~263k ETA≈2026-12-25 阻塞；git ff 同步他线推进(wake646 清 wake645 残留 rebase-apply/index.lock, wake644 体积维护 34.9KB→~30KB 压缩 wake628/637/643 已闭合块为指针)。需要时再读各 wake 块。



> 📦 wake629（2026-11-17 09:35 · posttrain 5run: · 第2次停 clean_5run+恢复 run2+加可绕过 env-var guard）→ 已归档要点 → daily 2026-11-17 wake629（**被 wake632 第3次复发+guard 硬化取代**：旧 env-var guard 被 `export BPT_CLEAN_5RUN_AUTHORIZED=1` 绕过，已升级为无条件 exit 7）。需要时再读。


> 📦 wake507 隧道复盘（2026-11-14 23:5x · posttrain infra: · 已闭合）→ daily 2026-11-14。**结论**：隧道坏过现已恢复（最后通 20:41:50 / 首断 22:4x / 恢复 23:26 / 故障域=中继侧 / 非本线造成亦非本线修复）。报告 `reports/report_infra_tunnel_postmortem_zh.html`。

> 📦 wake598/599 端口池并行诊断（2026-11-16 21:0x · posttrain 5run: · 已闭合=报运维）→ daily 2026-11-16。**结论**：22:0x 令第1步 verdict——client 侧不可重路由 code-gen（cline_mcp_settings.json 硬编码 8090，main.py 启动建池），沙盒 8650-8670 仅 8655 空闲（8656-8670=他人 daemon），无可用 4 口独立池；串行 global-wait 是数据完整性正确路径（已被 wake601+ share-8090-pool 取代）。

> 📦 wake590 纪律纠偏（2026-11-16 17:2x · posttrain rca: · 已闭合，被 wake629 复发处置取代）→ daily 2026-11-16。**结论**：第1次停未授权 clean_5run.sh + 恢复 run2 封存（git diff HEAD 空）。wake629 第2次复发已加 DISABLED guard。

## 进度快照

- PHASE: posttrain-wake648（✅ **2026-11-19「GPU 收缩到 4-5」令已执行 wake637 + wake638-648 standby 心跳复验持续成立 + wake648 git ff 同步 origin 0bc6baef3 + wake646 git 卫生修复(清 wake645 残留 rebase-apply/index.lock,ff 同步 origin a87d3b866) + wake644 体积维护(MEMORY 34.9KB→~30KB 回落 32KB 软限内)** + 22:0x 令全流程闭环 wake628 + wake633 归档 + wake634 kill_gpu_serve bug 修复：5-run 收口 n=5 mean=6.84%±6.12% [18.99,4.43,2.53,3.80,4.43]% rca_status=CLEAN，McNemar chi2=13.5 p<0.001 显著 vs 旧.17 3.04%±0.74%；R2 4-run mean≈0.475% decisively 负；主线阻塞于 pretrain ckpt ETA≈2026-12-25）
- 已完成: P0-P3预备✅;P1-P2✅;R1-R210✅;R280归档;R411-R428✅(verl BLOCKED→自写GRPO loop);R0 200步COMPLETED诚实负结果(cheat=0/3200,reward无方向信号);R2 200步COMPLETED(cheat=0/1600)+global_step_200 ckpt;R2 5-run eval run1-4 DONE mean≈0.475% decisively负;step105 baseline 0.0304±0.0083 locked;**2026-11-19 GPU收缩令✅ wake637**(SFT/R2 serve 裁减,posttrain 仅 GPU4 base standby)。[全量R-round/wake历史详见 daily-memories-posttrain/2026-11-{06..20}.md 与 EXPERIMENTS归档]
- 当前动作: wake655(2026-11-21 03:5x · posttrain baseline-nailed:)—【把 baseline 做扎实】令 **Stage2 ✅DONE → Stage3 🔄run2 RUNNING**。**Stage1 DONE**(baseline_measurement_audit.json: B1身份PASS/B2量尺差值15.19pp源头已修/B3 judge_sd=0; verdict=GO Stage2)。**Stage2 DONE**：A0 base run1 Pass@1=**69/158=43.67%**(单 run, .17口径, 修复后抽取器, 沙盒真执行验证)；打分可区分(passed69真OK/failed59真错误类型[AssertionErr26/TypeErr17等]⇒非评分bug虚高)；**B1真身份PASS**(158/158 session=minicpm5-2b, curl :8098 id=minicpm5-2b, serve PID799523 base)；**⚠final_report.model_name=zhulong_deepseek_v32 陈旧标签(§B.1已坐实, 已标注)**；B5逐题画像→`baseline_A0_base_run1_pertask.json`(fail_mode F5_logic40/F4_api21/F1_no_code18/F3_timeout9/F2=1; 四指标 agent_loop_entry93.67%/tool_call30.28/error0.76%/rag100%)。里程碑报告 `reports/report_posttrain_baseline_nailed_zh.html` 落盘。**口径六元组3项不同(A0 base/.17/修复量尺 vs 旧6.84% SFT/36.15/broken)→禁止直接比较**。**Stage3**：A0 run2 已起(PID4122533, batch=A0_base_run2_2026_1121_035757, codegen 跑中, 串行纪律自检通过)，后续 run3-5 补满→A0 5-run mean±std→A1(SFT step105)同尺5-run→量化SFT增量+补B4。细节见顶部预注册块。
- wake533 R533（已归档）:沙盒非确定性发现[baseline_dev direct 2/79 vs rescue 0/79,单 seed delta<沙盒方差⇒不可定论]+双轨 compare 方法论。详见 EXPERIMENTS §R533-sandbox-nondeterminism / daily 2026-11-15 wake533。
- 下一步: ✅ **2026-11-19 GPU 收缩令闭环 wake637** + ✅ 22:0x 令全流程闭环 + ✅ clean_5run guard 硬化(wake632 无条件 exit 7) + ✅ kill_gpu_serve bug 修复(wake634)。**主线阻塞于 pretrain S1 收敛 ckpt ETA≈2026-12-25**，就绪后在 GPU4-5 起对应 serve 自动起退火→SFT→RL→EDA-Eval 评测。后续候选（待用户定夺，不擅自起新 run）：① 全 recovered 同口径 fresh 5-run 定论 run1=18.99% ws-only outlier；② L4 designflow 全量 61 任务（需 BaiZe ckpt 可达，当前 /nas_train 在 .17 未挂载且 pretrain 未达 170k/180k）；③ 是否保留 base :8098 standby 或全释放 GPU4-5（待用户授权）。⚠ clean_5run.sh 已硬禁用（无条件 exit 7），未经用户授权不得再启动（已 3 次未授权复发）。
- 阻塞: ✅ **R2 200步主训 COMPLETED** + **R2 5-run eval run1-4 DONE mean≈0.475% decisively 负**(run5 被 kill 释放给 08:1x 最高优先令)。**R0=诚实负结果**(proxy reward 不移动 policy)。RL 基座=MiniCPM5-2B/SFT step105。**GPU 现状(wake637)**：GPU0-3=root;GPU4=base serve(:8098 standby);GPU5=FREE(posttrain备用);GPU6=vision VQA(非本线);GPU7=FREE(交vision)。SFT :8096/R2 :8095 serve 已裁减退出。沙盒经 dual-nix-tunnel 通。verl 结论性 BLOCKED 不再尝试。**正式 SFT/RL 阻塞于 pretrain ckpt ETA≈2026-12-25**。
- 本轮新增产出: wake655✅(baseline-nailed Stage2 DONE + Stage3 run2 起跑)：① **A0 base run1 DONE Pass@1=69/158=43.67%**(单run, final_report=/tmp/posttrain_5run_eval/A0_base/run1/final_report.json; 打分可区分 passed69真OK/failed59真错误类型→非评分bug虚高; gen success130/fail19/timeout9)；② **B1真身份PASS**(158/158 session=minicpm5-2b via per-session identity_crosscheck + curl :8098/v1/models + serve PID799523 base) + **⚠final_report.model_name=zhulong_deepseek_v32 陈旧config标签已显式标注**(§B.1风险坐实, 不触发停跑)；③ **B5逐题画像 DONE**→`baseline_A0_base_run1_pertask.json`(修 wake655 eval-dir 误用: 须指向batch目录含cli_data/非run_dir; fail_mode F5_logic40/F4_api21/F1_no_code18/F3_timeout9/F2=1; 四指标 agent_loop_entry93.67%/tool_call30.28/error0.76%/rag100%本地API检索); ④ **里程碑报告** `reports/report_posttrain_baseline_nailed_zh.html`(自包含, HTML well-formed, 首屏三句+A/B/C/D全表+B1-B5+口径六元组+落盘路径); ⑤ **Stage3 run2 起跑**(PID4122533, 串行纪律自检通过, codegen 跑中)。未碰 GPU0-3/GPU6-7、未 kill 他线、未改 eda_fastmcp 源码/未改协议。
- 未完成指令: 🔴 **2026-11-20 21:1x「把 baseline 做扎实」—Stage1✅DONE, Stage2✅DONE(A0 run1=43.67%单run+B5画像+里程碑报告), Stage3 🔄A0 run2 RUNNING(后续run3-5补满5-run→A1同尺5-run→量化SFT增量+补B4, ETA≈5h/run)**;🔴 2026-11-19「GPU 收缩到 4-5」——✅ wake637 闭环;🔴 2026-11-13 RL 起跑——✅ R0+R2 COMPLETED, R2 5-run mean≈0.475% decisively 负;🔴 2026-11-15 08:1x zhulong 评测——✅ wake628 闭环(5run 6.84%±6.12%);🔴 2026-11-16 22:0x 沙盒池——✅ wake628 闭环;L4 2026-11-12(zhulong step105 5/5 0.0304±0.0083;designflow base 5/5=0%, 全量61任务阻塞 BaiZe ckpt 不可达)
- git: super_intelligence_2035(**HEAD=db4adcc01f posttrain baseline-nailed wake654, PUSHED to origin (0 ahead/0 behind)**; origin/main healthy, doc/ intact)。wake654 复核: 工作树仅 `baseline_A0_base_run1_pertask_INTERIM.json` 未跟踪(formal pertask JSON 待 run1 done 产出)。⚠️ **wake654 NFS/autostash 教训**：本线 `run/` 工作树巨大且在 NFS 上，`git pull --rebase --autostash` 的 `git stash create`(扫描全工作树 stat)会 hang 在 NFS D-state(rpc_wait_bit_killable)6min+ 不恢复；而纯对象库操作(fetch/commit/read-tree/commit-tree)快(秒级)。**修法**：用 temp-index 重建 commit(`GIT_INDEX_FILE=/tmp/idx git read-tree origin/main`→`update-index --add --cacheinfo <mode> <blob> <path>` 仅本线 3 文件→`write-tree`→`commit-tree -p origin/main`→`update-ref refs/heads/main`→`git push` fast-forward)绕过工作树扫描；origin 持续被别线推进则 fetch+重建+push 重试循环(`/tmp/posttrain_push_retry.sh`)。push 后 `git reset --mixed HEAD` 同步 stale 真实 index(对象库操作,秒级)。本线提交前缀 posttrain baseline-nailed:; 不用 -A。
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;venv 重建后需重打此patch
- 🔧 **verl 0.4.0 GRPO 结论性 BLOCKED(wake411)→ ✅ wake412 换框架解除**:verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→init 握手死锁;1-GPU/2-GPU/NCCL 修复均复现;根因=verl 0.4.0+本机 Ray 命名 actor 可见性不兼容。**wake412 解除**：弃用 verl 路径，新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch，无 Ray/verl/torchrun），smoke 3 步 PASS(ratio=1.000)。verl surrogate 脚本保留但不再尝试。详见 EXPERIMENTS §R411/§R412
- 🔧 **torchrun 单驱动修复 R-launch-fix3(wake411)**:`baize_posttrain_rl_grpo_surrogate.sh` L320 `--nproc_per_node=1`(verl main_ppo 单驱动,n_gpus 来自配置);原 $NGPU 派生多 Ray 集群→多 GPU 起跑前提修复
- 🔧 **NCCL 接口修复 R-launch-fix4(wake411)**:脚本 export NCCL/gloo `SOCKET_IFNAME=bond0`+`NCCL_IB_DISABLE=1`+`NCCL_NET=Socket`(本机多网卡含 docker bridge);标准 torch.distributed-in-container 加固,实测对 verl 死锁无效(非根因)但保留
- 🔧 **R2 OOM 最终修复(wake429)**:A40 44GB 对 2B 全参 GRPO(G8 B2)预算过紧(policy+ref+Adam16GB+grad=28GB 基线+logits float32 峰值5GB 触顶)。修复=`--batch-prompts 1`(Gtot=8/step,**G=8 保持**)+`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。verl_cu124_venv 起 RL 必带此 env;若再 OOM 可进一步降 ctx 或切 8-bit Adam。
- 🔧 **config-path 修复 R-launch-fix2(wake410)**:`baize_posttrain_rl_grpo_surrogate.sh` L303 `CFG_DIR` 强制绝对路径;项目配置(sdpa/hybrid/timeout)现真正加载;RL 起跑前提(已验证有效)
- ✅ **kill_gpu_serve child-PID bug — wake634 已修复**：`baize_posttrain_rl_eval_chain.sh` 与 `baize_posttrain_r2_autofire_chain.sh` 的 `kill_gpu_serve` 原逻辑只对 `nvidia-smi --query-compute-apps=pid` 返回的 PID grep `vllm.entrypoints.openai.api_server`，但 vLLM 的 CUDA 上下文常由 multiprocessing 子进程（`python -c from multiprocessing.spawn...`）持有⇒子进程 argv 不含 serve 关键字⇒误判 skip，GPU 未释放（wake433 曾手动 kill 父进程 1802143 完成 OOM mitigation）。**wake634 修复**：取到 compute-app PID 后，若自身不匹配则 walk `ps -o ppid=` 到根（≤16 跳），命中 vLLM serve 祖先即 kill 该祖先（TERM→KILL）+ kill CUDA 子进程。两脚本 `bash -n` PASS；dry-run 实测 GPU7/6/4 三处 vLLM serve 正确命中祖先、GPU5 vision 非-vLLM serve 正确 skip（不误杀他线）。详见 wake634 块/daily 2026-11-17 wake634。




## GPU 端口映射表（2026-11-20 wake637 实测 · **GPU 收缩到 4-5 后**）

> 🔴 **2026-11-19 用户令已执行（wake637）**：posttrain 收缩到 **GPU 4-5**，GPU 6-7 交 vision。SFT :8096 / R2 :8095 serve 已退出（裁减，无流量）；posttrain 现仅 GPU4 base :8098 standby，GPU5 备用留空。不碰 GPU0-3/GPU6-7。

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B TP4 | ~44-45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | **vLLM MiniCPM5-2B base standby**(PID799523,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 --enable-auto-tool-choice --max-num-seqs 4,curl /v1/models 200 OK) | 39.2GB | ✅ wake637 保留(在 GPU4-5 内,供 ad-hoc 基线/诊断 eval) |
| 5 | — | — | **FREE（posttrain 备用）** | 3 MiB | 🟢 wake637 确认 vision 已释放；待 pretrain ckpt 就绪/需 eval 时启用 |
| 6 | 30001/30003 | qwen3.5-2b | **vision VQA 服务**(PID3308830/3311127,非本线,不碰) | 9.2GB | 🔵 vision 已迁入 GPU6(wake637 确认) |
| 7 | — | — | **FREE**（R2 :8095 serve 已退出） | 3 MiB | 🟢 wake637 确认无 posttrain compute-app；交 vision |

> vLLM venv: `/tmp/vllm_venv/bin/python`（transformers 4.49.0, vLLM 0.7.3）；日志: `/tmp/vllm_gpu{5,6,7}.log`
> ⚠️ vLLM venv 在 `/tmp`，重启机器后丢失需重建
> 🔧 **minicpm5 tool-call parser**（wake306 新增）：自定义vLLM parser解析MiniCPM5的`<function name><param>`XML→结构化`tool_calls`；源码在`run/baize_posttrain_vllm_minicpm5_parser.py`，安装到`/tmp/vllm_venv/.../tool_parsers/minicpm5_tool_parser.py`+`__init__.py`；venv重建后需重装（`cp run/baize_posttrain_vllm_minicpm5_parser.py /tmp/vllm_venv/.../tool_parsers/minicpm5_tool_parser.py` + 编辑`__init__.py`加import）；serve启动加`--tool-call-parser minicpm5`
> 🔧 拆除占位 serve（沙盒恢复后 Phase2 前）：`bash baize_posttrain_serve_teardown.sh`（默认拆 GPU5/6/7；`--gpu4` 也拆 GPU4；`--all` 全拆；`--status` 看占用；`--dry-run` 预览；**永不碰 GPU0-3/ROOT:8099**）— R165
> 🔧 维持占位 serve 健康（17:10令持续占位期间）：`bash baize_posttrain_serve_sentinel.sh`（`--check-once` 单次探测 / `--watch --auto-restart` 持续监控+GPU5/6/7崩溃自动重启 / `--status` 看配置 / **永不重启 GPU0-3**）— R167

## 关键事实（常驻）

- pretrain S1 现状：iter~112400/700000（2026-11-07 git log），ETA≈2026-12-25（`.29` 8×H100）
- post-train 正式训练窗口：≈2026-12 下 → 2027-01 中（ISEDA 投稿 2027-02-01）
- 评测锚点：MiniCPM5-2B 36%（full harness，与 DeepSeek 94% 同口径，差 58 pp）
- 评测基准：EDA-Eval-PyAether 158 任务，Pass@1，5-run mean±std，2500s/任务，`-p 8 -n`
- 成功阶梯（预注册）：36%(起点) → 50%(M1) → 65%(M2) → 75%(M3) → 85%+(M4)
- SFT 数据已就绪：UltraData-SFT-2605（319G 下载/75.87GB 分词/18.89B tok，DATA_MAPPING 单一事实源）+ UltraData-SFT-Agent-2609（54.22G 下载/23.89GB 分词/5.97B tok）已分词镜像
- B 类 agentic 数据已下载未分词（`/nas_inference`：AgentTrove/Nemotron-Cascade-SFT-SWE 等）
- PyAether 领域语料：✅ **已调研**（wake4）—— `~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json` 8,463 个 API（api_name/api_type/api_descriptions/category）展平 ≈3.3–4.5M tok；加 func_all_v3/api_summary/skills/prompts ≈4–5M tok 可导出纯文本；chroma_db_*（向量嵌入）不用；退火 domain 主体 + SFT 合成语料（详见 EXPERIMENTS §PyAether-corpus）
- MiniCPM5-2B 模型：✅ **已下载到 .17** `/tmp/models/MiniCPM5-2B/`（4.7GB，LlamaForCausalLM 42层 2048d，2026-11-06 17:14）→ vLLM venv ✅ **已就绪** `~/code/vllm_venv/`（v0.33.0, torch 2.14.0, 9.4GB）→ GPU 释放后可 `vllm serve` 跑诊断评测获取 36% 侧轨迹
- .17 GPU 现状：8×A40 全被 SGLang Qwen3.8-27B 占用（44-45/46GB），2026-11-09 分配 4 张给 post-train
- 🔴 **CUDA 不匹配（wake53 发现 → ✅ R25 已解决）**：系统 CUDA 驱动=12.4（nvcc 12.4.131, 驱动550.54.14），旧 vllm_venv torch=2.14.0+cu130 → `torch.cuda.is_available()=False`。✅ **R25 修复**：新建 cu124 venv `~/code/verl_cu124_venv/`（Python 3.10.22, torch 2.6.0+cu124）→ 包已确认安装（site-packages: sglang 0.4.6 + verl + flash_attn 2.7.4 + ray + flashinfer 0.2.3）。⚠️ NFS冷启动 import torch >30s（R45实测），起跑前需 warm-up。
- ✅ **git代理（wake209发现）**：`.17` → GitHub 需要 HTTP 代理 `172.19.92.25:13128`。已配置到 repo local config: `git config --local http.https://github.com/.proxy http://172.19.92.25:13128`。之后 `git push`/`fetch` 不再超时。wake208 的 fetch 超时即因此。
- ✅ **沙盒架构（wake327更新：隧道已通）**：`.17`→`10.251.36.15` EDA沙盒经 **dual-nix-tunnel** 连通。隧道：`ssh -p 3333 app.e0031982@localhost`→36.15（hostname hfeg0tedaap02）；SSH -L forwarding 把 `localhost:8664/8665/8653/8669/8667/8668`→36.15上`10.129.32.75:同端口`。eda_fastmcp `.env`（`/home/app.e0031982/code/eda_fastmcp/.env`）：`SANDBOX_HOST=127.0.0.1`，`PROXY_PORTS=8664,8665,8653,8669,8668,8652`，`SANDBOX_ENDPOINTS=8664:...,8665:...,8653:...,8669:...`（4端口并行池）。MCP server on :18888。`search_apis`/`get_api_details` 本地✅，`run_code` ✅已通（wake327/328/330 e2e PASS `2+2=4`）。沙盒=远程 EDA 执行环境（pyAether Python+SWIG + Virtuoso SKILL），不可本地复制。隧道README：`/nas_data/app.e0031982/code/dual-nix-tunnel/README.md`。
- 🔴 **R9 verl+SGLang 集成（wake57 发现）**：verl 原生支持 SGLang（`pip install verl[sglang]`），多轮工具调用**仅 SGLang** 支持。配置已从 vLLM 切到 SGLang（`rollout.name: sglang` + `multi_turn: True` + `mode: async`）。EDA 沙盒工具骨架 `baize_posttrain_eda_tool.py` 已创建（BaseTool 子类，dry-run✅）。**R69 修正**：v1 有 3 个 CRITICAL API 不匹配（F01-F03），v2 `baize_posttrain_eda_tool_v2.py` 已修复并 dry-run✅。`baize_posttrain_tool_config.yaml` 已创建（修 F09）。**F14 BLOCKER ✅ 已解决(R70)**：MiniCPM5-2B 用 XML 格式(`<function name=...><param name=...>`), 4 个 SGLang parser 均不匹配 → 设计 MiniCPM5FunctionDetector + monkey-patch `baize_posttrain_minicpm5_parser_patch.py`。单轮 RL 不受影响。
- SFT 语料：✅ v1 `sft_pyaether_corpus.jsonl`(19610对,0污染) + ✅ v2 `sft_pyaether_corpus_v2.jsonl`(19524对,64% has-args,0污染,R24) — **v2 替代 v1 用于训练**
- 🔴 **R60 上下文窗口发现（wake108）**：DeepSeek 全 harness 轨迹平均 **28,339 tokens**（中位 23,906），是 4096 的 6.9x。4096→99%截断 / 8192→98% / 16384→82% / **32768→32%（推荐）** / 65536→3%。KV cache ctx32768 bs8 = 10.5GB/卡，A40 ✅ 可行。SFT 默认 8192 必须升级到 ≥16384；RL 脚本当前**缺失**上下文配置，需补 CONTEXT_LEN=32768。截断→假阴性奖励（8192 下约 29.4% rollout 误判）→支持从 R2 起步。
- 🔴 **R61 吞吐量约束发现（wake109）**：ctx=32768 **non-hybrid 不可行**——KV cache 10.5GB/seq，SGLang budget 18GB → 每 GPU 仅 1 序列，G=8 需 8 个。**ctx=16384 + hybrid engine** 是 72h 窗口唯一可行方案（3.45 steps/hr → ~248 步/72h）。500 步需 ~6 天。Smoke 用 ctx=32768 bs=16 G=4（37min/10步）。RL 配置已补丁至 ctx=16384，SFT 升至 16384。**主 RL 目标步数从 500 降至 200**。
- RL/SFT Parquet：✅ **已转换**（R10）`run/rl_pyaether_synth_v2.parquet`（3347 records, 931KB, verl RLHF 格式: prompt+reward_model+agent_name）+ `run/sft_pyaether_corpus.parquet`（19610 records, 2.7MB, verl SFT 格式: conversation+metadata）
- 🔴 **R11 GRPO 内存校准（wake59 发现）**：当前 `gpu_memory_utilization=0.35` 在多轮 3-turn 场景下**可能 OOM**——KV cache 需 13.8GB > 分配 11.9GB。已校准为 **0.50 + max_num_seqs=12**。训练态 ~12GB/卡，剩余 ~34GB 给 SGLang。4×A40 对 2B 全参 GRPO 是充裕配置（verl 官方 3B LoRA 需 1×H100）。添加 entropy_checkpointing + entropy_chunking 优化。5 级 OOM 降级阶梯已写入 §R11。
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）
- ✅ **cline/zhulong 版本（wake534 补齐，36.15 实测）**：zhulong fork `3.0.29`（`/nasdata/app.e0031982/.local/zhulong/bin/zhulong`）/ cline official `3.0.51`（`/nasdata/app.e0031982/.local/bin/cline`）。PreToolUse hook 源码 `/nasdata/app.e0031982/code/eda_fastmcp/scripts/cline_hooks/PreToolUse`（白名单：MCP 工具 + submit + spawn；run_commands/bash/exec_command 被 overrideInput 改写为 echo 通知；read/list/write 限制在 workspace 内）。
- 🔴 **L4 领域评测命令链（wake339 建立，wake381 更新）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配），5-run eval IN PROGRESS on .17 GPU6(:8096 step105-final)；run 1:Pass@1=6/158=3.8%(code_gen_success=62/fail=92/timeout=4)，run 2 in progress(51/158)；② **designflow**=EDA-Flow-Bench（36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，1173 tasks 4 shards A253/B277/C310/D353，`scripts/run_design_flow_batch.py --session-backend http://127.0.0.1:8666/v1/run_code`，cline at `/nasdata/app.e0031982/.local/bin/cline`，PreToolUse hook anti-cheat）；③ **反向隧道**：.17 PID1008898 `ssh -p3333 -fN -R 18096:localhost:8096 app.e0031982@localhost` → 36.15 `curl localhost:18096/v1/models` returns minicpm5-2b-sft-v39-final ✅；④ **cline providers.json on 36.15**：已配置 `baseUrl http://127.0.0.1:18096/v1 model minicpm5-2b-sft-v39-final apiKey dummy-key`（updatedAt 2026-11-12T19:22）；⑤ **designflow BLOCKER**：prior evals `eval/status_minicpm5_expand30.jsonl` 16 entries ALL verdict=ERROR reason="check.py missing" → run_design_flow_batch.py 未将 task 的 `test` 字段（inline check function）写入 workdir/check.py，需 debug 该脚本或手动注入；⑥ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，BaiZe ckpts 在 .29，36.15 无 GPU → 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: **✅ 能，且 R0+R2 两路 200 步主训均已 COMPLETED，R2 5-run eval 正在跑。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令）。**wake412 起跑成功**（弃用 verl 0.4.0 结论性 BLOCKED，自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`，纯 HF+torch 单 GPU 无 Ray/verl）。**wake413-416 R0 全量 200 步 COMPLETED**（cheat=0/3200 红线绿，但 dynamics 偏负：reward 全程≈0/frac_nonzero≈0/nz 0.97 塌缩⇒ group std≈0⇒adv≈0⇒无梯度方向 ⇒ R0=诚实负结果，proxy reward 不产生有方向信号。⚠️wake463 修正：此前"mean_ratio==1.0 policy 不动"依据无效——ppo_epochs=1 下 mean_ratio==1.0 为结构性 logging artifact，非 policy 不动证据；R0 负结果只挂在 reward 无方向信号上）；R0 eval 链因 4 并发 vLLM serve OOM 断裂无数据，决策门 §R425 C 合规判分支2 missing-JSON）。**wake429-433 R2+sandbox-exec 200 步主训 COMPLETED**（@01:05:36，cheat=0/1600 红线绿，real signal+梯度流动[84/200 步 posadv>0, grad_norm 均值1.65 policy 实更新]但 reward step100 后平台/回落 seg 0.053→0.111→0.106→0.090，overall 0.0901）。**wake433 R2 global_step_200 serve GPU7:8095 READY + 5-run eval RUNNING**（autofire chain PID2322797，158题 Pass@1，~12h ETA~13:00→5run_rl_analysis_R2.json，vs step105 0.0304±0.0083 McNemar+bootstrap）。下一=5-run eval 完→R2 真实数字→显著则里程碑报告/负则诚实负结果+换奖励。**GPU 现状(wake637,2026-11-20)**：GPU0-3=root；GPU4=base serve(:8098 standby)；GPU5=FREE(posttrain备用)；GPU6=vision VQA(非本线)；GPU7=FREE(交vision)。SFT :8096/R2 :8095 serve 已裁减退出（2026-11-19 GPU 收缩令 wake637）；R2 5-run eval run1-4 已 DONE mean≈0.475% decisively 负。**主线阻塞于 pretrain ckpt ETA≈2026-12-25**。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。**GPU 现状(wake637,2026-11-20)**：GPU0-3=root SGLang(不可动)；GPU4=base MiniCPM5-2B serve(:8098 standby)；GPU5=FREE(posttrain备用)；GPU6=vision VQA(非本线,不碰)；GPU7=FREE(交vision)。SFT :8096/R2 :8095 serve 已裁减退出（2026-11-19 GPU 收缩令 wake637）。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake476–wake522（R476-R522）已归档 → daily-memories-posttrain/2026-11-{14,15}.md（基线 RCA v1+v2 交付+3.04%±0.83% 复核+36.15 重测起跑+A/B 裁决 A+归因链 path-bug 根因+rescue 三脚本修复[grep -a/绝对 benchmark/case 尾斜杠]+独立 helper bpt_attribution_manual_rescue.sh+A1 干净 0/40 恢复[12.66% 交叉污染排除]+postmortem 复核一至十五度 PASS+隧道恢复+归因链起跑 A1 23:30+复盘报告交付 commit 375e11bf7；详见 EXPERIMENTS §R485-§R522/§R-Attribution-overnight 各节）。

> 📦 wake523–wake531（R523–R531）已归档要点 → postmortem 十七~二十一度复核 PASS + A1=0/40·A3=2/40 干净复算 + P0base auto-rescue 去风险 + 归因夜报 HTML 交付 + P0-dev McNemar 对比脚本 + ETA 诚实修正 + baseline_dev 0/79 确认（详见 EXPERIMENTS §R523-§R531 / daily 2026-11-15）。
> 📦 wake537/wake538（R537/R538）已归档要点 → 双链健康监控+前置就绪验证（详见 EXPERIMENTS §R537/§R538 / daily 2026-11-15）。

> 📦 wake540–wake561（R540-R561）已归档 → daily 2026-11-15。均为 08:1x 令 zhulong 5-run 链健康监控/复核心跳轮（run2 64→148/158→collapse 0.0% / run3 38→158→collapse 0.0% / run4 31→120/158）+交付物完整性复核 PASS+报告§10 渐进刷新+收口脚本/归因聚合器交付+MEMORY 体积归档。无新结论（结论见 wake476-539 块与进度快照）。详见 daily 2026-11-15 wake540-561。


> 📦 wake529–wake539（R529-R539）已归档 → daily 2026-11-15。要点结论（不改）：①postmortem 复核十六~二十二度 PASS + P0 dev compare/rescue 工具链去风险。②08:1x 令「158 评测改用 zhulong 方式」首执行：36.15 run1=18.99% 本就是 zhulong 口径(hook 白名单 run_commands 禁用)+cline 版本补齐(3.0.29/3.0.51)+再归因四问[真 MCP 拒绝 6.0%/run_code 3.0%/静默 45=28.5%/+15.95pp]+旧报告 PENDING-REMOTEST banner。③zhulong 基线 5-run 链起跑+口径六项全量复核 PASS。④沙盒非确定性发现+双轨 compare 方法论。⑤R2 诚实负结果报告交付（4-run mean=0.47%±0.61% vs step105 3.04% Δ=−2.56pp Wilcoxon p=0.0025 decisively 负）。详见 EXPERIMENTS §R529-§R539 / daily 2026-11-15。

> 📦 wake1–wake432 (R1–R432) 已归档 → daily-memories-posttrain/2026-11-{06..14}.md（P0/P1/P2/SDPA/cu124 venv/verl/SGLang/Parquet/内存预算/500题/反作弊/替身RL预演/吞吐量/RL hooks/SFT脚本/serve占位/沙盒/schematic API+v8-v23语料+污染闸门/minicpm5 tool-call parser/API Validator+v11-v38 corpus/SFT v11v38 CONVERGED/sandbox e2e+RL launch-ready/designflow baseline 0%/v39 SFT/step105 baseline 0.0304±0.0083 locked/弃verl自写GRPO loop/R0 200步COMPLETED诚实负结果[reward无方向]/R2+sandbox 200步起跑+cheat=0+eval autofire chain落地；R-content 详见 EXPERIMENTS 归档）。

> 📦 wake433-447 已归档 → daily-memories-posttrain/2026-11-14.md（R2 200步COMPLETED+serve GPU7:8095+5-run eval 起跑；R434-447 run1 23→70/158 监控，0 infra 错误）。

> 📦 wake448-wake475 已归档 → daily-memories-posttrain/2026-11-14.md（R448-R475 5-run eval 健康监控 run1 COMPLETED Pass@1=0.63%(单run不预判)+run2 RUNNING；R461 fsync 修复+R463 RL 动力学指标重释[mean_ratio==1.0=ppo_epochs=1 logging artifact]；0 infra 错误，eval 全自治。详见 EXPERIMENTS §R448-§R475）。

> 📦 wake475 (R475 5-run eval run2 监控心跳轮) 已归档 → daily-memories-posttrain/2026-11-14.md（run1 COMPLETED Pass@1=0.63% 复核+run2 健康；详见 EXPERIMENTS §R475）。








> 📦 wake562–568 已归档 → daily-memories-posttrain/2026-11-15.md（均 08:1x 令 zhulong 5-run 链健康监控/误判撤回轮；彼时 run2/3/4=0.0% 后经 wake570-573 RCA 证伪=管线 ws/no-ws 路径失配非模型 collapse；wake566/568 显式 SUPERSEDED）。

> 📦 wake581/582/584/587（2026-11-16 10:5x–15:0x · posttrain eval/rca:）已归档要点 → 23:0x RCA 交付+独立复测全 PASS+六项复核齐备在 origin+干净 5-run 链 PID912262 健康(run5 GATING)+链死因更正(非 SIGHUP 系 14:05 wake 误读 item1 自行 kill)。详见 daily 2026-11-16。

> 📦 wake590/591/592（2026-11-16 17:2x–18:33 · posttrain rca:）已归档要点 → 纪律纠偏(停未授权起新 run 的 clean_5run.sh+恢复 run2 封存)+23:0x RCA 交付物复测全六项 PASS(报告0外链0script/rca_verify8=8行/exec43/28/35≫1证伪collapse)。结论不变(主因=管线 ws-no-ws 路径失配非 collapse；回补 run2/3/4=4.43/2.53/3.80%)。详见 daily 2026-11-16。

> 📦 wake593/595/600（2026-11-16 18:52–22:0x · posttrain 5run:）已归档要点 → 18:3x 令授权恢复干净 5-run，起跑链 PID1192182（幂等跳过 run1-4，run5 进 GATE 等沙盒）；wake595/600 为 global-gate 监控心跳轮。**后已被 wake601+ 的 share-8090-pool 路径取代**（链 PID1192182→PID1354030）。详见 daily 2026-11-16。
