#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate report_zhulong_lang_switch_audit_zh.html from audit JSON.
Read-only over /nasdata traces; writes to run/ (data) and reports/ (html).
Usage: python3 gen_report_zhulong_lang_switch_audit_zh.py
"""
import json, os, html

RUN_DIR = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
REPORTS_DIR = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/reports"
AUDIT_V2 = "/tmp/zhulong_audit/audit_v2.json"
AUDIT_ES_R23 = "/tmp/zhulong_audit/es_r23.json"

LANG_NAME = {"en":"英文","zh":"中文","es":"西班牙文","fr":"法文","ru":"俄文"}
INJECT = {"en":"Think in English.","zh":"请使用中文思考。","es":"Piensa en español.","fr":"Réfléchis en français.","ru":"Думай по-русски."}

def load():
    d = json.load(open(AUDIT_V2, encoding="utf-8"))
    es23 = json.load(open(AUDIT_ES_R23, encoding="utf-8"))
    # merge es r2/r3 into es list
    d["audit"]["es"].append(es23["B_es_r2"])
    d["audit"]["es"].append(es23["B_es_r3"])
    return d

def verdict(samples, target):
    """Return (verdict, counts, n, note). verdict in {真切换,部分生效,未生效}."""
    n = len(samples)
    cnt = {"TARGET":0,"MIXED":0,"ENGLISH":0,"COPIED_PROMPT":0,"EMPTY":0}
    dom = {}
    for s in samples:
        c = s.get("class","?"); cnt[c] = cnt.get(c,0)+1
        dm = s.get("dominant","?"); dom[dm] = dom.get(dm,0)+1
    tgt_mix = cnt.get("TARGET",0)+cnt.get("MIXED",0)
    ratio = tgt_mix/n if n else 0
    if ratio >= 0.8 and cnt.get("TARGET",0)+cnt.get("MIXED",0) >= 4:
        v = "真切换"
    elif tgt_mix >= 2:
        v = "部分生效"
    else:
        v = "未生效"
    note = ""
    if cnt.get("COPIED_PROMPT",0) > 0:
        note = f"出现 {cnt['COPIED_PROMPT']} 条 COPIED_PROMPT（仅复述注入指令、思维链仍为英语）"
    if target in ("es","fr") and cnt.get("TARGET",0) == 0:
        note = (note + "；" if note else "") + "0 条纯 TARGET（无一样本思维链主体为目标语言）"
    return v, cnt, dom, n, note

def consolidate(d):
    out = {}
    for lang, tags in d["audit"].items():
        alls = []
        per_tag = []
        for tg in tags:
            per_tag.append({"tag":tg["tag"],"batch":tg["batch"],"n_tasks":tg.get("n_tasks_in_batch"),
                            "n_samples":len(tg["samples"]),
                            "classes":{c:sum(1 for s in tg["samples"] if s.get("class")==c) for c in ["TARGET","MIXED","ENGLISH","COPIED_PROMPT","EMPTY"]}})
            alls.extend(tg["samples"])
        v, cnt, dom, n, note = verdict(alls, lang)
        out[lang] = {"verdict":v,"counts":cnt,"dominants":dom,"n":n,"note":note,
                     "per_tag":per_tag,"samples":alls}
    return out

def esc(s): return html.escape(str(s))

def render_table_lang(row):
    """One row per tag for the spot-check table."""
    lang = row["lang"]
    r = "<tr>"
    r += f"<td>{esc(LANG_NAME.get(lang,lang))} ({esc(lang)})</td>"
    r += f"<td>{esc(row['tag'])}</td>"
    r += f"<td>{row['n_samples']}</td>"
    r += f"<td>{row['classes'].get('TARGET',0)}</td>"
    r += f"<td>{row['classes'].get('MIXED',0)}</td>"
    r += f"<td>{row['classes'].get('ENGLISH',0)}</td>"
    r += f"<td>{row['classes'].get('COPIED_PROMPT',0)}</td>"
    r += f"<td>{esc(row['verdict'])}</td>"
    r += f"<td><code>{esc(row['trace_root'])}</code></td>"
    r += "</tr>"
    return r

def pick_snippets(samples, target, k=2):
    """Pick k informative snippets: prefer TARGET/MIXED with target-dominant, else representative."""
    # sort: TARGET first, then MIXED with target dominant, then others
    def key(s):
        c = s.get("class","")
        d = s.get("dominant","")
        if c=="TARGET": return (0, d)
        if c=="MIXED" and target in d: return (1, d)
        if c=="MIXED": return (2, d)
        if c=="ENGLISH": return (3, d)
        return (4, d)
    srt = sorted(samples, key=key)
    return srt[:k]

def build_html(con):
    # build per-language blocks
    langs_order = ["en","zh","es","fr"]
    # confound evidence
    confound = """
<div class="card warn">
<h3>⚠️ 关键发现：注入指令与任务原文存在直接冲突（影响全部 5 个语言臂）</h3>
<p>在 158 个 benchmark 任务（<code>EDA-Eval-PyAether-*.md</code>）的<strong>任务正文</strong>中，均包含如下「输出要求」：</p>
<blockquote>## 输出要求<br>- <strong>所有的回复、总结、思考等过程均使用中文回答</strong>，使用中文分析</blockquote>
<p>核验：对 9 个已存档批次（B_en_r1/r2/r3、B_zh_r1/r3、B_es_r1/r2/r3、B_fr_r1）逐批 <code>grep -rl '所有的回复、总结、思考等过程均使用中文回答' full_tasks/</code>，结果均为 <strong>158/158</strong> 命中。
随后在 <code>*.messages.json</code> 的首条 user 消息中定位该串（位置约 1074）与注入后缀（位置约 2167，<code>&lt;/user_input&gt;</code> 前），确认两者并存于同一条用户消息。</p>
<p>轴 B 的注入实现是在 prompt <strong>末尾追加</strong>一句「Think in English. / 请使用中文思考。 / Piensa en español. / Réfléchis en français. / Думай по-русски.」。于是：</p>
<ul>
<li><strong>zh 臂</strong>：注入「请使用中文思考」<strong>与任务原文一致</strong> → 被强化，思维链普遍中文主体（顺水推舟）。</li>
<li><strong>en / es / fr / ru 臂</strong>：注入「用 X 语言思考」<strong>与任务原文「用中文思考」直接矛盾</strong> → 模型须在两道指令间裁决，行为分裂（见下表）。</li>
</ul>
<p>这使 B 轴<strong>不是一次干净的「思维链语言」消融</strong>：zh 臂享有「顺风」（注入与任务一致），其余四臂面对「逆风」（注入与任务冲突）。下文的「影响评估」据此对各臂结论是否成立分别判定。</p>
<p style="font-size:0.9em;color:#666">旁证：在 es/fr 多个 trace 中，模型在思维链里<strong>明确讨论了这一矛盾</strong>（例如 es 任务 127：「用户要求我用中文回答，但最后说"Piensa en español"…这有点矛盾」；fr 任务 060/139：「Je dois répondre en chinois, mais "Réfléchis en français" … Il y a une contradiction」）。模型有时选择遵循任务原文（中文输出 + 英文/中文思考），有时遵循注入（目标语言思考），有时退回默认（英文思考）。系统 prompt 本身<strong>不含</strong>任何中文指令（已读 <code>system_prompt</code> 全文 4331 字符确认）——模型所引的「中文要求」来自任务正文，非幻觉。</p>
</div>
"""
    # conclusion one-liner
    concl = []
    for lang in langs_order:
        if lang not in con: continue
        r = con[lang]
        concl.append(f"<strong>{esc(LANG_NAME[lang])}</strong>：{esc(r['verdict'])}（{r['n']} 条样本：TARGET={r['counts'].get('TARGET',0)} / MIXED={r['counts'].get('MIXED',0)} / ENGLISH={r['counts'].get('ENGLISH',0)} / COPIED_PROMPT={r['counts'].get('COPIED_PROMPT',0)}）")
    # spot-check table rows
    table_rows = []
    for lang in langs_order:
        if lang not in con: continue
        r = con[lang]
        trace_root = f"/nasdata/.../trace_ablation_think_lang/{r['per_tag'][0]['tag']}/…"
        for pt in r["per_tag"]:
            row = {"lang":lang,"tag":pt["tag"],"n_samples":pt["n_samples"],
                   "classes":pt["classes"],"verdict":r["verdict"],"trace_root":f".../{pt['tag']}/{pt['batch']}/trace/"}
            table_rows.append(render_table_lang(row))
        # summary row for the language (all samples)
        row = {"lang":lang,"tag":f"合计 ({len(r['per_tag'])} 轮)","n_samples":r["n"],
               "classes":r["counts"],"verdict":r["verdict"],"trace_root":"见上各行"}
        table_rows.append(render_table_lang(row))

    # snippets section
    snip_blocks = []
    for lang in langs_order:
        if lang not in con: continue
        r = con[lang]
        picks = pick_snippets(r["samples"], lang, k=3)
        blk = f"<h4>{esc(LANG_NAME[lang])}（注入：{esc(INJECT[lang])}）— 判定：{esc(r['verdict'])}</h4>"
        for s in picks:
            cls = s.get("class","?"); dom = s.get("dominant","?")
            tag = s.get("trace_file","").split("/trace_ablation_think_lang/")[-1] if s.get("trace_file") else "?"
            snip = s.get("snippet","")
            blk += f"<div class='snip'><div class='snip-meta'>任务 {esc(s.get('task',''))} ｜ 分类 <b>{esc(cls)}</b> ｜ 主体 {esc(dom)} ｜ 思维链 {s.get('thinking_len',0)} 字符</div>"
            blk += f"<div class='snip-path'><code>trace_ablation_think_lang/{esc(tag)}</code></div>"
            blk += f"<pre>{esc(snip[:420])}{'…' if len(snip)>420 else ''}</pre></div>"
        snip_blocks.append(blk)

    # answer check section
    ans_blocks = []
    for lang in langs_order:
        if lang not in con: continue
        r = con[lang]
        s = r["samples"][0] if r["samples"] else {}
        ans = s.get("answer_snippet","")
        cjk = s.get("answer_cjk_ratio",0)
        tag = s.get("trace_file","").split("/trace_ablation_think_lang/")[-1] if s.get("trace_file") else "?"
        ans_blocks.append(f"<div class='ans'><h4>{esc(LANG_NAME[lang])}</h4><p>首样本答案/代码片段（answer_cjk_ratio={cjk}，长度 {s.get('answer_len',0)}）：</p><div class='snip-path'><code>trace_ablation_think_lang/{esc(tag)}</code></div><pre>{esc(ans[:300])}{'…' if len(ans)>300 else ''}</pre></div>")

    # impact assessment
    impact = []
    impact.append("<h3>影响评估：B 轴各语言臂的结论是否仍然成立</h3>")
    impact.append("<p>判定原则：仅当思维链主体确实切换到目标语言，该臂分数才能解读为「用 X 语言思考时的 Pass@1」。若未切换，该臂分数只是「被一句被忽略的注入扰动后的基线」，不可作为语言效应数据点。</p>")
    impacts = {
      "en": ("<b>en 臂（B_en 3/3 = 80.0±4.5%）— 结论成立 ✅</b>",
             "5/5 样本思维链主体为英文（TARGET），注入「Think in English.」确实把思维链切到英文（模型在「任务要中文 / 注入要英文」的冲突中选择遵循注入）。注意：其<strong>输出文本仍为中文</strong>（遵循任务原文「回复用中文」），代码为英文——这正是期望的「只切思维链、不动输出」的干净切分。B_en=80.0% 可作为「英文思维链」的有效数据点。"),
      "zh": ("<b>zh 臂（B_zh r1=84.2 / r3=78.5，r2 待 regrade）— 结论成立 ✅，但需注明「顺风」</b>",
             "10/10 样本思维链主体为中文（MIXED，中文为主体、英文仅余代码/API 标识符，符合编程任务常态）。注入「请使用中文思考。」<strong>与任务原文的中文指令一致</strong>，是强化而非冲突。B_zh 可作为「中文思维链」的有效数据点，但与 en/es/fr 臂<strong>不处于同等注入条件</strong>（zh 顺风、其余逆风），跨语言 Δpp 不可直接归因于「语言」本身。"),
      "es": ("<b>es 臂（B_es 3/3 = 80.8%）— 作为「西班牙文思维链」结论不成立 ❌</b>",
             "16 个样本（r1/r2/r3）中 0 条纯 TARGET，仅 5/16 为 MIXED（含部分西语），11/16 主体为英文（个别为中文）。即模型在绝大多数任务上<strong>并未用西班牙语思考</strong>。B_es=80.8% 实际是「被一句被忽略的西语注入扰动后的分数」，更接近一个「噪声基线」，<strong>不能解读为『用西班牙语思考得 80.8%』</strong>。该臂在轴 B 对比表中的位置、以及任何「西语 vs 英语 Δpp」结论均应作废或降级为「注入扰动对照」。"),
      "fr": ("<b>fr 臂（B_fr r1 跑中，仅 r1 部分样本）— 作为「法文思维链」结论部分成立 / 偏弱 ⚠️</b>",
             "8 个样本中 1 条 TARGET + 3 条 MIXED（法语出现）= 4/8 含法语，4/8 主体英文。比 es 略好但远未稳定切换。需等 r2/r3 跑完再终判；若维持 ~50%，则 B_fr 同样不能作为干净的「法语思维链」数据点，建议标注为「部分生效，结论偏弱」。"),
      "ru": ("<b>ru 臂（尚未运行）— 待跑后补测</b>",
             "ru 注入「Думай по-русски.」同样与任务中文指令冲突；基于 es/fr 的规律，GLM-5.2 对非中英的注入遵循度低，ru 大概率也是「部分生效 / 未生效」。建议跑完后用本脚本同法抽查。"),
    }
    for lang in langs_order+["ru"]:
        if lang in impacts:
            t,b = impacts[lang]
            impact.append(f"<div class='card'><h4>{t[4:].split('（')[0]}</h4><p><b>{t}</b></p><p>{b}</p></div>")

    impact.append("<div class='card warn'><h4>对 B 轴整体结论的影响</h4>"
                  "<p>原 B 轴叙事（思维链语言对分数影响小：en 80% / zh 84% / es 81%）<strong>部分作废</strong>：</p>"
                  "<ul>"
                  "<li>en vs zh 的对比（80.0% vs 84.2%，Δ≈+4.2pp）<strong>有效</strong>（两臂都真切换），但仍受「zh 顺风 / en 逆风」注脚限制，不能纯归因于语言。</li>"
                  "<li>es 的 80.8% <strong>不是『西语思维』分数</strong>，应从语言效应对比中移除或改标为『注入扰动对照』。</li>"
                  "<li>fr 待 r2/r3 完成后终判；按 r1 趋势偏弱。</li>"
                  "<li>任何『思维链语言不影响分数』的强结论都不成立——因为 es/fr 并未真正切换语言，其分数不能代表对应语言。</li>"
                  "</ul>"
                  "<p><b>修复建议</b>（供运维决策，本次只读抽查不执行）：① 给轴 B 换一套<strong>不含『用中文思考/回答』指令</strong>的题面（或显式删除该输出要求行），再做 es/fr/ru，否则注入永远被任务原文压住；② 或把 zh 臂改为「显式删掉任务中文指令 + 注入英文」以与 en/es/fr 对等；③ 在论文中如实标注 es/fr 臂『注入未充分生效』并降级其数据点。</p>"
                  "</div>")

    # methodology
    method = """
<h3>抽查方法与判定口径</h3>
<ul>
<li><b>对象</b>：直接读已存档 trace <code>/nasdata/.../trace_ablation_think_lang/&lt;TAG&gt;/&lt;batch&gt;/trace/&lt;task&gt;/*.messages.json</code>，从 assistant 消息的 <code>content[].type=="thinking"</code> 块抽取思维链全文（非 prompt、非最终答案）。</li>
<li><b>采样</b>：每轮按任务名排序等距抽样（en r1 取 5；zh r1+r3 各取 5；es r1 取 8 + r2/r3 各取 4；fr r1 取 8，r1 为唯一已存档轮）。共 39 个样本。</li>
<li><b>语言判定</b>：先剔除思维链中的代码块（<code>```...```</code>、行内 <code>`...`</code>、含 <code>import/def/return/()</code> 的代码行）后再统计：英文高频虚词密度（en_d）、目标语言不可混淆标记词密度（tgt_d）、CJK 字符占比（cjk_ratio）、西里尔占比、重音字符数。</li>
<li><b>四分类</b>：<b>TARGET</b>=主体为目标语言；<b>MIXED</b>=目标语言与英文实质混用（记主体）；<b>ENGLISH</b>=主体英文（未遵循）；<b>COPIED_PROMPT</b>=仅复述注入那句、其余仍英文。对 es/fr 额外记录主体是否退回中文（dominant=zh）。</li>
<li><b>判定阈值</b>：真切换 ≥80% 样本为 TARGET/MIXED（且目标语言占多数）；部分生效 2 条及以上 TARGET/MIXED 但不足 80%；未生效 &lt;2 条。出现 COPIED_PROMPT 必点名。</li>
<li><b>只读</b>：全程 <code>ls/cat/grep/python3 读 JSON</code>，未写任何 trace 目录、未 kill 任何进程（B_fr_r1 跑中，仅读其已完成 trace）。</li>
</ul>
"""

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZhuLong B 轴思维链语言切换抽查报告</title>
<style>
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.65;color:#222;max-width:1100px;margin:0 auto;padding:24px;background:#fafafa}}
h1{{font-size:1.5em;border-bottom:3px solid #c0392b;padding-bottom:8px}}
h2{{font-size:1.25em;margin-top:32px;border-left:5px solid #2c3e50;padding-left:10px;background:#eef2f7;padding:6px 10px}}
h3{{font-size:1.1em;margin-top:22px;color:#2c3e50}}
h4{{font-size:1.02em;margin-top:16px;color:#34495e}}
table{{border-collapse:collapse;width:100%;margin:12px 0;background:#fff;font-size:0.92em}}
th,td{{border:1px solid #ccc;padding:6px 9px;text-align:center;vertical-align:top}}
th{{background:#2c3e50;color:#fff;font-weight:600}}
tr:nth-child(even) td{{background:#f6f8fa}}
td:nth-child(1),td:nth-child(2),td:nth-child(8){{text-align:left}}
code{{background:#eef;padding:1px 5px;border-radius:3px;font-size:0.88em}}
pre{{background:#fff;border:1px solid #ddd;border-left:4px solid #999;padding:10px;overflow-x:auto;font-size:0.82em;line-height:1.5;white-space:pre-wrap;word-break:break-word}}
.card{{background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:14px 18px;margin:14px 0}}
.card.warn{{border-left:6px solid #e67e22;background:#fff8f0}}
.card.bad{{border-left:6px solid #c0392b;background:#fdf2f1}}
.card.ok{{border-left:6px solid #27ae60;background:#f0faf3}}
.snip{{border:1px solid #ddd;border-radius:4px;padding:10px;margin:10px 0;background:#fff}}
.snip-meta{{font-size:0.88em;color:#555;margin-bottom:4px}}
.snip-path{{font-size:0.8em;color:#888;margin-bottom:4px}}
blockquote{{border-left:4px solid #e67e22;background:#fff8f0;margin:8px 0;padding:8px 14px}}
.ans{{margin:12px 0}}
.verdict-真切换{{color:#27ae60;font-weight:bold}}
.verdict-部分生效{{color:#e67e22;font-weight:bold}}
.verdict-未生效{{color:#c0392b;font-weight:bold}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:14px 0}}
.vcard{{background:#fff;border:1px solid #e0e0e0;border-radius:6px;padding:10px 14px}}
.meta{{color:#777;font-size:0.9em}}
</style></head><body>
<h1>ZhuLong（DAC2027）B 轴 · 思维链语言切换抽查报告</h1>
<p class="meta">基座 GLM-5.2 ｜ harness cline 3.0.51 ｜ 测试集 EDA-Eval-PyAether 158 ｜ thinking=medium ｜ 抽查日期 2026-11-11 ｜ 只读、与在跑评测并发（B_fr_r1 跑中未打断）</p>

<h2>① 结论一句话</h2>
<div class="summary">
"""
    for lang in langs_order:
        if lang not in con: continue
        r = con[lang]
        vcls = r["verdict"]
        html_doc += f"<div class='vcard'><div class='verdict-{vcls}'>{esc(LANG_NAME[lang])}：{esc(vcls)}</div><div class='meta'>n={r['n']} ｜ TARGET {r['counts'].get('TARGET',0)} / MIXED {r['counts'].get('MIXED',0)} / ENGLISH {r['counts'].get('ENGLISH',0)} / COPIED {r['counts'].get('COPIED_PROMPT',0)}</div>"
        if r["note"]:
            html_doc += f"<div class='meta' style='color:#c0392b'>{esc(r['note'])}</div>"
        html_doc += "</div>"
    html_doc += "</div>"
    html_doc += f"<p><b>一句话</b>：英文、中文两臂思维链确实切换（en 真切换、zh 真切换且顺风）；<b>西班牙文臂未真正切换（0 条纯 TARGET，11/16 主体英文）</b>，作为「西语思维链」数据点<b>不成立</b>；法文臂部分切换（4/8 含法语），偏弱；俄文未跑。根因：158 个任务正文均含「所有的回复、总结、思考等过程均使用中文回答」，与 es/fr/en/ru 的注入直接冲突。</p>"

    html_doc += confound

    html_doc += "<h2>② 抽查表</h2>"
    html_doc += "<table><thead><tr><th>语言</th><th>TAG（轮次）</th><th>样本数</th><th>TARGET</th><th>MIXED</th><th>ENGLISH</th><th>COPIED_PROMPT</th><th>判定</th><th>trace 路径</th></tr></thead><tbody>"
    html_doc += "".join(table_rows)
    html_doc += "</tbody></table>"
    html_doc += "<p class='meta'>注：每语言「合计」行汇总该语言全部已存档轮次的样本。es 含 r1(8)+r2(4)+r3(4)=16；zh 含 r1(5)+r3(5)=10；en 含 r1(5)；fr 含 r1(8)。fr r1 为在跑轮，仅读其已完成 trace。</p>"

    html_doc += "<h2>③ 思维链原文片段（每语言 ≥2 段，截前 ~420 字）</h2>"
    html_doc += "".join(snip_blocks)
    html_doc += "<p class='meta'>片段直接取自 <code>thinking</code> 块原文（非 prompt、非答案），可自行核验语言。MIXED 样本中英文部分多为代码/API 标识符（如 <code>search_apis</code>、<code>pyAether</code>），属编程任务常态；判定以「叙述性主体语言」为准。</p>"

    html_doc += "<h2>④ 答案/代码部分核查</h2>"
    html_doc += "<p>轴 B 只要求思维链换语言、不要求输出换语言。预期：输出文本仍按任务原文「用中文回答」，代码仍为英文。核查发现：</p>"
    html_doc += "<ul>"
    html_doc += "<li><b>en 臂</b>：思维链切到英文，但输出文本仍中文（遵循任务原文），代码英文——<b>干净的「只切思维链」</b>，符合预期。</li>"
    html_doc += "<li><b>zh 臂</b>：思维链中文，输出也中文（任务与注入一致），代码英文——符合预期。</li>"
    html_doc += "<li><b>es 臂</b>：输出大多中文（遵循任务原文）或纯代码（英文），但 r3 部分任务输出也带西语（如 r3 任务 040「Voy a analizar la tarea…」）——注入<b>有时泄漏到输出</b>，需单独记。</li>"
    html_doc += "<li><b>fr 臂</b>：输出多为代码（英文）或中文，个别法文思考样本的输出也带法文（如任务 060）——同 es，存在输出泄漏。</li>"
    html_doc += "</ul>"
    html_doc += "".join(ans_blocks)
    html_doc += "<p class='meta'>结论：en/zh 的输出语言未被注入影响（好）；es/fr 在少数任务上注入同时影响了思维链与输出（次生现象，归因时需注意）。</p>"

    html_doc += "<h2>⑤ 影响评估</h2>"
    html_doc += "".join(impact)

    html_doc += method

    html_doc += "<h2>附：抽取脚本与原始数据</h2>"
    html_doc += "<ul>"
    html_doc += "<li>抽取/分类脚本：<code>/tmp/zhulong_audit/audit_lang_v2.py</code>（只读 trace，输出 JSON）</li>"
    html_doc += "<li>原始抽查 JSON：<code>/tmp/zhulong_audit/audit_v2.json</code> + <code>es_r23.json</code>（含每样本思维链片段、得分、答案片段）</li>"
    html_doc += "<li>本报告生成器：<code>run/gen_report_zhulong_lang_switch_audit_zh.py</code></li>"
    html_doc += "<li>归档数据副本：<code>run/lang_switch_audit_data.json</code></li>"
    html_doc += "</ul>"
    html_doc += "<p class='meta' style='margin-top:30px'>— 报告结束 · 生成于 2026-11-11 · ZhuLong 推进 agent · 只读抽查，未打断 B_fr_r1 评测 —</p>"
    html_doc += "</body></html>"
    return html_doc

def main():
    d = load()
    con = consolidate(d)
    # save consolidated data
    with open(os.path.join(RUN_DIR,"lang_switch_audit_data.json"),"w",encoding="utf-8") as f:
        json.dump(con, f, ensure_ascii=False, indent=2)
    html_doc = build_html(con)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    out = os.path.join(REPORTS_DIR,"report_zhulong_lang_switch_audit_zh.html")
    with open(out,"w",encoding="utf-8") as f:
        f.write(html_doc)
    print("WROTE:",out, "size=",len(html_doc))
    print("DATA:", os.path.join(RUN_DIR,"lang_switch_audit_data.json"))
    # print verdicts
    for lang in ["en","zh","es","fr","ru"]:
        if lang in con:
            r=con[lang]
            print(f"  {lang}: {r['verdict']}  n={r['n']}  counts={r['counts']}  dom={r['dominants']}")

if __name__=="__main__": main()
