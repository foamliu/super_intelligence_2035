import json, re, csv, io
from collections import Counter

d = json.load(open('boss_candidates.json', encoding='utf-8'))
cands = d['candidates']
lv = {r['姓名'] + str(r['年龄']): r['等级']
      for r in csv.DictReader(io.open('候选人筛选结果.csv', encoding='utf-8-sig'))}

# 上海高校 / 上海相关
SH_SCHOOL = re.compile('复旦|上海交大|交大|华东师范|华东理工|同济|上海大学|东华大学|'
                       '上海科技|上科大|上海理工|上海海事|上海师范|上海财经|'
                       '上海外国语|华东政法|上海电力|上海工程技术|上海纽约|'
                       '中科院上海|上海微系统|上海人工智能实验室|张江|临港')
# 其他城市
OTHER_CITY = re.compile('北京|合肥|杭州|南京|广州|深圳|香港|成都|武汉|西安|苏州|无锡|'
                        '天津|长沙|厦门|济南|大连|重庆|青岛|郑州|海宁|嘉兴')

print('===== S 级 8 人地点线索 =====')
for r in cands:
    k = lv.get(r['name'] + str(r['age']), '?')
    if k != 'S':
        continue
    t = r.get('lastText') or ''
    sh = set(SH_SCHOOL.findall(t))
    oc = set(OTHER_CITY.findall(t))
    tag = '✅上海' if sh else ('📍' + '/'.join(sorted(oc)) if oc else '❓未知')
    print(f"  {r['name']} {r['age']}岁 {r['job'][:16]} | {tag}")
    if sh or oc:
        print(f"     匹配: {sorted(sh | oc)}")

print()
print('===== S/A/A- 中的"上海"候选人（可优先联系）=====')
sh_list = []
for r in cands:
    k = lv.get(r['name'] + str(r['age']), '?')
    t = r.get('lastText') or ''
    m = set(SH_SCHOOL.findall(t))
    if m and k in ('S', 'A', 'A-'):
        sh_list.append((k, r['name'], r['age'], r['job'][:16], '/'.join(sorted(m))))
for x in sorted(sh_list):
    print(f"  [{x[0]}] {x[1]} {x[2]}岁 {x[3]} <- {x[4]}")
print('小计', len(sh_list))

