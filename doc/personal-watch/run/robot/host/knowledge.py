#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robot 线 · 知识点自动分类（L3 学情「正样本」收尾）。

ROADMAP「下一轮候选 #5」：App「答对/答错」知识点自动分类（LLM）。
此前 `POST /practice` 在 App 不带 `knowledge` 时一律记成「未分类」，
导致练习日志（正样本）进不了知识点画像。本模块补上这条链路：

  主路径 = 云端 DeepSeek（文本上行，token 极便宜，复用 `tutor_agent.chat()`）；
  离线兜底 = 确定性关键词匹配（`classify_knowledge_local`，纯函数、无网络）。

红线（11:10 令）：只返回**知识点名**，不返回答案、不代写、不瞎猜——
判不出就返回「未分类」，🚫 绝不静默也不编造。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import tutor_agent  # noqa: E402  复用 chat()：DeepSeek -> ollama 兜底（同一云端链路）

# 分类后端开关：deepseek（默认，LLM 分类）| local（纯本地关键词，离线/隐私模式）
KNOWLEDGE_BACKEND = os.environ.get("ROBOT_KNOWLEDGE_BACKEND", "deepseek").strip().lower()

# 允许的知识点标签 = 100 题题库抽出的 61 类（LLM 输出超出此表时按包含关系归一，
# 归不到且不像是术语的才落「未分类」）。
KNOWN_KNOWLEDGE = {
    "一元一次方程", "二元一次方程组", "一次函数求值", "一次函数求解析式", "一次函数图像",
    "整式加减", "因式分解", "整式乘法", "分式化简", "分式运算",
    "二次根式", "实数运算", "平方根",
    "全等三角形", "三角形内角和", "三角形外角", "等腰三角形", "轴对称", "勾股定理",
    "平行四边形", "平均数", "中位数", "众数", "方差",
    "匀速直线运动", "平均速度", "声速测距", "相对速度", "声速", "回声测距",
    "熔点", "沸点", "光的反射", "平面镜成像", "密度", "重力", "摩擦力",
    "压强", "液体压强", "阿基米德原理", "浮力",
    "一般现在时", "现在进行时", "比较级", "最高级", "一般过去时", "一般将来时",
    "现在完成时", "名词复数", "冠词", "介词", "动词不定式", "动名词",
    "情态动词", "反身代词", "物主代词", "形容词辨析", "主谓一致", "数量词",
    "情景交际", "介词辨析",
}

UNCLASSIFIED = "未分类"

# ── 确定性关键词规则表 ──────────────────────────────────────────────
# 每条 = (mode, keywords, knowledge)；mode: "any"=任一命中 / "all"=全部命中。
# 按「先具体、后宽泛」排序：方程组先于解方程、液体压强先于压强、摩擦先于匀速…
_RULES = [
    # ── 物理（先具体）──────────────────────────────
    ("any", ("液体压强", "ρgh"), "液体压强"),
    ("any", ("阿基米德", "排开"), "阿基米德原理"),
    ("any", ("浮力",), "浮力"),
    ("any", ("回声",), "回声测距"),
    ("all", ("声音", "距离"), "声速测距"),
    ("any", ("传播速度约为",), "声速"),
    ("any", ("相对", "同向", "相向"), "相对速度"),
    ("any", ("平均速度",), "平均速度"),
    ("any", ("摩擦",), "摩擦力"),
    ("any", ("匀速直线运动",), "匀速直线运动"),
    ("any", ("熔点", "熔化"), "熔点"),
    ("any", ("沸点", "沸腾"), "沸点"),
    ("any", ("反射", "入射"), "光的反射"),
    ("any", ("平面镜",), "平面镜成像"),
    ("any", ("密度",), "密度"),
    ("any", ("重力", "g 取"), "重力"),
    ("any", ("压强",), "压强"),
    # ── 英语（先于数学：英语选项里的 "/" 不能当成分式除号）──
    ("any", ("since 或 for",), "介词辨析"),
    ("any", ("a 或 an", "honest boy"), "冠词"),
    ("any", ("in / on / at",), "介词"),
    ("any", ("many 或 much",), "数量词"),
    ("any", ("is 或 are",), "主谓一致"),
    ("any", ("interested", "interesting"), "形容词辨析"),
    ("any", ("Would / Do", "some tea", "Would you like"), "情景交际"),
    ("any", ("himself", "herself", "itself", "反身代词"), "反身代词"),
    ("any", ("物主代词", "I) book"), "物主代词"),
    ("any", ("to be", "wants"), "动词不定式"),
    ("any", ("enjoys", "动名词"), "动名词"),
    ("any", ("must", "can"), "情态动词"),
    ("any", ("in our class", "最高级"), "最高级"),
    ("any", ("than", "比较级"), "比较级"),
    ("any", ("twice", "already", "yet"), "现在完成时"),
    ("any", ("yesterday", "ago", "last"), "一般过去时"),
    ("any", ("tomorrow", "next"), "一般将来时"),
    ("any", ("now", "Look", "Listen"), "现在进行时"),
    ("any", ("every day", "every morning", "often", "usually"), "一般现在时"),
    ("any", ("child", "名词复数"), "名词复数"),
    # ── 数学 ──────────────────────────────────────
    ("any", ("方程组",), "二元一次方程组"),
    ("any", ("解方程", "一元一次方程"), "一元一次方程"),
    ("any", ("因式分解", "分解因式"), "因式分解"),
    ("any", ("|-", "实数", "无理数"), "实数运算"),
    ("any", ("平方根", "算术平方根"), "平方根"),
    ("any", ("√", "根号", "二次根式"), "二次根式"),
    ("all", ("/", "计算"), "分式运算"),
    ("any", ("通分",), "分式运算"),
    ("any", ("/", "约分", "分式"), "分式化简"),
    ("any", ("解析式", "求 k"), "一次函数求解析式"),
    ("any", ("交点", "图像", "与 y 轴", "与 x 轴"), "一次函数图像"),
    ("any", ("一次函数",), "一次函数求值"),
    ("any", ("平行四边形",), "平行四边形"),
    ("any", ("勾股", "直角三角形", "直角边", "斜边"), "勾股定理"),
    ("any", ("全等", "≌"), "全等三角形"),
    ("any", ("等腰", "顶角", "底角"), "等腰三角形"),
    ("any", ("轴对称", "对称轴", "垂直平分"), "轴对称"),
    ("any", ("外角",), "三角形外角"),
    ("any", ("内角和", "求∠C"), "三角形内角和"),
    ("any", (")(x", ")(2", ")(a", ")(3", ")²"), "整式乘法"),
    ("any", ("整式加减", "合并同类项"), "整式加减"),
    ("any", ("方差",), "方差"),
    ("any", ("众数",), "众数"),
    ("any", ("中位数",), "中位数"),
    ("any", ("平均数",), "平均数"),
    ("any", ("化简",), "整式加减"),
]


def classify_knowledge_local(question: str) -> str:
    """确定性关键词分类（纯函数、无网络）。匹配不到返回「未分类」。"""
    q = (question or "").strip()
    if not q:
        return UNCLASSIFIED
    ql = q.lower()
    for mode, kws, knowledge in _RULES:
        if mode == "any":
            hit = any(k.lower() in ql for k in kws)
        else:
            hit = all(k.lower() in ql for k in kws)
        if hit:
            return knowledge
    return UNCLASSIFIED


def _normalize(raw: str) -> str:
    """把 LLM 输出归一成规范知识点名；判不出/不像术语 → 「未分类」。

    只认 61 类已知标签（覆盖 8 年级人教版课标 + 100 题题库）；归不到的
    （含「数学/物理」这类学科名、或 LLM 的整句废话）一律「未分类」——🚫 不瞎猜。
    """
    s = (raw or "").strip()
    s = re.sub(r"^[（(\[{【\s]+|[）)}\]}】\s，,。；;：:。!！?？]+$", "", s).strip()
    if not s or s == UNCLASSIFIED:
        return UNCLASSIFIED
    if s in KNOWN_KNOWLEDGE:
        return s
    # LLM 可能带解释（如「一元一次方程（解方程）」）：取被包含的已知标签
    for k in KNOWN_KNOWLEDGE:
        if k in s:
            return k
    return UNCLASSIFIED


_CLASSIFY_SYSTEM = (
    "你是初中家教助教，负责把一道题目归类到「知识点」。"
    "只输出一个知识点名称（2~8 个汉字或规范术语），不要解释、不要标点、"
    "不要输出答案或解题过程。知识点要具体（如「一元一次方程」「因式分解」"
    "「勾股定理」「一般过去时」），不要泛化（不要只写「数学」「物理」）。"
    "判断不出就只输出「未分类」。"
)


def classify_knowledge(question: str, backend: str = None):
    """LLM 分类 + 本地关键词兜底。返回 (知识点, trace)。

    trace = {backend, kind, fallback, latency_s}；`fallback` 非空 = 走了降级
    （🚫 不许静默降级，调用方能看到，口径同 tutor_agent.recognize_ex）。
    """
    q = (question or "").strip()
    if not q:
        return UNCLASSIFIED, {"backend": "none", "kind": "empty", "fallback": None}

    backend = (backend or KNOWLEDGE_BACKEND).strip().lower()
    trace = {}
    if backend in ("deepseek", "ollama"):
        import time
        t0 = time.time()
        try:
            raw = tutor_agent.chat(
                [{"role": "system", "content": _CLASSIFY_SYSTEM},
                 {"role": "user", "content": q}],
                backend=backend,
            )
            label = _normalize(raw)
            trace = dict(tutor_agent.LAST_TUTOR_TRACE)
            trace["kind"] = "llm"
            trace["raw"] = raw[:40]
            if label != UNCLASSIFIED:
                trace["fallback"] = None
                return label, trace
            trace["fallback"] = "LLM 判不出（%s）-> 本地关键词" % raw[:30]
        except Exception as e:  # noqa: BLE001  网络失败 / 无 key / ollama 未启动
            import time as _t
            trace = {"backend": "llm-error", "kind": "llm",
                     "fallback": "LLM 不可用：%s" % str(e)[:120],
                     "latency_s": round(_t.time() - t0, 2)}
    else:
        trace = {"backend": "local", "kind": "local",
                 "fallback": "显式指定 ROBOT_KNOWLEDGE_BACKEND=local（纯本地模式）"}

    label = classify_knowledge_local(q)
    trace = dict(trace)
    trace.setdefault("kind", "local")
    trace.setdefault("backend", "local")
    trace.setdefault("latency_s", 0.0)
    return label, trace


if __name__ == "__main__":
    samples = [
        "解方程：2x + 3 = 11",
        "解方程组：x + y = 10，x - y = 4",
        "因式分解：x² - 9",
        "已知等腰三角形顶角为 40°，求底角的度数。",
        "物体以 5 m/s 做匀速直线运动，求 10 s 内通过的路程",
        "用所给词的适当形式填空：She ___ (go) to school every day.",
        "用所给词的适当形式填空：He ___ (watch) TV now.",
        "声速 340 m/s，发出的声音经 0.2 s 返回（回声），求障碍物到声源的距离",
        "完全看不出这是一道什么题 abc",
    ]
    for s in samples:
        local = classify_knowledge_local(s)
        print("%-46s -> 本地=%-8s" % (s, local))
    print("\n[LLM 分类（默认 deepseek，可能走网络）]")
    for s in samples[:2]:
        label, trace = classify_knowledge(s)
        print("%-30s -> %s (trace=%s)" % (s, label, trace))
