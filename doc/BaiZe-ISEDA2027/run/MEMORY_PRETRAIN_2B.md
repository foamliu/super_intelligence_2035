# MEMORY_PRETRAIN_2B.md — BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）运行时状态
WAITING: 0
> 🛑 **【运维通告 · 2026-11-02 19:51】S1 已由 ops 中继重启并在跑**：`bash scripts/train.sh s1 --nodes 2`，launcher pid **4163528**，从 **ckpt 58000** 续（19:55:40 起 iter **58010**→58030，7.0–7.2 s/step ≈**582K tok/s**，双机 16 卡 **98–100%**、~75GB/卡、~690W）。⇒ **GPU 不再空闲**：🚫 严禁再起任何训练/GPU 评测进程；CPU 评测必须降载：`OMP_NUM_THREADS≤8` + `nice -n 19`，**禁止 `pkill python`**。
> 2026-11-05 16:24 #1401: ★ 运维令 11-05 09:0x·**监控轮·4/5 DONE·iter_50000仍在跑(~59.5min/ETA~16:39按74min/ckpt)·watcher就绪待5/5自动出终版报告**。4/5 results.json verified✅(harness Avg: iter_10000=51.50%/20000=52.00%/30000=53.00%/40000=55.12%, sciq恢复非NaN→NaN系HF/bf16路径非ckpt权重); iter_50000 eval alive(llama-server PID1145106 -t16 port8090 bz2b-50000-f16.gguf + eval driver PID1157255, etimes~3573s, dir仍空, prompt_tokens_total91622+cached430701, ETA~16:39); watcher PID2985640 alive(since14:52, polling30s, 5/5齐时自动跑gen_llamacpp_scaling_report.py出终版报告+done marker /tmp/baize_report_final_done.marker); 生成器已复核PASS(514行, harness Avg=acc_norm×6+acc×2, fit_log+fit_power报R²/RMSE/pred_700k, 0script/0外链/幂等/输出reports/正确路径); partial report 17401B@15:30(4/5dry-run)待watcher 5/5终版覆盖。S1健康(.29 GPU0-3 100%/~75GB); CUDA_VISIBLE_DEVICES=""全程; nice19; 未碰GPU/S1/vision/data/harness。git:up to date。📦 体积:TASK=27955B(27.3KB✓)/MEMORY=28445B(27.8KB✓)。未完成指令:**有**(iter_50000在跑~ETA16:39+终版报告待watcher自动交付后需agent commit)⇒ WAITING: 0。
> 📦 §#1400（11-05 16:09, 监控轮·4/5 DONE·iter_50000仍在跑~45min·生成器全路径已复核PASS）→ daily-memories/2026-11-05.md；**结论**：4/5 DONE, iter_50000 eval alive ETA~16:25, watcher就绪, 生成器全路径复核PASS。被#1401校正(iter_50000~59.5min@16:24, ETA上修~16:39按74min/ckpt, S1 GPU0-3全100%)。需要时再读。
> 📦 §#1399（11-05 16:04, 监控轮·4/5 DONE·iter_50000 64.3%·ETA~16:25）→ daily-memories/2026-11-05.md；**结论**：4/5 DONE, iter_50000 64.3%@16:04 ETA~16:25, 4 results.json verified, watcher+生成器就绪。被#1400校正(iter_50000仍在跑@16:09, 生成器全路径已复核)。需要时再读。
> 📦 §#1398（11-05 15:55, 监控轮·4/5 DONE·iter_50000~40%·归档3块TASK→27.3KB✓）→ daily-memories/2026-11-05.md；**结论**：4/5 DONE, iter_50000~40%ETA~16:38, 归档11-04 22:1x+14:0x+11-02 11:1x三块TASK→27.3KB✓, PR#31703确认已提交。被#1399校正(iter_50000 64.3%@16:04, ETA上修~16:25)。需要时再读。
> 📦 §#1397（11-05 15:39, 监控轮·4/5 DONE·iter_50000~20%·ETA~16:38）→ daily-memories/2026-11-05.md；**结论**：4/5 DONE harness Avg=51.50/52.00/53.00/55.12%, iter_50000已起ETA~16:38, watcher就绪, sciq恢复确认非NaN。被#1398校正(归档3块TASK→27.3KB✓, iter_50000~40%@15:55, PR#31703确认已提交)。需要时再读。
> 📦 §#1396（11-05 15:31, 监控轮·4/5 DONE·iter_50000评测进行中·生成器dry-run OK）→ daily-memories/2026-11-05.md；**结论**：4/5 DONE harness Avg=51.50/52.00/53.00/55.12%,iter_50000已起(PID1157255),生成器dry-run exit=0/17401B,watcher就绪。被#1397校正。需要时再读。
> 📦 §#1395（11-05 15:18, 监控轮·3/5 DONE·iter_40000进行中·ETA~16:40）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE,iter_40000 id_task31143活跃ETA~15:25,生成器已复核,watcher就绪。被#1396校正(4/5 DONE iter_40000 harness Avg=55.12%,iter_50000已起,生成器dry-run exit=0)。需要时再读。
> 📦 §#1394（11-05 15:07, 监控轮·3/5 DONE·iter_40000 ~79%·ETA~16:37）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE iter_40000~79%@15:06,全完成ETA~16:37,watcher就绪。被#1395校正。需要时再读。

> 📦 §#1393（11-05 15:00, 监控轮·3/5 DONE·iter_40000 ~68%·ETA~16:37）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE iter_40000~68%@15:00,ETA done~15:23,全完成~16:37,watcher就绪。被#1394校正(iter_40000~79%@15:06)。需要时再读。
> 📦 §#1391（11-05 14:38, 监控轮·3/5 DONE·iter_40000 ~39%·ETA~16:37）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE iter_40000~39%@14:38,每ckpt~74min,全完成ETA~16:37,报告生成器就绪需手动跑。被#1392接续(部署watcher自动跑生成器,无需手动)。需要时再读。
> 📦 §#1390（11-05 14:31, 监控轮·3/5 DONE·iter_40000 ~37%·ETA~16:20）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE iter_40000~37%@14:31。被#1391校正(iter_40000~39%@14:38,每ckpt~74min,全完成ETA~16:37)。需要时再读。
> 📦 §#1389（11-05 14:20, 监控轮·3/5 DONE·iter_40000 ~22%·ETA~16:00-16:38）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE,iter_40000~22%@14:20。被#1390校正(iter_40000~37%@14:31,ETA~16:20)。需要时再读。
> 📦 §#1388（11-05 14:10, 监控轮·3/5 DONE·iter_40000刚起·ETA全完成~16:38）→ daily-memories/2026-11-05.md；**结论**：3/5 DONE iter_30000@14:09,iter_40000已起,ETA~16:38。被#1389校正(iter_40000~22%@14:20,ETA~16:00-16:38)。需要时再读。
> 📦 §#1387（11-05 13:55, 监控轮·2/5 DONE·iter_30000 86%·ETA全完成~16:25）→ daily-memories/2026-11-05.md；**结论**：管线健康ETA~16:25。被#1388校正(3/5 DONE@14:09,iter_40000已起,ETA~16:38)。需要时再读。
> 📦 §#1380-#1386（11-05 13:0x–13:49, 7轮监控·iter_30000 5min→86%·ETA收敛）→ daily-memories/2026-11-05.md；**结论汇总**：管线全程健康,iter_30000 推进中,ETA从~16:40逐轮收敛。被#1388校正(3/5 DONE@14:09)。需要时再读。

> 📦 §#1378（11-05 12:4x, 监控轮·iter_20000 98%·ETA~16:25）→ daily-memories/2026-11-05.md；**结论**：管线健康,iter_20000 98%。被#1379 校正(iter_20000 DONE@12:53 Avg=52.00%, iter_30000已启动, ETA~16:35)。需要时再读。


> 📦 §#1374（11-05 11:5x, 监控轮·iter_20000 47%·ETA~16:00）→ daily-memories/2026-11-05.md；**结论**：管线健康ETA~16:00。被#1375/#1376 校正(iter_20000 72%@12:13, ETA全完成~16:20)。需要时再读。

> 📦 §#1377（11-05 12:2x, 监控轮·iter_20000 84%·ETA~16:20）→ daily-memories/2026-11-05.md；**结论**：管线健康,iter_20000 84%@12:2x。被#1378 校正(iter_20000 98%@12:42, ETA~16:25)。需要时再读。

> 📦 §#1375（11-05 12:0x, 监控轮·iter_20000 55%·ETA~16:15）→ daily-memories/2026-11-05.md；**结论**：管线健康ETA~16:15。被#1376/#1378 校正。需要时再读。
> 📦 §#1376（11-05 12:1x, 监控轮·iter_20000 72%·ETA~16:20）→ daily-memories/2026-11-05.md；**结论**：管线健康ETA~16:20,GGUF全5就绪。被#1378 校正(98%@12:42)。需要时再读。


> 📦 §#1373（11-05 11:4x, iter_10000 DONE·生成器口径bug已修）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：iter_10000完成@11:40(74min)harness Avg51.50%=HF对齐✅;生成器改harness口径+P6基线修正,报告12932B验证✅;ETA 74min/ckpt→全完成~16:30。被#1377校正~16:20。需要时再读。

> 📦 §#1372（11-05 11:2x, 监控轮·iter_10000 91%·ETA~15:13）→ daily-memories/2026-11-05.md；**结论**：管线健康ETA~15:13。被#1373校正为74min/ckpt,ETA~16:30。需要时再读。

> 📦 §#1371（11-05 11:1x, 监控轮·iter_10000 86%）→ daily-memories/2026-11-05.md；**结论**：管线健康,ETA~14:45。被#1373修正为74min/ckpt,ETA~16:30。需要时再读。
> 📦 §#1370（11-05 11:0x, 监控轮·iter_10000 77%·生成器复验PASS）→ daily-memories/2026-11-05.md；**结论**：ETA上修~15:00。被#1373修正为~16:30。需要时再读。
> 📦 §#1369（11-05 10:5x, 监控轮·iter_10000 60%·f-string bug已修）→ daily-memories/2026-11-05.md；**结论**：L440 f前缀已补,占位HTML验证PASS。需要时再读。

> 📦 §#1368（11-05 10:4x, 监控轮·管线50%·脚本对齐验）→ daily-memories/2026-11-05.md；**结论**：管线+生成器对齐PASS, ETA~13:50, CPU13%≪80%。被#1370修正ETA~15:00。需要时再读。
> 📦 §#1367（11-05 10:3x, 监控轮·管线健康·生成器复验）→ daily-memories/2026-11-05.md；**结论**：管线健康iter_10000推进中, 0/5产物, 生成器5614B占位✅。需要时再读。

> 📦 §#1366（11-05 10:2x, 管线并行度优化实测+ETA修正~40min/ckpt）→ daily-memories/2026-11-05.md；**结论**：parallel=4不提速(内存带宽bound), ETA~13:50全完成, f16精度最优保留。需要时再读。

> 📦 §#1365（11-05 10:0x, 报告生成器就绪+管线监控）→ daily-memories/2026-11-05.md；**结论**：生成器（491行,纯标准库,幂等）验证PASS,0/5待管线。需要时再读。

> 📦 §#1364（11-05 09:4x, llama.cpp全ckpt评测启动·修复恢复退化ckpt）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：5 ckpt全转GGUF f16(~28s/ckpt);冒烟iter_20000修复后sciq=0.82→NaN是PyTorch CPU float32 SSM不稳定非权重问题;全量管线PID1694987启动。被v2管线PID502077取代。需要时再读。

> 📦 §#1360（11-05 08:0x, llama.cpp 3-bug fix）→ daily-memories/2026-11-05.md；**结论**：✅ 3 bugs fixed（rope_type NONE→NEOX / build_attention_layer 缺 ggml_rope_ext / FFN RELU_SQR→GELU），commit 5dc38db00@fix/nemotron-h-undo-permute-and-rope，1-token Δmax=0.006（600×改善），undo_permute=True 正确，PR 草稿就绪等用户确认。需要时再读。
> 📦 §#1361（11-05 07:0x, sciq/piqa 复判 + PR 草稿）→ daily-memories/2026-11-05.md；**结论**：✅ 修复后 GGUF F16 sciq/piqa limit=100 全 4 项 |Δ|≤1pp（sciq 0.79→0.79/piqa 0.72→0.72），PR 草稿 reports/report_pretrain_llamacpp_pr_draft.md 就绪等用户确认发上游。需要时再读。

> 📦 §#1362（11-05 07:3x, CPU eval退化调查·推翻NaN在权重）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：逐张量扫描5 ckpt权重全无NaN/Inf;2-token前向logits有效。⚠️被#1363推翻(2 token太短,17+ token才触发NaN)。需要时再读。

> 📦 §#1363（11-05 09:0x, CPU eval退化根因·SSM数值不稳定）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：退化ckpt 17+ token时logits全NaN;根因=Mamba2 SSM数值不稳定(PyTorch reference CPU float32);退化eval为NaN伪影非真实能力。被#1360 llama.cpp C++ SSM修复(5 ckpt全可出分)取代。需要时再读。


> 📦 §#1359（11-05 06:0x, ROOT CAUSE:Q/K undo_permute损坏）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：Q/K权重被GGUF转换undo_permute损坏(max_diff0.15);Nemotron-H RoPE不需permute;fix=undo_permute=False。被#1360 3-bug fix(commit 5dc38db00,Δmax0.006)落地。需要时再读。
> 📦 §#1357（11-05 04:1x, 22:1x+14:0x执行·静态对照A/B/C已落盘·清理完成）→ daily-memories/2026-11-05.md「归档 2026-11-05」节；**结论**：A(group)PASS/B(conv1d)PASS/C(dt clamp)FAIL(无clamp);清理llama-server11→1/GGUF去重7→2释放21G;3.6nats偏差需D/E。被#1360 3-bug fix彻底解决。需要时再读。

> 🆕 2026-11-04 13:2x #1356：**运维令 13:2x logits 逐 token 对齐·根因定案=映射/计算错误（非精度累积）·llamacpp.txt §6+§7 已更新·等用户令**。运维令 13:2x（logits 对齐定案根因）执行结果：① **实验**：iter_10000 HF float32（p6_tf5 transformers 5.17，mamba_ssm/causal_conv1d blocked→PyTorch reference）vs llama.cpp F16 GGUF（build 149f5641b，llama-server /v1/completions + logprobs），同一 prompt 同一 token IDs。② **三个递增长度 prompt 对比**：1 token "Hello"→argmax 均为 ',' 但 logprob 差 **3.6 nats**（HF -0.78 vs LC -4.38）；2 token "The capital"→HF argmax ' of'(-0.64) vs LC argmax ' cost'(-5.86)，argmax **不匹配**，正确答案差 5.66 nats；5 token "The capital of France is"→HF argmax ' Paris'(-0.74) vs LC argmax ' the'(-4.20)，**' Paris' 不在 LC top-20**！③ **根因最终判定=映射/计算错误**：1 token 即 3.6 nats 偏差→排除递归累积精度假说（后者需多 token 才显现）；偏差从第 1 层 Mamba2 就开始→指向 build_mamba2_layer/nemotron-h.cpp 与 PyTorch reference 的系统性映射差异（group 展开/conv1d/dt 投影）；LC logprob 分布近乎均匀→hidden states 严重损坏。④ **nemotron-h.cpp 后续修复核对**：`git log 149f5641b..HEAD -- src/models/nemotron-h.cpp src/models/mamba-base.cpp`=空→HEAD=build commit，无额外修复。⑤ **修复方向**（已写入 llamacpp.txt，不擅自实施）：group 映射/conv1d/dt 投影/单层 hidden dump 逐层定位。⑥ **llamacpp.txt 更新**：§6 根因从"待做"改为定案结论+实测数据表+修复方向，§7 最终结论同步更新。⑦ **纪律**：CUDA_VISIBLE_DEVICES=""全程，OMP=8/nice19，S1 .29 GPU 97-100%健康，.12 CPU 90.6%idle，kill 仅 server PID 1313067，accelerate 临时 patch 已恢复。📦 体积：TASK=33.4KB(>32KB,<40KB红线)/MEMORY≈18KB✅。未完成指令：无（13:2x logits对齐已完成交付+commit，llama.cpp=FAIL等用户令）⇒ WAITING: 1。

> 🆕 2026-11-04 13:0x #1355：**llama.cpp 深度根因调查轮·GGUF 元数据验证=正确·真根因=C++ Mamba2 计算·报告已更正·50K eval DONE 5/5 完成·报告已更正**。运维令 09:3x（llama.cpp 提速）深度调查结果：① **GGUF 元数据经原始二进制解析验证完全正确**：block_count=56、feed_forward_length 数组(28 MLP=8192/24 SSM=0/4 attn=0)、head_count_kv 数组(4 attn=4/其余=0)→层分类逻辑正确。② **权重值逐一比对一致**(bf16→f16 精度仅)。③ **此前根因"Duplicated key 覆写元数据"不成立**——转换无实质错误。④ **真根因**：C++ `build_mamba2_layer`(基类 `llm_build_mamba_base`)的 Mamba2 SSM 数值实现与 PyTorch reference 有系统性计算差异→56层误差累积→logit 偏移。⑤ **生成质量测试**："The capital of France is"→GGUF 输出"the French department, which is the French department"(重复垃圾)→推理根本损坏。⑥ **llama-bench 测速**：F16 CPU 8线程 pp128=82 t/s / tg64=21 t/s（vs HF float32 ~3 t/s，快约7×但精度不可用）。⑦ **/v1/completions 格式**：返回新版 `logprobs.content[]` 非 `token_logprobs`，需 shim 或 --model gguf 后端（次要矛盾）。⑧ **5/5 eval 全部完成**：iter_10000 Avg=50.0%✅ / iter_30000 Avg=50.25%✅ / iter_20000+40000+50000 均 Avg=28.75%⚠️NaN(sciq=0.0, 三 ckpt 结果完全一致, md5 各不同→NaN 导致 tie-breaking 确定性, FP8 间歇性溢出)。⑨ **报告已更正** §⑤根因+llama-bench+生成测试+格式, §⑥ NaN 更新, 5/5 汇总表填满。**VERDICT: llama.cpp=FAIL(精度不可用)，保留 HF float32，等用户令**。📦 体积：TASK=31KB✅/MEMORY≈16KB✅。未完成指令：无（5/5 eval DONE, 报告已更新, llama.cpp=FAIL 等用户令）⇒ WAITING: 1。
> 📦 §#1322-#1328（11-04 03:28–04:12, 7轮监控·pilot=FAIL等令·4evals推进·S1 iter74190→74580）→ daily-memories/2026-11-04.md；**结论汇总**：4 evals稳定推进(.29~17s/it/.12~28s/it), 最坏ETA~13:05<deadline✅, iter_10000 DONE Avg50%, S1全程0NaN, CPU均<<80%。pilot=FAIL等用户令。需要时再读。

> 📦 §#1332（11-04 08:28, 监控轮·4evals推进正常·S1 iter76780健康）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:20, iter_10000 DONE Avg50%, S1 iter76780健康0NaN, CPU<<80%。被#1333确认继续有效。需要时再读。

> 📦 §#1334（11-04 08:42, 监控轮+归档pilot块·4evals推进正常·S1 iter76880健康）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:15, iter_10000 DONE Avg50%, S1 iter76880健康0NaN, CPU<<80%, pilot块已归档。被#1335确认继续有效。需要时再读。

> 📦 §#1339（11-04 09:07, 监控轮·4evals推进正常·S1 iter77120健康·最坏ETA~13:12）→ daily-memories/2026-11-04.md；**结论**：4 evals推进, 最坏ETA~13:12, iter_10000 DONE Avg50%, S1 iter77120健康0NaN, CPU<<80%。被#1340确认继续有效。需要时再读。

> 📦 §#1346（11-04 10:37, llama.cpp重试new binary 149f5641b·Δ16-18pp未修复·HF evals 2/5DONE+3在跑·S1 iter77890健康）→ daily-memories/2026-11-04.md；**结论**：新binary git diff无SSM改动，sciq=0.61/piqa=0.56与旧pilot一致，Δacc仍超标，保留HF float32。被#1347确认。需要时再读。
> 📦 §#1347（11-04 10:48, 监控轮·清理stale pilot server·TASK归档33918→31010B·HF evals 2/5DONE+3在跑·S1 iter77930健康）→ daily-memories/2026-11-04.md；**结论**：kill旧pilot server, TASK归档至30.3KB✅, .12两evals 95-96% ETA~11:28-11:39, .29 iter_50000_f32 80% ETA~13:03。被#1348确认。需要时再读。

> 📦 §#1348（11-04 10:57, 监控轮·HF evals 2/5DONE+3在跑·S1 iter78070健康·ckpt@78000）→ daily-memories/2026-11-04.md；**结论**：.12两evals 96-97% ETA~11:28-11:39, .29 iter_50000_f32 81% ETA~13:07, iter_10000/30000 DONE。被#1349-#1350确认继续有效。需要时再读。

> 📦 §#1349（11-04 11:03, 监控轮·HF evals 2/5DONE+3在跑·.12两evals ETA~11:28-11:39·.29 83% ETA~12:58）→ daily-memories/2026-11-04.md；**结论**：.12两evals即将完成, .29 iter_50000_f32 82.9% ETA~12:58, 2/5有效DONE。被#1350确认继续有效。需要时再读。
> 📦 §#1350（11-04 11:12, 监控轮·4evals推进·.12两evals即将完成）→ daily-memories/2026-11-04.md；**结论**：4evals推进, .12两evals 97-98%即将完成, .29 iter_50000_f32 84% ETA~12:56, iter_10000/30000 DONE Avg50%/50.25%。被#1351确认(.12两evals完成=NaN)。需要时再读。

> 🆕 2026-11-04 11:40 #1351：**监控+报告更新轮·.12两evals DONE(均NaN)·.29 50000_f32 88%在跑·报告含llama.cpp对照+NaN分析**。.12 iter_20000_f32 DONE 75307s sciq=0.0=NaN(float32也没修！)；.12 iter_40000_f32 DONE 74731s sciq=0.0=NaN。**关键发现：NaN是checkpoint权重问题非dtype**——iter_10000(bf16)OK/iter_30000(f32)OK但iter_20000/40000(f32)NaN→FP8训练间歇性溢出致部分步权重含NaN。.29 iter_50000_f32 @2296/2599(88%)@15.8s/it ETA~12:50(pid668677在跑)。报告已更新40765B含§⑤llama.cpp对照表(f16/f32/newbin三行,pilot=FAIL,Δacc=-17pp)+§⑥NaN分析。2/5有效DONE(iter_10000 Avg50%/iter_30000 Avg50.25%)。S1 ckpt@78000✅训练在跑。CPU .12 load13.3%/.29 load14.5%均<<80%✅。📦 体积：TASK=31010B(30.3KB✅)/MEMORY=30.7KB(归档0B)✅。未完成指令：有(.29 50000_f32 ~12:50完成后→检查NaN→再生成报告→5/5汇总+llama.cpp结论→等用户令)⇒WAITING: 0。

> 🆕 2026-11-04 11:46 #1352：**监控轮·.29 iter_50000_f32 90%在跑ETA~13:00·.12两evals DONE(均NaN,sciq=0.0,Avg=0.2875)·S1 ckpt@78000健康·llama.cpp=FAIL等用户令**。eval实测：.29 iter_50000_f32 @2327/2599(89.5%)@15.9s/it 剩~272req×15.9s≈72min ETA~12:58(pid668677在跑,dir hf_iter_50000_f32仍空)。**结果汇总(全部limit=100)**：iter_10000 Avg=0.5000✅valid(arc_c.29/arc_e.49/boolq.61/hs.36/obqa.20/piqa.72/sciq.79/wg.54)；iter_30000 Avg=0.5025✅valid(arc_c.26/arc_e.57/boolq.47/hs.37/obqa.21/piqa.69/sciq.83/wg.62)；iter_20000 Avg=0.2875❌NaN(sciq=0.0,全任务退化)；iter_40000 Avg=0.2875❌NaN(sciq=0.0,与20000完全相同→确定性退化输出)；iter_50000(bf16) Avg=0.2875❌NaN(同上,_f32重跑中)。**关键观察**：20000/40000/50000(bf16)三者结果完全一致(avg=0.2875,逐任务相同)→NaN权重产生确定性退化行为(非随机)。S1 latest_checkpointed_iteration=78000✅训练在跑(step~6.9s/loss~2.1)。CPU .29 load29.7/224(13.3%)/.12 load27.3/224(12.2%)均<<80%✅。📦 体积：TASK=31010B(30.3KB✅)/MEMORY≈30.5KB(归档#1350→pointer)✅。未完成指令：有(.29 iter_50000_f32 ETA~12:58完成后→检查是否NaN→更新报告5×8汇总表→等用户令)⇒WAITING: 0。



> 📦 §#1292-#1345（11-03 23:24→11-04 10:03, ~50轮监控·pilot=FAIL等令·4 evals推进·S1 iter72110→77600）→ daily-memories/2026-11-03.md & 2026-11-04.md；**结论汇总**：pilot=FAIL已交付(commit 9cdc4469f,根因=3 Duplicated key覆写hybrid元数据),4 evals稳定推进,iter_10000 DONE Avg50%,iter_30000 DONE Avg50.25%,S1全程0NaN,CPU均<<80%。需要时再读 daily-memories。

> 🆕 2026-11-04 12:1x #1353：**llama.cpp 重试·per-token 打分法已打通 logprobs 卡点·pilot DONE=Δacc 仍超标(FAIL)·.29 iter_50000_f32 96%在跑**。**运维令 09:3x 本轮进展**：① GGUF 转换已在 .12 完成（f16, 4.44GB, 20s, 仍有"Duplicated key"WARNING）；② **卡点定位（比运维预研更深）**：llama-server `/v1/completions` echo=True **不返回 prompt token logprobs**（只返回 generated token），lm_eval GGUFLM 靠 `text_offset < context_length` 切分 → 无法打分；`/completion` 端点也无 prompt logprobs；`--model gguf` 路径不可用（非格式问题，是 llama-server 不支持 prompt logprobs）；③ **解决方案 ① shim**：写了 `llamacpp_logprobs_shim.py`（格式转换 PASS ✅，但仍受限于无 prompt logprobs）；④ **解决方案 ② per-token 打分（真正可用）**：写了 `llamacpp_pertoken_lmeval.py`（自定义 lm_eval model，绕过 echo：对每个 continuation token 发 prefix as token IDs → 从 top_logprobs 查目标 token logprob → 累加）；⑤ **pilot DONE=FAIL**：sciq acc=0.42(HF=0.79,Δ=-37pp)/acc_norm=0.57(HF=0.71,Δ=-14pp), piqa acc=0.55(HF=0.72,Δ=-17pp)/acc_norm=0.51(HF=0.73,Δ=-22pp)。703.8s/600req。**根因**：BPE merge boundary(split 不准)+n_probs=50 截断+Duplicated key 元数据损坏(上轮已确认)。**VERDICT: FAIL，保留 HF float32 路线，等用户令**；⑥ **.29 iter_50000_f32** @2485/2599(95.6%)@15.9s/it ETA~30min。S1 训练健康(8 GPU 96-100%, ckpt@78000)。CPU .29 15.1%/.12 轻载 <<80%✅。📦 体积：TASK=31010B(30.3KB✅)/MEMORY≈16KB(归档~17KB→daily-memories)✅。未完成指令：有(.29 iter_50000_f32 ~30min完成后→检查是否NaN→5/5汇总+报告更新→等用户令)⇒ WAITING: 0。
> 🆕 2026-11-03 23:12 #1290：**🦙 llama.cpp pilot 已完成 → VERDICT=FAIL（不切换 GGUF，保留 HF 路线）**。iter_10000 F16 GGUF 跑 sciq+piqa --limit 100：06 契约自检 PASS ✅（tokenize/token-id prompt/logit_bias/n_probs）·02b 分词对拍 **24/24 PASS** ✅（用 tokenizers lib 绕开 py310 numpy ABI 冲突）·加速 **7.0x** ✅（1403.9s vs HF 估 9864s）·**但 |Δacc| 严重超标**：sciq 79%→61%(Δ=-18pp)·piqa 72%→56%(Δ=-16pp)·Avg Δ=-17pp（判据≤1pp）❌。最可能根因：F16 在 Mamba2 SSM(24/56层)递归累积精度不足（此前 bf16 在 HF 侧已致 NaN）。已交付 `reports/report_pretrain_llamacpp_pilot_zh.html`(5.4KB, 0 script/0 外链) + comparison.json + meta.json + 新增 `02b_check_tokenizer_fast.py`/`gen_pilot_report.py`。S1 iter71980/loss2.099/0NaN 健康未受影响。**按用户令：PASS 后先报告再等令——本轮 FAIL，同样等令，不擅自全量切换。** 未完成指令：有 ⇒ WAITING: 0。
> 📦 §#1291（11-03 23:17, 监控轮·pilot DONE 等令·3 evals 推进）→ daily-memories/2026-11-03.md；**结论**：iter_30000 29/2599(1.1%)@48s/it(ramping down), iter_40000 956/2599(36.8%)@30.4s/it→done~Nov4 13:15, iter_20000 953/2599(36.7%)@30.3s/it→done~Nov4 13:13, S1 iter72040/loss2.107✅, CPU .29 16.8%/.12 15.3%<<80%✅。被#1292 校正(iter_30000 ramp-down 收敛至16s/it done~Nov4 09:17)。需要时再读。
> 📦 §#1290（11-03 23:12, llama.cpp pilot=FAIL）见上条详述。需要时再读。
> 📦 §#1289（11-03 22:10, 监控轮·iter_50000 96.9%）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 96.9%(2518/2599) ETA~22:31, .12 双 float32 31.6%+31.4% ETA Nov4 13:12-13:15, iter_30000 SIGSTOP(510), S1 iter71470健康。被#1290 接续（pilot 已完成=FAIL）。需要时再读。
> 📦 §#1288（11-03 22:04, 监控轮·iter_50000 95.8%@15.67s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 95.8%(2491/2599) ETA~22:31, .12 双 float32 31.1%+31.0%(808+805)@~30.1s/it ETA Nov4 13:07-13:13, iter_30000 SIGSTOP(510), S1 iter71410/loss2.098健康。被#1289 校正(iter_50000 96.9%(2518)@15.68s/it, .12 820+817@~30.4s/it, S1 iter71470/loss2.101)。需要时再读。
> 📦 §#1287（11-03 21:57, 监控轮·iter_50000 95.0%@15.99s/it）→ daily-memories/2026-11-03.md；**结论**：4 evals 稳定推进, iter_50000 95.0% ETA~22:32, .12 双 float32 30.5%+~30%@~29.5s/it ETA Nov4 12:45-12:55, iter_30000 SIGSTOP(510), S1 iter71360/loss2.112健康。被#1288 校正。需要时再读。
> 📦 §#1286（11-03 21:52, 监控轮·iter_50000 94.2%@15.66s/it）→ daily-memories/2026-11-03.md；**结论**：被#1287 校正。需要时再读。
> 📦 §#1285（11-03 21:46, 监控轮·iter_50000 93.3%@~16.1s/it）→ daily-memories/2026-11-03.md；**结论**：被#1286 校正。需要时再读。
> 📦 §CPU-eval-snapshot #1234-#1290（11-02→11-03, 5 ckpt HF float32 CPU eval 监控·iter_10000 Avg=50.0% DONE/iter_50000 bf16 sciq=0 NaN/bf16→float32 修复/OMP=8/SIGSTOP 副作用）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论**：iter_10000 Avg=50.0%, bf16 NaN→float32 修复, 全 5/5 CPU eval 已被 11-05 llama.cpp 修复管线取代。需要时再读。
> 📦 §#1234-#1283（11-03 14:50→21:34, ~40轮监控·iter_50000 56%→92%·bf16 NaN根因+float32重跑+OMP=8+SIGSTOP优化）→ daily-memories/2026-11-03.md；**结论汇总**：bf16 NaN→float32修复, OMP=8收敛34.78s/it, SIGSTOP优化, 速度收敛(.29~16s/.12~30s), iter_10000 DONE Avg50%, CPU全程<<80%。需要时再读 daily-memories。



> 📦 §#1154-#1241（11-02 19:55→11-03 16:13, CPU eval监控·1-80轮+bf16 NaN根因+float32重跑+OMP优化+SIGSTOP）→ daily-memories/2026-11-02.md & 2026-11-03.md；**结论汇总**：5 export完成, bf16 NaN→float32修复, OMP=8, SIGSTOP优化, 速度收敛(.29~16s/.12~30s), iter_10000 DONE Avg=50%, ETA从~10天下修至<24h, CPU全程<<80%。需要时再读 daily-memories。
> 📦 §#1076-#1151（11-01 11:26→11-02 12:55, S1健康监控iter41950→55140, 共~70轮）→ daily-memories/2026-11-01.md & 2026-11-02.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.10-2.16稳态, 吞吐~550-631K tok/s(多数~605K), ckpt iter_38000→54000, grad-norm极稳(偶发瞬态spike均自恢复), decay 5000步CS8=58.97%, 论文6页ERR=0, baize-llm项目目录就绪。需要时再读 daily-memories。
> 📦 §#1043及更早（11-01 11:26前, iter≤41950, S1监控链#1044~#1067及更早）→ daily-memories/2026-11-01.md & run/ARCHIVE_OPERATOR_PRETRAIN.md；**结论汇总**：S1训练全程健康0NaN/0skip, loss~2.12-2.16稳态, ckpt iter_38000→42000; decay CS8=58.97%; 论文6页ERR=0。需要时再读。

---

## 关键笔记（运维常驻参考）
- seq_length=**4096**（=2¹²，用户直令 2026-10-14 固定口径）；改 seq 必须同时改 provider（recipe 已穿透）。
- WSD 语义：`--lr-decay-iters`=退火尾段；stable 段=train_iters-warmup-decay 自动。P-5b 口径 warmup238/decay477/4771步。
- 数据：P-5b 用 `data/p5b_l3/p5b_l3_train_s{0..15}`（16 片 1:1 blend ≈20.6B token）；P-8 主体=Ultra-FineWeb-L3 全量（base 下载中）。
- 环境：**训练**=`py310` env（`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`）；**推理/sglang 服务**=`vllm` env（sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13，Python 3.12）。
- 进程识别：单次 8 卡=1 torchrun master + 8 worker（pretrain_launcher）+ 每 rank 11×pt_data_worker，勿误判重复拉练。
- ⚠️ **机器甄别（防误判·2026-10-19 #601 立此存照）**：pretrain watchdog loop（`baize_pretrain_loop.sh` PID1294448）跑在 **.12**，但主训练（`baize_xmodel25_decay_v2.py` PID2597555）跑在 **.29**。判活检查（`pgrep -af torchrun` / `nvidia-smi` / `tail /tmp/baize_xmodel25_decay_v2_train.log`）**必须先 `ssh -o StrictHostKeyChecking=no 10.239.2.29 '...'` 再做**——在 .12 本地做会看到 ArmC 训练(PID3565540,`mllm_bridge/stage15_train_armC.py`,port30077,.12 8卡~15GB/卡)+已杀的#550 resume 日志(止于 step8070@17:17 SIGTERM)，**误判主 run 已死** ⇒ 这正是 #548/#550 两起误判的根因。SSH 已验证可用。判活三件套只在 .29 上有效；.29 的 `/tmp` log 才是主 run 实�