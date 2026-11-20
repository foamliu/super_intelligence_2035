# 深读笔记 — djvnv (e0014566@10.129.35.82, mc=79) · layout_virtuoso · flow-driving

**trace_source**: user=e0014566, host=10.129.35.82, session_file=1784165207680_djvnv.messages.json, match_count=79
**keywords**: virtuoso:172; drc:145; .gds:24; calibre:22; dbopencellviewbytype:21; ddgetobj:20; cellview...
**msgs**: 76 (39 user / 37 assistant). 真实 user 轮 = 2 条；其余 37 条 user 为空（工具结果回灌）。

## 用户真实意图（逐字）

- **U#0**: `read the prompt_autovia.md and do the job in it.`
- **U#44**: `read the prompt_powerfill.md and do the job in it.`

用户两次都是「读 prompt 文件 + 执行其中描述的 job」——典型的 **flow-driving**（11-15 令§二 revival：`flow-driving` 复活为合法任务）。
本轮取 **U#0 (AutoVia)** 单元造题；PowerFill (U#44) 留作后续 candidate。

## prompt_autovia.md 原文（用户驱动的 job recipe）

```
Please use the virtuoso-autovia-runner skill to run the AutoVia via generation flow.

Config file path: run_autovia_config.il

Execute the following steps:
1. Read the config file above and verify the parameters are correct (process, libName,
   cellName, pwrnets, via selections, etc.). If any parameters need to be changed, update them first.
2. Use skills/virtuoso-autovia-runner/scripts/gen_autovia_agent.py to generate a self-contained
   agent .il script with the config inlined.
3. Launch Virtuoso in batch mode via run_code (lang="skill") using shell() to run the agent script.
4. Wait 60 seconds, then check the log to confirm successful completion (look for
   "AutoVia completed successfully" and check for "*Error*").
```

## assistant 真实工具链（A#1–A#43）

1. A#1 read_files `/home/e0014566/test_power_analysis_6/prompt_autovia.md`
2. A#3 read_files `run_autovia_config.il` + `scripts/gen_autovia_agent.py`
3. A#5 read_files `assets/run_autovia_nogui.il`（首次路径错 → A#8 search_codebase → A#11 在 assets/ 找到）
4. A#11 read_files `SKILL.md` + `assets/run_autovia_nogui.il`
5. A#17 run_commands `python3.11 gen_autovia_agent.py <config> <nogui> <out>` → 生成 `run_autovia_agent.il`（44 config 参数 inlined）
6. A#19/A#21 read_files 验证生成文件 head/tail
7. A#25 SandBox_MCP_Server__run_code (lang="skill") `shell("nohup virtuoso -nograph -replay run_autovia_agent.il -log ... &")`
8. A#27–A#37 run_commands `sleep 60/30` + `tail -N run.log`（多次 sleep 超时，改轮询）
9. A#39 确认 log 含 `AutoVia completed successfully` + 无 `*Error*`，via cell `layout_austin6_V4V3V2V1CT_vss_VIA` 已创建
10. A#43 给出 step-by-step 总结报告

**gold verdict**: AutoVia flow 完成（via cell 已生成 + log 无 Error）。session exit=0。

## reframe = mock-behavioral `autovia-agent-script-gen`

r645–r734 family 新子型 **autovia-agent-script-gen**（layout_virtuoso / flow-driving / 11-15 令§二 revival）。

**真实行为可计算核心** = `gen_autovia_agent.py` 的纯文本变换（不依赖 Virtuoso 实跑）：
- 输入：config .il（key=value SKILL 语法）+ template .il（nogui 脚本，含 `load("...config.il")` 占位 + 3 行 tail hint）
- 变换：① 解析 config 所有 `var = value` 行 → ② 用 inline 赋值块替换 `load()` 块 → ③ 头部 `;; run_autovia_nogui.il` 替换为 `AUTO-GENERATED` 头 → ④ tail 3 行 hint 替换为 `RunAutoViaNoGui()` auto-start
- 输出：自包含 .il agent 脚本（无 `load()`、参数 inlined、自动启动）

**distinct vs 同 family**:
- vs r734 drc-svrf-setlayer-explain（单 SVRF rule 文件 SETLAYER parser）= 本例 **SKILL config + .il template 双文件 inlining 生成器**
- vs r733 drc-rule-var-prefix-collision（三文件交叉诊断）= 本例 **生成式变换**（产新文件）而非诊断式
- vs r731 launchability-judge（env 判断）= 本例 **代码生成**

## BUILD 计划

- **case_id**: `EDA-Eval-DesignFlow-AutoviaAgentScriptGen-001`
- **asset A**: 真实 `run_autovia_config.il`（cxmt10G4plus/austin/layout_austin6/vss!/viaCT,V1-V4=t）+ 真实 `run_autovia_nogui.il`（709 行模板，含真实 load 块 + tail hint）
- **hidden B**: 不同 config（不同 process/lib/cell/pwrnets/via 选择）+ 同模板 — 反 A 硬编码
- **hidden B2**: 再不同 config — 跨输入 guard
- **prompt.txt**: U#0 逐字 + prompt_autovia.md 原文
- **task_brief.md**: ≤3 行交付接口
- **check.py**: 14 条断言（a–n），跑 B + B2，subprocess 真跑 solve.py，验 inline 块/无 load/auto-start/AUTO-GENERATED 头/deterministic/anti-hardcode
- **negative/**: 空壳 + always-echo + 删核心 三假提交，全 FAIL
