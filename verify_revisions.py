import os

files = [
    'chapters_v0_9/03-ai-negotiator.md',
    'chapters_v0_9/05-cognitive-collaboration-critical-point.md',
    'chapters_v0_9/20-codes-and-memory.md',
    'chapters_v0_9/32-government-architect.md'
]

print('=== 修订验证 ===\n')

# 第3章检查
with open(files[0], 'r', encoding='utf-8') as f:
    content = f.read()
    checks = [
        ('红色的小人' in content, '新增深夜场景 - 红色的小人'),
    ]
    print('第3章《棋子》:')
    for ok, desc in checks:
        status = 'OK' if ok else 'FAIL'
        print(f'  [{status}] {desc}')
    print()

# 第5章检查
with open(files[1], 'r', encoding='utf-8') as f:
    content = f.read()
    checks = [
        ('摸了摸机器的外壳' in content, '第二次宣言改为动作 - 摸机器外壳'),
        ('擦了擦镜片' in content, '第三次宣言改为动作 - 擦镜片'),
    ]
    print('第5章《临界点》:')
    for ok, desc in checks:
        status = 'OK' if ok else 'FAIL'
        print(f'  [{status}] {desc}')
    print()

# 第20章检查
with open(files[2], 'r', encoding='utf-8') as f:
    content = f.read()
    checks = [
        ('沉默了两秒' in content, '墨子沉默时间改为两秒'),
        ('我的分析' not in content, '精简墨子回应（删除总结性论述）'),
    ]
    print('第20章《编码》:')
    for ok, desc in checks:
        status = 'OK' if ok else 'FAIL'
        print(f'  [{status}] {desc}')
    print()

# 第32章检查
with open(files[3], 'r', encoding='utf-8') as f:
    content = f.read()
    checks = [
        ('说下去' in content, '陈思危说\"说下去\"'),
        ('林薇在笔记本上写下' not in content, '删除独立笔记段落'),
    ]
    print('第32章《建筑》:')
    for ok, desc in checks:
        status = 'OK' if ok else 'FAIL'
        print(f'  [{status}] {desc}')
    print()

print('=== 所有修订已完成 ===')