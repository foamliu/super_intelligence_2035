# deepread 97ksq — duplicated subckt definition 诊断 (jiangbaol @ hfeg0pkn004)

## trace
- session: 1793849641832_97ksq (jiangbaol, hfeg0pkn004 / 10.129.2.13)
- 198 msgs, 1035030 B, mtime ~2026-11-05, dir-based
- spice keyword matches (cron): hspice=113 / netlist=636 / schematic=144
- 来源：11-05 重扫令 hfeg0pkn004 cron 盲区直扫，unscouted 按 spice 计数排序取 top

## 对话流（4 个用户任务轮，本 case 用 U#0）
- U#0 (idx=0, ts=1792559584843)：粘贴 hspice/finesim 报错
  `**error** (.../DqIb_2stg_DfeM6V2.spf.TYP_98_RCC:25) duplicated subckt definition
  'DqIb_2stg_DfeM6V2'. Please refer to option 'redefsub' ...` + 「该报错应该如何修改」
  → 提出需求/目标，未给根因/修复 → A-档选轮 ✓
- U#1 (idx=2)：如何设置 option 让 hspice 波形每层级含所有 net（另一话题，不入本 case）
- U#2 (idx=7)：检查 004_onlySlicer_delay_m2701.sp 为何无法 probe（另一话题）
- U#3 (idx=33)：在该 .sp 添加 measure 语句（另一话题）

## 金标准 (assistant A#1, idx=1)
通用 SPICE 网表/仿真器报错诊断（HSpice/FineSim/Spectre）：
1. 报错含义：PEX 提取的 SPF 寄生网表第 25 行，子电路 DqIb_2stg_DfeM6V2 被重复定义
   （同名 .subckt 出现 ≥2 次），默认重复定义为致命 error
2. 常见原因：
   ① 同一 .spf 在顶层 netlist 被 .include 两次（最常见）
   ② 两个不同文件定义了同名 subckt（.spf 与预仿真/顶层 cell 都有）
   ③ PEX 输出冗余（top cell 既作子电路输出又在顶层调用）
   ④ view/文件被多次加入 ADE/仿真器 netlist（config cellview 挂错被 netlist 两次）
3. 修复优先级：
   ① 根本：去掉重复的 .include，只在一处引入
   ② 只选其一：后仿删掉逻辑网表对 top cell 的定义，只保留 PEX
   ③ 治标：`.option redefsub` 把 error 降级为 warning（两份不一致时后读入覆盖前一个，慎用）
   ④ Cadence ADE：检查 config cell 是否 bind 多个 view，删多余一条
- assistant 未读真实 .spf（给通用解释，用户接受，无 U#0 后续追问）→ 金标准=通用结构化诊断

## 本 case 通用化
- 任务：解析任意 SPICE .spf 网表，定位重复 .subckt 定义，输出结构化诊断 JSON
- reference=diag_dup_subckt_ref.py：栈式配对 .subckt→.ends，按名分组找重复，
  输出 {total_lines, error_type, subckt_name, error_line(2nd .subckt 行),
  def_count, def_locations, ends_locations, redefsub_option, duplicates_identical,
  simulator, total_subckt_defs, duplicate_names}
- A=A_spf.spf(faithful 重建 40 行：DqIb_2stg_DfeM6V2 重复定义，2nd .subckt@line25，
  body 完全相同→identical=true，4 个 .subckt)
- hidden B=B_spf.spf(结构不同 31 行：Sa_dfe_top 重复定义，2nd .subckt@line20，
  body 不同(多 c0 行)→identical=false，5 个 .subckt)
- check.py 15 断言(a-o)：交叉输入守卫(n:A DqIb/25/identical=true)+A-only 泄漏闸门
  (o:源码不含 DqIb_2stg_DfeM6V2//proj/dejoa/TYP_98_RCC)+3 次幂等 sha256
- negatives: naive_hardcode_a(FAIL e)/print_expected_b(FAIL n)/empty_shell(FAIL d)/
  core_deleted(FAIL g) — 4 distinct

## 自验
- ref PASS 15/15 ✓
- 4neg ALL FAIL distinct(e/n/d/g) ✓ + NEG_RC=0 ✓
- §4.9 三假(空壳FAIL d/打印期望FAIL n/删核心FAIL g)全 FAIL ✓
- 断言闸门 k_rationale=15==k_check=15≥8 ✓
- jsonl test==disk sha b1e3c63ddd9f0edc ✓ → EDA-Eval-DesignFlow_B.jsonl 183→184
- mark ledger 185→186 covered, spice_sim 146→147
