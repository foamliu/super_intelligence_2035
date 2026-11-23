# qlvo2 — kevin3d FineSim ignore diff analyzer (deepread)

**Session**: 1795008667388_qlvo2.messages.json
**User**: kevin3d @ hfeg0pkn004, mc=56, domain=spice_sim
**Trace**: 79 msgs / 554KB, 2026-11-19

## U0 (msg0) — verbatim A 档需求

用户在 hfeg0plg103 上 grep 了 WOWTOP_10667_idd4r_aabb_FF112v130c 项目的 si.inp，
贴出大量 `.option finesim_ignore="..."` 行（active + `*.option` 注释行混合），
要求与 `IGNORE_PROBE_INST.list` 比对，找出 **生效但未在 list 里登记** 的 ignore name。

si.inp 格式特征：
- active 行：`.option finesim_ignore = "name"` 或 `.option finesim_ignore="name"`
- 注释行：`*.option finesim_ignore = "name"` 或 `***.option finesim_ignore = "name"`
- 多 name 行：`"name1 name2 name3"` （引号内空格分隔）
- 行尾注释：`"name" **B0` （引号外 `**` 后是注释）
- 特殊关键字：`"nan"` 是 FineSim 数值关键字，不是实例名
- 大小写差异：si.inp 用 `xI_` 前缀，inst list 用 `XI_` 前缀

## Assistant msg8 — diff_finesim_ignore.py

assistant 写 Python 脚本解析 si.inp：
1. 逐行扫描，跳过 `*` 开头的注释行
2. 提取引号内 name，拆分多 name 条目
3. strip 尾部空格
4. 排除 `nan` 特殊关键字
5. 与 inst list 做大小写不敏感比对
6. 输出 missing set

结果：7 个 DLDO_* name 需要补进 list（DLDO_ChanRight/Left/Mid/ArrayCtrlx4/AC/B/A）。

## 后续对话

- U15: "active 的 bank 有哪些？" → bank_active_check.py: 16 bank 布局, 13 整 bank ignore → active = B2/BA/BE
- U23: "zpower 筛选写进 aplmmx/ttsc_args" → check_zpower_filter.py 核对配置
- U29+: netlistHeader/netlist zpower 实例分类, rowaddr hierarchy check

## Reframe

取 U0 的核心需求（si.inp finesim_ignore diff analyzer）作为独立 L1 纯 Python case。
`finesim_ignore_diff.py <si.inp> <inst.list> <out.json>` → JSON diff report。

A = kevin3d 真实 si.inp（WOWTOP DDR5, 16 bank, DLDO_*, nan, **B0 注释）
hidden B = 五重 anti-hardcode（DDR6TOP, 8 bank, inf, Vbb*, xI_MemTop, active-commented 反转）
