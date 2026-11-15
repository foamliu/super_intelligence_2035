# 深读笔记 — 1788421090460_fzx8i（DDR5 run-regression skill 驱动）

- **trace**: `1788421090460_fzx8i.messages.json`（jason17w @ 10.129.32.190, mc=145, 101 msgs, 183KB）
- **路径**: `/home/jason17w/.cline/data/sessions/1788421090460_fzx8i/1788421090460_fzx8i.messages.json`
- **领域**: digital（DDR5 验证回归 / run-regression skill / LSF bsub 提交）
- **工具分布**: skills×1（load run-regression）· run_commands×多（cat/ls/bsub/bjobs/grep/firefox/sleep）
- **关键词命中**: floorplan:208 · innovus:123 · pyaether:63 · netlist:54 · aether:50（注：keyword 多来自路径名而非真实工具，真实工具是 VPS/LSF bsub）

## 用户意图

- USER#1 (idx 0, mode=act): `/run-regression run run_normal_prac_x16 for uvs` — 用 uvs 工具跑 run_normal_prac_x16 回归
- USER#2 (idx ~40): `continue`

单聚焦 flow-driving/skill 任务：驱动 run-regression skill 提交一条 DDR5 回归到 LSF 并监控。**r567 方法论判据**: 用户问的是单一 capability（run-regression 驱动）→ 类型 (a) 可固化 → **可造**。

## 真实流程（faithful）

```
USER "/run-regression run run_normal_prac_x16 for uvs"
  → agent load run-regression skill (skills tool)
  → cat setup_vps.sh → 取 queue=bcp_LP1, freq=8000, defines="USESDFX POST DISODTMON DISODTCOMP USETF SHORTSIM"
  → ls 验证 config ./run_script_uvs/run_normal_prac_x16 存在
  → 构造 bsub: cd <workdir> && module load univista/vps_202312 && bsub -q bcp_LP1 -o <log> "run_regr --config ./run_script_uvs/run_normal_prac_x16 -q bcp_LP1 -f 8000 -t <tag> -d '<defines>' --tool uvs"
  → bsub 返回 "Job <227197> is submitted to queue <bcp_LP1>"
  → bjobs 227197 → RUN
  → 找到 vps_log dir: run_normal_prac_x16_20260903_153853_8221
  → grep vps.log URL → https://172.16.8.155:8043/regression/task?run_id=...&user=jason17w&config=run_normal_prac_x16
  → bsub firefox 打开 URL (DISPLAY=hfeg0plg54:8100.0)
  → 监控 task_logs: Total 3, Pass 1, Running 1, Queued 1
USER "continue" → 继续监控
```

## 关键参数（setup_vps.sh）

| 参数 | 值 |
|---|---|
| workdir | /rundata/drcoa/V0/simdir/verilog/yesong/verilog.ddr5.drcoa.coa_1220_hj |
| module | univista/vps_202312 |
| queue | bcp_LP1 |
| frequency | 8000 |
| defines | USESDFX POST DISODTMON DISODTCOMP USETF SHORTSIM (6) |
| config (uvs) | ./run_script_uvs/<config> |
| config (xrun) | ./run_script/<config> |

## 合成（B 档 L1）

- **case**: `EDA-Eval-DesignFlow-RunRegrSubmit-001`（digital, synthesized, L1）
- **交付**: `run_regr_driver.py`（CLI `<bundle.json> <output.json>`/`--help`/无参 exit1，读 bundle → JSON 报告）
- **bundle schema**: skill_invocation{config,tool} / setup_vps_sh / bsub_output / vps_log / user / display / regr_tag
- **输出字段**: workdir/module/queue/frequency/defines(list)/config_path/tool/bsub_command/job_id(int)/report_url/run_id/project/task_status{total,queued,running,pass,fail}/firefox_command
- **资产 A** = bundle_A.json（jason17w, coa_1220_hj, bcp_LP1, 8000, 6 defines, uvs, ./run_script_uvs/run_normal_prac_x16, Job 227197, DRCOA(D5-1), task 3/1/1/1/0）
- **隐藏 B** = hidden/bundle_B.json（linwei, coa_1406_lm, bcp_LP2, 4000, 7 defines含LONGSIM, xrun, ./run_script/run_random, Job 318842, DRCOA(D5-2), task 5/0/2/3/0）— 与 A 全异
- **14 条断言** (a-n): ①(a)zip+py_compile ②(b)CLI契约+B运行exit0+JSON ③(c)workdir ④(d)module ⑤(e)queue+freq ⑥(f)defines列表 ⑦(g)config_path工具感知前缀+tool ⑧(h)bsub_command 5 token ⑨(i)job_id ⑩(j)report_url ⑪(k)run_id+project ⑫(l)task_status 5字段 ⑬(m)firefox_command含DISPLAY+url ⑭(n)跨输入守卫B不含A标记
- **自验**: ref selftest 14 PASS + negative_selftest 4/4 全 FAIL (naive→b / print_expected→c / core_deleted→c / hardcoded_A→c) + §4.9 三假提交全 FAIL + 3x sha256 一致 (44db2424...) + jsonl test roundtrip PASS (test field == check.py 11200 bytes). k_rationale=k_check=14>=8 GATE PASS. digital 域+1.
- **候选池重审复活第九条** (r560 ddprg / r561 g7hcn / r562 1yqtd / r563 xd7ut / r564 mt7ua / r565 f1rqc / r566 6kot7 / r568 7qn0b / r569 fzx8i): r556 163 误杀复活候选中, fzx8i 是 skill/flow-driving 类（旧 weak 筛子 REJECT），r567 方法论精化后判类型(a) 单聚焦 capability 可造 → fresh-deepread + B 档合成交付。
