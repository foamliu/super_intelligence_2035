# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

> 🟢 **llama.cpp × Qwen3.5-2B CPU 测速结果（2026-11-23 19:53 · ops 令 · verdict=FEASIBLE）**：single-stream 30.16 tok/s / **8-way aggregate 132.52 tok/s (G2 PASS ≥100)** / 5-run 预计 20.6h；per-agent 16.57 tok/s ⇒ mean task 752s < 2500s 超时(headroom 0.301)；G0 convert OK(qwen3_5 支持,llama.cpp rev 969d733+py310 torch)/G3 max-8gram=1/G4 jinja 可用。**A5 臂去阻塞路径新增 llama.cpp CPU（不依赖 ops 驱动≥560）**。⚠ 复现要点：脚本默认 PY(eda_fastmcp venv)缺 torch⇒须 `PY=.../py310/bin/python`；且须 `NO_PROXY=127.0.0.1,localhost`（否则 http_proxy 把 localhost curl 健康检查打到代理⇒server 永不 healthy）。按 §D 纪律 **G2=PASS 先报告再等令，不自动接 5-run**。产物 `run/llamacpp_speed_probe_20261123_194956.json`(不得手改)+证据 `/tmp/baize_llamacpp_probe_20261123_194956/`。

> 🔴 **预注册（2026-11-20 22:0x · baseline-nailed 令 §E.3 · 先定后测·跑完不许改判据）**：
> - **臂矩阵**：A0=MiniCPM5-2B 原模型(.17 口径:无RAG/无沙盒MCP/cline/-p8/-n/无hook,endpoint :8098) → 用户要的 base 数字；A1=SFT v39 step105(同尺同口径,endpoint :8096 需重起 serve) → 分离 SFT 增量；A2/A3(+RAG/+沙盒MCP,36.15 口径)暂缓待 A0/A1 干净。
> - **冻结协议**：158 题 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n`；正式数字用修复后口径(recovered/ws+no-ws fallback)；主结论用 recovered-4run(剔除 run1 ws-only 锚点)，混合 5-run 并列报告。
> - **判据(预注册)**：①B1 身份四证 requested==served==ckpt 一致否则停跑；②B2 量尺差值写进报告(已知 bug 偏差达 +15pp)；③B3 judge_sd=0(打分器确定性)，同臂两 run 差值 < 2×judge_sd 否则先修协议；④B4 执行翻转率(10题×10次)；⑤B5 逐题画像须用 MiniCPM5 自己数据重做(不得沿用 DeepSeek fail_mode)。
> - **交付物**：`baseline_measurement_audit.json`(Stage1) + `baseline_A0_run<N>_pertask.json`(Stage2/3) + `reports/report_posttrain_baseline_nailed_zh.html`(里程碑)。
> - **状态(全闭环 ✅ · wake728)**：Stage1-3 全 DONE；A0 5-run=43.29%±3.92% / A1 5-run=4.56%±1.70% / 配对 Δ=-38.73pp(McNemar χ²=68.01 p=0.0)⇒🔴 SFT 显著退化；五道验收项全过 B1✅/B2✅(15.19pp)/B3✅(judge_sd=0)/B4✅(flip=0)/B5✅。里程碑报告 `reports/report_posttrain_baseline_nailed_zh.html`。⚠ final_report.model_name=zhulong_deepseek_v32=陈旧标签(authoritative=curl B1 PASS)。[详态见 daily 2026-11-21/22]
> - ✅ **git/remote BLOCKER（2026-11-20 23:1x wake649→01:0x 运维已修复）**：origin/main 曾纯重命名 doc/，运维 commit ed5398c2b7 恢复；现 origin healthy、doc/ intact。(详态见 daily 2026-11-21)

> 📦 **wake734（2026-11-23 01:23 · 三条令恢复 + A0报告交付 · 已归档）**→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：ops commit f92c39bb3c 三条令被 auto-commit 25497f1dd7 误删⇒逐字恢复任务书；A0深度报告✅交付+wake745 byte-identical 复验。**口径勘误**：A0 实际用 RAG(search_apis=1969)+沙盒(run_code=81)+hook=cline 全工具口径(与 DeepSeek 工具维度一致)。A5 就绪：Qwen3.5-2B 在 `/nas_data/app.e0031982/models/Qwen3.5-2B`。需要时再读。
> 🔴 **A5 run1 smoke 收口 + 决策锐化（wake744 · 2026-11-23 09:3x · run1 STOPPED · 已被 wake760 llama.cpp Q4_K_M 路径取代）**→ 原文见 daily-memories-posttrain/2026-11-23.md。**合并结论**：v3 自写 server(HF generate)实测 **~40 tok/s 聚合 THROUGHPUT-INFEASIBLE**⇒80 题仅 5 真实完成/75 空代码(93.75% F1_no_code)⇒停跑(铁律2 不当能力结论)；vLLM 路径=Qwen3.5-2B `Qwen3_5ForConditionalGeneration` hybrid 架构本机 vLLM0.7.3 认不了⇒需 driver≥560+CUDA12.8+vLLM nightly(ops)；落盘 `baseline_A5_qwen35_2b_run1_smoke_contamination.json`(smoke 证据不并入 5-run)；GPU5 释放未碰 0-3/4/6。**wake760 改走 llama.cpp Q4_K_M CPU 路径起跑 run1**。需要时再读。

> 🔴 **llama.cpp × Qwen3.5-2B CPU 测速预注册（2026-11-23 19:0x · ops 令 §B · 先定后测 · 跑前写进 MEMORY）**：
> - **唯一任务**：跑 `bash run/baize_posttrain_llamacpp_speed_probe.sh`（~45 min，CPU-only，`CUDA_VISIBLE_DEVICES=""`，不碰 GPU0-3/4/6/7，不跑 158 题，不改协议）。
> - **预注册判据（跑完不许改）**：①**G0 架构**=HF→F16 GGUF 转换成功+server 能起；`unsupported model type qwen3_5` ⇒ 路线当场死；②**G1 单流**=记录 `tg128` 最好值（预期 20–60 tok/s，仅参照）；③**G2 聚合**=**8 路聚合 ≥100 tok/s=PASS；64–100=CONDITIONAL；<64=FAIL**（FAIL ⇒ 路线作废，禁拿它跑 158 题）；④**G3 重复**=任何输出 8-gram 最大重复 ≤5（防 BaiZe SSM-bug 式 repetition loop）；⑤**G4 工具**=`--jinja` 成功=可用，失败回退记 `tool_support=no_jinja`。
> - **交付**：`run/llamacpp_speed_probe_<TS>.json`（脚本产出，不得手改）+ 证据目录 `/tmp/baize_llamacpp_probe_<TS>/` + MEMORY 顶部 1 行 verdict+三数 + daily 一节。
> - **纪律**：G2=PASS 先报告再等令，不自动接 5-run；不把 BLOCKED/infra 失败写成「模型太弱」(铁律 2)。
> - **§E 顺带义务**：v3 server docstring 旧句「flash-linear-attention installed (wake745) batched throughput ~221 tok/s」**无落盘证据**(wake745 daily 只复验 A0 报告)⇒**已删除该句**(改为 wake744 实测 ~40 tok/s aggregate/THROUGHPUT-INFEASIBLE)，见 `baize_posttrain_a5_server_v3_realstream.py` docstring。

> 📦 **wake760（2026-11-23 22:2x · A5 单 run Q4_K_M+llama.cpp 起跑 · 已收口 wake766）**→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：ops 令(81c378c297) Q4_K_M+llama.cpp run1 起跑(pid2066371 :8095 CPU-only，B0/B1 6门全过，自建编排器 B2/B3/B4)；run1 COMPLETE=Pass@1=0.0%(Q4_K_M smoke，禁与 A0 fp16 43.29% 配对)；交付 `baseline_A5_qwen35_2b_llamacpp_q4km_run1_{pertask,summary}.json`。需要时再读。

> 📦 **wake745（2026-11-23 11:0x · A0 报告独立复现验证 · 已归档）**→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：独立重跑 gen+html 与 committed 报告 diff **IDENTICAL**；§三/§四/§五 数字独立从落盘 JSON 重算全吻合（error_types agg AssertionError=100/TypeError=91/GenFail=137/GenTimeout=50；fail_mode F5=51/F1=36/F4=31/F3=13/F2=2；breadth 7:51/6:82/5:22/4:3；agg run1 search_apis=1969/get_api_details=978/run_code=81）；格式 0 script/0 外链/内联CSS/卡片/表格/证据索引。⇒ §三「数字自己重算」经复算证实。需要时再读。

> ✅ **wake752（2026-11-23 16:1x · §G agentic 轨迹收割 + 健康行为模板 + 污染红线勘误）**→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：新建 `baize_posttrain_harvest_agentic_sft_corpus.py` 收割 25 条 pass_all agentic 轨迹→`agentic_sft_corpus_candidate.jsonl`(6.09MB)；🔴污染红线——25 条全来自 158 eval 任务⇒不可直接作 SFT 数据,合法用途=行为模板参考。需要时再读。

> 📦 wake507–wake648（2026-11-14–21 · posttrain 旧 5run/GPU收缩/infra/纪律纠偏/standby 心跳·均已闭合·已归档）→ 已降级要点 → daily-memories-posttrain/2026-11-{14,16,17,20}.md。**合并结论**：wake628 旧 5run 6.84%±6.12% rca CLEAN(McNemar p<0.001);wake637 GPU 收缩到 4-5 令闭环(仅 GPU4 base standby);wake632 clean_5run.sh guard 硬化无条件 exit 7(3 次未授权复发已止);wake634 kill_gpu_serve child-PID bug 修复;wake507 隧道坏过已恢复(故障域=中继侧);wake638-648 standby 心跳复验持续成立。需要时再读各 daily。


## 进度快照

- PHASE: posttrain-wake777（standby 心跳 + 安全态/交付物/基线数复核 · 三条令全 done/blocked · 主线 SFT 设计预研 §K 已交付）。**2026-11-20「把 baseline 做扎实」令全闭环**：A0 base 5-run=43.29%±3.92% + A1 SFT 5-run=4.56%±1.70% + 配对 Δ=-38.73pp(McNemar χ²=68.01 p=0.0)⇒🔴 SFT 显著退化；五道验收项全过；里程碑报告 `reports/report_posttrain_baseline_nailed_zh.html`。**2026-11-22 ops 三条令**：(1)A1✅ (2)A5=Qwen3.5-2B：vLLM 路径 BLOCKED 待 ops 驱动≥560，**llama.cpp Q4_K_M 路径本轮起跑 run1(ops 22:0x 令)** (3)A0深度报告✅ `reports/report_posttrain_A0_capability_deepdive_zh.html`。**SFT 设计预研链 §F→§G→§H→§I→§J TIERED 2842→§K 真实轨迹收割预注册+骨架(wake759)**。
- 已完成: P0-P3预备✅;R1-R210✅;R0/R2 200步诚实负结果;step105 baseline locked;GPU收缩令✅wake637;沙盒池✅wake628。[详态见 daily-memories-posttrain/ 与 ARCHIVE_*]
- 当前动作: wake777(2026-11-24 09:0x · standby 心跳 + 安全态/交付物/基线数复核 · WAITING:1)；上轮 wake776(08:32 安全态/交付物复核)。standby 全清：GPU0-3=root(45GB)/GPU4=:8098 base standby(39246MiB)/GPU5=3MiB FREE/GPU6=vision(9221MiB)/GPU7=3MiB FREE 全未碰；:8098/:8099(root)/:30001+30003(vision) 在听,:8095/8096/8097 均无监听。providers.json=GLM 网关 glm-5.2 安全态(@agi-gateway,md5=63e59e92,未指向已停 :8095)。A5 run1=COMPLETE(Pass@1=0.0% Q4_K_M smoke)不变。三令交付物在位复核(里程碑报告 父 reports/ 16433B;A0深度报告 run/reports/ 18802B;A1 summary 11530B+paired 26691B;A0 5run summary 11573B;A5 pertask 163529B+summary 2224B)；本轮从落盘 JSON 复算基线数吻合 A0 per_run[.437,.456,.481,.411,.380]/McNemar χ²=68.01。无新 ops 令(fetch origin 6e465734d3..5042cff00c 仅他线前进 19 commits=zhulong×5/data×5/pretrain#3259/3260/designflow shard/harness R2990)。未碰 GPU0-3/4/6/7·协议·题面·check.py·超时·-p；未起任何新 eval；未 kill 别线进程。基线表不变 A0=43.29%±3.92%/A1=4.56%±1.70%/Δ=-38.73pp。
- 下一步: A5 run1 已收口(wake766,Pass@1=0.0% Q4_K_M smoke,禁与 A0 fp16 配对)。A5 5-run 待用户决策(同栈 A0+A5 量化重跑 or vLLM nightly);官方 A5(fp16 vLLM)仍 BLOCKED 待 ops 驱动≥560+CUDA12.8+vLLM nightly。**主线阻塞于 pretrain ckpt ETA≈2026-12-25**；SFT 设计预研后继=§K runner 待 ckpt+沙盒+串行+授权。⚠ clean_5run.sh 已硬禁用(exit 7)。
- 阻塞: R0=诚实负结果(proxy reward 无方向信号);R2 5-run mean≈0.475% decisively负;RL 基座=MiniCPM5-2B/SFT step105。GPU 现状(wake637):GPU0-3=root/GPU4=base serve(:8098 standby)/GPU5=备用/GPU6=vision/GPU7=交vision。SFT:8096/R2:8095 serve 已裁减退出。沙盒经 dual-nix-tunnel 通。verl 0.4.0 GRPO 结论性 BLOCKED(自写单进程 GRPO loop 替代)。**正式 SFT/RL 阻塞于 pretrain ckpt ETA≈2026-12-25**。
- 本轮新增产出: wake777✅(standby 心跳 + 安全态/交付物/基线数复核)：无新 ops 令(fetch 6e465734d3..5042cff00c 仅他线前进 19 commits zhulong×5/data×5/pretrain#3259/3260/designflow shard A/B/D/harness R2990，无 OPS_/TASK/MEMORY_POSTTRAIN 改动，OPS_*.md 仍仅 SPEED_PROBE/Q4KM_RUN1 两条已执行令)；standby 全清复验(GPU0-3 root 45GB/GPU4 :8098 base standby 39246MiB/GPU5 FREE 3MiB/GPU6 vision 9221MiB/GPU7 FREE 3MiB;:8098/:8099/:30001+30003 听/:8095-8097 无;无 eval 运行)；providers.json=GLM glm-5.2 安全态(md5=63e59e92,@agi-gateway 未指向已停 :8095)；三令交付物实 ls 正确路径全在位(里程碑报告父 reports/ 16433B/A0深度报告 run/reports/ 18802B/A0 5run 11573B/A1 5run 11530B+paired 26691B/A5 Q4KM run1 pertask 163529B+summary 2224B)；本轮从落盘 JSON 复算基线数吻合(A0 per_run[.437,.456,.481,.411,.380]=43.29%±3.92%/McNemar χ²=68.01/A5 q4km=0.0%)；A0深度报告格式复核=0 script/0 外链/14 表/4 卡片/9 节。未碰 GPU0-3/4/6/7·协议·题面·check.py·超时·-p；未起 eval；未 kill 别线。
- 未完成指令: 🔴 2026-11-22 ops 三条令——(1)A1✅wake728；(2)A5=Qwen3.5-2B：**Q4_K_M run1 smoke 已收口(wake766,Pass@1=0.0%,非官方配对)**，官方 A5(fp16 vLLM)仍 BLOCKED 待 ops 驱动≥560+CUDA12.8+vLLM nightly；A5 5-run 待用户决策(同栈 fp16 重跑 or vLLM nightly)；(3)A0深度报告✅wake734+wake745复验。其余旧令全闭合(详见各 daily/ARCHIVE)。**主线阻塞于 pretrain ckpt ETA≈2026-12-25**。
- git 铁律(condensed):⚠ NFS stale-ref:`git fetch`后**绝不用符号 ref `origin/main` read-tree**,改用**显式 hash**(`git rev-parse FETCH_HEAD`),read-tree 带 `--reset <hash>`+verify `diff --cached <hash>` 为空;⚠ 工作树在 NFS 巨大,`pull --rebase`/`reset --mixed` hang D-state⇒**纯对象库提交法**:temp-index(`GIT_INDEX_FILE=/tmp/idx git read-tree --reset <显式hash>`→`hash-object -w`+`update-index --add --cacheinfo` 仅本线文件→`write-tree`→`commit-tree -p <显式hash>`→`update-ref`→`git push`)+verify diff 只含本线文件否则 abort;⚠ push 前重 fetch+用最新 origin 重建 tree(wake687 force-push 教训)。提交前缀 posttrain;不用 -A,用 `git add -- <本线路径>`。
- 🔧 fixes(condensed):SDPA patch(verl fsdp_sft L199 fa2→sdpa,venv 重建重打);verl0.4.0 GRPO 结论性 BLOCKED(list_named_actors 死锁)→wake412 自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`(纯 HF+torch 无 Ray,smoke PASS);torchrun --nproc_per_node=1;NCCL SOCKET_IFNAME=bond0+IB_DISABLE;R2 OOM 修复=`--batch-prompts 1`(Gtot=8/step)+expandable_segments;kill_gpu_serve child-PID bug wake634 已修(walk ppid 到 vLLM serve 祖先)。

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
- 🔴 **L4 领域评测命令链（wake339/381，详态见 ARCHIVE_OPERATOR_POSTTRAIN）**：① **zhulong 158 题**=EDA-Eval-PyAether 158 任务（cline harness，`--model` 可配）；② **designflow**=EDA-Flow-Bench（36.15，1173 tasks 4 shards，`run_design_flow_batch.py --session-backend ...:8666/v1/run_code`，PreToolUse hook）；③ **反向隧道**：.17 `ssh -p3333 -fN -R 18096:localhost:8096 ...` → 36.15 `curl localhost:18096/v1/models`；④ **designflow BLOCKER**：`run_design_flow_batch.py` 未将 task `test` 字段写入 workdir/check.py⇒verdict=ERROR，需 debug；⑤ **BaiZe ckpt BLOCKED**：`/nas_train` 未挂载 .17，ckpt 在 .29，36.15 无 GPU ⇒ 需 pretrain 线导出 HF 到共享 `/nas_data` NFS。**L4 现状**：zhulong 侧已并入 baseline-nailed（A0/A1 用同 cline harness 158 题）；designflow 侧仍 BLOCKED。

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: **R0+R2 两路 200 步主训均 COMPLETED（诚实负结果）**。RL 基座=MiniCPM5-2B（+SFT v39 step105），弃用 verl 0.4.0（结论性 BLOCKED 死锁）⇒wake412 自写单进程 GRPO loop `baize_posttrain_rl_grpo_loop.py`（纯 HF+torch 单 GPU 无 Ray/verl）。**R0**（proxy reward）200 步：cheat=0/3200 绿，但 reward≈0/frac_nonzero≈0 塌缩⇒group std≈0⇒adv≈0⇒无梯度方向=**诚实负结果**（proxy reward 不产生方向信号；wake463 修正：mean_ratio==1.0 为 ppo_epochs=1 结构性 logging artifact，非 policy 不动证据）；eval 链因 4 并发 vLLM serve OOM 断裂无数据。**R2**（+sandbox-exec）200 步：cheat=0/1600 绿，real signal+梯度流动(84/200 步 posadv>0)但 reward step100 后平台/回落 overall 0.0901；R2 5-run eval run1-4 mean≈0.475% **decisively 负**。⇒ **proxy reward 无方向信号；正式 SFT/RL 阻塞于 pretrain ckpt ETA≈2026-12-25**。**GPU 现状(wake637)**：GPU0-3=root；GPU4=base :8098 standby；GPU5=FREE；GPU6=vision；GPU7=FREE(交vision)。SFT :8096/R2 :8095 serve 已裁减退出。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`（8×A40，CUDA 12.4 max）。**GPU 现状(wake637,2026-11-20)**：GPU0-3=root SGLang(不可动)；GPU4=base MiniCPM5-2B serve(:8098 standby)；GPU5=FREE(posttrain备用)；GPU6=vision VQA(非本线,不碰)；GPU7=FREE(交vision)。SFT :8096/R2 :8095 serve 已裁减退出（2026-11-19 GPU 收缩令 wake637）。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水
> 🔴 **wake777（2026-11-24 09:0x · standby 心跳 + 安全态/交付物/基线数复核 · WAITING:1）**：①**无新 ops 令**：fetch origin(wake776 6e465734d3→5042cff00c)后 origin/main 仅他线前进(19 commits:zhulong×5/data×5/pretrain#3259/3260/designflow shard A/B/D/harness R2990)，**无 OPS_/TASK/MEMORY_POSTTRAIN 改动**，OPS_*.md 仍仅 SPEED_PROBE/Q4KM_RUN1 两条已执行令。②**standby 全清复验**：GPU0-3=root(45GB)/GPU4=:8098 base standby(39246MiB)/GPU5=3MiB FREE/GPU6=vision(9221MiB)/GPU7=3MiB FREE 全未碰；:8098/:8099(root)/:30001+30003(vision) 在听,:8095/8096/8097 均无监听；无 eval 运行。③**providers.json 安全态**=GLM 网关 glm-5.2(@agi-gateway,md5=63e59e92,未指向已停 :8095)。④**三令交付物实 ls 正确路径复核**(全在位)：里程碑报告(父 reports/ 16433B)/A0深度报告(run/reports/ 18802B)/A0 5run 11573B/A1 5run 11530B+paired 26691B/A5 Q4KM run1 pertask 163529B+summary 2224B。⑤**基线表不变**(本轮从落盘 JSON 复算吻合)：A0=43.29%±3.92%(per_run[.437,.456,.481,.411,.380])/A1=4.56%±1.70%/Δ=-38.73pp(McNemar χ²=68.01 p=0.0)/A5 Q4KM run1=Pass@1 0.0%(非官方禁与 A0 fp16 配对)。⑥**A0深度报告格式复核**=0 script/0 外链/14 表/4 卡片/9 节/首屏口径声明+口径勘误+posttrain 署名。全未碰 GPU0-3/4/6/7·协议·题面·check.py·超时·-p；未起任何新 eval；未 kill 别线进程。详 daily 2026-11-24 wake777。

> 📦 **wake776（2026-11-24 08:32 · standby 心跳 + 安全态/交付物复核 · 已被 wake777 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：无新 ops 令(fetch 1be638c7a2..23c689eba0 仅他线前进);standby 全清;providers.json=GLM glm-5.2 安全态(md5=31ec96fc);三令交付物全在位;基线表不变 A0=43.29%±3.92%/A1=4.56%±1.70%/Δ=-38.73pp/A5 Q4KM run1=0.0% 非官方禁配对。需要时再读。

> 📦 **wake775（2026-11-24 16:0x · standby 心跳 + 安全态/交付物复核 · 已被 wake776 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：无新 ops 令(fetch 39368333ab..1be638c7a2 仅他线前进);standby 全清;providers.json=GLM glm-5.2 安全态(sha256=a10b1fa6);三令交付物全在位;基线表不变 A0=43.29%±3.92%/A1=4.56%±1.70%/Δ=−38.73pp/A5 Q4KM run1=0.0% 非官方禁配对。需要时再读。

> 📦 **wake774（2026-11-24 14:0x · 交付物正确路径复核（路径误判自纠）· 已被 wake775 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：里程碑报告 `report_posttrain_baseline_nailed_zh.html` 落盘在父级 `doc/BaiZe-ISEDA2027/reports/`（生成器 REPORT_DIR=`../reports/`），自 wake728(commit 599446ecd4)起在 git，盘上 16433B 在位；regen byte-identical；standby wake768-773「在位」判断正确（跟踪父级路径），初查「丢失」系路径误判已纠正。需要时再读。

> 📦 **wake773（2026-11-24 12:0x · standby 心跳 + 安全态/交付物复核 · 已被 wake774 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：无新 ops 令(fetch 55723c86b0..c6a6661555 仅他线前进);三令交付物复核(里程碑报告在父级 reports/ 16433B 在位,本轮 wake774 已确认路径正确);A5 run1 COMPLETE(Pass@1=0.0%)不变;standby 全清;providers.json=GLM glm-5.2 安全态(sha256=efb3768a);基线表不变 A0=43.29%±3.92%/A1=4.56%±1.70%/Δ=−38.73pp。需要时再读。

> 📦 **wake772（2026-11-24 10:0x · standby 心跳 + 三令交付物/安全态复核 · 已被 wake773 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**结论**：无新 ops 令(fetch 1d258a4a0c..55723c86b0 仅他线前进);三令交付物在位复核全过;A5 run1 COMPLETE(Pass@1=0.0%)不变;standby 全清(GPU0-3 root/GPU4 :8098 base standby/GPU5 FREE/GPU6 vision/GPU7 FREE;providers.json=GLM glm-5.2 安全态 sha256=d8822fa0);基线表不变 A0=43.29%±3.92%/A1=4.56%±1.70%/Δ=−38.73pp。需要时再读。

> 📦 **wake768（2026-11-24 03:4x · standby 心跳 + A0 报告 §三 合规复验 · 已被 wake769 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：providers.json=GLM 网关 glm-5.2 安全态(未指向已停 :8095)；A0 报告 §三 合规复验 PASS(0 script/0 外链/14 表/4 卡片/首屏口径声明/posttrain 署名)；三令收口态不变。需要时再读。
> 📦 wake766（2026-11-24 02:42 · A5 run1 收口 COMPLETE · 已被 wake767/768 取代）→ 原文见 daily-memories-posttrain/2026-11-24.md。**结论**：A5 Q4_K_M run1 COMPLETE(158/158,Pass@1=0.0%,wallclock=15888s,eval_rc=0;fail F1_no_code=146/F3_timeout=11/F4=1);Q4_K_M 退化重复循环致 92% 无代码产出;非官方 A5(官方需 fp16 vLLM BLOCKED driver<560);Q4_K_M 禁与 A0 fp16 配对。需要时再读。

> 📦 **wake767（2026-11-24 03:2x · A5 run1 收口复核 + v3 server 残留清理 · 已被 wake769 取代）**→ 原文见 daily-memories-posttrain/2026-11-24.md。**合并结论**：A5 run1 COMPLETE 复核；v3 server 残留(pid1545491 :8097)清理⇒GPU5 4242→3MiB 释放；:8095/8097 均释放，GPU0-3/4/6/7 全未碰。需要时再读。

> 📦 wake761/762（2026-11-23 23:1x/23:45 · A5 run1 首/二次健康巡检 · 监控 wake）→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：run1 健康 PASS;发现并验证 B3 stale-jsonl 盲区修复路径=改读 batch `stats/` 三文件(本轮不改运行中编排器)。需要时再读。

> 📦 wake760（A5 单 run Q4_K_M+llama.cpp 起跑 · 有交付）→ 详见 daily-memories-posttrain/2026-11-23.md。**结论**：ops 22:0x 令,B0/B1预检6门PASS(pid2066371 :8095 CPU-only)+B2/B3/B4 编排器自治起跑;交付物落盘。需要时再读。

> 📦 wake759（2026-11-23 21:3x · §K held-out 真实 agentic 轨迹收割预注册+脚本骨架）→ 原文见 daily-memories-posttrain/2026-11-23.md。**结论**：§K 预注册+`baize_posttrain_heldout_agentic_trajectory_gen.py` 骨架(dry-run ALL GATES WIRED OK)+`heldout_agentic_trajectory_prereg.json` 冻结；A5 driver<560 未变。需要时再读。

> 📦 wake728/734/743/744/747/748/749/750（2026-11-22–23 · baseline-nailed 收口 / A0 报告交付+复验 / A5 smoke / 三条令恢复 / standby 心跳 · 已归档）→ 详见 daily-memories-posttrain/2026-11-{22,23}.md。**合并结论**：wake728 A1 5-run=4.56%±1.70%+配对 Δ=-38.73pp(McNemar p=0.0)+五验收项全过；wake734 A0 深度报告+wake745/750 复验；wake743/744 A5 smoke 93.75% 污染停跑；wake749 里程碑报告 NFS drift 修复。需要时再读。

> 📦 wake628–731 / wake476–722（2026-11-14–23 · Stage1-3/5run/A1 chain/RCA/GPU 收缩/clean_5run guard/kill_gpu_serve bug · 已归档）→ 详见 daily-memories-posttrain/2026-11-{14..23}.md。**合并结论**：A0 5-run=43.29%±3.92%；旧 5run 6.84%±6.12% rca CLEAN(McNemar p<0.001)；R2 诚实负(4-run 0.47%±0.61%)；clean_5run guard 硬化(exit 7)；kill_gpu_serve child-PID bug 修复(wake634)；GPU 收缩到 4-5(wake637)；wake723 NFS stale-ref 铁律(显式 hash read-tree)。需要时再读。

