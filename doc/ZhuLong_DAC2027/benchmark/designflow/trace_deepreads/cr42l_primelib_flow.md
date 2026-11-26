# 深读笔记：cr42l (1793866732639_cr42l) — PrimeLib K 库流程理解

## trace_source
- user: johnl
- host: hfeg0pkn001
- session_file: 1793866732639_cr42l.messages.json
- match_count: 43 (tools col: 532 netlist + 1 synthesis)
- msgs: 93, size: 496KB
- 6 user turns (IDX 0/21/27/45/88/92)

## USER 轮分析（A档选轮）
- **USER#0 (IDX 0)**: `/home/johnl/.cline/scripts/data/primelib/primelib_char_all_comb  帮我看下这里的k库流程是怎样的` → **纯目标"理解 k 库流程"，未给根因/修复 → A档任务说明**
- USER#1 (IDX 21): "在这里面查如何将lib转成.db不准自己写 只能查" → 查询 lib→db 转换方法（follow-up，非A档）
- USER#2 (IDX 27): "在项目里查文件 本地文件夹 我给你的" → 澄清搜索范围（follow-up）
- USER#3 (IDX 45): "我要把这个转成.db 你帮我修改对应文件 修改后differ确认" → **给出修复/修改请求，非A档**
- USER#4 (IDX 88): "输出在哪里" → 问产物位置（follow-up）
- USER#5 (IDX 92): "我要重新产生 给我说执行哪个命令" → 问重跑命令（follow-up）

## assistant gold 分析（IDX 20，对 USER#0 的完整回答）
工程 = **Synopsys PrimeLib 时序/功耗表征（K 库）流程**，给 stdcells_ac 普通布尔组合单元批量生成 Liberty 库，再用 LC 转 DB 库。

### 工程结构
| 路径 | 作用 |
|---|---|
| cells.txt / config/cells.txt | 表征目标清单（唯一 K 目标来源），当前 93 个 LVS 组合单元 |
| config/project.json | 默认 corner 配置 SS_0p98_m40c（model deck 路径、VCC/VBP=0.98V、T=-40°C、slew/load 网格、阈值、SPICE 参数） |
| config/project.SS_0p94_110c.json | 独立 corner 配置 |
| ../netlist.presim | 源 SPICE 网表 |
| scripts/ | 各阶段脚本 |
| work/ | 中间产物 + PREPARE.PASS 门禁 |
| output/ | 最终 .lib / .db |
| logs/ | PrimeLib / LC 日志 |
| reports/ | 端口检查、missing cell 报告 |

### 流程 5 步
- **Step 0 部署**: install_primelib_char_all_comb.sh（自解压安装器，base64 payload + SHA256 校验）
- **Step 1 盘点闭包**: run_prepare.sh → prepare_project.py
  1. 解析 netlist.presim 中 `*Library: stdcells_ac` 标注的 .SUBCKT，数量须 = expected_annotated_cells
  2. 按前缀分 5 类（普通组合/时序/三态/delay_pulse/ambiguous），有 ambiguous 直接失败
  3. 校验普通组合电源端口 = inh_vbn/inh_vbp/inh_vcc/inh_vss，不达标失败 → reports/ordinary_comb_pins.tsv
  4. 递归构建 SPICE 闭包 netlists/stdcells_ac_all_comb_closure.sp
  5. 生成 work/char_config.tcl + work/liberty_header.lib
  6. 全过写哨兵 work/PREPARE.PASS（运行门禁）；失败删旧产物+门禁
- **Step 2 PrimeLib 表征**: bsub_run_all.sh
  1. bsub_run_all.sh: 校验 JSON 合法 + 源网表/model 文件存在 → bsub -I -q fqueue3_analog 提交 LSF
  2. run_compute.sh: source LSF module init → module load tsa/primelib_2023.12-SP5 → run_all.sh
  3. run_all.sh: run_prepare.sh + run_primelib.sh
  4. run_primelib.sh: 检查 5 个 prepare 产物齐全 → 旧 lib 备份 → 设环境变量 → primelib -x source primelib/char_all_comb.tcl
  5. char_all_comb.tcl: create_operating_condition → 硬链接闭包网表 → import -recognize -flatten → configure -timing -power → characterize → model -liberty -create_new_model → output .lib
- **Step 3 严格校验**: validate_lib.py
  - cell 集合与 config/cells.txt 完全一致（不多不少无重复）
  - 不得出现 ff/latch 状态组
  - slew/load 网格与 config 一致
  - 8 个阈值属性（input/output 50%, slew 10/90%）正确
- **Step 4 (可选) LC 转 DB**: run_lc_lib_to_db.sh
  1. patch_lib_for_lc.py 生成 LC 专用副本（补 delay_model、写 physical area、clear_preset X→H）
  2. lc_shell -f scripts/lib_to_db.tcl: read_lib → cell 数校验 → write_lib -format db → output .db

### Corner 切换
PROJECT_CONFIG=config/project.SS_0p94_110c.json ./scripts/bsub_run_all.sh — shell/Tcl 零硬编码，全在 corner JSON 的 model 字段

### 一句话总结
netlist.presim → prepare(盘点分类+闭包+门禁) → LSF PrimeLib(FR 识别+timing/power 网格表征) → validate_lib 严校验 → (可选) LC 转 DB；配置驱动、失败即断、只表征普通布尔组合单元

## 判档
- **A档 faithful**: 任务说明 = USER#0 逐字原文；gold = assistant IDX 20 流程分析
- 交付物机器可验化: **analyze_flow.py** 读 primelib 项目目录，输出结构化 JSON（library_name/corner/cell_list_source/flow_steps[]/gate/tool/validation_checks/corner_mechanism）
- L1-static: 离线 Python 解析脚本文件，无需 EDA 工具
- A assets = 真实 primelib_char_all_comb 项目文件（README/cells.txt/config/scripts/primelib/char_all_comb.tcl）
- 隐藏 B = 结构对立重建的 iolib_io 项目（不同 library/corner/cell/script 名，同 5 步流程模式）

## 真实附件（在盘已确认）
primelib_char_all_comb/: README.md(83L), cells.txt(92L), config/{project.json(38L), cells.txt(93L), cells.yaml(487L)}, primelib/char_all_comb.tcl(86L), scripts/{bsub_run_all.sh(47L), run_all.sh(7L), run_compute.sh(42L), run_prepare.sh(6L), run_primelib.sh(53L), run_lc_lib_to_db.sh(51L), lib_to_db.tcl(43L), prepare_project.py(394L), validate_lib.py(95L), patch_lib_for_lc.py(111L), merge_group_libs.py(413L)}
