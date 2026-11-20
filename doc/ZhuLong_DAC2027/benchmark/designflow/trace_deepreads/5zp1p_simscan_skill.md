# trace deepread — 1794917878991_5zp1p (hairuizh@hfeg0pkn001, mc19)

**src**: `.75` ssh → 10.129.2.10 `/home/hairuizh/.cline/data/sessions/1794917878991_5zp1p/1794917878991_5zp1p.messages.json` (947454B active, 260 msgs) + `.messages.archive.json` (1538255B). NMSGS=260.
**kw**: hspice:22;waveview:18;netlist:14;aether:7;pyaether:2;rtl:1 → spice-dominant ratio 0.34 (B-kw filtered).
**tool counts**: editor:56, run_approved_command:36, read_files:17, list_allowed_files:5, skills:3, ask_question:4, edit:1.
**domain**: spice_sim (HSPICE param-scan optimization of DDR2 lvlshft). shard B.

## 用户真实意图（trace-faithful，按 msg 顺序）

用户 hairuizh 在做 DDR2 level-shifter (lvlshft) 的 HSPICE 参数扫描寻优。trace 三段：

### 段1 (msg 1) — Context summary（前置优化的状态总结）
已完成的 myxn 参数（intinvixn/fbpathxn/intinvoxn/nkratio/fbnpratio）对 4 个 lvlshft config (sel_vbias × sel_pm2) 优化，目标 F = sqrt(|iddq_vintcore|·|iddq_vwlp|)·max(tpr,tpf)·area，硬约束 l2_max,r2_max ≤ 0.9625，精度 0.1。两次 revision 完成。

### 段2 (msg 1→199) — **核心意图：创建可复用 skill `simscan_optimal_param`**
- msg1 user: 「将上述过程和脚本打包成为一个可以复用的skill，以加速agent对以后的通过参数扫描仿真，确认最优参数组合的任务；skill名称为simscan_optimal_param; 用户需要提供原始仿真网表，给出网表中需要扫描哪些参数，以及目标」
- agent 调 skill-creator → 在 `/home/hairuizh/.cline/skills/simscan_optimal_param/` 建 SKILL.md + references/methodology.md + scripts/simscan_core.py + scripts/build_summary_csv.py
- 用户迭代精化 skill（4 轮追加要求）：
  - msg25: 「刚创建的skill中是否会引导用户提供所需要扫描的参量的范围，若无，添加进去」→ 加参数范围引导
  - msg33: 「添加一步，在用户提供完所有所需信息后，应立即...执行第一轮少量仿真后停下，让用户查看方案、结果以及日志是否符合预期」→ 加冒烟必停点
  - msg113: 「汇总文件中应包括所有measure值，并且我遗漏了硬性要求，你应该提醒我；把这两个新的要求整合到所用的skill中」→ 汇总含全量 measure + skill 主动提醒硬性约束
  - msg145: 「加上硬性约束：所有corner下，tr_out和tf_out不大于80p，tpr_in_out和tpf_in_out不大于205p；另外在skill中加上保留每一轮最优的仿真波形，和测量结果源文件，分别放置到结果文件夹的子文件夹waves, 和mearsures中」→ 加硬约束 + waves/measures 归档

### 段3 (msg 45→113) — 应用 skill 到 vdleq 扫描（A 档 spec 来源）
- msg45: 「扫描 .../zl_vintcore2vdleq/zl_2vdleqbase.sp，找到 intinvixn fbpathxn intinvoxn fbnpratio 的最佳组合，目标 (iddq_vintcore * iddq_vdleq)^0.5 * max(tpr_in_out, tpf_in_out) * area」
- agent 建 zl_opt_vdleq.py → launch smoke (5 combos) → poll → full scan → summary CSV；用户追加硬约束 tr/tf≤80p, tpr/tpf≤205p

### 段4 (msg 201→259) — 应用 skill 到 vwlp 4-config 扫描（B 档 hidden spec 来源）
- msg201: 「现在执行另外一个扫描任务 .../zl_vintcore2vwlp/.../zl_2vwlpbase_withpwron.sp 这是四个扫描任务，分别是 sel_indrv=0,1,2,3；目标 (iddq_vintcore*iddq_vwlp)^0.5*max(tpr_in_out,tpf_in_out)*max(tr_out,tf_out)*area；硬性要求 l2_max 和 r2_max 均小于 0.9625；各 xn 不大于3，两个 ratio 不大于10，npw 不大于2000n」
- msg211: 「除 npw 的精度为 100n 外，其余精度都是 0.1」
- agent 建 zl_opt_pwron.py → smoke indrv=0 → full scan，trace 在 msg259 扫描中 SIGKILL/aborted 结束（未完成）

## reframe 判定（harness-for-teeth · 11-15 重审令 doc-Q&A/skill-creation 恢复可造）

**原 trace 交付物** = 一个写在用户家目录的 skill 包（SKILL.md + 2 scripts），引用 /proj/m2701 PDK + HSPICE 实跑，**不可便携**（r883 AgentFriendlyCheck-001 同类 skill-creation reframe 首例已立）。
**reframe** → produce 参数化生成器 `gen_simscan_skill.py`：输入 spec(objective, params[name,lo,hi,precision], constraints, archive_flags, smoke_pause) → 输出 `simscan_optimal_param/` skill 包（SKILL.md + simscan_core.py + build_summary_csv.py），把 trace 4 轮精化全部固化：参数范围引导 / 冒烟必停 / 全量 measure 汇总 / 硬约束主动提醒 / waves+measures 归档。
**check 牙**：B spec（vwlp 4-config，与 A 结构性差异：objective 多 max(tr,tf) 因子 / params 6 个 vs A 4 个 / ratio 上限 10 / npw 精度 100n / 约束 l2/r2≤0.9625）→ check 独立跑 SUT 生成器于 B，断言生成 SKILL.md 嵌入 B 的 objective/params/constraints（反硬编码 A）+ 4 项精化结构齐全 + 脚本 py_compile + 确定性 3 run + anti-stub。layer L1（无 EDA 二进制）。

## A/B spec 对照（造题用）

| 维度 | A (vdleq, trace-faithful) | B (hidden, vwlp, 结构性反向) |
|---|---|---|
| circuit | zl_2vdleqbase | zl_2vwlpbase_withpwron |
| objective | (iddq_vintcore*iddq_vdleq)^0.5*max(tpr_in_out,tpf_in_out)*area | (iddq_vintcore*iddq_vwlp)^0.5*max(tpr_in_out,tpf_in_out)*max(tr_out,tf_out)*area |
| params | 4: intinvixn/fbpathxn/intinvoxn/fbnpratio ≤3, prec 0.1 | 6: intinvixn/fbpathxn/intinvoxn ≤3 prec0.1 + fbnpratio/nkratio ≤10 prec0.1 + npw ≤2000n prec100n |
| constraints | tr_out/tf_out≤80p, tpr_in_out/tpf_in_out≤205p | l2_max≤0.9625, r2_max≤0.9625 |
| archive | waves+measures true, smoke_pause true | waves+measures true, smoke_pause true |

## 造题 ETA / DEBT
deepread 完成 r889。合成 case EDA-Eval-DesignFlow-SimScanSkillGen-001 计划同轮（k~15, 5 neg, L1 produce-generator）。若预算不足则 DEBT 顺延 r890 首事。
