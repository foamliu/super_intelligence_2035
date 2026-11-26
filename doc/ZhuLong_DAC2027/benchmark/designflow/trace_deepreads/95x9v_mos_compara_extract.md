# 深读笔记 · 95x9v · shanliny MOS transistor 提取脚本

**session**: 1795084821167_95x9v · **user**: shanliny · **host**: hfeg0pkn003 (10.129.2.12)
**match_count**: 10 (hspice:10, waveview:18, aether:18, netlist:15, pyaether:11, cadence:10, lvs:6, .gds:5)
**domain**: spice_sim / characterization（DSPF 网表 MOS 器件提取）
**agent**: lead (deepseek-v4-flash)

## 真实用户意图（user 原话）

- **U0 (msg0)**: `帮我看/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/mos_compara`
- **U1 (msg33)**: `太慢太慢，优化算法，多核并行处理一起上，10GB量级的网表你现在这个速度还差不到`
- **U2 (msg127)**: `我在compara目录塞了一张10GB量级的网表，你之后试验可以在86MB那个网表上试验，最终速度测试用这张大网表。再者你这个脚本输出文件最好塞在一个文件夹里，全挤在主目录算什么样子，给我整理好`

## 任务本质

从 DSPF 寄生网表里提取所有 MOS 晶体管（X 实例行），按 9 个 model 家族（nsvt/psvt/nlvt/plvt/nulvt/pulvt + hd_pu/hd_pd/hd_pg）过滤，要求器件带 L/W/nfin 三个必选参数（hd_* SRAM 器件无 L/W/nfin → 被过滤），输出结构化结果文件并整理进 `results/` 子文件夹，支持多核并行以应对 10GB+ 网表。

## 关键 trace 事实（非脱敏，全保真）

- **真实输入网表**:
  - `CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS.dspf.TYPICAL_25` (87MB) — 权限 e0031982 不可直读，从 trace tool_result 提取真实 X-line 样本
  - `HC1P_CXN4S1P2048X144M4B2C1R1W1BW1RE1.dspf.TYPICAL_-40` (20.4GB) — 大网表
- **真实 X-line 格式** (msg22 stdout，全文保真):
  `XXLIO.XLIO_L.XLIO_EDGE_D.XI0.MNM3 XLIO.XLIO_L.XLIO_EDGE_D.XI0.MNM3:d XLIO...:g VSS VSS nsvt_fs L=6e-09 W=1.19e-07 nfin=2 wgaa=3.5e-08 adej=2.6775e-15 ...`
  即 `X<inst> <d> <g> <s> <b> <model> <param>=<val> ...`，model 是第 6 个 token (toks[5])
- **真实 model 计数** (msg22): psvt_fs 4507, nsvt_fs 3776, hd_pu_fs 1312, hd_pd_fs 1312, hd_pg_fs 1312, nulvt_fs 276, pulvt_fs 273, nlvt_fs 96, plvt_fs 96
- **真实提取结果**: 9024 个有效晶体管（hd_* 1312×3=3936 因无 L/W/nfin 被过滤；12960 X 含 '=' 行中 9024 有 L/W/nfin）
- **真实 param 键** (msg22 全量): L, W, nfin, nf, wgaa, adej, asej, pdej, psej, gted, gteu, v0gd, v0gu, sa, sb, sdbl, sdbr, cctdmod, cctsmod, coagmod, delvtrand, dtemp, globalfactor, localfactor, totalfactor, ids0mult, u0mult, mr, dmbmod1, dmbmod2, dmby1, dmby2, nfm, nfp, osex1-2, osey1-2, pedl1-2, pedr1-2, peul1-2, peur1-2, plel1-3, pler1-3, ppmod, rctdmod, rctsmod, rgtmod, wpex1-2, wpey1-2

## 最终交付物（真实）

`/home/shanliny/mos_compara_extract_mp.py` (572 行, 21958 bytes, 已 scp 回 workdir 验证)
- **CLI**: `python3 mos_compara_extract_mp.py [网表] [-j N] [--serial]`
- **预过滤**: 行首 `X` 且含 `=` 才分词；其余 ~99% C/R 寄生行 bytes.startswith 跳过
- **model 过滤**: toks[5] ∈ 9 个 TRANSISTOR_MODELS
- **必选参数过滤**: L, W, nfin 三个全在才提取（hd_* 无 L/W/nfin → 排除）
- **输出到网表目录的 `results/` 子文件夹**:
  - `<design>__MOS_all.txt` — 2 行头(`# MOS_CMP design=<d> total=<N>` + 列说明) + 每器件一行 `<id>  <polarity>  <model>  k=v k=v ...`
  - `<design>__MOS_params.csv` — 宽表 CSV，头 `id,polarity,model,d,g,s,b,<ordered_keys>`
  - `<design>__cat_<8类>.csv` — 8 个分类 CSV (core_geometry/finger_geometry/diffusion_sd/od_extension/contact_spacing/extension_poly/model_modifiers/dtab_mismatch)
  - `<design>__cat_index.txt` — 分类索引
  - `<design>__MOS_summary.txt` — total + [count by model] + [count by polarity] + 每参数值统计
- **polarity 映射**: nsvt/nlvt/nulvt/hd_pd/hd_pg→NMOS; psvt/plvt/pulvt/hd_pu→PMOS
- **并行**: >128MB 用多进程 fork + 字节区间 pread 对齐行起始；小文件串行保底
- **真实实测** (msg157/161): 20.4GB 网表 -j 64 → 95924 器件, scan 29.35s, total 42s; MOS_all.txt 95926 行(2 头+95924 数据) 验证通过

## 合成计划 (A 档 trace-faithful)

**case_id**: EDA-Eval-DesignFlow-MosComparaExtractGen-001
**reframe (harness-for-teeth)**: one-off 脚本 → 参数化 produce-task。给一张真实风味的 DSPF 网表 (asset A, 14 有效器件 + 6 hd_* + 2 非晶体管 X + 8 C/R)，要求交付提取脚本；hidden B = 结构不同网表 (21 有效器件 + 12 hd_* + 3 非晶体管 X + 12 C/R，不同 design 名/器件数/model 配比/节点名/参数值) → 验通用性 + anti-hardcode-A (B 器件数 21≠A 14)。
**check()**: 在 B 上真跑候选脚本 (subprocess)，独立解析 B 为 ground truth，断言 ≥14 条 (a-n)：zip 含 .py / B 上 exit0 / results 产出 / MOS_all.txt 头 total 正确 / 数据行数 = N_B / polarity↔model 映射正确 / 仅 9 model 无 hd_* / 每行含 L/W/nfin / MOS_params.csv 头+行数 / cat_index.txt 存在 / MOS_summary.txt total+by-model+by-polarity / by-polarity NMOS+PMOS=N_B / 确定性重跑一致 / anti-hardcode-A (total=21 非 14) / hd_* 排除显式。
**负样本**: neg_empty / neg_print / neg_core(去掉 model 过滤) / neg_hardcode(硬编码 A 的 14) / neg_nothdfilter(保留 hd_*) — 含 §4.9 三假 (empty+print+core-removed)。
**自验**: ref(real script) PASS 14/14 + NEG 5/5 全 FAIL + 确定性 diff 一致。

**trace 真实性**: 经 .75 SSH scp 取回真实 messages.json 全文 + 从 trace tool_result 提取真实 X-line/param/model 计数(非脱敏，路径/器件名/model/参数值全保真)；asset A 的 X-line 用真实 param 值模板生成(6e-09/1.19e-07 等)，hidden B 同模板异 seed。
