import os
import shutil

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 从46到31倒序重命名，避免冲突
renames = [
    ('46-epilogue.md', '47-epilogue.md'),
    ('45-wisdom-of-blankness.md', '46-wisdom-of-blankness.md'),
    ('44-moment-of-choice.md', '45-moment-of-choice.md'),
    ('43-datong-ideal.md', '44-datong-ideal.md'),
    ('42-industrial-commons-governance.md', '43-industrial-commons-governance.md'),
    ('41-ubi-algorithm.md', '42-ubi-algorithm.md'),
    ('40-data-commons-tech.md', '41-data-commons-tech.md'),
    ('39-algorithm-transparency.md', '40-algorithm-transparency.md'),
    ('38-global-governance.md', '39-global-governance.md'),
    ('37-abundance-existentialism.md', '38-abundance-existentialism.md'),
    ('36-algorithm-accountability.md', '37-algorithm-accountability.md'),
    ('35-mixed-ownership.md', '36-mixed-ownership.md'),
    ('34-digital-family-elderly.md', '35-digital-family-elderly.md'),
    ('33-fifteen-hour-work.md', '34-fifteen-hour-work.md'),
    ('32-education-revolution.md', '33-education-revolution.md'),
    ('31-government-architect.md', '32-government-architect.md'),
]

for old, new in renames:
    if os.path.exists(old):
        shutil.move(old, new)
        print(f'Renamed: {old} -> {new}')
    else:
        print(f'Not found: {old}')

print('Done!')
