# Deepread seed — o9nm6 (zhililu, hfeg0plg49 / 10.129.8.86)

> 本轮 r1112 定位为 live D-relevant trace 候选，下轮 (ETA r1113) 深读 + 合成 case。
> 来源：r1112 deeper-scan 发现 summary.tsv stale（scan 候选 trace 多已被 cline 清理），
> 改为直接列 host live sessions dir（passive read-only，非 698 机主动扫描），
> 在 plg49/zhililu 发现 17 个 live session，取首个 o9nm6 peek 确认 D-relevant。

## 检索事实（可复现）
- host: hfeg0plg49 = 10.129.8.86（.75 以 e0031982 身份免密可达）
- user: zhililu
- session_file: 1793841644587_o9nm6.messages.json
- 路径: /home/zhililu/.cline/data/sessions/1793841644587_o9nm6/1793841644587_o9nm6.messages.json
- size: 437995 B, n_msgs: 28
- 检索命令（.75 上，eda_flow run_commands）:
  ```
  ssh -o BatchMode=yes -o ConnectTimeout=8 e0031982@10.129.8.86 'cat /home/zhililu/.cline/data/sessions/1793841644587_o9nm6/1793841644587_o9nm6.messages.json' </dev/null > ./o9nm6.messages.json
  ```

## peek 摘要（前 6 条 user-text）
- msg#0: pluginName=agent-policy-engine，policy enforcing，profileIds=[python-runner, shell-runner]，auditRequired=true（policy-gated 环境）
- msg#1: list_allowed_files → uploads/TS_core（用户上传文件 TS_core）
- msg#2: list_allowed_files /home/zhililu → 含 BitAnswer/, CDS.log, cross_probe_l2s_query_results/, cross_probe_s2l_query_results/（Cadence schematic↔layout cross-probe 工作目录）
- msg#3: run_commands disabled → 须用 run_approved_command + configured profile（policy 限制 shell）
- msg#4: read_file agent-policy.json → allowedTools=[apply_patch, ask_question, editor, read_file(s), run_approved_command, search_codebase, skills, RAG_MCP_Server__search_apis/get_api_details, SandBox_MCP_Server__run_code]；allowedScriptRoots=[/home/zhililu, /apps/imctf/cad/ai/agent/system_config/profiles]
- msg#5: read_file uploads/TS_core → **SPICE netlist**：
  ```
  ** Library name: lacaa_custom_logic_cell
  ** Cell name: INV_2X_SVT
  ** View name: schematic
  .subckt INV_2X_SVT I_INV O_INV VDD VSS
  XNM0_DUMMY VSS VSS VSS nsvt_dbc w=119e-9 l=6e-9 nfin=2 wgaa=35e-9 nf=1 mr=1 ...
  ```
  （nsvt_dbc 子电路实例化，finFET 参数 w/l/nfin/wgaa/nf/mr/nfp/nfm + 边界参数 sa/sb/plel/pler/wpex/wpey/osex/osey/dmby/gteu/peul/pedl 等）

## 初判
- domain: **schematic_netlist**（D shard 本域）—— 用户上传 SPICE 网表 + 在 Cadence schematic↔layout cross-probe 工作目录上下文
- n_msgs=28 小型会话，深读成本低
- 真实意图待中段补读（msg#6-27）：疑似 netlist 解析 / cross-probe 查询 / 单元参数审计类任务
- 下轮 r1113：scp 全 trace → 深读 msg#6-27 → reframe 为可 checkable 交付（参考 r1099 manual-grounded routing-map / r1108 netlist-extraction 接口化范式，L1 脚本交付）→ 合成 case

## 下轮 ETA
r1113: 深读 o9nm6 + 合成 1 条 case（schematic_netlist, L1, k≥8, 3 neg, §4.9 三假 FAIL, hidden B + A-prime anti-hardcode）
