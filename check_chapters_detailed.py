#!/usr/bin/env python3
import os
import re

def parse_readme_table():
    """解析README.md中的章节表格"""
    with open('chapters_v0_4/README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取章节表格部分
    table_pattern = r'\|\s*(\d+(?:-\d+)?)\s*\|\s*`([^`]+)`\s*\|\s*《([^》]+)》\s*\|'
    matches = re.findall(table_pattern, content)
    
    chapter_map = {}
    for match in matches:
        chapter_num = match[0]
        file_name = match[1]
        chinese_title = match[2]
        chapter_map[file_name] = (chapter_num, chinese_title)
    
    return chapter_map

def extract_title_from_file(file_path):
    """从文件中提取标题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
    
    # 尝试匹配 "# 第X章：标题"
    match = re.search(r'#\s*第[零一二三四五六七八九十百千万\d]+章[：:]\s*(.+)', first_line)
    if match:
        return match.group(1).strip()
    
    # 尝试匹配 "# 《标题》"
    match = re.search(r'#\s*《(.+)》', first_line)
    if match:
        return match.group(1).strip()
    
    # 尝试匹配 "# 标题"
    if first_line.startswith('#'):
        title = first_line.lstrip('#').strip()
        # 去除可能的中文标点
        title = re.sub(r'^[：:]\s*', '', title)
        return title
    
    return first_line

def check_all_chapters():
    chapter_map = parse_readme_table()
    print(f"从README解析到 {len(chapter_map)} 个章节")
    print("=" * 80)
    
    chapter_dir = 'chapters_v0_4'
    all_files = os.listdir(chapter_dir)
    chapter_files = [f for f in all_files if f.endswith('.md') and re.match(r'\d+', f)]
    
    issues = []
    checked_files = set()
    
    for file_name in sorted(chapter_files):
        # 处理15_5特殊文件
        if file_name == '15_5-han-civilization-sealing.md':
            # 这个文件对应第16章
            expected_file = '16-han-civilization-sealing.md'
            if expected_file in chapter_map:
                chapter_num, expected_title = chapter_map[expected_file]
                file_path = os.path.join(chapter_dir, file_name)
                actual_title = extract_title_from_file(file_path)
                
                if actual_title != expected_title:
                    issues.append(f"❌ {file_name} (对应第{chapter_num}章): 标题不匹配")
                    issues.append(f"   期望: 《{expected_title}》")
                    issues.append(f"   实际: {actual_title}")
                else:
                    print(f"✅ {file_name} (对应第{chapter_num}章): 标题匹配 《{expected_title}》")
                checked_files.add(expected_file)
                continue
        
        # 检查文件是否在README中
        if file_name not in chapter_map:
            # 检查是否是其他章节的变体
            matched = False
            for expected_file in chapter_map:
                # 检查文件名是否相似（忽略数字前缀）
                base_name1 = re.sub(r'^\d+-', '', file_name)
                base_name2 = re.sub(r'^\d+-', '', expected_file)
                if base_name1 == base_name2:
                    chapter_num, expected_title = chapter_map[expected_file]
                    file_path = os.path.join(chapter_dir, file_name)
                    actual_title = extract_title_from_file(file_path)
                    
                    if actual_title != expected_title:
                        issues.append(f"❌ {file_name} (对应第{chapter_num}章): 标题不匹配")
                        issues.append(f"   期望: 《{expected_title}》")
                        issues.append(f"   实际: {actual_title}")
                    else:
                        print(f"✅ {file_name} (对应第{chapter_num}章): 标题匹配 《{expected_title}》")
                    checked_files.add(expected_file)
                    matched = True
                    break
            
            if not matched:
                issues.append(f"⚠️  {file_name}: 在README表中未找到对应章节")
            continue
        
        # 正常检查
        chapter_num, expected_title = chapter_map[file_name]
        file_path = os.path.join(chapter_dir, file_name)
        actual_title = extract_title_from_file(file_path)
        
        # 检查文件名中的章节编号
        file_num_match = re.match(r'(\d+)-', file_name)
        if file_num_match:
            file_num = file_num_match.group(1)
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
        
        checked_files.add(file_name)
    
    # 检查README中有但文件系统中不存在的文件
    for file_name in chapter_map:
        if file_name not in checked_files:
            # 检查是否有_5变体
            if '16-han-civilization-sealing.md' == file_name:
                # 已经有15_5文件对应
                continue
            issues.append(f"❌ {file_name}: README中列出但文件不存在")
    
    print("=" * 80)
    if issues:
        print("发现问题:")
        for issue in issues:
            print(issue)
        
        # 生成修复建议
        print("\n" + "=" * 80)
        print("修复建议:")
        for issue in issues:
            if "标题不匹配" in issue:
                # 提取文件名和期望标题
                match = re.search(r'❌ (.+?):', issue)
                if match:
                    file_name = match.group(1)
                    # 找到期望标题
                    title_line = issue.split('\n')[1]
                    title_match = re.search(r'期望: 《(.+)》', title_line)
                    if title_match:
                        expected_title = title_match.group(1)
                        print(f"文件 {file_name} 的第一行应修改为: # 《{expected_title}》 或 # 第X章：{expected_title}")
            elif "文件编号不匹配" in issue:
                print(f"文件 {file_name} 应重命名以匹配章节编号")
            elif "README中列出但文件不存在" in issue:
                print(f"需要创建文件 {file_name} 或更新README表格")
    else:
        print("所有章节检查通过！")
    
    return issues

if __name__ == '__main__':
    check_all_chapters()