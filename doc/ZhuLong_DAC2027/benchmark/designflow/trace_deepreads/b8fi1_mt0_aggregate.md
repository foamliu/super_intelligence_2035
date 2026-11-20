# b8fi1 — declanzh mt0 aggregate deepread

- sid: `1795139659877_b8fi1` | user: declanzh | host: hfeahpc505 (10.129.33.28) | mc=10 (hspice)
- source: r915 rescan 41 fresh B-domain sids; r923 peek via .75 ssh cat messages.json (1.53MB/551 msg)
- messages.json on .75: `/home/declanzh/.cline/data/sessions/1795139659877_b8fi1/1795139659877_b8fi1.messages.json`

## 真实意图 (user 原话, 逐字)

- msg[0]/[1] (act): `/rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103`
- msg[2] (act): `帮我把这个文件夹下后缀为.mt0的文件数据汇总到一个文档，并给出每个参数的最大/最小值`
- msg[24] (act): `按绝对值/换算成mA为单位`
- 后续 msg[512-525]: 用户把这套 .mt0 解析/分组/单位换算逻辑沉淀成 `fuse-sense` skill (A→mA ×1000, ohm→Mohm /1e6, raw→% ×100, abs min/max, _grouped.txt/_summary.txt) — 本 case 只取前段清晰意图 (msg[2]+[24]): 汇总 .mt0 + per-param max/min + abs + mA。

## 真实行为 (来自 trace)

- 目录 `/rundata/.../core1103` 下 **77 个 .mt0** 文件 (名 `a51_AG_ThickVfsblnPumpCore_rerun.mt0` + `#1..#76.mt0`)
- 每个 .mt0 含**一行数据**，5 列: `i_vfsbln`(正, 注入) `i_vwlp_fsbln`(负, 抽取) `ieff.`(正) `temper`(°C) `alter#`(run 编号)
- .mt0 格式: `$`/`.` 开头是注释/标题行，列名行 (`i_vfsbln ...`)，然后 1 行 5 个 float
- 解析 (assistant msg[17]): 逐行跳过 `$`/`.`/列名/空行，取第一个 5-float 行
- 真实值 (msg[20] run 输出):
  - i_vfsbln:   min=7.724100e-03  max=1.569300e-02
  - i_vwlp_fsbln: min=-5.068600e-02  max=-2.528000e-02
  - ieff:       min=3.018600e-01  max=3.118700e-01
  - 温度跨度含 -40°C (max i_vfsbln) 与 130°C (min i_vfsbln)
- 交付 (assistant `mt0_summary_v2.py`): glob *.mt0 → 每文件取 5-float 行 → 存 A/mA/abs_A/abs_mA/temper/alter/file → console 打印 raw A min/max + abs mA min/max → 写 `core1103_mt0_summary.txt` (标题/来源目录/文件数/单位说明/参数说明/全局 abs min/max 表含 temper+file/原始带符号值表)

## 合成计划: Mt0AggregateGen-001

- A 档 trace-faithful: 用户原话 (msg[2]+[24]) 逐字作 prompt; 真实参数 (3 currents + temper + alter, 77 文件, 真实值域) 作 asset A。
- reframe harness-for-teeth: one-off `mt0_summary_v2.py` (硬编码 3 参数名 + 路径) → 参数化通用 `mt0_aggregate.py` (--dir + --spec{current_columns,temper_column,alter_column} + --out JSON); 输出结构化 JSON (per-param raw_A min/max + abs_mA min/max + argmin/argmax file/temper) 便于 §4.2 结构化断言; 仍兼容文本报告意图 (JSON 即"汇总文档")。
- hidden B: 异参数名 (ivdd/ileak/voffset 替代 i_vfsbln/i_vwlp_fsbln/ieff) + 异文件数 (50 vs 77) + 异值域 + 异温度档 (-55/0/40/95/125 vs -40/25/85/130) + voffset 负值主导 (验 abs 而非 raw) → 验通用性 + anti-hardcode-A。
- check.py 14 断言 (a-n): zip+compile / exit0+stdout / --out JSON 创建+合法 / 确定性字节一致 / file_count==实际 / parsed_count==file_count / params 数==spec / raw_A min/max 匹配独立 oracle / abs_mA min/max 匹配 / abs_mA argmin/argmax file+temper 匹配 / anti-hardcode-A(B 参数名无 A 名) / 负值 abs 正确性(voffset abs_mA.max 对应 raw_A.min) / --out 必需 / --spec 必需。
- 负样本 5: empty / print_expected / core_deleted / hardcode_a / no_abs。
- L1 静态 + subprocess 跑候选 (无需 hspice)。
