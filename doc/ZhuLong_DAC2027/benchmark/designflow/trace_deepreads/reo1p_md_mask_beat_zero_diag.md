# deepread — 1791191409174_reo1p · dandans @ hfhds201 · MdMaskBeatZeroDiag-001

## trace
- session `1791191409174_reo1p` (dandans, dir-based, 64 msgs, 1.45MB, Oct 8)
- agent=lead, cline session format (dict with "messages" list)
- source: hfhds201 cron blind spot (not in 11-05 summary); top-100 by size diff ledger → 61 not-in-ledger → peek 12 NEW → reo1p CLEAN

## U#0 (verbatim, A-faithful prompt — only user task turn; rest are tool_results)
> 帮我解析下ddr6_test.sv文件，告诉我为啥在CRC没开的时候+MD_8b+1P6时，PSD0的dq5的D16-D23位期望值是0？

选轮判定：U#0 提出需求（why 期望值=0），无根因、无修复方向 → A-faithful CLEAN ✓。其余 63 条 user msg 全为 tool_result（read_files/run_approved_command 结果），无第二个任务轮。

## 工具链 (assistant, 64 msgs)
- list_allowed_files ×2 (env root /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen)
- run_commands ×3 → 全 disabled ("Raw shell tool run_commands is disabled; use run_approved_command")
- search_codebase ×2
- read_files ×24：ddr6_test.sv (分 11 段 1-10950 行) + ddr6_tasks.sv (分 5 段 + 全量) + ddr6_genvector.sv + ddr6_interface.sv + ddr6_package.sv + ddr6_specdef.sv + compare_tasks.sv + pevave_tasks.sv
- M#63 最终分析（金标准）

## 金标准 (assistant M#63, 完整分析)
**核心结论**：`md_mask`（元数据掩码）在 `write_mem_arr` 中阻止 DQ5 的 D16-D23（beats 16-23）写入 `mem_arr`。与 CRC 是否使能无直接关系——由 `MR0_sys_md_mode`（元数据模式）决定，即使 `MR1_wr_crc_en=0` 仍生效。

### 详细溯源（与真实代码核对 ✓）
1. **数据格式** (`wr_reorganize_dq`, ddr6_tasks.sv L1921-1926)：X1P6 (DQ_BITS=6, bl=24, MAX_DQ_BITS=144) reorganize 后 DQ5 = bits[120:143]，beat0=bit120, beat23=bit143。
2. **md_mask 定义** (`write_mem_arr`, L1684-1774)：
   - X1P6 MD_OFF: `144'hFF0000_000000_000000_FF0000_000000_000000` (DQ5+DQ2)
   - X1P6 MD_8b_B DqSelect=0 (`else non-SC1 分支, L1728, last-if-wins): `144'hFF0000_000000_000000_000000_000000_000000` → **DQ5 masked**
   - X1P6 MD_8b_A DqSelect=0 (`else, L1726): `144'h000000_000000_000000_FF0000_000000_000000` → DQ2 masked
   - 注：L1717-1724 (`ifdef SC1) 与 L1726-1733 (`else) 重复定义，顺序 if（非 else-if）→ 后者覆盖；SC1 未定义 → `else 生效。
3. **md_mask 应用** (L1761-1771)：`for(i) if(md_mask[i]==0) mem_arr[...][i]=dq[i];` → md_mask==1 的位不写入，保留 init 值 0。
4. **FF0000 含义**（24-bit DQ5 字段）：`11111111_00000000_00000000` → 高 8 位 = beats 16-23 masked。
5. **CRC 无关**：Write 任务中 CRC 使能仅控制 CRC 错误注入块；无论 CRC 是否使能，后续 write_mem_arr 都按 MR0_sys_md_mode 应用 md_mask。
6. **读回路径** (read_mem_arr, L1776-1798)：从 mem_arr 读 val，CRC 使能时注入 CRC，否则跳过；mem_arr 中 DQ5 D16-D23 从未写入 → 读回为 0。

### 真实代码核对
从 trace read_files tool_results 提取 ddr6_tasks.sv L1684-2012 真实原文（write_mem_arr + read_mem_arr + wr_reorganize_dq + rd_reorganize_dq）。核对：
- L1714 X1P6 MD_OFF = FF0000_.._FF0000_.. ✓
- L1726-1733 `else 分支 MD_8b_B DqSelect=0 = FF0000_000000_000000_000000_000000_000000 ✓（DQ5 masked）
- L1761-1771 md_mask[i]==0 才写入 ✓
- L1921-1926 wr_reorganize_dq ✓
- `ifdef SC1 / `else 重复定义 ✓（真实代码的微妙点）

## 合成 (case EDA-Eval-DesignFlow-MdMaskBeatZeroDiag-001)
- **通用化** `diag_md_mask_beat_zero.py <tasks_sv> --dqmode X1P6 --md MD_8b_B --dqselect 0 -o out.json`：
  1. 预处理 `ifdef SC1/`else/`endif → 默认取 `else（non-SC1）分支
  2. 解析 write_mem_arr 的 md_mask 赋值（条件 dqmode/md/DqSelect），last-if-wins
  3. 解析 wr_reorganize_dq 注释得 DQ_BITS/MAX_DQ_BITS/MAX_BURST_LEN
  4. 解码 md_mask hex → bit i (0=LSB) set → DQ=i//24, beat=i%24 → 分组连续 beat 为区间
  5. 输出 {config, md_mask_hex, masked_dqs, reorganize, root_cause, crc_independent}
- **A=真实** (ddr6_tasks.sv L1684-2012 清洗版)：X1P6 MD_8b_B DqSelect=0 → md_mask=ff0000...(36 hex), DQ5 beats 16-23, beat_count=8
- **hidden B=合成** (ddr6_tasks_B.sv)：同 X1P6 reorganize，`else 分支 MD_8b_B DqSelect=0 改为 `000000_000000_00FF00_000000_000000_000000` → DQ3 beats 8-15（不同 DQ + 不同 beat 区间，挡硬编码）；SC1 分支放诱饵值（FFFFFF..）挡错误选支
- **判分 14 断言 (a-n)**：含交叉输入守卫（候选在 A 跑得 DQ5 beats 16-23 证泛化）+ A-only 未泄漏（outB 无 DQ5/16-23/A-mask）+ 3 次幂等 sha256
- 自验：ref PASS 14/14 ✓ + 4 negative 全 FAIL distinct（naive_hardcode_a→c / empty_shell→b / print_expected→k / core_deleted→d）+ NEG_RC=0 ✓ + §4.9 三假（空壳→b / 打印期望→k / 删核心→d）全 FAIL ✓ + 断言闸门 k_rationale=14==k_check=14≥8 ✓ + jsonl test==disk roundtrip sha e25348b43fa29a7b ✓
