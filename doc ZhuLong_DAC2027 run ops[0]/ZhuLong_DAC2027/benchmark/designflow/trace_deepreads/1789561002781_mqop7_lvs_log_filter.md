# Deepread — 1789561002781_mqop7 (ziyuny / hfeg0plg91, mc=466)

**Domain**: physical_verify (Argus LVS log 问题排查) — shard C
**Session**: 102 msgs, 1.0 MB messages.json
**Case built**: EDA-Eval-DesignFlow-LVSLogFilter-001 (L1-boundary, B-档 synthesized)

## 用户意图流
1. msg0: 「将工作目录转到 /home/ziyuny/lvsdebug」(setup)
2. msg9/msg17: 「精读 /home/ziyuny/lvsdebug/lvs_log_notes.md」(学习)
3. msg22: 「精读 /home/ziyuny/lvsdebug/argus-lvs-log-analysis.md」(学习 LVS log 格式)
4. **msg42 (真目标轮)**: 「根据前面学习到的 argus lvs log 文件知识，你到 /proj/drgqa/V0/ver/lvs_argus/drgqa_cmos_top 的所有 lvs 结果进行筛选，对所有的 argusLVS.log 文件做读取和分析，如果有以下情况，就把 lvs 结果筛选出来给我，并且记录在一个文档中，汇总所有有问题的 lvs 结果。1.莫名中断的 lvs 结果 2.跑了很久没跑出来的结果，卡在某一步很长时间点结果 3.有 power ground short 的结果 4.有很多 pin error 的结果，一个错误导致 log 中写入一堆错误信息，超过上万个 pin（可以看下 argusLVS.log 文件的大小，进行一个初步的判断）」
5. msg91: refinement — 编辑 argus-lvs-log-analysis.md (PVE 相关 log 不用看；PENDING operations 含义更正：不是堆积而是并发子任务数)

## assistant 工具链
- list_allowed_files 探 /proj/drgqa/.../drgqa_cmos_top (policy engine 重映射 /proj→/rundata)
- 抽样 Array16G_T/BCenter/DDR5TOP/Channel_x 子目录结构 → 每个 subdir 直接含 argusLVS.log
- search_codebase 找关键模式（受限只搜 15 文件，弃用）
- 批量 head 行数探测 (99800/149900/199800) 判日志大小级别
- 读取 99800 行处内容判 NE vs SVS 阶段
- 读 lvs.rep.shorts 确认 power/ground short (BCenter: vddq!-vdpg!; Channel_x: vcc!-vss!)
- NE 进度 = CMD n/total；PENDING ops 计数；REAL TIME 累计秒
- 写 lvs_problematic_results.md (244 行，6 节：扫描概况/4 类问题/优先级排序 P0-P3/无 log 目录/分析方法/已确认结果)

## 用户接受产物 (msg90)
`/home/ziyuny/lvsdebug/lvs_problematic_results.md` — 4 类分类汇总：
- 分类1 莫名中断: BCenter 系列 12 个 (99800+ 行仍 NE, CMD 44-75%)
- 分类2 卡住: Channel_wl2 (7%/140s/206 PENDING), Channel_z0120 (4%/70s/213), DDR5TOP_X (26%/240s/18.9GB OOM)
- 分类3 PG short: BCenter (vddq!-vdpg!, PASS 但 short), Channel_x (vcc!-vss!, FAIL)
- 分类4 pin error>万: Channel_x (~149983 行, >10万错误), DDR5TOP 系列 (cdns_subMaster 风暴), DDR5TOP_why1213 (HCELL AG_VblhRBiasUnit 13440 实例)

## 关键 log marker (来自 argus-lvs-log-analysis.md)
- NE: `argus -ne -hier lvs.pvrs`, `---- CMD n(sub) OPERATION START/FINISHED`, `REAL TIME = t`, `AND N PENDING OPERATIONS`, `TOTAL NE COMMANDS = N`, `MEM = a/b/c/dM`
- SVS: `Empyrean Argus SVS`, `HCELL name (N)`, `cdns_subMaster`, `BEGIN COMPARING LAYOUT AND SOURCE`
- verdict: `Done: LVS PASS.` / `Done: LVS FAIL.`
- 末尾: `============================end============================`；其后可附加 PVE viewer 段落 (`pve -port ... -viewer aether`)，**分析时以 end 标记为界忽略**
- 异常退出: `**Error: An error occurred.` + end 标记（无 verdict）

## L2 阻塞
/proj/drgqa 与 /rundata/drgqa 在 .75 sandbox 对 e0031982 均 Permission denied（仅 ziyuny 的 policy-engine agent 可读）。→ L1-boundary 占位：合成 argusLVS.log（faithful marker），捕获 4 类分类子任务。

## 资产合成
- A: lvs_runs/ 11 子目录（clean PASS/FAIL, interrupted ×2, stuck ×2, pg_short ×2, pin_error ×2, multi short+pin ×1）
- hidden B: lvs_runs_B 11 子目录（Bcell_* 不相交名, anti-hardcode, 同分布不同 count）+ B2 6-cell 子集
- log 行数控制: int/stuck <2000 行(不触发 pin_error 阈值), pin/multi >2000 行
- shorts 文件: lvs.rep.shorts 含 `netA - netB` 条目

## 判分
check.py 16 labels (a)-(p)，k_rationale=k_check=16>=8 GATE PASS。ref 16/16 PASS；5 fakes 全 FAIL (NEG_RC=0)。
