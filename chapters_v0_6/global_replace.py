import os
import re

# 定义替换规则
replacements = [
    # 主要术语替换
    (r'OpenAI', '北极星智能'),
    (r'普罗米修斯', '星云'),
    (r'中国路线', '开源/分散路线'),
    (r'美国路线', '闭源/集中路线'),
    (r'硅谷模式', '闭源垄断模式'),
    (r'中关村模式', '开源公地模式'),
    (r'中国选择了约束', '深智科技选择了约束'),
    (r'美国的路径是危险的', '闭源、不可审计的集中式AI是危险的'),
    (r'中国方案', '开源分散方案'),
    (r'美国方案', '闭源集中方案'),
]

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Updated: {filepath}')
            return True
        return False
    except Exception as e:
        print(f'Error processing {filepath}: {e}')
        return False

def process_directory(directory):
    updated_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.md') and filename not in ['revise_guide_v0.6.md', 'revise_guide_v0.6_v2.md', 'revise_guide_v0.6_v3.md', 'revise_guide_v0.6_v4.md', 'revise_guide_v0.6_v5.md', 'revise_guide_v0.6_v6.md', 'revise_guide_v0.6_v7.md', 'rename_chapters.py', 'global_replace.py']:
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                if replace_in_file(filepath):
                    updated_files.append(filename)
    
    print(f'\nTotal files updated: {len(updated_files)}')
    return updated_files

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    process_directory('.')