#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量删除书稿中的粗体标记
保留：章节标题、结构性小标题、文档标签
删除：警句式强调、对话强调、内心独白
"""

import os
import re
import sys

# 需要处理的章节目录
CHAPTERS_DIR = "chapters_v1_0"

# 保留粗体的模式（结构性内容）
KEEP_PATTERNS = [
    # 章节标题
    r'^#+\s+',
    # 表格内的粗体（保持表格格式）
    r'\|[^|]*\*\*[^*]+\*\*[^|]*\|',
]

# 需要删除的粗体模式（警句式内容）
REMOVE_PATTERNS = [
    # 普通警句式粗体
    (r'\*\*([^*]+?)\*\*', r'\1'),
]

def should_keep_bold(text):
    """判断是否应该保留粗体"""
    # 章节标题保留
    if text.startswith('#'):
        return True
    # 表格内粗体保留
    if '|' in text and text.strip().startswith('|'):
        return True
    # 文档标签格式保留（如"**模型营养标签**"这类结构性内容）
    if re.match(r'^\*\*[^*]+(?:镜子|标签|组件|优势|引擎|标题)\*\*$', text.strip()):
        return True
    return False

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_count = content.count('**')
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # 检查是否应该保留整行的粗体
        if should_keep_bold(line):
            new_lines.append(line)
            continue
            
        # 处理行内的粗体
        # 保留文档标签类的粗体
        if re.search(r'\*\*[^*]+(?:镜子|标签|组件|优势|引擎|标题|重|层)\*\*', line):
            new_lines.append(line)
            continue
            
        # 删除警句式粗体
        new_line = re.sub(r'\*\*([^*]+?)\*\*', r'\1', line)
        new_lines.append(new_line)
    
    new_content = '\n'.join(new_lines)
    new_count = new_content.count('**')
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    removed_pairs = (original_count - new_count) // 2
    return removed_pairs

def main():
    """主函数"""
    chapters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), CHAPTERS_DIR)
    
    if not os.path.exists(chapters_dir):
        print(f"错误：找不到目录 {chapters_dir}")
        sys.exit(1)
    
    # 处理所有.md文件
    total_removed = 0
    processed_files = []
    
    for filename in sorted(os.listdir(chapters_dir)):
        if not filename.endswith('.md'):
            continue
        if filename.startswith('revise_'):
            continue
        if filename in ['README.md', 'MARKET.md', 'SOUL.md', 'ZHIHU.md', 'Cognitive_Warfare.md']:
            continue
            
        filepath = os.path.join(chapters_dir, filename)
        try:
            removed = process_file(filepath)
            if removed > 0:
                total_removed += removed
                processed_files.append((filename, removed))
                print(f"[OK] {filename}: 删除 {removed} 处粗体")
        except Exception as e:
            print(f"[ERR] {filename}: 错误 - {e}")
    
    # 输出统计
    print(f"\n{'='*50}")
    print(f"处理完成：")
    print(f"- 处理文件数：{len(processed_files)}")
    print(f"- 删除粗体数：{total_removed}")
    print(f"{'='*50}")
    
    # 输出详细清单
    if processed_files:
        print("\n详细清单：")
        for filename, count in processed_files:
            print(f"  {filename}: {count} 处")

if __name__ == '__main__':
    main()