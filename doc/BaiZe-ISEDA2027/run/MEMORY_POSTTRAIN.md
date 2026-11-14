# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 0

> 🔧 **隧道复盘结论（wake507 · 2026-11-14 23:5x · posttrain infra:）**：隧道**坏过现已恢复**——最后通点 **20:41:50**（36.15 run1 完整 18.99% 落盘）/ 首断点 **22:4x wake505**（.17:3333 未监听+直连36.15:22超时）/ 恢复确认 **23:26 wake506**（中继 tunnel.ps1 重新在线）/ 故障域=**中继侧①+②**（排除SSH认证/36.15 sshd/.17端口重启）/ **非本线造成亦非本线修复**（20:41–23:30 posttrain 未碰中继与隧道，wake505 纯CPU、wake506 kill 仅作用36.15评测进程于恢复后）/ 当前隧道健康三条验证命令实测PASS。报告 `reports/report_infra_tunnel_postmortem_zh.html`。隧道恢复后已接回 A1/A3+P0dev（归因链 PID3707027，A1 23:30 起跑）。

## 进度快照

- PHASE: posttrain-wake500（✅ **归因前提核验PASS:5×跳升确属同模型step105不同环境比较**[curl .17:8096=id=minicpm5-2b-sft-v39-final root=global_step_105;36.15经反向隧道18096→.17:8096;final_report model_name=zhulong_deepseek_v32=config.yaml active_model陈旧标签非实际模型];**36.15 run1逐题画像[🔴wake500订正:完整run1=18.99%(30/158)/gen成功36/gen_fail121/生成后通过率83.3%;六类分型T6_tool_format_genfail121头号(76.6%);全局拒绝1304[run_commands1048/missing-field527/string-not-array321];wake499的15.82%/29/25/86.2%是20:03部分副本,已superseded]**;v2 RCA已交付[e434f6def];**双 eval 并行 RUNNING**:36.15重测 run1 DONE=18.99%(完整,wake500订正;旧15.82%为部分副本)/run2 RUNNING(PID2747266) + .17 R2 5-run chain PID2322797健康;v2 RCA核心:MCP工具6051+submit13699/91.77%报错/C5_degenerate_pass479/790=60.6%头号/检索333API仅19进代码5.7%）
- 已完成: P3预备✅;P0✅;P1✅;P2✅;R1-R210✅;R280归档;wake281-433✅;R411-R428✅(verl BLOCKED→自写GRPO loop/R0 200步COMPLETED+cheat=0/3200/step105 baseline 0.0304±0.0083 locked/eval 自治链路+决策门预注册+5-run并行不可行/R2 autofire chain 落地[全量详见 daily-memories 2026-11-13/14]);R431✅(R2 监控 step100+cheat=0/400+step50 ckpt)；R432✅(R2 主训监控 step151/200 健康[奖励平台期诚实修正:step100 后 mean_reward 0.113→0.105 平台/回落,纠正 wake431 单调上升]+cheat=0/1200 三次落盘+step150 ckpt+eval chain 健康等待)；R433✅(R2 200步主训 COMPLETED[cheat=0/1600 红线绿终值+global_step_200 ckpt 5.03GB+全200步奖励平台后回落 0.1195→0.0798]+GPU5 step60 serve 手动 teardown 完成 OOM mitigation[kill_gpu_serve child-PID bug 实证]+R2 serve GPU7:8095 READY[model minicpm5-2b-grpo-R2-step200]+5-run eval RUNNING 01:08:13 自动链 PID2322797 ~12h ETA~13:00)；R434-R452✅(5-run eval 健康监控 run1 ~23→94/158 渐进,8 worker,GPU7 87-100%util,3 并发 serve 稳定,GPU5=vision R9 占用,0 traceback/OOM/infra 错误,eval 全自治无人工动作[全量详见 daily-memories 2026-11-14])
- 当前动作: wake520 R520:**rescue 路径拼接 bug 定位+修复+独立 helper 落地(本轮实质)+双链监控**。①postmortem(🔴最高优先)十三度复核 PASS：报告 report_infra_tunnel_postmortem_zh.html 在位(commit 375e11bf7 origin/main)+隧道三命令 04:2x 实测全 PASS[3333 LISTEN 127.0.0.1; ssh -p3333→hfeg0tedaap02; 三隧道进程活 618469/1008898/1278889]。②**rescue RD 路径拼接 bug(wake520 新发现)**：ablation+dev-eval 脚本 rescue 块 `RD=$(grep ... 唯一输出目录)` 所得 RD **无尾斜杠**⇒`${RD}final_report.json` 拼成 `.../20261115_xxxx_app.e0031982final_report.json`(缺/)⇒`-f` 永假⇒auto-rescue **eval 跑成功但 cp 跳过**报"未产出 final_report"(实测 A1 re-rescue 坐实：final_report 在 `.../20261115_0431_app.e0031982/final_report.json` 存在但无/路径判 not-found)。修=加 `case "$RD" in */) ;; *) RD="$RD/" ;; esac`。三脚本(ablation/dev-eval/manual_rescue)均修+`bash -n` PASS。**新独立 helper** `bpt_attribution_manual_rescue.sh`(repo+scp 到 36.15)——抽 rescue 块成可独立调用，幂等(A1 已 rescue 则 moved=0 重跑复现 0/158)，**A1 实测复算 PASS：pass_rate=0.0/correct=0/gen_stats{success:6,fail:151,timeout:1}/gen_success_rate=0.0380 ⇒ A1 干净=0/40=0% 确认**。③**A3 auto-rescue 将失效预警**：A3 bash(PID1040673,03:56 起)在 fix 落盘(04:20 git pull new inode)前已启动⇒持有旧脚本(grep binary + 缺/ 双 bug)⇒A3 codegen(~39min,29/40 task,13 with_code)完成后 auto-rescue 必跳过⇒**下一 wake 须 `bash bpt_attribution_manual_rescue.sh --arm A3` 手动补 rescue**(helper 已就位 36.15)。P0base/P0p0(dev-eval 脚本,fix 已 scp 到 36.15,非运行中安全)起跑时读新脚本⇒auto-rescue 应正常。④R2 5-run：run1=0.63/run2=1.27/run3=0.0/run4=0.0 DONE,**run5 codegen RUNNING@03:33:34**(.17 31/158 task,GPU7:8095 serve 健康 minicpm5-2b-grpo-R2-step200);4-run mean 0.475%<<step105 3.04%±0.83 趋势负(待 run5+5run_rl_analysis_R2.json McNemar/bootstrap,负则诚实负结果)。⑤09:00 交付态:A1✅0/40+A3 待 rescue(helper 就位)+T6✅+P0base·P0p0 链自治 ETA 全链~07:00<09:00;下一 wake 链完成后汇总+McNemar+报告。0 infra,未碰 GPU0-5/运行中 eval/别线/隧道进程。
- 下一步: ①36.15 5-run完(~Nov15凌晨)→新基线(同158题,标环境差异:旧.17 no-sandbox-prompt+本地MCP:18888/隧道 vs 新36.15 sandbox-prompt+原生RAG:8090/沙盒:18891)→report_posttrain_baseline_pyaether_rca_3615_zh.html ②R2 5-run完→5run_rl_analysis_R2.json(vs step105 0.0304±0.0083,McNemar+bootstrap)→显著则里程碑报告report_posttrain_rl_surrogate_zh.html(标替身预演,论证引reward曲线+Pass@1,禁引mean_ratio)/负则诚实负结果+换奖励或修ppo_epochs≥2+old_logp冻结使clip生效再跑一轮 ③kill_gpu_serve child-PID bug待chain空闲修(L102-118)
- 阻塞: ✅ **R2 200步主训 COMPLETED**(PID2314192 已退出@01:05:36,cheat=0/1600,global_step_200 ckpt 已 serve)+✅ **5-run eval 自动链 RUNNING**(PID2322797,label=grpo_R2_step200,GPU7:8095,chain 标 ETA~13:00 偏乐观[实测速率因 timeout 放缓]→5run_rl_analysis_R2.json)。**R0=诚实负结果**(proxy reward 不移动 policy,训练侧 dynamics 已证;eval 因 infra 断裂[OOM 杀 serve+链]无数据,决策门 §R425 C 合规判分支2 missing-JSON)。RL 基座=MiniCPM5-2B/SFT step105(用户令解除 BaiZe 基模依赖)。GPU0-3=root;GPU4=base serve;GPU5=vision R9 占用(28GB,非本线,不碰);GPU6=step105-final baseline serve;GPU7=R2 global_step_200 serve(:8095)。沙盒经 dual-nix-tunnel 通(TUNNEL_OK 实测)。verl 结论性 BLOCKED 不再尝试。
- 本轮新增产出: R520✅(rescue RD 路径拼接 bug 定位+修复[三脚本 case 尾斜杠]+独立 helper bpt_attribution_manual_rescue.sh 落地[repo+scp 36.15,幂等 A1 实测 PASS 复算 0/158=0/40]+A3 auto-rescue 失效预警[旧脚本 in-mem,下轮手动 helper]+双链监控[postmortem 十三度 PASS/A3 codegen 29-40/R2 run5 RUNNING]+0 infra;详见 EXPERIMENTS §R520-rescue-slashfix); R519✅(rescue 双 bug 修复[grep -a+绝对 benchmark+陈旧 clear]+A1 干净 0/40 恢复[12.66%交叉污染彻底排除]+A3 RUNNING+R2 run5 RUNNING+postmortem 十二度复核 PASS;0 infra;详见 EXPERIMENTS §R519-rescue-fix); R518✅(双链健康监控心跳+postmortem 十一度复核 PASS+隧道三命令 03:5x 全 PASS[3333 LISTEN/ssh→hfeg0tedaap02/三隧道进程活]+归因链 A1 codegen RUNNING+R2 run5 codegen RUNNING[4-run mean 0.475%<<3.04%趋势负];0 infra;详见 EXPERIMENTS §R513-monitor); R516✅(双链健康监控心跳+postmortem 九度复核 PASS+rescue 内嵌验证[两条自治链 RUNNING 无法加速]；详见 EXPERIMENTS §R513-monitor); R504✅(R2 PPO clip 全程失效诊断+R3 ppo_epochs=2 修复 prep[已归档 daily 2026-11-14/15,详见 EXPERIMENTS §R504]); R503✅(Task B 补丁模板全量起草+dev-eval runner 去阻塞[已归档,详见 EXPERIMENTS §R-Attribution-update6]); R502✅(V1 提示差异实证+18.99% 权威复算[已归档,详见 EXPERIMENTS §R-Attribution-update5])
- 未完成指令: 🔴 2026-11-13 13:3x RL 起跑——✅ R0 200步主训 COMPLETED+诚实负结果[R0 负结果依据修正:proxy reward 全程≈0/frac_nonzero≈0/nz 0.97 塌缩→无梯度方向,而非 mean_ratio(后者为 logging artifact)]+✅ R2+sandbox-exec 200步主训 COMPLETED(cheat=0/1600,reward 0.053→0.111→平台/回落 0.090,grad_norm 非零 policy 实更新)+✅ 5-run eval RUNNING(01:08:13 自动链 PID2322797,serve R2 global_step_200 GPU7:8095→158题5-run→5run_rl_analysis_R2.json)；**run1 COMPLETED@07:46 Pass@1=1/158=0.63%<step105 5-run mean 3.04%±0.83%[单 run 不预判]**，run2 RUNNING@07:46(18/158 success=8/fail=1/timeout=0 健康,ETA≈14:25)；下一动作=5-run eval 完(run2-5 各~5-6h)→R2 5-run mean Pass@1(vs step105 0.0304±0.0083,McNemar+bootstrap)→显著则里程碑报告 report_posttrain_rl_surrogate_zh.html(标替身预演,论证禁引 mean_ratio,改引 reward 曲线+Pass@1)/负则诚实负结果+换奖励或修 ppo_epochs≥2+old_logp 冻结使 clip 生效再跑一轮(§用户令#4)；L4 2026-11-12(zhulong step105 ✅5/5 0.0304±0.0083;designflow base 5/5=0%)
- git: super_intelligence_2035(main=origin,main ahead1[vision 1b8e1adce local-only] behind11[origin 已前进],designflow/vision 在途文件不碰)；本轮交付(wake473: EXPERIMENTS §R473+MEMORY wake473 心跳[wake472→wake473 更新]+daily-memories 2026-11-14 wake473)；唤醒时清理 stale rebase-apply(06:02 别线 pull --rebase 中断残留)
- 🔧 **SDPA patch**(wake328):verl fsdp_sft_trainer.py L199 `attn_implementation="flash_attention_2"`→`"sdpa"`;venv 重建后需重打此patch
- 🔧 **verl 0.4.0 GRPO 结论性 BLOCKED(wake411)→ ✅ wake412 换框架解除**:verl hybrid GRPO `list_named_actors()` 找不到已创建的 register_center 命名 actor→init 握手死锁;1-GPU/2-GPU/NCCL 修复均复现;根因=verl 0.4.0+本机 Ray 命名 actor 可见性不兼容。**wake412 解除**：弃用 verl 路径，新写自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch，无 Ray/verl/torchrun），smoke 3 步 PASS(ratio=1.000)。verl surrogate 脚本保留但不再尝试。详见 EXPERIMENTS §R411/§R412
- 🔧 **torchrun 单驱动修复 R-launch-fix3(wake411)**:`baize_posttrain_rl_grpo_surrogate.sh` L320 `--nproc_per_node=1`(verl main_ppo 单驱动,n_gpus 来自配置);原 $NGPU 派生多 Ray 集群→多 GPU 起跑前提修复
- 🔧 **NCCL 接口修复 R-launch-fix4(wake411)**:脚本 export NCCL/gloo `SOCKET_IFNAME=bond0`+`NCCL_IB_DISABLE=1`+`NCCL_NET=Socket`(本机多网卡含 docker bridge);标准 torch.distributed-in-container 加固,实测对 verl 死锁无效(非根因)但保留
- 🔧 **R2 OOM 最终修复(wake429)**:A40 44GB 对 2B 全参 GRPO(G8 B2)预算过紧(policy+ref+Adam16GB+grad=28GB 基线+logits float32 峰值5GB 触顶)。修复=`--batch-prompts 1`(Gtot=8/step,**G=8 保持**)+`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。verl_cu124_venv 起 RL 必带此 env;若再 OOM 可进一步降 ctx 或切 8-bit Adam。
- 🔧 **config-path 修复 R-launch-fix2(wake410)**:`baize_posttrain_rl_grpo_surrogate.sh` L303 `CFG_DIR` 强制绝对路径;项目配置(sdpa/hybrid/timeout)现真正加载;RL 起跑前提(已验证有效)
- 🔧 **kill_gpu_serve child-PID bug(wake433 发现,待修)**:`baize_posttrain_rl_eval_chain.sh` L102-118 `kill_gpu_serve` 用 `nvidia-smi --query-compute-apps=pid` 取 GPU 占用 PID,但 vLLM serve 的 CUDA 上下文常由 multiprocessing 子进程持有(父=serve,子=`python -c from multiprocessing.spawn...`)⇒子进程 cmd 不含 `vllm.entrypoints.openai.api_server`⇒误判 skip,GPU5 step60 serve 未被 teardown。wake433 手动 kill 父进程 1802143 完成 OOM mitigation。**修法(待 chain 空闲)**:取到子 PID 后 walk `ps -o ppid=` 到根,沿路径 grep vllm serve;或改用 `pgrep -f 'vllm.entrypoints.openai.api_server.*--port <PORT>'`。不编辑运行中脚本。




## GPU 端口映射表（2026-11-10 wake195 实测）

| GPU | 端口 | served-model-name | 用途 | VRAM | 状态 |
|:--:|:--:|:--|:--|:--:|:--|
| 0-3 | 8099 | qwen3.8-27b | root SGLang Qwen3.8-27B | ~45GB/卡 | ✅ root 占用，不可动 |
| 4 | 8098 | minicpm5-2b | vLLM MiniCPM5-2B（Phase1评测用,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4） | 39.1GB | ✅ wake334 restarted(PID553793 was dead→new PID799523,+no_proxy env) |
| 5 | — | — | **vision R9 占用**(cpu_rl_v11_regen_experiment PID2498238,~32GB,非本线,不碰) | 32584 MiB | 🔵 vision R9 wake449 起占用 |
| 6 | 8096 | minicpm5-2b-sft-v39-final | **vLLM SFT v39 final ckpt serve**(wake360,global_step_105,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 **--enable-auto-tool-choice** --max-num-seqs 4,PID962854) | 39.2GB | ✅ wake361 parallel eval RUNNING(GPU6=81%util,step_105 eval PID972225) |
| 7 | 8095 | minicpm5-2b-grpo-R2-step200 | **vLLM R2 global_step_200 serve**(wake433,PID2353244,--max-model-len 65536 --enforce-eager --tool-call-parser minicpm5 --enable-auto-tool-choice --max-num-seqs 4,5-run eval RUNNING) | 39.1GB | ✅ wake433 serving+eval RUNNING |

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
- 🔴 **L4 领域评测命令链（wake339 建立，wake381 更新）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配），5-run eval IN PROGRESS on .17 GPU6(:8096 step105-final)；run 1:Pass@1=6/158=3.8%(code_gen_success=62/fail=92/timeout=4)，run 2 in progress(51/158)；② **designflow**=EDA-Flow-Bench（36.15 `/nasdata/app.e0031982/code/EDA-Flow-Bench/`，1173 tasks 4 shards A253/B277/C310/D353，`scripts/run_design_flow_batch.py --session-backend http://127.0.0.1:8666/v1/run_code`，cline at `/nasdata/app.e0031982/.local/bin/cline`，PreToolUse hook anti-cheat）；③ **反向隧道**：.17 PID1008898 `ssh -p3333 -fN -R 18096:localhost:8096 app.e0031982@localhost` → 36.15 `curl localhost:18096/v1/models` returns minicpm5-2b-sft-v39-final ✅；④ **cline providers.json on 36.15**：已配置 `baseUrl http://127.0.0.1:18096/v1 model minicpm5-2b-sft-v39-final apiKey dummy-key`（updatedAt 2026-11-12T19:22）；⑤ **designflow BLOCKER**：prior evals `eval/status_minicpm5_expand30.jsonl` 16 entries ALL verdict=ERROR reason="check.py missing" → run_design_flow_batch.py 未将 task 的 `test` 字段（inline check function）写入 workdir/check.py，需 debug 该脚本或手动注入；⑥ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，BaiZe ckpts 在 .29，36.15 无 GPU → 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: **✅ 能，且 R0+R2 两路 200 步主训均已 COMPLETED，R2 5-run eval 正在跑。RL 基座=MiniCPM5-2B（+SFT v39 step105），不再依赖 BaiZe 基模**（2026-11-13 用户令）。**wake412 起跑成功**（弃用 verl 0.4.0 结论性 BLOCKED，自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`，纯 HF+torch 单 GPU 无 Ray/verl）。**wake413-416 R0 全量 200 步 COMPLETED**（cheat=0/3200 红线绿，但 dynamics 偏负：reward 全程≈0/frac_nonzero≈0/nz 0.97 塌缩⇒ group std≈0⇒adv≈0⇒无梯度方向 ⇒ R0=诚实负结果，proxy reward 不产生有方向信号。⚠️wake463 修正：此前"mean_ratio==1.0 policy 不动"依据无效——ppo_epochs=1 下 mean_ratio==1.0 为结构性 logging artifact，非 policy 不动证据；R0 负结果只挂在 reward 无方向信号上）；R0 eval 链因 4 并发 vLLM serve OOM 断裂无数据，决策门 §R425 C 合规判分支2 missing-JSON）。**wake429-433 R2+sandbox-exec 200 步主训 COMPLETED**（@01:05:36，cheat=0/1600 红线绿，real signal+梯度流动[84/200 步 posadv>0, grad_norm 均值1.65 policy 实更新]但 reward step100 后平台/回落 seg 0.053→0.111→0.106→0.090，overall 0.0901）。**wake433 R2 global_step_200 serve GPU7:8095 READY + 5-run eval RUNNING**（autofire chain PID2322797，158题 Pass@1，~12h ETA~13:00→5run_rl_analysis_R2.json，vs step105 0.0304±0.0083 McNemar+bootstrap）。下一=5-run eval 完→R2 真实数字→显著则里程碑报告/负则诚实负结果+换奖励。GPU0-3=root；GPU4=base serve；GPU5=空闲(已 teardown)；GPU6=step105-final baseline serve；GPU7=R2 global_step_200 serve(:8095)。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。GPU0-3=root SGLang(不可动)；GPU4=base MiniCPM5-2B serve(:8098)；GPU5=vision R9 占用(非本线,不碰)；GPU6=step105-final baseline serve(:8096)；GPU7=R2 global_step_200 serve(:8095,5-run eval RUNNING)。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

> 📦 wake476–wake484 已归档（基线 RCA v1+v2 报告交付+逐项复算校验+36.15 重测起跑+A/B 之争 trace 实证[裁决 A]，commit 25eb93f0a/4de1f8058/67337d708/e434f6def/1bca8e2da；3.04%±0.83% 复核通过；v2 RCA 37415B/0script/0外链）→ 详见 daily-memories-posttrain/2026-11-14.md。

> 📦 wake485-wake488（R485-R488）已归档 → daily-memories-posttrain/2026-11-14.md（v2 RCA 多轮复验+stale 0.158 勘误+A/B trace 复算；详见 EXPERIMENTS §R485-§R488）。
> 📦 wake489（R489 监控心跳:v2 RCA终验+A/B裁决A+双eval进度）已归档 → daily-memories-posttrain/2026-11-14.md。

> 📦 wake490（R490 监控心跳:v2 RCA终验PASS+双eval实测+MEMORY归档）已归档 → daily-memories-posttrain/2026-11-14.md。
> 📦 wake491（R491 监控心跳:v2 RCA终验PASS+36.15重测run1=15.82%[~5x跳升重大发现]+双eval健康+MEMORY归档）已归档 → daily-memories-posttrain/2026-11-14.md。
> 📦 wake492（R492 唤醒核验:16:3x v2 RCA全维度执行级复验PASS+双eval健康+git跨线WAVEVIEW UU判定不push）已归档 → daily-memories-posttrain/2026-11-14.md。

> 📦 wake493 已归档 → daily-memories-posttrain/2026-11-14.md（v2 RCA 多轮复验+三项硬证+双eval健康；详见 EXPERIMENTS §R493/§R494）。

> 📦 wake494 已归档 → daily-memories-posttrain/2026-11-14.md（v2 RCA 多轮复验+三项硬证+双eval健康；详见 EXPERIMENTS §R493/§R494）。




> 📦 wake495–wake496（R495/R496）已归档 → daily-memories-posttrain/2026-11-14.md（三项用户令复核+36.15 run1漏斗拆解+5x归因trace分析+Task A/B scaffold；详见 EXPERIMENTS §R495/§R-Attribution）。

> 📦 wake497（R497）已归档 → daily-memories-posttrain/2026-11-14.md（Task A 前置：40 题分层抽样 + ablation runner run-ready；详见 EXPERIMENTS §R-Attribution-update）。
> 📦 wake498（R498）已归档 → daily-memories-posttrain/2026-11-14.md（Task B 前置：79/79 train/dev 拆分 + P0-tool-format 补丁模板 + dev-eval runner run-ready；详见 EXPERIMENTS §R-Attribution-update2）。
> 📦 wake499（R499）已归档 → daily-memories-posttrain/2026-11-14.md（归因前提核验+36.15 run1 逐题画像[**部分副本口径**，wake500 订正]；详见 EXPERIMENTS §R-Attribution-update3）。
> 📦 wake500（R500）已归档 → daily-memories-posttrain/2026-11-14.md（36.15 run1 口径订正 15.82%→18.99% + per-题画像/六类分型；详见 EXPERIMENTS §R-Attribution-update4）。
> 📦 wake501（R501 任务书归档+双eval心跳）已归档 → daily-memories-posttrain/2026-11-14.md（详见 EXPERIMENTS §R-Attribution-update4 收尾）。
> 📦 wake502（R502 V1 系统提示差异实证 + 18.99% 权威复算）已归档 → daily-memories-posttrain/2026-11-14.md（详见 EXPERIMENTS §R-Attribution-update5）。
> 📦 wake503（R503 Task B 补丁模板全量起草 P1/P2/P3 + dev-eval runner 去阻塞 + dry-run 验证）已归档 → daily-memories-posttrain/2026-11-14.md（详见 EXPERIMENTS §R-Attribution-update6）。
> 📦 wake504/wake505 已归档 → daily-memories-posttrain/2026-11-14.md（R504 PPO clip 诊断+R3 prep / R505 计划填妥+T6归因表+隧道HARD BLOCKED；详见 EXPERIMENTS §R504/§R-Attribution-T6）。

> 📦 wake508/wake509（R508/R509 postmortem 复核+双链监控）已归档 → daily-memories-posttrain/2026-11-15.md（隧道三命令全 PASS、归因链 A1 RUNNING、R2 5-run run4 RUNNING；详见 EXPERIMENTS §R508-monitor）。

> 📦 wake510 已归档 → daily-memories-posttrain/2026-11-15.md（postmortem 三度复核 PASS + 隧道三命令 00:47 PASS + 归因夜链 A1 RUNNING + R2 run4 RUNNING + MEMORY 归档 wake504/505；详见 EXPERIMENTS §R508-monitor）。

> 📦 wake511 已归档 → daily-memories-posttrain/2026-11-15.md（postmortem 四度复核 PASS + 归因夜链 A1 DONE 12.66%/A3 RUNNING + R2 run4 RUNNING；详见 EXPERIMENTS §R508-monitor）。
> 📦 wake512（R512 归因夜链有效性审计+postmortem 五度复核）已归档 → daily-memories-posttrain/2026-11-15.md（提示机制真生效实证[A1 no_sandbox/A3 +eda_flow移除/P0base old/P0p0 p0_toolfmt 单变量设计 de-risk]+§R512-attribution-audit）。
> 📦 wake513/wake514 已归档 → daily-memories-posttrain/2026-11-15.md（六/七度复核+跨机纠偏；详见 EXPERIMENTS §R513/§R514/§R515）。
> 📦 wake515 已归档 → daily-memories-posttrain/2026-11-15.md（归因链 path-bug 根因+rescue 修复+A1=0/40 交叉污染排除+干净重跑 relaunch515b 02:55 起；详见 EXPERIMENTS §R515-attribution-rescue）。
> 📦 wake516 已归档 → daily-memories-posttrain/2026-11-15.md（双链监控+postmortem 九度复核 PASS+rescue 内嵌验证 grep RESCUE=5/5；详见 EXPERIMENTS §R513-monitor）。
> 📦 wake517 已归档 → daily-memories-posttrain/2026-11-15.md（双链监控+重复链排查+R2 run4 DONE+postmortem 十度复核 PASS；详见 EXPERIMENTS §R513-monitor）。
> 📦 wake518 已归档 → daily-memories-posttrain/2026-11-15.md（双链监控+postmortem 十一度复核 PASS+relaunch515b A1 codegen RUNNING+R2 run5 起；详见 EXPERIMENTS §R513-monitor）。
> 📦 wake519 已归档 → daily-memories-posttrain/2026-11-15.md（rescue 双 bug 修复[grep -a+绝对 benchmark]+A1 干净 0/40 恢复+12.66% 确为 ZhuLong DeepSeek 交叉污染排除；详见 EXPERIMENTS §R519-rescue-fix）。
> 📦 wake520 已归档 → daily-memories-posttrain/2026-11-15.md（rescue RD 路径拼接 bug 修复[三脚本 case 尾斜杠]+独立 helper bpt_attribution_manual_rescue.sh 落地+A1 复算 0/40+A3 auto-rescue 失效预警；详见 EXPERIMENTS §R520-rescue-slashfix）。
> wake521 R521（2026-11-15 04:5x）: **postmortem 十四度复核 PASS + MEMORY 体积归档 + A3 rescue 后台启动 + 双链监控**。①postmortem(🔴最高优先)十四度复核 PASS：报告 `reports/report_infra_tunnel_postmortem_zh.html` 在位(commit 375e11bf7 origin/main)+纪律实测 PASS[0 script/0 外链/20.5KB]+**隧道三命令 04:5x 实测全 PASS**[V1 `ss -ltnp|grep 3333`=LISTEN 127.0.0.1 / V2 `ssh -p3333`→hfeg0tedaap02 TUNNEL_OK / V3 反向隧道 18096→`minicpm5-2b-sft-v39-final`]。②**MEMORY 体积维护**（wake520 交办）：wake515-520 流水原文已在 daily-memories-2026-11-15.md，本轮将 MEMORY 内联长条改为 1 行指针 ⇒ MEMORY 39.1KB→**33.3KB**（<32KB 软限附近，<40KB 硬限）。③**A3 rescue 后台启动**（本轮实质动作）：A3 bash(PID1040673,03:56:37 起)持有旧脚本(pre-fix)⇒auto-rescue 必跳过(wake520 预警)⇒起后台 poll-and-rescue(`/tmp/a3_rescue_poll.sh` PID3787607)：每 75s 探测 relaunch515b.log `[A3] done`，命中后自动 `bash bpt_attribution_manual_rescue.sh --arm A3`（helper 已就位 36.15 repo 路径，幂等）；A3 codegen 03:56 起 ~60min，ETA~05:04，rescue 完成写 `/tmp/a3_rescue_poll.out`。**A3 干净数字待 rescue 完成记录**（下一 wake 或本轮末确认）。④P0base/P0p0：relaunch515b 串行续跑（A3 后），dev-eval 脚本 fix 已 scp 36.15，起跑时 bash 读新脚本⇒auto-rescue 应正常。⑤R2 5-run：run1=0.63/run2=1.27/run3=0.0/run4=0.0 DONE，**run5 codegen RUNNING@03:33:34**(.17 38/158 task,GPU7:8095 serve 健康,eval chain PID2322797 活)；4-run mean 0.475%<<step105 3.04%±0.83 趋势负。0 infra，未碰 GPU0-5/运行中 eval/别线/隧道进程。→ 详见 daily 2026-11-15 与 EXPERIMENTS §R521-postmortem-arch。
> wake522 R522（2026-11-15 05:0x）: **postmortem 十五度复核 PASS + 双链健康监控 + A3 rescue poll 延长（本轮实质）**。①postmortem(🔴最高优先)十五度复核 PASS：报告 `reports/report_infra_tunnel_postmortem_zh.html` 在位(commit 375e11bf7)+隧道三命令 05:0x 实测全 PASS[3333 LISTEN 127.0.0.1 / ssh -p3333→hfeg0tedaap02 / 三隧道进程活]。②**归因夜链健康**（36.15）：relaunch 编排器 `bash /tmp/relaunch515b.sh`(PID700233,ppid=1,etime 2h12m)活⇒四臂串行 A1(done 03:56,pass_rate 0.12658=陈旧未被 rescue)/A3(RUNNING,PID1040673,73min,codegen.log 05:10 仍写)/P0base/P0p0(待 A3 后自动起)。③**P0base/P0p0 auto-rescue 去风险**（本轮实质核验）：dev-eval 脚本 `bpt_attribution_prompt_dev_eval.sh` 36.15 mtime=04:42:55=fix 版（L99 清陈旧/L116-117 pre-post 目录差集定位/L122 grep -a/L138-139 case 尾斜杠）⇒P0base/P0p0 起跑时读新脚本⇒auto-rescue 应正常，09:00「补丁 dev 前后对比」交付去风险。④**A3 rescue poll 延长**：A3(03:56 起 pre-fix in-mem)auto-rescue 必跳过⇒旧 poll(PID3787607,24 iter ~05:20 尽)窗口偏紧；已 kill 旧 poll+起 v2(`/tmp/a3_rescue_poll2.sh` PID3804659,80 iter~100min 至~06:50)命中 `[A3] done` 即自动 `bash helper --arm A3`（幂等），保 A3 干净数字。⑤R2 5-run run5 codegen RUNNING@03:33:34(.17 43/158 task~27%,stats success24/fail0/timeout10,GPU7:8095 serve 健康,eval chain PID2322797 活);4-run mean 0.475%<<step105 3.04%±0.83 趋势负;**run5 诚实 ETA~09:30(超 09:00 截止,R2 5-run 属独立交付项,非 09:00 归因及格线)**。0 infra,未碰 GPU0-5/运行中 eval/别线/隧道进程。→ 详见 daily 2026-11-15 与 EXPERIMENTS §R522-chain-monitor。




> 📦 wake507 已归档 → daily-memories-posttrain/2026-11-15.md（隧道事故复盘报告交付：报告 report_infra_tunnel_postmortem_zh.html + commit 375e11bf7 + MEMORY 顶部结论行；隧道恢复后接回 A1/A3+P0dev）。

> 📦 wake506 已归档 → daily-memories-posttrain/2026-11-15.md（隧道恢复+runner 缺陷修复[run_cline_script.sh 不读 MCP_CFG/SANDBOX_ON→按臂 stage CLI_DATA_DIR 改 cline_mcp_settings.json]+归因链起跑 A1 23:30；详见 EXPERIMENTS §R-Attribution-overnight）。




> 📦 wake481–wake485（R481–R485）已归档（36.15 环境核实+启动脚本+SMOKE+A/B 之争 trace 实证/v2 RCA 交付核验/36.15 重测起跑/wake485 监控心跳+stale 0.158 勘误；详见 daily-memories-posttrain/2026-11-14.md）→ 原文已搬，此处留指针。




> 📦 wake1–wake186 (R1–R139) 已归档 → daily-memories-posttrain/2026-11-{06,07,08,09,10}.md（P0/P1/P2/SDPA/cu124 venv/verl/SGLang/Parquet/内存预算/500题/反作弊/替身RL预演/吞吐量等全量调研；R-content 详见 EXPERIMENTS 归档）。



> 📦 wake189-wake245 (R142-R176) 已归档 → daily-memories-posttrain/2026-11-10/11.md（RL hooks/SFT脚本/Phase1就绪/serve占位/沙盒/SFT完成/RL dry-run；R-content 详见 EXPERIMENTS）。
> 📦 wake246-wake262 (R177-R193) 已归档 → daily-memories-posttrain/2026-11-11.md（R177-R183 schematic API修正+v8~v13语料+污染闸门 / R184-R193 v14-v23 语料：ae*/emy*/db* lifecycle+blind 全清/Mde* sweep-platform/coverage 59-67%）。


> 📦 wake263-wake316 已归档 → daily-memories-posttrain/2026-11-11/12.md（R291 SFT语法95.6%vsBase62.8%/P0 D1-D6终验；R302-316 minicpm5 tool-call parser+上下文溢出修复；v11-v35 语料943对；详见 EXPERIMENTS）。

> 📦 wake320–wake336 已归档 → daily-memories-posttrain/2026-11-12.md（API Validator+v11-v38 corpus 1344 pairs+SFT v11v38 CONVERGED+serve+post-SFT eval LAUNCHED；详见 EXPERIMENTS）。
> 📦 wake337–wake397 已归档 → daily-memories-posttrain/2026-11-12/13.md（sandbox e2e+RL launch-ready/designflow baseline 0%/v39 SFT训练+eval pipeline autonomous/R397 run2 Pass@1=1.9%；详见 EXPERIMENTS）。

> 📦 wake398-wake432 已归档 → daily-memories-posttrain/2026-11-13/14.md（step105 baseline 0.0304±0.0083 locked/弃verl自写GRPO loop/R0 200步COMPLETED诚实负结果[reward无方向]/R2+sandbox 200步起跑+cheat=0+eval autofire chain落地；详见 EXPERIMENTS）。

> 📦 wake433-447 已归档 → daily-memories-posttrain/2026-11-14.md（R2 200步COMPLETED+serve GPU7:8095+5-run eval 起跑；R434-447 run1 23→70/158 监控，0 infra 错误）。

> 📦 wake448-wake475 已归档 → daily-memories-posttrain/2026-11-14.md（R448-R475 5-run eval 健康监控 run1 COMPLETED Pass@1=0.63%(单run不预判)+run2 RUNNING；R461 fsync 修复+R463 RL 动力学指标重释[mean_ratio==1.0=ppo_epochs=1 logging artifact]；0 infra 错误，eval 全自治。详见 EXPERIMENTS §R448-§R475）。

> 📦 wake475 (R475 5-run eval run2 监控心跳轮) 已归档 → daily-memories-posttrain/2026-11-14.md（run1 COMPLETED Pass@1=0.63% 复核+run2 健康；详见 EXPERIMENTS §R475）。








