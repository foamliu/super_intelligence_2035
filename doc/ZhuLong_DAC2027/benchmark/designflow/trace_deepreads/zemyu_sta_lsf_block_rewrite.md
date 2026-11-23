# trace_deepreads — zemyu (PrimeTime STA LSF 提交块改写)

- **session**: 1795420804448_zemyu.messages.json
- **user/host**: e0046913 @ hfeg0pkn005 (10.129.2.14)
- **mc**: 56, keywords: pt_shell:257 / netlist:184 / rtl:69 / primetime:61 / synopsys:28 / verilog:4
- **domain**: A-pure pnr_signoff (PrimeTime STA)
- **msgs**: 71 (3 轮 Q&A + 1 produce + 2 STA 评估)
- **shard**: A → case `EDA-Eval-DesignFlow-StaLsfBlockRewriteProduce-001` (r1091)

## 用户意图流（trace 原话）

### U#0 (act) — LSF 跑不通诊断
> 在 /proj/lacaa/TV1_digital/simdir/yutingq/CxDP/1123-copy-from1118-for-pass/sta/run 此目录下，任务可以通过 "make common CXDP_STA_RUN_MODE=direct"(本地运行任务)顺利跑通，而无法使用"make common"跑通（使用LSF队列），报错显示为："[CXDP] analysis_lib.f: .../DBCP51H180L6W25T5_BASE_LVT_ssgnp_typical_v0p675_0c_ccs.db ..."

助手深读 Makefile + pt_shell_command.log + lsf_*.out：**LSF 作业 3934332 其实跑完了（pt_shell exit status = 0，作业在 hfeg0pgn022 上完整跑完）**，根因不是队列/挂载，而是 PrimeTime 读到的 SDC 约束文件不存在 → 时序分析"空跑"。

### U#19 (act) — 问改 LSF 提交写法的好处
> 把 STA 的 LSF 提交改成 FM 那种"整条命令进远端"写法有什么好处？

助手对比 STA（脆：环境在提交机搭 + `-env ALL` 拷贝 + pt_shell 裸起相对路径）vs FM（稳：整条命令作为字符串交远端 shell 执行 + `bsub -Is`）。

### U#21 (act) — produce: 生成只改 LSF 的 Makefile
> 不要直接改我的文件，而是在/home目录生成一份"把 STA 的 LSF 提交改成 FM 那种'整条命令进远端'写法"的Makefile文件（只改动LSF设置，其他地方不要动）。

助手第一版用 `-K`（submit-and-wait）+ 整条命令进远端字符串。

### U#34 (act) — 关键转折：不满意，两点修正
> 我对你的改动并不满意，原因在于：1.我想和FM提命令的方式一致，包括使用交互式界面-Is（-K选项是什么意思？有什么必要吗？），并和在本地跑任务存入同样的log，而不是专门生成lsf的log。2.我不需要保留lsf模式下冗余的run_pt那句指令module purge && module load，该删定的地方需要删。请再次修改/home目录的Makefile。

助手二次改写：
1. `bsub -Is`（交互式，对齐 FM，`-K` 没必要因为 `-Is` 本身同步且返回退出码）
2. `tee $(PT_LOG)` 挪进远端命令内部，日志写进和本地同款 `sta_*.log`，不再单独 `lsf_*.out/.err`
3. `run_pt` 删掉冗余 `module purge && module load`（已挪进 STA_LAUNCH）
4. 修 `$$` 转义（editor 把 `$$` 塌成 `$`，用 fix_make.py 修复）

最终 diff 确认只动 LSF 块 + run_pt 两 hunk，其余 473 行与原始一致。

### U#49/63 (act) — 评估 STA 结果
> /proj/lacaa/.../sta/all_out/v1.0_Latest 评估本次STA结果

助手发现目录是 ≥3 次运行混合体（17:16/17:20/17:31 时间戳），后 17:37 重新干净跑一遍：PASS（setup 全通过，blackbox_count=0，分析覆盖率正常）。

## 最终 produce 意图（U#21 + U#34 合成）

把 CXDP STA Makefile 的 LSF 提交块从「裸起 pt_shell + `-env ALL` + `-K` + 分裂日志」改写成 FM 风格：
- `bsub -Is -q ... -J ... "整条远端命令"`
- 整条远端命令 = `module purge && module load $(MODULE_PA) && module load $(MODULE_LC) && cd $(CURDIR) && $(PT_CMD) 2>&1 | tee $(PT_LOG)`
- else (direct) 分支跑同样内核命令（无 bsub），统一日志
- run_pt 删冗余 module/cd/管道 tee，`PIPESTATUS` → `$$?`
- `$$` 转义保留
- 其余行逐行不变

## case 构造

- **A 资产**: Makefile_A（cla_top / ssgnp_v0p675_0c / cxdp_sta，合成自含 CXDP STA Makefile，~110 行，结构忠于真实 trace Makefile 的 LSF 块 + run_pt 区）
- **hidden-B**: Makefile_B（pcie_top / ff_v1p1_125c / pcie_sta / ds/pt/2024.12-SP1 / sta_run_pcie.tcl，同结构零 A token 相交）
- **reference**: rewrite_lsf_block.py（通用结构化 rewriter：定位 `ifeq($(CXDP_STA_RUN_MODE),lsf)` 块 + `run_pt:` target，替换 LSF/direct 分支 + 清理 run_pt recipe，仅用 make 变量引用不硬编码值）
- **check**: 22 条独立断言（zip+py_compile+B 运行 + LSF -Is/-K/-env ALL/lsf log + 整条命令字符串 + run_pt module/cd/tee/PIPESTATUS + $$ 转义 + 其余行 byte-identical + 反硬编码 A + B 值保留 + 确定性 3x + direct 分支统一）
- **negatives**: empty / print-only-A-hardcoded / copy-unchanged，全 FAIL
- **自验**: ref PASS 22/22 + §4.9 三假 FAIL + neg_selftest OK + standalone check.py PASS
