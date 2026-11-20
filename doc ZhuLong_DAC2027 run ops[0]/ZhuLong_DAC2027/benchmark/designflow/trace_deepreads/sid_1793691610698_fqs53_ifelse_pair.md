# Deepread — sid 1793691610698_fqs53 (jianilu @ hfeg0pkn004, mc=46, 185 msgs, 742KB)

**trace 源**：fresh rescan 2026-11-06 17:19（`find -newermt '2026-11-06 16:30:00'` 扫 42 spice-active host），11-05 19:28 快照后新写入。scp 到 .75 workdir 解析。

## 用户意图轮（A-档，纯需求）
- **U#0/U#1**（verbatim）：`ERROR! if-else conditional statements not paired (/home/coverage/DDR5/DRGQA/sim_setup/Powervoltage/Pattern_Power.sp:2)讲解报错`
  - 用户只报错 + 要求讲解，**未指出根因、未给修复** → 合格 A-档任务说明轮 ✓
- U#2 = "继续"（助推，不用）
- U#34 起切到另一任务（spf_bl_extract.py 数据不全诊断，非 spice 产需，不用）

## assistant 工具链
list_allowed_files → read_files(Pattern_Power.sp 是 symlink → finesim 缓存) → 写脚本统计 `.if/.elseif/.else/.endif` 配对（发现 .if/.endif 计数相等）→ 检索 finesim 手册（知识库无专门条目）→ msg#33 给出配对语义讲解（.if 必须有且仅有一个 .endif 闭合；.elseif/.else 必须在所属 .if…endif 块内；finesim 报 "if-else conditional statements not paired"）。**用户未明确接受产物**（直接切下一任务）→ 金标准 = 合成（参 SramIreadGen/VcoKvcoChar 模式）。

## 真实 Pattern_Power.sp（.75 cat）
513 行，17 个 `.if/.elseif/.else/.endif` 行；多段嵌套：外层 `.if pvcc 范围` 三/四分支，内层 `.if ptemp==-40 / .elseif ptemp==98 / .else` 设 pvwlp/pvblh/pvmwln/pviso 等 `.param`。报错定位 line 2（第一条有效 .if）。assistant 疑「写法/大小写或条件语法致预处理器未识别 .if」。

## 合成金标准 + case 设计（EDA-Eval-DesignFlow-IfElsePairFix-001，spice_sim A-faithful L2）
- **任务说明** = U#0 verbatim。
- **交付** = 通用 `fix_ifelse_pairing.py <broken.sp> <out.sp> [--report]`：栈式解析 `.if/.elseif/.else/.endif`（case-insensitive, 前导点），检测失衡 → 修复（缺 .endif 在 .end 前补；孤儿 .endif/.else/.elseif 丢弃），保留 Power-table 条件结构。
- **A/B 切分**：A = 缺 .endif（3-way pvcc 分支，circuit 在条件块前，pvcc=0.95/vamp=1.7/1k/1n/vout_avg 10-20n）；hidden B = 孤儿 .endif（2-way 分支，pvcc=1.1/vamp=2.0/2k/2n/vout_avg 20-40n）。两种 break 类型不同 + 参数/电路不同 → 跨输入护栏。
- **.75 HSPICE 真跑验证**（PrimeSim HSPICE V-2023.12）：
  - broken A → `**error** ... .endif is missed at or before ".end"` + job aborted ✓
  - broken B → `**error** ... .if is missing at or before ".endif"` + job aborted ✓
  - ref-fixed A → `job concluded` ✓
  - ref-fixed B → `job concluded` ✓
- **check.py 12 条断言 a-l**（k=12≥8）：zip+py_compile / --help / A exit0+out_A / L2 hspice out_A concluded / out_A 配对 / out_A 保留≥1 .if / out_A .lis 无配对错误 token / broken A 直跑必败 / B exit0+out_B / L2 hspice out_B concluded / out_B 配对+保留 / 跨输入 out_A≠out_B。
- **自验**（.75 真跑）：reference PASS 12/12；5 negative（naive_empty/print_stub/copy_input/hardcode_A/strip_conditional）全 FAIL；§4.9 三假（空壳/print-expected/不修复）全 FAIL。断言闸门 k_rationale=k_check=12 ✓。

## 落库
- 追加 `EDA-Eval-DesignFlow_B.jsonl`（110→111 行，test==check.py 逐字符相等）。
- ledger mark --status case --case-id EDA-Eval-DesignFlow-IfElsePairFix-001（covered 114, spice_sim 85）。
