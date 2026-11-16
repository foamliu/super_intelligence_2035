# Deepread: k36er — hspice panel 当前项目查询 (Q&A/咨询)

- session: `1794200811873_k36er` (子目录 `1794200811873_k36er/` 下)
- user: e0041392 · host: hfeg0pkn003 (10.129.2.12) · mc=12 · domain: spice_sim
- scan: ssh_eda_search_20261116_072610 (keywords hspice:60;netlist:4;cmos:4;schematic:2)
- trace: 15 msgs / 44KB · model deepseek-v4-flash · ts 1794200811..833 (≈2026-11-04)
- 形态: Q&A/咨询 → 结构化回答（查 workspace 当前项目 + 关键 panel 设置）

## 用户原话（verbatim, msg[0]）
`<user_input mode="act">检查一下workspace中设置的当前项目是哪一个</user_input>`

## agent 工具链
1. `list_allowed_files(/home/e0041392/Desktop, depth=2)` → _anasim_check.py, alter/(check_size.py), backup_spice/, logs/(simulation_panel.log), runsim/
2. `get_agent_policy_status` → enforcing, profileIds=[python-runner, shell-runner]
3. `list_allowed_files` runsim/(空) / logs/(simulation_panel.log) / backup_spice/(空)
4. `read_files` simulation_panel.log + _anasim_check.py + alter/check_size.py
   - log 关键行: `Configuration saved to: /home/e0041392/Desktop/.hspice_panel_config.json`; `ml av ds/finesim` → finesim 2022.06-SP1(default)/2023.12-1; `Sim folder scanned: /home/e0041392/Desktop (0 SPICE files)`
5. `list_allowed_files(includeHidden=true)` Desktop + /home/e0041392 → 发现 `.hspice_panel_config.json`(Desktop+home) + `.anasim_pro_folders.json`(home)
6. `read_files` 三个 config:
   - `Desktop/.hspice_panel_config.json` 与 `/home/e0041392/.hspice_panel_config.json` 内容相同（hspice 仿真面板配置）
   - `.anasim_pro_folders.json`: `{"folders":[{"path":"/home/e0041392/Desktop","alias":null},{"path":"/home/e0041392","alias":null}],"active":"/home/e0041392"}`

## 关键产物（verbatim）
### `.anasim_pro_folders.json`（决定"当前项目"）
```json
{"folders":[{"path":"/home/e0041392/Desktop","alias":null},{"path":"/home/e0041392","alias":null}],"active":"/home/e0041392"}
```
⇒ **当前项目 = active = `/home/e0041392`**

### `.hspice_panel_config.json` 关键字段
- `global_model_path`: ""
- `default_queue`: "fqueue3"
- `default_cores`: "6"
- `default_output_path`: "1_sim"
- `default_simulator_type`: "finesim"
- `default_module_version`: "finesim 2023"
- `last_scan_path`: ""
- `hspice_versions`: 2017(default)/2019/2020/2021/2023/2023_ver03
- `finesim_versions`: "finesim 2023"=ds/finesim/2023.12-1, "finesim 2022 (default)"=""
- `primesim_versions`: (default)/2023_12/2025
- `simulator_core_limits`: finesim{1..6 def6}, finesim-spice{1..6 def6}, hspice{1..4 def4}, primesim-spice{1..6 def6}
- `pvt_defaults`: mos="tt ff ss sf fs tf ts st ft", res="ss ff", nicap="ss ff", diode="tt", bjt="tt", temp_sweep="-40 130", temp_nom="98", voltage_variation=0.1
- `output_directories`: alter=./alter, backup_spice=./backup_spice, runsim=./runsim, logs=./logs
- `measurement_file_patterns`: *.ma0..ma5, *.mt0..mt5, *.md0..md5
- `waveform_file_extensions`: .tr0/.ac0/.dc0/.sw0/.noise0/.tr1.../.fsdb
- `ui_settings`: window 1950x1000, panel_widths left550/middle700/right550
- `create_spice_defaults.option_file_template`: "/proj/{project}/{version}/setu..." (截断)

### `simulation_panel.log` 关键行
- 2026-10-15 20:11:22 Sim folder scanned: /home/e0041392/Desktop (0 SPICE files)
- ml av ds/finesim → finesim 2022.06-SP1(default) / 2023.12-1
- Configuration saved to: /home/e0041392/Desktop/.hspice_panel_config.json

## 合成决策
- A 档 trace-faithful：A 输入 = 真实三个 config 文件 + scenario（用户原话）+ task_spec
- 形态 = Q&A/咨询 → 产出生成式结构化报告 JSON（`hspice_panel_curproj_report.json`），脚本 `hspice_panel_curproj_report.py(workdir, out_dir)` 解析 config 产报告
- hidden B = 合成不同用户(e0044471)/不同 active 路径/不同 simulator(hspice 2023)/不同 queue(fqueue1)/不同 cores(4)/不同 output_path(2_simout)/不同 folders/不同 PVT → cross-input guard
- check.py ≥8 断言：zip含脚本 + py_compile + SUT在B上subprocess exit0真跑产合法JSON + 顶层键 + current_project==B.active(cross-input) + simulator_type==B(cross-input) + queue==B(cross-input) + cores==B(cross-input int) + output_path==B(cross-input) + workspace_folders==B集合(cross-input) + simulator_version==B(cross-input) + A-leak guard + 确定性3 rerun
- 负样本: 空壳/print-only-A/hardcode-A/deleted-core 全 FAIL
