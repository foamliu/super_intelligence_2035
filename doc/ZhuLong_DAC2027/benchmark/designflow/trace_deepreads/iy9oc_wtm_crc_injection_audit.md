# trace_deepread: iy9oc — WTM CRC injection audit (tongfanl@hfhds201)

- **session**: `1793363756811_iy9oc` (tongfanl, hfhds201, 54 msgs, 154 spice kw, mtime 2026-10-30 20:35)
- **domain**: spice_sim / sim_vector (WTM = Write Training Mode verilog vecgen pattern)
- **A-faithful need turn**: U#22 (verbatim) —
  「帮我看下/home/tongfanl/DDR6/DSCQA/analogsim/WTM/WTM004_block_check.v文件，
  95：97行能实现在WTM期间造CRC错的目的吗？
  158行到161行能实现在退出WTM后造CRC错的目的吗？
  写这个是为了验证，在WTM期间需要禁止CRC拉ALERT的功能」
  — 提出需求，无根因/修复方向 → A-faithful CLEAN ✓
- **non-prompt turns** (不入 prompt): U#0/U#18 (meta: 抽激励环境在哪), U#52 (CRC_11 env config 澄清)

## Gold standard (assistant msg#51 + refined msg#53 after U#52)

**Q1 (95-97行, WTM 期间造 CRC 错)**: ✅ 注入机制成立, ⚠️ 缺 CRC 使能
- 时序位置正确: line 57 `MR5=Write_Training_Mode` 进 WTM, line 146 才退出, 96 行 Write 在 WTM 期间
- `wrcrc_errforce=1 → Write → =0` 用法与 `CRC001_DualBank_ActWrRd_Err.v` (43-46行) 完全一致
- `.err_inject_rand(0)` 关掉随机总线错误, 错误源隔离干净
- **关键问题**: 扫 643 个 pattern, `MA_wr_crc_mode_sel` 只在 CRC001/CRC002/Training061/MCME004-005 显式设置, **WTM004 全程没设** → 若 TB 默认没使能写 CRC, DUT 不校验 CRC, 注入空转
- 用户 U#52 澄清: vecgen 配置 `CRC_11` 把 WR/RD CRC 都打开 → 最大前提问题解决

**Q2 (158-161行, 退出 WTM 后造 CRC 错)**: ✅ 位置正确, ❌ 159行 Active 协议问题
- 146 行 `MR5=Func_Disable` 退出 WTM, 158-161 注入在退出后 → 位置正确
- **159行**: bg1/bk1 在 149行激活后, 150-156 读全 `.ap(0)` bank 一直 open, 159行对同一 open bank 再发 ACT = 协议违规

**4 件建议处理/确认 (msg#53)**:
1. 159行重复 ACT 建议删 (协议问题, 与 CRC 无关)
2. CRC UI 与 WTM mask MR 的 UI 映射对齐 (CRC_11 后 burst 插入 CRC UI, gen_wtm_write_data 按 UI 序号打错, 需确认 mask 映射)
3. ALERT 检查手段确认 (CRC001 有 MA_alert_verify 序列 14-19行, WTM004 没有; pass 判据: WTM 期间 CRC 错不拉 ALERT=pass, 退出后拉 ALERT=pass)
4. 补 `MA_wr_crc_error_status` 回读形成正反证据 (CRC001 60-68行做法)

## 5-segment evidence chain
1. WTM entry/exit region: MR5=OP_func_mode_Write_Training_Mode (entry) / MR5=OP_func_mode_Func_Disable (exit)
2. CRC001 canonical wrcrc_errforce pattern (43-46行: =1→Write→=0)
3. 643-pattern scan: MA_wr_crc_mode_sel only in CRC001/CRC002/Training061/MCME004-005, NOT WTM004
4. injection timing: during-WTM (line 96, inside region) vs after-WTM (line 160, after exit)
5. repeat-ACT-on-open-bank at after-WTM Active (line 159, bg1/bk1 open via .ap(0) reads)

## Portable sub-skill extracted
`audit_wtm_crc_injection.py <wtm.v> -o out.json` — static code audit of any WTM pattern:
WTM region (entry/exit line) + wrcrc_errforce injection blocks (during/after WTM classification)
+ MA_wr_crc_mode_sel / MA_alert_verify / MA_wr_crc_error_status presence + repeat-ACT-on-open-bank
detection + .err_inject_rand(0) isolation + gen_wtm_write_data/ui_mask/dq_mask mask mapping.

## Case
- **case_id**: EDA-Eval-DesignFlow-WtmCrcInjectionAudit-001
- **A**: A_wtm_block_check.v (faithful reconstruction of WTM004_block_check.v; NO MA_wr_crc_mode_sel/
  MA_alert_verify/MA_wr_crc_error_status; HAS repeat-ACT-on-open-bank at after-WTM Active; A-only marker)
- **hidden B**: B_wtm_block_check.v (WTM005, structurally different: HAS all 3 MRs; NO act issue;
  different banks bg2/bk2/bg3/bk3, seed A5C3E1, write_num 8)
- **k=15** conditions (a-o); ref PASS 15/15; 4 negatives FAIL distinct (f/m/b/d); NEG_RC=0;
  §4.9 trio FAIL; assertion gate 15==15≥8
