# k2v1s deepread — stdcell-from-netlist 库构建 (jiashengz@hfeg0pkn004)

**trace**: `1795763198609_k2v1s.messages.json` (1.56MB, 519 msgs, mc=540)
**user**: jiashengz (stdcell library engineer, project R1ba1, Aether/pyAether)
**domain**: schematic_netlist
**keywords**: aether:760/netlist:705/schematic:431/pyaether:394/dbopencv:293

## 用户真实意图

用 `stdcell-from-netlist` skill 在 Aether/pyAether 中按 SPICE 网表 + placement guide
在 R1ba1 库逐 cell 构建 schematic + symbol 视图。519 条消息覆盖 18 个叶子 cell +
MUX02/MUX26/LATCH22B/DFF09_RB + 顶层 D_KD142(109 实例)的全流程构建与验收。

## 核心技术深度（synthesizable）

1. **变体 W/L 提取坑**：`.Parameters` 头部 `WN=/WP=/LN=/LP=`（含链式 `LN=LP=0.05U`）。
   M-line 实例参数名是 `W=/L=`。早期脚本误用 `wp/lp`（现代版本根本不存在，静默失败
   返回 None 不报错）→ 14 个 cell 的 W/L 全部没生效（DB 里全是库默认 0.82u/0.176u）。
   权威来源是网表原文 `W=0.5U L=0.05U` 与 header `WN=0.5U WP=0.5U LN=LP=0.05U`。
   后发现 ptn/ntn_m 模型物理下限 wmin=0.816u/lmin=0.158u，网表尺寸(0.3u/0.05u)超出
   → 用户裁决：尺寸不入库，只作命名/文档。

2. **`L=default` 解析**：`TRAN1_..._LDEF` / `TRI_..._LDEF` 的 `L=default` 须解析为网表
   顶部 `.DEFAULT L=` 声明值（=0.05U），不是库默认 0.176u。用户明确 "default L = 50nm = 0.05U"。

3. **finger 倍率**：变体名 `W05x2` ↔ M-line `W=0.5U*2`（x2 fingers）。倍率藏在 W 值里。

4. **引脚别名归一化**：网表端口用 `~` 后缀（`CK~`/`RST~`/`OUT~`），Aether 拒绝 `~` →
   skill 用 `n` 后缀（`CKn`/`RSTn`）+ overbar 显示。两份权威命名口径不同（网表 `~` vs
   DB `n`），解析层归一化 `~`→`n`，网表文本不改。

5. **拓扑/电源分类**：含 MOS M-line = leaf（实体电源线 L-LEAF）；只含 X-line 子例化 =
   wrap（figureless 电源 L-WRAP）；两者都有 = mixed（DFF09_RB 有裸 PMOS I7564 → L-LEAF）。

6. **匿名网识别**：auto-gen 中间网 `net8072`/`net8093`/`net8001`（`net\d+` 模式）须与
   具名网/端口/全局网(vcc!/vss!)区分。

7. **验收**：每 cell 8 断言（check&save 0E0W / netlist triple / power L-LEAF|L-WRAP /
   on_grid / collinear / anon nets / ports / symbol orphan）。

## case 合成 (StdcellVariantSpecExtract-001)

**synthesized-reframe**：把「构建 schematic/symbol」(强依赖 Aether DB) reframe 为
**网表 spec 提取器** `parse_stdcell_lib.py(netlist.sp)->report.json`——固化上述 1-6
全部解析逻辑，纯 Python 结构化判分，无真实 EDA 工具二进制依赖。

- **A**(visible) netlist_A.sp：6 cell 覆盖全部特征——NOT(leaf simple)/NAND2(x2 倍率+anon)/
  NOR3(多 anon)/TRAN1(L=default)/MUX02(wrap)/DFF09_RB(mixed+~ pins)。
- **hidden B** netlist_B.sp：5 cell token-structurally 不同——INV_S030/NAND3(x4)/PGATE/
  MUX4/LATRB，不同 W/L(0.25u/0.4u/0.6u)、不同倍率(x4)、不同 L default(0.04u)、不同
  anon 命名(n9001)、不同 cell 名。
- **reference** parse_stdcell_lib.py：~200 行 spec 驱动通用解析。
- **check.py 15 conds(a-o)**：独立从网表文本复算关键事实（.Parameters regex /
  W=*N 倍率 / net\d+ grep / .DEFAULT / ~ 端口）再断言报告一致 + B 反硬编码 + malformed +
  源码无 A token。
- **LIVE-NA** judge_layers=[L0,L1]：文本网表解析+结构化断言，无真实 EDA 二进制依赖。
- **自验全绿**：ref check.py PASS 15/15 + negative_selftest 6neg ALL-FAIL distinct
  first-fail{c,d,h,j,k,l}（§4.9 trio: empty→c/print_only→k/core_deleted→d + 3 extra:
  no_default→h/no_normalize→j/hardcode_a→l）+ SKIP_RUN=1 workdir leak 自检通过 +
  3-way sha sync(disk==JSON test==metadata.check_sha256=6999fc09... size 12912) +
  k_check=15=k_rationale=15 + 框架 auto-build jsonl D 600 case 含本条。
