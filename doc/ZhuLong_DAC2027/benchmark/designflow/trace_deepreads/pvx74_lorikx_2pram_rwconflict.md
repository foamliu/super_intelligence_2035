# Deepread: pvx74 (lorikx@hfeg0pkn001 / 10.129.2.10, mc=29, digital)

> Round r275 (2026-11-09). Status: **deepread done, case-build queued for next round**.
> 关键修正 r274：r274 称 e0046913(8uaii/vxorx/qo3pd)/fxian(7bg20) PURGED 复核属实(已删)，
> 但 r274 漏检 lorikx 的 3 个 pvx74/74bnn/cwx19（同任务不同 session）—— 它们 **EXISTS**
> 在新版 cline 目录结构 `<id>/<id>.messages.json` 下，r274 只查了 flat-file 路径才误判。

## Trace 元数据
- session: `1793098169771_pvx74.messages.json` (315,859 B, 23 msgs)
- user/host: lorikx @ hfeg0pkn001 = 10.129.2.10
- keywords: `rtl:44;verilog:29;synthesis:2;systemverilog:1` (digital-lean, mc29)
- 3 sibling sessions 同 user/host/keywords（同一任务的 3 次会话）: pvx74 / 74bnn / cwx19 — 只取最新 pvx74

## Workspace（资产路径，全部在 10.129.2.10）
`/home/lorikx/2prfbv_refer/CXMT_2PSRAM_1027_v14/rtl/`
- `sp_2pram.v` (204,266 B, mtime Oct 27 18:59) — **2P SRAM 模板（POST-fix，= golden 真实产物）**
- `MODEL_FIX.diff` (6,571 B, 106 lines) — 用户提供的修复参考 diff（3 hunks）
- `CONFLICT_QX_BUG_REPORT.md` (9,600 B, 190 lines) — 冲突 Q≠X 问题分析报告
- 另有: `sp_sram.v`, `tb_sp_sram.v`, `CR_MODEL_ALIGNMENT_NOTES.md`（非本任务必需）

## 对话流（23 msgs）
- USER#0: `ll`（ls 工作区）
- **USER#4（任务轮，逐字）**: `请阅读 @MODEL_FIX.diff @CONFLICT_QX_BUG_REPORT.md 文件，并对 @sp_2pram.v 进行修复`
  - ⚠️ 给出修复材料(diff+bug report)=给修复方案 → **B 档**（非 A-faithful，符合 §A-档选轮规则排除）
- assistant: list_allowed_files → search_codebase(锚点关键词) → get_agent_policy_status →
  editor#8 写 `.tmp_locate.py`（只读定位脚本，列 14 个锚点正则）→ run_approved_command 跑它 →
  read_files(sp_2pram.v 3 段: 1075-1215 / 2515-2625 / 3575-3690) →
  **editor#14: insert_line=2573, 在 sp_2pram.v SD 分支插入 "Read-write conflict backstop" 块**
- USER#17/#19/#21: `请继续 /compact` / `continue` / `继续`（assistant 未再产出，会话结束）

## 修复内容（关键）
MODEL_FIX.diff 含 3 hunks（用户参考），assistant **实际只应用 hunk 1**（SD 分支 backstop insert）：
1. **SD 分支 backstop insert**（@@ -2456 in 生成模型 / line 2573 in 模板 sp_2pram.v）✅ 已应用
2. SD 分支 `rw_conflict` 判据改 `(clkw_edged || (last_clkw_rise == $realtime))`（@@ -2468）❌ 未应用
3. **CD 分支 backstop insert**（@@ -3459）❌ 未应用

→ **golden = on-disk sp_2pram.v**（仅含 hunk 1 的 single insert）。会话末用户未明确接受，但这是 assistant 的真实产物。

### editor#14 插入块全文（= golden 增量，22 行）
```verilog
                        // ----------------------------------------------------------------
                        // Read-write conflict backstop (CLKR-edge-first delta ordering).
                        // CLKW and CLKR are separate nets inside the cell, so their
                        // posedges can be processed in different delta cycles of the
                        // SAME simulation time. If the CLKR posedge of this simulation
                        // time was already processed (or is being processed now) while
                        // both ports are active on the same address, the Q produced by
                        // that earlier read evaluation is invalid -> force Q = X now.
                        // ----------------------------------------------------------------
                        if ((WEB_buf === 1'b0) && (REB_buf === 1'b0) &&
                            (AW_buf === AR_buf) && (^AW_buf !== 1'bx) &&
                            (AW_buf < DEPTH) &&
                            (clkr_edged || (last_clkr_rise == $realtime))) begin
                            if (test_mode) begin
                                test_op_type_r = 2'd3;  // TEST mode: Q = X at negedge
                            end else begin
                                Q_r       = {DATA_WIDTH{1'bx}};
                                Q_force_x = 1'b1;
                            end
                        end
```

## Bug 根因（来自 CONFLICT_QX_BUG_REPORT.md）
2P SRAM 同地址读写冲突时 Q 应=X，但模型冲突检测依赖"同一 delta 内处理两个时钟沿"。
CLKW/CLKR 在 cell 内是两个独立网络，TB 中 clkr 由 always@* 从 clkw 生成，两沿 posedge 落在不同 delta，
always 块执行两次：第1次(CLRW先)写完成 clkw_prev_track=1；第2次(CLKR后)clkw_edged=0 → 冲突判据失效 → Q=新数据。
delta 顺序随仿真器版本/编译选项翻转 → 非确定现象。修复：用"本仿真时刻是否发生过 CLKW posedge"
(`last_clkw_rise == $realtime`) 替代"同 delta 两沿都置位"，并加 backstop 在写侧完成后强制 Q=X。

## Case 合成方案（next round 执行）
- **case_id**: `EDA-Eval-DesignFlow-RwConflictBackstop-001`
- **domain**: digital / verification
- **track**: B（USER#4 给修复材料=hint，非 A-faithful）
- **L 层**: L1-static（正则结构匹配；可选 L2=VCS 编译验证，但 backstop 语义需仿真冲突拍才显效，L2 成本高，先 L1）
- **交付**: `outputs/submit.zip` 含修复后的 `sp_2pram.v`
- **A 资产**（SUT 见）: pre-fix sp_2pram.v（从 on-disk golden 反向删除 22 行 insert）+ MODEL_FIX.diff + CONFLICT_QX_BUG_REPORT.md + prompt(USER#4 逐字) + task_brief(交付接口≤3行)
- **golden**（reference_submit.zip）: on-disk sp_2pram.v（含 single insert，= assistant 真实产物）
- **隐藏 B**: pre-fix sp_2pram.v 变体 —— 改参数名/周围注释使 insert 锚点行号偏移 + 信号局部改名(如 test_mode→test_en, Q_force_x→q_fx)，使"硬编码粘贴行2573"FAIL 而"结构化按锚点插入"PASS。check() 只跑 B。
- **pre-fix 反向重建**: 从 on-disk sp_2pram.v 找到 "Read-write conflict backstop" 注释块(22行)，整块删除 → pre-fix_A。验证：`grep -c "Read-write conflict backstop" pre_fix_A.sp_2pram.v` = 0；golden = 1。

### check.py ≥8 条断言清单（k_check≥8, 与 test_rationale 一一对应）
a. zip 内含 `sp_2pram.v` 且为非空 Verilog 文件
b. `sp_2pram.v` 保留 module/endmodule 完整（首 module 与末 endmodule 配对，文件可被行解析）
c. 含 "Read-write conflict backstop" 注释锚点（结构存在性）
d. 含读写双使能守卫 `WEB_buf === 1'b0` 与 `REB_buf === 1'b0`（同 always 块内）
e. 含同地址守卫 `AW_buf === AR_buf` 与 X 检测 `^AW_buf !== 1'bx`
f. 含深度边界 `AW_buf < DEPTH`
g. 含 CLKR-edge 条件 `clkr_edged` 与 `last_clkr_rise == $realtime`（或 B 改名后等价）
h. 含 test 分支 `test_op_type_r = 2'd3`（或 B 改名后等价）
i. 含 Q 强制 X `Q_r = {DATA_WIDTH{1'bx}}` 与 `Q_force_x = 1'b1`（或 B 改名后等价）
j. backstop 块位于读路径 always 块内（前后文含 `timing_check_write` 或 `cr_rw_violation_w`）—— 锚点定位
k. 无重复插入（backstop 注释块恰好出现 1 次，golden=1）
（k_check=11 ≥8 ✓）

### negative 样本（≥2，全 FAIL）
- neg1_noop: pre-fix sp_2pram.v 原样提交（未加 backstop）→ c/d/e... FAIL
- neg2_hardcode: 在错误位置(文件末尾)粘贴 backstop 字符串 → j(锚点) FAIL + k 可能>1
- neg3_stub: 只加注释行不加 if 逻辑 → d/e/f... FAIL

### §4.9 三假
- fake_empty: 空壳 zip → a FAIL
- fake_print: 只在文件头加注释 "fixed" 无逻辑 → c/d FAIL
- fake_core: golden 删 backstop if 块只留注释 → d/e/f FAIL

## 自验计划（next round）
1. 反向重建 pre-fix_A，`grep -c backstop` = 0
2. reference_submit.zip = golden，跑 check() 11/11 PASS
3. 3 negs 全 FAIL（NEG_RC=0）
4. §4.9 三假全 FAIL
5. 断言闸门 k_rationale=11 == k_check=11 ≥8 ✓
6. test 字段 sha 同步 disk check.py
7. append EDA-Eval-DesignFlow_A.jsonl → mark pvx74 case

## 资产提取命令（next round 直接用）
```bash
# 在 .75 workdir:
scp '10.129.2.10:/home/lorikx/2prfbv_refer/CXMT_2PSRAM_1027_v14/rtl/sp_2pram.v' ./sp_2pram_golden.v
scp '10.129.2.10:/home/lorikx/2prfbv_refer/CXMT_2PSRAM_1027_v14/rtl/MODEL_FIX.diff' ./MODEL_FIX.diff
scp '10.129.2.10:/home/lorikx/2prfbv_refer/CXMT_2PSRAM_1027_v14/rtl/CONFLICT_QX_BUG_REPORT.md' ./CONFLICT_QX_BUG_REPORT.md
# 反向重建 pre-fix_A: 删 "Read-write conflict backstop" 22 行块
python3 -c "..."
```
