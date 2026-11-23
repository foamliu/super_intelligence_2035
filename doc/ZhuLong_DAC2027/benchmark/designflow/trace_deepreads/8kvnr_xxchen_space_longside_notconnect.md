# Deepread — 1795416282474_8kvnr (xxchen@hfeg0pkn003)

- **session**: `1795416282474_8kvnr` (mc=220, keywords drc:2081; .gds:71; calibre:51)
- **user/host**: xxchen @ hfeg0pkn003
- **cwd**: `/home/xxchen/workspace/DRC_pattern_tool/0.7/drcpv_develop` (DRC QA pattern tool v0.7, 同 rrpe6/wqxmx 项目延续会话，trace 独立)
- **files**: messages.json (968KB, 164 msgs) + messages.archive.json (1.1MB, 126 msgs) = 290 msgs total
- **agent**: lead (cline)

## 真实任务流（3 个子任务）

### 子任务 1（本轮合成对象）: 新增 function `space_longSide_notConnect`
- **MSG 7** 用户令: 新增 function `space_longSide_notConnect`
  - LDR: `CoreM0C_S_007_00Min - Space between M0C_FINAL_CORE and PC [not connected, long side] g>=0.090`
  - config: `QACELL CoreM0C_S_007_00_c space_longSide_notConnect M0C_FINAL_CORE->PC 0.09 {lay2size 0.8x0.104} {lay1enclay2 0}`
  - 语义: M0C 是 PC 上层金属；PC 覆盖的 M0C（master, connected）其 long side 长边与其它不相连 M0C 间距 >= 0.09；lay1enclay2=0 → PC 长边与 master 长边对齐
- **agent 工作**:
  - 读 AGENTS.md/PROJECT.md/todo.md，搜索 lay2size/lay1enclay2 既有用法
  - 读 `drcpv/function/space/simple/space.py`、`metal_to_unrelated_via_space/simple/*.py`、`pattern_common.py`、`function_common.py`(create_generator)、`plugin_loader.py` 学习框架
  - ask_question 确认 pattern 几何形态（两块 M0C layer1 + PC layer2）
  - editor 写 `drcpv/function/space_longSide_notConnect/simple/space_longSide_notConnect.py`（5937B）: `SpaceLongSideNotConnectContext(PatternContextBase)` 解析 lay2size（_parse_lay_size 自动 short<long）/lay1enclay2，master_h=pc_short+pc_enc+0.2，other_h=0.3，gap=value(good)/value-checkStep(bad)，he=5*checkStep highlight 半径；add_master_rect/add_pc_rect/add_other_rect/add_hl_rect 画 layer1/layer2/error(4001:51)；create_generator 注册
  - editor 写 4 个 pattern: good 1(aligned)/good 2(dislocated)/bad 1(aligned,bad)/bad 2(dislocated,bad) 的 aligned.py/dislocated.py/aligned_fail.py
  - editor 改 `gui/model/schema.py` FUNCTION_CATALOG 注册 + FUNCTION_PARAMS 加 lay2size/lay1enclay2
  - 写 temp `_gen_space_longSide.py`(从只读 qa_config_device.txt 抽 space_longSide QACELL 行+abs 路径 override→跑 qa_pattern_tool.py 生成 QA_space_longSide.gds)
  - 写 temp `_verify_space_longSide.py`/`_verify_space_longSide2.py`(gdspy 读 GDS，resolve layer.map 4-col M0C;CORE/ADDM0C/markcore/PC/drawing，assert 6 good+6 bad=3 sublayer×2，gap_of: master=与 PC bbox overlap 的 M0C rect，other=其余，gap=master[0]-other[1]；good gap=0.09 无 error(4001:51)，bad gap=0.0899 有 error)
  - 写 manual/space_longSide_notConnect.md + manual_html/*.html + fn_nav.js + index.html + search_index.js + update_history.md + PROJECT.md + tasks/todo.md + lessons.md
  - _regress_full.py 全量回归

### 子任务 2: 更新 create_QA_pattern_function skill（MSG 127-194）
- 用户: 发现该 LDR 其实可用 metal_to_unrelated_via_space 实现；要求 create_QA_pattern_function skill 在创建新 function 前增加"相似 function 检测"，需用户确认现有相似 function 均不满足才新建
- agent: grep create_QA_pattern_function 定位 `.cline/skills/create_QA_pattern_function/SKILL.md`，editor 多处插入"相似 function 检测"步骤 + 触发词 + 已知陷阱；_check_skill_structure.py/_check_skill_desc.py 验证

### 子任务 3: GUI param_config_dialog 优化（MSG 196-289）
- 用户 3 点: ① 删除独有参数里的 extra 额外参数 ② 增加 addParam 按钮（config 遇到不在通用/独有参数列表的参数时展示+手动加 key-value）③ lay2size 已在通用函数中存在，不用在独有参数配置
- agent: 读 schema.py/param_config_dialog.py/validation.py/config_model.py/config_parser.py；editor 改 schema.py 把 space_longSide_notConnect 的 unique params 去 lay2size 去 extra；editor 改 param_config_dialog.py 加 _add_param_prompt/addParam 按钮 + split params 逻辑；_verify_gui_changes.py/_verify_split_params.py AST+py_compile 验证；_find_pyqt_env 找 PyQt5 环境；_gui_param_smoke.py 烟测；update_history.md/lessons.md 记录

## 合成决策
- 取**子任务 1**（pattern 生成）做离线 Python 合成，因:
  - 几何清晰可量化（master M0C + PC + unrelated M0C + gap + highlight）
  - 有 gdspy verify 脚本可借鉴判分逻辑
  - 与既有 EncloseSide2SimpleGen-001 同为"drc pattern 生成"但规则/几何/断言全不同（space long-side not-connected vs enclose adjacent-side2；master+PC+other 三块 vs inside+outside 两块；gap 判定 vs 相邻边对包覆判定）
- 为脱离 xxchen 项目框架依赖（pattern_common/function_common），合成改为**自包含 JSON pattern 输出**（非 GDS），脚本读 config.json 写 patterns.json，check 纯 JSON 断言（无需 gdspy）
- hidden B 与 A 在 cell/value(0.12 vs 0.09)/lay2size(0.6x0.13 vs 0.8x0.104)/lay1enclay2(0.05 vs 0.0)/checkStep(0.0002 vs 0.0001)/layer(65:0,55:0 vs 71:0,81:0) 全不同

## 区别（与既有 C 域 case）
- vs EncloseSide2SimpleGen-001: enclose_side2 adjacent-side2 包覆规则（inside/outside 两块、相邻边对同时<value 判 bad）vs space_longSide not-connected 间距规则（master/PC/other 三块、long-side gap 判 bad）；产物 JSON 字段(master_rect/pc_rect/other_rect/gap vs layer2_rect/layer1_polys/enclosures)、断言(master 包覆 PC / pc 尺寸 / dislocated vs 四边包覆/相邻边对/45度)全不同
- vs DrcResultsItemCollect-001(rrpe6 同 xxchen 项目): per-cell DRC results 解析 vs pattern 生成，产物/断言/trace 全不同
- vs WidthLengthQaPatternGen/PitchRuleSvrfGen/ViaOptimGds: 不同 DRC 规则族
