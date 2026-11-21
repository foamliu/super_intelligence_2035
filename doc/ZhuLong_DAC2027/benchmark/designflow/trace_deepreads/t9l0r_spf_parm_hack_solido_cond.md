# t9l0r deepread — SPF bitcell parm-hack + solido PVT-conditionalized .inc (r976)

- **session**: 1795052638809_t9l0r @ hfeg0plg68, user e0046686, mc=158, spice_sim
- **trace size**: 2.5MB / 407 messages
- **picked at**: r976 fresh queue (mc=158, B-spice top), claimed+合成 r976

## 用户意图（真实 trace 流）
用户 e0046686 @ hfeg0plg68 做 SRAM bitcell PVT corner 蒙特卡洛表征流程，task 文件
`TASK_HACK_SPF_V2.md` 给两块活：

主线 1 (parm_hack_for_large_spf.py 改造): 大 DSPF 里每个 bitcell 实例 6 个 pin device
行 (`*|I (XIbitcell_8x8[i].XICELL[j].<pin> ... )`)，需要追加 **参数名**（不是值！）
`sda_rnd_mis_{k}_local={pxx}_{k}` 共 K 个 token，让 finesim/nanospice 在 `.param` 块
里自动替换。原脚本错在追加"值"，新需求是追"名"。6 pin 固定顺序
MIPM0/MINM0/MINM3/MIPM1/MINM1/MINM2 → pu_b/pd_b/pg_b/pu_t/pd_t/pg_t。位单元路径前缀
大小写不固定，匹配要 case-insensitive。外围 (XLIO/XI_NAND/MIMP0@2 latch/IO 行)、
电容行、*|S 段不动。K 由 solido.txt 第一行 `.param` 的 `=` 个数决定（自己解析）。

主线 2 (solido_cond_gen.py 新建): solido.txt (Solido 蒙特卡洛输出) 按 mode group
分块 (`*===== <mode>_solido_txt =====`)，每 group N 个 PVT 段
(`*<mode>_<proc>_<volt>_<temp>_<sigma>`)，每段 6 行 `.param` (pd_t/pd_b/pu_t/pu_b/
pg_t/pg_b)，每行 K 个值 (`_0.._K-1`)。要转成 **单个 .inc**，用 HSPICE/FineSim 兼容
语法 `.if stricmp(SMODE,"<seg>")==0 / .elseif / .else / .endif` 把每个 PVT 段条件化，
group 内首段 `.if`、后续 `.elseif`、末尾 `.else`+`.endif`。已确认 finesim if/else
语法 HSPICE-compatible，支持 stricmp。集成进 memchar_gen.py 流程
(char.input weakcell=true + SMODE)。

## reframe (harness-for-teeth)
两块主线固化成两个通用脚本 + 一个 orchestrator：
- `spf_parm_hack.py`: 流式扫 DSPF，正则匹配 `<prefix>[i].XICELL[j].<pin>` (case-insensitive)，
  追加 `sda_rnd_mis_{k}_local=<pgroup>_{k}` (k=0..K-1)，幂等（先剥旧 token），非匹配行逐字节不动。
- `solido_cond_gen.py`: 解析 solido.txt mode group + PVT 段 + 6 .param 行，emit .inc with
  `.if stricmp(SMODE,"<seg>")==0` 块，group 内首 `.if` 后续 `.elseif` 末 `.else`+`.endif`。
- `build_submit.py`: 在 cwd 找 design.dspf/solido.txt/config.json，调上面两个脚本，
  产 outputs/hacked.dspf + outputs/solido.inc，打包 outputs/submit.zip。

## A 档 (trace-faithful, 可见)
design_A.dspf: subckt CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS，prefix XIbitcell_8x8，
6 bitcell (60 pin 行)，外围 XLIO.* 5 行，12 电容。solido_A.txt: 3 mode group
(icell/rsnm/wm)，PVT ffg/sfg/ssg × 0.6/1.02/0.54 × -40/25/125 × 6sigma，每行 9 值。
config_A.json: prefix/count/pin_map/param_rows/mode_groups/smode_convention/模板。

## hidden B (判分, 不进沙箱)
design_B.dspf: subckt CXN4HC1PS128X4M2B1C1R1W1BW1RE1_FS，prefix XIBITCELL_16x4，
10 bitcell (60 pin 行)，外围 XPIO.* 6 行，18 电容。solido_B.txt: 3 mode group
(icell_v2/read_mgn/write_mgn)，PVT ttg/ffg/ssg × 0.72/0.88/0.60 × -40/25/85/125 ×
5sigma，每行 12 值。结构同 A（通用 CLI 可跑）但 subckt 名/prefix/bitcell 数/
mode 名/PVT label/每行值数 K/所有参数值全异，非"换文件名"。

## 自验
- reference (3 脚本) 跑 B: hacked.dspf 60 bitcell 行各带 12 个 sda_rnd_mis_*_local=
  <pgroup>_<k> token，外围/电容逐字节不动；solido.inc 3 个 .if + 9 个 .elseif + 3
  个 .else + 3 个 .endif，12 段全覆盖，每段 6 .param × 12 值 ✓
- check.py (ref as submit.zip on B): PASS 12/12 (a-l) ✓
- negative_selftest: ref PASS; neg_empty FAIL[b], neg_print FAIL[b],
  neg_core_removed FAIL[d], neg_hardcode_a FAIL[d] ✓ (§4.9 三假全 FAIL + hardcode-A FAIL)
- k_rationale == k_check == 12 (≥8 硬闸门) ✓
- anti-hardcode-A: 12 个 A-only token 守门 (XIbitcell_8x8/CXN4HC1PS64X8/icell_ffg_0.6/
  icell_sfg/icell_ssg/icell_solido_txt/rsnm_/wm_ffg/wm_ssg/6sigma/sfg_/MMPM0) ✓
- 3-seed 确定性 (PYTHONHASHSEED=0/1/42) ✓

## 备注
- 资产全合成 (gen_assets.py，自包含，无 /rundata /proj 依赖)，同 r974 gpya9 模式。
- B 的 bitcell pin 行数 (60) 与 A 同，但 bitcell 数 (10 vs 6) 与 prefix 全异，
  anti-hardcode-A 守 prefix/subckt/mode/PVT/sigma/periphery-pin 全维度。
- token 模板 sda_rnd_mis_{k}_local=<pgroup>_{k} 中 <pgroup> 是 pin→param-row 映射
  (pu_b/pd_b/pg_b/pu_t/pd_t/pg_t)，与 solido.txt 的 6 个 .param row name 一致，
  这样 finesim 能在 .param 块里查到对应名字替换。
