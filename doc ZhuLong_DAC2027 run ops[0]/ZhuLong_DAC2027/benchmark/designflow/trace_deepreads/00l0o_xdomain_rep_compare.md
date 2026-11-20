# 深读 1792718147360_00l0o — jinsongl@hfeg0plg97 (mc=24, analog_context)

**session**: `/home/jinsongl/.cline/data/sessions/1792718147360_00l0o/1792718147360_00l0o.messages.json` (300KB, 52 msgs)
**扫描 kw**: analog:374;waveview:44;cadence:26;synopsys:17;drc:10;pyaether:9;aether:9;virtuoso:7

## 真实任务（U#0 逐字原文，produce task）
> 对于目录下的这两个文件 3.1_ChkXDomain_1.5_reuse.rep，他们的格式都是相同的 请帮我分析两个文件的异同点，有哪些节点两个都报告了 并且除了编号以外其他都相同，另外将不同的都报告出来，分成三个文件 一个是该节点在两个报告中都有，但是报错内容还有其他差异 一个文件是只在old中有的节点 一个是只在new中有的节点

U#21（追加，把脚本变成可复用 skill）：
> 我后续经常有比较这样rep文件的需求，可以把上面的这个写成一个skill吗

## 输入文件（真实，在 /home/jinsongl/ 下）
- `3.1_ChkXDomain_1.5_reuse.rep_old` — 42731 行 / **8541** 个 Dev 节点
- `3.1_ChkXDomain_1.5_reuse.rep_new` — 38531 行 / **7701** 个 Dev 节点
- Synopsys PrimeSim CCK ERC 报告（ChkXDomain 跨域电压检查）

## .rep 文件格式（CCK）
```
*
* Synopsys Inc.
* PrimeSim (TM) CCK ...
* Global Information:
*   version=2.0 ...
* CCK Command: ChkXDomain
*
Dev #1: xictop.xi_array16g_t.xi_array2g_bgab01...mn1
  Subinfo: ddr5top array16g_t array2g_top ... ntn_lv
  Attributes: gDom=hb_vblhsfrefci_l<0>, dsDom=vblh!, gPminVal=2.0, dPminVal=0.8, sPminVal=0.8
  Status: cross domain between G and S/D Vgmin > Vdsmin

Dev #2: ...
  Subinfo: ...
  Attributes: gmax=1.1, dmax=0.0, smax=0.0, gmin=1.1, dmin=0.0, smin=0.0, gDom=vcc!, sDom=vss!, dDom=vcc! vss!
  Status: gate cannot fully turnoff this device
...
* CCK Command Footer
* Total number of devices: 8541
```
- 每条记录：`Dev #N: <层级实例路径>` + `Subinfo:` + `Attributes:` + `Status:`（缩进 2 空格）
- **两种 Attributes 变体**：gDom/dsDom/gPminVal/dPminVal/sPminVal（G-S/D 跨域）vs gmax/dmax/smax/gmin/dmin/smin/gDom/sDom/dDom（gate turnoff）
- 节点身份 = `Dev #N:` 后的**完整层级路径**；`Dev #N` 是「编号」，比对时**忽略**
- body = Subinfo + Attributes + Status 行（去尾空格）

## 助手产出（gold，U#0→#20）
`compare_chkxdomain.py`（first script，硬编码路径）→ 跑通产出 4 个 .rep + 4 个 list .txt：
- `1_common_identical.rep` — 两报告都有且 body 完全相同（忽略 Dev #）= **5328**
- `2_common_diff.rep` — 都有但 body 有差异 = **681**（OLD/NEW 并排）
- `3_only_old.rep` = **2532**
- `4_only_new.rep` = **1692**
- `list_common_identical.txt` / `list_common_diff.txt` / `list_only_old.txt` / `list_only_new.txt`（编号路径列表）

U#21→#44：参数化成 `compare_rep.py` skill（`--old --new --out --prefix`），跑通复现同一组数字。

## gold 算法核心（compare_rep.py）
1. `parse_records(path)`：行状态机；遇 `^Dev #\d+[:：]\s*(.*)$` 开始新记录，path=group(1)；后续非空 stripped 行入 body/lines；flush 入 records 列表。`*` 注释/header/footer 行被自然跳过（path 为 None 时不收集）。
2. `classify(old, new)`：按 path 建 index（`setdefault(path,[]).append`，**重复 path 全保留**）；common = paths 交集；`b_old=[r["body"] for r in old_idx[p]]` vs `b_new`（**list of bodies 比较**，处理重复 path）；b_old==b_new → identical 否则 diff；差集 → only_old/only_new。
3. `write_outputs`：identical/only_old/only_new 直接 dump 记录原 lines；common_diff 用 `===== / NODE: / ----- OLD ----- / ----- NEW -----` 并排渲染；list 文件按 `i. path` 编号。
4. `summarize`：4 类计数。

## 关键正确点 / 易错点
- **Dev # 编号忽略**：同 path 同 body 但 Dev #5(old) vs #12(new) 必须 identical（naive 逐行 diff 会误判 diff）
- **重复 path**：同 path 多条记录，body 列表整体比较（不是单条）
- **两种 Attributes 变体**都要能解析（不能只认 gDom/dsDom）
- **header/footer `*` 注释**不进任何记录（path None 时跳过）
- only_old/only_new 输出**原 lines**（保留 Dev #、Subinfo 等原貌），不是只输出 path
- common_diff 必须同时含 OLD 和 NEW 两段（便于人工对照）
- 编号 i. 在 list 文件里从 1 起、连续

## B-grade 合成方向
真实文件含 DRAM 真实层级（ddr5top/array16g/...）42K 行不可沙盒复刻 → 合成小规模 CCK 格式 .rep：
- 可见 A（inputs_A/old_A.rep + new_A.rep，~28/24 节点，chipA.ia_* 命名，覆盖 identical/diff/only_old/only_new + 重复 path + 两种 Attributes 变体 + Dev#编号忽略探针）+ example_output
- 隐藏 B（hidden/inputs_B/old_B.rep + new_B.rep，~36/30 节点，socB.ib_* 命名，A/B 名完全不相交反硬编码，含重复 path 且 body 不同 的 tricky case）
- SUT 交付 `xdomain_rep_compare.py(--old --new --out --prefix)`，纯 stdlib，禁 subprocess/socket/urllib/requests/eval/exec/os.system/禁读 ref/hidden
- check.py 14 条件 a-n：独立 oracle（正则解析 + 重组分类，与 reference 行状态机结构不同）+ 子进程真跑 SUT + 4 类 path 集合逐类 == oracle + body 内容正确 + common_diff 含 OLD/NEW 并排 + Dev#编号忽略探针 + 反硬编码 A + 无 B 字面量 + 3-seed md5

## 维度正交
既有 D analog_context case 多为 sim report/oppoint/特性化/统计/老化/SHMOO/IV curve/ERC tcl 生成/SPF 电阻路径 — 本 case =「CCK ChkXDomain ERC 报告解析 + 按层级路径去编号分类（identical/diff/only_old/only_new）+ 重复 path body 列表比对 + 并排 diff 渲染」，机制/产物全不同。

DEBT: 0
