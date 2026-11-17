# y737t — VCS CFCILFBI separated-library-binding diagnosis · r706 deepread

- **session**: `1792480126204_y737t` · user `e13zhang` @ `hfeg0pgn012` (file on .75 /home/e13zhang) · mc=307
- **size**: 1,231,620 B / 338 msgs / 14 user-text-turns / ~150 tool_uses
- **keywords**: verilog:1403; lvs:698; netlist:73; drc:41; rtl:7; systemverilog:3
- **path**: `/home/e13zhang/.cline/data/sessions/1792480126204_y737t/1792480126204_y737t.messages.json`
- **old parked**: r295 "verilog_lib_trans_v2 tb fix, 3-turn evolved complex task needs xrun+actual files, too complex to parameterize" — 新标准下复活 (debug-Q&A 诊断报告是合法 design_flow 交付)

## 用户轮（14 个，关键 6 个集中在 CFCILFBI 诊断 msg[14]-msg[232]）
1. msg[0]: "怎么在TOP生成一个7.2GHz的时钟" (how-to, 与本题无关, 后续话题)
2. msg[14]: "你帮我看看 .../sim/ 下面的makefile 我先在make compile 一直报 Error-[CFCILFBI] Cannot find cell in liblist ... Cell 'XPIO_CA' cannot be found in liblist for binding" (核心诊断请求)
3. msg[74]: "但是为什么fpga_compile不会报错" (追问 vlogan 不报错)
4. msg[76]: "改了 还是一样的问题 Error-[CFCILFBI] ..." (用户尝试 agent 第一版修复后仍失败 → 推翻假设1)
5. msg[109]: "给你写权限 你帮我改好" (授权 agent 实测 + 修改)
6. msg[233]+: 转入 BUFGCE_DIV / DDR VIP Denali 协议错误 (与本题无关, 后续话题)

## agent 工具链（~90 calls, 集中在 msg[14]-msg[232]）
- list_allowed_files / read_files: 浏览 sim/ 目录, 读 Makefile / cfg.mk / harness_xpio.sv / XPIO_CA.sv / synopsys_sim.setup / compile.log / fpga_vlog.log / Vivado 官方 XPIO_CA.sh
- run_approved_command (shell-runner): 多轮 inspect*.sh 检查 vcs_lib 目录结构、make.vlogan/modfilename.db/work.lib++ 索引、grep _VCSgd_*.db
- editor + run_approved_command: 在 /home/e13zhang/vcstest/ 搭建**最小复现** (XPIO_CA.sv + sub.sv + top.sv + synopsys_sim.setup + run_all.sh / run_nomdir.sh / run_matrix.sh)，**实测 4 种绑定方式**
- editor: 最终修改项目 Makefile (复制到 home → 编辑 → 拷回 /rundata，绕过 policy.writableRoots + 文件只读权限)

## 诊断演进（3 次假设 → 2 次推翻 → 实测钉死）

### 假设1（msg[73]，WRONG）："fpga_compile 只编 XPIO_CA.sv，9 个文件被注释 → 库不完整"
- 证据：Makefile L157-166 显示 9 个 .sv 行首有 `#` 注释；fpga_vlog.log(15:11 历史成功) 显示曾全 10 文件编译
- 用户反馈 msg[76]："改了还是一样" → 推翻

### 假设2（msg[108]，WRONG）："fpga_compile 的 `-Mdir=.../vcs_lib/xil_defaultlib` 指向库目录本身 → 库只有索引(AN.DB/work.lib++)没有本体(_VCSgd_*.db)"
- 证据：库目录 ls 只有 AN.DB/ 和 work.lib++/，无 _VCSgd_*.db / 64/；对比 Vivado 官方脚本无 -Mdir
- agent 实测 msg[130-134]：**去掉 -Mdir 后还是同样错误** → 推翻

### 真根因（msg[138]，CORRECT，实测钉死）："vlogan -work xil_defaultlib + vcs -top -L xil_defaultlib 分离库绑定方式在这个 VCS 流程里根本不会把库 cell 实体化"
- 实测矩阵 msg[137]（4 种绑定方式，最小复现）：
  - A) `vcs top.sv xil_defaultlib.XPIO_CA` → `Error-[SFCOR] Source file cannot be opened` exit=255
  - B) `vcs -top top -L xil_defaultlib top.sv` → `Error-[CFCILFBI] Cannot find cell XPIO_CA` exit=255
  - (无 -Mdir) `vlogan -work xil_defaultlib` + `vcs -top -L` → 同样 CFCILFBI
  - C) **`vcs -top top XPIO_CA.sv sub.sv top.sv` (全部内联) → ✓ compile+elab+link 成功, exit=0, 生成 simvC**
- 结论：vlogan 只写 AN.DB 注册索引，不落盘 _VCSgd_*.db 单元本体；vcs -L 按索引找本体找不到 → CFCILFBI
- 修复 msg[232]：把 10 个 XPIO 源文件**内联进 compile 的 vcs 命令行**（在 $(HARNESS_FILE) 之后追加），不再依赖失效的预编译库

## B档合成（debug-Q&A 诊断脚本）
- **case_id**: EDA-Eval-DesignFlow-VcsCfcilfbiDiagnose-001 (verification, L2-B, k=16)
- **A 档 simdir**（trace-faithful 节选，给 SUT 看）:
  - `Makefile` (L149-169 fpga_compile with -Mdir + 9 commented files; L190-215 compile with -top -L)
  - `compile.log` (CFCILFBI error @ L2173-2182, Cell 'XPIO_CA' cannot be found)
  - `fpga_vlog.log` (vlogan success for all 10 files @ 15:27:21)
  - `vcs_lib_listing.txt` (ls -R vcs_lib/xil_defaultlib: only AN.DB/ + work.lib++, no _VCSgd_*.db)
  - `XPIO_CA.sv` (L110 instantiates submodule XPIO_CA_advanced_io_wizard_v1_0_10)
  - `vivado_official_vcs.sh` (reference: no -Mdir, elaborate xil_defaultlib.XPIO_CA inline)
  - `empirical_matrix.txt` (4-experiment reproduction: A SFCOR / B CFCILFBI / no-Mdir CFCILFBI / C inline ✓)
  - `synopsys_sim.setup` (xil_defaultlib : vcs_lib/xil_defaultlib + OTHERS chain)
  - `task_brief.md`
- **B 档 hidden simdir**（check() 只跑 B，与 A ≥10 维全异）:
  - cell=DDR5PHY_CA (A=XPIO_CA), lib=ddr5_xillib (A=xil_defaultlib), user=alice (A=ethan)
  - project=/rundata/linfeng/V1_digital/... (A=/rundata/lagat/V0_digital/...)
  - harness=harness_ddr5phy.sv (A=harness_xpio.sv), host=hfeg0pgn015 (A=hfeg0pgn012)
  - submodule=DDR5PHY_CA_advanced_io_wizard_v2_0_5 (A=..._v1_0_10)
  - empirical matrix: A SFCOR / B CFCILFBI DDR5PHY_CA / no-Mdir CFCILFBI / C inline ✓ exit=0
  - 10 文件名全异, compile.log error line/file 不同, vlogan timestamp 不同
- **ref**: `analyze_vcs_cfcilfbi.py` (CLI: `python3 analyze_vcs_cfcilfbi.py <simdir>`, 输出 JSON 诊断报告)
  - 解析 Makefile 提取 fpga_compile vlogan 命令 + compile vcs 命令
  - 解析 compile.log 提取 CFCILFBI error (cell name, instance path, liblist, source file:line)
  - 解析 fpga_vlog.log 提取 vlogan 成功的文件列表 + timestamp
  - 解析 vcs_lib_listing.txt 判断库结构 (只有 AN.DB/work.lib++ → index_only=True)
  - 解析 empirical_matrix.txt 提取 4 实验结果 (A/B/no-Mdir/C)
  - 综合判断 failure_class / root_cause / refuted_hypotheses / fix
- **check.py**: 16 断言 (a01-a16), 全独立可 FAIL, B-specific 值全异于 A
- **negatives**: 4/4 全 FAIL (naive_empty / print_expected_A / hardcoded_A / core_deleted)
- **§4.9 三假提交**: 全 FAIL distinct
- k_rationale=16==k_check=16≥8 GATE PASS

## 关联
- e13zhang 用户既有 case: 无 (本 shard 首条 e13zhang)
- 与 r703 XmsimInterrDiagnose / r701 IrunCuvpomDiagnose / r699 XrunTypeerrDiagnose 同类 debug-Q&A 诊断脚本，但**根因类型不同**：本 case 是 lib_binding (separated vlogan+vcs-L 不实体化)，r703 是 tool_crash (INTERNAL EXCEPTION segfault)，r701 是 compile_error (CUVPOM invalid-port)，r699 是 compile_error (TYPEERR)
- 与 r681 Http429Diagnose 不同：r681 是 runtime 429 退避，本 case 是 compile/elaborate 阶段 CFCILFBI
