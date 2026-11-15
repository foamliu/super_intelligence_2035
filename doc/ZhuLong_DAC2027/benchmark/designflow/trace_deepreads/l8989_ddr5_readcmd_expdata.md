# Deepread: 1792548360759_l8989 — DDR5 verilog2seq Read 命令添加 expdata

## trace_source
- session: `1792548360759_l8989`
- user: `tongfanl` @ `hfhds201` (= .75 / 10.129.32.75，trace 直接在本机)
- match_count: 见 scan summary（pool_reaudit_A.tsv 标 mc=n/a，原属 A 域 digital「default (no hard exclusion)」复活候选）
- 真实性: ✅ trace 文件 `/home/tongfanl/.cline/data/sessions/1792548360759_l8989/1792548360759_l8989.messages.json` 实测可读（173785 B / 22 msgs: 13 user + 9 assistant），agent='lead'，updated_at 2026-10-21T02:09:14Z
- 用户原话: 「分析一下抽激励的环境，帮我看下如何给一个Read命令添加expdata值」

## 用户真实意图（任务初衷对齐）
用户在 DDR5 verilog2seq **抽激励（stimulus-extraction）环境**下工作，想理解**如何给一个 Read 命令添加 expdata（expected data，期望数据）值**——即让 Read 命令在驱动 DQ 时把期望数据写进 `dq_exp_fifo`，供后续 `gencompare_expdata` 与 DUT 输出比对。
- 这是 **analysis / capability-Q&A**：用户要的是「看懂怎么加」，不是直接改代码（trace 里 agent 也只读代码+解释，未产出 patch）。
- 按新标准（任务初衷）合法可造；按 r567 方法论属「capability-Q&A 可固化」——把「分析 Read 任务 expdata 接入结构」的能力固化成 Python SV 静态分析器即可写出有牙 check()。纯解释 prose check 被 §4.2 禁止 ⇒ 必须 B 档固化。

## 环境与关键代码（实测来自 .75，私有 /proj，不入 SUT 沙箱）
- 工作根: `/home/tongfanl/dsh_workarea/verilog.ddr5.drcoa.verilog2seq`（DDR5 verilog2seq 抽激励环境）
- 核心文件:
  - `compare_tasks.sv` (1345 行) — 期望数据比对函数
  - `ddr5_test.sv` (11335 行) — ReadBase task 定义
  - `ddr5_interpreter.sv` — CA 命令解码成 `Task: ...` 序列

### expdata 接入结构（Read 命令添加 expdata 的完整链路）
1. **期望数据寄存器** `val` (`reg[MAX_BURST_LEN*DQ_BITS-1:0] val,val_dca,val_crc;`，ddr5_test.sv:3973)
   - 默认值: `if(!proj_voltage_monitors...arrayset) val='0; else val='1;` // "if read without active, dq_exp present default 1" (3976-3977)
2. **从存储阵列加载期望数据** (ddr5_test.sv:4246-4249, 4282-4285, 4303-4304):
   - `val[DQ_BITS*i+7 -: 8] = (mem_arr_wrflag[...][0]==1)?mem_arr[...] : ...` —— 按写标志位 mem_arr_wrflag 从 mem_arr 取期望值
3. **写入期望数据 FIFO** `loaddq_exp_fifo(.rl(rl-1), .bl(bl), .val(val), .termit(termit), .burst_order(col[3:2]), .val_crc(val_crc));` (4261, 4313)
   —— **这就是「给 Read 命令添加 expdata 值」的核心调用**：把 val 推进 dq_exp_fifo，按 RL/BL/burst_order 排布
4. **序列文件输出期望数据** (4324-4337):
   - `seq_exp_data_RD=ddr5.dq_exp_fifo[2*(rl-1)+i][3:0/7:0/15:0]`（按 dqmode X4/X8/X16 取宽）→ `$fwrite(fd_seq,"0x%0Nh ",seq_exp_data_RD)`
   - CRC 期望: `ddr5.dq_exp_fifo[2*rl+16-2] / [2*rl+17-2]`
5. **比对函数** `gencompare_expdata(string data_type, reg dut_data, reg out_data, reg exp_data, reg odt_data)` (compare_tasks.sv:365):
   - 三档主逻辑: out 非 z 且 exp 为 z → out；out/exp 均 z → (odt 为 x? dut : odt)；否则 → exp
   - `case(data_type)` 修饰: `ignorex` / `ignorez` / `ignore0` / `ignore1` / `only01` / `only01z` / `only0z` …（每个修饰改写特定 dut/out/exp 组合下的输出）

### ReadBase task 签名（ddr5_test.sv:3967）
```
task ReadBase(reg[BK_BITS-1:0] ba, reg[BG_BITS-1:0] bg, reg[CID_BITS-1:0] cid=0,
              reg[COL_ADDR_BITS-1:0] col, reg[CA_BITS-1:0] ca_bits='z,
              bit ap=0, bit bc=0, bit dummy=0, bit nt=0, bit drfm=0, bit termit=0,
              int enops=0, reg[2:0] burst_order='z, bit[1:0] ca_comp=2'b00, bit bl32ap=0, bit mppr_x16_fix=0);
```
- RL = `modereg.cl_num` (3992)；BL 默认 16 (4004)；burst_order → col[3:2] (4007-4010)
- `dqmode==X16` 时 col[10] 随机；density==S8G 时 ba 高位清零

## agent 行为（trace 摘要）
1. list_allowed_files → 看到 ddr5_interpreter.sv / dsh_workarea 等
2. search_codebase 因大文件路径过长失败 → 改写 Python 定向搜索脚本
3. expdata_search.py 超时(SIGKILL) → 缩范围 expdata_search2.py（仅顶层文件）→ 命中 compare_tasks.sv:365 gencompare_expdata
4. read_files ddr5_test.sv ReadBase 区段 (4569-4790, 4280-4360)
5. trace 在 msg 21（assistant thinking）截止，未见最终文字答案 —— 用户得到的「交付」是 agent 的代码定位+解释（capability 分析）

## 拟造任务形态（B 档固化，next-round fast-path）
- **case_id 候选**: `ReadExpdataWireAudit-001`（domain=digital, L1-B）
- **任务**: 给定一个 DDR5 风格 verilog2seq Read-task SV 片段（含 ReadBase task + gencompare_expdata 函数 + loaddq_exp_fifo 调用），写一个 Python 静态分析器，解析并报告「Read 命令的 expdata 接入结构」：
  ① 定位 ReadBase task ② 抽期望数据寄存器名(val/dq_exp) ③ 找 loaddq_exp_fifo 调用及其参数(rl/bl/val/burst_order/termit/val_crc) ④ 找 gencompare_expdata 函数及 data_type case 分支集合 ⑤ 判定 expdata 是否被接入 Read（即 Read task 内存在 loaddq_exp_fifo 调用）⑥ 报告 dqmode→位宽映射(X4=4bit/X8=8bit/X16=16bit) ⑦ 报告 seq_exp_data_RD 写序列路径 ⑧ 报告默认期望值规则(arrayset→'0 else '1)
- **check() ≥8 断言**: 在 hidden B（结构/信号名/位宽/dqmode 与 A 全异）上跑候选分析器，断言 JSON 输出结构字段；负样本（空壳/print-only/删核心/hardcoded-A）须 FAIL
- **hidden B 设计**: 用 X8 dqmode、不同 mem_arr/信号名、不同 data_type case 子集（如 only01z + ignore0）、不同 RL/BL，与 A(X16) 全异
- **资产可达性**: ✅ B 档自合成 SV 片段，不依赖私有 /proj（真实结构已在本笔记记录，可合成代表性自包含 SV）

## 判定
- 旧筛子: 未被判 weak（「default (no hard exclusion)」）—— 本就是真实用户意图，非误杀复活，而是 mc≥5 扩池新触达的 fresh 候选
- 新标准: ✅ 可造（capability-Q&A 可固化，B 档资产可达）
- **本轮**: deepread 完成，case 未合成（预算约束，非不可造）→ DEBT: 1 deepread (l8989) 未合成，next-round fast-path（本笔记复用，无需重读 trace）即可交付 ReadExpdataWireAudit-001
