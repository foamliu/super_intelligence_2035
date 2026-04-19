#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将《超级智能2035》v0.5版本的所有markdown章节合并成一个A5 Word文档
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


def get_chapter_files():
    """获取01-47章节文件，排除README等其他文件"""
    chapters_dir = Path("chapters_v0_7")
    # 只匹配 01- 到 47- 开头的md文件
    files = [f for f in chapters_dir.glob("*.md") if re.match(r'^\d{2}-', f.name)]
    
    # 按文件名排序（01-, 02-, ... 47-）
    def sort_key(f):
        match = re.match(r'(\d+)-', f.name)
        if match:
            return int(match.group(1))
        return 999
    
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


def parse_markdown_line(line):
    """解析markdown行，返回文本和级别"""
    line = line.rstrip()
    
    # 标题
    if line.startswith('# '):
        return line[2:].strip(), None, 1, 'heading'
    elif line.startswith('## '):
        return line[3:].strip(), None, 2, 'heading'
    elif line.startswith('### '):
        return line[4:].strip(), None, 3, 'heading'
    elif line.startswith('#### '):
        return line[5:].strip(), None, 4, 'heading'
    
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
    
    while i < len(lines):
        line = lines[i]
        
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
        text, image_path, level, line_type = parse_markdown_line(line)
        
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
    # 左右边距设置约18mm，使正文宽度约112mm
    # 10.5pt字体，每行约26-28个中文字符
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)


def main():
    print("开始合并《超级智能2035》v0.7版本章节...")
    
    # 创建Word文档
    doc = Document()
    
    # 设置A5纸张大小 (148mm x 210mm)
    section = doc.sections[0]
    section.page_width = Cm(14.8)
    section.page_height = Cm(21.0)
    
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
    run = subtitle.add_run('v0.7 版本')
    set_chinese_font(run, 'SimHei', 16, bold=True)
    
    doc.add_page_break()
    
    # 添加前言
    print("添加前言...")
    foreword_path = Path("chapters_v0_7/foreword.md")
    if foreword_path.exists():
        with open(foreword_path, 'r', encoding='utf-8') as f:
            foreword_content = f.read()
        process_markdown_content(doc, foreword_content, "foreword.md")
        doc.add_page_break()
    else:
        print("警告：未找到前言文件 foreword.md")
    
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
        # if i > 1:
        doc.add_page_break()
        
        # 处理内容
        process_markdown_content(doc, content, file_path.name)
    
    # 添加页码
    print("添加页码...")
    add_page_numbers(doc)
    
    # 保存文档
    import time
    timestamp = time.strftime("%m%d_%H%M")
    output_file = f'超级智能2035_v0.7_A5_{timestamp}.docx'
    doc.save(output_file)
    print(f"\n完成！文档已保存为: {output_file}")
    print(f"共处理 {len(chapter_files)} 个章节")
    print("提示：请在Word中打开文档，按Ctrl+A全选后按F9更新目录字段")
    print("如果仍有乱码，请确保系统安装了SimSun（宋体）和SimHei（黑体）字体")


if __name__ == '__main__':
    main()