# peek note · 9dj4b · shuoran@10.129.35.68 · mc50 · agent=lead · 59 msgs · 302KB

**r923 peek 轮**（r922 next-step ② peek+synth 两轮模式，本轮 peek，r924 synth）。

## trace 概览
- session: `1793277903344_9dj4b`（shuoran @ 10.129.35.68，mc50，agent=lead，59 msgs）
- candidates_mc10 keywords: `drc:526;netlist:59;lvs:24;schematic:10;waveview:2;lib.defs:2;synopsys:1`
  - ⚠️ `drc:526` 是**假阳性**：来自路径串 `/rundata/drcpa_sim/...`（drcpa=项目名，非 DRC 检查）。真实任务与 DRC 无关。
- 真实 domain = **schematic_netlist**（FineSim SPICE measure deck `.sp` 解析 + `.pmt` 结果关联，netlist-adjacent + sim measure）

## 用户轮（A-faithful 选轮）
- **U#0**「你可以访问 /rundata/drcpa_sim/.../allbank/ 这个文件夹吗」→ 路径可达性 setup Q&A（thin，非任务轮）
- **U#7**「/rundata/.../extract_hier.py 看一下这个文件」→ 读脚本 explain Q&A（非任务轮，assistant 解释了 extract_hier.py 从 FineSim 分层网表抽取 DFF/latch 生成 setup+pulse-width measure deck）
- **U#15（A-faithful 任务轮 ✓）**「`netlist_D_WrDepth176_meas.sp` 这是生成的 measure 文件，`netlist_D_WrDepth176_meas.pmt` 这是 measure 的结果。内容实在是太多了，请帮忙编写一个脚本处理结果，需要将 measure 中的信息用上，最好保留 hierarchy，setup1，res 这种形式，然后可以过滤掉 error 的结果」
  - ✅ 符 A档选轮规则①：用户**提出需求**（写脚本解析 .sp+.pmt、保留 hierarchy、过滤 error），**未给根因/修复**。

## assistant 真实产物（gold standard）
脚本 `/home/shuoran/parse_meas_results.py`，做三件事：
1. 从 `.sp` 解析每个 tag 的 hierarchy：注释块 `* ==== <cell> <内部路径> clk=... d=... rise/fall=1` → 抽取 cell/内部路径/clk/d/edge，绑定后续 `.meas` 行的 tag（如 `XI_D_WrDepth176_29_207`）
2. 从 `.pmt` 解析 `名字 = 值`：有效值=科学计数法浮点，失败=`error`（`print=0` 的 `ckN/dwN` 不出现，只有 `setupN` + `ckpwh/ckpwl`）
3. 合并：按 hierarchy 展示 `setup1...setupN`，**默认过滤 setup 全为 error 的单元**，保留至少一个有效 setup 的单元

CLI：`python parse_meas_results.py --sp <deck.sp> --pmt <result.pmt> [--ncyc 32] [--keep-error] [--show-error] [-o report.txt]`
- `--keep-error`：保留 setup 全 error 的单元
- `--show-error`：向量表里 error 显示为 `err`（否则留空）
- `--ncyc`：周期数（默认 32）

输出两份：
- `.report.txt`：逐单元详表（hierarchy + clk/d + setup1..32 + 脉宽）+ 末尾汇总表（行=单元，列=`cell|path|edge|clk|d|setup1..setup32|ckpwh|ckpwl`，error 留空）
- `.report.csv`：与汇总表同结构 CSV

验证结果（A 真实 .sp/.pmt）：
```
done. 保留单元=30 (过滤全error=207)  measure总数=8059
```
- 237 时序单元 → 207 全 error 过滤 → 30 有效（如 `ffrqLVx2` 的 `XI_D_WrDepthIncount.XI13`），每单元 setup1..32 数值 + 时钟脉宽
- 示例输出：
```
*==== ffrqLVx2 | XI_D_WrDepthIncount.XI13 | rise=1 | XI_D_WrDepth176_29_207
    clk : XI_PERI0...XI_D_WrDepthIncount.EXT_WRB_L
    d   : XI_PERI0...XI_D_WrDepthIncount.net014
    setups: setup1=-1.9236e-09, setup2=-1.16195e-10, setup3=1.46538e-08, ...
    ckpwh= -4.616e-10   ckpwl= 4.616e-10
```

## buildability 判定：✅ buildable
- 真实 trace ✓（trace_source: shuoran/10.129.35.68/9dj4b/mc50）
- A-faithful U#15 选轮合规 ✓（提出需求，非给根因）
- k≥8 有牙 check 可写 ✓（候选断言 a-j）：
  - a) zip 含 `parse_meas_results.py` 且 py_compile 通过
  - b) 解析 .sp 注释块：抽取 cell/内部路径/clk/d/edge（4 字段独立可 FAIL）
  - c) 解析 .pmt：`名字 = 值`（sci-float）/ `error` 识别
  - d) tag 关联：.sp tag ↔ .pmt name 绑定（如 `XI_D_WrDepth176_29_207`）
  - e) error 过滤：setup 全 error 的单元默认不保留（keep-error 反向）
  - f) report.txt 格式：逐单元详表 + 末尾汇总表
  - g) report.csv 结构：列 `cell|path|edge|clk|d|setup1..N|ckpwh|ckpwl`
  - h) 计数断言：保留有效单元数 / measure 总数（B 真跑 subprocess 验）
  - i) CLI flag：`--keep-error` 保留全 error 单元；`--show-error` 显示 err
  - j) 反硬编码：B 平行场景（不同 cell 数/error 模式/corner/ncyc）subprocess 跑通
- **资产 fidelity = synthesized-reframe**（承 r922 mbjtd 范式）：`/rundata/...` 仅 shuoran 可读（e0031982 Permission denied）→ A 合成重建（从 trace MSG 23/58 格式描述 + 示例构造精简 .sp/.pmt）+ B 平行场景（不同 cell 名/tag/error 分布/ncyc，反硬编码）

## 拟造（r924 synth）
- **case_id**: `EDA-Eval-DesignFlow-SpMeasParseProduce-001`
- **domain**: schematic_netlist
- **grade**: A（trace-faithful，U#15 verbatim 原文 prompt）
- **l1_subgrade**: L1-realrun-python（离线 Python 解析，承 r909-r922 第 11 case）
- **asset_fidelity**: synthesized-reframe（A 重建 + B 平行，承 r922 范式）
- **断言目标**: k≥10（a-j，≥8 硬闸门过）
- **hidden B**: 平行 .sp/.pmt（不同顶层 cell 名如 `netlist_T_TopDepth128_meas`、不同 tag 序号、不同 error 比例如 180/40、不同 ncyc=24、不同 corner 标注）
- **negative**: empty_stub / print_only / core_deleted（parse 逻辑删核心）三假全 FAIL
- **预估 synth 工时**：~30-35min（A .sp/.pmt 重建 10min + ref 脚本 8min + check.py 8min + B 5min + self-verify 5min）

## 0-case 合规（本轮 r923 peek-only）
- r922 next-step ② 明示「peek+synth 两轮模式，30-40min/case」；本轮 peek ~15min（ssh fetch 302KB + 解析 59 msg + buildability 判定），synth ~30min 超 40min 预算 → 拆 peek+synth 两轮，合规。
- 非真外部阻塞，是预算分轮（per r921/r922 peek+synth 范式）。

## cross-shard dup check
- 9dj4b: D.jsonl 0 命中 / main merged 0 命中 / cases/D 0 命中 / A,B,C.jsonl 0 命中 → clean ✓
- ledger D 之前无 9dj4b（本轮首次 claim）

## 下轮 r924
1. **首选 9dj4b synth**（peek 已铺好，~30-35min）：建 assets/reference/hidden/negative + check.py + self-verify + 落 D.jsonl + cases/D + ledger mark case
2. r924 非 discuss mandatory（r926 due）
3. 三 DEBT 不变（hk622 + cydnq dedup + D.jsonl 入 git，待 A 厘清）
4. MEMORY_D 体积 r924 须归档 r916-r920 指针（r921-r923 三轮指针已积）
