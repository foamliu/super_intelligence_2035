# Deep-read: 5q6uq (eva1li@hfeg0pgn145, mc112) — LPDDR6 lp6tb PreEM monitor analysis-Q&A

**session**: 1794882719879_5q6uq.messages.json · **user**: eva1li · **host**: hfeg0pgn145
**trace**: 598KB / 106 msgs · **keywords**: verilog:427;netlist:362;lib.defs:29;rtl:10;analog:5;binary:3;synopsys:1 (A-pure verification)
**scp path fix (r970)**: `.75` session files live in subdir `<ts_sid>/<ts_sid>.messages.json`, not flat. Used `ssh find -name '*5q6uq*'` to locate, then scp from `/home/eva1li/.cline/data/sessions/1794882719879_5q6uq/`.

## 5 clean user turns

- **U#1**: 「将@/rundata/.../1103_lp6tb/coverage 下的*_cov都列出来并描述它们的功能」
  → coverage 目录无 `*_cov` 文件，实际是 lpddr6_covergroup.sv 里 6 个 covergroup (CMD_JUMP_cov/SAME_CMD_BG_BA_cov/DIFF_CMD_BG_BA_CROSS_cov/REG_RW_cov/REG_RW_field_cov/CK_t_speed_grade_cov) + lpddr6_intf_sample.sv 里 SVA cover property (tXXX_cov 时序覆盖 18 个)。
- **U#2**: 「查找 link_ecc_log/link_ecc.link_ecc.x24/A_compare.rpt 的打印 `---link_ecc-----4b4g` 在哪里打出来的」
- **U#3**: 「PREEM 的monitor在哪里」
  → proj_monitors.sv 宏 `PREEM_COMPARE_DECLARE` (L1270-1343) + 4 实例 pupreem0/1/pdpreem0/1 (L1408-1462)，实例层级 `TOP.Chip.channelif.projmonitors.preemmonitors.*`；proj_special.sv TYPE_PREEM(L188)+preemmonitors 实例(L340)+DqOutTopM6IP bind(L5565)。
- **U#4** (本 case 提炼源): 「ref_rdqst_pdpre0_rdqst_exp是从哪里来的」
  → 5 步数据流链路 (见下)。
- **U#5**: 「DqOutTopM6IP的绝对路径是什么」
  → DUT netlist 中定义: `/rundata/.../netlist/V0_LP6TOP_2026Oct26.185525/netlist` L653600 `// Cell: DqOutTopM6IP`, L653607 `module DqOutTopM6IP (...)`, L654142 `endmodule`。bind 目标，非 testbench 文件。

## U#4 trace gold (本 case 核心)

**5 步数据流链路 (ref_rdqst_pdpre0_rdqst_exp → MA_Pre_PDDS_RDQS_t)**:

① **信号名生成** — `PREEM_COMPARE_DECLARE(TOP...preemmonitors.pdpreem0, pdpre0_rdqst, ref_rdqst, negedge, (14*rdqst_index+12), 0, 50, 0, 2)` @ proj_monitors.sv:1436
   - TRIG_SIG=ref_rdqst, PREEM_NAME=pdpre0_rdqst → 生成 `ref_rdqst_pdpre0_rdqst_exp`
   - 宏内 `ref_rdqst_pdpre0_rdqst_exp = exp_pdpre0_rdqst[TB_IDX]` @ L1290

② **期望数组赋值** — `exp_pdpre0_rdqst = exp_preem_val(.preem_mr(prepd_status),.preem_sel(0))` @ proj_monitors.sv:1429

③ **exp_preem_val 函数** @ proj_monitors.sv:1258-1264
   ```
   function reg exp_preem_val(reg[1:0] preem_mr=0, bit preem_sel=0);
       preem_bit = (preem_sel==0)?preem_mr[0]:preem_mr[1];
       exp_preem_val = preem_bit;
   ```
   - preem_sel=0 → exp = prepd_status[0] (bit0)

④ **status 赋值** — `prepd_status=get_prepd_rdqst_status()` @ proj_monitors.sv:1425

⑤ **get_prepd_rdqst_status 函数** @ lpddr6_tasks.sv:12726-12755
   ```
   function reg[1:0] get_prepd_rdqst_status(integer dutmr=3, integer rank=0);
       case(mrselect)
         'd0: modereg = dutconfig.mr[rankint][MA_Pre_PDDS_RDQS_t];
         'd1: modereg = dutconfig.mr1[rankint][MA_Pre_PDDS_RDQS_t];
         'd2: modereg = dutconfig.mr2[rankint][MA_Pre_PDDS_RDQS_t];
       endcase
       case(modereg & OP_Pre_PDDS_RDQS_t_BITS)
         OP_Pre_PDDS_RDQS_t_DIS:    ...=0;
         OP_Pre_PDDS_RDQS_t_Weak:   ...=1;
         OP_Pre_PDDS_RDQS_t_Middle: ...=2;
         OP_Pre_PDDS_RDQS_t_Strong: ...=3;
       endcase
   ```
   - **根源 = 模式寄存器字段 `MA_Pre_PDDS_RDQS_t`** (RDQS_t 下拉预驱强度)
   - mrselect 由 get_fsop 选择 (dutmr 0/1/2 对应 mr/mr1/mr2)

## 命名规律 (本 case 提炼的通用模式)

- preem_name `<pd|pu>pre<0|1>_<trig>`: pd=prepd(下拉), pu=prepu(上拉); 尾数 0/1 = preem_sel
- trig_sig `ref_<rdqst|rdqsc|dq>`: 被监控的 strobe
- MR field `MA_Pre_P<D|U>DS_<TRIG>`: PDDS=下拉, PUDS=上拉; TRIG ∈ {RDQS_t, RDQS_c, DQ}
- 完整链: PREEM_COMPARE_DECLARE 宏 → exp_<preem_name> = exp_preem_val(.preem_mr(<status>_status),.preem_sel(N)) → exp_preem_val 取 bit[N] → <status>_status = get_pre<pd|pu>_<trig>_status() → 函数读 dutconfig.mr[...][MA_Pre_P<D|U>DS_<TRIG>], case DIS/Weak/Middle/Strong→0/1/2/3

## 同 session 其他可造子任务 (未入库，备查)

- U#1 covergroup 枚举 (6 covergroup + 18 SVA 时序覆盖) — 可造 analysis-Q&A
- U#3 PREEM monitor 定位 (宏+实例层级+bind) — 可造 analysis-Q&A
- U#5 DqOutTopM6IP netlist 定位 — 可造 analysis-Q&A

## 选料注

- mc≥10 池 (shard_mc.A=10), _a_dom_cands_r963.tsv 420 A-domain 候选 × 4-shard ledger (4156 sids) 交叉得 46 fresh
- 5q6uq (eva1li mc112, verilog:427 主导 A-pure verification) 选中
- 与 r954 vgj4f (同用户 eva1li, lp6tb errforce/sc_int/mrr_expf analysis-Q&A) **无 intent-dup**: 不同 session 不同子任务 (U#4 PreEM 数据流溯源 vs r954 errforce ECC 错误注入分析)
- scp 路径修正沿用 r970 发现 (session 文件在子目录 `<ts_sid>/` 下)
