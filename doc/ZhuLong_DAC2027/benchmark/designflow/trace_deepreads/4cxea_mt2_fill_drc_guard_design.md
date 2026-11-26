# 4cxea — MT2 补孔 DRC-guard 脚本设计（brainstorming → spec）· yan1zh@hfeg0pkn005

- **session**: `1794445063551_4cxea` (yan1zh@10.129.2.14/hfeg0pkn005, mc=68, agent='lead', 57 msgs, 2026-11-12, 248KB)
- **keywords**: drc:360;aether:54;pyaether:36;lvs:29;calibre:20;virtuoso:7
- **历史台账**: r597 (2026-11-15) parked `not-produce (Q&A/brainstorming)` → **2026-11-15 §二 reaudit 复活**（brainstorming/design-spec 类全部恢复为可造）
- **实质任务**: 用户做 MT2 补孔（via landing pad fill）触发 DRC short/错误连接，希望设计一个"自带校验"的补全脚本。
  - U#0 brainstorming skill 启动 → 助手 5 问澄清（错误性质=短路/错误连接；纯版图无 net 信息；MT2 作孔的上层连接焊盘；环境不确定；方案=把 DRC/LVS 纳入补全流程）
  - U#22 "试一试A+B" → 助手三段设计（总体架构/组件划分+判定规则/错误处理+测试）
  - 方案 A = 放置前内联几何检查（mini-DRC 逐孔校验）：R1 已覆盖孔的同层 MT2=同 net 安全合并；R2 附近未覆盖孔的 MT2=疑似异 net，候选焊盘须保持 min_space，放不下就缩小或跳过
  - 方案 B = 补全后定向 DRC 反馈闭环（fill→DRC→自动修正→迭代，max 3 轮）
  - 6 模块：焊盘生成器/预检器/放置决策器/登记表/定向DRC运行器/违规回退器
  - 4 处置：placed / shrunk / skipped / 回退
  - 错误处理 6 场景（DRC 不可用降级 / 解析失败转人工 / 达 max 迭代停止 / 非本脚本引入不动 / 单孔异常跳过 / 关键规则值缺失 fail-fast）
  - 幂等性（登记表去重，重复跑不产重复焊盘）
  - 产物：`/home/yan1zh/docs/superpowers/specs/2026-11-12-mt2-fill-drc-guard-design.md`（152 行 13 章，3 git commit）
  - U#46 "我应该怎么调用这个脚本呢" → 助手澄清现在只有 spec 无脚本，补 §13 调用接口（Aether 交互式框选→菜单→确认→执行→报告）
  - trace 末尾 spec 完整提交（27a1af4）= trace-end-gold（设计规格文档）
- **档 B reframe（A 档不可行）**: A 档 gold = 152 行 free-text markdown spec，check() 在 free-text 上无法做 ≥8 独立断言且 print-only stub 直接打印 spec 即 PASS（违反 §4.3/§4.9）。**抽离可离线复刻的子交付 = 方案 A 内联预检决策引擎 `mt2_fill_decision.py`** = spec §4 决策流程 + R1/R2 判定规则 + 4 处置 + fail-fast + 幂等登记表的真实算法核心。纯 stdlib（rect 几何 + json + sys），输入 `<vias.json> <mt2.json> <config.json>`，逐孔计算候选焊盘→R1 同 net 覆盖判定→R2 异 net 间距判定→placed/shrunk/skipped 处置+冲突登记→确定性 JSON。2026-11-15 §二 recovery：brainstorming/design-spec 类恢复为可造（承 P-006 (C) harness-for-teeth reframe + B r849/r858 范式）。
- **hidden B**: 6 vias + 5 existing MT2，几何全异于 A，含自由放置/同 net 覆盖/可缩小/无空间跳过/重复 via id（幂等）5 种处置路径；config 值不同。
