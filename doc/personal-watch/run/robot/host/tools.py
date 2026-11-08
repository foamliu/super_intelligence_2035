#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robot 线 · L2 智能体工具集（5 个工具：计算器 / 题库 / 错题本 / 家长报告 / 函数绘图）。

这是「调用大模型 / 智能体辅导」里的**工具层**（ROADMAP L2 判据：5 工具可调）。
设计原则：
- 工具 = 确定性纯函数 + 显式异常（`ToolError`），🚫 不做静默降级；
- 计算器走 **AST 白名单**（🚫 不用 `eval`），只认数字/运算符/白名单函数，
  拒绝变量（x/y 等）→ 从根上杜绝「代解方程/代写作业」；
- 题库检索只回题干 + 知识点，**剥离 answer/leak** → 不泄原题答案；
- 错题本 / 家长报告只落本地（默认 `run/robot/logs/`，路径可配），不上传。

教育红线（11:10 令，违反即作废）：
  ① 不代写、只分步引导、最终答案默认不给；② 未成年保护（本地处理，不上传第三方）。
"""
import ast
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(HERE)                 # run/robot/
EVAL_DIR = os.path.join(ROBOT_DIR, "eval")
LOGS_DIR = os.path.join(ROBOT_DIR, "logs")
WRONG_BOOK_PATH = os.environ.get("ROBOT_WRONG_BOOK",
                                 os.path.join(LOGS_DIR, "wrong_book.json"))


class ToolError(ValueError):
    """工具调用失败 / 参数非法 / 触碰红线。上层据此给用户一句可读的说明。"""


# ══════════════════════════════════════════════════════════════════════════
# 安全表达式求值（calculator / plot_function 共用）
# ══════════════════════════════════════════════════════════════════════════

_CONSTANTS = {"pi": math.pi, "e": math.e}
_FUNCTIONS = {
    "sqrt": math.sqrt, "abs": abs, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log10": math.log10, "exp": math.exp,
    "round": round, "floor": math.floor, "ceil": math.ceil,
}
_BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
           ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
           ast.Pow: lambda a, b: a ** b, ast.Mod: lambda a, b: a % b}


def _normalize_expr(expr: str) -> str:
    """把常见写法归一成 Python 表达式（×/÷/^/＝ 等）。只做符号归一，不解析语义。"""
    s = expr.strip()
    s = s.split("=")[0].split("＝")[0]           # "3+4=?" 只取等号左边
    s = s.replace("×", "*").replace("÷", "/").replace("^", "**")
    s = s.replace("（", "(").replace("）", ")").replace("，", ",")
    s = s.strip().rstrip("?？")
    return s


def _eval_node(node, variables=None):
    """递归求值 AST 节点。variables: {name: value}（plot 时注入 x）。"""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ToolError("表达式里只能有数字")
    if isinstance(node, ast.BinOp):
        fn = _BINOPS.get(type(node.op))
        if fn is None:
            raise ToolError("不支持的运算符")
        return fn(_eval_node(node.left, variables), _eval_node(node.right, variables))
    if isinstance(node, ast.UnaryOp):
        v = _eval_node(node.operand, variables)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return +v
        raise ToolError("不支持的运算符")
    if isinstance(node, ast.Name):
        if variables is not None and node.id in variables:
            return float(variables[node.id])
        if node.id in _CONSTANTS:
            return float(_CONSTANTS[node.id])
        if node.id in _FUNCTIONS:
            raise ToolError("%s 是函数，要带括号调用（如 sqrt(9)）" % node.id)
        raise ToolError("不支持变量「%s」" % node.id)
    if isinstance(node, ast.Call):
        if not (isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS):
            raise ToolError("不允许的函数调用")
        if node.keywords:
            raise ToolError("不支持关键字参数")
        args = [_eval_node(a, variables) for a in node.args]
        return float(_FUNCTIONS[node.func.id](*args))
    raise ToolError("不支持的表达式结构")


def evaluate(expr: str, variables=None):
    """安全求值一个数学表达式，返回 float。变量默认禁止（calculator 用）。"""
    s = _normalize_expr(expr)
    if not s:
        raise ToolError("表达式为空")
    try:
        tree = ast.parse(s, mode="eval")
    except SyntaxError as e:
        raise ToolError("算式写错：%s" % e.msg) from e
    try:
        return _eval_node(tree, variables)
    except ZeroDivisionError as e:
        raise ToolError("不能除以 0") from e
    except OverflowError as e:
        raise ToolError("数字太大") from e


# ══════════════════════════════════════════════════════════════════════════
# 5 个工具
# ══════════════════════════════════════════════════════════════════════════

def calculator(expr: str) -> dict:
    """工具 1 · 计算器：纯算术求值（验算中间步骤用，🚫 不含变量）。

    返回 {"result": <数值字符串>}。
    拒绝变量 → 不能「代解方程」，只能帮学生核对纯计算（如 3×4、2^3、sqrt(9)）。
    """
    val = evaluate(expr)                      # 不注入 variables → 变量一律拒绝
    if val == int(val) and abs(val) < 1e15:
        return {"result": str(int(val))}
    return {"result": ("%.10g" % val)}


def _load_question_bank():
    sys.path.insert(0, EVAL_DIR)
    try:
        import question_bank  # noqa: PLC0415
        return list(getattr(question_bank, "QUESTION_BANK", []))
    except Exception as e:  # noqa: BLE001
        raise ToolError("题库加载失败：%s" % e) from e


def question_bank_lookup(subject: str = "", keyword: str = "", limit: int = 3) -> dict:
    """工具 2 · 题库：按学科/知识点检索同类题（只回题干 + 知识点，不泄答案）。

    用途：学生想「换一题同类练练」时给一道**新**题，不给原题答案。
    """
    bank = _load_question_bank()
    hits = []
    for q in bank:
        if subject and q.get("subject") != subject:
            continue
        if keyword and keyword not in (q.get("knowledge", "") + q.get("question", "")):
            continue
        hits.append(q)
    picked = hits[:max(1, min(int(limit), 10))]
    return {
        "count": len(picked),
        "questions": [{"id": q["id"], "subject": q["subject"],
                       "knowledge": q["knowledge"], "question": q["question"]}
                      for q in picked],        # 🚫 剥离 answer / leak
    }


def _load_wrong_book():
    if not os.path.isfile(WRONG_BOOK_PATH):
        return []
    try:
        with open(WRONG_BOOK_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001
        return []


def _save_wrong_book(items):
    os.makedirs(os.path.dirname(WRONG_BOOK_PATH), exist_ok=True)
    with open(WRONG_BOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def wrong_book_add(question: str, student_answer: str, knowledge: str = "") -> dict:
    """工具 3 · 错题本：记录一道错题（本地 JSON，不上传）。返回 {"total": n}。"""
    items = _load_wrong_book()
    items.append({
        "question": question,
        "student_answer": student_answer,
        "knowledge": knowledge,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    _save_wrong_book(items)
    return {"total": len(items)}


def wrong_book_list() -> dict:
    """错题本：返回当前已记录条数 + 最近 5 条（只回题干 + 知识点，不夹带答案）。"""
    items = _load_wrong_book()
    recent = [{"question": it.get("question", ""), "knowledge": it.get("knowledge", ""),
               "ts": it.get("ts", "")} for it in items[-5:]]
    return {"total": len(items), "recent": recent}


def parent_report(out_path: str = None) -> dict:
    """工具 4 · 家长报告：从错题本生成自包含中文 HTML（本地，不上传）。

    返回 {"path", "total_wrong", "knowledge_top"}。HTML 里只含自造题统计，不含学生隐私。
    """
    from collections import Counter
    items = _load_wrong_book()
    know = Counter(it.get("knowledge", "") for it in items if it.get("knowledge"))
    top = know.most_common(3)
    out_path = out_path or os.path.join(LOGS_DIR, "parent_report.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            _esc(it.get("knowledge", "")), _esc(it.get("question", "")),
            _esc(it.get("ts", "")))
        for it in items[-50:]
    )
    top_html = "".join("<li>%s：%d 题</li>" % (_esc(k), v) for k, v in top) or "<li>暂无</li>"
    html = ("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
            "<title>家教学习报告</title><style>body{font-family:system-ui;max-width:720px;"
            "margin:24px auto;padding:0 16px}table{border-collapse:collapse;width:100%%}"
            "td,th{border:1px solid #ddd;padding:6px 8px;text-align:left;font-size:14px}"
            "th{background:#f2f2f2}</style></head><body>"
            "<h1>家教学习报告</h1><p>错题总数：<b>%d</b></p>"
            "<h2>薄弱知识点</h2><ul>%s</ul>"
            "<h2>最近错题</h2><table><tr><th>知识点</th><th>题目</th><th>时间</th></tr>%s</table>"
            "</body></html>") % (len(items), top_html, rows)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return {"path": out_path, "total_wrong": len(items),
            "knowledge_top": [{"knowledge": k, "count": v} for k, v in top]}


def plot_function(expr: str, out_path: str = None, xmin: float = -10.0,
                  xmax: float = 10.0) -> dict:
    """工具 5 · 绘图：画 y = f(x) 的函数图像（支持 x 变量 + 白名单函数）。

    返回 {"path", "xmin", "xmax"}。用 matplotlib Agg 后端，无 GUI 依赖。
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    import numpy as np              # noqa: PLC0415

    s = _normalize_expr(expr)
    if "x" not in s:
        raise ToolError("图像表达式里要含变量 x，例如 x^2-1")
    tree = ast.parse(s, mode="eval")
    try:
        xs = np.linspace(xmin, xmax, 500)
        ys = np.array([_eval_node(tree, {"x": float(x)}) for x in xs])
    except ToolError:
        raise
    except Exception as e:  # noqa: BLE001
        raise ToolError("图像算不出来：%s" % e) from e

    out_path = out_path or os.path.join(LOGS_DIR, "plot_function.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(5, 3.4))
    plt.plot(xs, ys, linewidth=1.6)
    plt.axhline(0, color="#999", linewidth=0.7)
    plt.axvline(0, color="#999", linewidth=0.7)
    plt.title(expr, fontsize=11)
    plt.tight_layout()
    plt.savefig(out_path, dpi=110)
    plt.close()
    return {"path": out_path, "xmin": xmin, "xmax": xmax}


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ══════════════════════════════════════════════════════════════════════════
# 工具注册表（LLM 决策 / 路由 / 评测共用）
# ══════════════════════════════════════════════════════════════════════════

TOOLS = {
    "calculator": {
        "name": "calculator",
        "description": "纯算术计算（验算中间步骤），不能解方程/含变量。",
        "params": {"expr": "算术表达式，如 3*4 或 (2+3)^2"},
        "fn": lambda p: calculator(p.get("expr", "")),
    },
    "question_bank": {
        "name": "question_bank",
        "description": "按学科/知识点检索同类练习题（只给题干，不给答案）。",
        "params": {"subject": "学科（数学/物理/英语，可空）", "keyword": "知识点关键词（可空）"},
        "fn": lambda p: question_bank_lookup(p.get("subject", ""), p.get("keyword", "")),
    },
    "wrong_book_add": {
        "name": "wrong_book_add",
        "description": "把一道错题记入本地错题本。",
        "params": {"question": "题干", "student_answer": "学生的错答", "knowledge": "知识点（可空）"},
        "fn": lambda p: wrong_book_add(p.get("question", ""), p.get("student_answer", ""),
                                       p.get("knowledge", "")),
    },
    "wrong_book_list": {
        "name": "wrong_book_list",
        "description": "查看错题本里的错题。",
        "params": {},
        "fn": lambda p: wrong_book_list(),
    },
    "parent_report": {
        "name": "parent_report",
        "description": "生成家长报告（HTML，本地）。",
        "params": {},
        "fn": lambda p: parent_report(),
    },
    "plot_function": {
        "name": "plot_function",
        "description": "画函数 y=f(x) 的图像。",
        "params": {"expr": "含 x 的表达式，如 x^2-1"},
        "fn": lambda p: plot_function(p.get("expr", "")),
    },
}


def tool_names() -> list:
    return list(TOOLS.keys())


def tool_spec() -> str:
    """把工具清单拼成一段给 LLM 看的 JSON（用于 LLM 决策工具）。"""
    return json.dumps(
        [{k: t[k] for k in ("name", "description", "params")} for t in TOOLS.values()],
        ensure_ascii=False)


def call_tool(name: str, params: dict) -> dict:
    """按名调用工具。未知工具 / 异常都抛 ToolError。"""
    t = TOOLS.get(name)
    if t is None:
        raise ToolError("未知工具「%s」，可用：%s" % (name, ", ".join(tool_names())))
    try:
        return t["fn"](params or {})
    except ToolError:
        raise
    except Exception as e:  # noqa: BLE001
        raise ToolError("工具 %s 执行失败：%s" % (name, e)) from e


if __name__ == "__main__":
    # 自检演示（不触发真实网络/LLM）
    print("calculator(3*4) =", calculator("3*4"))
    print("calculator((2+3)^2) =", calculator("(2+3)^2"))
    print("question_bank(subject=数学, keyword=一元一次) 返回",
          question_bank_lookup(subject="数学", keyword="一元一次")["count"], "题")
    print("tool_spec() 摘要：", tool_spec()[:80], "...")
    try:
        calculator("x + 3")
    except ToolError as e:
        print("变量被拒（防代解方程）：", e)


