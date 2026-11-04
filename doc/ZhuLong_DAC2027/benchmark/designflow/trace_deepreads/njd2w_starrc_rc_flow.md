# 深读笔记 — njd2w StarRC RC Extraction Flow（shard A 候选）

- **session**: `1792031425233_njd2w`（simplec @ hfeg0pkn002 / 10.129.2.11，也见 hfeg0plg56）
- **trace 量**: 656 msgs / 2.6MB / agent=lead → **超 §3 阈值（>600msgs 且 >2MB）→ 本轮 DEBT=1 仅深读，下轮必须先交付 case**
- **match_count**: 118 · **domain**: pnr_signoff（StarRC RC 寄生提取 = signoff）· **verb**: starrc-rc-extract-flow
- **KW**: synopsys:1550; netlist:1080; cadence:49; calibre:30; skipper:11; schematic:10; primetime:9; aether:7
- **工具分布**: run_approved_command 116 · editor 93 · read_files 61 · list_allowed_files 34

## 用户真实意图（14 轮需求，A档逐字原文）
- [msg0] `我需要和我一起跑一下starrc RC 的flow，先进行第一步，你需要先分析一下 /home/simplec/to_simplechen_starrc/work/run_gxtr_MULTI_CORNER.csh 这个脚本`
- [msg21] 追问 CCI_data 路径来源（~1034 cell 已备好 query 数据）
- [msg31] 「如果指定另外路径的 cci 要修改对应路径，没指定就用默认」
- [msg33] autorun_gxtr_v0d1.csh 第 20 行 cci 路径也要同步修改
- [msg37] 指定运行路径 work/，cell.list 指定要跑哪些，先跑 10 个
- [msg123] `把 spf 中所有net的rc值提取出来`
- [msg133] 提取 `*|NET <name> <cap>PF` 这类信息（举例 Sandwich_M1_M2_W0P055_S0P2_M3.spf 第 34 行）
- [msg139] `增加指定starrc版本的功能`，换 module（如 ds/star/2022.03-SP3），不指定时报当前版本
- [msg236] `增加修改cell.list功能`（CCI_data 全部 / 随机 20 个）
- [msg332] 默认用 work/cell.list
- [msg340] `根据运行时间年月日小时分钟命名输出路径和done.list`
- [msg372/414] 跑 flow 测试
- [msg378] `旧结果默认保留`
- [msg454] 提出修改 cell.list 时 work/cell.list 同步更新
- [msg513] 工具超时如何解决

## 流架构（agent 最终产物）
核心交付 = `work/setup_and_run.sh`（由 `build_final.py` 生成，bash），功能矩阵：
1. **版本管理**：`--show-version` / `--list-versions` / `--version <module>` → `module swap`，自动 detect `ds/star/*`，报 StarXtract 路径 + version
2. **cell.list 管理**：`--cell-list show|status|all|first [N]|random [N]|filter <pat>|from <file>`；`all`=复制 CCI_data/cell.list，`random`=shuf -n，`first`=head -n；status 报 width/metal layer 分布
3. **清理**：`--clean` 保留旧 rundata（只删 tmp/sub_cmd_*），`--clean-all` 深清
4. **运行**：`--run` 前台 / `--bg` nohup 后台（写 flow_bg_<ts>.log + pidfile）；调 `run_gxtr_MULTI_CORNER.csh`
5. **输出**：`run_gxtr_MULTI_CORNER.csh` 用 `setenv outpath date +%y%m%d%H%M%S` → `rundata/<ts>/<cell>/*.spf` + `<ts>_done.list` + `<ts>_loss.list`
- 上游：`autorun_gxtr_v0d1.csh`（csh）→ `unsetenv LD_LIBRARY_PATH; StarXtract -clean ./CCI_cmd_$i`（每 cell 一个 CCI_cmd 文件）
- 下游：`extract_rc.py`（5707B，解析 SPF：`*|NET <name> <cap>PF` + `*|P` ports + `R<n>_<s>` 电阻 + `Cg<n>_<s>` 地容 + `C<n>_<s>` 耦合容 → total_cap/total_r/r_count/c_couple/c_ground）+ `extract_net_info.py`（2037B，提取 `*|NET` 头 → `net_info_summary.csv` with cell,net,total_cap_pf + per-cell 汇总）
- 还产 `skills/starrc_rc_flow/`（skill.md + run_starrc.sh 166B + README）

## SPF 格式（extract_rc.py 反推）
```
*|NET <netname> <total_cap>PF
*|P (<portname>) ...
R<idx>_<sub> <n1> <n2> <val>      # 电阻
Cg<idx>_<sub> <node> 0 <val>      # 地容
C<idx>_<sub> <n1> <n2> <val>      # 耦合容
.ENDS
```

## .75 可行性（已核实）
- ✅ StarRC 二进制在 PATH：`/apps/synopsys/SRB/starrc_2020.09-SP5-4-20220823/bin`（StarXtract）；module `ds/star/2020.09-SP5-4(default)` / `2022.03-SP3` / `2023.12-SP5` / `2024.09` 等
- ✅ PDK runset 目录 `/apps/imctf/runset/starrc/`：cl028hkn / cl028hkn_0d9v / cl028hkn_lihob / cxmt10G2_LP / cxmt10G3 / cxmt10G3_LP / cxmt10G4 / cxmt10G4_LP / cxmt10G4plus / cxmt10G4plus_DDR / cxmt10G4plus_DT ...（含 TF/LEF/mapping/CCI 模板）
- ⚠️ 用户 work dir 在 .75 与 hfeg0pkn002 均空（资产在 hfeg0plg56 或已清）。**需从 trace 的 editor writes 重建脚本**（已抽 37 文件 final state）+ **下轮在 .75 用 cxmt PDK runset 造最小可跑 StarRC 输入**（1-2 cell toy DEF + CCI_cmd + corner 配置）作为 hidden B
- ⚠️ .75 ↔ 本机无共享挂载；check.py L2 真跑须在 .75（经 eda_flow run_commands），判分器读 StarRC 产物（SPF/done.list/csv）做结构断言

## Case 计划（下轮交付）
- **id**: `EDA-Eval-DesignFlow-StarRCFlow-001`
- **domain**: pnr_signoff · **档**: B 档 synthesized（A 档 faithful 14 轮太散，单轮闭环选「build StarRC multi-corner flow driver with cell.list mgmt + version switch + SPF RC extract」）
- **trace_source**: user=simplec, host=hfeg0pkn002, session_file=1792031425233_njd2w.messages.json, match_count=118, real_task_summary=StarRC multi-corner RC extraction flow automation（版本切换/cell.list 管理/时间戳输出/SPF RC 解析）
- **交付**: `outputs/submit.zip` 含 `setup_and_run.sh`（bash flow driver）+ `run_gxtr_MULTI_CORNER.csh` + `autorun_gxtr_v0d1.csh` + `extract_rc.py` + `extract_net_info.py`
- **assets A**: prompt.txt（自然语言 StarRC flow 需求）+ task_brief.md（交付接口 ≤3 行）+ `feint/`（参考脚本片段：run_gxtr 模板 + CCI_cmd 样例 + 一个 cell 的 DEF/LEF 片段）+ `CCI_data/cell.list`（小规模 ~10 cell 名）
- **hidden B**: 不同 PDK（cxmt10G4_LP vs A 用 cxmt10G3）+ 不同 cell.list（不同 cell 名集/不同数量）+ 不同 corner — **5 维全异**；B 不进 SUT 沙箱
- **check.py ≥8 条件**（L2 真跑 StarXtract on B）：
  - a zip 含 5 个交付脚本
  - b setup_and_run.sh bash -n 语法 OK + 可执行
  - c `--show-version` 输出 StarXtract 路径 + module 名
  - d `--cell-list first 5` 后 work/cell.list 恰好 5 行且来自 B 的 CCI_data/cell.list
  - e `--cell-list random 3` 后恰 3 行且随机性（两次运行顺序不同）
  - f `--run` 在 B 上 exit 0，rundata/<ts>/ 下每个 cell 有 ≥1 个 .spf
  - g `<ts>_done.list` 行数 == cell.list 行数（全部完成）
  - h 时间戳目录名匹配 `%y%m%d%H%M%S` 格式
  - i extract_rc.py on B 的 SPF 产出合法 CSV：列 cell,net,total_cap_pf,total_r_ohm,r_count,c_couple_count,c_ground_count，行数 == B 中 *|NET 总数
  - j extract_net_info.py 产 net_info_summary.csv，per-cell cap 汇总与 SPF 一致
  - k `--clean` 不删旧 rundata/（保留旧结果断言）
  - l `--version <other_module>` 后 show_version 报新 module（版本切换生效）
  - m 跨输入护卫：B 的 cell token 在 A 的 feint 中不出现
  - n 3 随机种子重跑结构一致（cell.list random 不同顺序但 f-i 结论一致）
  - o SPF RC 值在合理量纲（cap pF 1e-3~1e2，R Ω 1e-3~1e6）
  - p 负样本：空壳 setup_and_run.sh（只有 echo）→ f FAIL；print-stub（print 期望串不跑 StarXtract）→ f FAIL（无 .spf 产出击穿）；core-deleted（删 StarXtract 调用）→ f FAIL
  → **k=16 条件 ≥8 ✓**
- **test_rationale**: `16 条断言：① zip 含 5 交付脚本 ② setup_and_run.sh 语法 OK 且可执行 ③ --show-version 报 StarXtract 路径+module ④ --cell-list first 5 恰 5 行且源自 B CCI_data ⑤ --cell-list random 3 恰 3 行且随机 ⑥ --run 在 B exit0 且每 cell 出 ≥1 .spf ⑦ <ts>_done.list 行数==cell.list 行数 ⑧ 时间戳目录名匹配 yymmddHHMMSS ⑨ extract_rc.py 产合法 CSV 且行数==B *|NET 总数 ⑩ extract_net_info.py per-cell cap 汇总与 SPF 一致 ⑪ --clean 保留旧 rundata ⑫ --version 切换后报新 module ⑬ 跨输入护卫 B token 不在 A feint ⑭ 3 种子重跑结构一致 ⑮ SPF RC 量纲合理 ⑯ 三假提交（空壳/print-stub/core-deleted）均 f FAIL`
- **风险**: StarRC 对输入（DEF/LEF/TF/CCI_cmd/layer mapping）挑剔，下轮首要任务是**在 .75 用 cxmt PDK runset 造最小可跑 StarRC B 并确认 StarXtract 真出 SPF**；若造不出可跑 B，则降级为 L1-boundary（SPF 解析静态断言 + 模拟 SPF 产物），但优先 L2 真跑
- ** negatives 计划**: fake_empty→a/b, fake_print_expected→f, fake_core_deleted(删 StarXtract 调用)→f, naive_no_version→c/l, naive_no_timestamp→h, naive_no_extract→i/j（共 ≥5）

## 抽取的 37 文件 final state（已存 .75 workdir extract_files.py 输出，下轮可复用）
run_gxtr_MULTI_CORNER.csh(82B) · autorun_gxtr_v0d1.csh(279B) · extract_rc.py(5707B) · extract_net_info.py(2037B) · check_star_version*.sh · clean_and_run.sh · setup_and_run.sh(由 build_final.py 生成) · build_final.py(9326B) · rebuild_all.py(9220B) · starRC_flow.il(11161B) · skills/starrc_rc_flow/{skill.md,run_starrc.sh,README.md} · cell.list 管理系列

## 结论
njd2w 是本 shard 当前**唯一**有真实设计流意图、可 L2 真跑（StarXtract on .75 ✓）、有完整交付产物的 fresh 候选。超规模 → 本轮 DEBT=1 深读，下轮第一件事：在 .75 造最小可跑 StarRC B → 合成 → 自验 → 追加 A.jsonl → mark case。
