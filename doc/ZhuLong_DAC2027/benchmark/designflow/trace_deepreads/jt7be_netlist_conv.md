# 深读笔记 — jt7be (1794191874918_jt7be) · e0039602 @ hfeg0plg103 · mc=311

- user: e0039602，host hfeg0plg103（10.129.8.235），session 1794191874918_jt7be
- 工具画像: 616 netlist / 7 schematic / 4 synthesis / 1 pyAether（netlist 域，digital gate-lib 转换）
- NMSG=189, NUSERINPUT=9（真实用户轮 9 条，其余为 tool_result）
- 私有项目: `/home/e0039602/Documents/verilog_lib_trans_skill/verilog_lib_trans_skill_aifree/` —— 确定性 verilog 门库转换 skill（无 AI 接口，规则引擎把标准门族机械转 `*_base` 叶单元）

## 用户真实意图（按轮）

- **idx0（核心需求/选作 A 档种子）**：「阅读项目了解 resultmap 输出逻辑，修改使 resultmap 只保留成功转换的（识别出无法通过固定规则转换、需调用大模型的，不打印在 resultmap 里），然后跑 final_merged_netlist_digital.v 转换」
  → 交付：改 run_skill.py 的 resultmap 输出（只留 ok，丢弃 needs_llm/unsupported）+ 跑转换
- **idx42（接口收紧）**：「最终 SV outputs/...converted.sv 也改：成功模块写进去，没转换的完全不要写，这个文件里只需要成功了的」
  → converted.sv 只含成功转换的 module 定义，未转换 module 不写
- **idx58**：「重新转换，用 block_name_digital.log 作为 runskill 命令行输入（只转 log 里的）」→ 引入 block-list 白名单
- **idx67**：换另一个 netlist (final_merged_netlist_stdcells_ac.v) + 对应 log 跑
- **idx76**：读 golden (simlib_stdcells_ac_copy.sv)，问 dlybias/dlybiasn 能否固定逻辑转换
- **idx98/99**：给出 dlyrc/dlybiasn 的详细转换规则（buf #(N,N)、dlyrc_base #(.STEP,.TR_D,.TF_D)、specparam tRise/tFall 三段插值），要求按 8 档插值/线性推自动生成延迟参数
- **idx136/138**：「以后遇到这类型都能写对吗」→ 8 档插值通用化

## 本案取材边界

取 **idx0 + idx42 + idx58** 的 clean produce 意图（resultmap 过滤 + converted.sv 只留成功 + block-list 白名单），**不取** idx76+ 的 delay-cell 8 档插值（过度设计特定、依赖 golden 比对，B 档自包含难保真）。门族限标准组合门（inv/invY/nand/nor/aoi/oai/buf/fbs/fbr），无延迟单元。

## 关键产物形态

- 输入: verilog netlist（多个 module 定义，含可转换门族 + 不可转换/custom cell）+ block_list log（白名单 module 名）+ gate→base 规则表（family pattern → base_cell + 端口映射 + 参数模板）
- 输出1 `result_map.csv`: 列 `module,base_cell,status`，**只含 status=ok 行**（block-list 内且匹配规则的可转换 module）；不写 unsupported/needs_llm/非白名单
- 输出2 `converted.sv`: **只含成功转换的 module 定义**（原网表顺序），每个 module 体替换为单个 `<base>_base #(.PARAMS) I0 (.ports...)` 实例，`\`celldefine` 包裹；未转换 module 完全不写
- 转换器须从 JSON 规则文件读映射（通用，不硬编码 A）

## 为什么 B 档 synthesized

私有 netlist（final_merged_netlist_*.v）+ 私有 skill 项目不可复刻；门族→base 映射规则可从 trace + README 提取通用模式。B 档自包含：可见 A（netlist_A.v + block_list_A.log + gate_rules.json）vs 隐藏 B（netlist_B.v + block_list_B.log + gate_rules_B.json），门族集/模块名/参数/白名单全不同反硬编码。
