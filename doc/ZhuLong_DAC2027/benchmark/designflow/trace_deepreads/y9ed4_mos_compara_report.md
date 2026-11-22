# 深读笔记 — 1795163343888_y9ed4（MOS 前后仿对比 xlsx 报告修复 · characterization L1 produce-reframe）

- **trace**: `/home/shanliny/.cline/data/sessions/1795163343888_y9ed4/1795163343888_y9ed4.messages.json`（shanliny @ hfeg0plg107, mc=49, 156 msgs, 828KB）
- **来源**: r1069 fresh B-spice 池（fresh_b_spice_local.tsv, 176 spice_kw）
- **keywords**: netlist/hspice/pdk/synopsys/transistor/opamp/schematic/analog — B characterization（MOS 前后仿对比）
- **domain**: characterization（MOS 管Idsat/Ioff/Vth 前仿 vs 后仿对比报告生成）

## 用户意图（U0 = msg 0，A-faithful produce-task：提需求未给根因/修复）

> 「你看一下 /proj/.../mos_compara_ver2，你写的脚本在生成 xlsx 文件时，并没有德尔塔 Ioff，脚本也没有去 fsdb 文件中把前仿后仿 fsdb 的 Vth 测出来，xlsx 的 Vth 项目也偏少，只有一个 Vth，缺少前仿、后仿、德尔塔的区别」

三处缺陷：
1. xlsx 缺 **ΔIoff%** 列（只有 ΔIdsat%）
2. 脚本未从 pre/post fsdb 提取 Vth
3. Vth 只有一列（仅 post），缺 **Vth(pre)/Vth(post)/ΔVth** 三列区分

## assistant 工具链（84 assistant msgs）

- `list_allowed_files` + `read_files` 读 mos_compara.py / START_HERE.txt / pre.mt0 / post.mt0
- 定位 `write_xlsx_report`：两 sheet（总览/逐管对比）表头只有 `ΔIdsat%`，Vth 只取 `post_m["vth_v"]`
- 定位 `extract_vth_from_fsdb`：只在 `/home/shanliny/.cline/skills/waveview-fsdb-readerV2-2` 找 reader，缺 `/home/e0039602/Documents/waveview-fsdb-reader` 回退路径
- `editor` 修补 `mos_compara_fixed.py`：
  - `extract_vth_from_fsdb`：补全 waveview_fsdb_reader 多导入路径
  - `write_xlsx_report` 两 sheet 改 11 列：`晶体管|极性|Idsat(pre)|Idsat(post)|ΔIdsat%|Vth(pre)|Vth(post)|ΔVth|Ioff(pre)|Ioff(post)|ΔIoff%`
  - title 合并 `A1:K1`
- 后续修复（U141-U155）：LV9 信号名 `lstrip('X')` bug → 多候选信号名；`wv` 本机 glibc 太旧 → `bsub -q wv_queue -env none`；`KeyError: 'fingers'` → `device_groups[:3]`

## GOLD（msg A46/A93/A154）

**核心交付**：`write_xlsx_report` 输出 11 列结构：
```
晶体管, 极性, Idsat(pre), Idsat(post), ΔIdsat%, Vth(pre), Vth(post), ΔVth, Ioff(pre), Ioff(post), ΔIoff%
```
- **ΔIdsat%** = (post-pre)/|pre|*100（相对百分比）
- **ΔIoff%** = (post-pre)/|pre|*100（同款相对百分比，Ioff 符号/量级差异做 None 防护）
- **ΔVth** = post-pre（绝对差 V）
- Vth(pre)/Vth(post) 分别从 pre.fsdb / post.fsdb 提取（LV9 信号）

真实数据验证（4907 管，sim/pre/pre.mt0 + sim/post/post.mt0）：
```
header: 晶体管, 极性, Idsat(pre), Idsat(post), ΔIdsat%, Vth(pre), Vth(post), ΔVth, Ioff(pre), Ioff(post), ΔIoff%
row3  : bkb.xbk_cnt.xxdec0.mnm_xbc_0_, NMOS, -2.155e-4, -2.155e-4, ΔIdsat=0, Vth(None), ..., -2.347e-11, -2.347e-11, ΔIoff=0
r7    : MPM_XBC, PMOS, Ioff 2.6152e-11 → 7.8457e-11, ΔIoff=200
r8    : XINV_FCK.MINM0, NMOS, Ioff -2.462e-10 → -4.925e-10, ΔIoff=-100
```

## 判定：buildable（L1 produce-reframe，characterization B-shard）

- ✅ 真实 trace + B-domain（MOS 前后仿 characterization 对比报告）
- ✅ A-faithful U0=msg0（提需求，未给根因/修复）
- ✅ GOLD = 11 列报告结构 + Δ 公式（ΔIdsat%/ΔIoff% 相对百分比，ΔVth 绝对差）+ None 防护
- **reframe**：`mos_compara_report.py <spec.json> <pre.json> <post.json> <out.json>` — 读 pre/post 每管测量记录，按 spec 列序计算 ΔIdsat%/ΔIoff%/ΔVth，输出 JSON 报告（每管 11 字段 + summary）
- **L1 离线 Python 复刻**：纯 stdlib 数据处理，无需真跑 fsdb/wv

## case_id: EDA-Eval-DesignFlow-MosComparaReportGen-001

**A（visible）**：真实结构采样 — 12 管（NMOS/PMOS 混），Idsat 负(NMOS)/正(PMOS)，Ioff 负(NMOS)/正(PMOS)，全管有 Vth。spec_A 列序 = [device,polarity,idsat_pre,idsat_post,delta_idsat_pct,vth_pre,vth_post,delta_vth,ioff_pre,ioff_post,delta_ioff_pct]

**hidden B（五重 anti-hardcode）**：
1. 列序不同（spec_B = [device,polarity,vth_pre,vth_post,delta_vth,idsat_pre,idsat_post,delta_idsat_pct,ioff_pre,ioff_post,delta_ioff_pct] — Vth 列前置）→ 反「硬编 A 列序」
2. B 管名不同（XTOP.XA.MN0 / XTOP.XB.MP1 ... vs A 的 bkb.xbk_cnt...）→ 反「硬编 A 管名」
3. B 部分管 vth_pre=None（missing，模拟真实 trace Vth 提取失败）→ delta_vth 必须 None（非 0/非 crash）
4. B ΔIdsat%/ΔIoff% 数值范围不同（post=2×pre / post=0.5×pre 等）→ 反「返回 A 常数」
5. B 极性分布不同（PMOS 主导 vs A NMOS 主导）

**check.py 13 条（a-m）**：①zip+compile ②B exit0+非空JSON ③顶层键⊇{spec,devices,n_devices,summary} ④n_devices==B 管数 ⑤每管 11 字段齐 ⑥ΔIdsat% 逐管与 oracle 一致(rel=1e-6) ⑦ΔIoff% 逐管与 oracle 一致 ⑧ΔVth 逐管与 oracle 一致 ⑨列序==B spec 列序(反 A 硬编) ⑩vth_pre=None 管 delta_vth==None(None 防护) ⑪极性逐管与输入一致 ⑫anti-hardcode(B 管名在场/A 管名缺席) ⑬3-seed sha256 一致

**3 negs**：neg_empty(0字节→①②) / neg_print_only(打印 A report 串无 JSON→②③④) / neg_core_removed(真解析 B 但 Δ 硬编 A 值/列序 A→⑥⑦⑧⑨ 四齿)

§4.9 三假全 FAIL ✓；k_rationale=13=k_check=13 ≥8 ✓
