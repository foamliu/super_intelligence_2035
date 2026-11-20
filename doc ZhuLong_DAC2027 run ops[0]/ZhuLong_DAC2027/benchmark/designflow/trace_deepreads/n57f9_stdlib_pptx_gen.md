# 深读笔记 · n57f9 — stdlib .pptx 生成（LELE/SADP/SAQP）

- **session**: `1793179786389_n57f9`
- **user / host**: zhiguo1w @ 10.129.40.209 (mc=8, keywords rtl:7;aether:4;pdk:2;waveview:1;pyaether:1)
- **域判定**: eda_other（半导体工艺知识 + stdlib 文档生成；keywords aether/pdk/waveview 来自环境与工艺设计 kit 语境，真实意图=工艺知识总结+PPT 生成，非真实 EDA 工具调用）
- **trace 大小**: 258KB / 81 msgs (66 user + 57 assistant... 实际 81 条)

## 用户意图（逐字，2 轮）

- USER[1] (msg#0): "帮我总结一下目前的半导体制造工艺，LELE/SADP/SAQP工艺的背景和方法，已经各自的优势劣势"
- USER[2] (msg#4): "帮我整理一份ppt出来"

真实意图 = 单轮知识总结 + PPT 交付。属 11-15 任务初衷重审后恢复的合法 explain/doc-generate 任务（旧规则下或被判 analysis-only/weak）。

## agent 工具链与交付

1. msg#1：直接给出 markdown 知识总结（LELE/SADP/SAQP 背景、方法、优劣势，含瑞利判据 CD=k₁·λ/NA）。
2. msg#3-12：检测环境 → Python 3.7.1，**python-pptx 未安装**，pip 因 libffi 缺失无法安装第三方库。
3. msg#16-50：改用**纯 Python 标准库**（zipfile + xml.sax.saxutils + ElementTree）手写合法 OOXML .pptx。脚本 `make_ppt.py` 增量构建：
   - 设计 token（DARK/ACC/LGT 配色）、`rect`/`tb`/`para`/`table`/`step_cards` 辅助函数
   - 13 页幻灯片：封面/目录/背景/LELE 方法/LELE 优劣/SADP/SADP 优劣/SAQP/SAQP 优劣/横向对比表/选型/总结
   - OOXML 打包：[Content_Types].xml / presentation.xml / slideMaster / slideLayout / theme / slideN.xml + rels
4. msg#52-58：运行生成 → `半导体多重图形化_LELE_SADP_SAQP.pptx`（~26.8KB，16:9，13 页）。
5. msg#58-76：写校验器 validate_ppt.py/validate2.py/check_text.py → **35 部件全部 XML 格式良好、关系全部解析、中文内容完好**。
6. msg#80：交付确认。

## 关键工程点（case 工程化依据）

- **stdlib-only** 是真实约束（环境无 python-pptx、无 pip），agent 真实用 zipfile+XML 手写 → 合法 produce-task。
- 交付物 = .pptx（OOXML ZIP 包），可结构化校验（解 zip / XML 格式 / 关系解析 / 幻灯片计数 / 文本提取）→ check() 有牙。
- 用户意图=特定主题（LELE/SADP/SAQP）PPT；按 §5 produce-task reframe 范式，将"特定主题 PPT"工程化为"spec 驱动的 .pptx 生成器"：A=LELE/SADP/SAQP 大纲（SUT 可见），B=不同主题（DUV→EUV 光刻演进）大纲（hidden），check() 真跑 B 验结构。spec 驱动是判定机制（防止硬编码 A），用户意图（半导体多重图形化 PPT）保留于 A 与 prompt。

## case 设计

- case_id: EDA-Eval-DesignFlow-StdlibPptxGen-001
- domain: eda_other / difficulty: L2 / grade: A（trace-faithful 用 USER 原话；参考解基于 trace agent 的 stdlib OOXML 方法重写为 spec 驱动）
- check() 17 断言：① submit.zip 可解压 ② 含 make_pptx.py ③ py_compile ④ stdlib-only ⑤ 跑 B exit0+产出 ⑥ is_zipfile ⑦ Content_Types ⑧ presentation.xml ⑨ XML 格式良好 ⑩ 关系全解析 ⑪ 幻灯片数==spec_B ⑫ 标题来自 spec_B ⑬ bullets 在对应页 ⑭ table 表头/单元格在对应页 ⑮ 16:9 尺寸 ⑯ theme 部件 ⑰ 3 次重跑确定性
- ref PASS 17/17；5 neg 全 FAIL（empty/print-expected/hardcoded-A/not-a-zip/malformed-xml）；§4.9 a/b/c 全 FAIL
