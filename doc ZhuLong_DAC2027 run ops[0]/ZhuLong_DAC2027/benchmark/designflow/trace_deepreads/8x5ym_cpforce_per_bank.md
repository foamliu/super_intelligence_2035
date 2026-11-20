# 8x5ym deepread — CP per-bank 注错使能（gracew @ hfeg0plg92）

## trace 溯源
- session: `1794812335509_8x5ym`，user `gracew`，host `hfeg0plg92`
- mc=159，291 msgs / 1.6MB messages.json，mtime Nov 19 16:50（r804 liveness 实测 ALIVE）
- domain: **verification**（LPDDR5 ddgoa proj_special.sv 的 CP_FORCE 注错 stimulus）
- trace 源文件路径（agent 只读，e0031982 无 r 权限，内容从 trace tool_result 提取）：
  `/rundata/ddgoa/V0/simdir/verilog/qi3wang/verilog.lpddr5.ddgoa.net1105/proj_special.sv`（8155 行）

## 用户意图（verbatim）
- **U0**（msg[0]）：「/rundata/ddgoa/V0/simdir/verilog/qi3wang/verilog.lpddr5.ddgoa.net1105/proj_special.sv 里面的 cpforce 现在是一次性注错所有 bank 的所有 cp，如果现在我想同时看两个 bank，一个 bank 对、一个 bank 错或者两个 bank 错的 cp 不一样应该怎么办」
- **U18**（msg[41]）：「你可以写个完整的出来吗」
- **U20**（msg[61]）：「在现在的基础上将注释转换成英文」

（之后 msg[83]+ 的 Compress_task.v bit14/8/10 优先级是另一独立子任务，不纳入本 case）

## agent 诊断（msg[14]/[16]/[18]/[20]/[30]）
- 生效的 `CP_FORCE` 块 = line 3398–3666 的 `hdl_msa_error_inject` 模块（line 3093 上面那段是注释掉的旧版，别动）。
- `bind` 绑到每个 array section（`msax512_fbcc`/`msax320_fbcc`），即每个 bank 一个实例。
- **根因**：每个实例都用**同一份全局掩码** `` `TOPHIENAME.A_proj_monitors_if.errorinjectmonitors.cp_force[0:35] `` 构建 `fail_cp[]`（line 3558–3563）；注入条件（line 3626/3641 `fail_cp[i]==cpnum`）只比 CP 号，**没用已解析的 bank 信息**（`bg`/`ba` 来自 `I_Array1GBK<0..F>`）。→ 选某 cp 所有 bank 一起错。
- bank 解析：`if(string_find(.source(hie),.target("Array1GBK"),...))begin case({bgba_info[0]}) "0".."F": bg/ba=...; default: bg=100;ba=100; endcase str_uv=...; case(str_uv) "U":uv=0;"V":uv=1; endcase end`
- 注入循环：`for(int i=0;i< `TOPHIENAME...failcp_num;i++)begin ... if(fail_cp[i]==32/34/33/35) for(j...) Yio0_temp[j]=hforce/lforce ... end`

## agent 交付（msg[30] ask_question → 用户选"最小改动" → msg[40]/[60] 完整替换 + msg[82] 英文注释）
用户在 ask_question 4 选项里选「保留全局 cp_force + 新增 bank_force[16] bank 使能掩码，改动最小、向后兼容」。agent 交付 `hdl_msa_error_inject.sv`（写在 /home/gracew，/rundata 对 agent 只读）：
1. **结构体加字段**：`TYPE_CP_FORCE` 加 `bit [15:0] bank_force;`（`bit<bank>=1`→该 bank 注错；`16'h0` 默认→所有 bank 注，旧行为）。
2. **加局部变量**：`int bank_idx; bit got_bank; bit bank_sel_ok;`。
3. **解析本实例 bank + 算门控**（在 bank 解析 case 块内 `got_bank=1;`，块后）：
   `bank_idx = (bg<<2) | ba;`（0..15 = `I_Array1GBK` digit）
   `if(`MACRO.bank_force == 16'h0) bank_sel_ok = 1'b1;`（旧行为）
   `else bank_sel_ok = got_bank && `MACRO.bank_force[bank_idx];`
4. **门控注入循环**：`for(int i=0;i<`MACRO.failcp_num;i++)begin` 后插 `if(!bank_sel_ok) begin $display(...); break; end`。
5. **注释转英文**（U20）：把新加的中文注释全转英文（CJK 行数=0，begin/end 配对 64/64 不变）。

## §5 reframe（produce-task + hidden-B 真跑）
trace 用户要的是「改完的 SV 文件」。为支持隐藏 B（词法不同变体）+ subprocess 真跑判分，reframe 成「交付参数化 Python 改造脚本 `apply_bank_gate.py`，读输入 SV 路径（argv[1]），把上述 5 处 per-bank 使能改动施加到输入上，输出到 stdout」。忠实保留用户意图核心（cp 注错 per-bank 使能 + 注释全英文），泛化成「可对任意同结构不同词法输入复跑」——与 r805 RtlPathSwapProduce-001 同一 §5 范式。

## A / B
- **A**（SUT 可见）：`proj_special_cpforce_A.sv`——trace 真实 CP_FORCE 块裁剪版（module `hdl_msa_error_inject`，宏 `` `TOPHIENAME.A_proj_monitors_if.errorinjectmonitors ``，struct `TYPE_CP_FORCE`，csl_num 默认 128，含 2 行中文注释待转英文）。
- **B**（hidden）：`proj_special_cpforce_B.sv`——结构与 A 完全一致，词法标识符不同（module `hdl_msa_err_inj_b2`，宏 `` `TOPH2.MON_IF.einjmon ``，struct `TYPE_CP_FORCE_B2`，csl_num 默认 80，bind 实例名不同，相同 2 行中文注释）。同 16-bank / 36-cp / `[15:0]` bank_force 宽度。

## case
- case_id: `EDA-Eval-DesignFlow-CpForcePerBank-001`
- domain: verification
- k_check = k_rationale = 15
- ref PASS 15/15 + 5neg 全 FAIL（①⑤⑪⑧⑩ 各命中不同断言证独立）+ §4.9 a/b/c 全 FAIL + e2e（test 字段独立运行）PASS
- judging_paradigm: S5 第三范式 produce-task reframe + B=测试输入
- cases/A/EDA-Eval-DesignFlow-CpForcePerBank-001.json（source of truth）+ assets + reference 落库
- ledger: 8x5ym → status=case

## 备注
- host hfeg0plg92 的 /rundata 对 e0031982 只读权限 denied，原 SV 内容从 trace messages.json 的 read_files tool_result 提取（line-numbered "N | text" 格式）。
- 本 case 的 assets/reference 被 shard B 的 bench-shardB 自动重建（commit 413a048c5, 18:35）以 `git add` 扫入提交（共享工作区 collision，内容=本线最终态，git diff 空）；cases/A/ json 由本线显式提交。
