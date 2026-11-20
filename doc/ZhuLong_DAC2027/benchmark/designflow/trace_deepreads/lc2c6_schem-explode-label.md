# Deepread — 1793755053336_lc2c6 (qunzhu @ hfeg0plg101)

- shard: D · domain: schematic_netlist · mc=29 · nmsg=21 · scan: ssh_eda_search_20261109_224902
- keywords: schematic:169;cellview:132;virtuoso:51;pyaether:31;dbget:29;transistor:23;mosfet:15;aether:11
- model: (lead) · updated 2026-11-04

## 原始任务（user 首轮）
> virtuoso 生成的电路图是乱的，我想给每个节点都用 "L" 快捷键打 label，帮我把管子打散，但是每个节点上都有 label，我自己重新连接即可

## 任务语义
Virtuoso 自动生成的原理图走线杂乱。用户要一个 SKILL/脚本：
1. 给每个 net 打 label（用 net 名作标签，等价手按 "L" 快捷键）
2. 把 MOS 管子「打散」——断开 MOS 器件 pin↔net 的连接
3. 每个节点保留 label，用户据此人工重连
4. 非 MOS 器件（R/C/BJT 等）保持连接

本质 = 原理图 net-labeling + MOS-instance disconnect（schematic_netlist 操作）。

## B-grade 合成方案（self-contained）
真实 SKILL 需 live Virtuoso cellview，不适合自包含沙盒 → 翻译为「Python 脚本读合成 .sch 文本」：
- `.sch` 格式：`INST <path> <cell> <type>` + `NET <name> <driver|PORT> <loads逗号>` + `#` 注释 + malformed 行
- MOS 识别：type 含 `mos|fet`（nmos/pmos/nmos4/pmos4/nfet/pfet）；非 MOS（res/cap/bjt）保留
- 输出三文件：`labels.txt`(net→sanitize label)、`exploded.txt`(MOS pin→net stub)、`summary.json`(7 项计数)
- A 可见样例 + `example_output/`；hidden B 不同结构(11 inst/8 MOS/3 non-MOS/9 net/3 malformed, 含 vdd!/net-a/net+f 需 sanitize)

## 案件产出
- case_id: EDA-Eval-DesignFlow-SchemExplodeLabel-001
- domain: schematic_netlist · layer: L2 · design: A-faithful · heavy: offline
- check.py: 13 条件 a-m（zip/py_compile/三文件/labels 全集/label sanitize/MOS 集合/非 MOS 未漏/MOS pin→net/summary 计数/反硬编码 A/无 B 字面量/3-seed 确定性/malformed 跳过）
- k_rationale == k_check == 13 · ref ALL PASS · negative_selftest: 4 stub FAIL · 3-seed sha256 一致
- degradation 三假(empty_shell/print_only/core_removed) 全 FAIL

## 复用要点
- mc≥30 fresh D 池已枯竭；本次降到 mc=29 + D-dominant 关键词 + 排除 C/B 信号(drc/gds/pex/hspice/liberty/calibre/lvs/cvps)找到 lc2c6
- excl_anchors.txt 是 base64 编码 —— 必须 `base64 -d` 后才能用作 grep -vFf 排除锚（之前未解码导致 parked session 误入候选）
