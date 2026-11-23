# trace_deepread: 1795159586165_1nlsg — AutoSimErrHandlingAudit

- **trace_source**: e0046686 @ hfhds201, session `1795159586165_1nlsg`, mc=89, domain=schematic_netlist (netlist:468/lvs:270/pex:244)
- **file**: `/home/e0046686/.cline/data/sessions/1795159586165_1nlsg/1795159586165_1nlsg.messages.json` (651KB, 59 msgs)
- **date**: 2026-11-20

## 真实用户意图（两轮）

### Turn 1 (msg 0-31): 诊断 autosim 后仿 netlist 生成失败
- 用户粘贴 autosim 界面日志：CDL tiling 生成 `CXN4HC1PS64X16M4B2C1R1W1BW1RE1_FS`，bsub jobid=3483380 提交后 "no running jobs detected"
- agent 读 `submit_bsub.log` 发现 `extract_gds.sh: line 7: cd: None: No such file or directory`
- 读 `extract_gds.sh`：第7行 `cd "None"`、第23行 `python3 None ...`、`--leafcell-gds None` —— 配置全 None
- 读 `spf_extractor_config.json`：**括号不平衡**（7 开 6 闭），`"DBC": {` 闭合后外层 `pex_config` 未闭合，`json.load()` 抛 ValueError
- 读 `spf_config.py:_load_spf_settings`：捕获异常后只 `log_warn` 一句就 `return {}`（静默吞异常）
- 结论：配置全丢 → GdsTilerConfig 查不到 1P 编译器 → script=None/tiler_dir=None → extract_gds.sh 内嵌字面量 None → bsub 必败
- 策略引擎拒绝直接改 AutoSimUni 代码树（只读根），agent 改为产出校验脚本 + 修复后的 JSON 供用户替换；发现文件已被并行修复

### Turn 2 (msg 32-58): 全面排查应报错退出却继续推进的位置
- 用户令："全面排查 AutoSimUni/autosim_script/ 下有哪些地方应该报 error 退出而非继续推进，并给出具体位置和修改建议"
- agent 调 `eda_script_standard` 技能，写扫描脚本对全目录扫裸 except/异常吞/shell 返回值/log_warn 站点/`|| true`
- 扫描 464 处候选，逐一判定确认 **21 处 A 级问题**（必须改报错退出）+ 10 类 B 级
- 完整报告写入 `/home/e0046686/project/autosim_uni/agent_workspace/outputs/error_handling_audit_report.md`
- A 级典型：spf_config.py:209 (json_load_swallow)、spf_extractor.py:60 (import_swallow)、extract_gds.sh (literal None 模板)、各 tiler/pex 配置缺失返回 None 调用方不检查

## 合成决策
- 抽取**静态扫描审计内核**做离线可验证评测（不依赖 autosim 运行时/bsub/沙箱）
- 4 类反模式：except_swallow / json_load_swallow / unchecked_command / shell_error_mask
- 隐藏 B1 (5py+1sh, 4 类全注入) / B2 (4py+1sh, 不同文件名行号结构, 反硬编码) / clean (3py+1sh, 0 误报闸门)
- check.py 12 断言：B1 4 类各≥1 / clean=0 / B2≠B1 位置集 / 确定性 / 改名根稳定性 / B2 4 类各≥1
- 3 负样本 (print_only/core_deleted/hardcode_a) 全 FAIL，reference PASS
- task_id: EDA-Eval-DesignFlow-AutoSimErrHandlingAudit-001, k_check=12, L2 (真 subprocess 在隐藏 B 上跑候选)
