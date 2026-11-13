# Deepread · 1794467464751_xsocp · DDR4 DQ FinalDrv Ron/cio_leakage 电路优化

- **trace**: `1794467464751_xsocp` · user=clarawu · host=hfeg0pkn003(10.129.2.12) · mc=310 · 域=spice_sim/characterization
- **source**: post-1109 daily-log 候选（`cand_post1109_r484.tsv`，4-shard ledger+main jsonl 三式去重后 fresh）
- **session**: 目录格式 `sessions/1794467464751_xsocp/1794467464751_xsocp.messages.json`（967KB, 242 msgs: 126 user / 116 assistant）
- **scp**: 经 .75 ssh 10.129.2.12 scp 到 workdir 成功（注意：candidate file 里 session_file 路径缺子目录，需 `find` 定位目录格式路径）

## 用户意图（原话）
- U0/U1: 「我有网表：@.../sim_DqFinalDrv_Ron_cio_leakage_versionD/.../netlist_delvto，学习激励：@.../stimulus_Ron.sp, stimulus_cio.sp, stimulus_leakage.sp, run, extract_all.py，@.../versionC/.../analyze_ron_smoothness.py。**帮我优化电路，使得到的 Ron 曲线 .../wv_Ron/Ron.md0, Ron#1.md0 能够穿过 230ohm 的水平线，并且曲线必须保证单调性，尽量光滑，即残差尽量小。CIO 也尽量小。**」
- U99: 「在这个版本 .../netlist_delvto 基础上优化，**保证 Ron 曲线线性度、光滑度、PVT 下都能穿过 230ohm 的情况下，优化 CIO、mismatch**」

## agent 工具链（L3 迭代优化）
- read_files: 读 netlist_delvto / stimulus_Ron.sp / stimulus_cio.sp / stimulus_leakage.sp / extract_all.py / analyze_ron_smoothness.py / Ron.md0 波形结果
- editor: 改 netlist（调器件参数 W/L/派生器件以调 Ron）
- run_approved_command: 跑 hspiceD 仿真 + extract_all.py 提取 Ron/CIO 曲线 + analyze_ron_smoothness.py 算单调性/光滑度残差
- 循环 ~30+ 次 editor→run_approved_command（A5-A115）：每轮改 netlist → 跑 sim → 查 Ron 是否穿过 230ohm + 单调 + 光滑 + CIO 小

## 资产依赖（A 档可行性）
- 全部输入在 `/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_DqFinalDrv_Ron_cio_leakage_versionD/` — **/proj 对 e0031982 权限拒绝**（A 档 trace-faithful 不可行，同 D r570 asset-unreachable）
- netlist_delvto / stimulus_{Ron,cio,leakage}.sp / extract_all.py / analyze_ron_smoothness.py / Ron.md0 均未在 trace tool_result 持久化正文（cline 清空），须 B 档合成

## B 档合成评估
- **deliverable 候选**: (1) 参数化 Ron 曲线分析与目标拟合脚本（给定 netlist 参数 + Ron 测量点，识别调参方向使 Ron≈230ohm + 单调 + 光滑）; (2) Ron 单调性/光滑度残差评估器（解析 .md0 测量数据，输出单调违例数 + 残差 + 是否穿 230ohm）
- **判分**: check.py subprocess 真跑 candidate 脚本于 hidden B（不同 DQ driver 参数集 + Ron 测量点），验证 (a) 穿 230ohm 判定正确 (b) 单调违例计数正确 (c) 光滑度残差计算正确 (d) 调参方向建议与 oracle 一致 — ≥8 断言可行
- **难度**: L2（脚本执行 + 结构断言，非真跑 hspice）— 因 /proj 不可达 + hspice license，退化为「分析/评估器」deliverable 而非「真改 netlist 跑 sim」
- **风险**: netlist + stimulus + extract 逻辑须从 trace assistant 文字描述合成（tool_result 已清空），合成保真度依赖 assistant 的解释文字量；若 assistant 多为 editor diff 无解释，B 档合成依据薄

## 下轮决策
- **优先合成路线**: 选 deliverable (2) Ron 曲线评估器（单调性 + 光滑度残差 + 穿 230ohm 判定）— 自包含、check.py 可纯 Python subprocess 判分、不依赖 hspice。需补看 assistant 文字描述确认 Ron.md0 格式 + extract_all.py 逻辑。
- **若 assistant 解释文字薄**: park 为 L3-asset-dependent（同 D r570 族），回退选更简单 produce-task 候选（如 jp83r 修目录格式路径后重 peek，或 w8jus/5qw2u）
- **DEBT**: 1（deepread 完成，下轮第一件事合成 case 或 park 决策，非连续深读）

## 候选池状态
- 1109 池 mc10.fresh(B)=0（mc-matrix 实测：pool=777/touched=777/fresh=0，src=summary_1109.tsv）
- post-1109 daily-log 候选 183 个（r481 扫描），r482-r487 消耗 7，余 ~176
- 本轮 peek 2: jp83r（NFS stale handle, 文件列表可见但 stat/cat 失败, 未 claim）/ xsocp（目录格式路径, scp 成功, 本 deepread）
