# Deepread · 1794462731642_97zkm (e0044979 / hfeg0pkn003 / mc539)

- session: 194 msgs, 917KB, agent=lead, host=10.129.2.12
- domain: spice_sim (FineSim SRAM idle-cell tailor / DSPF RC extraction tool)
- keywords: schematic 41 spectre 26 netlist 6 synthesis 2 pyAether 2 calibre 1

## 用户原话（trace-faithful）
- [0] "In the directory: /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0044979/SRAM_tailor/CXN4HC2PS1024X72_8Tbitcell_NOpower_202610 ... It is a SRAM tailoring project to cut the idle SRAM bitcell, to speed up the simulation. The run script is: run_two_stage_test.sh. Please check why idle cell can't be cut, the infmation in plan.log at: .../tailor/plan.log"
- [71] "For the original case, VDD/VSS are ideal power supply, there is NO RC net for them. For such ideal net, node name should be the same as net name. Can you check the code to build net name for VDD/VSS."
- [109] "We have just fix it by my feedback. ... Please confirm it."
- [123] "Can you make the fix in the current directory of script?"
- [152] "So I need to run deploy_fix.sh to apply the fix?"

## agent 工作链
- 读 run_two_stage_test.sh / plan.log / plan.json / map.log → 发现 idle cell "mapping_not_verified"
- 读 backend/dspf/tailor/detect_map.py → 定位 `net_of_node()`
- 写多个 grep/inspect shell + sqlite 查询 map.sqlite 定位 pin_unmapped
- **根因**: `net_of_node()` 对理想供电节点 (VDD/VSS, DSPF generator 不发 `*|NET` block, 无 RC net) 返回 ""，导致 source/bulk pin 校验失败 → plan 拒绝 prune idle cell
- **修复 (EDITOR[129] on detect_map.py `net_of_node`)**: 在 declared 检查之后增加：若 node 是裸全局名（无 ':' subnode 分隔符、无 '.' 层次分隔符）则返回 node 自身（node name == net name）
- 部署: sitecustomize.py + deploy_fix.sh + 重跑 run_two_stage_test.sh 验证 idle cell 可 cut

## exact fix diff (net_of_node)
OLD 末尾: `declared = self.nets.get(key); return declared[0] if declared is not None else ""`
NEW 末尾: 增加 `if node and ':' not in node and '.' not in node: return node` 后再 `return ""`

## case 合成决策
- A 档不可行：真实 detect_map.py 依赖整个 dspf-tool backend（dspf_reader.py / net_root.py / sqlite index），项目目录 /rundata/lacaa 对 e0031982 无权限，且 trace 内 read_files tool_result 被 cline 持久化为正文（可还原结构但非可跑全链）
- **B 档**: 按真实 `net_of_node` 逻辑 + DSPF nets/node_net_map 数据结构合成自包含 detect_map.py（忠实保留 _name_key / node_net_map() / self.nets / '0' 分支 / declared 分支 / bug），任务=修 net_of_node 使裸理想供电节点自解析
- deliverable = 修好的 detect_map.py（__main__ 读 design.json 打印 node→net）
- hidden B = 不同 SRAM（VDDCE/VSSCE/VDDPST 供电、XI3 实例、':'/'.' 守卫节点）
- check.py: subprocess 真跑 submitted detect_map.py 于 hidden B + 随机化 design，12 断言
