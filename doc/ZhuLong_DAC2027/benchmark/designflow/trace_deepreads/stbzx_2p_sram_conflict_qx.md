# 深读笔记：stbzx — 2P SRAM 同地址读写冲突 Q≠X 诊断+修复

- **trace**: `1793092577390_stbzx` · user=lorikx · host=hfeg0pkn001 · mc=167 · 247 msgs / 1.37MB
- **agent**: lead (glm-5.3-flash); policy-engine enforcing (python-runner / shell-runner profiles)
- **workdir**: `/home/lorikx/MY_SANDBOX/TV1_Model/verification/sram2p_conflict_addr_test_1`
- **scan kw(col6)**: `rtl:203;verilog:131;synopsys:107;vhdl:9;systemverilog:9;waveview:7;synthesis:2;cadence:1` → 强 digital/verification
- **选轮**: USER#0 提出 Q=X 需求（clean A-faithful，未给根因/修复）；USER#79=「可以把报告放到文件里吗」

## USER#0 原话（A-faithful 任务说明）
> 目前该目录下的仿真被反馈有问题：2p同一地址同时读写的情况，Q应该是X
> 从3500ps开始，读写同时使能，但是Q并不是X,请按找下面的表格要求检查问题出在哪了（uvm_sram_2p/rtl/），
> [Write-Port/Read-Port/AW/AR/DA/Q/Memory State 真值表三行]
> 由于测试的是例化文件，可以修改并调试改正代码，然后总结如何修改，我会用你的反馈内容去修改model文件

## 关键文件
- `uvm_sram_2p/rtl/CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_DBC_CH378L.v` (3851 行, memory compiler 模型, gen2prf.py 生成) — **实际编译的 model**
- `..._WRAP.v` — 顶层 wrap（bypass + Q 输出门）
- `sp_2pram_functional.sv` / `sram2p_wrap.sv` — 未参与编译（干扰项）
- TB/scoreboard/monitor/seq/test lib + Makefile + filelist (sram2p_verify_top.f 只编 CH378L+WRAP)
- 实例参数: CENTER_DECODE=1 → 走 `gen_cd`(CD 模式)分支（非 gen_sd）

## 工具链（真跑商业 EDA = L3）
1. read_files/list_allowed_files 读 RTL + log + filelist + scoreboard/monitor/seq/test
2. **VCS V-2023.12-SP2-3 编译+运行**（`/apps/synopsys/SRB/vcs/...`，license 已配）
   - 本地基线复现 bug：不带 debug → 首拍 Q=旧数据 111 / 带debug_access → 172/200 CONFLICT MISMATCH Q=222
   - 同一根因不同表象 = **delta 竞争 nondeterminism** 的实证
3. **FSDB 波形** → `fsdb2vcd` (verdi_2023.12) → VCD 解析（自写 extract_vcd.py）
   - 取证：@4500 拍 CLKW/CLKR posedge 同 sim 时刻不同 delta，`Q_force_x` 全程=0（冲突分支从未触发）
4. `ifdef CONFLICT_DEBUG` 调试打印 + pristine 对照树（.orig_bak）证明 exception_test 误报是既有问题
5. 12-test 全量回归（regress）

## 根因（双重，经波形逐拍取证）
**根因#1 模型 bug（主因）**: 主时钟块 `cd_main_clk`/`sd_main_clk` 用**同一次 always 执行内**的 `clkw_edged` flag 判冲突：
`rw_conflict = clkw_edged && (WEB_buf===0) && (REB_buf===0) && (AW_buf===AR_buf)`
但 CLKW/CLKR 是两个独立网络，posedge 落在同一 sim 时刻的**不同 delta** → CLKR delta 执行时 `clkw_edged` 已被清/未置 → 冲突漏检 → `Q_r <= mem[AR]` 读到刚写入的新数据。三种 VCS 调度（2020.12 / 2023.12 ±debug_access）三种表象，全指向同一 delta 竞争。

**根因#2 WRAP Q-clear bug**: `assign Q = bypass_mode ? D : (~REB ? Q_array : 'd0);` — REB=1 时 Q 清 0，违反规格表第 3 行（Write/No Access → Q=Q-1 保持）。导致 exception_test 边界拍 `AR=03ff Q=0 expect=0x3ff` 误报（pristine 对照证实是既有问题）。

**根因#3 monitor 采样时基混合**: `sram2p_rd_monitor` AR/REB 用 `cbr_mon`（沿前 #1step），WEB/AW/D 用 `vif` 直接采样（沿后 50ps）→ 边界拍冲突分类与 DUT 错位一相位。

## 修复（移植到 model 模板的部分，SD/CD 两分支都改）
**读侧冲突判据**: 用「本仿真时刻是否发生过 CLKW posedge」替代 delta-dependent flag：
```
last_clkw_rise <= $realtime;   // 每次 CLKW posedge 记时间戳
...
rw_conflict = (WEB_buf===0) && (REB_buf===0) && (AW_buf===AR_buf)
              && (^AW_buf !== 1'bx) && (AW_buf < DEPTH)
              && (clkw_edged || (last_clkw_rise == $realtime));  // 时间戳兜底，delta-independent
if (rw_conflict) Q_r <= {WIDTH{1'bx}};   // X-drive 保留
```
**写侧 backstop**: `... || (last_clkr_rise == $realtime)`（对称）
**real 比较**: `===`→`==`（real 无 x/z，语义等价，消 warning）
**WRAP 修复**: `assign Q = bypass_mode ? D : Q_array;`（Q 无条件保持，不清 0）
**monitor 修复**: WEB/AW/D 也从 `cbr_mon` 沿前采样（一致性）
**自恢复**: 冲突后 `Q_force_x` 清 0 逻辑保留

## 验证（USER#2 接受的结果 = 金标准）
- 修复前基线: CONFLICT MISMATCH=172 / CONFLICT OK=28（带 debug）
- 修复后: **CONFLICT MISMATCH=0 / CONFLICT OK=200**（200 拍冲突全 Q=X），UVM_ERROR=0
- 全量 12-test 回归 **12/12 PASS**（smoke/random/dual/mask/bypass/disable/boundary/uninit/conflict/conflict_addr/exception/stress）
- 产物: `MODEL_FIX.diff` + `CONFLICT_QX_BUG_REPORT.md`（6 章: 现象/根因/修复/验证/复现/遗留）
- USER#2「报告放到文件」→ assistant 写 CONFLICT_QX_BUG_REPORT.md → USER 无后续（隐式接受）

## 合成决策
- 真模型 3851 行 + 真 VCS 仿真对 SUT 太重（license/时长）→ **B档 synthesized**
- 合成 minimal repro：单一 always 块 + delta-dependent `clkw_edged` 冲突判据 + WRAP Q-clear bug
- 交付：`fix_2p_conflict.py <in_v> <out_v> <report.json>`（静态修复脚本）
- check.py 静态断言 fix 模式（$realtime 时间戳 / 去delta依赖 / WRAP Q-hold / X-drive保留 / 反硬编A），subprocess 真跑候选于 hidden B
- L1-static（无真 VCS，纯 python 静态分析）；domain=verification；track=A-faithful（prompt=USER#0 逐字）
