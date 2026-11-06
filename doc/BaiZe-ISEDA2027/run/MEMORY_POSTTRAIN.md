# MEMORY_POSTTRAIN.md — BaiZe Stage(ii) LLM Post-Training agent 运行时记忆

> ⭐ 本文件每次唤醒被全文读进 cline 上下文 ⇒ ≤32KB；超限滚动到 `daily-memories-posttrain/`。
> `WAITING:` 只在顶部出现一次；正文/流水/快照里不得再出现以 `WAITING:` 开头的行。

WAITING: 1

## 进度快照

- PHASE: posttrain-wake6（2026-11-06；补产 P1 数据盘点 HTML 报告 `reports/report_posttrain_data_inventory_zh.html`——此前 wake2 做了 P1-a/b/e 数据盘点写入 EXPERIMENTS 但**漏产 P1 交付物 4 的 HTML 报告**，本轮补齐：10 节/30.5KB/0 脚本/0 外链/自包含）
- 已完成: P3预备✅ 5 脚本骨架（wake1/2）；P1-e✅ 污染隔离闸门（wake2）；P1-a/b✅ 数据盘点（wake2）；P2✅ 三步方案书（wake3）；**P0✅ D1–D6 DeepSeek 侧实测报告（wake4 §1–§11 → wake5 增 §12 跨运行稳定性 22.0KB）**；**P1-d✅ PyAether 语料调研（4–5M tok，wake4）**；**P0✅ 跨运行稳定性验证（wake5）**；**P1✅ 数据盘点 HTML 报告 `reports/report_posttrain_data_inventory_zh.html`（wake6 补产，30.5KB/10 节/0 脚本 0 外链）**
- 当前动作: wake6 发现 P1 交付物 4（HTML 报告）从未产出（wake2 只写了 EXPERIMENTS §Data 表）→ 读 EXPERIMENTS §Data/§PyAether-corpus/§P1-e + DATA_MAPPING §A#11/#12 + §F（B 类 12 源 78.73GiB）→ 产 `report_posttrain_data_inventory_zh.html`（10 节：摘要+P1-a+P1-b+P1-c+P1-d+P1-e+退火语料组装+SFT 混合建议+阻塞项+红线合规；30.5KB ≥10KB ✅；0 script 0 外链 ✅）→ 更新 MEMORY/EXPERIMENTS → 体积自检+提交 `posttrain data:`
- 下一步: **本节点可达零 GPU 任务已全部完成**（P0 DeepSeek 侧含跨运行/P1 全套含 HTML 报告/P2/P3预备 全 done）。剩余：① P0 **MiniCPM5-2B 36% 侧** D1/D2/D6（轨迹在评测机 `~/eda_code_eval/`，不在本节点）→ 待运维拷贝或挂载；② P1-c（`/nas_inference` 未挂载 .17）→ 待运维挂载或 .29/.12 盘点；③ 正式训练 P3 阻塞 pretrain S1 ckpt（ETA≈2026-12-25）。下次唤醒先复查 ①②数据是否到位。
- 阻塞: P0-36%侧（eda_code_eval 在评测机非 .17）/P1-c（/nas_inference 未挂载 .17）待运维；正式训练阻塞 pretrain S1 ckpt（ETA≈2026-12-25）
- 未完成指令: 有（P0-36%侧 + P1-c 阻塞于本节点不可达的外部数据，待运维；本节点可达项已全完成含 P1 HTML 报告补产）⇒ WAITING=1

## 关键事实（常驻）

- pretrain S1 现状：iter~101320/700000，loss~2.058，ETA≈2026-12-25（`.29` 8×H100）
- post-train 正式训练窗口：≈2026-12 下 → 2027-01 中（ISEDA 投稿 2027-02-01）
- 评测锚点：MiniCPM5-2B 36%（full harness，与 DeepSeek 94% 同口径，差 58 pp）
- 评测基准：EDA-Eval-PyAether 158 任务，Pass@1，5-run mean±std，2500s/任务，`-p 8 -n`
- 成功阶梯（预注册）：36%(起点) → 50%(M1) → 65%(M2) → 75%(M3) → 85%+(M4)
- SFT 数据已就绪：UltraData-SFT-2605（319G 下载/75.87GB 分词/18.89B tok，DATA_MAPPING 单一事实源）+ UltraData-SFT-Agent-2609（54.22G 下载/23.89GB 分词/5.97B tok）已分词镜像
- B 类 agentic 数据已下载未分词（`/nas_inference`：AgentTrove/Nemotron-Cascade-SFT-SWE 等）
- PyAether 领域语料：✅ **已调研**（wake4）—— `~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json` 8,463 个 API（api_name/api_type/api_descriptions/category）展平 ≈3.3–4.5M tok；加 func_all_v3/api_summary/skills/prompts ≈4–5M tok 可导出纯文本；chroma_db_*（向量嵌入）不用；退火 domain 主体 + SFT 合成语料（详见 EXPERIMENTS §PyAether-corpus）
- 论文章节：`BaiZe-ISEDA2027/ISEDA2027/5_llm_posttrain.tex`（已写设计，结果=[TBD]）

## 运维问答（常驻）

- Q: post-train 现在能起训练吗？→ A: 不能。等 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。现在做 P0/P1/P2/P3预备（零 GPU）。
- Q: 用哪台机器？→ A: post-train 线在 `10.252.32.17`。P0/P1/P2/P3预备 纯 CPU/IO 在本机 `.17` 跑；正式训练的 GPU 待 pretrain 完成或运维协调分卡。
- Q: 评测怎么接入 BaiZe？→ A: vLLM/SGLang 暴露 OpenAI-compatible endpoint → `cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，harness 不改。
- Q: 红线？→ A: ① 158 任务禁入训练集（污染隔离）② anti-cheat 全程开 + 报 cheat rate ③ 5-run mean±std + 配对检验 ④ 评测协议冻结不改。

## 本唤醒流水

[14:00] wake1：恢复状态→查 P0 数据源（~/eda_code_eval、/nas_data/.../eda_code_eval、/nas_data/.../eda_fastmcp、训练数据BASE 全 MISSING；final_report.json 0 命中）→ P0 D1–D6 字段缺失（数据源不可达，已记口径，🚫 不编造、不产出空 HTML）→ 转做 P3-prep：写 4 脚本骨架（anneal/sft/rl_grpo/eval，参照 baize_p8_train.sh + baize_xmodel25_decay_v2.sh 结构，含 --dry-run 配方打印）→ bash -n 4/4 PASS + --dry-run 4/4 rc=0 → 写入 EXPERIMENTS §D(阻塞) + §Scripts(验证输出) → 体积自检+提交。
[14:30] wake2：git fetch/pull（需显式设 https_proxy=http://172.19.92.25:13128，非交互 shell 无 .bashrc 代理；清 14:13 陈旧 index.lock 后 fast-forward 到 8599eae7c）→ 复查数据可达性：eda_code_eval/eda_fastmcp//nas_inference/数据镜像(/nas_data/.../datasets) 本节点仍全 MISSING → 按 MEMORY 应急做 **P1-e**：读 CONTAMINATION_CHECK.md v0.3（data 线已建 536 任务黑名单 + check_contamination.py，220K docs 0 命中）→ 写 `baize_posttrain_contamination_gate.sh`（复用 check_contamination.py，逐输入扫描解析"命中（污染）文档数：N"，N>0 exit 2 阻断 / N=0 exit 0 / 缺件 exit 3 fail-safe；--dry-run + --build-blacklist）→ bash -n OK + dry-run(0/3输入/build) rc=0 → EXPERIMENTS §Data(P1-a/b 引 DATA_MAPPING 实值 18.89B/5.97B tok、P1-c/d 阻塞、P1-e✅) + §P1-e(规则+脚本+验证) + §PyAether-corpus(阻塞) + §Scripts(+gate 行) → 体积自检+提交。
[14:48] wake2 收尾（git 同步）：push 被 origin 领先拒绝 → 前台 `git pull --rebase --autostash` 两次撞 30s 工具超时被 kill（残留 stale index.lock[0B] + autostash 致工作区回退到提交前旧版）→ 改用 `setsid` 后台脚本 `/tmp/pt_sync.sh` 跑 pull --rebase --autostash + push：rebase 成功 replay 我的 commit → push `944a201de` 上远端（PULL_RC=0 / PUSH_RC=0）→ `git status` 见工作区 4 文件 M/D（autostash 旧版回灌）→ `git checkout --` 仅本线 4 文件恢复到 HEAD → NFS dir-cache lag 误报 gate 脚本缺失（`sync` 后 `test -f`=FILE_EXISTS 7896B）→ `git status` 干净 `## main...origin/main`。**坑（新增常驻）**：① 非交互 shell 无 .bashrc 代理须显式 `export https_proxy=http://172.19.92.25:13128`；② 慢 NFS+代理使单次 git op >30s 工具超时 ⇒ 须 `setsid` 后台跑 + 轮询日志；③ 被 kill 的 rebase 会留 stale index.lock + autostash 致工作区回退到旧版，恢复后必 `git checkout -- 本线文件` + 验证 `test -f`/`git status`；④ autostash 仅对**本线文件** checkout，绝不碰别线在途文件。
[15:10] wake3：git fetch+pull（behind 2 → `setsid` 后台 pull --rebase --autostash，PULL_RC=0，fast-forward 到 7738cd214）→ 读论文 `5_llm_posttrain.tex` §5.1–§5.5 + README §2/§3/§4/§5/§6/§7.0 → 写 **P2 三步训练方案书** `reports/report_posttrain_plan_zh.html`（38KB / 409 行 / 11 节：前提依赖 + 领域退火 + SFT + RL 4 臂 + 评测网格 + 成功阶梯 M1–M4 + 预注册阈值 + 时间线 + 风险 + 红线 + 脚本附录；0 script / 0 外链 src / 11 href 全为内部锚点；≥15KB ✅）→ EXPERIMENTS §Plan（方案要点表 + 成功阶梯 + 判定阈值 + 红线合规 + 阻塞项）→ 体积自检（TASK=20.8KB ✅ / MEMORY=5.8KB ✅）→ 提交 `posttrain plan:`。📦 体积：TASK=20.8KB / MEMORY=5.8KB（均 ≤32KB ✅，无需归档）。
[16:30] wake4：git fetch+pull（setsid 后台 pull --rebase --autostash，fast-forward）→ **⚠️→✅ 修正 wake1 路径误判**：wake1 查 `/nasdata`/`/nas_data/...` 全 MISSING，本轮改查 `~/code/` 发现 **eda_fastmcp（BASE_DIR）+ EDA-Eval-Framework + 158-case 数据集全在本节点可达**（`~/code/eda_fastmcp/pyAether-eval/...` + `~/code/EDA-Eval-Framework/output_evaluation/`13 份 final_report.json + DeepSeek 全 harness 轨迹 `cline_cli_trace/cline_trace_v1_3/`103 任务）→ 系统 python3=3.8 不支持 `str|None`，改用 `~/code/eda_fastmcp/.venv/bin/python`(3.13) 跑 `trace_reader.py` 的 `extract_tool_calls_from_trace`/`extract_tool_results_from_trace`/`classify_error` 提取 → `/tmp/pt_p0_analyze.py` → `/tmp/pt_p0_summary.json` → `/tmp/pt_p0_report.py` 产出 **`reports/report_posttrain_diagnose_d1d6_zh.html`**（18.3KB/11 节/0 script/0 外链/自包含，验证 grep 0 命中）：DeepSeek 全 harness 侧 **D1=0.6317（强度代理）/ D2=14.32 tool/task（search_apis 573/run_code 516/get_api_details 386）/ D3=0% 超时（0/103）/ D4=执行报错74%（import22/file19/type10/attr5/syntax3/name3）vs 断言26% / D6=Φ 均值5.01 中位5（1–14）**；代码生成侧 7 份 final_report + 数据集 metadata 联算 **D5 per-scenario**（Schematic66%<Layout64%<DesignMgmt83%≈Others83%，多轮 mean≈67% std≈2.6pp）+ 数据集画像（scenario 64/47/24/23 与任务书一致；category 分布；techlib_dependency 28%）；**结论：58pp 主体(估35–45pp)为"协议可回收"——工具频次/合法率/API领域知识/迭代闭环，对应 SFT→退火→RL(GRPO)；剩余10–15pp 真实能力差距**。MiniCPM5-2B 36% 侧 D1/D2/D6 **诚实标注"轨迹不在本节点"**（`~/eda_code_eval/` 在评测机非 .17）→ 待运维拷贝。同步 **P1-d PyAether 语料调研**：`docs/API_INFO_MERGED_V3.json` 8,463 个 API 展平 13.36M 字符 ≈3.3–4.5M tok + func_all_v3/api_summary/skills/prompts ≈**4–5M tok 可导出纯文本**（chroma_db_* 向量嵌入不用；CONTAMINATION_CHECK §5 0 命中合规）→ EXPERIMENTS §D（替换"字段缺失"表为实测值）+ §PyAether-corpus（替换"阻塞"为调研表+组装方案）+ §Data P1-d 行改 ✅ → 体积自检 + 提交 `posttrain diag:`。📦 体积待检。
[16:50] wake5：git status 干净（`## main...origin/main`）→ 复查阻塞数据源：`~/eda_code_eval/` 仍 MISSING + `/nas_inference` 仍未挂载 → grep -ri 'minicpm' 本节点 trace 目录 + EDA-Eval-Framework 零命中 → 确认本节点无 MiniCPM5 轨迹（36% 侧仍待运维）→ 转做**可达增值项**：对第二次 DeepSeek 全 harness 运行 `cline_trace_v1`（01-29, 103 任务）用同口径 `trace_reader.py`+`trace_parser.py`（venv py3.13）提取 D1/D2/D3/D4/D6 → `/tmp/pt_p0_crossval.py`→`/tmp/pt_p0_crossval.json` → **跨运行对比**：D1=0.6727vs0.6317(6%🟢稳定) / D2=20.51vs14.32(30%🟠) / D3=0%vs0%(🟢) / D4=100%执行报错vs74%(26%🟠) / D6=7.06vs5.01(29%🟠) / avg错=0.04vs0.85(🔴) → **判读：D1/D3 鲁棒单次可信；D2/D4/D6 单次±30%噪声须多运行→从诊断侧印证 5-run mean±std 必要性；不改变核心结论但增置信区间** → 报告 `report_posttrain_diagnose_d1d6_zh.html` 增 §12 跨运行稳定性（22.0KB/12 节/0 script/0 外链，验证 PASS）→ EXPERIMENTS §D 增"跨运行稳定性"子节 → 5 脚本 bash -n 全 PASS（健康复查）→ 体积自检 TASK=20.8KB✅/MEMORY=10.4KB✅ → 提交 `posttrain diag:`。📦 体积：TASK=20.8KB / MEMORY=10.4KB（均 ≤32KB ✅，无需归档）。
[17:00] wake6：git status 干净（`## main...origin/main`）→ 复查阻塞数据源：`~/eda_code_eval/` 仍 MISSING + `/nas_inference` 仍未挂载（与前 5 轮一致）→ **发现遗漏交付物**：P1 交付物 4 要求产 HTML 报告 `reports/report_posttrain_data_inventory_zh.html`，但 wake2 只写了 EXPERIMENTS §Data 表从未产 HTML → 读 EXPERIMENTS §Data（P1-a 18.89B tok/P1-b 5.97B tok/P1-c 78.73GiB 12源/P1-d 4-5M tok/P1-e 536黑名单）+ DATA_MAPPING §A#11/#12（分词镜像实测）+ §F（B类12源明细）→ 产 `report_posttrain_data_inventory_zh.html`（10节：摘要+P1-a通用SFT+P1-b agentic SFT+P1-c B类12源+P1-d PyAether语料+P1-e污染隔离+退火语料组装+SFT混合建议+阻塞项+红线合规；30.5KB ≥10KB ✅；0 script/0 外链 ✅；验证 grep 0 命中）→ 更新 MEMORY（PHASE→wake6·已完成增P1 HTML·关键事实修正token数 18.89B 非 20.97B）+ EXPERIMENTS §Data 增 HTML 报告交付指针 → 体积自检+提交 `posttrain data:`。📦 体积待检。

