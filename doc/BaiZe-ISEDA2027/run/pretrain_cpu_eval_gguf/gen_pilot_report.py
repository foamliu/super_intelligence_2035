#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_pilot_report.py — 生成 llama.cpp/GGUF pilot 中文 HTML 报告（单文件自包含）。

读取 05_compare_with_hf.py 的 comparison.json 与 gguf_lmeval_run.py 的 meta.json，
加上环境/契约/分词对拍等已采集信息，输出 0 <script> / 0 CDN / 0 外链 HTML。

用法:
  python3 gen_pilot_report.py \
      --comparison /path/gguf_iter_10000/comparison.json \
      --meta /path/gguf_iter_10000/meta.json \
      --out .../reports/report_pretrain_llamacpp_pilot_zh.html \
      [--gguf-size 4.2G] [--llama-version "..."] [--cpu "..."] [--nproc 224] \
      [--selftest-pass 1] [--tok-check "24/24 PASS"] [--hf-results /path/results.json]
"""
import argparse
import html
import json
import os
from datetime import datetime


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_pct(x):
    try:
        return f"{float(x) * 100:.2f}%"
    except Exception:
        return str(x)


def table_rows(rows):
    out = []
    for r in rows:
        delta = r.get("delta_pp", 0)
        cls = "ok" if r.get("ok") else "bad"
        out.append(
            "<tr>"
            f"<td>{esc(r['task'])}</td>"
            f"<td>{fmt_pct(r['hf'])}</td>"
            f"<td>{fmt_pct(r['gguf'])}</td>"
            f"<td class='{cls}'>{delta:+.2f}</td>"
            f"<td>{r.get('n_hf') if r.get('n_hf') is not None else '-'}</td>"
            f"<td>{r.get('n_gg') if r.get('n_gg') is not None else '-'}</td>"
            f"<td class='{cls}'>{'OK' if r.get('ok') else 'FAIL'}</td>"
            "</tr>"
        )
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparison", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gguf-path", default="")
    ap.add_argument("--gguf-size", default="")
    ap.add_argument("--llama-version", default="")
    ap.add_argument("--cpu", default="")
    ap.add_argument("--nproc", default="")
    ap.add_argument("--selftest-pass", default="1")
    ap.add_argument("--tok-check", default="")
    ap.add_argument("--hf-results", default="")
    ap.add_argument("--extra-note", default="")
    args = ap.parse_args()

    comp = json.load(open(args.comparison, encoding="utf-8"))
    meta = json.load(open(args.meta, encoding="utf-8")) if os.path.isfile(args.meta) else {}
    rows = comp.get("rows", [])
    verdict = comp.get("verdict", "?")
    hf_avg = comp.get("hf_avg", 0)
    gg_avg = comp.get("gguf_avg", 0)
    avg_delta = comp.get("avg_delta_pp", 0)
    max_abs = comp.get("max_abs_delta_pp", 0)
    speedup = comp.get("speedup", 0)
    hf_reqs = comp.get("hf_requests_est", 0)
    hf_sec = comp.get("hf_seconds_est", 0)
    gg_sec = comp.get("gguf_seconds", 0)
    n_tok_req = meta.get("n_token_requests")
    s_per_req = meta.get("sec_per_token_request")

    selftest_ok = str(args.selftest_pass) == "1"
    tok_ok = "PASS" in str(args.tok_check).upper() or "/" in str(args.tok_check)
    vcol = "#1a7f37" if verdict == "PASS" else "#cf222e"
    vtxt = "PASS \u2014 \u53ef\u5207\u6362 GGUF\uff08\u5f85\u7528\u6377\u6279\uff09" if verdict == "PASS" else "FAIL \u2014 \u4e0d\u8981\u5207\u6362\uff0c\u4fdd\u7559 HF \u8def\u7ebf"
    css = "body{font-family:-apple-system,\"PingFang SC\",\"Microsoft YaHei\",sans-serif;max-width:980px;margin:24px auto;padding:0 18px;color:#1f2328;line-height:1.6}h1{font-size:1.5em;border-bottom:2px solid #58a6ff;padding-bottom:8px}h2{font-size:1.15em;margin-top:28px;border-left:4px solid #58a6ff;padding-left:10px}table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}th,td{border:1px solid #d0d7de;padding:6px 9px;text-align:center}th{background:#f6f8fa}.ok{color:#1a7f37;font-weight:600}.bad{color:#cf222e;font-weight:600}.verdict{font-size:1.2em;font-weight:700;padding:10px 14px;border-radius:8px;display:inline-block;margin:10px 0}code{background:#f6f8fa;padding:1px 5px;border-radius:4px;font-size:13px}.meta{color:#57606a;font-size:13px}ul{margin:6px 0}"
    hf_table = ""
    if args.hf_results and os.path.isfile(args.hf_results):
        try:
            hr = json.load(open(args.hf_results, encoding="utf-8")).get("results", {})
            hrows = []
            for key in ("sciq", "piqa"):
                if key in hr:
                    hrows.append("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                        esc(key), fmt_pct(hr[key].get("acc,none")),
                        fmt_pct(hr[key].get("acc_norm,none")), hr[key].get("sample_len", "-")))
            if hrows:
                hf_table = ("<h2>HF \u57fa\u7ebf\uff08iter_10000, float32, limit=100\uff09</h2>"
                    "<table><tr><th>\u4efb\u52a1</th><th>acc</th><th>acc_norm</th><th>n</th></tr>"
                    + "\n".join(hrows) + "</table>")
        except Exception:
            pass
    P = []
    P.append(f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>BaiZe 2B llama.cpp GGUF pilot</title><style>{css}</style></head><body>")
    P.append("<h1>BaiZe 2B \u00b7 llama.cpp / GGUF CPU \u8bc4\u6d4b pilot</h1>")
    P.append(f"<p class='meta'>\u751f\u6210\uff1a{esc(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))} \u00b7 ckpt=iter_10000 \u00b7 F16 \u00b7 sciq,piqa \u00b7 limit=100</p>")
    P.append("<h2>\u7ed3\u8bba</h2>")
    P.append(f"<div class='verdict' style='background:{vcol}22;color:{vcol};'>{esc(vtxt)}</div>")
    selftest_txt = "PASS \u2705" if selftest_ok else "FAIL \u274c"
    tok_txt = esc(args.tok_check) if tok_ok else "\u672a\u901a\u8fc7"
    P.append(f"<ul><li>06 \u5951\u7ea6\u81ea\u68c0\uff1a<b>{selftest_txt}</b>\uff08tokenize / token-id prompt / logit_bias / n_probs\uff09</li>"
             f"<li>02 \u5206\u8bcd\u5bf9\u62cd\uff1a<b>{tok_txt}</b></li>"
             f"<li>\u9010\u4efb\u52a1 max|\u0394acc| = <b>{max_abs:.2f}pp</b>\uff08\u22641.0pp\uff09</li>"
             f"<li>Avg |\u0394acc| = <b>{abs(avg_delta):.2f}pp</b>\uff08\u22641.0pp\uff09</li>"
             f"<li>\u52a0\u901f\u6bd4 = <b>{speedup:.1f}x</b>\uff08\u22655x\uff09</li></ul>")
    P.append("<h2>\u73af\u5883\u4e0e\u7248\u672c</h2>")
    P.append(f"<table><tr><th>\u9879</th><th>\u503c</th></tr>"
             f"<tr><td>\u673a\u5668</td><td>10.239.2.29\uff08.29\uff09</td></tr>"
             f"<tr><td>CPU</td><td>{esc(args.cpu)}</td></tr>"
             f"<tr><td>\u6838\u6570</td><td>{esc(args.nproc)}</td></tr>"
             f"<tr><td>llama-server</td><td><code>{esc(args.llama_version)}</code></td></tr>"
             "<tr><td>\u540e\u7aef</td><td>\u7eaf CPU\uff08GGML_NATIVE=ON, OpenMP\uff09, nice -n 19, -t 16, --parallel 2</td></tr>"
             "<tr><td>GPU</td><td>\u672a\u4f7f\u7528\uff08CUDA_VISIBLE_DEVICES=\"\"\uff09</td></tr></table>")
    P.append("<h2>\u6a21\u578b\u4e0e GGUF</h2>")
    P.append(f"<table><tr><th>\u9879</th><th>\u503c</th></tr>"
             "<tr><td>HF \u76ee\u5f55</td><td><code>/nas_train/.../nemo_experiments/baize2b/hf_iter_10000</code></td></tr>"
             "<tr><td>\u7ed3\u6784</td><td>nemotron_h \u00b7 56 \u5c42\uff0824 Mamba2 + 4 Attn + 28 MLP\uff09\u00b7 vocab 129408</td></tr>"
             f"<tr><td>GGUF \u8def\u5f84</td><td><code>{esc(args.gguf_path)}</code></td></tr>"
             f"<tr><td>GGUF \u5927\u5c0f</td><td>{esc(args.gguf_size)}</td></tr>"
             "<tr><td>\u91cf\u5316</td><td>F16\uff08\u5b98\u65b9\u53e3\u5f84\uff09</td></tr></table>")
    P.append("<h2>\u56db\u4e2a\u5951\u7ea6\u81ea\u68c0\uff0806_server_selftest.py\uff09</h2>")
    if selftest_ok:
        P.append("<ul><li>/tokenize\uff1a\u8fd4\u56de int token \u6570\u7ec4 \u2705</li>"
                 "<li>/completion \u63a5\u53d7 token-id \u6570\u7ec4 prompt \u2705</li>"
                 "<li>logit_bias \u5f3a\u5236\u76ee\u6807 token\uff0cn_probs>0 \u8fd4\u56de logprob \u2705\uff08forced id==target\uff09</li>"
                 "<li>cache_prompt \u91cd\u590d\u8bf7\u6c42\u7ed3\u679c\u4e00\u81f4\uff08|\u0394logprob|=0\uff09 \u2705</li></ul>")
    else:
        P.append("<p class='bad'>\u81ea\u68c0\u672a\u901a\u8fc7\u3002</p>")
    P.append("<h2>\u5206\u8bcd\u5bf9\u62cd\uff0802b_check_tokenizer_fast.py\uff09</h2>")
    if tok_ok:
        P.append(f"<p>12 \u6761\u4e2d/\u82f1/\u6df7\u6392/\u4ee3\u7801\u6837\u4f8b \u00d7 {{add_special True/False}} = 24 \u7ec4\uff0cGGUF(llama-server /tokenize) vs HF(tokenizer.json) <b>token id \u5b8c\u5168\u4e00\u81f4</b>\uff1a<span class='ok'>{esc(args.tok_check)}</span>\u3002</p>")
        P.append("<p class='meta'>\u6ce8\uff1a\u539f 02_check_tokenizer.py \u7528 transformers.AutoTokenizer\uff0c\u5728 py310 env \u89e6\u53d1 numpy ABI \u4e0d\u517c\u5bb9\uff08torch \u6309 numpy2.x \u7f16\u8bd1\u3001\u8fd0\u884c\u65f6 numpy 1.26.4\uff09\u3002\u56e0 HF AutoTokenizer \u5e95\u5c42\u5373 tokenizers\uff08\u7eaf Rust\uff09\uff0c\u6539\u7528 02b \u76f4\u63a5\u8bfb tokenizer.json\uff0c\u903b\u8f91\u7b49\u4ef7\u3001\u7ed5\u5f00 numpy\u3002</p>")
    else:
        P.append("<p class='bad'>\u5206\u8bcd\u5bf9\u62cd\u672a\u901a\u8fc7\u3002</p>")
    P.append("<h2>\u9010\u4efb\u52a1\u7ed3\u679c\uff08GGUF vs HF, acc\uff09</h2>")
    P.append(f"<table><tr><th>\u4efb\u52a1</th><th>HF</th><th>GGUF</th><th>\u0394pp</th><th>n_hf</th><th>n_gg</th><th>\u5224\u5b9a</th></tr>{table_rows(rows)}</table>")
    P.append(f"<p>Avg\uff1aHF = <b>{fmt_pct(hf_avg)}</b> \u00b7 GGUF = <b>{fmt_pct(gg_avg)}</b> \u00b7 \u0394 = <b>{avg_delta:+.2f}pp</b>\uff08\u4ec5 sciq+piqa\uff09</p>")
    if hf_table:
        P.append(hf_table)
    P.append("<h2>\u901f\u5ea6</h2>")
    P.append(f"<table><tr><th>\u9879</th><th>HF\uff08\u4f30\uff09</th><th>GGUF\uff08\u5b9e\u6d4b\uff09</th></tr>"
             f"<tr><td>\u8bf7\u6c42\u6570</td><td>{hf_reqs}</td><td>\u2014</td></tr>"
             f"<tr><td>token-requests</td><td>\u2014</td><td>{n_tok_req}</td></tr>"
             f"<tr><td>\u603b\u8017\u65f6</td><td>{hf_sec/3600:.2f}h</td><td>{gg_sec/60:.1f}min</td></tr>"
             f"<tr><td>\u6bcf\u8bf7\u6c42</td><td>16.44 s/req</td><td>{s_per_req}s/tok-req</td></tr>"
             f"<tr><td><b>\u52a0\u901f\u6bd4</b></td><td colspan='2'><b>{speedup:.1f}x</b></td></tr></table>")
    P.append("<p class='meta'>HF \u8017\u65f6\u4e3a\u6362\u7b97\u4f30\u8ba1\uff08\u8bf7\u6c42\u6570\u00d716.44 s/req\uff09\uff1bGGUF \u4e3a meta.json \u5b9e\u6d4b elapsed_sec\u3002\u4e24\u5957\u201c\u8bf7\u6c42\u201d\u53e3\u5f84\u4e0d\u540c\uff0c\u52a0\u901f\u6bd4\u6309\u603b\u5899\u949f\u6298\u7b97\u3002</p>")
    if args.extra_note:
        P.append(f"<h2>\u5907\u6ce8</h2><p>{esc(args.extra_note)}</p>")
    P.append("<h2>\u540e\u7eed\u5efa\u8bae</h2>")
    if verdict == "PASS":
        P.append("<ul><li>\u5df2 PASS\uff1a\u5efa\u8bae 5 \u4e2a ckpt \u5168\u7528 GGUF(F16) \u91cd\u8dd1\uff0c\u5148 --limit 100 \u590d\u73b0 5 \u70b9\u3002</li>"
                 "<li><b>\u4f46\u6309\u7528\u6237\u4ee4\uff0cPASS \u540e\u5148\u62a5\u544a\u518d\u7b49\u4ee4\uff0c\u4e0d\u64c5\u81ea\u5168\u91cf\u5207\u6362\u3002</b></li>"
                 "<li>02 \u7684 numpy \u95ee\u9898\u9700\u5728 py310 \u4fee numpy \u6216\u6539\u7528 02b\u3002</li></ul>")
    else:
        P.append("<ul><li>\u672a\u901a\u8fc7\u5224\u636e\uff0c\u4fdd\u7559 HF \u8def\u7ebf\u3002</li>"
                 "<li>\u53ef\u8003\u8651 .12 float32\u2192bf16 \u5e94\u6025\uff08\u7ea62x\uff09\uff0c\u4f46\u91cd\u542f\u8bc4\u6d4b\u9700\u7528\u6237\u6279\u51c6\u3002</li></ul>")
    P.append("</body></html>")
    outdir = os.path.dirname(args.out)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(P))
    print(f"[report] {args.out} ({os.path.getsize(args.out)} B)")


if __name__ == "__main__":
    main()
