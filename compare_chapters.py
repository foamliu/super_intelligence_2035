#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较 chapters 和 chapters_new 两个目录的差异
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def get_chapter_info(directory):
    """获取指定目录下的所有章节文件信息"""
    chapters_dir = Path(directory)
    if not chapters_dir.exists():
        return []
    
    files = list(chapters_dir.glob("*.md"))
    
    chapter_info = []
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            line_count = len(lines)
            
            # 提取标题
            title = ""
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            # 提取章节编号
            chapter_num = None
            # 尝试从文件名提取数字
            match = re.match(r'(\d+)', file_path.name)
            if match:
                chapter_num = int(match.group(1))
            
            # 如果没有数字前缀，尝试从标题提取
            if chapter_num is None:
                title_match = re.search(r'第[一二三四五六七八九十百千]+章|第\d+章|chapter\s*\d+', title, re.IGNORECASE)
                if title_match:
                    # 尝试提取数字
                    num_match = re.search(r'\d+', title_match.group())
                    if num_match:
                        chapter_num = int(num_match.group())
            
            chapter_info.append({
                'file': file_path.name,
                'num': chapter_num,
                'title': title,
                'lines': line_count,
                'content': content[:500] + '...' if len(content) > 500 else content  # 前500字符作为摘要
            })
    
    # 按章节编号排序
    chapter_info.sort(key=lambda x: x['num'] if x['num'] is not None else 999)
    return chapter_info

def compare_directories():
    """比较两个目录的内容"""
    print("=" * 80)
    print("《超级智能2035》chapters vs chapters_new 对比报告")
    print("=" * 80)
    
    # 获取两个目录的信息
    old_chapters = get_chapter_info("chapters")
    new_chapters = get_chapter_info("chapters_new")
    
    print(f"\n【目录概览】")
    print(f"chapters 目录: {len(old_chapters)} 个文件")
    print(f"chapters_new 目录: {len(new_chapters)} 个文件")
    
    # 创建文件名的映射
    old_files = {c['file']: c for c in old_chapters}
    new_files = {c['file']: c for c in new_chapters}
    
    # 分析文件命名模式
    print(f"\n【文件命名模式对比】")
    print(f"chapters 命名示例:")
    for c in old_chapters[:5]:
        print(f"  - {c['file']}")
    if len(old_chapters) > 5:
        print(f"  ... 共 {len(old_chapters)} 个文件")
    
    print(f"\nchapters_new 命名示例:")
    for c in new_chapters[:5]:
        print(f"  - {c['file']}")
    if len(new_chapters) > 5:
        print(f"  ... 共 {len(new_chapters)} 个文件")
    
    # 统计章节编号覆盖
    print(f"\n【章节编号覆盖】")
    old_nums = {c['num'] for c in old_chapters if c['num'] is not None}
    new_nums = {c['num'] for c in new_chapters if c['num'] is not None}
    
    all_nums = sorted(old_nums | new_nums)
    missing_in_old = new_nums - old_nums
    missing_in_new = old_nums - new_nums
    
    print(f"chapters 有编号的章节: {len(old_nums)} 章 (编号范围: {min(old_nums) if old_nums else 'N/A'} - {max(old_nums) if old_nums else 'N/A'})")
    print(f"chapters_new 有编号的章节: {len(new_nums)} 章 (编号范围: {min(new_nums) if new_nums else 'N/A'} - {max(new_nums) if new_nums else 'N/A'})")
    
    if missing_in_old:
        print(f"\n⚠ chapters 缺少的章节编号: {sorted(missing_in_old)}")
    if missing_in_new:
        print(f"\n⚠ chapters_new 缺少的章节编号: {sorted(missing_in_new)}")
    
    # 详细的章节对比
    print(f"\n【详细章节对比】")
    print("-" * 80)
    
    # 按编号创建映射
    old_by_num = {c['num']: c for c in old_chapters if c['num'] is not None}
    new_by_num = {c['num']: c for c in new_chapters if c['num'] is not None}
    
    for num in sorted(all_nums):
        old_ch = old_by_num.get(num)
        new_ch = new_by_num.get(num)
        
        print(f"\n第 {num:02d} 章:")
        
        if old_ch and new_ch:
            # 两者都有
            print(f"  chapters:      {old_ch['file']}")
            print(f"                 标题: {old_ch['title'][:50]}{'...' if len(old_ch['title']) > 50 else ''}")
            print(f"                 行数: {old_ch['lines']}")
            print(f"  chapters_new:  {new_ch['file']}")
            print(f"                 标题: {new_ch['title'][:50]}{'...' if len(new_ch['title']) > 50 else ''}")
            print(f"                 行数: {new_ch['lines']}")
            
            # 比较差异
            if old_ch['lines'] != new_ch['lines']:
                diff = new_ch['lines'] - old_ch['lines']
                print(f"  📊 行数差异: {diff:+d} 行")
            if old_ch['title'] != new_ch['title']:
                print(f"  📝 标题不同")
        elif old_ch:
            # 只有旧版
            print(f"  chapters:      {old_ch['file']} ({old_ch['lines']} 行)")
            print(f"  chapters_new:  ❌ 无对应章节")
        elif new_ch:
            # 只有新版
            print(f"  chapters:      ❌ 无对应章节")
            print(f"  chapters_new:  {new_ch['file']} ({new_ch['lines']} 行)")
    
    # 总结
    print(f"\n【总结】")
    print("-" * 80)
    print(f"chapters 目录结构:")
    print(f"  - 文件采用编号-类型-主题 格式 (如: 00-preface.md, 01-interlude-body.md)")
    print(f"  - 包含前言、间奏、章节、尾声、附录等多种类型")
    print(f"  - 共 {len(old_chapters)} 个文件")
    
    print(f"\nchapters_new 目录结构:")
    print(f"  - 文件采用纯数字编号格式 (如: 01-linwei-morning.md)")
    print(f"  - 主要为连续编号的章节内容")
    print(f"  - 共 {len(new_chapters)} 个文件")
    
    # 检查特殊文件（非章节内容）
    print(f"\n【特殊文件对比】")
    old_special = [c for c in old_chapters if c['num'] is None or c['num'] == 0]
    print(f"chapters 特殊文件:")
    for c in old_special:
        print(f"  - {c['file']}: {c['title'][:40] if c['title'] else '无标题'}")
    
    # 行数统计对比
    print(f"\n【行数统计对比】")
    if old_chapters:
        old_lines = [c['lines'] for c in old_chapters]
        print(f"chapters:     总 {sum(old_lines)} 行, 平均 {sum(old_lines)/len(old_lines):.1f} 行/文件")
    if new_chapters:
        new_lines = [c['lines'] for c in new_chapters]
        print(f"chapters_new: 总 {sum(new_lines)} 行, 平均 {sum(new_lines)/len(new_lines):.1f} 行/文件")

if __name__ == '__main__':
    compare_directories()