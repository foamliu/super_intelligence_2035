#!/bin/bash

echo "章节结尾检查报告 - $(date)"
echo "=================================="
echo ""

# 列出所有章节文件
for file in chapters_v0_4/*.md; do
    chapter_num=$(echo "$file" | grep -o '[0-9]\+' | head -1)
    chapter_name=$(basename "$file" .md)
    chapter_title=$(echo "$chapter_name" | sed 's/^[0-9]\+-//')
    
    # 获取最后5行
    last_lines=$(tail -5 "$file")
    
    # 检查结尾类型
    if echo "$last_lines" | grep -q -E "[？?]|！|……" ; then
        ending_type="已有钩子"
    elif echo "$last_lines" | grep -q -E "。$|\.$" ; then
        ending_type="总结性"
    else
        ending_type="其他"
    fi
    
    echo "第${chapter_num}章: ${chapter_title}"
    echo "文件: ${file}"
    echo "结尾类型: ${ending_type}"
    echo "结尾内容:"
    echo "${last_lines}"
    echo "---"
done
