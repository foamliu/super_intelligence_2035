# Deepread: 1793792373749_l5r0u — IO buffer SPICE 参数调谐 (data_H/data_L 目标满足)

## Trace meta
- **user**: elianaz @ hfeg0pkn002
- **session**: 1793792373749_l5r0u (230 msgs, 单用户轮)
- **match_count**: 218 (hspice:125/netlist:44/schematic:4 — hspice 主导)
- **agent**: lead (cline, deepseek-v4-flash)
- **domain**: analog_context (SPICE 参数调谐 / IO buffer characterization)
- **tools**: editor×44, read_files×29, run_approved_command×29, list_allowed_files×11, search_codebase×2

## 用户轮（逐字原文，红线 #2 不脱敏）
- **U#0（唯一需求轮，A 档合规）**：
  > `@/rundata/drcoa/V0/simdir/finesim/workdir/elianaz/simulation/99_IO_buffer/001_z_top_drgqa_slow_MC_PDA_TT.sp用这个文件跑仿真，调整参数值，使measure得到的data_H的值大于等于0.99*VDDQ，data_L的值小于等于0.001，参数范围如下LR56大于等于2.5u，小于等于3.5u，LMP12大于等于0.5u，小于等于1.5u，WMP12大于等于5u，小于等于6u，WP1大于等于1u，小于等于3.5u，WN1大于等于1u，小于等于3.5u`
- **A 档选轮判定**：U#0 = 提出目标（跑仿真调参使 measure 达标）+ 给出参数范围，**未给根因/修复方案** → 符合 A 档选轮规则②。✓

## 真实任务流（从 .sp 头部 + 工具链推断）
1. 用户指定一个现成 FineSim/HSPICE deck（`001_z_top_drgqa_slow_MC_PDA_TT.sp`，drcoa V0 IO buffer 慢角 TT PDA 仿真）。
2. deck 含 `.param VDDQ=1.1`、`.param VREF=0.75*VDDQ`、`.lib '/proj/drcoa/V0/model/current/model.sp' tt`（foundry CXMT drcoa V0 模型，**不可移植 .75**）。
3. 5 个可调 MOS W/L 参数：`LR56∈[2.5u,3.5u]`、`LMP12∈[0.5u,1.5u]`、`WMP12∈[5u,6u]`、`WP1∈[1u,3.5u]`、`WN1∈[1u,3.5u]`。
4. 2 个 measure 目标：`data_H >= 0.99*VDDQ`（高电平达标）、`data_L <= 0.001`（低电平达标）。
5. agent 读 deck → 理解参数/measure → 迭代调参跑仿真 → 找到满足双目标的参数组合。

## 子技能（可移植化 / B 档 synthesized 候选）
**IO buffer 输出驱动器参数调谐**：给定 deck + 5 参数范围 + 2 measure 目标，搜索满足目标的参数组合。
- 真实 deck 用 foundry drcoa V0 模型（不可移植 .75）→ B 档 synthesized。
- **可便携子技能**：level-1 Shichman-Hodges CMOS IO buffer（pre-driver + final-driver push-pull）+ 5 个 W/L 参数 + data_H/data_L .meas tran + 参数搜索器（网格/二分/随机）。
- 候选写 `iobuf_tune.py`（CLI `--spec <spec.json> --deck <template.sp> --outdir`）：读 spec{ranges,targets,vddq} → 生成 deck（注入参数）→ 调 HSPICE 真跑 → 解 .mt0/.lis measure → 搜索满足双目标的参数 → 输出 `tuned_params.json` + `tune_report.md` + 验证日志。
- **A-档 faithful 可行性**：U#0 纯 produce + 用户接受产物可能存在 → A-faithful 候选；但产物在 /rundata/drcoa（非便携）+ live FineSim 验证 → **B 档 synthesized**（子技能忠实于用户需求，金标准由 .75 HSPICE 标定）。

## distinct vs 已有 D analog_context case
- SpiceMeasGen-001 (#339, ho5p2)：FineSim .meas 语句生成 + 解析（无参数调谐/搜索）
- AnalogGroupCfgMergeDummy-001 (#341, ca92c)：AnaWeave GG cfg 深合并 + dummy 审计（无 SPICE/调谐）
- CpumpDeckGen-001 (#330, kja6z)：charge pump deck 生成（无参数搜索/measure 达标判定）
- LdoCircuitReport-001 (#336)：LDO deck+report 生成（无调谐搜索）
- **本条 = IO buffer 参数调谐搜索器（5 参数范围 + 双 measure 目标 + 搜索满足）**，shard D 首个「参数调谐搜索器」case，distinct ✓。

## 合成 plan（B 档 synthesized, L2 真跑 HSPICE）
- **自包含 IO buffer**（level-1 MOS，无 foundry）：pre-driver 反相器链 + final push-pull（PMOS pull-up / NMOS pull-down），5 参数映射到 final-driver MOS W/L + 电阻 LR56。
  - `WP1`/`WN1` = final PMOS/NMOS width
  - `WMP12`/`LMP12` = mid-driver PMOS W/L
  - `LR56` = 串联电阻（负载线宽）
- **deck**：`.param VDDQ=1.1` + `.meas tran data_H MAX v(data) FROM=<drive_window>` + `.meas tran data_L MIN v(data) FROM=<drive_window>` + `.tran` 扫驱动窗口。
- **搜索器**：网格/随机搜索 5 参数在范围内 → 每组合生成 deck → 跑 HSPICE → 解 data_H/data_L → 判 `data_H>=0.99*VDDQ` AND `data_L<=0.001` → 命中则输出。
- **A**（可见）：VDDQ=1.1, ranges 如 U#0, level-1 MOS vto_n=0.4/vto_p=-0.4, kp_n=120u/kp_p=50u。金标：存在满足参数组合（grid search 找到）。
- **hidden B**：VDDQ=1.2, ranges 全不同（LR56∈[1.5u,2.5u], WP1∈[2u,5u]...）, vto_n=0.35/kp_n=150u → 不同满足参数组合。cross-input guard：B tuned_params 与 A 全不同。
- **hidden B2**（反硬编码第三轴）：targets 反转（data_H>=0.95*VDDQ 较松 + data_L<=0.0005 较严）→ 不同满足参数。
- **check.py 16 条断言 (a-p)**：zip 含 iobuf_tune.py + tuned_params.json + tune_report.md · py_compile · 候选在 hidden B 上 exit 0 + 产出 · tuned_params 5 键齐全且在 B 范围内 · data_H_B >= 0.99*VDDQ_B（HSPICE 重跑验证）· data_L_B <= 0.001 · HSPICE 曾调用（.lis/.mt0 证据）· tune_report 含搜索日志/迭代次数/命中参数 · 报告含 data_H/data_L 数值 · 报告含 VDDQ · 跨输入守卫(B≠A) · B2 targets 不同→不同参数 · 反硬编码源码无 A 字面量 · B2 重跑 data_H_B2>=0.95*VDDQ_B2 · 确定性 3x sha256 · 负样本全 FAIL。
- **风险**：自包含 level-1 IO buffer 在 HSPICE tran 的 data_H/data_L 必须可被搜索器找到满足组合（需 .75 上先标定 GT）。若 level-1 buffer 驱动太弱/太强使全范围无解 → 调 vto/kp/load 使可行域存在。**下轮 #344 第一件事**：在 .75 上建 level-1 IO buffer deck → 跑 5 参数网格 → 确认可行域存在 → 标定 A/B/B2 GT → 写 check.py + negatives + 自验 → 落库。

## 台账
- claimed shard D 2026-11-07 (#343 选料轮)。
- **下轮 #344 必须合成并交付 case**（DEBT:1，本轮因 40min 预算耗尽仅完成选料+深读）。
