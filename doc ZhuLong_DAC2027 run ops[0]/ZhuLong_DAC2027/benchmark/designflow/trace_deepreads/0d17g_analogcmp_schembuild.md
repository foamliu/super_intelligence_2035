# 深读 0d17g — xxchen @ hfeg0pkn002 (mc=393)

- session: `1791851758041_0d17g.messages.json` (目录式 `/home/xxchen/.cline/data/sessions/1791851758041_0d17g/`)
- 规模: 299 msgs / 165 user turns / 134 assistant turns
- 项目: QA Pattern Tool v0.3, `/home/xxchen/workspace/DRC_pattern_tool/0.3/device_rule1`
- 工具关键词: dbCreateRect(43) / cellview(3) / dbCreatePath(1)（首条 user msg 上下文）；session 偏 SKILL/gdspy 脚本 + PCell 批次转换
- 用户首轮: 「续接备注 — skill_pcell 批次转换（25/28，density_upon_step 记录更新中）… 坐标对齐 GRID 0.0001µm … 单元命名 {good|bad}_{QACELL}_{L1}_{L2} … 标准验证三步：离线脚本 → 全工具 → gdspy GDS 检查」
- 性质: **resume / skill-authoring**（续接 PCell 批次转换 + density_upon_step 记录），非 clean produce；属 DRC pattern 工具开发（physical_verify/skill 边界）
- 取用: B-grade synthesized — 取其「程序化 cell 生成 + 坐标/命名规范 + 三步验证」技术，合成 spec-driven **模拟原理图构建** case（AnalogCmpSchemBuild-001，schematic_netlist），mock 录制 stub 离线判分；不直接复刻 DRC pattern（避免与 QaLibCellBuild-001 重复）
- 选取原因: fresh mc>=30 D-domain 候选池 clean schematic_netlist/waveform produce 稀缺（多为 layout/powerfill/rscalc=shard C 或 debug/resume），0d17g 为 fresh（台账未动过）且含 cell 生成技术
