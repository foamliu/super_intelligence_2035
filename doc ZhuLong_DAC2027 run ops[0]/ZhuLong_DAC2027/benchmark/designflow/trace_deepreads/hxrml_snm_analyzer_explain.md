# Deepread: hxrml — mc_snm_analyzer.py 逻辑讲解

- session: 1794461037123_hxrml.messages.json
- user: e0030760 @ hfeg0pkn004
- mc: 28 (spice_sim)
- 形态: explain/介绍 Q&A → 结构化讲解报告
- 12 msgs / 119KB / 1 substantive user turn
- trace 在子目录 `1794461037123_hxrml/` 下 (非根 .messages.json)

## 用户原话 (msg 0)
`/proj/lacaa/V0/workdir/e0039809/MC_hspice/HD_FS_CH252_6T/ttg_25T_0.75V/mc_snm_analyzer.py 这个脚本处理HSNM、RSNM，和统计结果的逻辑是什么？分别在做什么？`

## agent 工具链
1. read_files mc_snm_analyzer.py (默认范围, 截断到 L92)
2. read_files L93-400 + L400-681 (核心逻辑)
3. read_files L182-324 + L478-600 (补两段截断: snm_square/索引构建 + GUI 统计显示)
4. list_allowed_files 目录 (depth 1) → 确认配套: CH252_FS_6T_SRAM_single_Bitcell.sp / FS_CH252.ms0 / FS_CH252.lis / .snm_cache.csv / .butterfly_index
5. read_files FS_CH252.ms0 头6行 + snm_cache.csv 头3行 + butterfly_index 头5行 (核对数据格式)
6. 最终结构化讲解报告 (3615 字, 9 节)

## 真实脚本 (mc_snm_analyzer.py, 761 行, 从 trace read_files 结果 verbatim 还原)
完整 761 行已重建到 assets/EDA-Eval-DesignFlow-SnmAnalyzerExplain-001/doc/mc_snm_analyzer.py。

### 关键结构 (用于造题的 ground truth)
- `NODES = ("q_rnm","qb_rnm","q_hnm","qb_hnm")` — 4 节点
- `PARAMS = ["WNML","WNMR","WNM_min","RSNM","HSNM","Iread","Ileak","log_Ileak"]` — 8 可统计参数
- `phi(x)=0.5*erfc(-x/sqrt(2))`; `phi_inv(p)`: ±12 区间 80 次二分
- `interp(xs,ys,x)` — 线性插值
- `max_square(ad,xs)` — 14 次二分 + 单调 deque 滑窗最小值, 求最大内接正方形边长
- `snm_butterfly(vin,q_free_l,qb_free_r)` — Seevinck SNM: 镜像曲线 + 公共网格插值 + 垂直距离 ad + max_square
- `parse_ms0(path)` — 解 .ms0 (列: index wnml wnmr iread ileak log_ileak temper alter#)
- `extract_snm_from_lis(path,...)` — 逐行状态机: "vin...voltage" 列头 → pend → NODES 行 → 开表收 (vin,V(node)) 两列 → 下一个列头+q_rnm已存在 → flush() 算 RSNM(q_rnm/qb_rnm)+HSNM(q_hnm/qb_hnm)。关键 bugfix: 列头在任何状态下都能触发 (旧代码只在 cur 非空时识别 → 0 samples)
- `snm_square(vin,q_free_l,qb_free_r)` — 同 snm_butterfly 但额外返回正方形几何 (x0,y0,side)
- `build_lis_index(path,...)` — 8MB 块扫, "monte carlo index=N" 标记 → 字节偏移映射, 只提交后跟 q_rnm 表的标记 (排除 transient/measure 区无表标记)
- `save_index_file`/`load_index_file` — 缓存 .butterfly_index, 用 `# lis_size` 校验
- `read_butterfly_at(path,offset)` — seek 到偏移毫秒级解析 4 张表
- `calc_stats(a)` — n/mean/median/std(ddof=1)/min/max/skew(三阶标准化矩)/kurt(四阶-3, 超额峰度); numpy 局部导入
- `calc_sigma(a,smin,smax)` — normal sigma=(mean-spec)/std; violations=count(arr<spec); yield=1-nv/n; quantile sigma=phi_inv(nv/n); 0 违例 → 检测极限 phi_inv(1/n)
- `selftest_run` — --selftest N 无 GUI 打印统计
- `run_gui` — Tkinter: 左参数列表 / 中 60-bin 直方图+正态拟合+spec 竖线 / 右统计+sigma 文本框; 后台 daemon 线程解析, root.after 回主线程
- `main()` — 不带参时 cwd glob *.ms0/*.lis
- 文件头 4 个已修复 bug: ①列头识别死锁(0 samples) ②缩进丢失(IndentationError) ③messagebror 拼写 ④np 未模块级导入(NameError)

## 数据文件样本 (msg 10)
- FS_CH252.ms0: `$DATA1 SOURCE='PrimeSim HSPICE' ...` + 列 `index wnml wnmr iread ileak log_ileak temper alter#`
- snm_cache.csv: `RSNM,HSNM` 头 + `1.5157e-01,3.3032e-01` 等
- butterfly_index: `# lis_size 381190679` + `1 1964082` (sample→offset)

## A 档不可行性
真实 trace 纯代码阅读 Q&A, 用户只要"理解脚本逻辑", 无文件产物交付。→ B 档 synthesized: 造「读脚本产结构化 JSON 讲解报告」生成器, hidden B 换变体脚本反背题。

## 拟造 case
EDA-Eval-DesignFlow-SnmAnalyzerExplain-001 (spice_sim L1 离线 SRAM SNM 分析器脚本结构化讲解报告生成器, B档)
- A = doc/mc_snm_analyzer.py (真实 761 行 verbatim) + task_spec.json (9 顶层键 schema)
- hidden B = hidden/doc/mc_snm_analyzer_v2.py (合成变体: 换节点名 q_read/qb_read/q_hold/qb_hold, 换参数表, 换二分次数 20, 换直方图 bin 50, 换 phi_inv ±10/100, 换数据源 .mt0, 换统计字段, 换 fixed-bugs) + task_spec + hidden_manifest
- check: 9 字段 cross-input guard (每字段从 B 源码独立重解析真值逐字段比对) + A-leak guard + 真跑 + 确定性 + 4 假提交回归
