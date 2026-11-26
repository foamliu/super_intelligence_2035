# trace_deepread: 1792215882223_qv6pl — WaveView ACE 批量波形分析 skill 构建

- **trace**: adaml @ hfeg0pkn001, session 1792215882223_qv6pl, glm-5.3-flash, 337 msgs, status=completed/exit 0.
- **真实任务**: 用户先给 `waveview-fsdb-reader` skill 全文 + WaveView 手册 (`/apps/synopsys/wv/T-2022.06-SP1/doc/wv_docs/index.htm`)，要求"基于 ACE command 编写 Waveview TCL script，实现自动化批量波形分析" → 新建 `waveview-ace-batch` skill。agent 产 SKILL.md (14.7KB) + wv_ace_batch.py (54.8KB) + cheatsheet + 5 TCL 模板。
- **关键用户轮**:
  - msg[0] 初始建 skill
  - **msg[162] (提出需求/目标，A 档候选)**: "这个目录下有tr0的波形文件，尝试用这个skill验证一下，要求提取所有toggle波形的tr/tf" — 用真实 HSPICE tr0 验证 skill，提取所有 toggle 波形的 tr/tf。
  - msg[232] "总结验证过程，更新skill"
  - msg[263] "学习 /home/adaml/WVSrcipts/ 下的 ace TCL 脚本，进一步优化"
  - msg[290]/[293] "继续之前没有完成的工作"
- **真实产物**: wv_ace_batch.py（生成 ACE TCL：measurements/equations/edge scans/eye metrics/waveform export；单/多文件；bsub wv_queue 或直跑；parse_results 按 by_file 分组）+ SKILL.md + cheatsheet + 4-5 TCL 模板。在真实 HSPICE tr0 (m2701 DDR4 hold testbench) 上验证 tr/tf 提取。
- **不可移植部分**: 真实流用 CXMT foundry tr0 (/proj/m2701/...) + Synopsys WaveView (wv -ace_no_gui, license 12000@hl04..) + LSF wv_queue — .75 无 wv license/二进制，foundry tr0 不可读。
- **可复现子技能 (本 case 取的)**: msg[162] 的核心——从 HSPICE `.tr0`（`.option post=2` ASCII 固定宽格式）批量提取所有 toggle 电压信号的 tr(10-90%)/tf(90-10%)，逐边测量。该子技能不依赖 wv，可在 .75 用 hspice 产 tr0 + 纯 python 解析复现。
- **真实陷阱（烤进 case）**:
  1. `.tr0` 首 4 字符 = nvars；信号名 8 字符定长截断（`v(vdd_net`→`v(vdd_ne`，无闭合括号；`v(0`=地）；`$&%#` 数据标记；数据 14 字符定宽浮点折行拼接（行宽≠nvars×14，必须正则扫，不能按行 split）；`0.1000000E+31`=1e31 结束哨兵。
  2. tr/tf 必须用**实际摆幅** swing=voh-vol 算 10/90% 阈值（不能假设 nominal vdd）；逐边**线性插值**（不能取最近样本，10p 步长 + 50p 沿 → 最近样本偏 ~10p）。
  3. toggle 判定须同时有上升+下降沿；排除电流 `i(`、地 `v(0`、静态 vdd。
- **distinctness vs 既有 case**: 已有 WaveView-002（FSDB signal query via wv）、WvEdgeTiming-001（从预提取波形点算 edge stats）、WaveSig-001（hierarchy signals）。本 case 独特点 = **HSPICE .tr0 二进制/ASCII 格式解析** + hspice 再生 tr0（L2）+ tr/tf 10-90，tr0 格式解析是 WvEdgeTiming 未覆盖的子技能。
- **去向**: EDA-Eval-DesignFlow-Tr0TrTfMeas-001 (spice_sim, B档 synthesized, L2, track faithful)。
