# deepread — dnp2f (junweix @ hfeg0pkn002, mc=50) · schematic cross-hierarchy net highlight

## trace 概况
- session: `1793870525412_dnp2f` / 46 msgs / 135KB / 用户 junweix / host hfeg0pkn002 (10.129.2.11)
- 关键词命中: aether:146; mixed-signal:41; schematic:38; waveview:18; virtuoso:11; pyaether:9; floorplan:9; analog:3
- 工具分类: 14 schematic / 11 virtuoso / 7 pyAether

## 用户轮（仅 2 个真实 user turn）
- msg[2] U#0: 「怎么可以跨层级点亮信号线」(how to cross-hierarchy highlight signal net)
- msg[15] U#1: 「aether 怎么可以跨层级点亮信号线」(同义重述，明确 aether)

> 用户仅提出需求/目标，未指出根因或给出修复方案 → A 档**任务说明**可用原文；但 trace 末尾**无用户接受的工具产物**（见下），故**不可 A-faithful**，做 B-grade synthesized。

## assistant 行为
- msg[1]: 加载「Aether EDA 工具问答」skill，提示用户提问
- msg[3-28]: 一系列 list_allowed_files / search_codebase / editor 写临时检索脚本 / run_approved_command (python-runner) 在 `/home/junweix/.cline/skills/aether-tool-qa/references/*.md` 中 grep 关键词（跨层/高层/点亮/highlight/Trace Net/trace/probe/高亮）
- msg[28] grep 命中: aether_tool_qa.md:322「成组线电路图点亮如何版图线也亮」、:326「开 SDL 模式，再点亮」、:3611「alt+f 只能按下层 PIN 信息往上生成 PIN」等
- msg[29-41]: read_files 读 aether_tool_qa.md / 快捷键速查.md / Part_II_Schematic_Editor.md / Part_V 手册中 Trace Net 参数（原理图 15.1 / 版图 57.8）跨层级选项
- msg[42]: 「已从交流群问答、快捷键速查表和手册交叉检索到完整信息。先清理临时检索脚本，然后给出答案」→ 写 cleanup_tmp.py 删除 find_refs.py/grep_refs.py/grep_manual.py
- msg[44]: run_approved_command cleanup_tmp.py
- msg[45]: **tool_result = `{"error":"code_sidecar_sigterm"}`** ← code sidecar 被信号终止，**最终答案未交付，用户未接受任何结果**

## 金标准判定
- 🚫 无 trace 末尾用户接受的工具产物（session 在 cleanup 阶段被 sigterm，最终答案文本未生成）
- → **A-faithful 不可用**；取 B-grade synthesized：以「跨层级信号线点亮/追踪」为主题，合成可离线验证的 build 任务

## 合成方向（B-grade synthesized, schematic_netlist, L2）
- 主题迁移：cline 里「跨层级点亮信号线」= 在层级化原理图/网表中按名称模式追踪某 net 在所有层级实例中的出现位置 + 完整层级路径
- 合成任务：候选写 `hier_net_trace.py <netlist.sp> <pattern> <out.json>`，解析层级 SPICE 网表（subckt 定义/端口、instance 调用 pin→net 映射、层级路径），按 glob 模式匹配 net，输出结构化 JSON（subckts/matched_nets/occurrences/stats）
- A = sram_col.sp（SramCol→BitCellArray×8 BitCell / SenseAmpCol / ColMux / PrechargeBlk，pattern bl*）；隐藏 B = rf_read.sp（RfReadPath→WordDrv×4 / RbCell×16 / RwAmp / RwlPrech，pattern wl*）——结构/规模/取值/模式全不同，反硬编码
- 判分 L2：subprocess 真跑候选脚本于隐藏 B + 结构化字段断言（subckt 数/instance 数/匹配数/层级路径/端口-内部分类/pin 映射/反硬编码/3-seed 规范化不变性）

## 真实标识符保留
- user=junweix / host=hfeg0pkn002 / ip=10.129.2.11 / session=1793870525412_dnp2f / 路径 `/home/junweix/.cline/...` 全部原值保留（仅本笔记 + jsonl metadata.trace_source）

## 结论
- 选料: dnp2f → B-grade synthesized, schematic_netlist, L2
- case_id: `EDA-Eval-DesignFlow-HierNetTrace-001`
