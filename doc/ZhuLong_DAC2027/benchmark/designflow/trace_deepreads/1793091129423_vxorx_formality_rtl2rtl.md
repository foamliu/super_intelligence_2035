# Trace deepread — 1793091129423_vxorx (e0046913 / hfeg0pkn003, mc=64)

- **domain**: verification (Synopsys Formality RTL2RTL)
- **opening user turn (verbatim, A-faithful)**: 「在当前/rundata/lacaa/TV1_digital/simdir/yutingq 目录下，参考feint文件内的formality相关脚本，为我在fm_r2r目录下开发rtl2rtl功能，并使用ref_verilog和imp_verilog中的test案例去跑通。」
- **真实资产**: feint/{scripts/fm.tcl, Makefile, setup/common_setup.tcl}（formality 参考模板）; fm_r2r/{ref_verilog/E902_asic_rtl.f(88行), imp_verilog/E902_asic_rtl.f(89行)}; ref/imp filelist 仅 line 45 异：ref 含 `cr_ifu_ibuf.v`，imp 含 `cr_ifu_ibuf_r2rQA1.v`+`cr_ifu_ibuf_r2rQA2.v`。
- **关键产物 (assistant)**:
  - 深析 QA 模块：QA1 = golden `cr_ifu_ibuf` 去掉调试输出 `ifu_iu_ex_inst[31:0]` 及 `pop1_inst` 逻辑 → 功能等价（排除该口即 PASS，88 比较点）；QA2 大幅裁剪端口/逻辑 → 非等价。
  - `fm_r2r/scripts/fm_r2r.tcl`：env-driven rtl2rtl 流程（FM_R2R_REF_F/IMP_F/REF_TOP/IMP_TOPS/DONT_VERIFY_REF），read ref→set_top r→set_dont_verify_points（wildcard -type port，**双引号非大括号**否则 Tcl 不替换变量）→read imp→遍历 IMP_TOPS match/verify→PASS/FAIL 图案。
  - `run_fm_r2r.sh`：**unset LD_PRELOAD**（agent eda_agent libstdc++ 污染致 fm_shell GLIBCXX_3.4.29 not found）+ fm_shell -f。
  - 4 case：qa1/qa2/one2two→FAIL，pass（QA1+dont_verify ifu_iu_ex_inst）→PASS（88 compare points SUCCEEDED）。
- **fm_shell**: V-2023.12-SP5 (hfeg0pkn003)，需 `unset LD_PRELOAD LD_LIBRARY_PATH` 后可启动。
- **top**: E902 CPU 顶层（cr_ifu_top 实例化 ibuf），模块级 rtl2rtl 比较。
- **reframe for benchmark**: 沙盒 .75 MISSING formality，real E902 RTL 不可达/体积大 → 用结构同构小自含 verilog 对（A: 8-bit 计数器 cnt_unit/cnt_unit_impl+cnt_dbg; B: 4-bit 仲裁器 arb_unit/arb_unit_impl+arb_dbg）承载相同 rtl2rtl + dont_verify 机制；L2 以候选 `run_fm_r2r.sh --check-rtl` 真跑 vcs elaboration 在 B 上为代理（留 simv 击穿 print-stub），formality TCL 本体静态判分。
- **case**: EDA-Eval-DesignFlow-FmRtl2RtlFlow-001 (verification, L2, A-faithful, 14 conds a-n).
