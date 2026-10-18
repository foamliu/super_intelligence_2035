# 排队计划：read-back 轴成本重测（N' + B）

> 状态：**QUEUED（2026-10-18）** · 不打断当前 `ZL.glm-5.2` r1
> 关联审计：`run/PAPER_RETEST_AUDIT.md`
> 目标：① 补 `(N')` 5-run 的 Pass@1 + 成本；② 把 `(B)` 成本从 n=1 升到 5-run；③ 检验「成本是否随观测变窄单调上升」还是「无反馈反而少搜索」。

---

## 0. 前置与排队

1. 当前 P0（`ZL.glm-5.2` r1，09:38 启动）完成、`pgrep -af 'bash scripts/run_zhulong_script'` 无输出；
2. GPU 空闲（8 卡可用）；
3. 不重启/不打断其他 eval；不改 `cline 3.0.51`；不删任何 trace；
4. 主基座固定 **`deepseek-v4-pro-fp4`**（与论文主表一致）。若网关不可用，**报 blocker，不擅自换模型**。

---

## 1. 配置（与 (B)/(F) fresh 完全一致，只改回读档）

```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
export EDA_OMEGA_FIDELITY=high
export EDA_RUNCODE_READBACK=none      # (N') 唯一变量
export EDA_PHI_BUDGET=0
export EDA_PHI_LAGGED=0
# V3 文档 + 自探索 ON + full harness 保持与 B/F fresh 相同
python scripts/set_s1_fidelity.py readback_none   # 或按现有脚本等价切换
bash stop.sh && bash start.sh                     # MCP 重启，核对 /proc/<pid>/environ
```

启动前核验：`.env` 与 `/proc/<MCP_PID>/environ` 均为 `READBACK=none / OMEGA=high / BUDGET=0 / LAGGED=0`；4 端口 `8650/8651/8652/8654@10.129.32.75` OPEN；反作弊 hook `ACCESS RESTRICTED` 可命中。

---

## 2. 运行矩阵

| 轮次 | 命令 | batch | 备注 |
|:--:|:--|:--|:--|
| r1 | `setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_readback_none_retest_r1.log 2>&1 < /dev/null &` | 记录 | 158 题，2500s/题 |
| r2–r5 | 同 r1，改日志名 | 记录 | 串行，逐轮打分 |

每轮结束先 `ps -p <PID>` 判 GONE，再按现有模板 regrade（4 端口 + RAG:9006 + `SANDBOX_HOST=10.129.32.75` + `export PYTHON=$PWD/venv/bin/python`），记录 `pass (xx.x%)`、timeout、gen-fail、exec_err。

**判据（沿用十三）**：timeout ≤10、0 infra、0 exec_err；Pass@1 任何值有效，不因低分重跑。

---

## 3. Trace 保留（本次重测的核心）

> 上次 `(N')` 成本丢失就是因为 trace 被清理。本计划把「保留 trace」作为硬前置。

每轮结束、清理前：

```bash
OUT=/nasdata/app.e0031982/code/EDA-Eval-Framework/output_evaluation
DEST=/nasdata/app.e0031982/code/ZhuLong_DAC2027/trace_retest/readback_none/<batch>
mkdir -p "$DEST"
# 复制该 batch 的 cline session / trace / generated code 元数据（不要只复制 reward）
cp -a "$OUT/<batch>" "$DEST"/ 2>/dev/null || true
# 若 trace 在 ~/.cline/data，按 session 目录一并复制
```

验收：每轮 trace 文件数 ≥158（或与 158 题一一对应）；`du -sh` 记录；**不删除、不 `git add`**（trace 体积大，留在 NAS）。

---

## 4. 指标与预注册分析

**每轮必报**：
- Pass@1（通过数/158）
- mean `run_code` calls / trace（逐 trace 计数）
- code-generation wall-clock（Step3 开始 → Step6 完成；不是总 batch 时长）
- timeout 数（命中 2500s 的题数）
- Converged（finish reason=completed 的比例）
- Mean gen-fail（未产出可执行代码的题数）

**预注册**：
1. 报告 5-run `mean ± sample std`，不只报单轮；
2. `(N')` vs `(B)` vs `(F)` 的成本对比**不做单调性假设**；先看数据，再决定措辞；
3. 若 `(N')` 成本低于 `(B)/(F)`，如实报告「无反馈 → 少搜索/早提交 → 成本低但准确率最低」，并把 Principle 2 的成本表述限定为 `(B)→(F)` 区间；
4. 统计检验：McNemar（paired per-task pass/fail）+ paired bootstrap 95% CI，与 `(F)` 和 `(B)` 各做一次；
5. 禁止插补、禁止用 legacy 数字替代、禁止把单轮说成 5-run。

---

## 5. `(B)` 成本 5-run（优先零 GPU）

先查 2026-10-15 的五个 fresh batch 是否仍有 trace：
- r1 `2026_1015_093317`、r2 `2026_1015_143848`、r3 `2026_1015_193004`、r4/r5 从 `/tmp/ABL_readback_binary_r{4,5}.log` 的 batch 行恢复。

若 `output_evaluation/2026_1015_*` 或 `~/.cline/data` 仍有逐 trace 记录：直接解析 5 轮，产出 `mean±std`（零 GPU）。  
若 trace 已丢失：按 §2 同法补 `(B)` 5-run（`READBACK=binary`），预计 ≈7.5h GPU。  
**注意**：现表 `(B)` 的 13 是 r1 的 timeout，5-run 均值可能不同；不要沿用 13。

---

## 6. 交付物

1. `zhulong_results.md`：S1.readback_none 节补 5-run 明细 + 成本列；S1.readback_binary 节补 5-run 成本。
2. `6_exp.tex`：`tab:readback-cost` 填 `(N')` 三列；`tab:ablation-harness` 的 Mean read-backs 更新；如实证非单调，改写成本段措辞。
3. `PAPER_RETEST_AUDIT.md`：把 #9/#14/#15 状态改为 DONE，并记录新数字。
4. commit：`zhulong retest: readback none 5-run + cost (n=5)`；论文改动 `zhulong paper: fill readback cost table from 5-run retest`。
5. 重编译 `main.pdf`（36.15 上 `latexmk -pdf main.tex`）。

---

## 7. 红线

- 🚫 不打断 `ZL.glm-5.2` r1；🚫 不改 `cline 3.0.51`；🚫 不换主基座；
- 🚫 不删 trace、不清 `/tmp` 里的本轮日志，直到 5-run 解析完成；
- 🚫 不把 `(N')` 成本插补成「最高」；🚫 不用 legacy 数字冒充 5-run；
- 🚫 不因 `(N')` 成本低于 `(B)` 就隐藏或重跑——这是有价值的负结果。
