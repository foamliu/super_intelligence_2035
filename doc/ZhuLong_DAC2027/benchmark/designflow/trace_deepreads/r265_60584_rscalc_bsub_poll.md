# r265 deep-read — 1786016997085_60584 (e0014566@hfeg0pkn001, mc=234)

- session: 1786016997085_60584.messages.json (10.129.2.10, nested path /home/e0014566/.cline/data/sessions/<sid>/<sid>.messages.json), 82 msgs (49 user / 33 assistant), 2 real user turns, agent=lead.
- keywords (raw.tsv): waveview:1041; pyaether:962; virtuoso:277; aether:199; analog:48; synopsys:21; schematic:7; mixed-signal:3.  tool calls: run_commands 24, SandBox_MCP_Server__run_code 8 (SKILL), read_files 8, editor 4, search_codebase 3.
- 真实任务: 在 /home/e0014566/test_layout_rscalc_flow_7 中排查 rscalc baseline(testpg1) 计算失败。

## User intent (real turns)
- U1 (msg[0], 提出需求未给根因): 「为什么 rscalc 计算失败了，排查下原因」。
- U2 (msg[23], 给修复方案): 「要的，帮我改为非交互提交+轮询。以及修复了layout的问题。」(A档不可用——已给修复方案；U1 可作 A档 seed)。

## Agent 排查结论 (两个独立失败点)
- A. LSF `rscalc` 队列爆满(384/384 RUN, 288 PEND)。`run_rscalc_agent.il` 第472行 `shell(strcat("cd " runDir "; bsub -I -n " parallel " -q rscalc ./runrsc -config rsc.config > rscalc.log 2>&1; sleep 10"))` 用 `bsub -I`(交互模式) 提交，作业 552940 在 PEND 停留 443s 后被属主杀掉(`bjobs -l`: EXIT, TERM_OWNER: job killed by owner, RUN=0 从未真正运行)，零结果。
- B. layout `vdd` 网络短路。`lvnt_dbtext`: vss 2 标签(y=-2.0), vdd 3 标签(y=2.0×2 on M1, y=6.0 on M5); `lvnt.log` Short node=1; `rsb.log` 报 vdd 短路; `addPoints.txt` 全是 vdd 大量在 y=-4.0。SKILL sandbox 打开 cellview(162 shapes, rect+label 无 instance): M1-M5 各有一条 0.3um 窄金属条从 y=-4.5 向上(M1 x=5.0 y=-4.5→0.5 与 vss M1 底轨 y=-3.5~-0.5 重叠; M5 x=13.0 y=-4.5→4.5 与 vdd M5 顶轨 y=4.5~7.5 边界相接)。20 个 RNODE "vdd" 检查点被放在 y=-4.0(x=5,13,21,29 × M1-M5) 正好落在连接 vss 的金属条上 → rsbuild 加虚拟 vdd 节点时落在 vss 金属 → vdd/vss 短路。

## Agent 修复
- bsub 改非交互+轮询: 编辑 `virtuoso-rscalc-runner/assets/run_rscalc_nogui.il`(line 472 bsub -I → bsub 无 -I + bjobs 轮询 DONE/EXIT + pollCount/maxPoll 超时), `env -u LD_PRELOAD /usr/bin/python3 gen_rscalc_agent.py` 重新生成 `run_rscalc_agent.il`(line 369 新变量, line 477+ 轮询逻辑, 无 bsub -I)。
- layout 修复: SKILL 删 20 个 RNODE@y=-4 标签, shape 162→142 验证通过。
- 端到端: 清旧 run dir, `nohup virtuoso -nograph -replay ...` 后台启动 rscalc_fix_test, 等 120s 查日志确认 GDS 重流(含 layout 修复)+ 非交互 bsub 正常。

## B 档重定义 (为何离线)
真实 LSF 队列 / Virtuoso / OA / /rundata / /proj 不可在沙盒复现。可离线化的核心 = 「bsub -I → 非交互 bsub + bjobs 轮询(DONE/EXIT/timeout) + 状态写出」这一 LSF 作业编排逻辑。重定义为 stdlib python `rscalc_bsub_poll_runner.py` 读 config json, 判分用 stub `bsub`/`bjobs`(控制状态序列)真跑候选(L2)。

## DISTINCT from 现有 layout_virtuoso/physical_verify 系
r264 ScmosCrossProbeCsvGen(OA 实例图 cross-probe CSV)/r252 LayStructExtract(layout 结构)/r255 CmMaOpTableGen(物理验证表)/r259 DrcConnectGraphGen(DRC 图)/r262 SacapSpfCouplingExtract(SPF 耦合)——本案首次 ground on "rscalc RC 提取流 LSF 交互作业被杀 → 非交互 bsub + bjobs 轮询状态机重写", 沙盒真跑候选的 subprocess 编排。

## 本 case
EDA-Eval-DesignFlow-RscalcBsubPollRunner-001 (layout_virtuoso, B-synthesized, L2, k=16 a-p)
