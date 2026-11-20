# 深读笔记 · vumhg · e03179 · IO_CABufCore characterization

- session: `1791786108086_vumhg.messages.json`（host hfeg0pkn002 / 10.129.2.11，user e03179，mc=274，319 msgs，1.18MB）
- domain: **characterization**（shard B）
- ledger: claimed 2026-11-11 shard B 轮，session=vumhg，status=seeded（待下轮合成 case）
- trace_source.real_task_summary: e03179 调用 vam-agent 对 IO_CABufCore 单元做时序表征建模，netlist 在 /home/e03179/IO_CABufCoreTT092V25C/netlist，跑 PVT corner 生成 cosim_timing_param/*.dat 并产出审核报告。

## ① 用户原话（A-faithful 候选）
USER#0（唯一自然语言 prompt，逐字）：
> `[vam-agent] 帮我建模 IO_CABufCore，netlist 在/home/e03179/IO_CABufCoreTT092V25C/netlist`

其后 318 条几乎全是 tool_use/tool_result，无更多自然语言指令 ⇒ 单轮闭环任务，prompt 极短、trace-faithful 友好。

## ② 真实工作目录（全部在 /home/e03179/ 下 ⇒ e0031982 可读）
`/home/e03179/IO_CABufCoreTT092V25C/`：
- 顶层文件：`Add_vcap_Pre_log`、`BiasTrimAccuracy`、`check_compile.sh`、`check_env.sh`、`check_logs.sh`、`.run.swp`、`.stimulus.swp`、`run`、`stimulus`、`netlist`（子目录或文件）
- `cosim_timing_param/IO_CABufCore/`：PVT corner .dat 文件——`FF_df0.dat`、`FF_dr0.dat`、`FF_tf0.dat`、`FF_tr0.dat`、（推断还有 TT/SS 各 dr/df/tr/tf 组合，典型 8-corner 表征输出）
- `vam_cosim_utf_psf/`：`logFile`、`timeSweep`（仿真日志 + 时间扫描结果）
- 仿真 run dir：`/rundata/dscqa/V0/simdir/finesim/workdir/e03179/simulation/`（含 cosim_timing_param、D_RdBlkN_D_YioDiffSA_Ysa、dscqa_digital_D_RdBlkN_schematic_ALPS 等多 block 仿真目录）⇒ FineSim 后端

## ③ agent 工具链
1. `list_allowed_files` 探 `/home/e03179/IO_CABufCoreTT092V25C` 顶层
2. `read_files` 读 netlist / stimulus / run 脚本
3. vam-agent skill：建模 → 生成 cosim_timing_param PVT .dat 扫描集
4. 跑 FineSim（/rundata/.../finesim/workdir/e03179/simulation/）
5. 末尾：修 skill add_entry bug（experience 目录未创建）+ 生成「紧凑版审核报告」

## ④ agent 最终产物（供 check.py 参考）
- PVT corner .dat 文件集（cosim_timing_param/IO_CABufCore/*.dat，每 corner 一份 df/dr/tf 测量）
- `vam_cosim_utf_psf/timeSweep`（时间扫描结果）
- 审核报告（紧凑版，#312 生成；#318 修 bug 后重跑）

## ⑤ 下轮合成方案（建议）
- **A 档 trace-faithful**：用 USER#0 逐字作 prompt；attachments A = 真实 netlist + stimulus（从 .75 上 `/home/e03179/IO_CABufCoreTT092V25C/netlist`、`stimulus` 抓取，e0031982 可读 /home）。
- **hidden B**：另一 IO 单元（如同 host 下 e03179 的其它 IO_CABufCore 变体，或手工改 netlist/stimulus 规模与 corner 集）——B 与 A 在 netlist 规模、corner 数、.dat 行数上不同。
- **check.py（≥8 条独立断言）候选条件**：
  1. submit.zip 解包含指定文件集（modeling driver 脚本 + 生成的 .dat / 报告）
  2. 候选脚本在 hidden B netlist 上 `subprocess` 执行 exit 0
  3. 生成的 PVT .dat 文件数 == 期望 corner 数（B 的 corner 数 ≠ A）
  4. 每个 .dat 含表头 + ≥N 行测量数据（tr/tf/dr/df 四类）
  5. timeSweep 含时间列 + 测量列，行数在 B 期望范围内
  6. 审核报告含 corner 表 + 每个 corner 的 tr/tf/dr/df 值
  7. 报告含 PASS/FAIL 判定行（按 spec 阈值）
  8. cross-input guard：候选在 B 上跑出的 worst-corner 名 != A 的 worst-corner（防硬编码 A 答案）
  9. 候选不包含 A 的 netlist 路径硬编码（grep A-specific 路径字符串）
  10. .dat 数值在物理合理范围（tr/tf 在 ps 级，非 0/非 inf）
- **负样本**：empty stub / 只 print A 的报告 / 删 corner 扫描循环 —— 全 FAIL。
- **难度**：L2（真跑 FineSim 候选脚本）或 L1（offline 解析已跑过的 .dat/timeSweep 生成报告）——若 .75 上 FineSim 可调则升 L2。
- **判分口径**：subprocess 跑候选在 B 上生成 .dat/报告，解析结构 + 数值范围，不做文本相似。

## ⑥ 本轮未合成的客观原因
本轮预算（40min）消耗于：(1) mc-matrix 取证；(2) 候选访问性排查——发现远程 /proj/* 不可读、远程 /home/<user>/.cline 需走子目录路径 `<id>/<id>.messages.json`、e0031982 仅能读 /home 下文件；(3) 多个候选被证伪（mx7xh 远程不可读、8b8wk agent read_files 全空=臆造、j93p1/sr426/qrmvt 非 spice 域或无真实 spice 文件内容）；(4) 定位到 vumhg 这一接地气的 characterization trace 时已临近超时。下轮第一件事：抓 vumhg 真实 netlist/stimulus + 合成 case（DEBT:1）。

## ⑦ 访问性备忘（供后续轮复用）
- .75 本机（hfhds201）：`/home/<u>/.cline/data/sessions/<id>/<id>.messages.json` —— e0031982（gid guest + eda_agent）可读 t0002965/dsgao/e0023936 等（组权限或 others-r）。
- 远程 pkn/pnd：session 文件路径同上（子目录！），e0031982 可读 /home/<u>/.cline/（多数用户组含 guest 或 others r-x 进目录），但 **/proj/* / /rundata/* 对 e0031982 不可读**。
- 抓真实附件：只能从 trace 的 tool_result 提取，或从 /home/<u>/ 下的可读项目目录抓（如本例 /home/e03179/IO_CABufCoreTT092V25C/）。
