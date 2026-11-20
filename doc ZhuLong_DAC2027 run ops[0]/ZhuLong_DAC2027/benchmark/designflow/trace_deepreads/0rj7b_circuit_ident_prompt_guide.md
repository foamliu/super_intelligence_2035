# Deepread · 0rj7b · 电路识别提示词写法 Q&A

- session: 1792572197494_0rj7b.messages.json
- user: e0022089 @ hfeg0pkn002
- match_count: 24 · domain: spice_sim · 9 msgs / 26KB · trace 在子目录 `1792572197494_0rj7b/` 下
- 旧判定: parked "consultation explain-model-purpose" (r435) · r618 reaudit 复活为可造 (how-to Q&A)
- 合成 case: **EDA-Eval-DesignFlow-CircuitIdentPromptGuide-001** (spice_sim L1 · how-to Q&A → 产出生成式 how-to 指南)

## 用户真实意图（trace 原话）

msg[0]: `请问需要你识别某个路径下的电路，需要如何输入提示词`
msg[8]（追问，未答）: `/proj/ddcpb/V0/libs/ddcpb_digital/RWAbusBnkGapLeft/schematic/sch.oa ，请问这个模型的作用是啥`

用户想知道：要让我（zhulong agent）识别某个路径下的电路，提示词该怎么写。这是 meta-Q&A——
问的是"提示词写法"本身，不是要 agent 立刻去识别某个具体电路。

## 助手工具链与关键产物

1. `get_agent_policy_status` → 策略引擎 enforcing, sessionId, profileIds=[python-runner, shell-runner], readableRootCount=2, writableRootCount=1
2. `list_allowed_files` (depth=2) → 可读根 `/home/e0022089/Desktop`（当前为空）
3. `RAG_MCP_Server__search_apis` ×2 (lang=skill + lang=pyAether, query="读取电路原理图 schematic cellview 打开设计" / "load circuit netlist file read design") → 命中:
   - SKILL 侧: schPinListToSchem, **schHiOpenCellView**, schHiOpenOtherView, **schCheck**, deOpenCellView
   - pyAether 侧: **seGuiShowNetlist**, **dmExportNetlist**, **aeExportNetlistCDLShow**, dmGuiGenNetlistView, mdeSetNetlistViewList
4. 助手产出结构化回答（msg[7]）：
   - **四要素**：① 绝对路径 ② 文件格式 ③ 识别目标 ④ 背景约束（可选）
   - **五类场景模板**：A 网表文件 / B Cadence 原理图 cellview（库/单元/视图）/ C 电路截图 / D GDS 版图 / E 配合仿真波形
   - **注意事项**：路径必须绝对且在可读根内；文本网表准确率最高；Cadence 数据库给"库/单元/视图"三要素；一次一个明确任务；提供上下文提升准确度

## 真实命名（A 档 trace-faithful 重建用）

- 可读根: `/home/e0022089/Desktop`
- 可用配置: `python-runner`, `shell-runner`
- API（SKILL 侧）: schHiOpenCellView / schCheck / dmExportNetlist / seGuiShowNetlist / aeExportNetlistCDLShow / dmGuiGenNetlistView / mdeSetNetlistViewList
- API（pyAether 侧）: dmExportNetlist
- 用户追问路径: `/proj/ddcpb/V0/libs/ddcpb_digital/RWAbusBnkGapLeft/schematic/sch.oa`

## 合成方案

- **form**: how-to Q&A → 产出生成式 how-to 指南（同 AetherHowToGuide-001 首例同族）
- **A 档 trace-faithful**: doc/env_profile.txt 用 trace 真实环境画像 verbatim 重建（user/host/readable_root/profiles/真实 API 目录）；doc/scenario.txt 用用户原话 + focus
- **hidden B 叠加 cross-input guard**: 合成不同环境画像（user ythchen @ hfeg0plg77, readable_root /home/ythchen/workbench, profiles python-runner/skill-runner, pyAether-dominant API 目录: aeGetCurDesign/aeOpenCellView/schCheckFull/dmExportNetlist/aeExportNetlistCDL/aeNetlistToCDL/dmGuiGenNetlistView）——同 archetype + 同四要素/五场景结构约定，名字/路径/API 集 不同
- **任务**: 写 circuit_prompt_guide_gen.py(workdir, out_dir) 解析 doc/env_profile.txt + scenario.txt → prompt_guide.json（12 顶层键）
- **check.py**: 16 断言，独立解析 B 的 env_profile 算期望值（user/host/readable_root/profiles/API 目录/网表导出 API 子集），cross-input 值守卫(e/f/g/h/k) + A-leak 守卫(o: e0022089//home/e0022089/hfeg0pkn002//proj/ddcpb/RWAbusBnkGapLeft/schHiOpenCellView/seGuiShowNetlist/mdeSetNetlistViewList/aeExportNetlistCDLShow/shell-runner 禁现) + 真跑 subprocess + 确定性 3 rerun
- **自验**: ref 16/16 PASS + 4 negs(空壳→d / print-only→c / hardcode-A→e cross-input / deleted-core→k)全 FAIL · k_rationale==k_check==16

## trace-faithful 性

用户原话「请问需要你识别某个路径下的电路，需要如何输入提示词」直接进 scenario.txt 与 prompt；
助手真实环境画像（可读根 / API 目录）verbatim 进 env_profile.txt；
用户追问 `/proj/ddcpb/.../RWAbusBnkGapLeft/schematic/sch.oa` 作为 A-leak 专属 token（B 不可出现），
让 A-leak 守卫有真实"牙"——这是 trace 真实用户意图（追问该 sch.oa），不是人为加难。
