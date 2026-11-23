# deepread: z9h81 — xxchen DRC Pattern QA GUI (drcpv) 参数语法校验

- session: `1795084452944_z9h81.messages.json`
- user/host: xxchen @ hfeg0plg18 (scan ip 172.16.8.163)
- mc=321, 224 msgs (114 user / 110 assistant), tools: editor×66, read_files×15, run_approved_command×24
- domain: physical_verify (DRC pattern tooling)
- workspace: `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`

## 真实用户意图（USER 原话要点）

- USER[0] 上下文：drcpv PyQt5 GUI 已建成（17 模块：model/{config_model,config_parser,schema}, generate/{generator,gds_view_bridge}, ui/{config_page,qacell_page,param_config_dialog,function_select,placeholder_pages}, app.py/main.py）。config 模型含 TOOL/DEVICE/LDR/VIRLAYER/QACELL/GROUP 段；QaCell.ldr_desc 为 GUI-only 不序列化；分组按工具语义 `?`->`.*`。已验证 model round-trip（68 QACell/12 DEVICE/2 LDR/28 VIRLAYER/3 GROUP，0 errors）。
- USER[1] run.sh 在 RHEL6 节点报 GLIBC_2.15/2.14/2.17 not found → 自动探测 native `_python_real` vs 捆绑 glibc-2.17 包装器 `bin/python`。
- USER[15] 优化 QA pattern GUI：① QACELL 收起 bug（收起后只留 groupName，再点展开无反应）② 边框丑，要 Qt 优美。
- USER[75] 点参数配置崩溃：`gds_view.py mouseMoveEvent ... self._coord_cb(sp) TypeError: lambda() missing 1 required positional argument: 'y'`。
- USER[99] 优化 QA pattern GUI：② 参数配置 gdsView 框太窄，整体 X 拉大约 2 倍；④ 从 manual 提取每个参数用法，参数名可点击弹窗看解释；⑤ **参数保存后自动检查参数语法是否合法**；⑥ TOOL 页面按 type 分区块，key+文本框。
- USER[188] TOOL 页面文本框调小，一排两块；添加选项去掉（TOOL 参数固定）；TOOL key 也可点击看解释。

## 关键交付（assistant 工具链）

- `param_help.py`（4 edits，10KB）：解析 `manual/<function>.md` 的 `## 参数解释` 表（5 列：参数|填写位置|类型|默认值|说明），跳过分隔行；`function_param_help(fn)` 返回 `{param:{pos,type,default,desc}}`；`FRAMEWORK_HELP` 手维护框架参数（auxRegion/layer1_device/lay1size/waive/...）；新增 `tool_param_help()` 解析 `manual/QA_tool_main.md` 的 `### 1. TOOL` 段第二张表（参数|类型|缺省|说明），key 去反引号。
- `validation.py`（2 edits，4KB）：`validate_cell(cell, model)` 返回 `[(field,msg)]`：
  1. `value` 列空 → "value 列不能为空 (规则阈值/关键字)。"
  2. 必填 Params：`info.pos.startswith("Params")` AND `info.default=="必填"` 且 `cell.get_param(param)` 空 → "必填参数缺失。"（EDIT2 收紧：原版误把 layer1/value 列名行当 Params，收紧为只认 pos startswith "Params"）
  3. choice：`schema` 里 `type=="choice"`，取值不在 options（大小写不敏感）→ "取值必须是 X / Y / X/Y 之一。"
  4. 数字：`info.type=="数字"`，取值非数字 → "'<v>' 应为数字 (um)。"；`_is_num` 容忍尾缀 `GRID`/`um`；`_is_size` 跳过 `WxL`（含 `x`）；空值跳过。
  - NA 规则（`cell.is_na`）跳过不校验。
- `ui/qacell_page.py`（6 edits）：DragReorderTable 新增 bannerClicked 信号 + set_banner_resolver；refresh() 每行显式 setRowHidden(False/True)（修复收起 bug：原版只 setRowHidden(True) 从不 False，行一旦隐藏永远隐藏）；_make_banner 加箭头 ▸/▾ + "(N 条)"。
- `ui/param_config_dialog.py`（10 edits）：左表单 + 右 gdsView + 刷新；参数名可点击弹窗（param_description）；保存前跑 validate_cell，有错警告不落盘。
- `generate/gds_view_bridge.py`（3 edits）：on_coord 改单参处理器（修复 lambda(x,y) 崩溃），_show_coord(sp) 换算 μm 显示坐标标签。
- `theme.py`（新）：扁平现代浅色 QSS（蓝主色 #1a5fb4）全局统一。
- `run.sh`（2 edits）：自动探测节点 glibc，现代走 native `_python_real`，老 RHEL6 退回捆绑 glibc 包装器 `bin/python`。

## 选料结论

- 不可直接读 xxchen workspace 源文件（group=cad，e0031982 不在 cad），但 messages.json（.cline/data/sessions，rw-rw-r--）可读，validation.py + param_help.py final 内容从 editor new_text 完整还原。
- reframe 为纯 stdlib 离线 `drc_rule_validator.py`：parse_manual + validate_cell(4 规则) + validate_all + main CLI。A 档用 enclose_side2/space_side/width（3 function），B 档 disjoint 用 notch/overlap/area。14 断言 teeth-checkable，反硬编码 A（B 函数/参数/规则号全不同）。
- 与既有 case 正交：LdrLiteralEscapeFix-001(r918 wpu28，DRC pattern 正则字面转义) 是 LDR pattern 匹配器，本校验器是 manual 表解析 + 参数语法校验，无重叠。
