#!/usr/bin/env python3
"""
dead_loop_scan.py -- scan a SystemVerilog file for loop constructs and emit a
single structured JSON document on stdout.

Usage:
    python3 dead_loop_scan.py <sv_file>

Recognised loop forms (per-type counts + 1-based start line numbers):
    forever          monitor/driver threads -> "intentional"
    for (...)        counted loops -> "bounded" (or "dead_loop" for for(;;))
    while (...)      plain while; busy-wait polling -> "dead_loop_candidate"
    do ... while()   one "do" construct (trailing while() line also reported)
    repeat (...)     counted loops -> "bounded"

A dead loop / candidate never terminates: either it has no timing control (a
combinational infinite loop) or it busy-waits on an external condition that is
not guaranteed to change.

Pure Python standard library, no third-party dependencies.
"""

import json
import os
import re
import sys


def blank_comments_and_strings(text):
    """Replace // and block comments plus double-quoted strings with spaces,
    preserving newlines so line numbers stay unchanged."""
    lines = text.split('\n')
    out_lines = []
    in_block = False
    for line in lines:
        chars = list(line)
        n = len(chars)
        i = 0
        while i < n:
            c = chars[i]
            if in_block:
                end = line.find('*/', i)
                if end == -1:
                    for k in range(i, n):
                        chars[k] = ' '
                    i = n
                else:
                    for k in range(i, end + 2):
                        chars[k] = ' '
                    i = end + 2
                    in_block = False
                continue
            if c == '"':
                j = i + 1
                while j < n:
                    if chars[j] == '\\':
                        j += 2
                        continue
                    if chars[j] == '"':
                        j += 1
                        break
                    j += 1
                for k in range(i, min(j, n)):
                    chars[k] = ' '
                i = j
                continue
            if c == '/' and i + 1 < n and chars[i + 1] == '/':
                for k in range(i, n):
                    chars[k] = ' '
                i = n
                continue
            if c == '/' and i + 1 < n and chars[i + 1] == '*':
                end = line.find('*/', i + 2)
                if end == -1:
                    for k in range(i, n):
                        chars[k] = ' '
                    in_block = True
                    i = n
                else:
                    for k in range(i, end + 2):
                        chars[k] = ' '
                    i = end + 2
                continue
            i += 1
        out_lines.append(''.join(chars))
    return '\n'.join(out_lines)


# ---------------------------------------------------------------------------
# regexes and small helpers
# ---------------------------------------------------------------------------

RE_FOREVER = re.compile(r'\bforever\b')
RE_FOR     = re.compile(r'\bfor\s*\(')
RE_WHILE   = re.compile(r'\bwhile\b')
RE_DO      = re.compile(r'\bdo\b')
RE_REPEAT  = re.compile(r'\brepeat\s*\(')
RE_BEGIN   = re.compile(r'\bbegin\b')
RE_END     = re.compile(r'\bend\b')
RE_TIMING  = re.compile(r'[@#]|\bwait\b|\bevent\b|->|\bjoin\w*\b')
RE_TASK_FN = re.compile(r'\b(function|task)\s+(?:automatic\s+|static\s+)?([A-Za-z_][A-Za-z0-9_$]*)\b')
RE_BLOCK   = re.compile(r'\bbegin\s*:\s*([A-Za-z_][A-Za-z0-9_$]*)')
RE_MODULE  = re.compile(r'\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)\b')


def line_number(line_starts, offset):
    lo, hi = 0, len(line_starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def find_context(orig_lines, line_no):
    """Return (kind, name) of the nearest enclosing named construct by scanning
    upward from the 1-based line number."""
    for idx in range(line_no - 1, -1, -1):
        text = orig_lines[idx]
        m = RE_TASK_FN.search(text)
        if m:
            return m.group(1), m.group(2)
        m = RE_BLOCK.search(text)
        if m:
            return 'block', m.group(1)
        m = RE_MODULE.search(text)
        if m:
            return 'module', m.group(1)
    return None, None


def extract_body(cleaned, loop_offset):
    """Return the loop body from the first 'begin' after loop_offset to its
    matching 'end' (or a bounded window for single-statement bodies)."""
    bm = RE_BEGIN.search(cleaned, loop_offset)
    if not bm:
        sm = re.search(r';', cleaned[loop_offset:])
        return cleaned[loop_offset:loop_offset + (sm.start() if sm else 400)]
    depth = 0
    pos = bm.start()
    for m in re.finditer(r'\bbegin\b|\bend\b', cleaned[pos:]):
        if m.group() == 'begin':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return cleaned[pos:pos + m.end()]
    return cleaned[pos:pos + 400]


def extract_for_header(cleaned, loop_offset):
    """Return the text between the parentheses of a for (...) header."""
    om = re.search(r'\(', cleaned[loop_offset:])
    if not om:
        return ''
    open_pos = loop_offset + om.start()
    depth = 0
    for i in range(open_pos, len(cleaned)):
        ch = cleaned[i]
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return cleaned[open_pos + 1:i]
    return ''


_LOOP_PATTERNS = {
    'forever': RE_FOREVER,
    'for': RE_FOR,
    'while': RE_WHILE,
    'do': RE_DO,
    'repeat': RE_REPEAT,
}


def loop_offset(cleaned, line_starts, ln, kind):
    """Recover the character offset of the loop keyword on the given line."""
    start = line_starts[ln - 1]
    end = line_starts[ln] if ln < len(line_starts) else len(cleaned)
    seg = cleaned[start:end]
    m = _LOOP_PATTERNS[kind].search(seg)
    return start + m.start() if m else start


def classify_and_reason(kind, body, ctx, header=''):
    """Return (classification, reason) for one loop."""
    has_timing = bool(RE_TIMING.search(body))
    name = ctx if ctx else '<unnamed>'
    if kind == 'forever':
        if has_timing:
            return ('intentional',
                    'forever thread in "%s" contains event/delay control: '
                    'intentionally never-terminating monitor/driver loop '
                    '(exits only via disable or end of simulation)' % name)
        return ('dead_loop_candidate',
                'forever loop in "%s" has no timing control: combinational '
                'infinite loop with zero simulation-time progress' % name)
    if kind == 'repeat':
        return ('bounded',
                'repeat loop in "%s" with a fixed iteration count: always '
                'terminates' % name)
    if kind == 'for':
        parts = [p.strip() for p in header.split(';')]
        if len(parts) < 3 or parts[1] == '':
            return ('dead_loop',
                    'for loop in "%s" has an empty termination condition '
                    '(for(;;)): never terminates' % name)
        return ('bounded',
                'bounded for-loop in "%s" with init/condition/step header: '
                'terminates after a finite number of iterations' % name)
    if kind == 'while':
        if not has_timing:
            return ('dead_loop',
                    'while loop in "%s" has no timing control: zero-delay '
                    'spin, the process cannot make simulation-time progress' % name)
        return ('dead_loop_candidate',
                'while busy-wait loop in "%s" polls a condition with delay '
                'control but no guaranteed exit: may spin forever if the '
                'awaited condition never changes' % name)
    if kind == 'do':
        if not has_timing:
            return ('dead_loop',
                    'do...while loop in "%s" has no timing control: '
                    'zero-delay spin' % name)
        return ('dead_loop_candidate',
                'do...while loop in "%s" only advances when its trailing '
                'while() condition is satisfied; if the awaited external '
                'signal/watchdog never changes it never terminates' % name)
    return ('unknown', 'unrecognised loop construct')


def scan_file(source_text, filename):
    cleaned = blank_comments_and_strings(source_text)
    orig_lines = source_text.split('\n')

    line_starts = [0]
    for i, ch in enumerate(cleaned):
        if ch == '\n':
            line_starts.append(i + 1)

    # Collect loop-keyword events in document order.
    events = []
    for rex, kind in ((RE_FOREVER, 'forever'), (RE_FOR, 'for'),
                      (RE_WHILE, 'while'), (RE_DO, 'do'),
                      (RE_REPEAT, 'repeat')):
        for m in rex.finditer(cleaned):
            events.append((m.start(), kind))
    events.sort(key=lambda e: e[0])

    loops = []
    do_stack = []
    for off, kind in events:
        ln = line_number(line_starts, off)
        if kind == 'do':
            loop = {'type': 'do', 'line': ln, 'while_line': None}
            loops.append(loop)
            do_stack.append(loop)
        elif kind == 'while':
            # A 'while' that is the trailing test of a do...while() loop is
            # immediately preceded by the 'end' of the do block.
            if do_stack and re.search(r'\bend\s*$', cleaned[:off]):
                do_stack.pop()['while_line'] = ln
            else:
                loops.append({'type': 'while', 'line': ln})
        else:
            loops.append({'type': kind, 'line': ln})

    for loop in loops:
        kind = loop['type']
        _, ctx = find_context(orig_lines, loop['line'])
        loop['context'] = ctx
        off = loop_offset(cleaned, line_starts, loop['line'], kind)
        body = extract_body(cleaned, off)
        header = extract_for_header(cleaned, off) if kind == 'for' else ''
        cls, reason = classify_and_reason(kind, body, ctx, header)
        loop['classification'] = cls
        loop['is_dead_loop_candidate'] = cls in ('dead_loop_candidate', 'dead_loop')
        loop['reason'] = reason

    loops.sort(key=lambda x: (x['line'], x['type']))

    counts = {'forever': 0, 'for': 0, 'while': 0, 'do': 0, 'repeat': 0}
    for loop in loops:
        counts[loop['type']] += 1
    counts['total'] = len(loops)

    def lines_of(kind):
        return [l['line'] for l in loops if l['type'] == kind]

    dead = [l for l in loops if l['is_dead_loop_candidate']]

    result = {
        'file': filename,
        'counts': counts,
        'forever': {
            'count': counts['forever'],
            'classification': 'intentional',
            'lines': lines_of('forever'),
        },
        'for': {'count': counts['for'], 'lines': lines_of('for')},
        'while': {'count': counts['while'], 'lines': lines_of('while')},
        'do': {'count': counts['do'], 'lines': lines_of('do'),
               'while_lines': [l['while_line'] for l in loops if l['type'] == 'do']},
        'repeat': {'count': counts['repeat'], 'lines': lines_of('repeat')},
        'loops': loops,
        'dead_loop_candidates': dead,
        'summary': {
            'total_loops': counts['total'],
            'dead_loop_candidates': len(dead),
            'intentional_forever': counts['forever'],
        },
    }
    return result


def main(argv):
    if len(argv) != 2:
        sys.stderr.write('usage: python3 dead_loop_scan.py <sv_file>\n')
        return 2
    path = argv[1]
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as fh:
            text = fh.read()
    except OSError as exc:
        sys.stderr.write('error: cannot read %s: %s\n' % (path, exc))
        return 1
    result = scan_file(text, os.path.basename(path))
    sys.stdout.write(json.dumps(result, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))