#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 chapters_v0_9 目录下所有 Markdown 文件中的英文引号为中文引号。

使用方法:
    python fix_quotes.py

功能:
    - 将英文双引号 " 替换为中文左右双引号 " "
    - 将英文单引号 ' 替换为中文左右单引号 ' '
    - 直接修改原文件，不创建备份
"""

import os
import glob
from pathlib import Path


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
                result.append('“')
                double_quote_open = True
            else:
                result.append('”')
                double_quote_open = False
        elif ch == "'":
            if not single_quote_open:
                result.append('‘')
                single_quote_open = True
            else:
                result.append('’')
                single_quote_open = False
        else:
            result.append(ch)

    return ''.join(result)


def process_file(file_path: Path) -> bool:
    """
    处理单个文件，修复引号。
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否进行了修改
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 修复引号
        fixed_content = fix_quotes(original_content)
        
        # 如果没有变化，跳过
        if fixed_content == original_content:
            print(f"  [跳过] 无需修改: {file_path.name}")
            return False
        
        # 写回修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # 统计替换数量
        double_count = original_content.count('"')
        single_count = original_content.count("'")
        
        print(f"  [修复] {file_path.name}: 双引号×{double_count}, 单引号×{single_count}")
        return True
        
    except Exception as e:
        print(f"  [错误] 处理 {file_path.name} 时出错: {e}")
        return False


def main():
    """主函数"""
    # 获取脚本所在目录（chapters_v0_9）
    script_dir = Path(__file__).parent
    
    print(f"开始修复目录: {script_dir}")
    print("=" * 50)
    
    # 查找所有 .md 文件
    md_files = sorted(script_dir.glob("*.md"))
    
    if not md_files:
        print("未找到 .md 文件")
        return
    
    print(f"找到 {len(md_files)} 个 Markdown 文件")
    print()
    
    processed = 0
    modified = 0
    
    for file_path in md_files:
        if process_file(file_path):
            modified += 1
        processed += 1
    
    print()
    print("=" * 50)
    print(f"处理完成: {processed} 个文件, 修改了 {modified} 个文件")
    print()
    print("说明:")
    print("  - 原文件已直接修改")
    print("  - 无备份文件创建")


if __name__ == '__main__':
    main()