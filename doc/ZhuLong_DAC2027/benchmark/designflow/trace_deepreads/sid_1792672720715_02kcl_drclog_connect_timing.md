# 深读笔记 — kevinc 1792672720715_02kcl（physical_verify · DRC log 连接耗时分析）

## meta
- session: 1792672720715_02kcl
- user: kevinc / host: hfeg0pkn004 (10.129.2.13)
- mc: 87 · model: glm-5.3-flash · cwd: /home/kevinc
- status: completed · msgs: 121 · user_inputs: 10
- 工具直方图: editor 20 / run_approved_command 19 / list_allowed_files 9 / read_files 4

## T0 (A-档 seed, 逐字原文)
> `/proj/drvsa/V0/ver/drc/kevinc/drvsa_top/WOWTOP_1022_fb_sl`
> 帮我分析一下这个路径下的drc.log，为什么跑的特别慢

纯需求委托轮，无根因/无修复 = **合规 A-档 seed**。

## 后续 user turns（均为 refine / 追问，非 seed）
- U[1] FB_SL_的rule是不是已经跑完了
- U[2] 贴 FB_SL_03_m_c 规则体，问 merge→extent 可以吗（rule-fix hint）
- U[3] 为什么单独跑 FB_SL 很快
- U[4] /proj/drvsa/.../WOWTOP_UT/1022 分析时间耗费 + 优化方向
- U[5/6] 为什么拿掉 FB_SL 后 connect 建立快多了
- U[7] 有什么好的优化方向吗
- U[8] 可以控制先建立连接关系吗，最后再 run FB_SL
- U[9] 贴 nobrknet CONNECT 链，问为什么连接建立慢

## assistant 工具链
- list_allowed_files 探 /home/kevinc + /proj/drvsa + /rundata/drvsa
- run_approved_command (profile=shell-runner) 跑 grep/awk/head 取 drc.log / .drc.summary 片段
- editor 写 analyze_drc_log{,2,3,4}.py 四版迭代解析器
  - **analyze_drc_log3.py** (1256B): 解析 WOWTOP.drc.summary，正则 `RULECHECK <name> ... TOTAL Result Count = N (M)`，按违例数 sort desc，top10 占比
  - **analyze_drc_log4.py** (1884B, 最终 gold): 解析 rundrc.log，提取 `LAYOUT PATH` / `DRC SELECT CHECK` 列表 / `NODE UPDATE:` 层序列 / `CONNECT|DISCONNECT completed. CPU TIME=N REAL TIME=M` / `NETS =` 统计；按 run(k/k1) 逐 log 输出结构化报告

## 用户接受 = 末轮 assistant 给出 prose 根因分析
（nobrknet 阵列 strap 亿级多边形、层级压缩失效、派生层布尔运算破坏规则性、CONNECT 块全量执行不裁剪、FB_SL MERGE 污染、DRC INCREMENTAL CONNECT 优化建议）
会话 status=completed，多轮追问 = 用户接受。

## gold 可用性判定
- **gold = analyze_drc_log4.py（最终版 1884B，自包含 Python3 解析器）**
- 输入：calibre rundrc.log（文本日志）
- 输出：结构化 stdout（LAYOUT PATH / SELECT CHECK 列表 / NODE UPDATE 层 / CONNECT/DISCONNECT CPU+REAL+小时 / NETS 统计）
- **L1**：纯文本正则解析，无需 live calibre，check.py 可 subprocess 真跑候选 on hidden B
- 与 DRCTimeStats-001（yzwang, 每 rule CPU/REAL 排序）**维度不同**：本 case 关注 CONNECT/DISCONNECT 操作级耗时 + SELECT CHECK 裁剪行为 + NODE UPDATE 层序列 + NETS 规模，非 per-rule timing

## 阻塞 / 资产准备
- 真实 log 在用户主机 /proj/drvsa + /rundata/drvsa，**.75 ssh 到 hfeg0pkn004 被拒（permission denied）**，真实 log 不可达
- → 下一轮合成时需按 calibre rundrc.log 真实格式**合成 A/B 日志**（含 LAYOUT PATH / DRC SELECT CHECK 块 / 多条 CONNECT completed CPU/REAL / NODE UPDATE / NETS = 行 / RULECHECK 行），A 模拟 1022_fb_sl 慢场景（CONNECT 3-4.5h），B 结构性不同（不同 SELECT CHECK 列表 / 不同 CONNECT 层链 / 不同耗时排序 / 含 DISCONNECT）
- prompt.txt = T0 逐字原文 + 沙盒注（交付接口 python3 analyze_drc_log.py <rundrc.log>）
- task_brief.md = 交付接口 ≤3 行

## 下一轮第一件事
合成 EDA-Eval-DesignFlow-DRConnTiming-001（physical_verify, A-档 faithful, L1），清 DEBT。
