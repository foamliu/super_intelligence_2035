# trace_deepread: 2sopo (e0029308 @ hfeg0pkn002, mc=62, hspice:203 dominant)

session: 1794818788622_2sopo / 1794818774473_rs6bc (dup kw)
user: e0029308 (NEW-user, first B case)
host: hfeg0pkn002 (10.129.x, .75 免密可达)
agent: lead
trace: 61 msgs / 211KB (messages.json; archive 25MB 未用)
path base: /proj/lacaa/TV1_DBC_Virtuoso/workdir/e0029308/BK/AI/Auto_Check/

## 7 轮 user intent
1. **[0-17] gui_pipeline.py `_running` 卡死修复**: `cdl验证完全没反应` 根因 = `_on_run_done`(1251) 只禁暂停按钮没复位 `_running` + `_worker_chain` 异常路径(~1141) `except...return` 也没复 `_running` → 某步抛异常后 `_running` 永远 True → 之后点任何按钮都被 `if self._running:` 挡住。修：异常路径 + on_run_done 都加 `self._running=False`。
2. **[18-35] compare_truth_table.py DFF 段 CLC 风格**: 用户要 DFF 判定参照 CLC 结构去驱动/工艺(D1/D2 后缀)、按 cell 类型分组、列具体 cell 名(原来只在差异时给名字)。改 `dff_compare_report`：按类型分组 + 一致/不同清单。实测输出 DFKRPQD1/DFKRPPQD2 等 42 cell/21 类型。
3. **[36-37] 多信号优先级 Q&A**: 方法论——异步复位 RN/R > 异步置位 SN/S > 扫描使能 SE > 数据 D；两两冲突实验法。
4. **[38-53] 4_DFF_Reset_sim.sp 加第3个 .alter**: 用户加 SE=0 + SN/SDN→0(t=0.5) + CD/C→1(t=0.8) 做 set+reset 同时有效(0.8→1.0)优先级冲突。问题：下游 `6_dff_hspice_summary.py` Reset 变体表写死 `[0,1]` 不读第3变体。
5. **[54-57] Reset 旧检查口径解释**: base(.mt0)=复位侧(SN=0.75, CD t=0.5 拉高→Q=0, D=0.75)；alter1(.mt1)=置位侧(CD=0, SN t=0.5 拉低→Q=1, D=0)；5 采样点 b[0..4], >0.4V 判 1；`reset_desc(b,exp_final)` 分类。
6. **[58-59] b[3] 是否用了**: 是，5 点全用：b4!=exp→无; b0!=b1→异步; b1!=b2→下降沿·同步; b2!=b3→上升沿·同步; else→持续。
7. **[60] 新判定口径(最终意图)**: b3 作复位/置位判定位置(对比 b3 vs b0 是否相同)；新增 b3 vs b4 是否跳变判 scan vs set/reset 优先级(跳变=scan 优先级高，反之 set/reset 优先级高)。

## reframe 决策
trace-faithful A 档不可便携(/proj/lacaa 内部路径 + gui_pipeline/compare_truth_table/Hspice_SIM 大量内部脚本 + Virtuoso/HSPICE 实跑依赖)。harness-for-teeth reframe：把用户最终要的判定口径(signal_desc 5 分支 + b3/b0 生效判定 + b3/b4 跳变优先级)抽成参数化 `dff_reset_prio_classify.py`，一次覆盖 trace 后半 reset/priority Q&A 全部真实判定逻辑。asset A = format-faithful(真实 cell 名 + 5 点 0/1 采样 + exp_final_reset=0/exp_final_set=1)。hidden B = 结构性反向(8 cell 全不同名 + 采样值覆盖 5 分支 + 优先级 scan=5/setreset=3 与 A 不同)，反硬编码 A。
