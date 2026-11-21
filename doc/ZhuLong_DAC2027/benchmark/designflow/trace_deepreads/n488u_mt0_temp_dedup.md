# n488u — FineSim .mt0 duplicate-temp-row cleanup (DEBT: deepread done, case synthesis pending)

- **session**: 1795073056270_n488u.messages.json
- **user**: willz @ hfeg0plg77 (IP in summary_1120_reconstructed.tsv = 0.0.0.0 placeholder; host hfeg0plg77)
  - ⚠️ note: summary_1120_reconstructed.tsv row shows host=hfeg0plg77; the .75 ssh target for the snapshot is the .75 local filesystem (hfhds201) since the session dir lives under /home/willz on .75. Live session dir was empty; used .snapshot/hourly-new.2026-11-22_0000.
- **match_count**: 63 (summary_1120_reconstructed.tsv); keywords: netlist:299;schematic:78;hspice:77;cmos:48;waveview:12;drc:5;analog:5
- **domain**: spice_sim
- **ledger status**: claimed (r999, 2026-11-22) — NOT parked, viable distinct candidate
- **msgs**: 226 total / 13 real user_input / 59 assistant

## Trace intent (U[1], the FIRST and primary distinct sub-task)

用户原话（idx=0）：
> `/proj/ddgot/V0/workdir/willz/simulation/sim_result_261112/24_sense_T/mt_files_contents.txt`修改该文件，去掉每一段中temp重复的前几行数据

**背景**：willz 用自写 `mergemt.py`（trace idx=11 读到，44 行）把 `24_sense_T/` 子树下所有 `.mt0`/`.ma0` 文件按 `=== <standard_name> ===` 分段头拼接成单个 `mt_files_contents.txt`（每段 = 一个 PVT corner 的 FineSim .mt0 测量表）。

**文件结构**（每段）：
- L1: `=== <flat_name>.mt0 ===`
- L2: `$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0`
- L3: `.TITLE '...'`
- L4: 列头（12 列）：`cadelay1 cadelay2 carf_skew ckt_cadelay1 ckc_cadelay2 ckrf_skew ckr_caset ckt_caduty ckc_caduty car_caduty temper alter#`
- L5+: 数据行，第 11 列 = `temper`（温度），第 12 列 = `alter#`（1-based 扫描序号）

**bug 现象**：每个 .mt0 段有 13-14 数据行，但 deck（`rcv_ca_top_sim.sp`）的 intended temp sweep 是 base `.temp 45` + 10 个 `.alter`（-40, -20, 0, 20, 40, 60, 80, 100, 120, 125）= 11 个温度点。.mt0 输出里前面多了 3 行 spurious：`130, -40, -40`（alter 3/4/5），其中 130 不在 sweep 里、两个 -40 是 alter 2 的重复。agent 在 idx=17 thinking 里确认：deck intended sweep = `45, -40, -20, 0, 20, 40, 60, 80, 100, 120, 125`，.mt0 多了 leading `130, -40, -40`。

**用户要的变换**：每段去掉这几行 spurious 重复 temp 数据（保留 intended sweep 的 11 行）。

## 会话其余子任务（与 lbrbv r983 同 tree，近-dup，不造题）

U[2]/U[5]/U[7]/U[9]/U[12] 全是 `sim_result_261112` 树上的 .sp deck 编辑（netlist/spf include 重写、加 model、改 vdd 值、同步 diff、改 measure 语句）—— 这些与 r983 SpDeckModelStripMigrate 的 deck-migrate reframe 近-dup，**不造题**。U[1] 的 .mt0 duplicate-temp cleanup 是唯一 distinct 的 produce 意图。

## 造题方向（next round）

**form**: `mt0_temp_dedup.py` — 参数化 FineSim .mt0 拼接文件温度去重工具（produce, A-faithful, layer L1, 纯 Python 文本解析无 EDA 二进制）

**CLI**: `python3 mt0_temp_dedup.py --input <concatenated_txt> --temps <intended_temp_csv> --output <cleaned_txt>`

**行为**：
1. 解析 `--input`：按 `=== <name> ===` 切段；每段跳过 `$DATA1`/`.TITLE`/列头行，读数据行（按空白 split，第 11 列 = temper）。
2. 解析 `--temps`：intended 温度列表（如 `45,-40,-20,0,20,40,60,80,100,120,125`）。
3. 每段保留 temper ∈ intended 的数据行；丢弃 spurious 行（temper 不在 intended，或重复 temp 的多余行）。
4. 保留段头 + $DATA1 + .TITLE + 列头 + 保留的数据行，写 `--output`。
5. 写 `dedup_report.json`：`segments` (count), `rows_kept`/`rows_dropped` per segment, `total_dropped`。

**A-faithful**: `mt_files_contents_A.txt` — 4 段（f6P4_ff130/f6P4_ssm40/f7P2_ff130/f7P2_ssm40），每段 13 行含 spurious `130,-40,-40` leading + intended 11 temps；`temps_A.txt` = `45,-40,-20,0,20,40,60,80,100,120,125`。

**hidden B**: `mt_files_contents_B.txt` — 3 段（不同 corner 名 g3P1_tt25/g3P1_ff110/g3P1_ss-40），每段 16 行含不同 spurious 模式（leading `110,-40,-40,-40` + intended 12 temps 含 `135`）；`temps_B.txt` = `-40,-20,0,5,25,45,65,85,105,125,135,150`（anti-hardcode-A：段名/温度集/spurious 模式全异）。

**check.py ≥8 条**（draft）：
- a. zip 含 mt0_temp_dedup.py + py_compile 通过
- b. 跑 B exit 0，产出 cleaned.txt + dedup_report.json
- c. cleaned.txt 段数 == B 段数（3）
- d. 每段保留行数 == intended temps 数（12）
- e. 每段保留行的 temper 集合 == intended_B temps（集合相等）
- f. 段头/$DATA1/.TITLE/列头逐字保留
- g. spurious 行全删（cleaned.txt 中无 110/-40 重复 leading）
- h. dedup_report.json total_dropped == B 总 spurious 行数
- i. anti-hardcode-A：cleaned.txt 无 A 段名 f6P4/f7P2 + 无 A temp 45/125
- j. 3-seed 确定性（打乱段序，cleaned 内容按段一致）

**核心齿**: (d) 每段保留行数 == intended 数 + (e) temper 集合相等 — 反 neg_core_removed（裸 copy 不删行）+ neg_print_only（hardcode report 不删行）。

** negatives **: neg_empty（空脚本）/ neg_print_only（硬编码 report 说删了但不改 input）/ neg_core_removed（裸 copy input→output 不删任何行）/ neg_hardcode_a（用 A temps 删 B）。

## dedup 决策（造题时确认）

"重复的前几行"的精确语义：删除每段 leading 区里 temper 不在 intended sweep 的行 + temper 重复的多余行（保留首个匹配 intended 的）。next round 造题时需从 trace idx=17 agent thinking + 实际 .mt0 文件确认 intended sweep 与 spurious 模式的精确对应（不同 corner 段是否同模式）。

## DEBT

- **DEBT: 1 case 合成未做**（deepread 已完成，case 合成待 r1000）。next round 直接按上方造题方向合成即可，无需重读 trace。
- 预算：r999 ~30min 后判断 40-min 预算不足以做满 §4.9（8 条 + 3 neg + hidden B + anti-hardcode + 3-seed + self-verify），转 0-case stop-loss 轮，留 DEBT。
