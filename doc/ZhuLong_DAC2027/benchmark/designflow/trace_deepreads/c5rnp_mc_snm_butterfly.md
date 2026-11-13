# Deepread: 1794444643468_c5rnp — e0030760 MC 5000 SRAM SNM butterfly + 算法有效性 bug

> trace_source: user=e0030760, host=hfeg0pkn004, session_file=1794444643468_c5rnp.messages.json, mc=114, match_count_kw=hspice:314;rtl:21;synopsys:12;transistor:4;netlist:4;aether:3
> scp: 1241872 B / 145 msgs (agent=lead, model glm-5.3-flash), 2026-11-12 03:38Z
> 池: 1113 (summary_1113.tsv), fresh r493 (parked r493: szlie/aiusb/lot4l/gx89q/m0ezp/07yj8/55a3n)

## 用户意图（4 轮 user_input）
1. msg0: 「/proj/lacaa/V0/workdir/e0039809/MC_hspice 这个路径下有我根据对应的testbench跑完的5000 次MC的结果，读取这里面的结果」
2. msg39: 「那你修复一下这个脚本，新脚本输出到/home/e0030760路径中」(修 mc_snm_analyzer.py)
3. msg75: 「确认一下，这个脚本是通过计算蝴蝶曲线的内接正方形边长导出来的HSNM和RSNM吧？」
4. msg81: 「再给上面这个py图形化窗口加入一个可以选择某一个MC点，读取其蝴蝶曲线数据并绘制图功能，蝴蝶曲线内内含有最大内接正方形和对应的SNM值」
5. msg128: 「输出的butterfly图内接正方形没在蝴蝶曲线内，测试逻辑是否正确？」⭐ 关键

## 数据结构（HSPICE Monte Carlo, CH252 6T SRAM, FS corner, 25°C, 5000 MC, SRS seed=1, 486 局部变量）
- `FS_CH252.ms0` — 每次仿真 WNML/WNMR/Iread/Ileak (5000 组, 0 fail)
- `FS_CH252.mt0` — Iwrite_peak/Iwrite_avg (5000 组)
- `FS_CH252.mc0` — 486 局部变量 SRS 采样
- `FS_CH252.lis` (381MB) — 5000 组蝶形曲线 → RSNM/HSNM
  - 每个 MC 样本: `vin voltage` 头行 + 4 节点表(q_rnm/qb_rnm/q_hnm/qb_hnm)，各 ~754 行两列(vin, V)，间隔 ~3034 行，总 15,314,880 行
  - ⚠️ 每个样本有**两条** `*** monte carlo index = N ***` 标记：一条在 DC 蝶形段前(~101528 行)，一条在文件末尾瞬态/measure 段前 → 索引若"后者覆盖前者"全错
- `FS_CH252_a0/a1.ava.report` — AVA 统计报告(均值/σ/分位数/敏感性)，用于交叉验证

## agent 工作（多轮 editor + run_approved_command python-runner）
### A. MC 结果解析 (msg1-38)
- 写 `peek_lis.py` 探查 .lis 蝶形表格式 → 写 `mc_lib.py`(SNM 蝶形算法+统计) + `mc_extract.py`/`mc_report.py`/`run_report.py`(主入口, 断点续跑)
- 跑通 5000 样本, 与 AVA 交叉验证一致 (iwrite_avg mean=1.5847e-07 vs AVA 1.584671e-07)
- 关键统计(n=5000): RSNM 0.1583±0.0084, HSNM 0.3351±0.0070, WNM_min 0.2736±0.0153, Iread 25.79µA, Iwrite_peak 49.74µA, Ileak 37.8pA

### B. 修 mc_snm_analyzer.py (msg39-74) — 4 个 bug
1. **整个文件丢失全部缩进** (IndentationError, 无法导入) → 重建 442 行缩进
2. **bootstrap 死锁**: `vin voltage` 表头只在 `st["cur"] is not None` 时识别, 但每个表头出现时无打开的表 → 状态机永不启动, 0 样本 → 去掉前置条件
3. `messagebror`→`messagebox.showerror` 笔误
4. `calc_stats`/`calc_sigma` 用 `np` 但 numpy 只在 run_gui/selftest_run 局部导入 → 补 import

### C. SNM 算法确认 (msg75-80)
- 写 `confirm_snm.py` 用独立 O(n²) 暴力枚举内接正方形 vs 脚本二分搜索
- 蝶形构造: 左曲线=(vin, V(Q)); 右曲线=QB 曲线横纵轴互换(镜像到 y=x 对称); SNM=两曲线间最大内接正方形(边平行坐标轴)边长
- 实现: 公共栅格算垂直间距 |A(x)-B(x)|, 二分搜索边长 s(14 次), 单调队列维护滑窗最小值 O(n) 判定
- 验证: RSNM 0.151576 vs 暴力 0.151792 (差 0.22mV=1mV 步长量化误差), HSNM 0.330322 vs 0.330000

### D. GUI 蝶形绘图 + 索引 (msg81-127)
- 顶栏加 MC sample 输入框 + plot butterfly 按钮
- 一次性索引: 扫 381MB .lis (9.7s) 建 样本号→字节偏移 映射, 缓存 .lis.butterfly_index (带文件大小校验)
- 按需 seek 读取, 单样本 5ms
- 修两个坑: ① 两条 monte carlo 标记(只 q_rnm 后才提交索引) ② 慢路径 bytes/str 比较失效

### E. ⭐ 内接正方形几何有效性 bug (msg128-145) — 最独特的子技能
- 用户: 「输出的butterfly图内接正方形没在蝴蝶曲线内，测试逻辑是否正确？」
- agent 诊断: `snm_square` 假设"间距最小点(pinch)在窗口右端、正方形向左延伸"(上瓣构造), 但当窗口落在**下瓣(A<B)**或曲线局部非单调时, 正方形画到曲线外 (sample 1048 HSNM 正方形 y0+s=0.757>VDD, x0=-0.0107)
- `debug_square.py` 量化: 旧正方形在**所有样本**上都穿越曲线(70~355 个违例点), 真值内接正方形比旧值**小 10~24mV** → 系统性 bug
- 根因(msg140-145): **Q(vin) 和 QB(vin) 是几乎相同的下降曲线**(VTC 及其镜像配置的测量), 蝶形图=VTC vs 自身镜像。两条曲线都下降时, 旧的"逐点垂直间距"算法**在数学上不成立**(找到的窗口不能保证正方形内接)
- ⚠️ session 在 msg142 (dump_curve2.py) 处结束, **未给出修复后的正确算法** — 这是 open end

## 与既有 case 的关系 (P-004 dup-risk 评估)
- e0030760 既有 SNM/butterfly case: SramSNM-001(f0vya, butterfly-SNM 子任务), ButterflyCurve-001(gnmu0, 蝶形曲线 max inscribed square=SNM, VTC), SramButterfly-001(sram_butterfly.py CLI)
- **核心技能重叠**: 都计算"蝶形曲线最大内接正方形=SNM" → 高 dup 风险
- **可能区分角度**: c5rnp 的独特处是 **几何有效性 bug** — 朴素垂直间距法在两条下降 VTC 曲线下产生**落在曲线外**的内接正方形(系统性, 真值小 10-24mV)。既有 case 是"正确生成/计算 SNM", 本 case 是"诊断+修正 SNM 算法的几何无效性" — debug-correct vs generate, 方向相反
- **判定**: dup 风险中-高。若做, 必须在 prompt + test_rationale 明确区分: deliverable = `snm_square_validator.py` (给定蝶形曲线, 计算 SNM 且**验证内接正方形几何包含性**, 拒绝朴素垂直间距法的越界输出), check.py 断言"正方形四角在两曲线之间"非仅 SNM 数值
- **未决**: 是否值得做 vs 接受 e0030760 SNM 域饱和。需下一轮裁定

## 下一步建议
- 若做 c5rnp: B 档合成, deliverable=snm 几何有效性校验器, L2, k≥10 断言(SNM 值 + 正方形四角包含 + 拒绝越界 + 3 随机种子 + B≠B2)
- 若不做: park c5rnp (e0030760 SNM 域饱和), 走 post-1113 daily-log 路径找新 spice produce-task
