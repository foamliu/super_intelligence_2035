# r1135 (2026-11-24) — 527j4 build-round deepread · SRAM WM/RM meas-gen 通用引擎

## 背景
r1131 peek 527j4 判 "complex-continuation deferred: 真交付 ✓ 但依赖 80MB DSPF + 前序 session + 3 未确认定义，单轮不可自包含封装"。r1134 心跳指示下一步为「527j4 专项 build 轮（需 2-3 轮+80MB DSPF）」。

本轮执行：开 eda_flow session (synthetic task_id=DesignFlow-B-build-r1135) → ssh hfeg0plg107 scp 完整 527j4 session (650KB/135msgs) + 0rh2t uploads 全量资产 → 解析对话流 → **推翻 r1131 "不可自包含" 结论**：80MB DSPF 不需要，只需 `.SUBCKT` 顶层引脚声明（~1.2KB header）。

## trace 溯源
- user: shanliny · host: hfeg0plg107 · session: `1794970325758_527j4.messages.json` · mc: 24 · domain: characterization
- 前序 session: `1794964870215_0rh2t` (同 user/host, 554KB, uploads/ 含 config 全套)
- real_task_summary: 为 SRAM 奇偶核 (M4B2 64×8, `CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS`) 设计 WM/RM 测量方案 + 重写 `generate_xtop.py`/`sram_meas_gen.py` 为对任意 instance 生效的通用引擎

## 对话流（user 意图演化）
- U#0 (context summary): Goal = 设计 meas/RM/WM 方案 + 重写 generate_xtop.py；State = 已重写 generate_xtop.py(修 `+` 续行 bug)、已扫 80MB DSPF 抓真实层次(XBKB/XBKT bank, XIR0/1 xdec, XIC0..3 bit列, XIbitcell_4x1[y], XICELL[wl] WL, XLIO.xsa SA)、确认地址位序 A[1:0]=y, A[2]=bank, A[4:3]=WL组, A[5]=xdec
- U#1 "继续你的meas和vec输出" → assistant 读 config 验证 3 阻塞点
- U#16 assistant 从 config_path.txt 网表宏实锤 3 阻塞点：①xdec 下=XIR0/上=XIR1 ②bit 左右缘=nb_l/nb_r ③SA 归属=XLIO.xsa
- U#19 "只保留w0r0，直接把rm和wm也在这两个周期测了" → 收敛为 2 拍方案（原 4 拍 w0/r0/w1/r1 → 砍互补态 w1/r1）
- U#21 "开始吧" → 生成首版 vec
- U#22-28 多轮纠错：vec 端口必须对齐 XTOP(真实 .SUBCKT) 而非原 racing.vec；D 用 `[[l:h]]` 区间格式；VDD/VSS 电源列不写；Q 不写；CLK 不入 vec
- U#42 "/home/shanliny/CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS.dspf.TYPICAL_25 就是真实网表" → assistant 解析真实 .SUBCKT 得 56 脚权威 XTOP
- U#50 "clk不入vec，不用BWEB你根据端口算出来放进vec里保持全写入，其他引脚我在pdef里用电压源固定，crs首拍锁存"
- U#53 "Q不是Z，直接不写进vec"
- U#77 "全写进/home/shanliny/"
- U#91 "生成的东西可以，所以你的对任意instance生效的程序呢？" → **核心交付触发**：重写为参数化通用引擎 sram_meas_gen.py
- U#92-122: 重写 sram_meas_gen.py（从真实 DSPF .SUBCKT 动态解析顶层引脚 + 从 config_path.txt 读 $cm/$bk/$nw/$nb/$re 与宏递归展开 + 地址布局参数化 {xdec}{wl(2)}{bank}{y}）；验证对 64×8 真实网表产出与手写版逐字一致 + 对 2048×72/退化情形(mux=1/bank=1)正确折叠位数
- U#125 "直接写到/home/shanliny/" → 落盘

## 交付物（真交付 ✓）
**`sram_meas_gen.py`** (14744B) — 参数化通用 WM/RM 引擎：
- 输入：`--spf <DSPF>` (只读 `.SUBCKT` 顶层引脚，不读 80MB body) + `--cfg <config_path.txt>` (读 $cm/$bk/$nw/$nb/$re + $lio_*/$array_bk*/$bitcell_* 宏递归展开)
- 输出：`rmwm.vec` + `rmwm.pdef` + `rmwm_meas.txt`
- 关键设计（"对任意 instance 生效"三支柱）：
  1. 顶层引脚动态解析：`parse_top_pins(spf)` 读 `.SUBCKT` → `bus_width(pins,"A"/"D"/"BWEB")` 得位宽 → vec 头自动生成列
  2. 参数/路径全来自 config：`Cfg._evalparams` 解 $cm/$bk/$nw/$nb → `nxdec_perbk=words/mux/bank/4-1`；`Instance.bitcell_path/sa_path` 用 $bitcell_bk{bk}{half}_{edge}_y{y} / $lio_{edge} 宏，缺则 fallback 合成
  3. 地址布局参数化：`addr_value` 按 `log2(mux)/log2(bank)` 动态拼位 {xdec}{wl(2)}{bank}{y}

## 关键文件（源 hfeg0plg107 路径，持久存在，下轮可直接 scp）
| 文件 | 路径 | 大小 | 用途 |
|---|---|---|---|
| sram_meas_gen.py | /home/shanliny/.cline/data/sessions/1794964870215_0rh2t/uploads/sram_meas_gen.py | 14744B | **参考解** |
| config_path.txt | 同上 uploads/ | 48611B (1007 $宏) | A 输入：instance 配置 |
| config_racing_meas.txt | 同上 | 10508B | A 输入：meas 模板参考 |
| racing.vec | 同上 | 4626B | A 输入：vec 格式参考 |
| dspf_header | /home/shanliny/CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS.dspf.TYPICAL_25 head -c 1200 | 1.2KB | A 输入：.SUBCKT 引脚声明 |
| rmwm.vec/pdef/_meas.txt | 同上 uploads/ | 33K/24K/137K | 参考输出（自验对照） |
| config_inst.txt | 同上 | 138B | 4 个 instance 名清单 |

## config_path.txt 结构（B 构造依据）
```
$cm=4 $bk=2 $nw=64 $nb=8 $re=1   # instance 参数
$nb_l=floor($bits/2)-1  $nb_r=ceil($bits/2)-1  $nxdec_perbk=$words/$mux/$bank/4-1  # 派生
$lio_ll=xtop.xlio.xlio_l.xlio0   $lio_lr=...xlio_l.xlio$nb_l   # SA 列路径（4 边缘）
$array_bk0_l=xtop.xbkb.xbk_l.xarray  $array_bk1_l=xtop.xbkt...  # bank 数组路径
$bitcell_bk{0,1}{d,u}_{ll,lr,rl,rr}_y{0..mux-1} = ...xicell[wl]  # 位单元路径宏（1007 行）
```

## .SUBCKT 权威引脚（A = 64×8 真实）
`.SUBCKT CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS VDD VSS CEB CLK WEB A[5]..A[0] D[7]..D[0] Q[7]..Q[0] BWEB[7]..BWEB[0] WT[1] WT[0] RT[3]..RT[0] RA[1] RA[0] TEST BYP CRSRE CRSRA[1] CRSRA[0] CRSLE CRSLA[1] CRSLA[0] WA WAT[1] WAT[0] WAV[1] WAV[0]`
→ A=6, D=8, BWEB=8, CRSLE/RE 各 1, CRSLA/RA 各 2

## case 合成计划（下轮，ETA 1 轮）
- **case_id**: `EDA-Eval-DesignFlow-SramWmRmMeasGenProduce-001`
- **domain**: characterization · **layer**: L1（纯 Python stdlib 复刻，不需 .75 EDA 工具）
- **A (visible, assets/)**: dspf_header_A.txt (1.2KB .SUBCKT) + config_path_A.txt (48KB) + racing.vec (格式参考) + config_racing_meas.txt (meas 模板)
- **B (hidden, assets/hidden/)**: 构造合成 32×4 instance：
  - dspf_header_B.txt: `.SUBCKT MYTEST_SRAM_32X4 ... A[4]..A[0] D[3]..D[0] Q[3]..Q[0] BWEB[3]..BWEB[0] ...` (A=5, D=4, BWEB=4)
  - config_path_B.txt: `$cm=2 $bk=2 $nw=32 $nb=4` + $lio_*/$array_bk* 适配 + 少量 $bitcell_* 宏（或靠 fallback）
- **prompt**: 真实场景——shanliny 要为 SRAM 奇偶核写通用 WM/RM meas-gen 引擎，给 DSPF header + config + racing.vec 格式参考 + config_racing_meas 模板，要求产出 sram_meas_gen.py 对任意 instance 生效
- **check() (~12 条独立断言)**:
  1. 产出 3 文件齐全 (rmwm.vec/pdef/_meas.txt)
  2. vec VNAME 含 CEB/WEB/A[[w-1:0]]/D[[w-1:0]]/BWEB[[w-1:0]]，宽度 = B 的 .SUBCKT 解析值
  3. vec VNAME 不含 CLK/VDD/VSS/Q/DIN/TESTN/TESTP（电源/输出/mock 端口剔除）
  4. vec 拍数 = 2 bank × 2 half × 4 edge × mux_B × 4 wl × 2 beat + 1 CRS 锁存行
  5. meas RM 行数 = WM 行数 = 2×2×4×mux_B×4（各半）
  6. 每 RM cellid 结尾 `_r0`，每 WM cellid 结尾 `_w0`
  7. 所有拍行窗口名唯一 (per_bk{bk}{half}_{edge}_y{y}_wl{wl}_{beat})
  8. BWEB 列全 0（全写使能）于所有拍行
  9. WEB 列 = 0(w0 拍) / 1(r0 拍)
  10. pdef `.param per_...` 数 = 拍数，第 i 个 = `'per * (i+0.5)'`
  11. pdef 含 WT/RT/RA/WA/WAT/WAV/TEST/BYP 引脚的 v_ 占位电压源
  12. 地址唯一性：每拍行地址 = {xdec}{wl(2)}{bank}{y} 按位宽拼接，全拍无重复
- **negative/**: empty.py / only_print.py / core_deleted.py（删 parse_top_pins 或 bus_width 核心逻辑）→ 全 FAIL
- **随机化**: check 在 B 上抽 3 个随机 (bk,half,edge) 子集验窗口名/地址/WEB 一致
- **自验**: ref sram_meas_gen.py 跑 B → check PASS；3 假 FAIL；negative_selftest 全 FAIL

## 本轮动作
- eda_flow open_session (synthetic) → ssh/scp 完整 session + uploads 资产到 workdir
- 解析 135 msgs 对话流 + 读 ref 引擎 + config + DSPF header + racing.vec + 参考输出
- 台账 527j4: parked → claimed (r1135 build-round deepread done)
- 结论：**r1131 "不可自包含" 结论被推翻**——80MB DSPF 不需要，只需 1.2KB .SUBCKT header；case 可自包含封装为 L1
- DEBT: 1 case 未合成（527j4 SramWmRmMeasGenProduce-001，下轮 ETA 1 轮）

## 体积
- 📊 covered=592/4529=13.1%(mc>=10, 不变，无新 case)
- 🎯 最近20条 20/20=100%(观察值,不变)
- 台账 B: 1758 → 1758（527j4 parked→claimed，0 净增）
- DEBT:1（527j4 case 合成）
