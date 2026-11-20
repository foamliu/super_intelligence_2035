# Deepread: 1794465241456_ua9tu (clarawu / hfeg0pkn003 / mc29)

## 用户原话（trace-faithful）
> 写一个python脚本，从 @.../wv_Ron/Ron.md0 中获得关于 rpu_50 和 rpd_50 随 zqdec 变化的曲线的光滑度

后续: "把这个脚本复制到 .../stimulus_file/ 路径下"

## 会话概览
- 53 msgs, 29 user msgs, 215KB, dir-format (sessions/<slug>/<slug>.messages.json)
- 环境: python 3.7.1, numpy 1.21.6, matplotlib 3.5.1
- 可读根: /rundata/m2701/.../wv_Ron/ (FineSim 输出) + /home/clarawu
- 产物: analyze_ron_smoothness.py (11811 bytes, sha256 a433f31d...)

## agent 工作流
1. list_dir → 发现 Ron.md0 + Ron_*.log + Ron_*.md0
2. probe env (python/numpy/matplotlib 版本)
3. 写 analyze_ron_smoothness.py (分 4 段 edit: parse_md0 + get_xy + analyze + make_report + plot)
4. 首跑 FAIL: ValueError "未找到列头(index 行)" — parse_md0 找不到 header
5. 修 parser (改 header 识别逻辑) → 重跑 PASS
6. 输出报告: rpu_50 64点 zqdec 0..63 124.87..266.21 Ohm, 2 非单调跳变(15→16,47→48), dR min=-6.270 max=0.470 mean=-2.243 std=1.398, 二阶差分 rms=1.4223
7. 改 plot label 中文→英文
8. 用户要求复制脚本到项目目录 → cp 完成

## 脚本核心算法（从 trace tool_result diff 还原）
### parse_md0(path)
- 找 header 行（含列名的 "index" 行）
- 收集后续所有数值 token（**对折行鲁棒**：不按行切，按 token 流收集后按 header 长度切块）
- 返回 (headers, rows)

### get_xy(path, col_x, col_y)
- 调 parse_md0，按列名取 x/y 列

### analyze(x, y, label) → dict
- n, xrange, yrange
- 相邻步长 d[i]=y[i+1]-y[i]: min/max/mean/std
- 最大步长占均值比例
- 二阶差分（局部毛刺）: rms
- 单调性: 期望随 zqdec 增大单调下降，非单调跳变次数 + 位置

### make_report(path, ru, rd) → 文本报告
### 曲线拟合: 1/(a+b·z) 模型
### matplotlib 绘图

## A 档可行性
🚫 不可行: .md0 在 /rundata/m2701/... (项目目录, e0031982 权限拒绝, ssh cat 实测 Permission denied)
⇒ **B 档**: 合成忠实 .md0 (FineSim 格式, zqdec/rpu_50/rpd_50, 折行, 非单调跳变) + hidden B (不同点数/值/跳变位置)

## B 档合成计划
- Input A: Ron_A.md0 (64点, zqdec 0..63, rpu_50 266→125, 2跳变) + manifest_A + task_context.md
- Hidden B: Ron_B.md0 (48点, zqdec 0..47, rpu_50 240→100, 3跳变, 不同折行) + manifest_B
- reference: ron_smoothness_analyzer.py (parse_md0 token-collection + smoothness metrics + JSON report)
- check.py: 13 断言 (subprocess 真跑 B + 独立复算 各指标 + A≠B + 3seed + 退化)
- negative: naive_grep / hardcoded_A / always_smooth / negative_selftest

## mcguard
- clarawu 新用户, 0 既有 case ⇒ P-004 无风险
- archetype: .md0 measurement 解析 + smoothness 指标计算 (区别于既有 Mt0MeasureStat/McLisSnmExtractor: 那些是 .mt0/.lis 解析, 本 case 是 .md0 + smoothness/monotonicity 专项)
