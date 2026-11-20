# Deepread: 1794572120764_64rg2 — vlshft 设计自动化（level shifter 参数优化）

> **shard B · r536 · 2026-11-14** · trace_source: user=hairuizh, host=hfeg0pkn001 (10.129.2.10), session=1794572120764_64rg2.messages.json, match_count=365 (365 hspice + 3 netlist), 361 msgs
> **来源**: daily-log 增量挖掘 r536（eda_trace_2026111*.log, spice tool-count≥10）：664 spice-dominant slugs → diff vs 1113 scan pool (4624 slugs) → 47 truly-NEW → diff vs 4-shard ledger (3201) → **1 unpeeked = 64rg2** → CLEAN B-domain → claim → deepread
> **状态**: DEBT:1（本轮深读，下轮交付 case）

## 一、用户意图（USER#0 原文）

```
<user_input mode="act">vlshft设计自动化:
通过扫描@/rundata/m2701/V0_DDR2/simdir/finesim/workdir/hairuizh/simulation/presim/lvlshft/spice/zl_vintcore2vwlp/zl_2vwlpbase.sp 中的myxn,寻找到最优的参数组合;目标
两个sel_cond下的meas_tpr_in_out和meas_tpf_in_out<280p, meas_tr_out和meas_tf_out<125p, iddq_vintcore<1.5n, iddq_vwlp<4.1n, idda_vintcore<0.6u, idda_vwlp<11.8u;若能同时满足所有目标,寻找 iddq_vwlp*(meas_tpr_in_out＋meas_tpf_in_out)/2*area最小的参数组合,每个参数精确到0.1,其中area是所有晶体管的W*L和(不包含Xindrv和Xoutdrv);若无法同时满足所有目标,则寻找各目标相对偏移量*area 乘积最小的参数组合,示例meas_tpr_in_out的相对偏移量为max(meas_tpr_in_out/280p,280p/meas_tpr_in_out).所有测量值参与计算时都应先转换为正值;所有测量值不允许fail.
```

## 二、任务结构（B 域 spice_sim/characterization · L2）

- **5 个可调参数**（.data myxn block）：`intinvixn`, `fbpathxn`, `intinvoxn`, `nkratio`, `fbnpratio`，精度 0.1
- **8 个测量目标**（两个 sel_cond 各一组）：
  - 时序：meas_tpr_in_out < 280p, meas_tpf_in_out < 280p, meas_tr_out < 125p, meas_tf_out < 125p
  - 电流：iddq_vintcore < 1.5n, iddq_vwlp < 4.1n, idda_vintcore < 0.6u, idda_vwlp < 11.8u
- **目标函数**：
  - 全满足时：minimize `iddq_vwlp * (meas_tpr_in_out + meas_tpf_in_out)/2 * area`
  - 不全满足时：minimize `Σ relative_deviation_i * area`（relative_deviation = max(val/target, target/val)）
  - area = Σ 所有晶体管 W*L（不含 Xindrv 和 Xoutdrv）
- **硬约束**：所有测量值不允许 fail（必须有效数值，转正值后参与计算）

## 三、assistant 工具链（真跑 hspice）

1. `list_allowed_files` 探索目录 → `read_files` 读 zl_2vwlpbase.sp（143 行）+ invdrvs.sp + 历史 .mt0.csv
2. `read_files` 读 helper 脚本（mspice.sh, run_hspice.sh, find_mspice.sh）
3. `editor` 写 env_check.sh / launch_bg.sh / poll.sh / build_deck.py / eval_csv.py
4. `run_approved_command` (profile=shell-runner) 后台跑 hspice：`hspice -i <deck> -o <out>/zl_test`，sleep+poll
5. `run_approved_command` (profile=python-runner) 跑 build_deck.py（注入 combos 到 .data myxn block）+ eval_csv.py（解析 .mt0.csv → area + feasibility + objective + rank）
6. **7+ 迭代**：coarse scan → refine → fine local scan，每轮 8-10 combos

## 四、关键实测结果

- baseline: area=1062f m², iddq_vwlp 9.9n/13.6n (target 4.1n) FAIL, idda_vwlp 19.4u/16.6u (target 11.8u) FAIL, iddq_vintcore sel8 1.69n (target 1.5n) FAIL → **infeasible**
- iter1 (8 combos, vwlp levers): all infeasible, timing sensitive to fbnpratio/nkratio
- iter4 best: (ii=1.8, fb=1, io=0.6, nk=1.1, fbn=3.5) obj=7.691e-12, tpr=277p just meets
- iter6 best: (ii=1.8, fb=1, io=0.4, nk=1.1, fbn=3.5) obj=6.393e-12, tr=119p, iddq_vwlp=6.75n
- **io=0.3 invalid** (ntk width min exceeded under shrink), **fb<1.0 invalid** (ptk W/L out of range)
- iter7+ 后续: 最终在 fallback objective 下优化（iddq_vwlp/idda_vwlp targets 物理不可达）
- 最终 best combo 区域: (ii≈1.8, fb=1, io=0.4, nk≈2.5, fbn≈2.3) fallback obj ≈ 6.2e-12

## 五、case 合成计划（下轮 r537 交付）

- **task_id**: EDA-Eval-DesignFlow-VlshftParamOpt-001
- **domain**: spice_sim (characterization)
- **difficulty**: L2（真跑 hspice/finesim on .75）
- **A 档 trace-faithful**：prompt 用 hairuizh 原文（保留真实路径/参数名/目标）
- **attachments**: zl_2vwlpbase.sp（143 行 deck，含 .subckt/.data myxn/.meas）+ invdrvs.sp（include 文件）
- **deliverable**: submit.zip 含 params.json（5 参数）+ modified zl_2vwlpbase.sp
- **hidden B**: 不同 sel_cond 参数 / 不同 outload / 不同 target 阈值（规模/取值/结构异于 A）
- **check.py**（k≥8 独立条件）：
  ① zip 内 params.json + .sp 齐全
  ② 5 参数均在有效范围（io≥0.4, fb≥1.0 等物理约束）
  ③ hspice 退出码 0 + job concluded（subprocess 真跑 on B deck）
  ④ .mt0 所有测量值非 fail（无 missing/fail 标记）
  ⑤ meas_tpr_in_out < 280p（两个 sel_cond）
  ⑥ meas_tr_out < 125p
  ⑦ iddq_vintcore < 1.5n
  ⑧ iddq_vwlp < 4.1n（或 fallback 模式下偏移量合理）
  ⑨ area 计算正确（Σ W*L 排除 Xindrv/Xoutdrv，oracle subprocess 重算）
  ⑩ objective 值与 oracle 一致（反硬编码 B-token guard）
- **negative**: fake_empty / fake_print_target / naive_baseline_combo（全 FAIL）
- **test_rationale**: `10 条断言：①zip 齐全 ②参数范围 ③hspice exit0 ④测量无fail ⑤tpr<280p ⑥tr<125p ⑦iddq_vintcore<1.5n ⑧iddq_vwlp<4.1n ⑨area oracle 一致 ⑩objective 一致`

## 六、deck 已提取 ✓ → 下轮第一件事 = 合成交付 case

- **deck 已提取**：`zl_base_template.sp`（143 行）从 `/home/hairuizh/agent_out/2026-11-13-20-00/zl_base_template.sp` (10.129.2.10, /home/hairuizh/agent_out/ 可读) ssh 读取，存 `designflow/trace_deepreads/64rg2_zl_base_template.sp`。
- deck 结构：.option + .param（电压域/尺寸/outload=8f/sel_cond=7→.alter 8）+ .data myxn（5 参数）+ .inc conditions_new.sp + invdrvs.sp + 8 个 X 器件（Xindrv/Xoutdrv 排除 area）+ vcap + 电源 + .tran sweep + 18 个 .measure（含 tpr/tpf/tr/tf + iddq/idda）+ .alter sel_cond=8
- **下轮第一件事**：用此 deck 合成 EDA-Eval-DesignFlow-VlshftParamOpt-001：assets/（deck + invdrvs.sp + conditions_new.sp 需从 .75 取或构造等价）→ reference/（最优 params.json + check.py）→ hidden/（B 变体：不同 outload/target/sel_cond）→ negative/ → .75 hspice 自验 → 落 jsonl_B → mark case。
- ⚠️ invdrvs.sp + conditions_new.sp（.inc 文件）尚未提取，下轮需从 conversation 或 agent_out 取（合成时可用等价 stub 替代 if 不可得，但优先取真文件）。
- ⚠️ deck 含 .inc 绝对路径指向 /proj/m2701/...（.75 上可能可读），check.py 需改 .inc 为 workdir 相对路径或预置 include 文件。
