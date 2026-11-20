# r880 deepread — 7ypz6 (dechaoc@hfeg0pkn004, mc=16217, digital/verification)

**session**: 1794829264163_7ypz6 · user dechaoc · host hfeg0pkn004 (10.129.2.13) · 162 msgs · deepseek-v4-flash · ALIVE (messages.json 1.77MB, scp OK)

## 用户真实意图（verbatim, U#1, 唯一实质提问）
`log/cmds_p1_cm_check.x8_9200/xrun.log分析下错误的原因`
单问 debug-Q&A：给一篇 xrun 仿真日志，分析错误原因。

## trace agent 行为
- 在 `/rundata/drcpa/V0/simdir/verilog/dechaoc/verilog.ddr5.drcpa.rundir_name/log/cmds_p1_cm_check.x8_9200/` 定位 xrun.log（89,389 行）
- 写 `analyze_xrun.py` 提取 tail + error/fatal 行
- 报告根因（msg #161）：
  1. **CUVUNF**（数千条）：`xmelab: *E,CUVUNF (./proj_special.sv,2568|73): Hierarchical name component lookup failed for 'TOP' at 'PERI0.I_BCenter.I_BCenterL.I_T_CMLeft_R1.I_T_CmFsLatchX6L_o1037.I_m_CmFsLatchX6L'`，源文件 ./proj_special.sv 行 2568-2841+
  2. **INTERR**：`xrun: *F,INTERR: INTERNAL EXCEPTION`
  3. **signal #11** SIGSEGV：`Unexpected signal #11, program terminated (null)`
  4. exit status 250，工具 xrun(64) 23.09-s003，hostname hfechds010
  5. design hierarchy: Modules 40338/27, Primitives 68240/8, snapshot worklib.AF_Seg:verilog

## 合成（A 档 trace-faithful, produce-task）
- **case_id**: EDA-Eval-DesignFlow-XrunCuvunfSegfaultDiagnose-001
- 交付物 = `analyze_xrun_error.py`（解析 xrun.log 输出结构化 JSON 诊断根因）
- fixture A = `simdir_A/xrun.log`（忠实复刻真实日志错误结构：CUVUNF/INTERR/signal#11/exit250/xrun23.09-s003/proj_special.sv/PERI0.I_BCenter...）
- hidden B = `xrun_B.log`（结构不同：ILLDRV elaboration 失败，无崩溃，exit 1，v24.10-s002，drcpa_top.sv，DDR5TOP.I_PHY.I_DqsCtrl...）judge-only
- check.py 15 断言（动态解析 B 推导 ground-truth，anti-leak 防 A 硬编码）
- 自验：gold PASS 15/15 + 3 neg 全 FAIL（empty/print-A/core-deleted）+ §4.9 三假 FAIL（空zip/print-A/core-del）+ 确定性重跑稳定
- k_check == k_rationale == 15 ≥ 8 硬闸门过
- eda_flow session r880: open → scp 7ypz6 messages.json 1.77MB → parse → declare_done → close cleaned

## 11-21 新全量扫描（r880 重建 driver）
- 重建 `scan_driver.sh`（xargs -P 24 over ssh_auth_ok.txt 698 IP + scan_remote.sh）→ `/home/t0002965/log/ssh_eda_search_20261121_005100/`
- 扫描 58s，5434 行 / 3846 dedup sids（00:51 AM off-hours 仅 43 主机响应，但仍够选料）
- A-domain fresh（未触碰台账）候选 7 条，选 7ypz6（verilog:4915+drc:7104 主导, A 域 digital）
