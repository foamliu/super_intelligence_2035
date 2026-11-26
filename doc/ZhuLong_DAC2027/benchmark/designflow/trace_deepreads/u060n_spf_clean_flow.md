# 深读笔记：1794461300466_u060n（e0046686 @ hfeg0plg49, mc=24）

**domain**: analog_context（SPF/PEX 寄生参数提取流程 + PVT corner 状态跟踪 + 临时文件清理）
**case_id**: EDA-Eval-DesignFlow-SpfCleanFlow-001
**grade**: B（synthesized reframe，trace 末无用户接受产物）
**layer**: L2（候选写 Python 脚本，check.py 在隐藏 B/B2/B3 目录树上真跑）

## trace 摘要

- 33 msgs，agent=lead，sessionId=1794461300466_u060n
- U#0（act 模式）：「按照TASK_CLEAN_SPF_TMP_AND_LOG.md执行」
- assistant 读 TASK_CLEAN_SPF_TMP_AND_LOG.md → 核心需求：
  1. 抽 spf 成功后删除临时文件（中间文件、日志文件），保留脚本/工具/结果文件（netlist、gds）
  2. **关键约束**：每个 PVT 提交集群仿真，上层脚本不监控各 PVT 状态 ⇒ 必须在每个 instance **完全成功后**才清理，否则保留供分析
  3. 要求先形成方案 review 确认后再执行

## assistant 工具链（探索阶段）

1. `list_allowed_files` 项目根目录 → 找到 TASK_CLEAN_SPF_TMP_AND_LOG.md
2. `read_files` TASK_CLEAN_SPF_TMP_AND_LOG.md
3. `list_allowed_files` 参考目录 `peinie/spf_1p/CXN4HC1PS512X17M4B2C1R1W1BW1RE1_FS` + autosim_script
4. `list_allowed_files` 参考 PVT 子目录 `ffgnp_0p75v_125c`
5. `get_agent_policy_status` + `list_allowed_files` netlist_tools
6. `read_files` full_flow.py → 发现 import SpfConfig/process_instance from spf_extractor
7. `list_allowed_files` spf_extractor 包
8. `read_files` spf_extractor.py + spf_status.py → **核心机制**：spf_status.py 通过 job_log.json 跟踪每个 PVT 的 SPF_DONE/SPF_FAIL，instance 级状态在全部 PVT 完成后升为 DONE/FAIL
9. `read_files` spf_extractor.py 中段 + 三个 shell 模板(extract_spf.sh/run_extract_spf.sh/submit_bsub.sh)
10. `read_files` 参考 job_log.json + downstream.sh + `list_allowed_files` tt_0p75v_125c → **关键发现**：参考目录 instance_status=FAIL（ffgnp 失败，3 成功），SPF 结果是 PVT 目录下 `<inst>.dspf`
11. `read_files` spf_extractor.py 280-410 + `run_approved_command`(/dev/stdin → 被 policy 拒)
12. `editor` 写 scan_spf_status.py → 被 policy writableRoots 阻断
13. [32] session 结束（无后续 assistant 输出，无用户接受产物）

## 关键技术点（判分依据）

- **job_log.json 结构**：`{instance, pvts: {pvt_name: {status: "SPF_DONE"|"SPF_FAIL", dspf: path|null}}, instance_status: "DONE"|"FAIL", version}`
- **instance_status 语义**：全部 PVT SPF_DONE ⇒ "DONE"；任一 SPF_FAIL ⇒ "FAIL"
- **清理规则**：仅 instance_status=="DONE" 才删临时文件；FAIL 的 instance 全保留
- **临时文件**：*.tmp, *.log, spf_error.log, .gex/ 目录, .gui/ 目录
- **结果文件（保留）**：*.dspf, *.spf, *.gds, *.netlist, *.sp, *.spi
- **参考目录路径**：`/rundata/lacaa/TV1_FS/simdir/finesim/workdir/peinie/spf_1p/CXN4HC1PS512X17M4B2C1R1W1BW1RE1_FS`

## 为什么 B 档

- trace 末 [32] 无用户接受产物（assistant 被 policy 阻断后 session 终止）⇒ 无金标准 ⇒ 不能做 A 档
- 原 SPF 输出目录在 `/rundata/lacaa/...` 私有路径不可复现 ⇒ 合成目录树

## 合成方案

- **A（可见）**：spf_output.zip → spf_output/，2 instance：CXN4HC1(3 PVT 全成功) + CXN4HC2(2 PVT，1 成功 1 失败)
- **B（隐藏判分）**：spf_output_B/，3 instance：SRAM4KX32(2 PVT 全成功) + RFAMP(1 PVT 全失败) + LDO(3 PVT，2 成功 1 失败) — 名称/值全异于 A 反硬编码
- **B2（退化）**：单 instance 单 PVT 全成功
- **B3（退化）**：空目录无 instance
- **check.py**：14 条件 a-n，含 dry-run 报告验证 + --execute 实际删除验证 + 反硬编码 + 两个退化场景
