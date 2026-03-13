#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查《超级智能2035》新版本的所有章节（1-12章）
"""

import os
import re
from pathlib import Path

def get_all_chapter_files():
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
    
    return sorted_files

def check_chapter_format():
    """检查章节格式是否符合要求"""
    print("检查所有章节格式...")
    print("=" * 80)
    
    files = get_all_chapter_files()
    
    total_lines = 0
    chapter_stats = []
    
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
            
            # 提取章节编号和标题
            chapter_num = re.match(r'(\d+)', file_path.name).group(1)
            title_line = content.split('\n')[0] if content else ''
            title = title_line[2:] if title_line.startswith('# ') else title_line
            
            stats = {
                'file': file_path.name,
                'num': chapter_num,
                'title': title,
                'lines': line_count,
                'has_title': has_title,
                'has_image': has_image,
                'has_sections': has_sections,
                'has_summary': has_summary,
                'has_preview': has_preview,
                'has_quote': has_quote
            }
            chapter_stats.append(stats)
            
            print(f"第{chapter_num:>2}章: {file_path.name}")
            print(f"  标题: {title}")
            print(f"  行数: {line_count} {'(符合120-150行要求)' if 120 <= line_count <= 150 else f'(超出范围: {line_count}行)'}")
            print(f"  结构检查: {'✓' if has_title else '✗'}标题 {'✓' if has_image else '✗'}图片 {'✓' if has_sections else '✗'}分节 {'✓' if has_summary else '✗'}要点 {'✓' if has_preview else '✗'}预告 {'✓' if has_quote else '✗'}日记")
            print()
    
    avg_lines = total_lines / len(files) if files else 0
    print(f"所有章节（{len(files)}章）总行数: {total_lines}")
    print(f"平均每章行数: {avg_lines:.1f}")
    print("=" * 80)
    
    return chapter_stats

def get_part_info():
    """获取各部分信息"""
    return {
        '第一部分': {'start': 1, 'end': 6, 'name': '身在此山中'},
        '第二部分': {'start': 7, 'end': 12, 'name': '通用性的迷雾'},
    }

def create_summary_report(chapter_stats):
    """创建详细的汇总报告"""
    
    parts = get_part_info()
    
    summary_content = "# 《超级智能2035》新版本章节汇总报告\n\n"
    summary_content += "## 项目进度总览\n\n"
    
    # 计算完成情况
    total_chapters = 30  # 计划总章数
    completed_chapters = len(chapter_stats)
    completion_rate = (completed_chapters / total_chapters) * 100
    
    summary_content += f"- **计划总章数**: {total_chapters}章\n"
    summary_content += f"- **已完成章数**: {completed_chapters}章\n"
    summary_content += f"- **完成进度**: {completion_rate:.1f}%\n\n"
    
    # 各部分进度
    summary_content += "## 各部分完成情况\n\n"
    
    for part_name, part_info in parts.items():
        part_chapters = [c for c in chapter_stats if part_info['start'] <= int(c['num']) <= part_info['end']]
        part_total = part_info['end'] - part_info['start'] + 1
        part_completed = len(part_chapters)
        part_rate = (part_completed / part_total) * 100
        
        summary_content += f"### {part_name}: {part_info['name']}\n"
        summary_content += f"- **计划**: 第{part_info['start']}-{part_info['end']}章（共{part_total}章）\n"
        summary_content += f"- **已完成**: {part_completed}章\n"
        summary_content += f"- **完成率**: {part_rate:.1f}%\n"
        
        if part_completed > 0:
            summary_content += "- **已完成章节**:\n"
            for ch in part_chapters:
                summary_content += f"  - 第{ch['num']}章: {ch['title']} ({ch['lines']}行)\n"
        summary_content += "\n"
    
    # 未开始部分
    summary_content += "### 待完成部分\n\n"
    summary_content += "1. **第三部分: 权力的阴阳** (第13-18章，共6章)\n"
    summary_content += "2. **第四部分: 社会的断层** (第19-24章，共6章)\n"
    summary_content += "3. **第五部分: 全球的秩序** (第25-28章，共4章)\n"
    summary_content += "4. **第六部分: 文明的抉择** (第29-30章+附录，共3章)\n\n"
    
    # 详细章节列表
    summary_content += "## 已完成章节详细信息\n\n"
    
    for stats in chapter_stats:
        summary_content += f"### 第{stats['num']}章: {stats['file']}\n"
        summary_content += f"**标题**: {stats['title']}\n\n"
        summary_content += f"**行数**: {stats['lines']}\n\n"
        summary_content += f"**结构完整性**:\n"
        summary_content += f"- 标题: {'✓' if stats['has_title'] else '✗'}\n"
        summary_content += f"- 图片: {'✓' if stats['has_image'] else '✗'}\n"
        summary_content += f"- 分节: {'✓' if stats['has_sections'] else '✗'}\n"
        summary_content += f"- 要点总结: {'✓' if stats['has_summary'] else '✗'}\n"
        summary_content += f"- 下章预告: {'✓' if stats['has_preview'] else '✗'}\n"
        summary_content += f"- 日记引用: {'✓' if stats['has_quote'] else '✗'}\n\n"
    
    # 格式检查总结
    summary_content += "## 格式检查总结\n\n"
    
    all_checks = ['标题', '图片', '分节', '要点总结', '下章预告', '日记引用']
    check_keys = ['has_title', 'has_image', 'has_sections', 'has_summary', 'has_preview', 'has_quote']
    
    for check_name, check_key in zip(all_checks, check_keys):
        passed = sum(1 for s in chapter_stats if s[check_key])
        total = len(chapter_stats)
        rate = (passed / total) * 100 if total > 0 else 0
        summary_content += f"- {check_name}: {passed}/{total} ({rate:.1f}%)\n"
    
    # 行数统计
    summary_content += "\n## 行数统计\n\n"
    
    lines_by_chapter = [s['lines'] for s in chapter_stats]
    if lines_by_chapter:
        avg_lines = sum(lines_by_chapter) / len(lines_by_chapter)
        min_lines = min(lines_by_chapter)
        max_lines = max(lines_by_chapter)
        
        summary_content += f"- **平均行数**: {avg_lines:.1f}行\n"
        summary_content += f"- **最少行数**: {min_lines}行 (第{min([s['num'] for s in chapter_stats if s['lines'] == min_lines])}章)\n"
        summary_content += f"- **最多行数**: {max_lines}行 (第{min([s['num'] for s in chapter_stats if s['lines'] == max_lines])}章)\n"
        summary_content += f"- **目标范围**: 120-150行/章\n\n"
        
        # 行数分布
        within_target = sum(1 for l in lines_by_chapter if 120 <= l <= 150)
        below_target = sum(1 for l in lines_by_chapter if l < 120)
        above_target = sum(1 for l in lines_by_chapter if l > 150)
        
        summary_content += f"- **符合目标**: {within_target}章 ({(within_target/len(lines_by_chapter))*100:.1f}%)\n"
        summary_content += f"- **低于目标**: {below_target}章 ({(below_target/len(lines_by_chapter))*100:.1f}%)\n"
        summary_content += f"- **高于目标**: {above_target}章 ({(above_target/len(lines_by_chapter))*100:.1f}%)\n"
    
    # 图片检查
    summary_content += "\n## 图片资源检查\n\n"
    
    images_dir = Path("images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*.png"))
        summary_content += f"**图片总数**: {len(image_files)}个\n\n"
        
        summary_content += "**章节图片对应情况**:\n"
        for i in range(1, 13):
            expected_pattern = f"{i:02d}_*.png"
            matching = list(images_dir.glob(expected_pattern))
            if matching:
                summary_content += f"- 第{i:02d}章: {matching[0].name}\n"
            else:
                summary_content += f"- 第{i:02d}章: 未找到对应图片\n"
    else:
        summary_content += "**警告**: images目录不存在\n"
    
    # 下一步建议
    summary_content += "\n## 下一步工作建议\n\n"
    summary_content += "1. **继续第三部分** (第13-18章): 主题为'权力的阴阳'\n"
    summary_content += "2. **确保格式一致性**: 所有章节应遵循标准模板\n"
    summary_content += "3. **检查东方思想融入**: 每章应有明确的东方思想应用\n"
    summary_content += "4. **维护故事连贯性**: 确保林薇人物发展弧线连贯\n"
    summary_content += "5. **准备Word文档合并**: 完成一定章节后生成Word文档\n\n"
    
    summary_content += "## 脚本使用说明\n\n"
    summary_content += "```bash\n"
    summary_content += "# 运行本检查脚本\n"
    summary_content += "python check_all_chapters.py\n\n"
    summary_content += "# 如需合并为Word文档\n"
    summary_content += "pip install python-docx\n"
    summary_content += "python merge_to_word_with_images.py  # 可能需要修改脚本以支持chapters_new目录\n"
    summary_content += "```\n"
    
    output_path = "项目进度总报告.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"已创建详细汇总报告: {output_path}")
    return output_path

def main():
    print("《超级智能2035》新版本章节检查与汇总")
    print("=" * 80)
    
    # 检查章节格式
    chapter_stats = check_chapter_format()
    
    if not chapter_stats:
        print("未找到章节文件！")
        return
    
    # 创建汇总报告
    report_file = create_summary_report(chapter_stats)
    
    print(f"\n完成！共找到 {len(chapter_stats)} 章。")
    
    # 显示简要统计
    parts = get_part_info()
    for part_name, part_info in parts.items():
        part_chapters = [c for c in chapter_stats if part_info['start'] <= int(c['num']) <= part_info['end']]
        if part_chapters:
            print(f"\n{part_name} ({part_info['name']}): {len(part_chapters)}/{part_info['end'] - part_info['start'] + 1} 章完成")
            for ch in part_chapters:
                status = "✓" if all([ch['has_title'], ch['has_image'], ch['has_sections'], ch['has_summary'], ch['has_preview'], ch['has_quote']]) else "⚠"
                print(f"  {status} 第{ch['num']}章: {ch['title']} ({ch['lines']}行)")
    
    print(f"\n详细信息请查看: {report_file}")
    print("\n注：计划总章数为30章，目前已完成前12章。")

if __name__ == '__main__':
    main()