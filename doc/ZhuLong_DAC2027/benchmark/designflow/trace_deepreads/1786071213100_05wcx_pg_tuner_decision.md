# 深读笔记 — 1786071213100_05wcx（PG 电阻优化闭环 · 自适应调优决策）

- **trace**: `1786071213100_05wcx.messages.json`（e0014566 @ hfeg0pkn001, mc=245, 151 msgs, 632KB）
- **路径**: `/home/e0014566/.cline/data/sessions/1786071213100_05wcx/1786071213100_05wcx.messages.json`
- **领域**: pg_layout（电源网格电阻优化）→ shard C
- **工具分布**: run_commands 59 · read_files 14 · RAG_MCP_Server__search_apis 4 · SandBox_MCP_Server__run_code 1 · search_codebase 1
- **用户意图轮**: 仅 1 条文本轮 —— `<user_input mode="plan">启动业务场景: 模拟电路优化·二次执行</user_input>`（A 档不可行：意图过简，必须 B 档合成）

## 真实流程（faithful）

```
RsCalc(基准, testpg1) → [ AutoVia → PowerFill → RsCalc ] 循环
终止: 电阻下降 ≥ 30% 或 maxIterations = 3
```

- **workdir**: `/home/e0014566/test_layout_rscalc_flow_8`
- **子 runner**: `virtuoso-rscalc-runner/` / `virtuoso-autovia-runner/` / `virtuoso-powerfill-runner/`
- **cell 演进**: `testpg1`(orig) → `testpg1_via1` → `testpg1_opt1` → `testpg1_via2` → `testpg1_opt2`
- **adaptive_tuner.py 真实 CLI**:
  ```
  /usr/bin/python3 adaptive_tuner.py <workdir> <iter> --target-reduction 0.3 --orig-cell testpg1 --prev-csv <iterN_rpoints.csv>
  ```
  退出码: 0=继续/可执行决策；2=INCONCLUSIVE；1=坏输入。

## iter1 状态（gold）

- ✅ 基准 RsCalc(testpg1): 完成，**RSDB 0 entries**（无检查点）
- ✅ AutoVia iter1: testpg1→testpg1_via1，自动检测 `vdd! vss!`，**插 0 via**（via_tier=0）
- ✅ PowerFill iter1: testpg1→testpg1_opt1，runMode=normal，**建 0 fill cell**（pf_tier=1）
- ✅ RsCalc iter1(testpg1_opt1): 完成，**RSDB 0 entries**
- ✅ adaptive_tuner iter2 决策:
  - **Via 升级**: tier 0→1（添加 `viaV5=t` + `viaRDV=t`，因 iter1 插 0 via）
  - **PowerFill 升级**: tier 1→2（normal 16-core，因未建 fill cell）
  - 建议: 继续执行（exit 0）

## 关键决策规则（合成分类器所复刻）

优先级: ①reduction≥target→STOP_TARGET_REACHED ②iter≥max→STOP_MAX_ITER ③via=0且tier<max→UPGRADE_VIA_TIER ④fill=0且tier<max→UPGRADE_POWERFILL_TIER ⑤rsdb=0且via>0且fill>0→RSDB_EMPTY_RETRY ⑥partial 0<red<target两档有余量→UPGRADE_BOTH ⑦两档用尽→INCONCLUSIVE(exit2)。
**注意**: 真实 tuner 即便 RSDB=0 仍先升 via/pf tier（tier 升级优先于 RSDB 空告警）—— 故 RSDB_EMPTY 在 via/pf 升级之后。

## 环境/坑

- `python3` 在 PATH 指向坏的 Python 3.7；`/usr/bin/python3`(3.6.8) 可用 → 调用 tuner 必须用绝对路径。
- Virtuoso 启动需 `env -u ARGUS_HOME _CXMT_SH_PROJ_WRITE_CHECK=1 OA_UNSUPPORTED_PLAT=... LD_PRELOAD=/usr/lib64/libstdc++...` + `nohup`，`sleep` 轮询日志。
- AutoVia agent 生成脚本 `run_autovia_agent.il`（SKILL），经 SandBox MCP `run_code(lang="skill")` 启动；GDS stream-out 偶有 stale，需 `grep leoXstreamOut / defGdsFile` 排障。
- PowerFill `speedMode` 需为字符串 "16"（`sed -i -E 's/.../16/'` 修复）。

## 合成（B 档 L1-boundary）

- **case**: `EDA-Eval-DesignFlow-PGTierTunerDecision-001`（pg_layout, synthesized, L1-boundary）
- **交付**: 单文件 `pg_tuner_decision.py`（标准库 only），读迭代状态 bundle(JSON)，输出 4 行 VERDICT/ROOT_CAUSE/RECOMMENDED_ACTION/CONFIDENCE，exit 0/2/1。
- **资产 A**: `inputs/bundle_A.json`（iter1 状态: vdd!/vss!, 0 via, 0 fill, rsdb=0 → UPGRADE_VIA_TIER）
- **隐藏 B**: 10 个嵌入 check.py 的 bundle（B1-B10），覆盖 STOP_TARGET_REACHED/STOP_MAX_ITER/UPGRADE_VIA/UPGRADE_PF/RSDB_EMPTY/INCONCLUSIVE/UPGRADE_BOTH/坏输入/30%边界/29%边界，网名/电阻结构均 ≠ A（pvdd/pvss/avdd/dvdd 等）。
- **16 条断言 (a)-(p)**, k=16≥8；自验 ref PASS 16/16，negative_selftest 5 fake 全 FAIL（NEG_RC=0）。
- **test 字段 md5** `f8ad78567820382523dd6a22721ceda3`（17722B），与磁盘 check.py 一致。

## 失败模式（教学点）

- 把「RSDB=0」当成硬阻塞会误判：真实 tuner 仍升级 tier（via/pf 优先）。
- reduction 计算需对负值钳 0、baseline 空视为无法计算（不能除 0）。
- 跨输入守卫：root cause 必须用 bundle 的 `autovia_detected_nets`，不能硬编码 A 的 `vdd!/vss!`。
- 边界: 恰好 30% 属于 STOP_TARGET_REACHED（≥）。
