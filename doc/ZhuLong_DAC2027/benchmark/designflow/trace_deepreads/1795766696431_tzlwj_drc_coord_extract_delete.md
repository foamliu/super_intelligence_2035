# Deepread — tzlwj (stivens@hfeg0plg91, mc229, layout_aether/physical_verify)

## Trace 溯源
- session: 1795766696431_tzlwj.messages.json (128 msgs, 747KB)
- user: stivens @ hfeg0plg91 (10.129.32.114-ish plg91)
- keywords: drc:1055; pyaether:284; aether:127; dbget:105; calibre:96; lvs:77; .lef:53; cellview:38
- trace_source: real cline session, stivens 真实 DRC 清理工作流

## 真实意图（用户原话 idx2/idx3）
layout 路径 /proj/train/drgqa_V0/libs/drgqa_array_core_train/test/layout/layout.oa。
当 autovia / powerfill 工具 deck 错误，会在某些 layer 打出海量错误 pattern（top 层量级大），
手删困难、直接遍历 layout 检索太慢。思路：从 DRC 结果(test.drc.out)直接提取错误 pattern 坐标，
再通过 select by line/point 删除接触此坐标的 layer，**限定同一层防误删**。
"接下来我们先实现提取坐标"。后续(idx5)以 HSP_S_001_00/HSP_S_002_00 两条 rule 为例实现删除脚本。
最终(idx6)把整个 flow 生成 skill。

## assistant 工具链
list_allowed_files → read test.drc.out → editor write parse_drc_out.py (iter v1→v4, 加 CN 仿射变换取整)
→ run_approved_command 验证 → dump HSP_S_001/002 坐标 → RAG search pyAether API (dbGetTrueOverlapsEx/dbDelete)
→ SandBox run_code pyAether 验证 → editor write delete_hsp_by_drc.py → editor write skill
(SKILL.md + scripts/delete_shapes_by_drc.py + references/drc_out_format.md)

## 关键产物
1. parse_drc_out.py: 解析 Calibre/Argus DRC ASCII 结果，逐 RULE 提取 polygon 顶点，
   施加 CN 仿射变换(X=a·x+b·y+tx, Y=c·x+d·y+ty, 自内向外逐层)到顶层坐标，输出 JSON
   (rules→[{points,bbox,centroid,closed}], +layout_path/precision/system)
2. delete_shapes_by_drc.py: 读 DRC → 解析 → 限 --layer(默认HSP) + --rules 白名单 →
   dbGetTrueOverlapsEx(cv, bbox, layer, purpose) 空间索引查询 → dbDelete，dry-run 默认

## DRC report 格式 (Calibre/Argus ASCII)
```
<RULE_NAME>                              <- 规则名行
<n> <n> <n> <Weekday> <Month> <day> <HH:MM:SS> <year>   <- 日期行(规则起点标识)
LAYOUT_PRECISION 10000
LAYOUT_PATH /path/test.gds
LAYOUT_SYSTEM GDSII
SUMMARY_FILE /path/test.drc.sum
RuleCheckOrder: <n>
Rule File Pathname: /path/.calibreDRC.rule.use_db
RULE <RULE_NAME> {
; <description>
<rule body>
}
p <序号> <顶点数>                          <- polygon 块头
CN <cell> c <a> <b> <c> <d> <tx> <ty> <flag>   <- 可选 instance 上下文(可多个,自内向外)
<x> <y>                                    <- 顶点(dbu 整数,局部系)
...
p <序号> <顶点数>
CN <cell2> c <a2> <b2> <c2> <d2> <tx2> <ty2> <flag2>
...
```
CN 仿射: X=a·x+b·y+tx, Y=c·x+d·y+ty; 多个 CN 自内向外逐层施加得顶层坐标;
无 CN 或 CN test (单位阵 1 0 0 1 0 0) 即顶层坐标。

## LIVE 分类: LIVE-NA
deliverable=parse_drc_out.py(纯 Python 文本解析, 确定性输出). check 独立 oracle 重新解析 B 的 DRC report
逐坐标比对, 非真 EDA 工具产物依赖. §2.1 桩体检 Q2=否: shape-correct-but-wrong-coords 骗不过 oracle.
judge_layers=[L0,L1].

## 去重体检
全 C cases 扫 "drc" + "parse" + "coord" + "extract": DrcRunsetBlankDiag / DrcQaRunDiag / DrcWaiveScreener
均为 runset/waiver/QA 意图, 无 "DRC report 坐标提取+CN仿射" 题. gohxq(DRC runset diag)不同.
⇒ 不重复, 选定.
