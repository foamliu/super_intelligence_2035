# trace_deepread: z9h81 — DRC Pattern QA GUI core (physical_verify)

- **sid**: `1795084452944_z9h81`
- **user / host**: xxchen / hfeg0plg06 (10.129.32.13) [scan 也命中 hfeg0plg18=172.16.8.163]
- **match_count**: 321 (drc:1421; .gds:50; .lef:41; pdk:30; techfile:24; pyaether:1)
- **domain**: physical_verify
- **session size**: 224 msgs, messages.json 1.06 MB
- **agent tool chain**: editor×66, run_approved_command×24, read_files×15, list_allowed_files×2, search_codebase×1

## 用户意图

xxchen 在 `~/workspace/DRC_pattern_tool/0.6/device_rule1/drcpv` 迭代构建一个
**DRC Pattern QA GUI 工具**（PyQt5，包名 `drcpv`）。会话起点是一个 context
summary（前一会话已完成 brainstorm→spec→implementation→offscreen 验证：68
QACell / 12 DEVICE / 2 LDR / 28 VIRLAYER / 3 GROUP，0 errors，`?`→`.*` group
matching，17 模块 py_compile 全过）。本轮用户提了 5 个 act 类诉求：

1. `bash run.sh` 报 GLIBC_2.14/2.15/2.17 not found（pyqt5-rhel6 env 的
   `_python_real` 与本机 libc 不兼容）。
2. QACELL 收起功能 bug（收起后只剩 groupName，再点展开无反应）；GUI 边框丑。
3. 点参数配置时崩溃：`GdsViewBridge.__init__.<locals>.<lambda>() missing 1
   required positional argument: 'y'`（mouseMoveEvent 回调签名缺 y）。
4. 参数配置 gdsView 框太窄（整体 X 拉大约 2×）；从 manual 提取参数用法做成可
   点击弹窗；参数保存后自动校验语法；TOOL 页改成分块（key+文本框）。
5. TOOL 页文本框调小、一排两块、去掉"添加"（参数固定不可随意加）；TOOL key
   也做成可点击查看解释。

## assistant 关键产出

- 修 GLIBC：换用兼容的 pyqt5 env python；gdsView 加宽；修 lambda 签名
  (`sp` → `x, y`)。
- 抽公共 `ui/widgets.py`：`HelpLabel`（可点击下划线标签）+ `param_popup`。
- `param_help.py` 新增 `tool_param_help()/tool_param_description()`：解析
  `manual/QA_tool_main.md` 的 TOOL 参数表（参数/类型/缺省/说明），strip 反引号
  （`` `GRID` ``→`GRID`）。
- `ui/config_page.py` 的 `ToolPage`：2 列 QGridLayout，文本框 maxWidth 240，
  删掉新增表单。
- 38 项离屏冒烟全 PASS，22 模块 py_compile ALL_OK。

## reframe 子型（本 case）

GUI 包装不可独立判分（依赖 PyQt5 + 显示）。把**非 GUI 核心**提取为独立
fixture-driven judge：给 `config.qa`（QACELL/DEVICE/LDR/VIRLAYER/GROUP/TOOL
六段，`|` 分隔，`#` 注释，`?` 通配）+ `manual.md`（markdown 参数表），输出
`counts/groups/validation/tool_desc/renormal` JSON。覆盖：六段计数、`?`→`.*`
通配+rule 过滤解析、字段数+LDR 数值校验、手册表格反引号剥离+第4列说明提取、
规范化重导出（`?`→`.*`、按段固定顺序、段内按首字段排序、round-trip 守恒）。

## 为什么合法 produce

- 真实 trace 存在（.75 免密 ssh 到 172.16.8.13 取到 messages.json 1.06MB）。
- 真实输入文件（config/manual）位于 xxchen 工作区，核心解析逻辑有明确规格。
- reframe 子型首例：C 域 physical_verify 此前有 StarRC/DSPF/LVS/dont_touch
  类，DRC Pattern QA config 解析+`?`→`.*` group+手册表格提取+规范化重导出
  是新子型，与现有 C case 正交。

## 质量

k=15 (a-o)；ref PASS 15/15；3 neg FAIL distinct（empty_stub→②, print_only→⑮
跨输入守卫, core_deleted→⑨）；§4.9(a) empty zip FAIL；3-seed 确定性 YES；
check() 独立 tmp dir；roundtrip sha256 4b5df470 ✓；C.jsonl 596→597。
