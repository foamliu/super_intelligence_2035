#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将《超级智能2035》v1.1版本的所有markdown章节合并成一个A5 Word文档
"""

import os
import re
from pathlib import Path

# 需要安装: pip install python-docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn


def set_chinese_font(run, font_name='SimSun', font_size=10.5, bold=False, italic=False):
    """设置中文字体"""
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    # 设置中文字体（关键）
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)


def fix_quotes(text: str) -> str:
    """
    将文本中的英文直引号替换为中文弯引号。
    - 英文双引号 " -> 中文左右双引号 " "
    - 英文单引号 ' -> 中文左右单引号 ' '
    """
    result = []
    double_quote_open = False  # 双引号是否处于"开"状态
    single_quote_open = False   # 单引号是否处于"开"状态

    for ch in text:
        if ch == '"':
            if not double_quote_open:
                result.append('"')
                double_quote_open = True
            else:
                result.append('"')
                double_quote_open = False
        elif ch == "'":
            if not single_quote_open:
                result.append(''')
                single_quote_open = True
            else:
                result.append(''')
                single_quote_open = False
        else:
            result.append(ch)

    return ''.join(result)


def get_chapter_files():
    """获取章节文件，包括.5小数章节，排除README等非章节文件"""
    chapters_dir = Path("chapters_v1_1")
    # 匹配 01-, 02-, ..., 22_5-, 23_5-, 41- 等格式的md文件
    # 排除非章节文件（如abstract, foreword, glossary, profiles, appendix等）
    exclude_names = {
        'abstract.md', 'foreword.md', 'glossary.md', 'profiles.md',
        'appendix-practical-handbook.md', 'author-words.md',
        'Cognitive_Warfare.md', 'MARKET.md', 'SOUL.md', 'ZHIHU.md',
        'README.md', 'REVISION_SUMMARY.md', 'V2_0_MANUAL_CHANGES.md',
        'timeline_analysis.md', 'timeline_analysis_revised.md',
        'fix_quotes.py',
    }
    files = [
        f for f in chapters_dir.glob("*.md")
        if re.match(r'^\d{2}([._]\d+)?-', f.name) and f.name not in exclude_names
    ]

    # 按文件名排序（01-, 02-, ... 08-cognitive-miners, 08-ninety-nine-percent, ... 22-, 22_5-, 23_5-, 23-, ... 42-）
    def sort_key(f):
        # 匹配主版本号和可选的小数版本号（支持 . 和 _ 分隔符）
        match = re.match(r'(\d+)(?:[._](\d+))?-', f.name)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else 0
            return (major, minor)
        return (999, 0)

    return sorted(files, key=sort_key)


def add_heading(doc, text, level=1):
    """添加标题，并设置为Word标题样式（用于目录）"""
    # Word的标题级别：Heading 1, Heading 2, etc.
    style_name = f'Heading {level}'

    # 确保样式存在并设置中文字体
    try:
        style = doc.styles[style_name]
    except KeyError:
        style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)

    # 设置样式字体
    style.font.name = 'SimHei'  # 黑体用于标题
    style.font.size = Pt([16, 14, 12, 11][min(level-1, 3)])
    style.font.bold = True

    # 关键：设置中文字体
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')

    paragraph = doc.add_paragraph(text, style=style_name)

    # 为每个run设置中文字体
    for run in paragraph.runs:
        set_chinese_font(run, 'SimHei', [16, 14, 12, 11][min(level-1, 3)], bold=True)

    return paragraph


def add_image_to_doc(doc, image_path, caption=None):
    """添加图片到文档"""
    try:
        # 检查图片是否存在
        if not os.path.exists(image_path):
            print(f"  警告：图片不存在: {image_path}")
            return False

        # 添加图片
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()

        # 插入图片，设置宽度为3.5英寸（适应A5纸张，可用宽度约11.2cm）
        inline_shape = run.add_picture(image_path, width=Inches(3.5))

        # 如果有说明文字，添加在图片下方
        if caption:
            caption_para = doc.add_paragraph()
            caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = caption_para.add_run(caption)
            set_chinese_font(run, 'SimSun', 10, italic=True)

        # 添加空行
        doc.add_paragraph()
        return True

    except Exception as e:
        print(f"  错误：无法添加图片 {image_path}: {e}")
        return False


def parse_image_markdown(line):
    """解析markdown图片语法 ![alt](path)"""
    # 匹配 ![alt text](../images/filename.png) 或 ![alt](path)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    match = re.match(pattern, line.strip())

    if match:
        alt_text = match.group(1)
        image_path = match.group(2)
        return alt_text, image_path

    return None, None


def process_inline_formatting(paragraph, text):
    """处理行内格式（粗体、斜体、代码）"""
    # 模式：粗体 **text** 或 __text__
    # 斜体 *text* 或 _text_
    # 代码 `code`

    # 使用正则表达式分割，保留分隔符
    # 先处理粗体
    parts = re.split(r'(\*\*[^*]+\*\*|__[^_]+__)', text)

    i = 0
    while i < len(parts):
        part = parts[i]

        if part.startswith('**') and part.endswith('**'):
            # 粗体
            content = part[2:-2]
            run = paragraph.add_run(content)
            set_chinese_font(run, 'SimSun', 10.5, bold=True)
        elif part.startswith('__') and part.endswith('__'):
            # 粗体（下划线形式）
            content = part[2:-2]
            run = paragraph.add_run(content)
            set_chinese_font(run, 'SimSun', 10.5, bold=True)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            # 斜体（确保不是粗体的星号）
            if not (part.startswith('**') and part.endswith('**')):
                content = part[1:-1]
                run = paragraph.add_run(content)
                set_chinese_font(run, 'SimSun', 10.5, italic=True)
        elif part.startswith('`') and part.endswith('`'):
            # 行内代码
            content = part[1:-1]
            run = paragraph.add_run(content)
            set_chinese_font(run, 'Courier New', 10)
        else:
            # 普通文本，但可能包含斜体或代码
            # 进一步处理斜体
            sub_parts = re.split(r'(\*[^*]+\*|_[^_]+_|[`][^`]+[`])', part)
            for sub_part in sub_parts:
                if sub_part.startswith('*') and sub_part.endswith('*') and len(sub_part) > 2:
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'SimSun', 10.5, italic=True)
                elif sub_part.startswith('_') and sub_part.endswith('_') and len(sub_part) > 2:
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'SimSun', 10.5, italic=True)
                elif sub_part.startswith('`') and sub_part.endswith('`'):
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'Courier New', 10)
                else:
                    if sub_part:
                        run = paragraph.add_run(sub_part)
                        set_chinese_font(run, 'SimSun', 10.5)

        i += 1


def is_table_line(line):
    """判断是否为markdown表格行（以|开头或以|结尾的行）"""
    stripped = line.strip()
    return stripped.startswith('|') and '|' in stripped[1:]


def parse_table_row(line):
    """解析表格行，返回单元格内容列表"""
    stripped = line.strip()
    # 移除首尾的 |
    if stripped.startswith('|'):
        stripped = stripped[1:]
    if stripped.endswith('|'):
        stripped = stripped[:-1]
    # 按 | 分割单元格
    cells = [cell.strip() for cell in stripped.split('|')]
    return cells


def parse_alignment(cell):
    """解析对齐格式行中的单个单元格，返回 Word 对齐常量"""
    cell = cell.strip()
    left = cell.startswith(':')
    right = cell.endswith(':')
    if left and right:
        return WD_ALIGN_PARAGRAPH.CENTER
    elif right:
        return WD_ALIGN_PARAGRAPH.RIGHT
    else:
        return WD_ALIGN_PARAGRAPH.LEFT


def add_table_to_doc(doc, headers, alignments, rows):
    """向文档中添加 Word 表格"""
    if not headers:
        return

    num_cols = len(headers)
    # 对齐行不生成行，但可能包含额外列信息
    if alignments:
        num_cols = max(num_cols, len(alignments))

    # 数据行数 + 1（表头）
    num_rows = 1 + len(rows)

    table = doc.add_table(rows=num_rows, cols=num_cols, style='Table Grid')

    # 填充表头
    for j, header in enumerate(headers):
        if j >= num_cols:
            break
        cell = table.cell(0, j)
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(header)
        set_chinese_font(run, 'SimHei', 10.5, bold=True)
        # 设置表头单元格底色为浅灰
        from docx.oxml import OxmlElement
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), 'D9D9D9')
        shading_elm.set(qn('w:val'), 'clear')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    # 填充数据行
    for i, row_data in enumerate(rows):
        for j, cell_text in enumerate(row_data):
            if j >= num_cols:
                break
            cell = table.cell(i + 1, j)
            cell.text = ''
            p = cell.paragraphs[0]
            # 设置对齐方式
            if alignments and j < len(alignments):
                p.alignment = alignments[j]
            # 处理单元格内的行内格式（粗体、斜体等）
            process_inline_formatting(p, cell_text)
            # 如果没有产生 runs（纯文本），手动添加
            if not p.runs:
                run = p.add_run(cell_text)
                set_chinese_font(run, 'SimSun', 10.5)

    # 表格后添加空行
    doc.add_paragraph()


def parse_markdown_line(line):
    """解析markdown行，返回文本和级别"""
    line = line.rstrip()

    # 图片
    alt_text, image_path = parse_image_markdown(line)
    if image_path:
        return alt_text, image_path, 0, 'image'

    # 标题
    if line.startswith('# '):
        return line[2:].strip(), None, 1, 'heading'
    elif line.startswith('## '):
        return line[3:].strip(), None, 2, 'heading'
    elif line.startswith('### '):
        return line[4:].strip(), None, 3, 'heading'
    elif line.startswith('#### '):
        return line[5:].strip(), None, 4, 'heading'

    # 表格行
    elif is_table_line(line):
        return line.strip(), None, 0, 'table_row'

    # 列表项
    elif line.startswith('- ') or line.startswith('* '):
        return line[2:].strip(), None, 0, 'list'
    elif re.match(r'^\d+\.\s', line):
        text = re.sub(r'^\d+\.\s', '', line)
        return text, None, 0, 'list_numbered'

    # 引用
    elif line.startswith('> '):
        return line[2:].strip(), None, 0, 'quote'

    # 代码块标记
    elif line.startswith('```'):
        return "", None, 0, 'code_marker'

    # 代码缩进
    elif line.startswith('    ') or line.startswith('\t'):
        return line.strip(), None, 0, 'code'

    # 普通段落
    elif line.strip():
        return line.strip(), None, 0, 'paragraph'

    # 空行
    else:
        return "", None, 0, 'empty'


def process_markdown_content(doc, content, file_name):
    """处理markdown内容并添加到文档"""
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_content = []

    # 表格状态
    table_rows = []      # 收集表格行（原始文本）
    in_table = False

    def flush_table():
        """将收集到的表格行转换为 Word 表格并插入文档"""
        nonlocal table_rows, in_table
        if not table_rows:
            return
        # 第一行是表头
        headers = parse_table_row(table_rows[0])
        alignments = []
        rows = []
        start_idx = 1
        # 第二行如果是对齐行（:---: 等），解析对齐
        if len(table_rows) > 1:
            second_cells = parse_table_row(table_rows[1])
            # 判断是否为对齐行：所有单元格都匹配 --- 模式
            is_align_row = all(
                re.match(r'^:?-{3,}:?$', cell) for cell in second_cells
            )
            if is_align_row:
                alignments = [parse_alignment(cell) for cell in second_cells]
                start_idx = 2
            else:
                # 不是对齐行，作为数据行
                rows.append(second_cells)
                start_idx = 2
        # 其余是数据行
        for row_line in table_rows[start_idx:]:
            rows.append(parse_table_row(row_line))
        add_table_to_doc(doc, headers, alignments, rows)
        table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i]

        # 代码块处理
        if line.startswith('```'):
            flush_table()
            if in_code_block:
                # 代码块结束，添加代码内容
                if code_content:
                    p = doc.add_paragraph()
                    p.style = 'Intense Quote'
                    run = p.add_run('\n'.join(code_content))
                    set_chinese_font(run, 'Courier New', 10)
                    code_content = []
            in_code_block = not in_code_block
            i += 1
            continue

        if in_code_block:
            # 在代码块内，收集代码
            code_content.append(line)
            i += 1
            continue

        # 解析行
        text, image_path, level, line_type = parse_markdown_line(line)

        if line_type == 'table_row':
            # 收集表格行
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(text)
        else:
            # 非表格行，先刷新之前的表格
            flush_table()

            if line_type == 'image':
                # 转换图片路径
                # 从 ../images/xxx.png 转换为 images/xxx.png
                if image_path.startswith('../'):
                    actual_path = image_path[3:]  # 移除 ../
                elif image_path.startswith('./'):
                    actual_path = image_path[2:]  # 移除 ./
                else:
                    actual_path = image_path

                # 添加图片
                add_image_to_doc(doc, actual_path, text if text else None)

            elif line_type == 'heading':
                add_heading(doc, text, level)

            elif line_type == 'list':
                p = doc.add_paragraph(style='List Bullet')
                process_inline_formatting(p, text)
                if not p.runs:
                    run = p.add_run(text)
                    set_chinese_font(run, 'SimSun', 12)

            elif line_type == 'list_numbered':
                p = doc.add_paragraph(style='List Number')
                process_inline_formatting(p, text)
                if not p.runs:
                    run = p.add_run(text)
                    set_chinese_font(run, 'SimSun', 12)

            elif line_type == 'quote':
                p = doc.add_paragraph(style='Quote')
                process_inline_formatting(p, text)
                if not p.runs:
                    run = p.add_run(text)
                    set_chinese_font(run, 'SimSun', 12)

            elif line_type == 'paragraph':
                p = doc.add_paragraph()
                # 添加两个全角空格作为首行缩进
                p.paragraph_format.first_line_indent = Pt(21)  # 两个全角空格约21pt
                process_inline_formatting(p, text)

            # 空行不处理（Word自动处理段落间距）

        i += 1

    # 处理文件末尾可能残留的表格
    flush_table()


def create_toc_page(doc):
    """创建目录页"""
    # 添加分页符
    doc.add_page_break()

    # 添加目录标题
    toc_title = doc.add_paragraph()
    toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = toc_title.add_run('目  录')
    set_chinese_font(run, 'SimHei', 18, bold=True)

    doc.add_paragraph()  # 空行

    # 添加说明
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = note.add_run('（请在Word中按Ctrl+A全选后按F9更新目录）')
    set_chinese_font(run, 'SimSun', 10)

    doc.add_paragraph()  # 空行


def add_page_numbers(doc):
    """为文档添加页码"""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn as oqn

    # 为每个节添加页脚
    for section in doc.sections:
        footer = section.footer
        footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加页码字段
        run = footer_para.add_run()

        # 创建fldChar元素
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(oqn('w:fldCharType'), 'begin')

        instrText = OxmlElement('w:instrText')
        instrText.set(oqn('xml:space'), 'preserve')
        instrText.text = "PAGE"

        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(oqn('w:fldCharType'), 'end')

        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)

        # 设置页码字体
        set_chinese_font(run, 'SimSun', 10)


def setup_document_styles(doc):
    """设置文档样式"""
    from docx.shared import Pt
    from docx.enum.text import WD_LINE_SPACING

    # 设置默认样式
    style = doc.styles['Normal']
    style.font.name = 'SimSun'
    style.font.size = Pt(10.5)  # 五号字 10.5pt
    # 关键：设置中文字体
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

    # 设置行距为单倍行距
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # 设置列表样式
    for style_name in ['List Bullet', 'List Number']:
        try:
            style = doc.styles[style_name]
            style.font.name = 'SimSun'
            style.font.size = Pt(10.5)
            style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
            style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        except:
            pass


def setup_page_margins(section):
    """设置页边距，使每行26-28字"""
    # A5纸张：148mm x 210mm
    # 缩小边距：左右边距约10mm，使正文宽度约128mm
    # 10.5pt字体，每行约29-31个中文字符
    section.left_margin = Cm(1.0)
    section.right_margin = Cm(1.0)
    section.top_margin = Cm(1.2)
    section.bottom_margin = Cm(1.2)


def insert_special_file(doc, file_name, chapters_dir, label=""):
    """如果文件存在，插入特殊文件（前言、摘要、作者的话等）"""
    file_path = chapters_dir / file_name
    if file_path.exists():
        if label:
            print(f"添加{label}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = fix_quotes(content)
        doc.add_page_break()
        process_markdown_content(doc, content, file_name)
        return True
    else:
        print(f"警告：未找到文件 {file_name}")
        return False


def main():
    print("开始合并《超级智能2035》v1.1版本章节...")

    chapters_dir = Path("chapters_v1_1")

    # 创建Word文档
    doc = Document()

    # 设置A5纸张大小 (148mm x 210mm)
    section = doc.sections[0]
    section.page_width = Cm(14.8)
    section.page_height = Cm(21.0)

    # 设置页边距
    setup_page_margins(section)

    # 设置文档样式
    setup_document_styles(doc)

    # 添加封面
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('超级智能2035')
    set_chinese_font(run, 'SimHei', 28, bold=True)

    doc.add_paragraph()

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('v1.1 版本')
    set_chinese_font(run, 'SimHei', 16, bold=True)

    doc.add_page_break()

    # 添加前言
    insert_special_file(doc, "foreword.md", chapters_dir, "前言")

    # 添加摘要
    # insert_special_file(doc, "abstract.md", chapters_dir, "摘要")

    # 添加作者的话
    # insert_special_file(doc, "author-words.md", chapters_dir, "作者的话")

    # 创建目录页
    create_toc_page(doc)

    # 获取所有章节文件
    chapter_files = get_chapter_files()
    print(f"找到 {len(chapter_files)} 个章节文件")

    # 处理每个章节
    glossary_inserted = False
    appendix_inserted = False

    for i, file_path in enumerate(chapter_files, 1):
        print(f"处理第 {i}/{len(chapter_files)} 个文件: {file_path.name}")

        # 读取markdown内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修复中文引号
        content = fix_quotes(content)

        # 添加分页符
        doc.add_page_break()

        # 处理内容
        process_markdown_content(doc, content, file_path.name)

        # 在第39章（算法透明）之后插入术语表
        if not glossary_inserted and re.match(r'^39[._]?-', file_path.name):
            glossary_path = chapters_dir / "glossary.md"
            if glossary_path.exists():
                print("在第39章之后插入术语表...")
                with open(glossary_path, 'r', encoding='utf-8') as f:
                    glossary_content = f.read()
                glossary_content = fix_quotes(glossary_content)
                doc.add_page_break()
                process_markdown_content(doc, glossary_content, "glossary.md")
                print(f"已插入术语表: {glossary_path}")
            else:
                print(f"警告：未找到术语表文件 {glossary_path}")
            glossary_inserted = True

    # 添加实践手册附录
    # insert_special_file(doc, "appendix-practical-handbook.md", chapters_dir, "实践手册附录")

    # 添加人物小传附录（放在全书最后）
    # print("添加人物小传附录...")
    # profiles_path = chapters_dir / "profiles.md"
    # if profiles_path.exists():
    #     doc.add_page_break()

    #     # 添加附录标题
    #     appendix_title = doc.add_paragraph()
    #     appendix_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    #     run = appendix_title.add_run('附  录')
    #     set_chinese_font(run, 'SimHei', 18, bold=True)

    #     doc.add_paragraph()  # 空行

    #     # 读取并处理人物小传内容
    #     with open(profiles_path, 'r', encoding='utf-8') as f:
    #         profiles_content = f.read()
    #     profiles_content = fix_quotes(profiles_content)
    #     process_markdown_content(doc, profiles_content, "profiles.md")
    #     print(f"已添加人物小传附录: {profiles_path}")
    # else:
    #     print(f"警告：未找到人物小传文件 {profiles_path}")

    # 添加页码
    print("添加页码...")
    add_page_numbers(doc)

    # 保存文档
    import time
    timestamp = time.strftime("%m%d_%H%M")
    output_file = f'超级智能2035_v1.1_A5_{timestamp}.docx'
    doc.save(output_file)
    print(f"\n完成！文档已保存为: {output_file}")
    print(f"共处理 {len(chapter_files)} 个章节")
    print("提示：请在Word中打开文档，按Ctrl+A全选后按F9更新目录字段")
    print("如果仍有乱码，请确保系统安装了SimSun（宋体）和SimHei（黑体）字体")


if __name__ == '__main__':
    main()