# 深读笔记: 1792551877743_4i1w4 (fernandoy@10.129.8.124 / hfeg0plg76, mc329)

## 来源与复苏
r528 parked 候选 (旧判定 `file-deleted-postscan-r528`)。r820 发现 subdir-path false-negative:
session 文件实际在 `sessions/<sid>/<sid>.messages.json` 子目录, 旧直接路径判定必 NOFILE。
本轮 r821 用 subdir-aware find 证 ALIVE (3016446B/801msgs, mtime Oct 27 17:06), 跨 shard
核验无碰撞 (B/D ledger 无 4i1w4 占用), 遂深读 + 造题。

## 用户与场景
- 用户: fernandoy, host 10.129.8.124 (hfeg0plg76)
- 工程: PIM2 设计验证, `/home/fernandoy/project/pim2/latest/iegoa`
- 环境: VCS (Synopsys R-2020.12) + UVM 1.1, 本地仿真 target `all_uvm_local`
- session 是续作 (首条是 Context summary), 共 20 条真实 user msg, 801 msg total

## 真实任务 (用户原话, 选作造题锚点)
> 我运行 `make all_uvm_local TC_UVM=pu_case1` 结果还是 pu_case0, 请至少跑两个 case 验证一下。

## agent 的排查与真实根因 (trace msg 484-511)
1. 读 Makefile: line 193 `TC_UVM ?= pu_case0`, line 194 `all_uvm_local: clean_uvm_local comp_uvm_local run_uvm_local`, line 230 `./simv +UVM_TESTNAME=$(TC_UVM) ...`
2. agent 推理: `?=` 条件赋值, 命令行 `TC_UVM=pu_case1` 应覆盖; `run_uvm_local` 用 `$(TC_UVM)` 变量, 没写死 → Makefile 变量传递**本身正确**
3. 列 tc/ 目录 (msg 498): 78 个 .sv (pu_case0/pu_both_bank_case/pu_std_intmac_stacc_case/pu_ex_*/pu_mix_*/pu_std_intmac_*/... + regress.py), **无 pu_case1.sv**
4. 真实根因 (msg 499/503/507): **pu_case1.sv 不存在** → `+UVM_TESTNAME=pu_case1` UVM factory 找不到 test → UVM_FATAL (test not found) / 回退默认 → 用户看到"还是 pu_case0"
5. 正确修复: 用真实存在的 case 名 (pu_both_bank_case / pu_std_intmac_stacc_case), 或新建 pu_case1.sv 并注册

## 其他子任务 (本 session, 未选作造题料, 记备查)
- `${root_dir}` 在 VCS .f 文件不展开 → Makefile `export root_dir=$(root_dir)` 修复
- verdi 打开 fsdb "no source file" → filelist 路径问题 → 打平成绝对路径 files_flat.f / +fsdb relpath
- verdi "undefined module" bank2pu_vif/dbg_vif (pu_uvm_top_local.sv line 5,7) → 接口定义未入 filelist
- simv.daidir/csrc 生成到 tb/ 目录而非 case 子目录 → SIM_OUT_U 重定向
- module 版本切换 ds/verdi/2023.12-SP2-3, ds/vcs/2023.12-SP2-3
- README case list 清理

## 姊妹 session
yseg9 (1793092177260_yseg9, 同 fernandoy 同工程, mc343, 836msgs) — 同 context summary,
同 PIM2 UVM env 调试的另一段 (subdir ALIVE 已证, 未碰撞, 留作下轮备料)。

## 造题
- case_id: EDA-Eval-DesignFlow-MakeTcUvmFallbackDiagnose-001
- domain: verification (scan 时标 pnr_signoff 是误判, 实为 UVM/VCS 验证)
- 档: A档 trace-faithful (用真实 Makefile uvm_local 片段 + 真实 tc/ 清单, 用户原话不改写)
- 判分: S5 analysis-Q&A + specificity oracle + refuse-to-hallucinate, k=14/14
- 自验: ref PASS + 4 退化(空壳/echo/coredel/b_leak)全 FAIL + 3 负样本全 FAIL
- B 档并行: QIM3 工程 (qim3_Makefile + qim3_tc_listing), B-only 标识符 qim3/pu_case5/pu_case7/pu_alu_*/pu_dma_burst_case 等, 防背题泄漏
