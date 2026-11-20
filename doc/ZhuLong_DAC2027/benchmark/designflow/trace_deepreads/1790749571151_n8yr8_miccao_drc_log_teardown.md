# trace_deepreads/1790749571151_n8yr8_miccao_drc_log_teardown.md — r383 deepread

## meta
- session: `1790749571151_n8yr8`（miccao @ hfeg0pnd007 / 10.129.32.46，mc=185，physical_verify / Calibre DRC-H log 拆解）
- model: glm-5.3-flash，cwd `/home/miccao`
- status: idle（09-07 → 09-30），~202 msgs
- title: # Calibre/Argus DRC Log 拆解报告
- 档位：**B-档 synthesized**（用户提供完整 workflow spec，非 A-档「只提需求」）

## 用户意图（逐字原文）
U#1（提供完整 workflow spec）：
> # Calibre/Argus DRC Log 拆解报告
> ## 元数据
> - **类型**: Workflow
> - **适用场景**: 拿到一个 Calibre DRC-H 或 Argus DRC 的运行 log（通常名为 `rundrc.log`），需要拆解这次 job 的时间花在哪里、为什么慢、可优化什么。
> ## 目标与边界
> **目标**：对一份 DRC 运行 log 做完整拆解，产出一份**四模块简化报告**：
> 1. 各大步骤时间占比总结（总耗时、核数、各模块 REAL TIME 与占比、cumulative 各操作类别总开销分布）
> 2. 连接关系建立时间总结（每次 CONNECT 的 REAL TIME / NETS / EPINS、cumulative 总计；冗余建立则指出）
> 3. 图形计算部分（Top-15 操作、HGC/FGC/VHC 统计、hierarchy 失效判断）
> 4. 优化建议

U#2-U#4：「继续」「你什么时候能做完？」「继续啊」（agent 编辑工具反复丢失 path 参数，卡在写报告末段）

## assistant 工具链 + 关键产物
1. 构建 bash+awk 脚本序列（drc_ops2.sh → drc_ops5.sh → drc_final.sh → drc_last.sh）解析 DRC log
2. 提取中间文件：_ops_top40.txt（Top-40 ops by REAL）、_rule_summary_sorted.txt、_vhc_stats.txt、_heavy_stats.txt、_connect_windows.txt、_src_layers.txt、_deck_rules.txt、_log_rules.txt
3. 关键发现：
   - 总耗时 REAL 49,433s / CPU 553,032s / 64 核，利用率 17.5%
   - CONNECT 34,182s = 69.1% 墙钟（第一瓶颈）
   - PDK_FB_PCA_TOUCH_M0A 花 16,629s + CONNECT 4,998s，结果 0
   - Close_VIA 系列 STEP 迭代导致 FGC 爆炸（3.4 亿）
   - 3,013 (HIER) ops 中 VHC=F 2,829 (93.9%)
4. write_report.sh 写出报告主体（DRC_Log_Analysis_WOWTOP_B2B_0907.txt，164 行 / 13.8KB）
5. 编辑工具反复丢失 path 参数（~30+ 次失败），最终用 shell 脚本写报告绕过

## gold 产物
- `/home/miccao/zl/rep/DRC_Log_Analysis_WOWTOP_B2B_0907.txt`（164 行，4 模块完整报告）
- 14 个中间证据文件（_ops_top40.txt 等，可复核）
- 原始 DRC log 权限不可读（/rundata/drvsa/.../rundrc.log，193,412 行 / 12.2MB）

## case 合成（DRCLogTeardown-001）
- 从报告引用的 log 行 + 中间数据合成 rundrc_log_A.txt（~75 行关键摘录，含 MODULE COMPLETED / Cumulative / CONNECT windows / (HIER) ops / RuleCheck COMPLETED / TOTAL）
- hidden B：不同 DRC run（32 核 / 32,000s / 8 CONNECT / 1 DISCONNECT / 不同 top ops / VHC=F 1720）
- check.py 12 条件 (a-l)：zip 含报告 / 4 模块标记 / 总 REAL / CPU 利用率 / CONNECT 总 REAL / CONNECT % / top-1 op 名 / top-1 REAL / VHC=F / CONNECT 窗口数 / DISCONNECT 数 / 总 rules
- ref PASS 12/12，3 neg（empty/print_expected/core_deleted）全 FAIL

## 访问方式发现
- 10.129.32.x 子网主机 session 文件在 **子目录** `<sid>/<sid>.messages.json`（非平铺）
- 10.129.2.x 子网 NFS automount 仍坏（ls 可见 cat 失败）
- n8yr8 在 10.129.32.46（miccao）可经 ssh cat 读取（子目录结构）
