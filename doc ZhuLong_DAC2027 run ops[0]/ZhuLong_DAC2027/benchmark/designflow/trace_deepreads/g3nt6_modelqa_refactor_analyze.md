# deepread: g3nt6 — runModelQA refactor analysis (spice_sim / characterization)

- **session**: `1791449736348_g3nt6.messages.json` · user `rongjiez` @ `hfeg0pkn005` · mc=22 · 20 msgs · 636KB
- **trace path on host**: `/home/rongjiez/.cline/data/sessions/1791449736348_g3nt6/1791449736348_g3nt6.messages.json` (子目录下)
- **files attached in trace**: `/home/rongjiez/jira_dev/mpqa/scripts_t/runModelQA.pl` (137700B/3042 行) + `runModelQA_new.pl` (60390B/1630 行)

## 用户意图（原话）
> @runModelQA.pl @runModelQA_new.pl runModelQA_new.pl是我对原始代码runModelQA.pl进行重构得到的新代码，请你仔细分析这两个文件，给出我的新代码到技术突破与创新，例如新的代码支持primesim hspice nanospice finesim多种仿真器

= 分析两个 Perl 脚本（旧 vs 重构新），结构化总结新代码的技术创新。

## agent 工具链
- read_files 分段读全两文件（旧 3042 行 / 新 1630 行，中段多次截断需补读 97-1002 / 690-927 / 784-845 / 1750-2200 / 1842-2130 / 2300-2560 / 2382-2560 等）
- search_codebase（索引空，0 命中）→ run_commands 被 policy 禁 → 改 read_files 直读
- 最终给出六维创新分析报告

## 关键产物 / 事实（ground truth）
**旧 runModelQA.pl (3042 行)**:
- `my $simulator = "";` · 仿真器分支仅 `finesim` / `primesim`（2 个）
- 版本史 v1.00 Frank 2019 → v2.2.1 Lulu 2022
- 关键 sub: `read_cfg` `get_device_info` `generate_temp_netlist`(模板+正则修补) `generate_idsat/ioff/vth/cgg/idvd/idvg_netlist` `run_simulation` `summary_result`(硬编码测量名) `generate_report`
- testbench 生成 = 模板补丁式（generate_temp_netlist），无 build_testbench_* 家族
- 无 dry-run / CI 模式

**新 runModelQA_new.pl (1630 行, -46%)**:
- `my $simulator = "finesim";` · 4 仿真器 `finesim` `primesim` `hspice` `nanospice`
- `use Excel::Writer::XLSX` `Data::Dumper` `Cwd abs_path` `require cxmt_spiceMeasurementDataConvert.pm`
- 关键 sub: `parse_options` `getSSD` `getShrinkFromModel`(model 零配置自省) `extractDrnPortName` `getPVT` `getDevices` `merge_devparams` `parse_device` `init_run_dir` `runSimulation` `build_testbench_header/setup/instances/stimulus/idcurve_stimulus/measurement/alter`(结构化 testbench builder) `summary_all_results`(按仿真器泛化结果解析: primesim *.md0 / hspice·nanospice *.ms* / finesim *#*.md0)
- `# Dry-run mode for offline testing / CI (no simulator launched).` (line ~828)
- 代码 3042→1630 (-46.42%)

## 六维创新（agent 总结）
1. 多仿真器统一适配层（finesim/primesim/hspice/nanospice，4 层面：testbench 语法 / 激励 / 执行 / 结果解析）
2. testbench 生成范式：build_testbench_* 结构化 builder（vs 旧模板+正则修补）
3. Vth 方法论
4. 模型零配置自省（getShrinkFromModel / getSSD / extractDrnPortName 自动从 model 提取）
5. PVT/器件参数空间扩展（getPVT / merge_devparams / _expand_sweep_dim）
6. 结果解析泛化（summary_all_results 按仿真器文件发现 vs 旧 summary_result 硬编码）
+ dry-run/CI 模式 + 代码量 -46%

## 造题处置
- 形态 = analysis-Q&A → 脚本分析报告（L1 离线 Python 解析两 Perl 文件 → 结构化 JSON）
- A 档 trace-faithful：asset A = 真实两 Perl 文件 verbatim（3042/1630 行，从 host scp 落盘）
- hidden B = 合成同构对（eldo/spectre/ngspice/xyce 4 仿真器，1850/920 行，不同 subs/dry-run），_gen_hidden_B.py 生成 + _gt_B.json 真值
- check.py 17 断言（含 cross-input value guard + A-leak guard + 确定性 + 真跑 subprocess）
- 自验: ref 17/17 PASS + 4 negs(空壳/print-only-A/hardcode-A/deleted-core)全 FAIL
- 旧判 parked "code_analysis"（旧规则判 non-produce-task）→ r618 reaudit 复活为可造（analysis-Q&A 真实用户意图）
- case_id = EDA-Eval-DesignFlow-ModelQaRefactorAnalyze-001
