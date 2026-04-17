#!/usr/bin/env python3
import os
import re

# 读取 chapters_v0_4/README.md 中的章节表格
def parse_readme_table():
    with open('chapters_v0_4/README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取章节表格部分
    # 表格格式：| 章节 | 文件 | 中文标题 | 核心意象 |
    # 使用正则表达式匹配表格行
    table_pattern = r'\|\s*(\d+(?:-\d+)?)\s*\|\s*`([^`]+)`\s*\|\s*《([^》]+)》\s*\|'
    matches = re.findall(table_pattern, content)
    
    # 构建映射：文件 -> (章节号, 中文标题)
    chapter_map = {}
    for match in matches:
        chapter_num = match[0]  # 章节号，如 "01" 或 "27-28"
        file_name = match[1]    # 文件名，如 "01-linwei-morning.md"
        chinese_title = match[2]  # 中文标题，如 "晨钟"
        chapter_map[file_name] = (chapter_num, chinese_title)
    
    return chapter_map

def check_all_chapters():
    chapter_map = parse_readme_table()
    print(f"从README解析到 {len(chapter_map)} 个章节")
    print("=" * 80)
    
    # 获取所有章节文件
    chapter_dir = 'chapters_v0_4'
    all_files = os.listdir(chapter_dir)
    chapter_files = [f for f in all_files if f.endswith('.md') and re.match(r'\d+', f)]
    
    issues = []
    
    for file_name in sorted(chapter_files):
        if file_name not in chapter_map:
            # 检查是否有带 _5 的文件（如 15_5-han-civilization-sealing.md）
            if '_5-' in file_name:
                # 这是 15_5 文件，需要特殊处理
                base_name = file_name.replace('_5-', '-')
                if base_name in chapter_map:
                    # 使用基名称对应的映射
                    chapter_num, expected_title = chapter_map[base_name]
                    file_path = os.path.join(chapter_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                    
                    # 提取实际标题
                    actual_title_match = re.search(r'#\s*第[零一二三四五六七八九十百千万\d]+章：(.+)', first_line)
                    if actual_title_match:
                        actual_title = actual_title_match.group(1).strip()
                    else:
                        actual_title = first_line.replace('#', '').strip()
                        # 尝试其他格式
                        if '：' in actual_title:
                            actual_title = actual_title.split('：', 1)[1].strip()
                    
                    if actual_title != expected_title:
                        issues.append(f"❌ {file_name}: 标题不匹配")
                        issues.append(f"   期望: 《{expected_title}》")
                        issues.append(f"   实际: {actual_title}")
                    else:
                        print(f"✅ {file_name}: 标题匹配 《{expected_title}》")
                    continue
                else:
                    issues.append(f"⚠️  {file_name}: 在README表中未找到对应章节")
                    continue
            else:
                issues.append(f"⚠️  {file_name}: 在README表中未找到对应章节")
                continue
        
        chapter_num, expected_title = chapter_map[file_name]
        file_path = os.path.join(chapter_dir, file_name)
        
        # 读取文件第一行
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        
        # 提取实际标题
        # 格式可能是 "# 第一章：晨钟" 或 "# 第一章：晨钟" 等
        actual_title_match = re.search(r'#\s*第[零一二三四五六七八九十百千万\d]+章：(.+)', first_line)
        if actual_title_match:
            actual_title = actual_title_match.group(1).strip()
        else:
            # 尝试其他格式
            actual_title = first_line.replace('#', '').strip()
            if '：' in actual_title:
                actual_title = actual_title.split('：', 1)[1].strip()
        
        # 检查文件名中的章节编号
        file_num_match = re.match(r'(\d+)-', file_name)
        if file_num_match:
            file_num = file_num_match.group(1)
            # 处理章节号如 "27-28" 的情况
            expected_num = chapter_num.split('-')[0] if '-' in chapter_num else chapter_num
            if file_num != expected_num:
                issues.append(f"❌ {file_name}: 文件编号不匹配")
                issues.append(f"   期望章节号: {expected_num}")
                issues.append(f"   文件编号: {file_num}")
        
        # 检查中文标题
        if actual_title != expected_title:
            issues.append(f"❌ {file_name}: 标题不匹配")
            issues.append(f"   期望: 《{expected_title}》")
            issues.append(f"   实际: {actual_title}")
        else:
            print(f"✅ {file_name}: 标题匹配 《{expected_title}》")
    
    # 检查README中有但文件系统中不存在的文件
    for file_name in chapter_map:
        if file_name not in chapter_files:
            # 检查是否有 _5 变体
            if '15-' in file_name:
                alt_name = file_name.replace('15-', '15_5-')
                if alt_name in chapter_files:
                    continue
            issues.append(f"❌ {file_name}: README中列出但文件不存在")
    
    print("=" * 80)
    if issues:
        print("发现问题:")
        for issue in issues:
            print(issue)
    else:
        print("所有章节检查通过！")
    
    return issues

if __name__ == '__main__':
    check_all_chapters()