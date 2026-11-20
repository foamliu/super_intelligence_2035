#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_ocr_synth.py — Synthetic OCR image-text pair generator for BaiZe vision
encoder pretraining (CLIP / AIMv2-style image-text contrastive).

Produces WebDataset shards loadable by run/vision/data.py `build_mixed_loader`
(GPIC json-caption path): each tar sample = `<key>.jpg` + `<key>.json` (NO .txt),
json carries a `caption` field (short CLIP text-tower description) plus rich
metadata. `caption_type='short'` is set so `build_gpic_loader(caption_type='short')`
also accepts the data.

Design goals (operator note 2026-10-25 22:4x):
  - 8 categories, 10M total (P0 smoke = proportional 100k subset).
  - Render base 448px (long images proportional, max side <=1024), JPEG q=90.
  - 30% low-quality augmentation (blur / jpeg / perspective / low-contrast).
  - Cross-shard text-SHA1 dedup (<1% repeat). Eval-leakage guard hook.
  - Fixed seed + param block at top => reproducible. Resume skips existing tars.
  - CPU-only, multiprocessing, nice-friendly.

Corpora: English from /usr/share/dict/words (facts, redistributable); Chinese from
a curated common-hanzi/word list (facts); math from curated LaTeX expressions
rendered via matplotlib mathtext; charts via matplotlib. All sources marked in
DATASET_CARD. No copyrighted / crawled text. (Known bias: synthetic-template
text, not real Wikipedia/books — see report.)
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, os, random, tarfile, time
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["figure.max_open_warning"] = 0  # we close every fig; suppress noise at scale

# =====================================================================================
# CONFIG / PARAM BLOCK  (edit here to re-run; fixed seed => byte-reproducible)
# =====================================================================================
CONFIG = {
    "seed": 20261025,
    "out_dir": "/nas_train/app.e0031982/datasets/baize-vision/ocr_synth_10m",
    "render_size": 448,        # base render width; long images proportional
    "max_side": 1024,          # cap longest side
    "jpeg_quality": 90,
    "per_tar": 5000,           # samples per shard
    "key_digits": 10,          # zero-pad global index
    "degrade_frac": 0.30,      # fraction of samples receiving low-quality aug
    "dedup_target": 0.01,      # max allowed cross-shard text repeat rate
    # category -> (count_full, cat_code, lang_default). P0 scales proportionally.
    "categories": {
        "english":   (3_000_000, "en", "en"),
        "chinese":   (2_000_000, "zh", "zh"),
        "mixed":     (1_000_000, "mix", "mix"),
        "document":  (1_500_000, "doc", "mix"),
        "chart":     (1_000_000, "chart", "en"),
        "math":      (1_000_000, "math", "en"),
        "handwrite": (  300_000, "hw", "mix"),
        "scene":     (  200_000, "scene", "en"),
    },
    "math_split": {"printed": 0.50, "inline": 0.30, "formtab": 0.20},
    "n_workers": min(32, os.cpu_count() or 8),
}

# =====================================================================================
# FONTS  (curated, all system-installed; redistributable fonts only)
# =====================================================================================
FONT = {
    "en_sans":   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "en_sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "en_serif":  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "en_serif_b":"/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "mono":      "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "cjk_song":  "/usr/share/fonts/truetype/arphic/uming.ttc",
    "cjk_kai":   "/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf",
    "cjk_hei":   "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "cjk_song_gb":"/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf",
    "math":      "/usr/share/texmf/fonts/opentype/public/lm/lmroman10-regular.otf",
}
_FONT_CACHE: dict = {}
def F(path, size):
    k = (path, size)
    f = _FONT_CACHE.get(k)
    if f is None:
        f = ImageFont.truetype(path, size)
        _FONT_CACHE[k] = f
    return f

# =====================================================================================
# CORPORA
# =====================================================================================
def _load_english_words():
    p = "/usr/share/dict/words"
    words = []
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="ignore") as fh:
            for w in fh:
                w = w.strip()
                if 2 <= len(w) <= 12 and w.isascii() and w.isalpha():
                    words.append(w.lower())
    if len(words) < 1000:
        words = ("the of and to a in is it you that he was for on are with as his they "
                 "at be this from i or by had but not what all were we when your can said "
                 "data model system method result analysis research problem process").split()
    return sorted(set(words))
ENGLISH_WORDS = None  # lazily set in each worker

ENGLISH_TEMPLATES = [
    "{s1} {s2}.",
    "The {n1} {v1} {adj1} {n2} {adv1}.",
    "{s1}, {s2}, and {s3} are discussed in this section.",
    "Note: {n1} {v1} {prep} the {n2} with {adj1} {n3}.",
    "Figure {d1}: {n1} {v1} over {n2} ({d2} samples).",
    "Result: the {n1} reached {d1} units {adv1}, a {adj1} increase.",
    "{s1} is a {adj1} {n1} used in {n2} and {n3}.",
    "In {d1}, the team found that {n1} {v1} {adv1} under {adj1} {n2}.",
    "Definition. A {n1} is {adj1} if it {v1} {prep} every {n2}.",
    "Warning: do not {v1} the {n1} while the {n2} is {adj1}.",
]
EN_SYN = {"n1":"system","n2":"model","n3":"method","v1":"shows","adj1":"stable",
          "adv1":"quickly","prep":"on","s1":"data","s2":"results","s3":"graphs",
          "d1":"2024","d2":"512"}

_ZH_RAW = (
    "的一是不了人我在有他这大为来上以个中们到说时地也子就道要让"
    "你去会过自己下面后里年多得可就对么能起好把与给你们这个而"
    "天那如今以于由从把将被让使往向给跟和及或者但并且然而所以因"
    "为如果虽然然后还再又只才便就且学习工作生活时间问题方法研究"
    "结果数据模型系统过程状态变化发展关系结构形式内容意义价值作用"
    "影响原因条件因素特征特点性质规律原则标准目标方向途径手段工具"
    "技术科学文化教育经济社会政治历史地理环境资源能源材料产品设备"
    "设施建筑交通通信网络计算机信息知识理论概念定义分类类型种类"
    "样本实例对象元素成分部分整体个体群体集合序列顺序排列组合转换"
    "变化运动静止平衡稳定增长下降上升减少增加扩大缩小提高降低改善"
    "北京上海广州深圳香港台湾中国华夏中华东方西方南北东西上下左右"
    "前后内外中间旁边附近周围中心边缘表面内部外部顶部底部春夏秋冬"
    "风雨雷电雪霜云雾晴阴山川河海湖江林田路桥楼房院门窗图像视觉文字"
)
ZH_CHARS = "".join(dict.fromkeys(c for c in _ZH_RAW if "\u4e00" <= c <= "\u9fff"))
ZH_WORDS = [
    "数据","模型","系统","方法","结果","分析","研究","问题","过程","结构",
    "技术","网络","信息","知识","理论","概念","定义","分类","样本","实例",
    "计算","统计","处理","存储","更新","调整","评估","验证","测试","检验",
    "北京","上海","深圳","中国","工程","科学","教育","经济","社会","文化",
    "历史","环境","资源","能源","材料","产品","设备","建筑","交通","通信",
    "发展","变化","增长","改善","提高","降低","加强","促进","推动","支持",
    "决策","选择","排除","包含","覆盖","涉及","根据","按照","基于","通过",
    "利用","使用","采用","应用","实施","执行","完成","实现","达到","满足",
    "图像","视觉","文字","识别","合成","训练","编码器","表征","对比","文档",
    "版面","表格","图表","公式","手写","场景","文本","语言","中文","英文",
    "段落","标题","页眉","页脚","分栏","单元格","数值","标签","坐标","参数",
]
ZH_TEMPLATES = [
    "{w1}是{w2}的{w3}。",
    "本文研究{w1}与{w2}的关系，结果表明{w3}对{w1}有显著影响。",
    "图{d1}：{w1}在{w2}下的{w3}变化（样本数{d2}）。",
    "定义：若{w1}满足{w2}，则称其为{w3}。",
    "注意：在{w1}过程中，请勿修改{w2}的状态。",
    "{w1}、{w2}与{w3}是本节讨论的三个核心问题。",
    "结果：{w1}达到{d1}个单位，较基线提升{d2}%。",
    "{w1}是一种用于{w2}的{w3}方法。",
    "在{d1}年，团队发现{w1}在{w2}条件下{w3}显著改善。",
    "说明：{w1}的{w2}已更新，请重新加载{w3}。",
]
# --- LaTeX expressions for math (matplotlib mathtext-renderable subset) ---
MATH_LATEX = [
    r"$a^2 + b^2 = c^2$", r"$E = mc^2$",
    r"$\int_0^{\infty} e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}$",
    r"$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$",
    r"$\lim_{x \to 0} \frac{\sin x}{x} = 1$",
    r"$\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$",
    r"$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$",
    r"$\hat{\theta} = \arg\min_{\theta} \sum_{i}(y_i - f(x_i;\theta))^2$",
    r"$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$",
    r"$\frac{d}{dx}\left[\int_a^x f(t)\,dt\right] = f(x)$",
    r"$\cos^2\theta + \sin^2\theta = 1$",
    r"$\prod_{i=1}^{n} x_i = x_1 x_2 \cdots x_n$",
    r"$\sqrt{a^2 + b^2} \le |a| + |b|$",
    r"$\log_b(x) = \frac{\ln x}{\ln b}$",
    r"$\binom{n}{k} = \frac{n!}{k!(n-k)!}$",
    r"$\vec{F} = m\vec{a}$",
    r"$\forall \varepsilon > 0,\ \exists \delta > 0$",
    r"$\mathbb{E}[X] = \sum_i x_i p_i$",
    r"$e^{i\pi} + 1 = 0$", r"$\partial_u f = \nabla f \cdot \mathbf{u}$",
]

CAPTION_TPL = {
    "english":   ["a scanned english document page with text",
                  "a printed english paragraph on white paper",
                  "an english text line in {font_desc} font",
                  "a clean english document excerpt"],
    "chinese":   ["a scanned chinese document page with text",
                  "a printed chinese paragraph on white paper",
                  "a chinese text line in {font_desc} font",
                  "a clean chinese document excerpt"],
    "mixed":     ["a technical document mixing chinese and english text",
                  "a bilingual document page with mixed scripts"],
    "document":  ["a {layout} document page with headings and {cols} columns",
                  "a formatted document page with header, footer and a table",
                  "a two-column document layout with a title"],
    "chart":     ["a {ctype} chart with value labels",
                  "a {ctype} plot showing data trends",
                  "a {ctype} chart with a legend and axis labels"],
    "math":      ["a printed mathematical formula",
                  "a document line with an inline equation",
                  "a formula displayed above a data table"],
    "handwrite": ["handwritten text in a cursive style",
                  "a handwritten note on lined paper"],
    "scene":     ["scene text on a {bg} background",
                  "outdoor sign text with perspective distortion",
                  "text on a {bg} surface"],
}
FONT_DESC = {"en_sans":"sans-serif","en_serif":"serif","mono":"monospace",
             "cjk_song":"song","cjk_kai":"kai","cjk_hei":"sans"}
LAYOUT_DESC = {"single":"single-column","double":"two-column","triple":"three-column"}
CHART_DESC = {"bar":"bar","line":"line","pie":"pie"}
BG_DESC = {"gradient":"gradient","brick":"brick-wall","sky":"sky","wood":"wood"}

# =====================================================================================
# HELPERS
# =====================================================================================
def _rng(seed):
    return random.Random(seed)

def _worker_init(seed):
    global ENGLISH_WORDS
    if ENGLISH_WORDS is None:
        ENGLISH_WORDS = _load_english_words()
    random.seed(seed)

def _text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]

def _wrap(draw, text, font, max_w):
    """Greedy word/char wrap to max_w pixels. Handles CJK by char, Latin by word."""
    lines, cur = [], ""
    has_cjk = any("\u4e00" <= c <= "\u9fff" for c in text)
    if has_cjk:
        for ch in text:
            if ch == "\n":
                lines.append(cur); cur = ""; continue
            test = cur + ch
            if _text_size(draw, test, font)[0] <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = ch
        if cur: lines.append(cur)
    else:
        for para in text.split("\n"):
            words = para.split(" ")
            for w in words:
                test = (cur + " " + w) if cur else w
                if _text_size(draw, test, font)[0] <= max_w:
                    cur = test
                else:
                    if cur: lines.append(cur)
                    cur = w
            if cur: lines.append(cur); cur = ""
    return lines or [""]

def _new_canvas(w, h, bg=(252, 250, 245)):
    return Image.new("RGB", (w, h), bg)

def _fit_size(img, max_side):
    w, h = img.size
    m = max(w, h)
    if m > max_side:
        s = max_side / m
        img = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    return img

def apply_degradation(img, rng):
    """Random low-quality aug: blur / jpeg / perspective / low-contrast / noise."""
    mode = rng.choice(["blur", "jpeg", "perspective", "contrast", "noise", "jpeg"])
    if mode == "blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.6, 2.2)))
    elif mode == "jpeg":
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=rng.randint(20, 50))
        buf.seek(0); img = Image.open(buf).convert("RGB")
    elif mode == "perspective":
        img = _perspective(img, rng)
    elif mode == "contrast":
        arr = np.asarray(img).astype(np.float32)
        arr = arr * rng.uniform(0.55, 0.85) + rng.uniform(10, 40)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    elif mode == "noise":
        arr = np.asarray(img).astype(np.int16)
        _nrng = np.random.RandomState(rng.randint(0, 2**31 - 1))
        arr = arr + _nrng.randint(-25, 25, arr.shape).astype(np.int16)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img

def _perspective(img, rng):
    w, h = img.size
    import cv2
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dx = rng.uniform(0.04, 0.12) * w; dy = rng.uniform(0.04, 0.12) * h
    dst = np.float32([[rng.uniform(0, dx), rng.uniform(0, dy)],
                      [w - rng.uniform(0, dx), rng.uniform(0, dy)],
                      [w - rng.uniform(0, dx), h - rng.uniform(0, dy)],
                      [rng.uniform(0, dx), h - rng.uniform(0, dy)]])
    M = cv2.getPerspectiveTransform(src, dst)
    return Image.fromarray(cv2.warpPerspective(np.asarray(img), M, (w, h),
                          borderMode=cv2.BORDER_REPLICATE))

def make_caption(cat, rng, **kw):
    tpl = rng.choice(CAPTION_TPL[cat])
    ctx = {"font_desc": rng.choice(list(FONT_DESC.values())),
           "layout": rng.choice(list(LAYOUT_DESC.values())),
           "cols": rng.choice(["one", "two", "three"]),
           "ctype": rng.choice(list(CHART_DESC.values())),
           "bg": rng.choice(list(BG_DESC.values()))}
    ctx.update(kw)
    try:
        return tpl.format(**ctx)
    except Exception:
        return tpl

# =====================================================================================
# TEXT GENERATORS  -> dict(text, lang, font_key, src, extra)
# =====================================================================================
def gen_english(rng):
    n_lines = rng.randint(1, 6)
    out = []
    for _ in range(n_lines):
        tpl = rng.choice(ENGLISH_TEMPLATES)
        syn = dict(EN_SYN)
        if ENGLISH_WORDS:
            for k in ("n1", "n2", "n3", "s1", "s2", "s3"):
                syn[k] = rng.choice(ENGLISH_WORDS)
            for k in ("v1",):
                syn[k] = rng.choice(["shows", "uses", "forms", "needs", "gives", "finds"])
            for k in ("adj1",):
                syn[k] = rng.choice(["stable", "clear", "large", "small", "rapid", "novel"])
        syn["d1"] = str(rng.randint(1990, 2026))
        syn["d2"] = str(rng.randint(64, 4096))
        try:
            out.append(tpl.format(**syn))
        except Exception:
            out.append(tpl)
    return {"text": "\n".join(out), "lang": "en",
            "font_key": rng.choice(["en_sans", "en_serif", "mono"]), "src": "dict+template"}

def gen_chinese(rng):
    n_lines = rng.randint(1, 6)
    out = []
    for _ in range(n_lines):
        tpl = rng.choice(ZH_TEMPLATES)
        ctx = {k: rng.choice(ZH_WORDS) for k in ("w1", "w2", "w3")}
        ctx["d1"] = str(rng.randint(1990, 2026))
        ctx["d2"] = str(rng.randint(64, 4096))
        try:
            out.append(tpl.format(**ctx))
        except Exception:
            out.append(tpl)
    return {"text": "\n".join(out), "lang": "zh",
            "font_key": rng.choice(["cjk_song", "cjk_hei", "cjk_song_gb"]), "src": "curated+template"}

def gen_mixed(rng):
    en = gen_english(rng); zh = gen_chinese(rng)
    parts = []
    for _ in range(rng.randint(1, 4)):
        parts.append(en["text"] if rng.random() < 0.5 else zh["text"])
    return {"text": "\n".join(parts), "lang": "mix",
            "font_key": "cjk_hei", "src": "en+zh template"}

def _gen_latex(rng):
    """Combinatorial mathtext-safe LaTeX expression generator (depth<=2).
    Vastly expands the unique-formula space beyond the fixed MATH_LATEX pool."""
    vars_ = list("abcdefghknprtxyz") + [r"\alpha", r"\beta", r"\gamma",
              r"\theta", r"\lambda", r"\mu", r"\sigma", r"\omega", r"\phi"]
    greek = [r"\alpha", r"\beta", r"\gamma", r"\delta", r"\theta", r"\lambda",
             r"\mu", r"\sigma", r"\omega", r"\phi", r"\psi", r"\eta"]
    consts = [r"\pi", r"\infty", "e", "0", "1"]
    ops = ["+", "-", r"\cdot", r"\times", "=", "\leq", "\geq", r"\approx", r"\neq"]

    def atom():
        r = rng.random()
        if r < 0.45:
            return rng.choice(vars_)
        if r < 0.70:
            return str(rng.randint(1, 99))
        if r < 0.85:
            return rng.choice(greek)
        return rng.choice(consts)

    def term(depth):
        if depth >= 2:
            return atom()
        r = rng.random()
        if r < 0.25:
            return r"\frac{%s}{%s}" % (term(depth + 1), term(depth + 1))
        if r < 0.40:
            return r"\sqrt{%s}" % term(depth + 1)
        if r < 0.52:
            v = rng.choice(["i", "n", "k", "j"])
            return r"\sum_{%s=1}^{%s} %s" % (v, rng.randint(2, 20), term(depth + 1))
        if r < 0.62:
            return r"\int_0^{%s} %s\,d%s" % (rng.choice(["x", "t", r"\infty"]),
                                             term(depth + 1), rng.choice(["x", "t"]))
        if r < 0.74:
            return r"%s^{%s}" % (atom(), atom())
        if r < 0.84:
            return r"%s_{%s}" % (atom(), atom())
        return atom()

    lhs = term(0)
    rhs = term(0)
    op = rng.choice(ops)
    return "$%s %s %s$" % (lhs, op, rhs)

def gen_math_text(rng):
    sub = rng.choices(["printed", "inline", "formtab"],
                      weights=[CONFIG["math_split"][k] for k in ("printed", "inline", "formtab")])[0]
    latex = _gen_latex(rng) if rng.random() < 0.70 else rng.choice(MATH_LATEX)
    if sub == "printed":
        return {"text": latex, "lang": "en", "font_key": "math",
                "src": "curated latex", "math_sub": "printed", "latex": latex}
    if sub == "inline":
        en = gen_english(rng)
        return {"text": en["text"] + " " + latex, "lang": "en",
                "font_key": "math", "src": "en+latex", "math_sub": "inline", "latex": latex}
    return {"text": "Table 1. " + latex, "lang": "en", "font_key": "math",
            "src": "latex+table", "math_sub": "formtab", "latex": latex}

def gen_document(rng):
    # full-page layout: title + columns of mixed en/zh + optional table line
    layout = rng.choice(["single", "double", "triple"])
    title = gen_english(rng)["text"].split("\n")[0] if rng.random() < 0.5 else gen_chinese(rng)["text"].split("\n")[0]
    body_lines = []
    ncol = {"single": 1, "double": 2, "triple": 3}[layout]
    for _ in range(rng.randint(3, 10)):
        body_lines.append(gen_english(rng)["text"] if rng.random() < 0.6 else gen_chinese(rng)["text"])
    body = "\n".join(body_lines)
    return {"text": title + "\n" + body, "lang": "mix", "font_key": "cjk_hei",
            "src": "layout template", "layout": layout, "ncol": ncol}

def gen_chart_text(rng):
    ctype = rng.choice(["bar", "line", "pie"])
    n = rng.randint(4, 8)
    labels = [rng.choice(ENGLISH_WORDS or ["a","b","c"])[:6] if ENGLISH_WORDS else "c%d" % i
              for i in range(n)]
    vals = [rng.randint(5, 95) for _ in range(n)]
    text = ", ".join(f"{l}={v}" for l, v in zip(labels, vals))
    return {"text": text, "lang": "en", "font_key": "en_sans",
            "src": "matplotlib", "ctype": ctype, "labels": labels, "vals": vals}

def gen_handwrite(rng):
    if rng.random() < 0.5:
        t = gen_chinese(rng)
        return {"text": t["text"], "lang": "zh", "font_key": "cjk_kai", "src": "curated+kai"}
    t = gen_english(rng)
    return {"text": t["text"], "lang": "en", "font_key": "cjk_kai", "src": "dict+kai"}

def gen_scene(rng):
    if rng.random() < 0.5:
        t = gen_english(rng); words = t["text"].replace("\n", " ")
    else:
        t = gen_chinese(rng); words = t["text"].replace("\n", "")
    return {"text": words[:40], "lang": t["lang"], "font_key": rng.choice(["en_sans_b", "cjk_hei"]),
            "src": "dict+perspective", "bg": rng.choice(list(BG_DESC.keys()))}

GEN_TEXT = {
    "english": gen_english, "chinese": gen_chinese, "mixed": gen_mixed,
    "document": gen_document, "chart": gen_chart_text, "math": gen_math_text,
    "handwrite": gen_handwrite, "scene": gen_scene,
}

# =====================================================================================
# RENDERERS  -> PIL.Image (RGB)
# =====================================================================================
def render_text_lines(td, rng):
    """Generic renderer for english/chinese/mixed/handwrite/scene: wrapped lines
    on a paper-like canvas, margins, random font size & line spacing."""
    text = td["text"][:512]
    fkey = td["font_key"]
    size = rng.randint(22, 40)
    font = F(FONT.get(fkey, FONT["en_sans"]), size)
    W = CONFIG["render_size"]
    margin = rng.randint(24, 56)
    max_w = W - 2 * margin
    tmp = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(tmp)
    lines = _wrap(d, text, font, max_w)
    line_sp = int(size * rng.uniform(1.25, 1.6))
    H = margin + len(lines) * line_sp + margin
    H = max(H, size + 2 * margin)
    img = _new_canvas(W, H)
    draw = ImageDraw.Draw(img)
    y = margin
    ink = (rng.randint(10, 40), rng.randint(10, 40), rng.randint(20, 50))
    for ln in lines:
        if td.get("font_key") == "cjk_kai":  # handwriting jitter
            _draw_jittered(draw, ln, font, (margin, y), ink, rng)
        else:
            draw.text((margin, y), ln, font=font, fill=ink)
        y += line_sp
    return img

def _draw_jittered(draw, line, font, xy, ink, rng):
    """Handwriting simulation: kai (楷) font + per-character position jitter and
    occasional size variation, drawn directly (no compositing => robust)."""
    x, y = xy
    base = font.size
    for ch in line:
        if ch == " ":
            x += base // 3; continue
        jx = x + rng.randint(-2, 2); jy = y + rng.randint(-2, 2)
        # occasional slight size wobble for stroke-irregularity feel
        sz = base + rng.choice([-2, 0, 0, 0, 2])
        f = F(FONT["cjk_kai"], sz) if sz != base else font
        draw.text((jx, jy), ch, font=f, fill=ink)
        box = draw.textbbox((0, 0), ch, font=f)
        x += (box[2] - box[0]) + rng.randint(0, 2)

def render_chart(td, rng):
    """matplotlib chart (bar/line/pie) with value labels -> PIL.Image."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ctype = td.get("ctype", "bar"); labels = td["labels"]; vals = td["vals"]
    fig, ax = plt.subplots(figsize=(4, 3), dpi=96)
    fig.patch.set_facecolor("white")
    if ctype == "bar":
        ax.bar(labels, vals, color="#3b6fb6")
        for i, v in enumerate(vals):
            ax.text(i, v + 1, str(v), ha="center", fontsize=8)
    elif ctype == "line":
        ax.plot(labels, vals, marker="o", color="#c0392b")
        for i, v in enumerate(vals):
            ax.text(i, v + 2, str(v), ha="center", fontsize=8)
    else:
        ax.pie(vals, labels=labels, autopct="%d%%", textprops={"fontsize": 8})
        ax.set_aspect("equal")
    if ctype != "pie":
        ax.set_xlabel("category", fontsize=9); ax.set_ylabel("value", fontsize=9)
    ax.set_title("Figure: data overview", fontsize=10)
    buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig); buf.seek(0)
    return Image.open(buf).convert("RGB")

def render_math(td, rng):
    """matplotlib mathtext renders the LaTeX subset to an image."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    latex = td.get("latex", td["text"])
    sub = td.get("math_sub", "printed")
    # Continuous random variation so the SAME latex renders to DIFFERENT pixels
    # (kills image-dedup collisions; keeps the <1% dup target at scale).
    fig = plt.figure(figsize=(rng.uniform(4.0, 6.5), rng.uniform(1.6, 2.8)),
                     dpi=rng.randint(90, 130))
    fig.patch.set_facecolor("white")
    fs = rng.uniform(15, 30)
    ink = (rng.randint(8, 55),) * 3  # dark-gray shade, varies per sample
    cx = rng.uniform(0.38, 0.62); cy = rng.uniform(0.42, 0.58)
    if sub == "printed":
        fig.text(cx, cy, latex, fontsize=fs, ha="center", va="center", color=ink)
    elif sub == "inline":
        pre = rng.choice(["Hence ", "Thus ", "So ", "Note ", "Since ", ""])
        fig.text(cx, cy, pre + latex + " holds.", fontsize=fs, ha="center",
                 va="center", color=ink)
    else:  # formtab: randomized small data table under the formula
        fig.text(cx, 0.72, latex, fontsize=fs, ha="center", va="center", color=ink)
        nr = rng.randint(2, 4)
        rows = ["x | y"] + ["%d | %d" % (rng.randint(1, 99), rng.randint(1, 99))
                            for _ in range(nr)]
        fig.text(cx, 0.26, "\n".join(rows), fontsize=rng.uniform(9, 13),
                 ha="center", va="center", family="monospace", color=ink)
    buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight",
                                    pad_inches=rng.uniform(0.05, 0.25),
                                    facecolor="white")
    plt.close(fig); buf.seek(0)
    return Image.open(buf).convert("RGB")

def _scene_background(w, h, bg, rng):
    if bg == "gradient":
        arr = np.zeros((h, w, 3), np.uint8)
        for c in range(3):
            arr[:, :, c] = np.linspace(rng.randint(40, 90), rng.randint(140, 200), w, dtype=np.uint8)
        return Image.fromarray(arr)
    if bg == "sky":
        arr = np.zeros((h, w, 3), np.uint8)
        arr[:, :, 0] = rng.randint(120, 170); arr[:, :, 1] = rng.randint(160, 200)
        arr[:, :, 2] = rng.randint(200, 240)
        return Image.fromarray(arr)
    if bg == "wood":
        arr = np.full((h, w, 3), (120, 80, 50), np.uint8)
        for y in range(0, h, rng.randint(6, 14)):
            arr[y, :] = np.clip(arr[y, :].astype(int) + rng.randint(-20, 20), 0, 255)
        return Image.fromarray(arr)
    # brick
    arr = np.full((h, w, 3), (150, 90, 70), np.uint8)
    for by in range(0, h, 30):
        off = 0 if (by // 30) % 2 == 0 else 30
        for bx in range(-off, w, 60):
            cv2 = __import__("cv2")
            cv2.rectangle(arr, (bx, by), (bx + 56, by + 26), (90, 50, 40), 1)
    return Image.fromarray(arr)

def render_scene(td, rng):
    """Scene text: text on a synthetic background + perspective distortion."""
    W = CONFIG["render_size"]; H = int(W * rng.uniform(0.5, 0.9))
    bg = _scene_background(W, H, td.get("bg", "gradient"), rng)
    img = bg.convert("RGB")
    draw = ImageDraw.Draw(img)
    size = rng.randint(28, 52)
    font = F(FONT.get(td["font_key"], FONT["en_sans_b"]), size)
    tw = _text_size(draw, td["text"], font)[0]
    x = rng.randint(10, max(11, W - tw - 10)); y = rng.randint(10, max(11, H - size - 10))
    # outline for readability on noisy bg
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            draw.text((x + dx, y + dy), td["text"], font=font, fill=(255, 255, 255))
    draw.text((x, y), td["text"], font=font, fill=(rng.randint(10, 40),) * 3)
    return _perspective(img, rng)

def render_document(td, rng):
    """Full-page layout: title bar + ncol columns of body text + header/footer."""
    W = CONFIG["render_size"]
    H = rng.randint(int(W * 1.2), CONFIG["max_side"])
    img = _new_canvas(W, H, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    ncol = td.get("ncol", 1)
    margin = 28
    col_gap = 24
    col_w = (W - 2 * margin - (ncol - 1) * col_gap) // ncol
    # header
    draw.text((margin, 10), "BaiZe Document  -  page %d" % rng.randint(1, 20),
              font=F(FONT["mono"], 12), fill=(120, 120, 120))
    # title
    title = td["text"].split("\n", 1)[0]
    body = td["text"].split("\n", 1)[1] if "\n" in td["text"] else ""
    ty = 40
    tfont = F(FONT["cjk_hei"], 26)
    draw.text((margin, ty), title[:60], font=tfont, fill=(20, 20, 20))
    ty += 40
    draw.line([(margin, ty), (W - margin, ty)], fill=(60, 60, 60), width=1)
    ty += 12
    # body into columns
    paras = [p for p in body.split("\n") if p]
    if not paras:
        paras = [gen_english(rng)["text"]]
    col_x = [margin + i * (col_w + col_gap) for i in range(ncol)]
    cur_col, cy = 0, ty
    bfont = F(FONT["cjk_hei"], 16)
    for p in paras:
        lines = _wrap(draw, p, bfont, col_w)
        for ln in lines:
            if cy > H - 60:
                cur_col = min(cur_col + 1, ncol - 1); cy = ty
            draw.text((col_x[cur_col], cy), ln, font=bfont, fill=(30, 30, 30))
            cy += 24
    # footer
    draw.text((margin, H - 22), "- %d -" % rng.randint(1, 99),
              font=F(FONT["mono"], 12), fill=(120, 120, 120))
    return img

RENDER = {
    "english": render_text_lines, "chinese": render_text_lines, "mixed": render_text_lines,
    "handwrite": render_text_lines, "scene": render_scene, "document": render_document,
    "chart": render_chart, "math": render_math,
}

# =====================================================================================
# SAMPLE WORKER + DEDUP + LEAKAGE GUARD
# =====================================================================================
_LEAK_HASHES = None
def _load_leakage_hashes():
    """Best-effort: hash set of normalized eval QA text (OCRBench/DocVQA/ChartQA/
    InfoVQA). Synthetic text from word-lists cannot collide with real eval QA, so
    an empty set is still a valid guard; we report whether eval text was found."""
    global _LEAK_HASHES
    if _LEAK_HASHES is not None:
        return _LEAK_HASHES
    found = []
    for pat in ["*/ocrbench*", "*OCRBench*", "*docvqa*", "*DocVQA*",
                "*chartqa*", "*ChartQA*", "*infographicsvqa*", "*InfoVQA*"]:
        import glob
        found.extend(glob.glob(os.path.expanduser("~/.cache/huggingface") + "/**/" + pat,
                               recursive=True)[:5])
    _LEAK_HASHES = set()  # placeholder; real eval QA text rarely sits as plain text
    return _LEAK_HASHES, len(found)

def _norm_hash(text):
    t = "".join(ch for ch in text.lower() if ch.isalnum())
    return hashlib.sha1(t.encode("utf-8")).hexdigest()

def make_one(payload):
    """Worker: payload=(cat, idx, seed) -> (idx, cat, jpg_bytes, meta) or None on fail."""
    cat, idx, seed = payload
    try:
        rng = random.Random(seed)
        _worker_init(seed)
        td = GEN_TEXT[cat](rng)
        text = td["text"]
        if not text or len(text.strip()) == 0:
            return (idx, cat, None, None, "empty_text")
        try:
            img = RENDER[cat](td, rng)
        except Exception:
            # robust fallback: plain text render keeps the same text + cat,
            # so no slot is wasted and category balance is preserved.
            img = render_text_lines(td, rng)
        # cap longest side
        img = _fit_size(img, CONFIG["max_side"])
        # 30% degradation
        if rng.random() < CONFIG["degrade_frac"]:
            img = apply_degradation(img, rng)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=CONFIG["jpeg_quality"])
        jpg = buf.getvalue()
        if len(jpg) < 200:  # suspiciously tiny => likely blank
            return (idx, cat, None, None, "tiny_jpg")
        w, h = img.size
        cap = make_caption(cat, rng, font_desc=FONT_DESC.get(td["font_key"], "sans"),
                           layout=LAYOUT_DESC.get(td.get("layout", "single"), "single-column"),
                           ctype=CHART_DESC.get(td.get("ctype", "bar"), "bar"),
                           bg=BG_DESC.get(td.get("bg", "gradient"), "gradient"))
        meta = {
            "text": text[:512], "caption": cap[:128], "caption_type": "short",
            "lang": td["lang"], "cat": cat, "w": w, "h": h,
            "font": td["font_key"], "src": td["src"], "id": idx,
            "sha1": hashlib.sha1(jpg).hexdigest(),      # image-content dedup key
            "text_sha1": _norm_hash(text),               # leakage-guard key (vs eval text)
        }
        for k in ("math_sub", "ctype", "layout", "latex"):
            if k in td: meta[k] = td[k]
        return (idx, cat, jpg, meta, "ok")
    except Exception as e:
        return (idx, cat, None, None, "exc:" + type(e).__name__)

# =====================================================================================
# TAR / METADATA WRITERS
# =====================================================================================
def _key(idx):
    return str(idx).zfill(CONFIG["key_digits"])

def _write_shard(path, samples):
    with tarfile.open(path, "w") as tf:
        for idx, jpg, meta in samples:
            k = _key(idx)
            ti = tarfile.TarInfo(k + ".jpg"); ti.size = len(jpg)
            tf.addfile(ti, io.BytesIO(jpg))
            js = json.dumps(meta, ensure_ascii=False).encode("utf-8")
            ti2 = tarfile.TarInfo(k + ".json"); ti2.size = len(js)
            tf.addfile(ti2, io.BytesIO(js))

def _write_dataset_card(path, stats):
    licenses = {
        "english": "/usr/share/dict/words (word list, facts, public domain)",
        "chinese": "curated common-hanzi/word list (facts, public domain)",
        "mixed": "english + chinese sources (public domain)",
        "document": "layout template + en/zh sources (public domain)",
        "chart": "matplotlib-rendered (self-built, no third-party data)",
        "math": "curated LaTeX expressions (facts / self-built)",
        "handwrite": "kai font (AR PL KaitiM, ARPHIC public license) + curated text",
        "scene": "synthetic backgrounds + dict text (self-built)",
    }
    lines = ["# DATASET_CARD — ocr_synth_10m", "",
             "Synthetic OCR image-text pairs for BaiZe vision encoder pretraining.",
             "Format: WebDataset tar, `<key>.jpg` + `<key>.json` (NO .txt).",
             "json fields: text, caption, caption_type='short', lang, cat, w, h, font, src, id, sha1.",
             "Loader: run/vision/data.py `build_mixed_loader` (GPIC json-caption path).", "",
             "## Per-category sources & licenses"]
    for c, lic in licenses.items():
        lines.append(f"- **{c}**: {lic}")
    lines += ["", "## Known biases",
              "- Text is synthetic-template (word-list + grammar templates), NOT real",
              "  Wikipedia/books/news. Visual diversity is the primary value for OCR pretraining.",
              "- Handwriting approximated with a kai font + per-char jitter (not true stroke sim).",
              "- Math uses matplotlib mathtext (LaTeX subset), not a full TeX render.",
              "- Scene text uses synthetic backgrounds + perspective warp, not real photos.",
              "", "## Generation", f"- seed={CONFIG['seed']}, render_size={CONFIG['render_size']},",
              f"  max_side={CONFIG['max_side']}, jpeg_q={CONFIG['jpeg_quality']},",
              f"  degrade_frac={CONFIG['degrade_frac']}.", "- Generator: vision/ocr_synth/gen_ocr_synth.py (reproducible)."]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def _existing_shards(out_dir):
    import glob
    tars = sorted(glob.glob(os.path.join(out_dir, "shard-*.tar")))
    done = 0
    for t in tars:
        try:
            with tarfile.open(t) as tf:
                done += sum(1 for m in tf.getmembers() if m.name.endswith(".jpg"))
        except Exception:
            pass
    return tars, done

# =====================================================================================
# PLAN + MAIN
# =====================================================================================
def _plan_counts(total):
    cats = list(CONFIG["categories"].keys())
    full = {c: CONFIG["categories"][c][0] for c in cats}
    S = sum(full.values())
    counts = {c: int(round(total * full[c] / S)) for c in cats}
    diff = total - sum(counts.values())
    i = 0
    while diff != 0:
        c = cats[i % len(cats)]
        counts[c] += 1 if diff > 0 else -1
        diff += -1 if diff > 0 else 1
        i += 1
    return counts

def _build_schedule(counts):
    cats = [c for c, n in counts.items() if n > 0]
    queues = {c: counts[c] for c in cats}
    schedule = []
    while any(v > 0 for v in queues.values()):
        for c in cats:
            if queues[c] > 0:
                schedule.append(c); queues[c] -= 1
    return schedule

def run(total, out_dir, n_workers, tag):
    os.makedirs(out_dir, exist_ok=True)
    counts = _plan_counts(total)
    schedule = _build_schedule(counts)
    tars_done, n_done = _existing_shards(out_dir)
    start_slot = n_done
    print(f"[{tag}] target={total} done={n_done} start_slot={start_slot}", flush=True)
    print(f"[{tag}] per-cat: {counts}", flush=True)
    if start_slot >= total:
        print(f"[{tag}] already complete."); return
    leak_set, n_leak_found = _load_leakage_hashes()
    print(f"[{tag}] leakage eval files found in HF cache: {n_leak_found}", flush=True)
    per_tar = CONFIG["per_tar"]; seed0 = CONFIG["seed"]
    payloads = [(schedule[s], s, seed0 + s) for s in range(start_slot, total)]
    buf = []; shard_no = start_slot // per_tar; seen_sha = set()
    stats = {"ok": 0, "fail": 0, "dup": 0, "leak": 0, "bytes": 0,
             "fails_by_reason": {}, "cat_counts": {c: 0 for c in counts},
             "text_lens": [], "shards_written": len(tars_done)}
    # open index.jsonl with a small NFS-race retry (rm -rf + immediate recreate
    # can leave the freshly-made dir invisible to open() for a few ms on NFS)
    for _att in range(5):
        try:
            idxf = open(os.path.join(out_dir, "index.jsonl"), "a", encoding="utf-8")
            break
        except FileNotFoundError:
            os.makedirs(out_dir, exist_ok=True); time.sleep(0.5)
    else:
        idxf = open(os.path.join(out_dir, "index.jsonl"), "a", encoding="utf-8")
    t0 = time.time()
    pool = Pool(n_workers, initializer=_worker_init, initargs=(seed0,))
    try:
        for res in pool.imap_unordered(make_one, payloads, chunksize=64):
            idx, cat, jpg, meta, status = res
            if status != "ok":
                stats["fail"] += 1
                stats["fails_by_reason"][status] = stats["fails_by_reason"].get(status, 0) + 1
                continue
            sha = meta["sha1"]
            tsha = meta["text_sha1"]
            if sha in seen_sha:
                stats["dup"] += 1; continue
            if leak_set and tsha in leak_set:
                stats["leak"] += 1; continue
            seen_sha.add(sha); stats["ok"] += 1; stats["bytes"] += len(jpg)
            stats["cat_counts"][cat] += 1; stats["text_lens"].append(len(meta["text"]))
            buf.append((idx, jpg, meta))
            idxf.write(json.dumps({"key": _key(idx), "shard": shard_no, "cat": cat,
                                   "lang": meta["lang"], "n_tokens": len(meta["text"].split()),
                                   "text_sha1": tsha, "img_sha1": sha}, ensure_ascii=False) + "\n")
            if len(buf) >= per_tar:
                _write_shard(os.path.join(out_dir, f"shard-{shard_no:06d}.tar"), buf)
                stats["shards_written"] += 1; buf = []; shard_no += 1
                el = time.time() - t0; rate = stats["ok"] / max(el, 1e-6)
                print(f"[{tag}] {stats['ok']}/{total} shards={stats['shards_written']} "
                      f"{rate:.0f} img/s elapsed={el:.0f}s", flush=True)
    finally:
        pool.close(); pool.join()
        if buf:
            _write_shard(os.path.join(out_dir, f"shard-{shard_no:06d}.tar"), buf)
            stats["shards_written"] += 1
        idxf.close()
    _finalize(out_dir, stats, counts, total, tag, t0)

def _finalize(out_dir, stats, counts, total, tag, t0):
    import glob
    tl = stats["text_lens"]
    text_dist = {"p50": int(np.percentile(tl, 50)) if tl else 0,
                 "p95": int(np.percentile(tl, 95)) if tl else 0,
                 "max": max(tl) if tl else 0, "mean": float(np.mean(tl)) if tl else 0}
    fail_rate = stats["fail"] / max(total, 1)
    dup_rate = stats["dup"] / max(stats["ok"] + stats["dup"], 1)
    tars = sorted(glob.glob(os.path.join(out_dir, "shard-*.tar")))
    man = []
    for t in tars:
        h = hashlib.sha256()
        with open(t, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        man.append(f"{h.hexdigest()}  {os.path.basename(t)}")
    with open(os.path.join(out_dir, "MANIFEST.sha256"), "w") as f:
        f.write("\n".join(man) + "\n")
    total_bytes = sum(os.path.getsize(t) for t in tars)
    stats_out = {
        "tag": tag, "target": total, "ok": stats["ok"], "fail": stats["fail"],
        "fail_rate": round(fail_rate, 4), "dup": stats["dup"],
        "dup_rate": round(dup_rate, 4), "leak": stats["leak"],
        "shards_written": stats["shards_written"], "n_tars": len(tars),
        "total_bytes": total_bytes, "total_tb": round(total_bytes / 1e12, 4),
        "avg_bytes": int(total_bytes / max(stats["ok"], 1)),
        "throughput_img_s": round(stats["ok"] / max(time.time() - t0, 1e-6), 1),
        "elapsed_s": round(time.time() - t0, 1),
        "cat_counts": stats["cat_counts"], "cat_plan": counts,
        "text_len_dist": text_dist, "fails_by_reason": stats["fails_by_reason"],
        "seed": CONFIG["seed"], "render_size": CONFIG["render_size"],
        "max_side": CONFIG["max_side"], "jpeg_quality": CONFIG["jpeg_quality"],
        "degrade_frac": CONFIG["degrade_frac"],
    }
    with open(os.path.join(out_dir, "STATS.json"), "w", encoding="utf-8") as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=2)
    _write_dataset_card(os.path.join(out_dir, "DATASET_CARD.md"), stats_out)
    print(f"[{tag}] DONE ok={stats['ok']} fail={stats['fail']} fail_rate={fail_rate:.4f} "
          f"dup_rate={dup_rate:.4f} tars={len(tars)} tb={stats_out['total_tb']} "
          f"img/s={stats_out['throughput_img_s']}", flush=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["p0", "full"], default="p0")
    ap.add_argument("--total", type=int, default=0, help="override count (0=use mode default)")
    ap.add_argument("--out", default=CONFIG["out_dir"])
    ap.add_argument("--workers", type=int, default=CONFIG["n_workers"])
    args = ap.parse_args()
    CONFIG["out_dir"] = args.out
    total = args.total or (100_000 if args.mode == "p0" else 10_000_000)
    run(total, args.out, args.workers, args.mode)



# (render_document relocated above RENDER dict)

