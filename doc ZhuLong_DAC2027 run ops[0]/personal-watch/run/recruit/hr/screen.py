# -*- coding: utf-8 -*-
"""
Boss直聘候选人自动筛选脚本
按 AI+EDA研究员（DRAM设计方向）JD 对候选人打招呼内容分级

★ 招聘范围（刘杨 2026-09-23 口径）：**只招实习生 + 社招，不做校招**
  → 「求职意向」判定为 **校招**（校招 / 校园招聘 / 秋招 / 春招 / 应届生）的候选人
    标为 **X**，单独成节、不推进；
  → 意向为 **实习** 或 **其他（社招/未表态）** 的正常参与 S/A/A-/B/B-/C 分级。

用法:  python screen.py
输入:  boss_candidates.csv   (由 Playwright 采集脚本导出)
输出:  候选人筛选结果.csv / 候选人筛选结果.md
"""
import csv
import io
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'boss_candidates.csv')
OUT_CSV = os.path.join(BASE, '候选人筛选结果.csv')
OUT_MD = os.path.join(BASE, '候选人筛选结果.md')

# ---- JD 关键词库 ----
# EDA / 芯片方向（最高优先级，对应 JD 第 2 条硬门槛）
EDA_KW = [
    'EDA', '电子设计自动化', 'ICCAD', 'ASP-DAC', 'ASPDAC', 'AI4EDA', 'AI for EDA',
    '芯片设计', '集成电路', '微电子', 'IC设计', '数字IC', '模拟IC', '后端设计',
    'RTL', 'Verilog', 'SystemVerilog', 'VHDL', '布局布线', '时序分析', '静态时序',
    'DFT', 'DRAM', '存储芯片', '存储器', '处理器设计', '体系结构', '流片', 'Tapeout',
    '形式验证', '版图', 'Cadence', 'Synopsys', 'Innovus', 'Genus', 'PrimeTime',
    '逻辑综合', '物理设计', '低功耗设计', 'SoC', 'FPGA', 'NPU', 'AI芯片', 'GPU架构',
]
EDA_REGEX = [(r'\bDAC\b', 'DAC'), (r'\bDATE\b', 'DATE'), (r'\bICCAD\b', 'ICCAD'),
             (r'\bASP-?DAC\b', 'ASP-DAC'), (r'\bRTL\b', 'RTL'), (r'\bSoC\b', 'SoC'),
             (r'\bDFT\b', 'DFT'), (r'\bSTA\b', 'STA'), (r'\bASIC\b', 'ASIC')]

# 学历
DEG_KW = ['硕士', '研究生', '博士', '博后', 'PhD', 'PHD', 'MSc', 'Master', 'MPhil']

# AI / 大模型能力（对应 JD 第 1、3、4、5 条）
AI_KW = [
    '大模型', 'LLM', 'MLLM', '多模态', 'VLM', 'Agent', '智能体', 'RAG', '微调', 'SFT',
    'LoRA', 'QLoRA', 'DPO', 'GRPO', 'PPO', 'RLHF', '强化学习', 'PyTorch', 'Transformer',
    'NLP', 'CV', '深度学习', '机器学习', '算法', 'prompt', '上下文工程', 'MCP',
    'LangChain', '向量数据库', '知识库', '预训练', '推理优化', '模型部署', 'vLLM',
    '蒸馏', '量化', 'Qwen', 'LLaMA', 'ChatGLM', 'Baichuan',
]

# ---- 招聘范围 / 求职意向（★ 刘杨 2026-09-23 口径：只要实习生和社招，不要校招）----
# ⚠️ 只认「在找什么」，不认「身份」：在读研究生找实习 = 实习（要），
#    已毕业的人找校招 HC = 校招（不要）。所以不能用「在读 / 应届」这类身份词当门槛，
#    也不能用光杆「实习」当减分项（「曾在腾讯实习」是经历，不是意向）。
INTENT_INTERN = [
    '实习生', '实习岗位', '实习岗', '实习机会', '求实习', '找实习', '应聘实习',
    '到岗实习', '可实习', '每周可实习', '连续实习', '实习时间', '实习期',
    '长期实习', '实习转正', '等待实习',
]

INTENT_CAMPUS = [
    '校招', '校园招聘', '秋招', '春招', '应届', '应届生', '校招生',
    '正职机会', '校招hc', '秋招hc',
]

# ★ 刘杨 2026-09-23 补充 —— **校招最明显的两个标志**：
#   ① 「2027 年（明年）毕业」→ 27 届 / 2027 届；
#   ② 「申请全职岗位，但本人还在校」。
CAMPUS_GRAD_RE = [
    (r'(?<!\d)(?:20)?27\s*届', '27届'),
    (r'2027\s*年\s*毕业', '2027年毕业'),
    (r'2027\s*年\s*\d{1,2}\s*月', '2027年毕业'),
    (r'明年\s*毕业', '明年毕业'),
    (r'27\s*年\s*毕业', '27年毕业'),
]

# 「本人还在校」的判定词（配合「岗位名不含实习」使用 = 在校投全职岗 → 校招）
STUDENT_KW = [
    '在读', '在校', '在读研究生', '在读硕士', '在读博士',
    '本科在读', '硕士在读', '博士在读',
    '研一', '研二', '研三', '大二', '大三', '大四', '学生',
]

JOB_SOCIAL = '大模型 / Agent算法工程师'

# 意向标签
I_INTERN = '实习'
I_CAMPUS = '校招'
I_OTHER = '其他（社招/未表态）'

# 分级排序：X（校招 · 不推进）永远排在最后
LEVEL_ORDER = {'S': 0, 'A': 1, 'A-': 2, 'B': 3, 'B-': 4, 'C': 5, 'X': 9}


def hit(text, kws):
    """关键词命中。
    纯英文且较短的词（如 EDA / SoC / RAG / SFT）使用词边界匹配，
    避免 PagedAttention 命中 EDA、WebSocket 命中 SoC、storage 命中 RAG 之类的误报。
    """
    up = text.upper()
    out = []
    for k in kws:
        ku = k.upper()
        if re.fullmatch(r'[A-Za-z0-9_.\-]+', k) and len(k) <= 6:
            if re.search(r'(?<![A-Za-z0-9])' + re.escape(ku) + r'(?![A-Za-z0-9])', up):
                out.append(k)
        elif ku in up:
            out.append(k)
    return out


def hit_re(text, patterns):
    return [name for pat, name in patterns if re.search(pat, text, re.I)]


def intent_of(text, job):
    """兼容包装：只返回意向标签。"""
    return intent_detail(text, job)[0]


def intent_detail(text, job):
    """返回 (求职意向, 排除原因)。

    ★ 刘杨 2026-09-23：**只要实习生 + 社招，不要校招**。
      「校招最明显的标志就是 2027 年（明年）毕业，或者申请全职岗位但自己还在校。」
      「**投实习岗的当然是实习生候选人**。」
    判定顺序（先到先得）：
      ① **岗位名含「实习」→ 实习** —— 岗位是第一判据，届别不覆盖它
         （27 届投实习岗 **仍是实习生候选人**）
      ② 其余都是**全职岗**，此时才看校招标志：
         a. 「2027 届 / 明年毕业」→ **校招**
         b. 「本人还在校」（在读 / 研一~研三 / 学生）→ **校招**
         c. 打招呼里明确要**校招 / 秋招 / 春招 / 应届** → **校招**
         d. 明确**求实习**（可实习 / 实习期 / 长期实习…）→ **实习**
      ③ 其余 → **其他（社招/未表态）**
    """
    if '实习' in job:
        return I_INTERN, '实习：投的就是实习岗'
    g = hit_re(text, CAMPUS_GRAD_RE)
    if g:
        return I_CAMPUS, '校招：%s（明年毕业）' % g[0]
    if hit(text, STUDENT_KW):
        return I_CAMPUS, '校招：在校投全职岗'
    if hit(text, INTENT_CAMPUS):
        return I_CAMPUS, '校招：打招呼含校招/秋招/应届'
    if hit(text, INTENT_INTERN):
        return I_INTERN, '实习：投全职岗但明确求实习'
    return I_OTHER, ''


def classify(text, job):
    """返回 (等级, EDA命中, 学历命中, AI命中)"""
    eda = sorted(set(hit(text, EDA_KW) + hit_re(text, EDA_REGEX)))
    deg = hit(text, DEG_KW)
    ai = sorted(set(hit(text, AI_KW)))
    if eda:
        level = 'S'
    elif deg and len(ai) >= 3:
        level = 'A'
    elif deg and len(ai) >= 1:
        level = 'A-'
    elif len(ai) >= 3:
        level = 'B'
    elif len(ai) >= 1:
        level = 'B-'
    else:
        level = 'C'
    return level, eda, deg, ai


def main():
    rows = []
    with io.open(SRC, 'r', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            text = (r.get('最后消息内容') or '').strip()
            job = r.get('应聘岗位') or ''
            lv, eda, deg, ai = classify(text, job)
            # ★ 求职意向分流：校招 → X（按 2026-09-23 口径不推进）
            it, reason = intent_detail(text, job)
            r['求职意向'] = it
            r['关键词等级'] = lv
            if it == I_CAMPUS:
                r['等级'] = 'X'
                r['排除原因'] = reason
            else:
                r['等级'] = lv
                r['排除原因'] = ''
            r['EDA命中'] = '/'.join(eda)
            r['学历命中'] = '/'.join(deg)
            r['AI命中'] = '/'.join(ai[:8])
            r['_len'] = len(text)
            rows.append(r)

    rows.sort(key=lambda r: (LEVEL_ORDER.get(r['等级'], 8), -r['_len']))

    cnt = Counter(r['等级'] for r in rows)
    cnt_intent = Counter(r['求职意向'] for r in rows)

    # ---- 写 CSV ----
    cols = ['等级', '求职意向', '排除原因', '关键词等级', '序号', '姓名', '年龄', '性别', '应聘岗位',
            '最近时间', '最后消息发送方', '最后消息内容', 'EDA命中', '学历命中', 'AI命中',
            'uid', 'securityId']
    with io.open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ---- 写 Markdown ----
    L = []
    A = L.append
    A('# Boss直聘候选人自动筛选结果\n')
    A('**筛选依据**：AI+EDA研究员（DRAM设计方向）JD\n')
    A('**数据来源**：`boss_candidates.csv`（%d 人）\n' % len(rows))
    A('> ★ **招聘范围（刘杨 2026-09-23 口径）**：**只招「实习生」和「社招」，不做校招**。\n')
    A('> **校招的两个最基本标志**（刘杨原话）：「**最明显的标志就是 2027 年（明年）毕业，'
      '或者申请全职岗位但自己还在校**」。\n')
    A('> 命中上述任一条的候选人标为 **X**，单独成节、**不推进**；**校招者不再收简历**，'
      '若需联系**只答一句「我们这边是社招岗」**。CSV 里仍保留，未删除。\n')
    A('> 意向统计：**实习 %d · 校招 %d · 其他（社招/未表态）%d**\n'
      % (cnt_intent.get(I_INTERN, 0), cnt_intent.get(I_CAMPUS, 0), cnt_intent.get(I_OTHER, 0)))
    A('## 分级说明\n')
    A('| 等级 | 含义 | 人数 |')
    A('|---|---|---|')
    A('| **S** | 打招呼明确提到 **EDA/芯片设计/集成电路** 相关背景 | %d |' % cnt.get('S', 0))
    A('| **A** | 硕士/博士 + 大模型/Agent 能力（≥3 个关键词） | %d |' % cnt.get('A', 0))
    A('| **A-** | 硕士/博士 + 有 AI 相关经验 | %d |' % cnt.get('A-', 0))
    A('| **B** | 大模型/Agent 能力强，但未提学历 | %d |' % cnt.get('B', 0))
    A('| **B-** | 有 AI 相关经验，信息较少 | %d |' % cnt.get('B-', 0))
    A('| **C** | 无明显匹配信息 | %d |' % cnt.get('C', 0))
    A('| **X** | ⛔ **校招意向**（27 届/明年毕业 · 在校投全职岗 · 校招/秋招/应届）—— 不推进 | %d |' % cnt.get('X', 0))
    A('')
    A('---\n')

    for lv, title in [('S', '★ S 级：EDA / 芯片方向（最可能符合 JD 硬门槛）'),
                      ('A', '★ A 级：硕士/博士 + 大模型能力'),
                      ('A-', '○ A- 级：硕士/博士 + AI 经验')]:
        sub = [r for r in rows if r['等级'] == lv]
        if not sub:
            continue
        A('## %s（%d 人）\n' % (title, len(sub)))
        for i, r in enumerate(sub, 1):
            txt = r['最后消息内容'].replace('\n', ' ')
            A('**%d. %s**（%s，%s，%s，意向：%s）'
              % (i, r['姓名'], r['年龄'] + '岁', r['性别'], r['应聘岗位'], r['求职意向']))
            A('   > %s' % txt)
            if r['EDA命中']:
                A('   - 🔹 EDA/芯片关键词：`%s`' % r['EDA命中'])
            if r['学历命中']:
                A('   - 🎓 学历：`%s`' % r['学历命中'])
            if r['AI命中']:
                A('   - 🤖 AI 技能：`%s`' % r['AI命中'])
            A('')
        A('---\n')

    # B 级只列名字
    for lv, title in [('B', 'B 级：大模型/Agent 能力强（未提学历）'),
                      ('B-', 'B- 级：有 AI 经验（信息较少）')]:
        sub = [r for r in rows if r['等级'] == lv]
        if not sub:
            continue
        A('## %s（%d 人）\n' % (title, len(sub)))
        A('| # | 姓名 | 年龄 | 岗位 | 意向 | 最后消息 |')
        A('|---|---|---|---|---|---|')
        for i, r in enumerate(sub, 1):
            t = r['最后消息内容'].replace('\n', ' ')[:90]
            A('| %d | %s | %s | %s | %s | %s |'
              % (i, r['姓名'], r['年龄'], r['应聘岗位'].split(' ')[0], r['求职意向'], t))
        A('')
        A('---\n')

    # X 级：校招意向（按 2026-09-23 口径不推进）—— 单独成节，保留可核验
    sub = [r for r in rows if r['等级'] == 'X']
    if sub:
        A('## ⛔ X 级：校招意向（%d 人 · 按 2026-09-23 口径**不推进**）\n' % len(sub))
        A('> 依据：**只招实习生 + 社招，不要校招**；**校招者不再收简历**，'
          '若需联系**只答一句「我们这边是社招岗」**（考虑实习的话有实习岗），不解释、不挽留。\n')
        A('> 校招只在**投了全职岗**的人里判：①「2027 届（明年毕业）」或 ②「本人还在校」，'
          '或 ③打招呼里直接要校招/秋招/应届 HC。**投实习岗的一律是实习生候选人。**\n')
        A('| # | 姓名 | 年龄 | 岗位 | 关键词等级 | 排除原因 | 原话（截断） |')
        A('|---|---|---|---|---|---|---|')
        for i, r in enumerate(sub, 1):
            t = r['最后消息内容'].replace('\n', ' ')[:100]
            A('| %d | %s | %s | %s | %s | %s | %s |'
              % (i, r['姓名'], r['年龄'], r['应聘岗位'].split(' ')[0], r['关键词等级'],
                 r.get('排除原因', ''), t))
        A('')
        A('---\n')

    A('## 完整数据\n')
    A('- `候选人筛选结果.csv` —— 全部分级结果（可在 Excel 按「等级」/「求职意向」列排序筛选）')
    A('- `boss_candidates.csv` / `boss_candidates.json` —— 原始采集数据')

    with io.open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))

    print('OK  total=%d' % len(rows))
    for k in ['S', 'A', 'A-', 'B', 'B-', 'C', 'X']:
        print('  %-3s %d' % (k, cnt.get(k, 0)))
    print('--- 求职意向 ---')
    for k in [I_INTERN, I_CAMPUS, I_OTHER]:
        print('  %-14s %d' % (k, cnt_intent.get(k, 0)))


if __name__ == '__main__':
    main()
