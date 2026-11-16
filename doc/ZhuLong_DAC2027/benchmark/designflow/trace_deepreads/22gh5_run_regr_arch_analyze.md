# Deepread: 22gh5 — run_regr 框架架构分析 (code-comprehension / analysis-Q&A)

**Trace source**: user `e0039102` / host `hfeg0plg74` (=10.129.2.? ) / session `1793762019450_22gh5` / mc=? (parked_reaudit_A row) / domain `eda_other`
**Trace meta**: 413765 bytes, 40 msgs, 2 user turns, model deepseek-v4-flash, status=failed (exit 1), ran 2026-11-04 03:13 → 11-06 05:58
**Tool calls**: list_allowed_files ×13, read_files ×10 (no run_approved_command, no search_codebase)
**Old parked reason** (r295): "USER#0=告诉我配置思路 run_regr analysis-only Q&A, not produce-task" → **revived per 11-15 令** (analysis-Q&A = 真实用户意图)

---

## 用户原话 (逐字)

**U#0**:
> /proj/drgsa/V0/simdir/verilog/jason17w/regression/verilog.ddr5.drgsa.clean/run_regr
> /rundata/ddgoa/V0/simdir/verilog/jason17w/regression/verilog.lpddr5.ddgoa.0812/run_regr
> 这两个项目里的run_regr文件是vps的ae配的，我想用Agent自动配置，需要先了解架构，你根据项目理解一下配置思路，告诉我配置思路，run_regr里每个文件夹/文件在做什么

**U#35**:
> 把两个项目里通用的框架文件与项目相关文件功能，整理成md格式讲清楚

= **code-comprehension / analysis-Q&A**: 用户要理解 VPS run_regr 回归框架的架构，区分「通用框架文件」vs「项目相关文件」，为 Agent 自动配置做准备。非产脚本，交付 = 结构化分析报告。

## Agent 工具链

1. list_allowed_files 探索两个项目根目录 (drgsa/ddgoa) + bin/ + config/ + run_regr/ (depth 3)
2. read_files 读关键文件: README, run_regr.py (1-570), custom_utils.py (1-290), caselist, regr.env, pattern, run_case.sh, before/after_default_opts, all_on_task_post_cmd.sh, multi_opt_*.sh, single_opt_off_post_cmd.sh, task_post_cmd.sh, run_normal_x16, run_option_probe.py, read_json.py, vsim_uvs_vps (Perl), run_normal_allconfig_noprobe_xrun_jason0905 (Perl), sourceme
3. Agent 未输出最终报告 (status=failed, 2 天后超时)

## 框架架构分析 (从 trace read_files 结果归纳)

### 两个项目
- **drgsa**: `/rundata/drgsa/V0/simdir/verilog/jason17w/regression/verilog.ddr5.drgsa.clean/run_regr` — DDR5 drgsa 项目
- **ddgoa**: `/rundata/ddgoa/V0/simdir/verilog/jason17w/regression/verilog.lpddr5.ddgoa.0812/run_regr` — LPDDR5 ddgoa 项目
- 两者 run_regr/ 目录结构几乎相同 (同套 VPS 框架)

### 通用框架文件 (common, 两项目共享同构)

| 文件 | 作用 | 关键内容 |
|---|---|---|
| `run_regr.py` | 主编排器 (Python) | argparse + toml config; TASK_SCHEMA (task_name/extends/conditions/env/group/weight/timeout/seed/coverage_file/tags/count); get_config_name/get_run_timeout/get_base_pattern/get_mail; add_group/add_grid/add_task; 从 caselist 建 VPS task; ~570 行 |
| `custom_utils.py` | 工具函数 | read_caselist (解析 bsub 行, get_job_submit_options 提取 LSF 选项); create_child_case (parent+sim 子任务, conditions all_success); get_byte_value (读 config/tbconfig tbarchetecture, 默 lpddr4); get_uvs_version (bsub -Is uvs -h); get_define_envs; parse_value |
| `caselist` | 用例列表 | `bsub -n 1 -q vps_rd ./run_regr/run_case.sh > ${VPS_TASK_RUN_DIR}/comp.log test=test1` (每行 1 bsub 任务, test= 指定用例名) |
| `regr.env` | 回归环境配置 | auto_rety=2, retry_percent=100, task_timeout=86400, session_timeout=604800, VPS_PROJECT=uvs_regression, VPS_LOCAL_SESSION_PRE_POST=true |
| `pattern` | pass/fail 模式匹配规则 | `comp_error::fail::20::Error\|ERROR`, `normal_pass::pass::99::PASS`, `irun_comp_pass::pass::9::ncsim> run`, `irun_sim_pass::pass::9::Simulation is complete`, `irun_fatal::fail::3:: *F,`, `pattern_fail::fail::2::Failed Pattern: [1-9].*`, `SUB-PATTERN::sim1::There were 0 error*`, `COMBINE::sim_pass::pass::9::sim1,sim2` (格式: name::pass/fail::weight::regex) |
| `run_case.sh` | 单用例执行器 | `#!/bin/bash; set -x; if [ $(($RANDOM % 10)) -gt 5 ]; then echo ERROR; else echo "PASS"; fi` (stub, 随机 PASS/ERROR) |
| `README` | 运行说明 | `source ${VPS_HOME}/venv/bin/activate; setup_regr; cd ./run_regr; python ./run_regr.py -c ./caselist \| tee ./test.log` |
| `before_default_opts` | 选项探针-前 (全开) | opt1/opt2/opt3/opt4/opt5 (5 行) |
| `after_default_opts` | 选项探针-后 (全关) | opt1_off/opt2_off/opt3_off/opt4_off/opt5_off (5 行) |
| `run_option_probe` | 选项探针入口 | `#!/bin/bash; source $VPS_HOME/venv/bin/activate; python $cwd/run_regr/run_option_probe.py "$@"` |
| `run_option_probe.py` | 选项探针生成器 | read_option_file (跳 # 注释, 去重); dump_opt_file; get_tasks_for_initial_options (all_on task + opt1/opt1-2/opt1-3... 探针任务) |
| `all_on_task_post_cmd.sh` | all_on 任务后处理 | get_session_dir_from_log (grep Log directory/Run ID/Result URL); vpsrequest 查 fail tasks → data.json; python read_json.py → selected_tasks.list; mv 到 opt_file_dir |
| `read_json.py` | JSON 解析 | load_json_from_file; 取 results[0]; 写 selected_tasks.list = data["task_name"] |
| `multi_opt_pre_cmd.sh` | 多选项探针前置 | 读 multi_opt_off_file 行数 <2 则 skip |
| `multi_opt_on_post_cmd.sh` | 多选项后处理 | grep "Total normal tasks:" → custom_field total/pass/fail |
| `single_opt_off_post_cmd.sh` | 单选项关后处理 | pass 时 cat probe_opt_file >> multi_opt_off_file; custom_field total/pass/fail |
| `task_pre_cmd.sh` | 任务前置 hook | `#!/bin/bash` (ddgoa 版空) |
| `task_post_cmd.sh` | 任务后置 hook | `python $dir/extract_memory.py $tool $logpath`; custom_field -p perf_data.txt (ddgoa 版有内存提取) |
| `probe.env` | 探针环境 | (ddgoa 版空) |
| `custom_utils_bak_0903.py` | 工具函数备份 | (备份) |

### 项目相关文件 (project-specific)

| 文件 | 项目 | 作用 |
|---|---|---|
| `run_normal_x16` | ddgoa | x16 normal 回归脚本; getopts t/f/q/d/b/m/c; mkdir ${date}; `./bin/vsim_uvs -b "x16" -f "${frequency}" -q "${queue}" -d "${define}" -l ${date} -sr checkin_0 -o +mi`; define="SHORTSIM USESDFX USETF" |
| `vsim_uvs_vps` | drgsa | Perl vsim 包装器 v1.6 (Leo.Zhao/weki/tomtang); GetOptions proj/arch/createtb/byte/simulation/regnamea/regnameb/logname/define/ncconfig/gseed/netlist/merge; use lib /proj/shdc/cad/script/package; Parallel::ForkManager |
| `run_normal_allconfig_noprobe_xrun_jason0905` | ddgoa | Perl xrun 脚本; `/proj/ddgoa/V0/sim/verilog/lpddr5_tb/bin/vsim -sr auto -d "LPDDR5G USESDF PWRBC FUSA" --noprobe -q bcp_LP1 --ncconfig "+ncnowarn+TRTDECAY ..." -l "log_net0723_xrun"` (多 system sleep 5 并发) |
| `sourceme` | drgsa | `module load univista/2026.06-1` |

### 配置思路 (用户要的)

1. **入口**: `python run_regr.py -c caselist` → 读 caselist (每行 1 bsub 任务) → custom_utils.read_caselist 解析 → 建 VPS task (name/group/submit_options/grid)
2. **task schema**: TASK_SCHEMA 定义 task 字段 (name/extends/conditions/env/group/weight/timeout/seed/count/coverage_file/tags) → toml 配置
3. **环境**: regr.env 设 VPS_PROJECT/timeout/retry; pattern 文件定义 pass/fail 判据 (正则 + 权重)
4. **执行**: run_case.sh 跑单用例 → 输出经 pattern 匹配判 pass/fail
5. **选项探针流**: before_default_opts (全开) → all_on_task_post_cmd (查 fail → selected_tasks.list) → run_option_probe.py 生成 opt1/opt1-2 探针任务 → single_opt_off_post_cmd 收集 pass opt → multi_opt_pre/multi_opt_on 多选项组合
6. **项目定制**: run_normal_x16 (ddgoa) / vsim_uvs_vps (drgsa) 调 vsim_uvs/vsim 跑仿真; sourceme 加载工具

---

## 合成计划 (下轮 r644 合成)

- **case_id**: `EDA-Eval-DesignFlow-RunRegrArchAnalyze-001`
- **档**: C-A (trace-faithful A 档, 用户原话逐字)
- **domain**: eda_other (A shard)
- **task form**: analysis-Q&A / code-comprehension (理解 run_regr 框架架构, 区分通用 vs 项目相关, 整理成 md/JSON 报告)
- **交付**: `run_regr_arch_analysis_report.json` only (zip 内单文件, 结构化 JSON)
- **A 文件** (trace-embedded, asset_fidelity=original, 从 trace read_files tool_results 抽取, 行号剥离还原): 8-10 文件
  - A1=run_regr.py (1-120 主框架 + TASK_SCHEMA 片段)
  - A2=custom_utils.py (1-120 create_child_case/get_byte_value + 139-290 read_caselist/get_job_submit_options)
  - A3=caselist (全文 3 行)
  - A4=regr.env (全文 6 行)
  - A5=pattern (全文 13 行)
  - A6=run_case.sh (全文 8 行)
  - A7=README (全文 6 行)
  - A8=before_default_opts + after_default_opts (合 1 文件, 10 行)
  - A9=all_on_task_post_cmd.sh + multi_opt_pre_cmd.sh + single_opt_off_post_cmd.sh (合 1 文件, 探针流脚本)
  - A10=run_normal_x16 (ddgoa 项目相关, 1-74) + vsim_uvs_vps header (drgsa 项目相关, 1-50) + sourceme
- **B 文件** (variant, anti-hardcode ≥6 维度全异): 换项目名 (ddr6_eksa/lpddr6_ekoa), 换 caselist test 名 (testA/testB), 换 pattern 规则 (不同的 pass/fail 正则 + 权重), 换 regr.env (不同的 timeout/retry/VPS_PROJECT), 换 run_case.sh (不同随机逻辑), 换 run_normal 脚本 (不同 -b/-f/-q/-d/-sr), 换 vsim 工具名, 换 define 串
  - B_SPEC 以 JSON 字符串内联进 check.py, _parse_b 独立解析
- **check() 条件** (~16-18, k_check=k_rationale≥8):
  - structure (a-b): zip 单文件 + JSON 顶层段齐全
  - content-correctness (c-n, ~12): 
    - run_regr.py 作用 = 主编排器 (argparse/toml/TASK_SCHEMA/read_caselist)
    - custom_utils.py 作用 = 工具函数 (read_caselist/create_child_case/get_byte_value)
    - caselist 格式 = bsub 命令行 (bsub -n -q ./run_case.sh test=)
    - regr.env 参数 = auto_rety/retry_percent/task_timeout/session_timeout/VPS_PROJECT
    - pattern 格式 = name::pass/fail::weight::regex (≥3 具体规则识别)
    - run_case.sh = 单用例随机 stub
    - 选项探针流 = before/after_default_opts + run_option_probe.py + all_on_task_post_cmd + multi_opt/single_opt
    - task_post_cmd.sh = 内存提取 + custom_field
    - 通用 vs 项目相关区分 = ≥3 通用文件 + ≥2 项目文件正确分类
    - 两项目 = drgsa DDR5 / ddgoa LPDDR5
    - 配置思路 = 入口→caselist→task→env→pattern→探针 (≥4 步)
    - vsim_uvs_vps = Perl 包装器 (drgsa 项目)
  - evidence-verification (o): ≥5 引真实 A 文件名
  - B judge-self-check (p): _parse_b 解析隐藏 B 变体 → B truth, A-report 关键事实与 B truth 在 ≥6 anti-hardcode 维度全异 (项目名/caselist_test/pattern_rules/regr_env_params/run_case_logic/vsim_define/run_normal_sr)
  - 3-seed (q): _parse_b 顺序无关, b_files shuffle sha256 稳定
  - conclusion (r): confidence + summary
- **A_FILES+B_SPEC**: base64 内联进 check.py (自包含; 规避 write_file 转义腐蚀)
- **负样本** (≥2 + §4.9 三假): empty/no_evidence/wrong_arch/b_overfit/print_only + (a)空壳(b)只print(c)删核心
- **自验**: ref ALL PASS + neg 全 FAIL distinct + §4.9 三假全 FAIL + e2e jsonl PASS
- **ledger**: 22gh5 parked→claimed→case (mark --shard A)
- **parked_reaudit**: 22gh5→DONE_r644

## nfb5r 处置

nfb5r (xmvlog 3 compile error diagnosis, digital) — **本轮深读后发现 error 1 (EXPSMC 1806 blmonitor_if) 根因歧义**: 5 个 monitor class 全在 proj_package (未 import), 但仅 blmonitor_if 报错, 其余 4 个 (errorinject_if/pracmonitor_if/wlmonitor_if/csmonitor_if) 同结构不报错 → "missing import" 假说被矛盾. 无法从 trace 证据确定 error 1 真实根因 (无 ddr6_package 源码, 无法跑 xmvlog 验证). check() 无法建在有牙判分上 → **parked (ambiguous root cause)**, 不造题, 待有 ddr6_package 源码或可跑 xmvlog 时再评估. errors 2&3 (TYPE_BANK_INFO undefined + import ordering) 根因清晰, 但 error 1 歧义致整题不可公平判分.
