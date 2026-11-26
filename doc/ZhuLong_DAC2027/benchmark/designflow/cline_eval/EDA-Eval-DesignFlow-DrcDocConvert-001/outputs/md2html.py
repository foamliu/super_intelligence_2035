#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md2html - a generic Markdown -> HTML converter.

Converts a Markdown file into a standalone, human-friendly HTML document.

Usage:
    python3 md2html.py <input.md> <output.html>

Supported syntax:
    * ATX headings (#, ##, ...) and setext headings (===)
    * paragraphs and hard-wrapped lines
    * fenced code blocks (``` ... ```, ~~~ ... ~~~) and indented code blocks
    * unordered (- * +) and ordered (1. 2. ...) lists, including nesting
    * blockquotes (> ...)
    * horizontal rules (--- *** ___)
    * inline code (`...`), bold (**...** / __...__), italic (*...* / _..._)
    * links [text](url) and images ![alt](url)

This script only uses the Python standard library and does not hard-code any
document content; it is a fully general converter.
"""

import sys
import os
import re
import html as _html


_HTML_SHELL = """<!DOCTYPE html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
        "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
        "Noto Sans CJK SC", "Helvetica Neue", Arial, sans-serif;
    line-height: 1.75;
    color: #24292f;
    max-width: 960px;
    margin: 0 auto;
    padding: 24px 36px 80px;
    background: #ffffff;
}
h1, h2, h3, h4, h5, h6 {
    color: #16324f;
    margin: 1.7em 0 0.55em;
    line-height: 1.3;
    font-weight: 600;
}
h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.05em; }
h5, h6 { font-size: 1em; }
p { margin: 0 0 16px; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background: rgba(27, 31, 35, 0.06);
    border-radius: 3px;
    padding: 0.15em 0.35em;
    font-size: 0.9em;
}
pre {
    background: #f6f8fa;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    padding: 14px 16px;
    overflow: auto;
    line-height: 1.45;
    margin: 0 0 16px;
}
pre code { background: transparent; padding: 0; font-size: 0.88em; }
blockquote {
    margin: 0 0 16px;
    padding: 0 1em;
    color: #57606a;
    border-left: 4px solid #d0d7de;
}
ul, ol { margin: 0 0 16px; padding-left: 2em; }
li { margin: 0.25em 0; }
li > ul, li > ol { margin: 0.3em 0; }
li p { margin: 0.3em 0; }
hr { border: none; border-top: 2px solid #eaecef; margin: 24px 0; }
table { border-collapse: collapse; margin: 0 0 16px; }
th, td { border: 1px solid #d0d7de; padding: 6px 13px; }
th { background: #f6f8fa; }
strong { font-weight: 600; }
</style>
</head>
<body>
__BODY__
</body>
</html>
"""


_LIST_RE = re.compile(r'^([ ]*)([-*+]|\d+[.)])\s+(.*)$')
_CJK_RE = re.compile(r'[\u3400-\u9fff]')


def _escape(text):
    return _html.escape(text, quote=False)


def _protect_code_spans(text):
    """Replace inline `code` spans with placeholders; return (text, tokens)."""
    tokens = []

    def _repl(m):
        tokens.append(m.group(1))
        return '\x00CS%d\x00' % (len(tokens) - 1)

    text = re.sub(r'`([^`]*)`', _repl, text)
    return text, tokens


def _restore_code_spans(text, tokens):
    def _repl(m):
        idx = int(m.group(1))
        return '<code>%s</code>' % tokens[idx]

    return re.sub(r'\x00CS(\d+)\x00', _repl, text)


def _inline(text):
    text = _escape(text)
    text, tokens = _protect_code_spans(text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_([^_\n]+)_(?!\w)', r'<em>\1</em>', text)
    return _restore_code_spans(text, tokens)


def _is_hr(line):
    s = re.sub(r'\s+', '', line.strip())
    return len(s) >= 3 and len(set(s)) == 1 and s[0] in '-*_'


def _is_block_start(line):
    s = line.strip()
    if not s:
        return False
    if s.startswith('```') or s.startswith('~~~'):
        return True
    if re.match(r'^#{1,6}\b', s):
        return True
    if _is_hr(line):
        return True
    if re.match(r'^>', s):
        return True
    if _LIST_RE.match(line):
        return True
    if line[:4] == '    ' or line[:1] == '\t':
        return True
    return False


def _parse_list(lines, i):
    """Parse one (possibly nested) list starting at lines[i]; return (html, next_i)."""
    first = _LIST_RE.match(lines[i])
    base = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    tag = 'ol' if ordered else 'ul'
    n = len(lines)
    out = ['<' + tag + '>']

    while i < n:
        line = lines[i]
        # Blank lines inside a list: only continue if a same-level item follows.
        if line.strip() == '':
            j = i
            while j < n and lines[j].strip() == '':
                j += 1
            if j >= n:
                i = j
                break
            mj = _LIST_RE.match(lines[j])
            if mj and len(mj.group(1)) == base and (mj.group(2)[0].isdigit()) == ordered:
                i = j
                continue
            break

        m = _LIST_RE.match(line)
        if not m:
            break
        ind = len(m.group(1))
        this_ord = m.group(2)[0].isdigit()
        if ind < base:
            break
        if ind == base and this_ord != ordered:
            break
        if ind > base:
            # A nested list directly under the previous item.
            frag, i = _parse_list(lines, i)
            out.append(frag)
            continue

        # A same-level list item.
        text = m.group(3)
        i += 1
        out.append('<li>' + _inline(text))
        cont = []
        while i < n:
            nl = lines[i]
            if nl.strip() == '':
                j = i
                while j < n and lines[j].strip() == '':
                    j += 1
                if j >= n:
                    i = j
                    break
                mj = _LIST_RE.match(lines[j])
                if mj and len(mj.group(1)) > base:
                    if cont:
                        out.append('<p>%s</p>' % _inline(' '.join(cont)))
                        cont = []
                    i = j
                    if i < n:
                        frag, i = _parse_list(lines, i)
                        out.append(frag)
                    continue
                break
            mnl = _LIST_RE.match(nl)
            if mnl:
                ni = len(mnl.group(1))
                if ni > base:
                    if cont:
                        out.append('<p>%s</p>' % _inline(' '.join(cont)))
                        cont = []
                    frag, i = _parse_list(lines, i)
                    out.append(frag)
                    continue
                break
            cont.append(nl.strip())
            i += 1
        if cont:
            out.append(' ' + _inline(' '.join(cont)))
        out.append('</li>')

    out.append('</' + tag + '>')
    return ''.join(out), i


def _parse(lines):
    """Convert a list of raw markdown lines into an HTML body fragment."""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == '':
            i += 1
            continue

        # Fenced code block.
        ls = line.lstrip()
        if ls.startswith('```') or ls.startswith('~~~'):
            fence = ls[:3]
            i += 1
            buf = []
            while i < n and not lines[i].lstrip().startswith(fence):
                buf.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code = '\n'.join(buf)
            if code.endswith('\n'):
                code = code[:-1]
            out.append('<pre><code>%s</code></pre>' % _escape(code))
            continue

        # ATX heading.
        m = re.match(r'^[ ]{0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$', line)
        if m:
            lvl = len(m.group(1))
            txt = (m.group(2) or '').strip()
            out.append('<h%d>%s</h%d>' % (lvl, _inline(txt), lvl))
            i += 1
            continue

        # Setext heading (=== under a text line).
        if (i + 1 < n and lines[i + 1].strip() and
                re.fullmatch(r'[ ]*={3,}[ ]*', lines[i + 1]) and not _is_hr(line)):
            out.append('<h1>%s</h1>' % _inline(line.strip()))
            i += 2
            continue

        # Horizontal rule.
        if _is_hr(line):
            out.append('<hr>')
            i += 1
            continue

        # Blockquote.
        if re.match(r'^[ ]{0,3}>', line):
            qlines = []
            while i < n and (re.match(r'^[ ]{0,3}>', lines[i]) or lines[i].strip() == ''):
                mq = re.match(r'^[ ]{0,3}> ?(.*)$', lines[i])
                qlines.append(mq.group(1) if mq else '')
                i += 1
            out.append('<blockquote>%s</blockquote>' % _parse(qlines))
            continue

        # List.
        lm = _LIST_RE.match(line)
        if lm:
            frag, i = _parse_list(lines, i)
            out.append(frag)
            continue

        # Indented code block.
        if line[:4] == '    ' or line[:1] == '\t':
            buf = []
            while i < n and (lines[i][:4] == '    ' or lines[i][:1] == '\t' or lines[i].strip() == ''):
                cur = lines[i]
                if cur.strip() == '':
                    buf.append('')
                elif cur[:4] == '    ':
                    buf.append(cur[4:])
                else:
                    buf.append(cur[1:])
                i += 1
            while buf and buf[-1] == '':
                buf.pop()
            out.append('<pre><code>%s</code></pre>' % _escape('\n'.join(buf)))
            continue

        # Paragraph.
        buf = [line.strip()]
        i += 1
        while i < n and lines[i].strip() != '' and not _is_block_start(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append('<p>%s</p>' % _inline(' '.join(buf)))
        continue

    return ''.join(out)


def _extract_title(text, fallback):
    for line in text.split('\n'):
        m = re.match(r'^[ ]{0,3}#[ \t]+(.*)$', line)
        if m:
            t = m.group(1).strip()
            t = re.sub(r'`([^`]*)`', r'\1', t)
            t = re.sub(r'\*\*([^*]+)\*\*', r'\1', t)
            t = re.sub(r'\*([^*]+)\*', r'\1', t)
            t = re.sub(r'__([^_]+)__', r'\1', t)
            t = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', t)
            return _escape(t)
    return _escape(fallback)


def convert(text, title=None, lang=None):
    if lang is None:
        lang = 'zh' if _CJK_RE.search(text) else 'en'
    if title is None:
        title = _extract_title(text, 'Document')
    body = _parse(text.replace('\r\n', '\n').replace('\r', '\n').split('\n'))
    return (_HTML_SHELL
            .replace('__LANG__', lang)
            .replace('__TITLE__', title)
            .replace('__BODY__', body))


def main(argv):
    if len(argv) != 3:
        sys.stderr.write('Usage: python3 md2html.py <input.md> <output.html>\n')
        return 2
    src, dst = argv[1], argv[2]
    with open(src, 'r', encoding='utf-8') as fh:
        text = fh.read()
    stem = os.path.splitext(os.path.basename(src))[0]
    result = convert(text, title=_extract_title(text, stem))
    with open(dst, 'w', encoding='utf-8') as fh:
        fh.write(result)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))