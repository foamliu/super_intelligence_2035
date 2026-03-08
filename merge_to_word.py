#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将《超级智能2035》的所有markdown章节合并成一个Word文档，并添加目录
"""

import os
import re
from pathlib import Path

# 需要安装: pip install python-docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


def set_chinese_font(run, font_name='SimSun', font_size=12, bold=False, italic=False):
    """设置中文字体"""
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    # 设置中文字体（关键）
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)


def get_chapter_files():
    """获取所有章节文件，按正确顺序排序"""
    chapters_dir = Path("chapters")
    files = list(chapters_dir.glob("*.md"))
    
    # 按文件名排序（00-, 01-, 02-...）
    def sort_key(f):
        # 提取数字前缀
        match = re.match(r'(\d+)-', f.name)
        if match:
            return int(match.group(1))
        return 999  # 其他文件放最后
    
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
    style.font.size = Pt([18, 16, 14, 12][min(level-1, 3)])
    style.font.bold = True
    
    # 关键：设置中文字体
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimHei')
    
    paragraph = doc.add_paragraph(text, style=style_name)
    
    # 为每个run设置中文字体
    for run in paragraph.runs:
        set_chinese_font(run, 'SimHei', [18, 16, 14, 12][min(level-1, 3)], bold=True)
    
    return paragraph


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
            set_chinese_font(run, 'SimSun', 12, bold=True)
        elif part.startswith('__') and part.endswith('__'):
            # 粗体（下划线形式）
            content = part[2:-2]
            run = paragraph.add_run(content)
            set_chinese_font(run, 'SimSun', 12, bold=True)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            # 斜体（确保不是粗体的星号）
            if not (part.startswith('**') and part.endswith('**')):
                content = part[1:-1]
                run = paragraph.add_run(content)
                set_chinese_font(run, 'SimSun', 12, italic=True)
        elif part.startswith('`') and part.endswith('`'):
            # 行内代码
            content = part[1:-1]
            run = paragraph.add_run(content)
            set_chinese_font(run, 'Courier New', 11)
        else:
            # 普通文本，但可能包含斜体或代码
            # 进一步处理斜体
            sub_parts = re.split(r'(\*[^*]+\*|_[^_]+_|[`][^`]+[`])', part)
            for sub_part in sub_parts:
                if sub_part.startswith('*') and sub_part.endswith('*') and len(sub_part) > 2:
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'SimSun', 12, italic=True)
                elif sub_part.startswith('_') and sub_part.endswith('_') and len(sub_part) > 2:
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'SimSun', 12, italic=True)
                elif sub_part.startswith('`') and sub_part.endswith('`'):
                    content = sub_part[1:-1]
                    run = paragraph.add_run(content)
                    set_chinese_font(run, 'Courier New', 11)
                else:
                    if sub_part:
                        run = paragraph.add_run(sub_part)
                        set_chinese_font(run, 'SimSun', 12)
        
        i += 1


def parse_markdown_line(line):
    """解析markdown行，返回文本和级别"""
    line = line.rstrip()
    
    # 标题
    if line.startswith('# '):
        return line[2:].strip(), 1, 'heading'
    elif line.startswith('## '):
        return line[3:].strip(), 2, 'heading'
    elif line.startswith('### '):
        return line[4:].strip(), 3, 'heading'
    elif line.startswith('#### '):
        return line[5:].strip(), 4, 'heading'
    
    # 列表项
    elif line.startswith('- ') or line.startswith('* '):
        return line[2:].strip(), 0, 'list'
    elif re.match(r'^\d+\.\s', line):
        text = re.sub(r'^\d+\.\s', '', line)
        return text, 0, 'list_numbered'
    
    # 引用
    elif line.startswith('> '):
        return line[2:].strip(), 0, 'quote'
    
    # 代码块标记
    elif line.startswith('```'):
        return "", 0, 'code_marker'
    
    # 代码缩进
    elif line.startswith('    ') or line.startswith('\t'):
        return line.strip(), 0, 'code'
    
    # 表格分隔符
    elif re.match(r'^\|[-\s|]+\|$', line):
        return "", 0, 'table_separator'
    
    # 表格行
    elif line.startswith('|'):
        return line, 0, 'table_row'
    
    # 普通段落
    elif line.strip():
        return line.strip(), 0, 'paragraph'
    
    # 空行
    else:
        return "", 0, 'empty'


def create_table_from_markdown(doc, table_lines):
    """从markdown表格行创建Word表格"""
    if not table_lines:
        return
    
    # 解析表头
    header_line = table_lines[0]
    headers = [cell.strip() for cell in header_line.split('|')[1:-1]]
    
    # 解析数据行（跳过分隔符行）
    data_rows = []
    for line in table_lines[2:]:  # 跳过分隔符
        if line.strip():
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells:
                data_rows.append(cells)
    
    if not headers:
        return
    
    # 创建表格
    table = doc.add_table(rows=1+len(data_rows), cols=len(headers))
    table.style = 'Table Grid'
    
    # 设置表头
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        # 设置表头格式
        for paragraph in header_cells[i].paragraphs:
            for run in paragraph.runs:
                set_chinese_font(run, 'SimHei', 11, bold=True)
    
    # 设置数据行
    for row_idx, row_data in enumerate(data_rows):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, cell_text in enumerate(row_data):
            if col_idx < len(row_cells):
                row_cells[col_idx].text = cell_text
                # 设置单元格格式
                for paragraph in row_cells[col_idx].paragraphs:
                    for run in paragraph.runs:
                        set_chinese_font(run, 'SimSun', 11)
    
    # 添加空行
    doc.add_paragraph()


def process_markdown_content(doc, content, file_name):
    """处理markdown内容并添加到文档"""
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_content = []
    table_lines = []
    in_table = False
    
    while i < len(lines):
        line = lines[i]
        
        # 表格处理
        if line.startswith('|') and not in_code_block:
            table_lines.append(line)
            in_table = True
            i += 1
            continue
        elif in_table and not line.startswith('|'):
            # 表格结束
            create_table_from_markdown(doc, table_lines)
            table_lines = []
            in_table = False
            continue
        
        if in_table:
            i += 1
            continue
        
        # 代码块处理
        if line.startswith('```'):
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
        text, level, line_type = parse_markdown_line(line)
        
        if line_type == 'heading':
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
            process_inline_formatting(p, text)
        
        # 空行不处理（Word自动处理段落间距）
        
        i += 1
    
    # 处理最后可能未结束的表格
    if table_lines:
        create_table_from_markdown(doc, table_lines)


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
    # 设置默认样式
    style = doc.styles['Normal']
    style.font.name = 'SimSun'
    style.font.size = Pt(12)
    # 关键：设置中文字体
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
    
    # 设置列表样式
    for style_name in ['List Bullet', 'List Number']:
        try:
            style = doc.styles[style_name]
            style.font.name = 'SimSun'
            style.element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
        except:
            pass


def main():
    print("开始合并《超级智能2035》章节...")
    
    # 创建Word文档
    doc = Document()
    
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
    run = subtitle.add_run('事缓则圆——在加速时代的生存哲学')
    set_chinese_font(run, 'SimHei', 16, bold=True)
    
    doc.add_page_break()
    
    # 创建目录页
    create_toc_page(doc)
    
    # 获取所有章节文件
    chapter_files = get_chapter_files()
    print(f"找到 {len(chapter_files)} 个章节文件")
    
    # 处理每个章节
    for i, file_path in enumerate(chapter_files, 1):
        print(f"处理第 {i}/{len(chapter_files)} 个文件: {file_path.name}")
        
        # 读取markdown内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加分页符（除了第一章）
        if i > 1:
            doc.add_page_break()
        
        # 处理内容
        process_markdown_content(doc, content, file_path.name)
    
    # 添加页码
    print("添加页码...")
    add_page_numbers(doc)
    
    # 保存文档（使用新文件名避免占用）
    import time
    timestamp = time.strftime("%m%d_%H%M")
    output_file = f'超级智能2035_{timestamp}.docx'
    doc.save(output_file)
    print(f"\n完成！文档已保存为: {output_file}")
    print("提示：请在Word中打开文档，按Ctrl+A全选后按F9更新目录字段")
    print("如果仍有乱码，请确保系统安装了SimSun（宋体）和SimHei（黑体）字体")


if __name__ == '__main__':
    main()