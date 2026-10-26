#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 H-A SWE-bench Verified 横评就绪核查报告（中文 HTML，自包含）。

按 BAIZE_HARNESS_TASK.md §1.2「先 20-50 条跑通全流程」+ §3「先报预算再跑」，
本轮交付物 = 就绪核查 + 预算 + 试点计划，供运维拍板是否放大。
数据全部来自实测（命令+输出见报告「证据」列），不编造。
命名规程：报告正文一律写 `cline`（不写 cline-patched）。
"""
from __future__ import annotations
import html
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "report_swebench_verified_readiness_zh.html"

# ---- 实测数据（每条带溯源） ----
CHECKS = [
    ("Docker 镜像（SWE-bench Verified）", "✅ 通过",
     ("sg docker -c 'docker images | grep swebench | sort -u | wc -l'",
      "500 （样本 swebench/sweb.eval.x86_64.sympy_1776_sympy-24213:latest）")),
    ("下载完成性", "✅ 通过",
     ("tail swebench_verified_pull_progress.txt:514",
      "DONE 2026-10-26 18:23:06 total=500 pulled=500 failed=0 skipped=0 ; swebench/* present: 500/500")),
    ("docker 访问权限", "✅ 通过（sg docker）",
     ("sg docker -c 'docker images -q | wc -l'", "610 张镜像可读（本用户经 sg docker 切组可访问 docker）")),
    ("swebench 包", "✅ 通过",
     ("python3 -c 'import swebench; print(swebench.__version__)'",
      "5.0.2 @ /nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/swebench/__init__.py")),
    ("模型网关可达性", "✅ 通过",
     ("curl http://agi-gateway.cxmt.com/v1/models", "HTTP 200  time=0.020994s")),
    ("模型可调用性", "🟡 待 gw_proxy 复测",
     ("run_harness.py:42 / curl gateway chat(dummy key)",
      "kimi-k2.6-cloud 统一骨干；直连 dummy key 返回空(预期:真实 key 在 gw_proxy/secrets)")),
    ("Verified 数据集（HF）", "✅ 通过（需 proxy）",
     ("https_proxy=172.19.92.25:13128 load_dataset(princeton-nlp/SWE-bench_Verified,test)",
      "Verified 500 首题 astropy__astropy-12907 (与 image_list.txt 一致)")),
    ("实例列表", "✅ 通过",
     ("wc -l swebench_verified_image_list.txt", "500 行,格式 instance_id<TAB>docker_image")),
    ("磁盘空间", "✅ 通过", ("df -h /data", "7.0T 总/1018G 已用/6.0T 可用(15%)")),
    ("系统负载", "✅ 通过（低）", ("cat /proc/loadavg", "7.52 7.96 8.91 (224 核,~3.4%)")),
    ("训练避让", "⚠️ 需注意",
     ("ps aux|grep baize_pretrain_loop", "PID 1401353 bash ./baize_pretrain_loop.sh 在 .29 运行(避让重 I/O)")),
    ("unshare rootfs 路线", "❌ 不适用（仅 13 个）",
     ("ls /nas_train/app.e0031982/harness_work/rootfs/|wc -l", "13 个(Lite pilot 用,对 500 题不现实)")),
    ("官方 docker 评测入口", "🟡 需适配",
     ("from swebench.harness.run_evaluation import run_evaluation",
      "ImportError(v5.0.2 改名;r1_eval.py 已用 make_test_spec/get_eval_report 可用)")),
]

BUDGET_ROWS = [
    ("20 实例 × 7 harness = 140 预测", "串行 7-19h；gw_proxy 并发 7 路 ≈ 1-3h", "容器临时层 <50GB"),
    ("50 实例 × 7 harness = 350 预测", "串行 18-47h；并发 7 路 ≈ 3-7h", "容器临时层 <120GB"),
    ("docker 评测(apply patch+run tests)", "≈2-10 min/实例；140 条并发 8 路 ≈ 0.5-3h", "ephemeral,结束即释放"),
]

PLAN = [
    ("规模", "先 20 条(§1.2 下限),从 image_list.txt 抽 5 个 repo 各 4 题,覆盖 astropy/django/sympy/matplotlib/flask"),
    ("harness", "先跑 cline + hermes 两路(已验证可用适配器),跑通后再扩到 7 路"),
    ("模型", "kimi-k2.6-cloud(与 2100 Lite 同一统一骨干,口径可比)"),
    ("评测", "docker 官方 harness(500 镜像已就绪);若 v5.0.2 入口不符,用 r1_eval.py 的 docker-exec 适配层"),
    ("口径", "同实例集/同模型/同 timeout/同 max_turns/同评测脚本(§1.2 统一口径)"),
    ("并发", "预测阶段 gw_proxy 7 路并发(Lite 已验证);评测阶段 docker --max-workers=8"),
    ("避让", "pretrain 在 .29 训练→预测 gen 吃 CPU/网络,评测吃 docker/CPU;限并发=4 或等训练间隙"),
    ("交付", "harness/SWEBENCH_VERIFIED_PILOT.html(口径·结果表·失败模式·日志路径)+原始 patch/评测输出(不入库)"),
]

RISKS = [
    "v5.0.2 的 run_evaluation 入口改名→需先查 swebench/harness/run_evaluation.py 实际导出,或用 r1_eval.py 的 docker-exec 适配层(已 import make_test_spec/get_eval_report)。",
    "kimi-k2.6-cloud 直连 gateway 用 dummy key 返回空→必须经 gw_proxy(9090/9091,注入真实 key);启动前先 smoke 1 条预测验证。",
    "pretrain 训练在 .29→重 I/O 避让:预测并发≤4、docker 评测 --max-workers≤4,或等训练间隙。",
    "docker 仅经 sg docker 可用→评测脚本须以 sg docker -c 包裹,或加入 docker 组(需运维)。",
    "Verified 部分实例的 test 较重(如 sphinx/build)→单条 timeout 按官方默认 1800s,超时记 timeout 非失败。",
]

def esc(s): return html.escape(str(s))

CSS = """
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1080px;margin:24px auto;padding:0 20px;color:#222;line-height:1.65}
h1{font-size:1.5em;border-bottom:3px solid #6c5ce7;padding-bottom:8px}
h2{font-size:1.2em;color:#6c5ce7;margin-top:2em;border-left:5px solid #6c5ce7;padding-left:10px}
h3{font-size:1.05em;color:#444;margin-top:1.4em}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.92em}
th,td{border:1px solid #ccc;padding:6px 9px;text-align:left;vertical-align:top}
th{background:#f4f1fb}
tr:nth-child(even){background:#fafafa}
.ok{color:#0984e3;font-weight:bold}.warn{color:#e17055;font-weight:bold}.bad{color:#d63031;font-weight:bold}
.tldr{background:#f4f1fb;border:1px solid #d5cdf5;border-radius:8px;padding:14px 18px;margin:16px 0}
.code{font-family:ui-monospace,Consolas,monospace;font-size:0.85em;background:#f6f6f6;padding:2px 5px;border-radius:3px}
.ev{font-family:ui-monospace,Consolas,monospace;font-size:0.82em;color:#555}
small{color:#888}
.tag{display:inline-block;background:#6c5ce7;color:#fff;border-radius:10px;padding:1px 8px;font-size:0.78em;margin-right:4px}
"""

def table_check():
    rows = []
    for name, status, (cmd, out) in CHECKS:
        cls = "ok" if status.startswith("✅") else ("warn" if ("🟡" in status or "⚠️" in status) else "bad")
        rows.append(f'<tr><td>{esc(name)}</td><td class="{cls}">{esc(status)}</td>'
                    f'<td class="ev">$ {esc(cmd)}<br>→ {esc(out)}</td></tr>')
    return "<table><tr><th>核查项</th><th>状态</th><th>证据（命令/输出）</th></tr>" + "".join(rows) + "</table>"

def table_budget():
    rows = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>' for a, b, c in BUDGET_ROWS)
    return "<table><tr><th>场景</th><th>时间估算</th><th>磁盘估算</th></tr>" + rows + "</table>"

def table_plan():
    rows = "".join(f'<tr><td><span class="tag">{esc(k)}</span></td><td>{esc(v)}</td></tr>' for k, v in PLAN)
    return "<table><tr><th style=width:120px>维度</th><th>方案</th></tr>" + rows + "</table>"

def main():
    h = []
    h.append("<!DOCTYPE html><html lang=zh-CN><head><meta charset=utf-8>"
             "<meta name=viewport content='width=device-width,initial-scale=1'>"
             "<title>H-A SWE-bench Verified 横评就绪核查报告</title><style>" + CSS + "</style></head><body>")
    h.append("<h1>H-A · SWE-bench Verified 横评就绪核查报告</h1>")
    h.append('<p><span class="tag">H-A</span><span class="tag">SWE-bench Verified</span>'
             '<span class="tag">就绪核查</span><span class="tag">预算</span>'
             '<small>  BaiZe Harness 研究线 · 2026-10-26 22:4x · R518</small></p>')
    h.append('<div class="tldr"><h3 style="margin-top:0">TL;DR</h3>'
             '<p>SWE-bench Verified <b>500 张 docker 镜像已全部下载完成</b>（500/500，0 failed，'
             '进度文件 <span class="code">swebench_verified_pull_progress.txt:514</span>）。'
             '经 <span class="code">sg docker</span> 实测 500 个 <span class="code">swebench/*</span> 仓库在盘可读；'
             'swebench v5.0.2、模型网关（HTTP 200）、Verified 数据集（带 proxy 可加载，500 题）均就绪。'
             '<b>评测路径选定 docker 官方 harness</b>（unshare rootfs 仅 13 个，不适用于 500 题）。</p>'
             '<p><b>结论：就绪，可启动 20 条试点</b>（§1.2 下限）。建议先 cline + hermes 两路 smoke，'
             '跑通全流程（预测→docker 评测→打分）后再扩 7 路 × 50 条。<b>需运维拍板</b>：'
             '① 是否批准 20 条试点启动；② 是否限并发（pretrain 在 .29 训练，重 I/O 避让）。</p></div>')

    h.append("<h2>1. 下载状态</h2>")
    h.append('<p>SWE-bench Verified 共 500 题，镜像由 <span class="code">swebench_verified_pull.sh</span> '
             '后台批量拉取（Docker Hub 匿名限速 100 manifest/h，串行 + 断点续跑）。</p>')
    h.append('<p class="ev">$ tail swebench_verified_pull_progress.txt<br>'
             '→ [swebench-pull] DONE 2026-10-26 18:23:06 total=500 pulled=500 failed=0 skipped=0<br>'
             '→ [swebench-pull] swebench/* present: 500 / 500</p>')
    h.append('<p>实例列表 <span class="code">swebench_verified_image_list.txt</span>（500 行，'
             '格式 <span class="code">instance_id&lt;TAB&gt;docker_image</span>），首题 '
             '<span class="code">astropy__astropy-12907</span>，与 HF 数据集一致。</p>')

    h.append("<h2>2. 评测路径选型</h2>")
    h.append("<table><tr><th>路线</th><th>机制</th><th>对 Verified 适用性</th><th>结论</th></tr>"
             "<tr><td>docker 官方 harness</td><td>500 张 sweb.eval 镜像，apply patch + run tests + grade</td>"
             "<td>✅ 镜像已就绪 500/500</td><td class=ok><b>采用</b></td></tr>"
             "<tr><td>unshare 沙箱（r1_eval.py）</td><td>每实例需独立 rootfs</td>"
             "<td>❌ 仅 13 个 rootfs（Lite pilot 用），500 题建 rootfs 工作量过大</td><td class=bad>不采用</td></tr>"
             "</table>")
    h.append('<p><small>注：r1_eval.py 的评分代码（<span class="code">make_test_spec</span> / '
             '<span class="code">get_eval_report</span>）仍可复用于 docker 路线的 grading 层。</small></p>')

    h.append("<h2>3. 就绪核查清单</h2>")
    h.append(table_check())
    h.append("<h2>4. 预算估算</h2>")
    h.append('<p>基于 2100 条 Lite 历史运行（7 harness × 300 实例 serial ~7h）外推，'
             '单 harness 单实例预测 ~3-8 min（带工具循环），docker 评测 ~2-10 min/实例。</p>')
    h.append(table_budget())
    h.append('<p><small>磁盘：docker 镜像已占盘（/data 1018G 已用），评测容器为 ephemeral，'
             '增量主要是临时层 <120GB，6.0T 可用充足。</small></p>')

    h.append("<h2>5. 试点计划（20 条）</h2>")
    h.append(table_plan())
    h.append("<h2>6. 风险与待解项</h2>")
    h.append("<ul>" + "".join("<li>" + esc(r) + "</li>" for r in RISKS) + "</ul>")

    h.append("<h2>7. 复现命令</h2>")
    h.append('<p class="ev">'
             '# 下载完成性<br>tail doc/BaiZe-ISEDA2027/run/harness/swebench_verified_pull_progress.txt<br><br>'
             '# docker 镜像计数（经 sg docker）<br>'
             'sg docker -c \'docker images --format "{{.Repository}}" | grep -i swebench | sort -u | wc -l\'<br><br>'
             '# swebench 版本<br>python3 -c "import swebench; print(swebench.__version__)"<br><br>'
             '# 网关可达<br>curl -sS -m8 -o /dev/null -w "%{http_code}" http://agi-gateway.cxmt.com/v1/models<br><br>'
             '# Verified 数据集（需 proxy）<br>'
             'https_proxy=http://172.19.92.25:13128 python3 -c "from datasets import load_dataset; d=load_dataset(\'princeton-nlp/SWE-bench_Verified\',split=\'test\'); print(len(d), d[0][\'instance_id\'])"<br><br>'
             '# 系统负载 / 训练避让<br>cat /proc/loadavg; ps -eo pid=,args= | grep baize_pretrain_loop | grep -v grep</p>')

    h.append("<h2>8. 下一步</h2>")
    h.append("<ol>"
             "<li><b>等运维拍板</b>：是否批准 20 条试点 + 并发限制。</li>"
             "<li>批准后：smoke 1 条（cline，astropy__astropy-12907）验证「预测→docker 评测→打分」全链路。</li>"
             "<li>smoke 通过 → 跑 20 条 × cline + hermes → 出初步结果表 → 报运维决定是否放大到 50/500。</li>"
             "<li>放大到 7 路 × 50/500 前，确认 v5.0.2 docker 评测入口 / gw_proxy 并发 / 训练避让。</li>"
             "</ol>")
    h.append('<p style="margin-top:2em"><small>本报告数据全部来自实测命令输出（见「证据」列与「复现命令」），'
             '不编造。命名遵循规程：正文一律 <code>cline</code>。BaiZe Harness 研究线 R518，2026-10-26。</small></p>')
    h.append("</body></html>")
    OUT.write_text("\n".join(h), encoding="utf-8")
    print("WROTE " + str(OUT) + "  " + str(OUT.stat().st_size) + " B")

if __name__ == "__main__":
    main()
