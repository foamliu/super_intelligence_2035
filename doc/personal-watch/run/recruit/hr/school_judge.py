# -*- coding: utf-8 -*-
"""读 resume_scan*.json（Boss 简单简历原文）→ 判定 在校 / 已毕业(社招)，出决策表。
用法：python resume_report2.py <scan.json> <out.md>
"""
import json, re, sys, os, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'resume_scan_social.json')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '社招判定.md')
NOW_Y = datetime.date.today().year

RE_AGE = re.compile(r'(\d{2})岁')
RE_FRESH = re.compile(r'(\d{2})年应届生')
RE_EXP = re.compile(r'(\d+年以上|\d+年)\s')
RE_RANGE = re.compile(r'(\d{4})(?:[.\-/]\d{1,2})?\s*[-–~至]\s*(\d{4}|至今)')
RE_SCHOOL = re.compile(r'(大学|学院|科学院|研究所|University|College|职业技术)')
RE_ROLE = re.compile(r'([\u4e00-\u9fa5A-Za-z0-9·（）()\-]{2,24})\s*·\s*([\u4e00-\u9fa5A-Za-z0-9/ \+]{1,24})')
RE_JOB = re.compile(r'沟通职位：\s*(.+?)\s*期望：')
RE_EXPECT = re.compile(r'期望：\s*(.+?)(?:\s*\d{4}[-./]|\s*\d{2}:\d{2}|$)')


def exp_years(header):
    m = RE_EXP.search(header)
    if not m:
        return 0.0
    s = m.group(1)
    if '以上' in s:
        return float(re.sub(r'\D', '', s)) + 0.5
    return float(re.sub(r'\D', '', s) or 0)


def age_of(header):
    m = RE_AGE.search(header)
    return int(m.group(1)) if m else 0


def latest_role(header):
    """最近一段工作经历：日期块之后的第一个非「学校/学位/专业」的「X · Y」"""
    roles = RE_ROLE.findall(header)
    bad = ('硕士', '本科', '博士', '大专', 'MBA', '肄业', '在读', '专业', '沟通职位')
    for comp, title in roles:
        if RE_SCHOOL.search(comp) or RE_SCHOOL.search(title):
            continue
        if any(b in comp or b in title for b in bad):
            continue
        return '%s · %s' % (comp.strip(), title.strip())
    return ''


def classify(header):
    ev = []
    if RE_FRESH.search(header):
        ev.append('标签「%s年应届生」' % RE_FRESH.search(header).group(1))
    exp = RE_EXP.search(header)
    rng = RE_RANGE.findall(header)
    max_end = max([int(b) for _, b in rng if b != '至今'] or [0])
    if exp:
        ev.append('工作年限「%s」' % exp.group(1).strip())
    if rng:
        ev.append('年份 ' + ' / '.join('%s-%s' % (a, b) for a, b in rng[:4]))
    if RE_FRESH.search(header):
        return '在校（应届生）', ev
    if exp:
        return '已毕业（社招）', ev
    if max_end >= NOW_Y:
        return '在校（经历在读）', ev
    return '未表态', ev


def main():
    data = json.load(open(SRC, encoding='utf-8'))
    rows = data.get('rows', {})
    recs = []
    for name, r in rows.items():
        h = (r.get('header') or '').replace('\n', ' ')
        if not h:
            recs.append({'name': name, 'verdict': '无数据', 'ev': [r.get('error') or ''], 'h': '', 'exp': 0, 'age': 0, 'role': '', 'job': '', 'expect': ''})
            continue
        v, ev = classify(h)
        jobm = RE_JOB.search(h); em = RE_EXPECT.search(h)
        recs.append({'name': name, 'verdict': v, 'ev': ev, 'h': h, 'exp': exp_years(h), 'age': age_of(h),
                     'role': latest_role(h), 'job': (jobm.group(1) if jobm else ''), 'expect': (em.group(1) if em else '')})

    soc = sorted([r for r in recs if r['verdict'].startswith('已毕业')], key=lambda x: (-x['exp'], -x['age'], x['name']))
    stu = sorted([r for r in recs if r['verdict'].startswith('在校')], key=lambda x: x['name'])
    oth = sorted([r for r in recs if r['verdict'] in ('未表态', '无数据')], key=lambda x: x['name'])

    L = []
    def clean_expect(s):
        s = re.sub(r'\s*\d{1,2}[-/.]\d{1,2}\s*$', '', s or '')      # 去掉尾部 09-19
        s = re.sub(r'\s*\d{1,2}:\d{2}\s*$', '', s)
        s = re.sub(r'\s*\d{1,2}\s*$', '', s)                        # 去掉被截断的 K 前数字
        return s.strip()
    L.append('# 在校 / 社招 判定表（读 Boss「简单简历」· 只读，未发任何消息）')
    L.append('')
    L.append('> 数据源：`%s` · 生成 %s' % (os.path.basename(SRC), datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
    L.append('> ★ 判据 = Boss 简单简历里的 **「XX年应届生」标签 / 教育经历在读 / 工作年限**；**「投社招岗」不作为依据**（刘杨 2026-09-23 指出）。')
    L.append('')
    L.append('## 汇总')
    L.append('')
    L.append('| 判定 | 人数 |')
    L.append('|---|---|')
    for k, v in [('✅ 已毕业（社招）', len(soc)), ('❌ 在校', len(stu)), ('⚠️ 未表态 / 无数据', len(oth))]:
        L.append('| %s | **%d** |' % (k, v))
    L.append('| 合计 | **%d** |' % len(recs))
    L.append('')

    L.append('## 一、✅ 已毕业（社招）· 按工作年限排序 —— %d 人' % len(soc))
    L.append('')
    L.append('| # | 姓名 | 年龄 | 工作年限 | 最近一段经历 | 应聘岗位 | 期望 |')
    L.append('|---|---|---|---|---|---|---|')
    for i, r in enumerate(soc, 1):
        L.append('| %d | **%s** | %d | %s | %s | %s | %s |' % (i, r['name'], r['age'], ('%g 年' % r['exp']) if r['exp'] else '—', r['role'] or '—', r['job'] or '—', clean_expect(r['expect']) or '—'))
    L.append('')

    L.append('## 二、❌ 在校 · %d 人' % len(stu))
    L.append('')
    L.append('| # | 姓名 | 证据 |')
    L.append('|---|---|---|')
    for i, r in enumerate(stu, 1):
        L.append('| %d | %s | %s |' % (i, r['name'], '；'.join(r['ev'])[:150]))
    L.append('')

    L.append('## 三、⚠️ 未表态 / 无数据 · %d 人' % len(oth))
    L.append('')
    L.append('| # | 姓名 | 证据 |')
    L.append('|---|---|---|')
    for i, r in enumerate(oth, 1):
        L.append('| %d | %s | %s |' % (i, r['name'], '；'.join([e for e in r['ev'] if e])[:150]))
    L.append('')

    L.append('## 四、简单简历原文（可核查）')
    L.append('')
    for r in soc + stu + oth:
        L.append('### %s — %s' % (r['name'], r['verdict']))
        L.append('')
        L.append('```')
        L.append(r['h'][:700] or '(未读到)')
        L.append('```')
        L.append('')
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
    sys.stdout.buffer.write(('社招(已毕业)=%d  在校=%d  未表态/无数据=%d  合计=%d\n' % (len(soc), len(stu), len(oth), len(recs))).encode('utf-8'))
    print('OUT=' + OUT)


if __name__ == '__main__':
    main()