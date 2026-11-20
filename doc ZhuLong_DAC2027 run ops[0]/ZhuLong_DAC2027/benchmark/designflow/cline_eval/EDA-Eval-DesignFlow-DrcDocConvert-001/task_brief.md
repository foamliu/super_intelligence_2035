交付：outputs/submit.zip，内含 md2html.py（通用 markdown→HTML 结构转换器，命令行用法：python3 md2html.py <输入.md> <输出.html>）与 run_logic_notes_zh.html（对所给 run_logic_notes.md 产出的中文 HTML）。
输入文件：run_logic_notes.md（位于工作目录，DRC Connect QA 工具的运行逻辑说明，英文）。
判分：校验 submit.zip 内 HTML 的结构与中文翻译，并独立在一份隐藏输入上重跑 md2html.py 验证其通用性（不可只硬编码本文档的输出）。
