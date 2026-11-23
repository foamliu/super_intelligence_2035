# r1089 wvtff 深读 — HSPICE G5CIP characterization sweep runner + watch

## trace 来源
- session: `1795341648818_wvtff` (weiyue @ hfeg0plg78, mc471)
- scan: ssh_eda_search_20261123_064315 (Nov 23 06:49)
- cross-4-shard ledger dedup: NONE ✓ (true fresh — r1088 误报 fresh 池耗尽因 cross-shard dedup 过期)
- domain: spice_sim (shard B) — hspice:1447 netlist:307 纯 HSPICE characterization
- msgs: 542 archive + 125 active = 667 total, 2.26MB archive + 0.39MB active

## 用户真实意图（trace msg 流）
weiyue 在开发/调试一个 HSPICE device characterization sweep runner `run_cells.py`（G5CIP platform，每器件 14364 AC points + 3564 DC points，bsub 提交 hspice）。核心诉求演进：
1. **磁盘空间管理**（msg 0-80）：G5CIP_result 目录重复、磁盘满、DC/AC 网表占空间、迁移到 /proj/train/V0/workdir/weiyue/Simulation/Hspice/
2. **目录结构**（msg 91-142）：Hspice/weiyue 之间套 Simulation 层；版本化结果文件夹 `00_streams_<version>/`、`01_streams_<version>/`（多次仿真自增 NN_）；log 替代 README.md
3. **run all / watch / stop 命令**（msg 126-460）：
   - `run all` nohup 后台跑，终端只打印 pid+log 指针
   - `watch` 命令：单行实时进度（\r 原地更新，不刷屏），显示 `{netlist=X/Y} {submit=X/Y} {sim(done)=X/Y} | current=<dev> finished=<dev1,dev2,...>`
   - `stop`（停 orchestrator，bsub job 继续跑）/ `stop kill`（bkill 释放集群）
   - Ctrl-C 只停 watch，仿真继续
4. **仿真顺序**（msg 166）：width↑ → length↑ → Vg↑ → temp(-40,25,98) → corner(ss,tt,ff)
5. **per-device 参数摘要**（msg 272-345）：stop 后 log 记录已完成器件 + 每器件参数（W/L/temps/corners/Vg/Vdd）
6. **watch 进化**（msg 459-568）：v1→v12，解决 \r 被转成换行（ocrnl）、单行不滚动、显示 finished devices（不截断 ntn_lvio→ntn_lvi bug 修复）、全屏 clear-redraw
7. **对齐数据**（msg 534-626）：仿真完一器件产生对齐数据；ntn 对齐失败排查（error.log）

## 关键产物（scp 自 hfeg0plg78:/home/weiyue/Simulation/Hspice/）
- `run_cells.py` (55KB, 1228 行)：主 sweep 引擎
  - `_prog` dict: {current, phase, step, done[], work_root, paramd{}} — Ctrl-C 摘要
  - `_PP` dict: live progress snapshot for watch
  - `_save_progress()`: 写 `.progress` 文件（key=value，sorted keys，节流 0.3s）
  - `gen_ac_netlists` / `gen_dc_netlists`: `_PP.update(current=dev, phase='netlist', net='AC %d/%d'%(j,n))`
  - `submit_wait_chunked`: `_PP.update(phase='submit', sub='%d/%d'%(submitted,total), sim='%d/%d'%(shown,total))`，打印 `dev submit=X/Y  done=X/Y`
  - device banner: `print('\n\033[1m=== {} ({} / {}) ===\033[0m'.format(name, polarity, thick))`
  - 完成器件: `_prog['done'].append(name); _PP['done']=','.join(_prog['done'])`
  - extract: `_PP.update(phase='extract result', extract='AC %d/%d'%(i,_tot))`
- `watch` (bash, 1.9KB)：读 `.progress` + log，渲染单行/3 行进度
  - find_log(): 找最新 run_*.log（.current_log 指针 + glob）
  - 读 .progress: current/phase/net/sub/sim/done/extract (sed -n 's/^key=//p')
  - 渲染: `[watch] current : <cur>` + `phase : <ph> netlist=<net> submit=<sub> sim(done)=<sim>` + `finished: <done>`
- `run` (bash, 2.5KB)：nohup 后台启动 + auto exec watch
- `stop` (bash, 1.7KB)：stop / stop kill
- `readme_bsub.md` (3KB)：命令速查

## `.progress` 文件格式（run_cells.py _save_progress）
```
current=<device>
done=<dev1,dev2,...>
extract=<AC X/Y | DC X/Y>    # 仅 extract result 阶段
net=<AC X/Y | DC X/Y>        # 仅 netlist 阶段
phase=<netlist|submit|extract result|align result>
sim=<X/Y>
sub=<X/Y>
```
key 按 sorted 排序，每行一个 key=value。

## run_all log 格式
- device banner: `\033[1m=== <name> (<polarity> / <thick>) ===\033[0m`（ANSI bold）
- gen 进度行: `<dev> gen AC <j>/<n>` / `<dev> gen DC <j>/<n>`
- submit 进度行: `<dev> submit=<X>/<Y>  done=<X>/<Y>`
- [ok]/[FAIL] 行

## 真实数值（trace msg 220/302/459/517/525）
- ntn device: 14364 AC points, 3564 DC points
- watch 实测 (msg 517): `{netlist=DC 3564/3564} {submit=11880/11880} {sim(done)=11746/11880} | current=ptn_lvl finished=ntn,ntn_m,ntn_lv,ntn_lvi`
- watch 实测 (msg 525): `finished=ntn,ntn_m,ntn_lv,ntn_lvio,ntn_lvl,ntn_zvt,ptn,ptn_lv,ptn_lvio`
- 器件族: ntn, ntn_m, ntn_lv, ntn_lvio, ntn_lvl, ntn_zvt, ptn, ptn_lv, ptn_lvio, ptn_lvl

## reframe（case = EDA-Eval-DesignFlow-HspiceSweepWatchRender-001）
**L1 Python 纯标准库**：`hspice_watch.py <progress_file> <log_file> <out.json>`
- 解析 `.progress` key=value (current/phase/net/sub/sim/done/extract)
- 解析 log: device banners `=== <name> (<pol>/<thick>) ===`(带 ANSI)、`gen (AC|DC) X/Y`、`submit=X/Y`、`done=X/Y`
- 输出 JSON: current_device, phase, netlist{raw,type,done,total}, submit{done,total}, sim{done,total}, extract{...}|null, finished_devices[], devices_started[], n_devices_started, n_devices_finished, last_gen{...}, last_submit{...}, last_simdone{...}, pct_sim_complete, watch_line
- watch_line 格式: `[watch] {netlist=<type> <done>/<total>} {submit=<done>/<total>} {sim(done)=<done>/<total>} | current=<cur> finished=<dev1,dev2,...>`

**A**（visible，trace-faithful）: ntn 族，DC 3564/3564 submit 11880/11880 sim 11746/11880 finished ntn,ntn_m,ntn_lv,ntn_lvi current=ptn_lvl phase=submit
**B**（hidden，anti-hardcode 五重）: ①不同器件族(sntn/sntn_hvt/ntn_hvt/ptn_hvt/pt 代替 ntn 族) ②不同数值 ③phase=extract result（A 是 submit）④B 含 extract 字段（A 无）⑤B 器件数与 A 不同

**check 15 条**: (a)zip+compile+size (b)B exit0+非空 JSON (c)顶层键集 (d)current_device (e)phase (f)netlist 结构+type/done/total (g)submit 结构 (h)sim 结构 (i)extract 结构(B 必有) (j)finished_devices 列表 (k)devices_started 列表+顺序 (l)last_gen from log (m)pct_sim_complete 数值 (n)watch_line 格式 (o)anti-hardcode:A 器件名缺席 B 在场

**3 negs**: neg_empty(→a/b) / neg_print_only(硬编 A report→d/e/f/g/h/i/j/k/l/m/n) / neg_core_removed(真解析但 watch_line 固定+A 器件名→n/o)

## near-dup 自查
现存 B cases: PowerSupplyDcTypeGen / CornerBlockGen / McVariationBlockGen / ProbeBlock / SpTemplatePvtGroupRender / Vvdd2cStimRewrite / DynPowerScan / Mt0CornerPivotAggregate / FinesimMt0Parser / SpiceNetlistFaultAnalyzer / MosComparaReport / ProbeCovAnalyzer / SubcktUnclosedDiag / SigmaflagEffect / UlvtGmChar / LsfSubmitDiag / VrwckPvdbiasInterp / SpTocParamRewrite / BuildStepCacheClassify / FsdbCurrentReportAggregate / DutyOffsetAlertMax / PigzResolver / QuadClkSkewMeas / SigmaDcSweepAudit / DelvtoNetlistModifier / CharRemovalAbort / StrongarmBaseline / LatchFomSweep / SharedLibDeployFix / PvtMt0ThreeLevelAggregate / DutyMidvalMeasRewrite / LatchResetFomSweep / C2cCornerAmplifierAudit / PvtConfigDeckGen / PVTalterChar / TieJitterIncGen / SpTocParamRewrite / PowerSupplyDcTypeGenProduce / SpiceNetlistFaultAnalyzer 等。
**本 case 不同**: 解析 `.progress` snapshot + run_all log（双源）→ JSON 进度报告 + watch_line 渲染。无 near-dup（HSPICE sweep live progress parser 是新角度，LsfSubmitDiag 是 bsub 输出解析器不同，Mt0CornerPivotAggregate 是 mt0 结果聚合不同）。✓
