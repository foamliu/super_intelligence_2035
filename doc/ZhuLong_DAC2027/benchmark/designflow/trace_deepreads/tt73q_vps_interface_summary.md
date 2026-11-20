# Deepread note: 1791897142698_tt73q → EDA-Eval-DesignFlow-VpsInterfaceSummaryQA-001

**shard**: A (eda_other)  **round**: r798  **date**: 2026-11-19
**trace**: `1791897142698_tt73q.messages.json` (233KB, 19 msgs, agent=lead)
**user/host**: jason17w @ 10.129.32.190 (hfhds208 / hfeg0pnd002)  **mc**: 5

## 用户原话 (USER[15])
> 给我总结一下VPS有哪些接口，能做什么？这份总结用于我们智能EDA部门举办AI开放日时说明这个通过Agent启动运行vps的flow有什么优势，我们基于这个平台开发了一套新的flow（第一步：自然语言任务提交。第二步：智能结果分析-决策重跑。第三步：智能结果分析执行重跑生成报告）

## 任务定性
单轮 **analysis-Q&A** (S5 第二范式)。用户要一份 VPS 接口总结 markdown, 用于 AI 开放日
说明 Agent-driven vps flow 的优势。非 doc-search/retrieval (用户语料就在本地 cline skill
目录与 vps/run_regr 目录), 非 env-config, 非 debug-Q&A。11-15 重审后 analysis-Q&A 可建案。

## 真实 A 资产 (scp from 10.129.32.190 → eda_flow workdir)
- `/home/jason17w/.cline/skills/vps-cli/SKILL.md` (20KB) — VPS CLI 完整参数表 (38 旗标) +
  VPC 语法 + task 状态 + category 大全 + GUI + FAQ + 已知陷阱
- `/home/jason17w/.cline/skills/vps-cli/VPS_User_Guide_Reference.txt` (60KB, 3684 行,
  VPS_v2025.09, UniVista) → 裁剪为 `VPS_User_Guide_Reference_trimmed.txt` (12KB, 保真摘录)
- `/home/jason17w/vps/run_regr/run_regr.py` (17KB, 21 funcs) — 自定义回归驱动 (argparse +
  generate_vpc/run_vpc/main)
- `/home/jason17w/vps/run_regr/custom_utils.py` (11KB, 6 funcs) — read_caselist/create_child_case/
  get_task_name/get_byte_value/get_uvs_version/get_define_envs
- `regr.env` (auto_rety=2, retry_percent=100, VPS_PROJECT=uvs_regression) +
  `README_run_regr` + `task_post_cmd.sh` + `all_on_task_post_cmd.sh` (custom_field + perf_data.txt)

## ground-truth 签名 (subprocess 解析 A 拼接文本推导, 非 hardcode)
- 版本 `VPS_v2025.09` / 厂商 `UniVista`
- vps CLI 18 核心旗标: `-c CONFIG_FILE` `--dryrun` `--run_mode{normal,extract,merge}`
  `--data_mode{normal,profile}` `--tasks` `--groups` `--tags` `--mail_enable` `--cov`
  `--rerun_only` `--no_rerun` `--probe_enable` `--selected_only` `--daemon` `--cpu_affinity`
  `--lite` `--db` `--timeout`
- VPC 段: `[[tasks]]` `[env]` `[group.X]` `[coverage]` `[mail]`; extends/include; env 四级作用域
- task 状态: `pass`/`fail` (+DONE/RUNNING/PENDING/ABORTED/KILLED/LOST/TIMEOUT);
  产物 `PASS.list` `FAIL.list` `NON_PASS` `ALL.list` `summary.json` `result.log` `reproduce.sh`
- smart timeout: `Timeout = smart_timeout_factor * avg_duration + smart_timeout_base`;
  `VPS_TASK_SMART_TIMEOUT_FACTOR` / `VPS_TASK_SMART_TIMEOUT_BASE`; group/task 级覆盖
- 自动重试 `retry` / 自动重跑 `rerun_cmd` (enabled/disabled 二选一);
  条件依赖 `all_success` `all_failed` `all_completed` `any_success` `any_failed`
- `custom_field -p key=value` 写 VPS DB; `perf_data.txt` (task_post_cmd.sh 生成) 由 custom_field 写库
- 驱动函数: `generate_vpc` `run_vpc` `read_caselist` `create_child_case` `get_task_name`
  `get_tasks` `get_retry` `get_rerun` `get_coverage` `get_mail` `get_early_stop`

## hidden B (specificity oracle, judge-only)
`hidden/vps_guide_B.txt` = 同构但 8 维度标识符全部改名的 `TRO_v2024.03` / `TestFlowCorp` 变体:
1. 版本 VPS_v2025.09 → TRO_v2024.03
2. 厂商 UniVista → TestFlowCorp
3. CLI config 旗标 `-c CONFIG_FILE` → `--cfg CONFIG_FILE`
4. task 段 `[[tasks]]` → `[[jobs]]`
5. 状态 `pass/fail` + `PASS.list/FAIL.list/NON_PASS` → `ok/ko` + `OK.list/KO.list/NON_OK`
6. smart-timeout 常量 `VPS_TASK_SMART_TIMEOUT_FACTOR/BASE` → `TF_SMART_FACTOR/BASE`
7. 自定义数据 `custom_field` + `perf_data.txt` → `tro_metric` (无 perf_data.txt)
8. 适配脚本 `setup_regr/run_regr` → `setup_tro/run_tro` + `TRO_HOME`
B 独有标识符 34 个 (TRO_v2024.03/TestFlowCorp/--cfg/[[jobs]]/OK.list/KO.list/all_ok/
TF_SMART_FACTOR/setup_tro/tro_metric/--preview/--deadline/--labels/--squads/--notify/
--merge_cov/--picked_only/--bg_daemon/--pin_cpu/--slim/TRC/tro_log/job_logs/jobsquad/...)
须不出现在 SUT 关于 A 的报告 (防背题/防抄 B)。

## check.py 设计 (15 条独立断言, k_check=k_rationale=15)
① 非空壳(>=200字)+含VPS  ② 版本VPS_v2025.09  ③ 厂商UniVista
④ CLI `-c CONFIG_FILE` + 语义邻近(VPC/配置/回归)  ⑤ 覆盖>=6/18核心旗标
⑥ 状态产物PASS.list/FAIL.list/NON_PASS + 语义邻近(task/状态)
⑦ smart_timeout机制  ⑧ custom_field+perf_data.txt  ⑨ 条件all_success/all_failed/all_completed(>=2)
⑩ rerun_cmd重跑  ⑪ 驱动函数>=2/11  ⑫ 反造假(旗标必在A白名单)  ⑬ specificity oracle(不含B独有34标识)
⑭ 反退化(>=2标题+中文>=30+>=4能力类别词)  ⑮ 确定性(核心签名池>=8/19, 3 seed抽样命中)
ground-truth 自检: 每条先验 A 真带该签名 (判分口径错则 _fail)。

## 验证
- 参考解 `make_summary_ref.py` (解析 A → 合成结构化中文 md → submit.zip) **PASS 15/15**
  (flags_covered=12, core_pool=19, b_only_count=34)
- 5 负例全 FAIL:
  - neg_empty (§4.9a) → ① (6字<200)
  - neg_print_expected (§4.9b) → ④ (裸旗标串无语境)
  - neg_delete_core (§4.9c) → ② (无版本号)
  - neg_hallucinate_B → ⑫ (编造B旗标 --merge_cov/--picked_only/--bg_daemon/--pin_cpu)
  - neg_generic_eda → ① (无VPS)
- §4.9 a/b/c 全 FAIL ✓

## 同轮审计的另两个 parked 候选 (均判 non-buildable)
- `1794193348712_x0mjt` (wscli env-config): agent 全程配 wscli 环境, 从未产出 deliverable → 不可建案
- `1792224394327_gheik` (private-KB doc-search): 源文档 `【G3】LP4_CM_Manual_DBPMA_RevF.docx`
  不可访问 (私有 cimi-kb dataset), SUT 沙箱无法重建检索语料 → 不可建案

## 交付物
- `benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-VpsInterfaceSummaryQA-001/`:
  8 A 资产 + prompt.txt + hidden/ (vps_guide_B.txt + hidden_manifest.json)
- `benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-VpsInterfaceSummaryQA-001/`:
  check.py + make_summary_ref.py + negative/negative_selftest.py
- `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl`: 追加 1 行 (395→396)
- ledger `trace_ledger_A.tsv`: tt73q claimed → case
