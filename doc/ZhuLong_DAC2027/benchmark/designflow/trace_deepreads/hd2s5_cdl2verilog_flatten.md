# 深读笔记 — hd2s5 (1793154281875_hd2s5)

- **trace**: `1793154281875_hd2s5` · user `yiminh` · host `hfeg0pkn004` (10.129.2.13) · domain `digital`
- **markers**: `500 netlist  25 innovus  1 schematic` (innovus=25)
- **文件**: `/home/yiminh/.cline/data/sessions/1793154281875_hd2s5/1793154281875_hd2s5.messages.json` (654KB, 199 msgs) + `.messages.archive.json` (1.7MB)
- **来源**: daily eda_trace_2026110*.log (summary.tsv 10/28 快照已 stale，本轮扫 daily log innovus≥10 非 alan3zh 候选)
- **台账**: claim → **deepread**（viable B档但资产非便携，本轮只深读，下轮合成）

## 任务（用户真实意图）
Calibre ICV 晶体管级抽取（420MB CDL/SPICE）→ Verilog 网表转换 + 扁平化。
- **Phase 1**（hierarchical V4 conversion）：用 `cdl2verilog_large.py` 把 CDL 转 hierarchical Verilog，保留 ICV_* 块层级。**COMPLETE & validated**（673MB test_netlist.v，2,236 modules，8.1M leaf inst，vlogan subset 0 err/warn）。
- **Phase 2**（new flatten algorithm，用户 3 条要求）：
  1. **No `\` escapes** — 标识符清洗为 `[A-Za-z0-9_]`（`cpu_pwdata[7]` → `cpu_pwdatacd_7_`，数字 net → `n647050`）
  2. **No ICV** — DFS 从 top 扁平化，只剩 leaf cell 在一个 flat module；wrapper 名作前缀（`X0_X5_X4`）
  3. **No VDD/VSS** — PG pin 连接丢弃；PG-only port/net 不声明
- **验证**：8,103,906 leaf inst == V4 独立计算 ✓；vlogan sample 0 err/warn ✓；FLAT_AUDIT PASS ✓

## 用户轮性质（A/B 档判定）
- 用户#1 = **Context summary 续接纪要**（非"提出需求"轮，是助手/系统写的续接 note）→ **A 档规则②禁用**
- 用户#2-#6 = `continue` / `also for top level netlist, the port direction can be traced by stdcell. If the stdcell pin is SDF*/Q, then the port is output`（#4 是修复/细化方案，非 clean need）
- → **B 档 synthesized**（无 clean A档 need 轮；金标准=Phase2 已验证的 flat netlist）

## 资产可达性
- workspace `/home/yiminh/Desktop/gds2rtl/work/`：e0031982 ssh 10.129.2.13 可读（find/cat 成功，NIS 偶发 timeout 但可重试）
- **资产规模问题**：input 420MB CDL / output 673MB Verilog / 1.05GB flat netlist → **无法打包进 benchmark bundle**（assets/ 需自包含小文件）
- 转换耗时 30-60 min（full vlogan）→ 不适合 SUT 实跑

## 合成路径（下轮 B档）
**必须用合成小网表重建**（非真实 420MB 资产）：
- assets/A: 手写小 hierarchical CDL/Verilog（~50 行：top → 2-3 ICV_* wrapper → 3-4 leaf cell，含 `\`-escape net + VDD/VSS + bus `[7]`）
- hidden/B: 异构小网表（不同 top/leaf/escape 集合）
- 交付=submit.zip{flatten_verilog.py(通用 CDL/Verilog 扁平化器, CLI `<input>[-o]`)+flat_A.v}
- check.py ≥8 条断言：①zip 2 件 ②py_compile ③subprocess 跑 A exit0 ④A 输出无 `\` escape ⑤A 输出无 ICV_* 模块实例 ⑥A 输出无 VDD/VSS net/port ⑦A leaf inst 数 == oracle ⑧A wrapper 名前缀保留(X0_X5_X4) ⑨subprocess 跑 B exit0 ⑩B 输出无 `\`/ICV/VDD-VSS ⑪跨输入守卫 B leaf 数 != A ⑫(可选 L2) vlogan 编译 A 输出 0 err
- **难度**：DFS 扁平化 + 标识符清洗 + PG 剥离 = 真 algorithm 题，非 trivial regex → 符 §5 难度
- **风险**：参考 flatten 实现需正确（DFS inline + 名前缀 + net 重命名），~80-120 行 Python；需独立 oracle 验证 leaf/net 计数

## 关键发现（影响未来轮次）
1. **eda_trace log 路径 BUG**：daily eda_trace_*.log 记录的 session 路径是**扁平**的（`/home/<u>/.cline/data/sessions/<id>.messages.json`），但真实布局是**子目录**（`/home/<u>/.cline/data/sessions/<id>/<id>.messages.json`）。直接 cat 日志里的路径 → "No such file"。**修正方法**：`ssh <ip> 'find /home/<u>/.cline/data/sessions/ -name "*<id>*messages.json" -type f'`。**这是前几轮 fresh session 访问失败的根因之一**。
2. **daily_eda_scan.sh step3 awk 缺数字工具词**（MEMORY 已记）：dc_shell/primetime/formality/vcs/verdi/genus/tempus/icc2 不在 awk 过滤正则 → 纯数字 build session 被丢弃，daily log 只留 innovus/calibre/synthesis/hspice 等。**修法**：给 step3 awk `e` 正则加这些词，重跑日扫。
3. **shard-A fresh 候选模式**：本轮 daily log innovus≥10 非 alan3zh 候选 13 条，深读 7 条全为：①续接纪要(web/cline-watchdog) ②infra 请求(start virtuoso) ③meta 提问(原始对话在哪) ④无可判定交付(study-note 未完成) ⑤非便携巨资产(420MB CDL)。**印证 MEMORY 轮37结论**：shard-A digital/verif/pnr trace 多为知识/咨询/续接型，真实 build 在 analog/shard-B-C。
