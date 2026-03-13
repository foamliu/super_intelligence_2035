#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查生成的Word文档内容
"""

import zipfile
import re

def check_docx_content():
    docx_file = '超级智能2035_第一部分_身在此山中.docx'
    
    try:
        # 读取docx文件内容（docx是zip格式）
        with zipfile.ZipFile(docx_file, 'r') as z:
            # 读取document.xml文件
            xml_content = z.read('word/document.xml').decode('utf-8')
            
            # 统计章节标题
            chapter_titles = re.findall(r'<w:t>第[一二三四五六]章.*?</w:t>', xml_content)
            print(f'文档中找到 {len(chapter_titles)} 个章节标题:')
            for i, title in enumerate(chapter_titles[:10], 1):
                title_text = re.sub(r'<[^>]+>', '', title)
                print(f'  {i}. {title_text}')
            
            # 统计图片引用
            image_refs = re.findall(r'<a:blip.*?r:embed="[^"]+"', xml_content)
            print(f'\n文档中包含 {len(image_refs)} 个图片引用')
            
            # 检查是否包含第一部分总结
            if '第一部分：身在此山中' in xml_content:
                print('\n文档包含第一部分总结')
            else:
                print('\n文档不包含第一部分总结')
            
            # 检查关键内容
            keywords = ['林薇', '算法', '身体', '祖父', '递归', '时间', '临界点']
            print('\n文档包含的关键词:')
            for keyword in keywords:
                count = xml_content.count(keyword)
                if count > 0:
                    print(f'  {keyword}: {count}次')
            
            # 检查文档大小
            file_size = len(z.read('word/document.xml'))
            print(f'\n文档XML内容大小: {file_size:,} 字节')
            
    except Exception as e:
        print(f'检查文档时出错: {e}')

if __name__ == '__main__':
    check_docx_content()