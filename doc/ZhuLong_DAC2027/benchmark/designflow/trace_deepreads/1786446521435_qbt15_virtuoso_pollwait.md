# Deepread: 1786446521435_qbt15 (e0014566 @ hfeg0pkn001, mc=244, 146 msgs, agent cline lead)

## 真实任务
USER#0 `看下这3个 skill, 在virtuoso运行的过程中，是怎么个等待的机制`
USER#24 (意图轮，逐字) `因为代码执行的时间是不确定的，尤其是一些规模比较大的版图，执行时间会很长很长。所以这种方式不好。希望能够实现：1）启动之后等待跑完，每隔20秒检查一下跑的状态。2）如果跑完了则继续走后面的步骤；3）如果检查到代码还在继续跑，则继续等待；如果检查到程序状态不对，已经出错退出，则分析下出错原因，然后重试。4）重试的次数控制在两次。`
USER#100 `把最大等待时间改为10个小时吧。`
USER#110 `请你结合prompt_flow.md 这个流程说明，对我们这个流程做个详细的说明，出个文档。标题和内容都为英文`

## 上下文
工作目录 `/home/e0014566/test_layout_rscalc_flow_10/`：Virtuoso `-nograph` 批处理电阻优化流
(RsCalc→AutoVia→PowerFill 循环降电源网络寄生电阻)。三个 runner SKILL.md +
prompt_flow.md + common.config/rscalc.config + run_*_config.il + gen_*_agent.py。
旧模式 = 固定 `sleep 180` + 一次性 grep，大版图误判超时/浪费/崩溃不察觉。

## agent 工具链 (146 msgs)
read_files×16 (3 SKILL.md + prompt_flow.md + configs + gen_*_agent.py + run_*.cmd)
editor×28 (写 scripts/poll_wait.sh #29-35；改 3 SKILL.md #49-91；改 prompt_flow.md #63-71；
  写 FLOW_DOCUMENTATION.md #117-129 ~860 行)
run_commands×22 (cat/sed/grep 验证)

## gold 产物 (磁盘真实文件，已 cat 核实)
1. **scripts/poll_wait.sh** —— 自适应轮询等待 helper：
   - CLI: `-l log -s success_marker -p pid_file [-e error_marker] [-m max_wait] [-i interval] [-h]`
   - 默认 `-e '\*Error\*'`、`-m 36000`(10h)、`-i 20`
   - 退出码 0 SUCCESS / 1 FAILED / 2 TIMEOUT / 3 BAD_ARGS
   - is_alive=`kill -0 $(tr -d space < pid_file)`；check_success=`grep -qF`；check_error=`grep -qE`
   - 轮询循环：先查成功(无论死活)→存活则继续等(有错误标记打 WARNING 继续)→首轮宽限→死且无成功→FAILED+print_analysis→达 max_wait→TIMEOUT
   - print_analysis：`========== ERROR ANALYSIS ==========` + Error lines(grep -nE head20) + Last 40 lines + Known-error hints(9 关键字: sysname/CXXABI/ARGUS/cdslck/license-FNP-flexlm/No RTEXT/metalOption/bsub-LSF/strmout-gds-libXp)
2. **prompt_flow.md §5.1** —— 自适应等待节 + PID 捕获(`echo $! > pid`) + 重试策略(3 次尝试，cleanup cdslck)
3. **3 SKILL.md Step 3** —— 每工具集成 poll_wait.sh + 重试(2 retry)
4. **FLOW_DOCUMENTATION.md** —— 英文流程文档

## 关键失败模式 / 教学点
- 旧 `sleep N` 对大版图不可控 → 改"轮询 + 进程存活 + 错误提取 + 超时"
- 成功标记必须**字面**(`grep -qF`，标记可能含正则元字符如 `[` `*`)；错误标记必须**正则**(`grep -qE`，支持 `FAIL|ABORT`)
- PID 存活用 `kill -0` 而非文件存在性；首轮宽限避免进程未起误判
- 重试**不在** poll_wait.sh 内（上层编排负责 3 次尝试 + cdslck 清理），脚本只做"一次等待"+错误分析输出
- 已知错误提示表 = 把现场诊断知识固化进脚本（OA/libstdc++/ARGUS/锁/license/...）

## A/B 档判定
A 档不可行：gold = poll_wait.sh 真实脚本 + 依赖上层 virtuoso 流上下文 + 多文件协同
(prompt_flow/SKILL/FLOW_DOCUMENTATION)，单轮交付件无法在沙盒真跑 Virtuoso 验证。
→ **B 档 synthesized L1-boundary**：seed=USER#24 逐字意图。交付 = 单文件 poll_wait.sh
(bash)，check.py 用 subprocess 在隐藏 B 行为场景(日志/PID)上黑盒验证四要素决策 +
退出码 + 字面/正则匹配语义 + 错误分析输出。无需真跑 Virtuoso。

## 正交性
shard C 首个「Virtuoso 批处理**自适应轮询等待**」子主题。正交于：
- AutoViaLayoutMerge / PowerFillMergeGen / PFMergeDupAudit (via/fill 合并去重，工具内部)
- PlacePersistAudit (aeSaveDesign 落盘持久性，Aether headless)
- DrcWaiveDeckGen (SVRF waive deck 生成)
本 case = "**流编排层面的等待/重试机制**"(orchestration-level wait/retry)，非工具内部算法，
非落盘，非 deck 生成。首次把"固定 sleep → 轮询 + kill -0 + 错误提取 + 超时 + 重试"的
运维型失败模式转成判分核心，覆盖 grep -F vs grep -E 语义差异 + 退出码契约 + 已知错误提示固化。

## 选料注
r128 候选池 mc≥30 shard-C 过滤后 807 条可用。高 mc 多为已落 ledger/纯 Q&A 探索
(t45kv=PR 问答无产物; d810y=waveview/仿真问答 52 轮; 4n3ry=网表分析问答)。
qbt15(e0014566,mc=244,4 真实用户轮,editor×28 写 poll_wait.sh+文档)= 真实产物 +
明确意图轮 + 失败模式(固定 sleep 不可控) + 教学点(grep -F/-E 语义)。当选。
