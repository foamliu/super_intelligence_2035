# b3weg 深读 — FineSim SPF-sim skew trim range t_r0_2_f01 增量分析

**session**: `1792397240623_b3weg.messages.json`
**user/host**: joeyl @ hfeg0plg74 (also visible on hfeg0plg93/hfeg0pkn004)
**mc**: 6 (summary_20261121_151844.tsv keywords: binary:8;spectre:4 — 关键词弱但意图清晰)
**domain**: spice_sim (FineSim characterization post-processing)
**msgs**: 25 (110KB)
**date**: 2026-11-09

## 用户真实意图 (msg 0)

> 请看这个文件夹：/proj/drgqa/V0/simdir/finesim/workdir/joeyl/simulation/sim/SPF-sim/008_FullPath_skew_trim_range，
> 里面子文件夹的000～111各有一个csv，里面包含tt25/tt98/ss25/ss98/ff25/ff98 按顺序6个corner的alter结果，
> 需要关注这个数据，t_r0_2_f01，随着从000到111逐渐增加，我希望你分corner整理出来从000到111每个step的增量，单位为ps，以表格形式呈现给我

**任务形态**：FineSim characterization 后处理。8 个 trim 码（000~111 二进制）对应 8 个子文件夹
（000_5corner ~ 007_5corner），每个文件夹一个 `.mt0.csv`（FineSimPro 测量输出），含 6 行 alter
结果按 tt25/tt98/ss25/ss98/ff25/ff98 顺序。提取 `t_r0_2_f01` 列，按 corner 计算 7 个 step 增量
（001−000, 010−001, ..., 111−110）+ 累计（111−000），单位 ps，表格输出。

## assistant 工具链 (msgs 1-24)

1. `list_allowed_files` 探目录 → 发现 8 子文件夹 + .sp 文件
2. `list_allowed_files` 000/007 子文件夹 → 发现 `0_000.mt0.csv` ~ `7_111.mt0.csv`
3. `read_files` 0_000.mt0.csv → FineSimPro CSV 含 `t_r0_2_f01` 列
4. `read_files` run 脚本 → 确认映射 `0_000.sp → 000_5corner` … `7_111.sp → 007_5corner`
   （即 trim 码 000~111 依次对应文件夹 000~007）
5. `search_codebase` corner/temp → 超时
6. `list_allowed_files` /home/joeyl → 确认可写
7. `editor` 写 `extract_trim_skew.py`：解析 8 个 .mt0.csv，提取 t_r0_2_f01（6 corner），算 step 增量
8. `run_approved_command` python-runner → 失败（文件夹名 `0_5corner` 应为 `000_5corner` 三位补零）
9. `editor` 修 `FOLDERS = ["{:03d}_5corner".format(i) for i in range(8)]`
10. `run_approved_command` → 成功，输出 8×6 raw 值 + 增量表

## 关键产物 (msg 23-24)

**raw t_r0_2_f01 (秒)**：
- 000: [1.2493e-10, 1.2523e-10, 1.2582e-10, 1.2588e-10, 1.2526e-10, 1.2484e-10]
- 001: [1.2852e-10, 1.2841e-10, 1.2927e-10, 1.2934e-10, 1.2802e-10, 1.2821e-10]
- 010: [1.3154e-10, 1.3122e-10, 1.3244e-10, 1.3243e-10, 1.3047e-10, 1.3076e-10]
- (011~111 由增量表反推)

**增量表 (ps)** — msg 24：
| corner | 001−000 | 010−001 | 011−010 | 100−011 | 101−100 | 110−101 | 111−110 | 累计 |
| tt25 | +3.59 | +3.02 | +2.90 | +1.58 | +3.04 | +2.65 | +3.23 | +20.01 |
| tt98 | +3.18 | +2.81 | +3.24 | +1.72 | +3.09 | +1.98 | +3.24 | +19.26 |
| ss25 | +3.45 | +3.17 | +3.50 | +1.40 | +3.61 | +3.08 | +3.52 | +21.73 |
| ss98 | +3.46 | +3.09 | +3.64 | +1.82 | +3.18 | +2.90 | +3.52 | +21.61 |
| ff25 | +2.76 | +2.45 | +2.98 | +1.16 | +3.14 | +2.63 | +2.66 | +17.78 |
| ff98 | +3.37 | +2.55 | +3.21 | +1.29 | +2.51 | +2.37 | +3.20 | +18.50 |

assistant 人工核对：tt25 144.94−124.93=+20.01ps ✓；001−000=128.52−124.93=+3.59ps ✓

## reframe (portable L1 纯 Python)

`trim_skew_increment_analyzer.py --data-dir <dir> --column <name> --report <out.json>`

- 扫描 `--data-dir` 下 8 个 `NNN_5corner` 子文件夹（N=0..7），每个含 `<dec>_<bin3>.mt0.csv`
- 解析 CSV header 找 `--column` 列，读 6 行（按 alter 顺序 → tt25/tt98/ss25/ss98/ff25/ff98）
- trim 码 = 文件夹索引的二进制 3 位补零（000~111）
- per corner: 7 step 增量 = 后一个 trim 减前一个（ps = (v[i+1]-v[i]) × 1e12）
- 累计 = v[7] - v[0]
- JSON 输出：{trim_codes, corners, column, unit, raw, increments, cumulative}

**A** (dir_A, 忠实 joeyl 真实数据): column=t_r0_2_f01, 8 trim × 6 corner, 值 ~1.25e-10
**hidden B** (hidden/dir_B, 五重 anti-hardcode): column=t_skew_2_r1, 8 trim × 6 corner, 值 ~1.85e-10,
  不同的 baseline/增量模式/column 名全异

**case_id**: EDA-Eval-DesignFlow-TrimSkewIncrementProduce-001
**check.py 12 条** (a-l, k_check=k_rationale=12):
①(a)zip+py_compile+size>200 ②(b)B exit0+JSON 产生 ③(c)JSON 含 {trim_codes,corners,column,unit,raw,increments,cumulative}
④(d)trim_codes==['000'..'111'] 8 个 ⑤(e)corners==['tt25','tt98','ss25','ss98','ff25','ff98'] 6 个
⑥(f)increments[corner] 7 个 step ⑦(g)每 increment==独立 oracle 复算 (tol 1e-6 ps)
⑧(h)cumulative==sum(increments)==last-first ⑨(i)unit=='ps'+raw 值×1e12 后量级~100ps
⑩(j)anti-hardcode: A column 't_r0_2_f01' 缺席 + B column 't_skew_2_r1' 在场 ⑪(k)per-corner 独立(无跨 corner 混)
⑫(l)3-seed PYTHONHASHSEED=1/2/3 sha256 一致

**核心齿**: ⑦精确增量(反 naive 全正/全零) + ⑧累计一致性(反硬编码累计) + ⑩anti-hardcode(反硬编码 A column)
