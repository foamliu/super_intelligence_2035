WAITING: 0（shard A 轮 64：**完成 EDA-Eval-DesignFlow-FmRtl2RtlFlow-001（verification, L2, A档 faithful）** —— trace 1793091129423_vxorx (e0046913/hfeg0pkn003, mc=64, formality rtl2rtl) → 选 turn 0 用户原话逐字「在当前/rundata/lacaa/TV1_digital/simdir/yutingq 目录下，参考feint文件内的formality相关脚本，为我在fm_r2r目录下开发rtl2rtl功能，并使用ref_verilog和imp_verilog中的test案例去跑通。」真实任务：E902 CPU ibuf 模块级 RTL2RTL formality 等价验证；金洞察：imp cr_ifu_ibuf_r2rQA1 = ref cr_ifu_ibuf 去掉调试输出口 ifu_iu_ex_inst+pop1_inst 逻辑（set_dont_verify_points 排除该口后 88 比较点全 PASS），QA2 大幅裁剪非等价；agent LD_PRELOAD 污染致 fm_shell 启动失败 → launcher 须 unset LD_PRELOAD。为适配 design_flow 隐藏B+subprocess+沙盒缺 formality，交付 = scripts/fm_r2r.tcl(参数化 formality rtl2rtl 流程，env-driven: FM_R2R_REF_F/IMP_F/REF_TOP/IMP_TOPS/DONT_VERIFY_REF) + run_fm_r2r.sh(含 --check-rtl vcs 预检模式 + unset LD_PRELOAD + fm_shell)。assets A: feint/{fm.tcl,Makefile,common_setup.tcl} 模板 + ref_verilog/cnt_unit{.f,.v}(8-bit 计数器+cnt_dbg 调试口) + imp_verilog/cnt_unit_impl{.f,.v}(无 cnt_dbg)。hidden B: arb_unit{.f,.v}(4-bit 仲裁器+arb_dbg) + arb_unit_impl{.f,.v}(无 arb_dbg) —— 模块/功能/位宽/调试口名全异。reference: fm_r2r_ref.tcl + run_fm_r2r_ref.sh + check.py(14 条件 a-n) + reference_submit.zip + negative/(5: fake_empty→b / fake_print_expected→l(L2 真跑击穿,无 simv) / fake_core_deleted→h / naive_no_dont_verify→g / naive_hardcode_a→m) + negative_selftest.py。**L2 核心 (l)**: vcs R-2020.12 真跑——在 B 上执行提交的 run_fm_r2r.sh --check-rtl，vcs elaboration B ref(arb_unit)+imp(arb_unit_impl) 各 exit0 留 simv 无 Error-[ 输出 RTL_OK；print-stub 无 simv 即被击穿。自验(本地静态 + .75 L2 手动): ref PASS(13 静态 a-k,m,n 本地 + L2 l 在 .75 vcs 留 simv/RTL_OK/无Error) + §4.9 三假全 FAIL + 2 naive 全 FAIL + print-stub 无 simv。断言闸门 k_rationale=k_check=14>=8 PASS。追加 A.jsonl 末行（test==disk roundtrip OK）。台账 mark case。covered=71（+1 verification）。**注记**：沙盒 .75 MISSING formality，故 L2 以 vcs elaboration 为代理（候选 run_fm_r2r.sh --check-rtl 真跑 vcs 在 B 上），formality TCL 本体静态判分；real E902 RTL 在用户 /proj 网络不可达且体积大，故用结构同构的小自含 verilog 对（计数器/仲裁器）承载相同 rtl2rtl+dont_verify 机制。infra 坑同前：.75↔本机无共享挂载、本机不可直连 .75，自验走本地静态 + .75 手动 L2。
（轮 63 DrcDocConvert-001 / 轮 63b SimMakefileVCS-001 / 轮 62 NetCellMap-001 / 轮 61 RunsetVer-001 / 轮 60 VpsRegrErrorEngineer-001 落地见归档批次 57；轮 50–57 已归档至 `MEMORY_A_archive.md` 归档批次 56（2026-11-04）；轮 43–49 见归档批次 55；轮 33–42 见归档批次 50。）

## 顶部快照
- **PHASE**: shard A 轮 64（FmRtl2RtlFlow-001 落地完成, DEBT=0）· covered=71 / target=1369 (mc≥30) = 5.2% · domain: digital:22 · eda_other:15 · pnr_signoff:21 · verification:13
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=71 / target=1369 = 5.2%（fresh 纯数字候选仍稀缺；本轮从 synopsys-heavy 候选中选出真 formality rtl2rtl 验证任务，verification 域 +1）
- 📦 体积：TASK≈17KB / MEMORY_A≈9KB
- DEBT: 0；BLOCKER: ① fresh 纯数字候选稀缺——daily log tool markers 缺 vcs/verdi/dc_shell/formality/primethe（运维待修），summary.tsv tools 列亦无；本轮改走 synopsys-heavy 关键字筛出真数字/验证任务；② 沙盒 .75 HAS vcs(/apps/synopsys/SRB/vcs/R-2020.12/bin/vcs)+dc_shell+primetime+pt_shell，MISSING verdi/formality/verilint/uvs/vps → formality 类 L2 以 vcs elaboration 为代理；③ 真实设计文件常 permission-denied → 多走 B 档；④ /nasdata 不在 .75 挂载、本机不可直连 .75 → 文件过坝走 eda_flow read_file（text 返 verbatim，zip 走 base64 或本地按 ref 重建）
- 🧾 断言: 今日 1/1 达标（FmRtl2RtlFlow-001：k_rationale=14=k_check=14 ✓，存量断言清单进度 23/30）

## 迁移说明
- 轮 33-42 已归档至 `MEMORY_A_archive.md`（归档批次 50，2026-11-04）。
- 轮 43-49 已归档至 `MEMORY_A_archive.md`（归档批次 55，2026-11-04）。
- 轮 50–57 已归档至 `MEMORY_A_archive.md`（归档批次 56，2026-11-04）。
- 本 MEMORY 为 shard A 独立文件；旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）

## 下一轮第一件事（DEBT=0）
DEBT 已清零。下轮按 `python3 designflow/trace_ledger.py --shard A next --n 5` 选新 trace → claim → 深读 → 合成新 case。**选料前必查重**：`grep <候选 case_id> EDA-Eval-DesignFlow_A.jsonl` + `git log -- benchmarks/EDA-Eval-DesignFlow/assets/<候选 case_id 路径>`，避免重复合成（轮60 教训）。优先覆盖 domain 尚无 case 的纯数字/verification 候选。
