# -*- coding: utf-8 -*-
"""
从 Boss「简单简历」扫描结果生成两张候选表（社招 / 实习）。

★ 排序口径（草案，明确标注，不自行发明）：
  ① 论文线索：命中「四大 EDA 顶会 / AI 顶会」关键词（= 刘杨已定口径的会议范围）→ 置顶
  ② 学历：博士 > 硕士 > 本科 > 大专
  ③ 学校档：C9 > 985 > 其他（**只用刘杨已定的 C9/985 两档**；211/双非/港澳/中科院系档未给 → 全部归「其他」）
  ④ 名企 / 大厂经历：有 > 无
  ⑤ 活跃度：刚刚活跃 > 今日活跃 > 3日内 > 本周 > 2周内 > 更久
  ⚠️ 「论文线索」仅表示**平台文本里出现顶会关键词**，**不等于达标**（达标须核实「一作 + 已录用」）。

用法：
  python build_candidate_tables.py <scan_others.json> <scan_intern.json> <out_social.md> <out_intern.md>
输出：两张 .md 表 + 一张合并 .csv（可进 Excel 排序）
"""
import csv
import io
import json
import os
import re
import sys

ACT_LIST = ['刚刚活跃', '今日活跃', '3日内活跃', '本周活跃', '2周内活跃',
            '1个月内活跃', '月内活跃', '半年前活跃', '年前活跃']
ACT_RANK = {k: i for i, k in enumerate(ACT_LIST)}

DEG_RANK = {'博士': 0, '硕士': 1, '本科': 2, '大专': 3, '其他': 4}
DEGS = ('博士', '硕士', '本科', '大专', '学士')
# 「专业 · 学位」对（专业不含空格）
DEG_PAIR_RE = re.compile(r'([^\s·][^\s·]{0,24})\s*·\s*(博士|硕士|本科|大专|学士)(?=\s|$)')
# 「A · B」对（A/B 均不含空格）
WORK_RE = re.compile(r'([^\s·]{2,26})\s*·\s*([^\s·]{2,24})(?=\s|$)')
YEAR_RANGE_RE = re.compile(r'(\d{4})\s*[-–]\s*(\d{4})')

C9 = ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学',
      '中国科学技术大学', '南京大学', '哈尔滨工业大学', '西安交通大学']
D985 = ['华东师范大学', '华中科技大学', '山东大学', '北京理工大学', '北京航空航天大学',
        '武汉大学', '同济大学', '东南大学', '中山大学', '四川大学', '南开大学', '天津大学',
        '厦门大学', '吉林大学', '湖南大学', '中南大学', '重庆大学', '大连理工大学',
        '东北大学', '兰州大学', '电子科技大学', '西北工业大学', '华南理工大学',
        '中国农业大学', '北京师范大学', '中国人民大学', '西北农林科技大学', '国防科技大学',
        '中央民族大学']

CONF_EDA = ['DAC', 'ICCAD', 'ASP-DAC', 'ASPDAC', 'DATE']
CONF_AI = ['NeurIPS', 'ICML', 'ICLR', 'CVPR', 'ICCV', 'ECCV', 'AAAI', 'IJCAI',
           'ACL', 'EMNLP', 'NAACL', 'MICCAI', 'ACM MM', 'KDD', 'SIGIR']

BIGCO = ['阿里巴巴', '淘天', '腾讯', '字节跳动', '字节', '百度', '美团', '京东', '小米',
         '华为', '海思', '平头哥', '英伟达', 'NVIDIA', 'AMD', '英特尔', 'Intel', '网易',
         '滴滴', '快手', '蚂蚁', '商汤', '旷视', '依图', '云从', '科大讯飞', '第四范式',
         '阶跃星辰', '稀宇', 'MiniMax', '智谱', '月之暗面', '百川', '零一万物', 'DeepSeek',
         '寒武纪', '地平线', '摩尔线程', '壁仞', '燧原', '天数智芯', '兆易创新', '中芯国际',
         '长江存储', '长鑫', '联发科', '紫光', '浪潮', '微软', 'Google', '亚马逊', 'Apple',
         'Meta', 'IBM', '摩根', '高盛', '中金', '蚂蚁集团', '众擎', '赛力斯', '哈啰',
         '爱奇艺', '平安', '中兴', '海康', '大疆', '腾讯云', '阿里云', '中国电信', '奇富',
         '建信', '小红书', 'B站', '哔哩哔哩', '作业帮', '好未来', 'Momenta', '文远知行']

# ★★★ 刘杨 2026-09-25 正式给出的**社招岗三档排序口径** ★★★
#   第一档：在下列「最强 AI 公司」有 **1 年以上大模型算法岗** 工作经验
#   第二档：**本科 C9** + 硕士以上学历 + 有**大厂**工作经历
#   第三档：**本科 211 以上** + 硕士以上学历 + 有**论文和开源项目**
#   ⚠️ 简单简历**只有最高学历那一条教育记录** → 「本科院校」拿不到 → 二/三档的「本科」条件**只能标待核**。
TIER1_CO = [('阿里', '阿里Qwen'), ('Qwen', '阿里Qwen'), ('通义', '阿里Qwen'), ('千问', '阿里Qwen'),
            ('DeepSeek', 'DeepSeek'), ('深度求索', 'DeepSeek'),
            ('Kimi', 'Kimi'), ('月之暗面', 'Kimi'),
            ('MiniMax', 'MiniMax'), ('稀宇', 'MiniMax'),
            ('字节', '字节Seed'), ('Seed', '字节Seed'),
            ('智谱', '智谱'), ('阶跃', '阶跃星辰'), ('面壁', '面壁智能')]
# 「大模型算法岗」关键词：命中**大模型词** → 明确吻合；仅命中**通用算法词** → 疑似，需人工确认
LM_STRONG = ['大模型', 'LLM', 'Agent', '智能体', '多模态', 'RAG', '强化学习', '预训练']
LM_WEAK = ['算法', 'NLP', '自然语言', 'AI', '深度学习', '机器学习', '模型']
SPAN_RE = re.compile(r'(\d{4})\s*[.\-/]\s*(\d{1,2})?\s*[-–]\s*(?:(\d{4})\s*[.\-/]\s*(\d{1,2})?|至今|现在)')
NOW_YM = (2026, 9)          # 「至今」以本工作区当前日期 2026-09 为终点
OS_KW = ['开源', 'GitHub', 'gitlab', 'Open Source', 'huggingface', 'HuggingFace']   # 「开源项目」线索词

# 211 名单（含全部 985；**本工作区自建清单**，如与你的口径不符请指出）
D211 = ['北京大学', '清华大学', '中国人民大学', '北京航空航天大学', '北京理工大学', '北京师范大学',
        '中国农业大学', '中央民族大学', '北京交通大学', '北京工业大学', '北京科技大学', '北京化工大学',
        '北京邮电大学', '北京林业大学', '北京中医药大学', '北京外国语大学', '中国传媒大学', '中央财经大学',
        '对外经济贸易大学', '北京体育大学', '中央音乐学院', '中国政法大学', '华北电力大学', '中国矿业大学',
        '中国石油大学', '中国地质大学', '南开大学', '天津大学', '天津医科大学', '河北工业大学', '太原理工大学',
        '内蒙古大学', '大连理工大学', '东北大学', '辽宁大学', '大连海事大学', '吉林大学', '延边大学', '东北师范大学',
        '哈尔滨工业大学', '哈尔滨工程大学', '东北农业大学', '东北林业大学', '复旦大学', '同济大学', '上海交通大学',
        '华东理工大学', '东华大学', '华东师范大学', '上海外国语大学', '上海财经大学', '上海大学', '第二军医大学',
        '南京大学', '东南大学', '南京航空航天大学', '南京理工大学', '河海大学', '江南大学', '南京农业大学',
        '中国药科大学', '南京师范大学', '苏州大学', '浙江大学', '安徽大学', '中国科学技术大学', '合肥工业大学',
        '厦门大学', '福州大学', '南昌大学', '山东大学', '中国海洋大学', '郑州大学', '武汉大学', '华中科技大学',
        '武汉理工大学', '华中农业大学', '华中师范大学', '中南财经政法大学', '湖南大学', '中南大学', '湖南师范大学',
        '国防科技大学', '中山大学', '暨南大学', '华南理工大学', '华南师范大学', '广西大学', '海南大学', '重庆大学',
        '西南大学', '四川大学', '电子科技大学', '西南交通大学', '西南财经大学', '四川农业大学', '贵州大学', '云南大学',
        '西藏大学', '西安交通大学', '西北工业大学', '西北农林科技大学', '西安电子科技大学', '长安大学', '陕西师范大学',
        '第四军医大学', '西北大学', '兰州大学', '青海大学', '宁夏大学', '新疆大学', '石河子大学']


def school_rank(name):
    if not name:
        return 2
    for s in C9:
        if s in name:
            return 0
    for s in D985:
        if s in name:
            return 1
    return 2


def school_211(name):
    """第三档「本科 211 以上」用（清单本工作区自建）"""
    return bool(name) and any(s in name for s in D211)


def has_conf(text, names):
    up = text.upper()
    for n in names:
        nu = n.upper()
        if re.search(r'(?<![A-Z0-9-])' + re.escape(nu) + r'(?![A-Z0-9-])', up):
            return n
    return ''


def parse(header):
    t = header or ''
    head = t.split('沟通职位：')[0]
    rec = {'raw': t, 'degree': '其他', 'school': '', 'major': '', 'edu_span': '',
           'jobs': [], 'expect': '', 'job_applied': '', 'activity': '', 'age': '',
           'grad': '', 'paper': '', 'paper_ev': '', 'paper_accept': False, 'bigco': '',
           'spans': [], 'exp_dur': [], 'dur_reliable': False,
           'tier1': '', 'tier1_weak': '', 'opensource': ''}

    for a in ACT_LIST:
        if a in t:
            rec['activity'] = a
            break
    m = re.search(r'(\d{2})\s*岁', t)
    if m:
        rec['age'] = m.group(1)
    m = re.search(r'(\d{2})\s*年应届生', t)
    if m:
        rec['grad'] = m.group(1) + '年应届生'

    # 教育：先定最后一个「专业 · 学位」对，再向前取「学校」
    deg_m = None
    for mm in DEG_PAIR_RE.finditer(head):
        deg_m = mm
    edu_lo = edu_hi = None
    if deg_m:
        major = deg_m.group(1)
        deg = '本科' if deg_m.group(2) == '学士' else deg_m.group(2)
        pre = head[:deg_m.start()]
        parts = pre.rsplit('·', 1)
        seg = parts[0] if len(parts) == 2 else pre
        toks = seg.split()
        school = toks[-1] if toks else ''
        rec.update({'school': school, 'major': major, 'degree': deg})
        spans = [(mm2.start(), mm2.group(0)) for mm2 in YEAR_RANGE_RE.finditer(head[:deg_m.start()])]
        if spans:
            rec['edu_span'] = spans[-1][1]
        edu_lo, edu_hi = deg_m.start() - (len(school) + 4), deg_m.end()

    # 工作经历 / 教育条目：所有「A · B」对，排除落在教育段内的
    for mm2 in WORK_RE.finditer(head):
        if deg_m and edu_lo <= mm2.start() and mm2.end() <= edu_hi:
            continue
        a, b = mm2.group(1), mm2.group(2)
        if b in DEGS:
            continue
        if a and a not in [j[0] for j in rec['jobs']]:
            rec['jobs'].append((a, b))
    rec['bigco'] = next((b for b in BIGCO if b.lower() in head.lower()), '')   # 大小写不敏感
    rec['has_work'] = bool(rec['jobs']) and '未填写工作经历' not in head
    # 经历性质：职位名含「实习」→ 实习；否则视为正式工作/在职
    rec['has_real_work'] = any('实习' not in j[1] for j in rec['jobs'])
    rec['has_intern_exp'] = any('实习' in j[1] for j in rec['jobs'])

    m = re.search(r'沟通职位：(.+?)期望：', t)      # 完整岗位名（含空格 / 斜杠）
    if m:
        rec['job_applied'] = m.group(1).strip()
    else:
        m = re.search(r'沟通职位：\s*([^\s\d]+)', t)
        if m:
            rec['job_applied'] = m.group(1)
    m = re.search(r'期望：\s*([^0-9]{1,40}?)(?:\s*\d|\s*$)', t)
    if m:
        rec['expect'] = m.group(1).strip(' ·')

    rec['opensource'] = next((k for k in OS_KW if k.lower() in t.lower()), '')

    # ★ 时间线 × 经历 **顺序对应**（简单简历布局：时间段在前、经历对在后，均最新在前）
    #   仅当「时间段数 == 非教育经历数」时采信时长；否则时长留空 = 标待核，避免错位误判。
    spans = []
    for mm in SPAN_RE.finditer(head):
        y1, m1 = int(mm.group(1)), int(mm.group(2) or 1)
        if mm.group(3):
            y2, m2 = int(mm.group(3)), int(mm.group(4) or 1)
        else:
            y2, m2 = NOW_YM
        months = (y2 - y1) * 12 + (m2 - m1)
        if 0 <= months <= 600:
            spans.append(months)
    rec['spans'] = spans
    rec['dur_reliable'] = (len(spans) == len(rec['jobs']))
    for i, (co, pos) in enumerate(rec['jobs']):
        mo = spans[i] if (rec['dur_reliable'] and i < len(spans)) else None
        rec['exp_dur'].append((co, pos, mo))

    # 第一档：**最强 AI 公司** + **大模型算法岗** + **在职 ≥ 12 个月**
    for co, pos, mo in rec['exp_dur']:
        std = next((s for k, s in TIER1_CO if k.lower() in co.lower()), '')
        if not std:
            continue
        if mo is None:
            if not rec['tier1_weak']:
                rec['tier1_weak'] = '%s · %s（公司吻合，但时长待核：时间段与经历无法一一对应）' % (std, pos)
            continue
        if mo < 12:
            continue
        pl = pos.lower()
        if [k for k in LM_STRONG if k.lower() in pl]:
            rec['tier1'] = '%s · %s · **%d 个月**' % (std, pos, mo)
            break
        if not rec['tier1_weak'] and [k for k in LM_WEAK if k.lower() in pl]:
            rec['tier1_weak'] = '%s · %s · %d 个月（岗位名只含通用算法词，是否属「大模型算法岗」需你确认）' % (std, pos, mo)

    conf = has_conf(t, CONF_EDA) or has_conf(t, CONF_AI)
    if conf:
        pos = t.upper().find(conf.upper())
        rec['paper'] = conf
        rec['paper_ev'] = t[max(0, pos - 30):pos + 30].strip()
        rec['paper_accept'] = bool(re.search(r'录用|中稿|接收|accept', t, re.I))
    return rec


def in_school(rec):
    """刘杨判据：届别标签 → 在校；教育区间仍在读 → 在校；工作年限标签 + 教育已结束 → 已毕业。"""
    if rec['grad']:
        return True
    m = re.search(r'(\d{4})\s*[-–]\s*(\d{4})', rec['raw'].split('沟通职位：')[0])
    if m and int(m.group(2)) >= 2027:
        return True
    return False


def tier_info(r):
    """★ 刘杨 2026-09-25 正式社招三档口径。返回 (tier, 档位文本, 依据, 待核)。
    1 = 第一档（最强 AI 公司 ≥1 年大模型算法岗）2 = 第二档候选 3 = 第三档候选 9 = 未入档。
    ⚠️ 简单简历**只存最高学历那条教育** → 「本科院校」缺失 → 二/三档的「本科」条件一律标待核。"""
    if not r['group'].startswith('社招'):
        return 9, '—', '', ''
    if r.get('tier1'):
        return 1, '第一档 ✅', r['tier1'], ''
    if r.get('tier1_weak'):
        return 1, '第一档 ⚠️待核', r['tier1_weak'], '岗位是否属「大模型算法岗」/ 在职是否满 1 年'
    d = r['degree'] or ''
    master = ('硕士' in d) or ('博士' in d)
    if master and r['bigco']:
        ev = '硕士以上（%s · %s）+ 大厂经历（%s）' % (d, r['school'], r['bigco'])
        extra = []
        if r['paper']:
            extra.append('论文线索 %s%s' % (r['paper'], '（含「录用」字样）' if r.get('paper_accept') else '（仅提及）'))
        if r['opensource']:
            extra.append('开源线索 %s' % r['opensource'])
        if extra:
            ev += '；' + ' / '.join(extra)
        return 2, '第二档候选 ⚠️', ev, '**本科院校**（C9 走二档 / 211 走三档 / 其他 → 未入档）'
    if master and (r['paper'] or r['opensource']):
        ev = []
        if r['paper']:
            ev.append('论文线索 %s%s' % (r['paper'], '（含「录用」字样）' if r.get('paper_accept') else '（仅提及）'))
        if r['opensource']:
            ev.append('开源线索 %s' % r['opensource'])
        return 3, '第三档候选 ⚠️', '硕士以上（%s · %s）+ %s' % (d, r['school'], ' / '.join(ev)), \
               '**本科院校**（须 211 以上）+ 论文是否一作且已录用'
    return 9, '未入档', '', '本科院校（简单简历不含）'


def sort_key(r):
    p = 0 if r.get('paper_accept') else (1 if r['paper'] else 2)
    span = re.search(r'(\d{4})', r['edu_span']) if r['edu_span'] else None
    return (r.get('tier', 9),
            p,
            DEG_RANK.get(r['degree'], 4),
            school_rank(r['school']),
            0 if r['bigco'] else 1,
            ACT_RANK.get(r['activity'], 99),
            -(int(span.group(1)) if span else 0))

def load(path):
    with io.open(path, encoding='utf-8') as f:
        return (json.load(f) or {}).get('rows', {})


def fmt_jobs(r):
    js = r['jobs'][:3]
    return ' / '.join('%s · %s' % (c, p) for c, p in js) if js else ('未填写工作经历' if '未填写工作经历' in r['raw'] else '—')


def build(rows, group):
    out = []
    for name, r in rows.items():
        rec = parse(r.get('header', ''))
        rec['name'] = name
        rec['error'] = r.get('error', '')
        rec['in_school'] = in_school(rec)
        rec['group'] = group
        out.append(rec)
    out.sort(key=sort_key)
    return out


def md_table(items, title, note, f, show_tier=False):
    f.write('# %s\n\n' % title)
    f.write('%s\n\n' % note)
    if show_tier:
        f.write('| # | 姓名 | 档位 | 档位依据 | 待核 | 年龄 | 学历 | 学校 | 专业 | 状态 | 最近经历 | 期望 | 活跃 | 论文线索 | 投递岗位 |\n')
        f.write('|' + '---|' * 15 + '\n')
    else:
        f.write('| # | 姓名 | 年龄 | 学历 | 学校 | 专业 | 状态 | 最近经历 | 期望 | 活跃 | 论文线索 | 投递岗位 |\n')
        f.write('|' + '---|' * 12 + '\n')
    for i, r in enumerate(items, 1):
        if show_tier:
            f.write('| %d | **%s** | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
                i, r['name'], r.get('tier_txt', ''), r.get('tier_ev', ''), r.get('tier_todo', ''),
                r['age'] or '—', r['degree'], r['school'] or '—', r['major'] or '—',
                '在校' if r['in_school'] else '已毕业', fmt_jobs(r), r['expect'] or '—',
                r['activity'] or '—', paper_txt(r), r['job_applied'] or '—'))
        else:
            f.write('| %d | **%s** | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
                i, r['name'], r['age'] or '—', r['degree'], r['school'] or '—', r['major'] or '—',
                '在校' if r['in_school'] else '已毕业', fmt_jobs(r), r['expect'] or '—',
                r['activity'] or '—', paper_txt(r), r['job_applied'] or '—'))
    f.write('\n')


CSV_COLS = ['group', 'name', 'age', 'degree', 'school', 'major', 'status', 'edu_span',
            'jobs', 'expect', 'activity', 'paper', 'paper_accept', 'paper_ev',
            'job_applied', 'bigco', 'error', 'raw']


def paper_txt(r):
    if not r['paper']:
        return '—'
    return '%s · %s' % (r['paper'], '含「录用」字样' if r.get('paper_accept') else '仅提及')


def main():
    others_json, intern_json = sys.argv[1], sys.argv[2]
    out_social = sys.argv[3] if len(sys.argv) > 3 else '候选表-社招.md'
    out_intern = sys.argv[4] if len(sys.argv) > 4 else '候选表-实习.md'
    out_csv = '候选表-全部.csv'

    # ★ 分组依据 = Boss 简单简历里的「沟通职位」（= 平台记录的申请岗位，对应刘杨口径第①条「申请社招岗」）
    INTERN_JOB = '大模型预研实习生'
    recs = {}
    for r in build(load(others_json), '社招池（旧分组）') + build(load(intern_json), '实习池（旧分组）'):
        r['src_pool'] = r['group']
        r['group'] = '实习岗（大模型预研实习生）' if r['job_applied'] == INTERN_JOB else '社招岗'
        recs[(r['name'], r['job_applied'])] = r
    pool = [r for r in recs.values() if not r['error']]

    # ★ 档位必须在**平台「沟通职位」定稿分组之后**再算（否则会按旧池把实习岗的人误判）
    #   在校（投实习岗 / 投社招岗但在校）= 不推进 → 不排档
    for r in pool:
        if r['group'].startswith('社招') and not r['in_school']:
            r['tier'], r['tier_txt'], r['tier_ev'], r['tier_todo'] = tier_info(r)
        else:
            r['tier'], r['tier_txt'], r['tier_ev'], r['tier_todo'] = 9, '—', '', ''

    # ★★ 刘杨 2026-09-25 口径（原话）：
    #   「什么是校招？1.申请社招岗；2.在校，没有工作/在职经历。」（三条同时成立才算校招）
    #   「为什么我反复说只要实习和社招，因为等不起。」
    #   → 要能【马上到岗】：已毕业 → 立刻全职（社招 ✅）；在校 → 立刻实习（实习 ✅）；等毕业 → 不招（校招 ❌）。
    intern_ok = [r for r in pool if r['group'] == '实习岗（大模型预研实习生）']
    socialpool = [r for r in pool if r['group'] == '社招岗']
    # ★ 刘杨 2026-09-25 第 2 次明确：**在校 + 投社招岗 → 不能立刻到岗 → 不推进**
    #   「这些人在校又投社招，所以不能立刻到岗」；**不再看有无工作/实习经历**。
    #   如需要回复，统一用（刘杨原话）：「这是社招岗位，需要工作经历」。
    social = [r for r in socialpool if not r['in_school']]
    social_school = [r for r in socialpool if r['in_school']]
    campus_reply = '这是社招岗位，需要工作经历'
    grad_intern = [r for r in intern_ok if not r['in_school']]

    # ★ 按刘杨三档口径排序（社招表用 tier；实习表档位为「—」，仍按学历/学校/大厂/活跃度排）
    social.sort(key=sort_key)
    social_school.sort(key=sort_key)
    intern_ok.sort(key=sort_key)

    NOTE_S = ('> 数据源：Boss 会话头「简单简历」（只读扫描 `%s`）。\n'
              '> ★★★ **排序口径 = 刘杨 2026-09-25 正式下达的三档**（本表即按此排序）：\n'
              '> **第一档**：在**最强 AI 公司**（阿里Qwen / DeepSeek / Kimi / MiniMax / 字节Seed / 智谱 / 阶跃 / 面壁）'
              '有 **1 年以上大模型算法岗** 工作经验；\n'
              '> **第二档**：**本科 C9** + 硕士以上学历 + 有**大厂**工作经历；\n'
              '> **第三档**：**本科 211 以上** + 硕士以上学历 + 有**论文和开源项目**。\n'
              '> ⚠️ **「本科院校」简单简历里没有**（只存最高学历那一条教育）→ 二/三档**只能标「候选 · 本科院校待核」**，'
              '**待核项单列一列**，不自行当成达标。\n'
              '> ⚠️ **第一档「1 年」怎么算的**：简单简历的时间段与经历**顺序对应且最新在前** → 按位置配对算月数；'
              '**只有「时间段数 == 经历数」时才采信**，否则标「时长待核」。岗位名只含通用算法词（算法/AI/NLP）的也标待核。\n'
              '> ⚠️ 「大厂」与「211」清单为**本工作区自建**，如有出入请指出。\n'
              '> ★ **投社招岗 + 在校 → 不能立刻到岗 → 不推进**（见文末附节）；如回复用「**这是社招岗位，需要工作经历**」。\n'
              '> ⛔ 本表**不是达标判定**；本轮未发任何消息。' % others_json)

    NOTE_I = ('> 数据源：Boss 会话头「简单简历」（只读扫描 `%s`）。\n'
              '> ℹ️ **刘杨 2026-09-25 的三档排序口径只给了社招岗** → 本表仍按客观证据排序（**草案**）：\n'
              '> ① 论文线索（仅线索，需核实）② 学历 ③ 学校档（C9 > 985 > 其他）④ 名企经历 ⑤ 活跃度。\n'
              '> ⏳ **实习岗的正式排序口径等你给**。\n'
              '> ℹ️ 状态列 = 是否在校：**届别标签（`28年应届生`）或教育区间仍在读（如 `2025-2028`）→ 在校**。\n'
              '> ✅ 本表所有人**投的是实习岗 → 按刘杨口径不是校招**（在校生可**马上实习**，正是「等不起」下要的人）。\n'
              '> ⛔ 本表**不是达标判定**；本轮未发任何消息。' % intern_json)

    with io.open(out_social, 'w', encoding='utf-8') as f:
        md_table(social, '社招候选表 · 已毕业（%d 人，按刘杨三档口径排序）' % len(social), NOTE_S, f, show_tier=True)
        f.write('---\n\n## 附：投社招岗但**仍在读（校）**（%d 人，**不推进**）\n\n' % len(social_school))
        f.write('> 口径（刘杨 2026-09-25，第 2 次明确）：「**这些人在校又投社招，所以不能立刻到岗**」→ **不推进**。\n'
                '> **不再区分有无工作 / 实习经历** —— 在校 = 不能立刻到岗 = 等不起。\n'
                '> 如需要回复，统一用（刘杨原话）：「**%s**」。\n\n' % campus_reply)
        f.write('| # | 姓名 | 年龄 | 学历 | 学校 | 教育区间 | 经历（原文） | 期望 | 投递岗位 |\n'
                '|---|---|---|---|---|---|---|---|---|\n')
        for i, r in enumerate(social_school, 1):
            f.write('| %d | %s | %s | %s | %s | %s | %s | %s | %s |\n'
                    % (i, r['name'], r['age'], r['degree'], r['school'], r['edu_span'],
                       fmt_jobs(r), r['expect'], r['job_applied']))
        # （原「附 B 校招」节已并入上方「附：投社招岗但仍在校」—— 在校 + 投社招岗一律**不推进**）

    with io.open(out_intern, 'w', encoding='utf-8') as f:
        md_table(intern_ok, '实习候选表 · 投实习岗（%d 人，按客观证据排序草案）' % len(intern_ok), NOTE_I, f)
        f.write('---\n\n## 附：投实习岗但简历显示**已毕业**（%d 人，需人工确认是否仍接受实习）\n\n' % len(grad_intern))
        f.write('| # | 姓名 | 年龄 | 学历 | 学校 | 最近经历 |\n|---|---|---|---|---|---|\n')
        for i, r in enumerate(grad_intern, 1):
            f.write('| %d | %s | %s | %s | %s | %s |\n'
                    % (i, r['name'], r['age'], r['degree'], r['school'], fmt_jobs(r)))
        f.write('\n')

    allrows = social + social_school + intern_ok
    csv_cols = CSV_COLS + ['tier', 'tier_txt', 'tier_ev', 'tier_todo',
                           'has_work', 'has_real_work_unreliable', 'campus_flag']
    with io.open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(csv_cols)
        for r in allrows:
            flag = ('社招岗-在校不推进' if r in social_school else
                    '实习岗-可马上实习' if r['group'] == '实习岗（大模型预研实习生）' else '社招岗-已毕业')
            w.writerow([r['group'], r['name'], r['age'], r['degree'], r['school'], r['major'],
                        '在校' if r['in_school'] else '已毕业', r['edu_span'], fmt_jobs(r),
                        r['expect'], r['activity'], r['paper'], r['paper_accept'], r['paper_ev'],
                        r['job_applied'], r['bigco'], r['error'], r['raw'][:400],
                        r.get('tier', ''), r.get('tier_txt', ''), r.get('tier_ev', ''), r.get('tier_todo', ''),
                        '有' if r['has_work'] else '无', '是' if r['has_real_work'] else '否', flag])

    moved = [r for r in allrows if r.get('src_pool', '').startswith('实习池') and r['group'] == '社招岗']
    if moved:
        print('[WARN] 分组纠正：%d 人原在「实习池」名单里，但平台记录的「沟通职位」= 社招岗 → 已改归社招岗：%s'
              % (len(moved), ' / '.join(r['name'] for r in moved)))
    def cnt(t):
        return len([r for r in social if r['tier'] == t])
    print('[TIER] 一档=%d（明确 %d / 待核 %d）· 二档候选=%d · 三档候选=%d · 未入档=%d'
          % (cnt(1), len([r for r in social if r.get('tier1')]), cnt(1) - len([r for r in social if r.get('tier1')]),
             cnt(2), cnt(3), cnt(9)))
    cum = [r for r in social if r['tier'] != 1
           and sum(mo for co, pos, mo in r['exp_dur'] if any(k in co for k, _ in TIER1_CO) and mo) >= 12]
    if cum:
        print('[TIER] 「一档公司单段<1年、多段累计>=1年」= %d 人（累计算不算「1年以上」的口径未给）：%s'
              % (len(cum), ' / '.join(r['name'] for r in cum)))
    print('OK 社招岗·已毕业=%d · 投社招岗但在校(不推进)=%d；实习岗=%d(其中已毕业 %d) 合计=%d'
          % (len(social), len(social_school), len(intern_ok), len(grad_intern), len(allrows)))
    print('OUT %s | %s | %s' % (out_social, out_intern, out_csv))


if __name__ == '__main__':
    main()
