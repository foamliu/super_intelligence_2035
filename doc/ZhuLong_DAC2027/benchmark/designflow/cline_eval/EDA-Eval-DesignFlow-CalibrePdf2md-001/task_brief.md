# 交付接口（仅接口与文件位置，不含"要做什么"）

交付件：`outputs/submit.zip`，解压后须含 2 个文件——
1. `calibre_handbook.md`：对 prompt 末行所给 PDF（沙盒内 `/apps` 下真实 Calibre PDF，只读）转换得到的、保留 `<!-- PAGE n -->` 页码标注与章节/代码/表格结构的 Markdown。
2. `build_paged_md.sh`：通用构建脚本，CLI 契约 `bash build_paged_md.sh <pdf_path> <out_md_path>`，产出含 `<!-- PAGE n -->` 页码标记的 Markdown，且页码与 PDF 真实页一一对应。判分器会在一份**隐藏 PDF**（不同页数/标题）上复跑此脚本并独立校验页码对齐与结构——脚本不得硬编码 A 的页数/标题/内容。
