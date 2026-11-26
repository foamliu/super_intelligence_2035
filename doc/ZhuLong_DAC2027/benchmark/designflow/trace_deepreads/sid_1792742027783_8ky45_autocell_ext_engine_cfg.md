# Deepread: 8ky45 — AutoCell external DRC/LVS engine config (kit TCL variant)

- **trace**: `1792742027783_8ky45` · user `e0047434` @ `hfeg0pnd002` (10.129.x) · mc=211
- **keywords**: `schematic:435;netlist:428;calibre:330;.cdl:176;.gds:169;pdk:157;virtuoso:117;transistor:49`
- **tools** (81 calls): list_allowed_files×21, read_files×18, editor×9, run_approved_command×8, search_codebase×2, get_agent_policy_status
- **size**: 200 msgs / 1.47 MB (OK, under 2MB & 600 msgs)
- **domain**: physical_verify (AutoCell 外部 DRC/LVS 验证引擎配置)
- **shard**: C

## 真实意图（USER 逐字）

- **USER#1-5**：try autocell → pwd → use Chinese → stop running autocell → pwd（orient）
- **USER#6**：读 autocell doc，准备解释后续 log/result
- **USER#7-15**：粘 AutoCell 启动 banner + 报错（sch.cdl vs placement.json vs R.tcl mismatch；H204_R kit 是否用 placement.json；问 layout_gen/ 下该用哪个 kit tcl）
- **USER#16（A-档 seed 候选，提出目标）**：「in the dirctory where R_H204_000.tcl is in, please generate a R_H204_000_explain.tcl, in this file, add comments to explain each line of R_H204_000.tcl」
- **USER#17-22**：问 `${tcl_script_dir}`、design rules（double patterning min space / PRL）、tech.tcl/p51h204l6.tcl/options.tcl 路径、谁提供这 3 文件、`add_rule` 是何命令、customized rule
- **USER#23（关键，A-档 seed 候选，提出目标）**：「在使用autocell的时候，如果要检测lvs和drc，则需要lvs和drc相应的rule deck，我刚刚问客户要，他们回复了路径：`/apps/imctf/cad/runset/lacaa/tv1_dbc/current`、`tv1_dbc_virtuoso/current`、`tv1_fs/current`、`tv1_fs_virtuoso/current`。应该如何理解？这4个路径分别是什么？跟lvs和drc相应的rule deck是什么关系？」
- **USER#24**：客户反馈「fs 和 dbc 分别表示正面和背面供电」（= hint）
- **USER#25-27**：问 GUI 里 DRC/LVS rule file 该填什么、为什么不用 tv1_dbc_virtuoso、tv1_fs_virtuoso 和 tv1_fs 内容是否完全一样（= hint，迭代）
- **USER#28（关键，提出目标）**：「GUI 的 Rule File Settings - Technology 对话框填不进去 `tv1_fs/current/calibre_DRC_FS.rule` / `calibre_LVS_FS.rule`，请查文档告诉我为什么？应该如何解决？」
- **USER#29（A-档 seed，提出目标，未给根因/修复）**：「我选方案B，是指改 R_H204_000.tcl 文件吗？如果是的话，请不要直接改，而是生成一个 R_H204_000_rule.tcl 文件，在这里面加上rule相关的配置」
- **USER#30-32（= hint，迭代细化）**：「R_H204_000_rule.tcl 文件里不要写注释，请修改 / 重新生成」（3 次）
- **USER#33-34**：「what is your problem」/「test」（末尾用户挫败感，assistant 重复生成未达预期）

> A-档 seed 选 **USER#29**（提出"生成 R_H204_000_rule.tcl 加 rule 配置"目标，未给根因/修复）。USER#23-28 给 deck 路径推理 = hint 不进 prompt；USER#30-32 "不要注释" = hint。
> gold = 用户实际接受的结果 = `R_H204_000_rule.tcl`（assistant TC#79 生成 + TC#80-81 自验）。

## assistant 工具链（关键节点）

- TC#3-10：list_allowed_files + read_files 探 autocell 安装树、task 目录、configuration
- TC#12-36：list_allowed_files + read_files 通读 `autocell/doc/tcl_commands/{schematic,device_class,cell,options,utility}` 文档
- TC#39-40：editor + run_approved_command `ac_xcross.py`（sch.cdl vs placement.json vs R.tcl 交叉核对）
- TC#45-56：探 `autocell_n5_release_20260910/autocell_library`（layout_gen / layout_spec / 各 cell），`ac_n5_rows.py`
- TC#57-59：editor 生成 `R_H204_000_explain.tcl`（逐行注释版，USER#16 交付）
- TC#62-67：`ac_rules_probe.py` / `ac_paths_probe.py`（design rules / 3 文件路径）
- TC#68-71：list_allowed_files 4 个 runset 路径（tv1_dbc / tv1_dbc_virtuoso / tv1_fs / tv1_fs_virtuoso）
- TC#74-75：`ac_fs_compare.py`（tv1_fs vs tv1_fs_virtuoso 内容对比）
- TC#77-78：`ac_guirule_probe.py`（GUI Rule File Settings 探查 → 确认 GUI 拒 .rule 扩展名，文档认可 TCL `set_external_engine` 入口）
- TC#79：editor 生成 `R_H204_000_rule.tcl`（USER#29 交付）
- TC#80-81：`ac_rule_verify.py`（剥离注释后比对新文件与原 kit 代码序列：原代码零改动 + 仅插入 set_external_engine 段）

## 关键发现 / 知识

### set_external_engine 命令（doc: tcl_commands/utility/set_external_engine.md）
- Syntax: `tech <name> set_external_engine [options]`
- Scope: tech（挂在 technology/library 上，run_drc/run_lvs 默认用之）
- Options: `-bin {binary_path}`（共享；`-drc_bin`/`-lvs_bin` 可分覆盖，默认 `calibre`）、`-drc_deck {file}`、`-lvs_deck {file}`、`-drc_engine`/`-lvs_engine`、`-drc_runner`/`-lvs_runner`（默认 `${autocell_root}/linux/${arch}/bin/calibre_drc.sh`）、`-no_wait`、`-timeout {sec}`（默认 60）、`-retain_temp_files`、`-set_env {k=v;...}`
- 引擎二进制默认 `calibre`

### runset 路径约定（tv1 = ALS PDK，lacaa 工艺）
- `tv1_fs` = 正面供电（front-side）→ `calibre_DRC_FS.rule` / `calibre_LVS_FS.rule` / `argus_LVS_FS.rule`
- `tv1_dbc` = 背面供电（back-side）→ `calibre_DRC_DBC.rule` / `calibre_LVS_DBC.rule` / `argus_LVS_DBC.rule`
- `tv1_fs_virtuoso` / `tv1_dbc_virtuoso` = Virtuoso OA flow 变体（.rule 内容与 non-virtuoso 同，但面向 Virtuoso 集成）
- **AutoCell GDS flow**（`write_layout -type gds`）→ 选 **non-virtuoso** 变体；用户正面供电 → `tv1_fs/current/calibre_DRC_FS.rule` + `calibre_LVS_FS.rule`

### GUI .rule 扩展名问题
- GUI "Rule File Settings - Technology" 对话框拒绝 `.rule` 扩展名（文档示例全为 `.drc`/`.lvs`）；文档认可正式入口 = TCL `set_external_engine`
- 解决方案 B（用户选）：不动原 kit `R_H204_000.tcl`，生成 kit 变体 `R_H204_000_rule.tcl`，在 tech 创建后插入 `set_external_engine` 配置段

### gold = R_H204_000_rule.tcl（assistant 实际产物）
原 `R_H204_000.tcl`（30 行 kit TCL）：
```
# AutoCell Layout Generator TCL, Version 1.26.7.56db6cb
source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl
option router 1
option router_method 2
option router_solver_optimize_mode 0
option lvs_check 1
option lvs_dont_compare_bulk 1
set_constraint PVS 0
set_constraint PVBS 0
set_constraint FPVB 0
set_constraint TTS 1
set_constraint VVA 1
schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}
cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin
cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device
cell ${cell_name} generate_layout
write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
```
生成的 `R_H204_000_rule.tcl`（删头注释 + 在 `source prepr.tcl` 后插入 5 行 set_external_engine 段）：
```
source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl
tech default_tech set_external_engine \
    -bin calibre \
    -drc_deck /apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_DRC_FS.rule \
    -lvs_deck /apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_LVS_FS.rule \
    -timeout 600
option router 1
... (原代码 verbatim)
```
- 删原头注释 `# AutoCell Layout Generator TCL...`
- 原非注释代码行 verbatim 全保留（零改动）
- 插入段恰 5 行（`tech ... set_external_engine \` + 4 个续行），位于 `source prepr.tcl` 之后、`option router 1` 之前
- `-bin calibre`、`-drc_deck tv1_fs/current/calibre_DRC_FS.rule`、`-lvs_deck tv1_fs/current/calibre_LVS_FS.rule`、`-timeout 600`
- tech 名 = `default_tech`

## 合成决策

- gold 依赖 live AutoCell + live PDK runset（`/apps/imctf/cad/runset/lacaa/` 内网）+ live autocell doc → .75 沙盒可达（文件实存），但 SUT 沙盒**不应**直接读 live runset（隔离）；且 gold 是确定性 TCL 文本变换 → **A-档 disqualified（tooling/data 依赖 + 答案是静态文件）** → **B-档 synthesized L1-boundary**（离线 manifest → kit 变体生成器）
- 交付物改为**生成器脚本** `gen_rule_kit.py`：读 manifest JSON + kit TCL → 产 `<kit_base>_rule.tcl`（manifest 指定 power_side/fs|dbc + flow/gds|oa + tech + timeout + runset_root + 插入锚点 + no-comments + preserve-original）
- check.py 在 hidden B（3 变体：dbc/gds、fs/oa-virtuoso、dbc/oa-virtuoso）上跑生成器，逐条断言（≥8）+ `tclsh` info complete 真跑候选
- 与 AutoCellKitMap-001（.cdl→kit 映射）、AutoCellFlowValidate-001（flow 文件/源序校验）、AutoCellClassify-001（cell 分类）**正交**——本案是外部 DRC/LVS 引擎 deck 配置 + kit 变体生成

## check.py 14 条断言（a–n）
- a) submit.zip 含 gen_rule_kit.py，py_compile 通过
- b) 在 B 上跑生成器 exit 0 且产出文件名 = `<kit_base>_rule.tcl`
- c) 输出 rule.tcl 无注释行（stripped 不以 `#` 开头）
- d) 原 kit 非注释代码行 verbatim 全保留（无 missing）
- e) 输出含 `set_external_engine` 调用
- f) `set_external_engine` 含 `-bin calibre`（manifest bin）
- g) `-drc_deck` 路径 = manifest 期望（power_side + flow 变体 + `calibre_DRC_<SIDE>.rule`）
- h) `-lvs_deck` 路径 = manifest 期望（`calibre_LVS_<SIDE>.rule`）
- i) set_external_engine 段插在 `source .../prepr.tcl` 之后
- j) **真跑候选**：subprocess `tclsh` `info complete` 校验 TCL 语法合法
- k) set_external_engine 目标 tech 名 = manifest tech_name（default_tech）
- l) deck 路径变体正确（flow=gds → 无 `_virtuoso`；flow=oa → 含 `_virtuoso`）
- m) 含 `-timeout` 且值 = manifest timeout（600）
- n) 原 kit 头注释行（`# AutoCell...`）不在输出中
