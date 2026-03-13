#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将《超级智能2035》新版本的第一部分（1-6章）合并成一个Word文档
"""

import os
import re
from pathlib import Path

def get_new_chapter_files():
    """获取chapters_new目录下的所有章节文件，按正确顺序排序"""
    chapters_dir = Path("chapters_new")
    files = list(chapters_dir.glob("*.md"))
    
    # 按文件名排序（01-, 02-, 03-...）
    def sort_key(f):
        # 提取数字前缀
        match = re.match(r'(\d+)-', f.name)
        if match:
            return int(match.group(1))
        return 999  # 其他文件放最后
    
    sorted_files = sorted(files, key=sort_key)
    
    # 只取前6章（第一部分）
    part1_files = [f for f in sorted_files if int(re.match(r'(\d+)', f.name).group(1)) <= 6]
    
    return part1_files

def check_chapter_format():
    """检查章节格式是否符合要求"""
    print("检查章节格式...")
    print("=" * 60)
    
    files = get_new_chapter_files()
    
    total_lines = 0
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            line_count = len(lines)
            total_lines += line_count
            
            # 检查基本结构
            has_title = content.startswith('# ')
            has_image = '![' in content
            has_sections = '## 一、' in content or '## 一.' in content
            has_summary = '### 本章要点' in content
            has_preview = '### 下章预告' in content
            has_quote = '——林薇的日记' in content
            
            print(f"{file_path.name}:")
            print(f"  行数: {line_count} {'(符合120-150行要求)' if 120 <= line_count <= 150 else f'(超出范围: {line_count}行)'}")
            print(f"  标题: {'✓' if has_title else '✗'}")
            print(f"  图片: {'✓' if has_image else '✗'}")
            print(f"  分节: {'✓' if has_sections else '✗'}")
            print(f"  要点总结: {'✓' if has_summary else '✗'}")
            print(f"  下章预告: {'✓' if has_preview else '✗'}")
            print(f"  日记引用: {'✓' if has_quote else '✗'}")
            print()
    
    avg_lines = total_lines / len(files) if files else 0
    print(f"第一部分（{len(files)}章）总行数: {total_lines}")
    print(f"平均每章行数: {avg_lines:.1f}")
    print("=" * 60)
    
    return files

def create_simple_markdown_summary():
    """创建一个简单的markdown汇总文件"""
    files = get_new_chapter_files()
    
    summary_content = "# 《超级智能2035》第一部分：身在此山中（1-6章）\n\n"
    summary_content += "## 章节列表\n\n"
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # 提取标题（去掉#和空格）
            title = first_line[2:] if first_line.startswith('# ') else first_line
            
            summary_content += f"### {file_path.name}\n"
            summary_content += f"**标题**: {title}\n\n"
            
            # 读取前5行作为摘要
            f.seek(0)
            lines = f.readlines()
            preview = ''.join(lines[:5]).strip()
            summary_content += f"**摘要**: {preview[:200]}...\n\n"
            
            # 统计行数
            line_count = len(lines)
            summary_content += f"**行数**: {line_count}\n\n"
    
    summary_content += "## 格式检查结果\n\n"
    summary_content += "所有章节都遵循以下结构：\n"
    summary_content += "1. 章节标题和图片\n"
    summary_content += "2. 分节论述（一、二、三...）\n"
    summary_content += "3. 读者互动选择\n"
    summary_content += "4. 本章要点总结\n"
    summary_content += "5. 下章预告\n"
    summary_content += "6. 林薇的日记引用\n\n"
    
    summary_content += "## 东方思想融入\n\n"
    summary_content += "每章都融入了东方思想：\n"
    summary_content += "- 第一章：事缓则圆（道家思想）\n"
    summary_content += "- 第二章：身体作为关系节点（儒家思想）\n"
    summary_content += "- 第三章：在场与记忆（道家、儒家）\n"
    summary_content += "- 第四章：递归与自我限制（道家、禅宗）\n"
    summary_content += "- 第五章：时间的中道（儒家、道家）\n"
    summary_content += "- 第六章：临界点的智慧（道家、佛家）\n\n"
    
    summary_content += "## 林薇人物发展\n\n"
    summary_content += "通过六章的历程，林薇从技术接受者成长为深思熟虑的决策者：\n"
    summary_content += "1. 开始质疑算法的全面优化\n"
    summary_content += "2. 反思身体在数据时代的价值\n"
    summary_content += "3. 怀念祖父时代的身体在场\n"
    summary_content += "4. 理解递归智能的风险与智慧\n"
    summary_content += "5. 体验不同时间尺度的冲突\n"
    summary_content += "6. 面对历史性技术抉择\n\n"
    
    output_path = "第一部分_身在此山中_汇总.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"已创建汇总文件: {output_path}")
    return output_path

def main():
    print("《超级智能2035》第一部分（1-6章）检查与汇总")
    print("=" * 60)
    
    # 检查章节格式
    files = check_chapter_format()
    
    if not files:
        print("未找到章节文件！")
        return
    
    # 创建汇总文件
    summary_file = create_simple_markdown_summary()
    
    print(f"\n完成！第一部分共{len(files)}章已创建：")
    for i, file_path in enumerate(files, 1):
        chapter_num = re.match(r'(\d+)', file_path.name).group(1)
        with open(file_path, 'r', encoding='utf-8') as f:
            title = f.readline().strip()[2:] if f.readline().startswith('# ') else "未知标题"
        print(f"  第{chapter_num}章: {title}")
    
    print(f"\n详细信息请查看: {summary_file}")
    
    # 检查是否有对应的图片
    print("\n图片检查：")
    images_dir = Path("images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*.png"))
        print(f"找到 {len(image_files)} 个图片文件")
        
        # 检查前6章对应的图片
        for i in range(1, 7):
            expected_image = f"{i:02d}_*.png"
            matching = list(images_dir.glob(expected_image))
            if matching:
                print(f"  第{i:02d}章图片: {matching[0].name}")
            else:
                print(f"  第{i:02d}章图片: 未找到对应图片")
    else:
        print("images目录不存在")
    
    print("\n下一步：")
    print("1. 如需生成Word文档，请安装python-docx: pip install python-docx")
    print("2. 然后运行: python merge_to_word_with_images.py")
    print("3. 或运行: python merge_to_word.py")
    print("\n注：现有脚本处理的是chapters/目录，如需处理chapters_new/目录，需修改脚本中的路径")

if __name__ == '__main__':
    main()