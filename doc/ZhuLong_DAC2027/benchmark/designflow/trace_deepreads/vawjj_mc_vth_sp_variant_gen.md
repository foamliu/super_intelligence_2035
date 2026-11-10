# trace_deepreads/vawjj_mc_vth_sp_variant_gen.md — 1794277350221_vawjj

## 元信息
- anchor: 1794277350221_vawjj
- user: leliow
- host: hfeg0plg52
- match_count: 340 (msgs)
- mtime: 2026-11-10 ~17:0x (fresh-window mtime >= 15:30)
- domain: spice_sim
- verdict: CLEAN produce-task (U1)

## 选轮（A-合规评估）
- U1 (ts=1793351622661)：「现在需要根据d0_bl10_m0.sp生成d0_bl10_m2.sp文件…查看vth.mt0…将序号2的vth组合…依次替换…的被减数…」= CLEAN produce-task ✓（提需求 + 给出算法，未给根因/修复方案）
- U2-U10: 后续不同 batch .sp 修改任务（255_11111111_bybl KCT 参数修改 / mixw mismatch 替换 / 16mm .param 删除等），各自独立 produce-task，本轮不取
- 选 U1：算法清晰、自包含、可泛化（hidden B 换 vth.mt0 + mc_index）

## 深读（U1 段 idx 7-19，340 msgs / 175 user turns）
- assistant 工具链：find_files.sh (run_approved_command shell-runner) 定位 mc_100/ 下 d0_bl10_m0.sp / m1.sp / vth.mt0 → read_files 读三文件 → 分析 m0.sp base = vth.mt0 mc_index 1 行 (4.9529/4.9529/5.3261/5.3261) → 发现 m1.sp 已用 combo 4.9437/5.0067/5.3819/5.1319 但 NsR 行 minuend 未换（用户示例笔误）→ ask_question 求确认 → code_sidecar_sigterm（session 中断，未产出最终 m2.sp）
- **金标准 = 用户 U1 文档化算法**（assistant 未产出最终文件）：
  1. 读 base.sp，定位 4 条 .param delvtoBL0_{NsL,NsR,PsL,PsR}='+(<minuend> - <subtrahend>)*2'
  2. 读 vth.mt0：前 3 行头注释，第 4 行起 100 行，col1=index(0..99)，cols 2-5 = vth_NsL/NsR/PsL/PsR
  3. 取 index==mc_index 行的 4 个 vth 值
  4. 依次替换 4 条 .param 的被减数(minuend, 第一操作数)，减数(subtrahend=nominal)与 *2 不变
  5. 其余行原样保留
- 真实文件在 /rundata/sim_cloud/CRG/leliow/drgqa/...（.75 e0031982 无权限读，已验证 No such file）→ B-synthesized 资产

## 合成
- case EDA-Eval-DesignFlow-McVthSpVariantGen-001 (spice_sim/synthesized/L1 k=17)
- deliverable: mc_vth_sp_variant_gen.py (CLI: <base.sp> <vth.mt0> <mc_index> <out.sp> <out_report.json>)
- 资产 A: base.sp (4 .param delvtoBL0 + .inc/.tran/.measure/.print/.end) + vth.mt0 (3 头 + 100 行, seed=42) + output_format_spec.txt + task_brief.md
- 隐藏 B1: hidden_b1_base.sp (nominal 0.481/0.5205) + hidden_b1_vth.mt0 (seed=137) + mc_index=7
- 隐藏 B2: hidden_b2_base.sp (nominal 0.512/0.548) + hidden_b2_vth.mt0 (seed=99) + mc_index=63 (反硬编码)
- reference: mc_vth_sp_variant_gen_ref.py (regex 解析 .param + vth.mt0，保留 *2 因子，report JSON)
- check.py: 17 断言 a-q，subprocess 真跑候选在 B1+B2，_parse_vth_row/_parse_base_nominals 独立重算

## 自验
- ref PASS 17/17 (B1 idx=7: 4 minuends=vth row 7, subtrahends=nominal, *2 kept, non-param preserved, report fields+vth match; B2 idx=63: minuends=vth row 63 ≠ B1; determinism 3x identical md5)
- A (idx=2) 端到端正确：minuends=4.8878e-01/4.9877e-01/5.3958e-01/5.6752e-01，subtrahends=4.9529e-01/4.9529e-01/5.3261e-01/5.3261e-01
- 6 neg (naive_empty/hardcoded_a/only_print/empty_shell/no_replace/ref_core_deleted) 全 FAIL NEG_RC=0
- §4.9 三假 (empty_shell→f/c, only_print→f, ref_core_deleted→i/p) 全 FAIL
- 断言门 k_rationale=k_check=17 ≥ 8 ✓
- test 字段与盘上 check.py 字节同步 sha256=2d248b13b6613369381d835050dfc6097d8b4ff990a0359c3fe7467e2428863a (8629B)
- jsonl B 238→239, ledger covered 239→240 (spice_sim 192→193)
