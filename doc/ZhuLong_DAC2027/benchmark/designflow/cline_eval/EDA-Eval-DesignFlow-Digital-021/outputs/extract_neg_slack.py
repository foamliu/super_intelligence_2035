#!/usr/bin/env python3
"""Extract all paths with negative (violating) slack from a PrimeTime
report_timing report and write them to a new report.

Usage:
    python3 extract_neg_slack.py <input_report> <output_report>

The input is a plain-text PrimeTime report_timing dump. Each path block starts
with a line such as "Path 1: VIOLATED Late External Delay Assertion" and is
followed by Endpoint / Beginpoint / Path Groups / Analysis View lines and the
timing value lines (Other End Arrival Time, External Delay, Phase Shift,
CPPR Adjustment, Uncertainty, Required Time, Arrival Time, Slack Time).
"""

import re
import sys

PATH_HEADER_RE = re.compile(r'^Path\s+(\d+):\s*(.*)$')


def parse_number(line):
    """Return the trailing numeric token of a timing line as a float."""
    tokens = line.split()
    if not tokens:
        return None
    try:
        return float(tokens[-1])
    except ValueError:
        return None


def parse_endpoint(line):
    """Return the endpoint name from an 'Endpoint:' line.

    Example:
        "  Endpoint:   test_so[25]   (^) checked with leading edge of 'x'"
    returns "test_so[25]".
    """
    body = line.split('Endpoint:', 1)[1]
    return body.split()[0]


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(
            'Usage: python3 extract_neg_slack.py <input_report> <output_report>\n')
        return 2

    in_path, out_path = argv[1], argv[2]

    with open(in_path, 'r') as fh:
        lines = fh.readlines()

    # Split the raw lines into path blocks. Text before the first "Path N:"
    # line is the report header and is ignored for path extraction. Each block
    # is stored as [path_number, status, [raw_lines...]].
    blocks = []
    current = None
    for raw in lines:
        line = raw.rstrip('\n')
        match = PATH_HEADER_RE.match(line)
        if match:
            if current is not None:
                blocks.append(current)
            current = [int(match.group(1)), match.group(2).strip(), [line]]
        else:
            if current is not None:
                current[2].append(line)
    if current is not None:
        blocks.append(current)

    total = len(blocks)
    neg_blocks = []
    worst_slack = None
    worst_slack_str = None
    worst_endpoint = None

    for path_num, status, blines in blocks:
        slack_val = None
        slack_str = None
        endpoint = None
        for ln in blines:
            if 'Slack Time' in ln:
                slack_val = parse_number(ln)
                slack_str = ln.split()[-1]
            if ln.lstrip().startswith('Endpoint:'):
                endpoint = parse_endpoint(ln)
        if slack_val is not None and slack_val < 0.0:
            neg_blocks.append((path_num, status, blines))
            if worst_slack is None or slack_val < worst_slack:
                worst_slack = slack_val
                worst_slack_str = slack_str
                worst_endpoint = endpoint

    # Write every violating path block to the output report, preserving the
    # original report formatting for each block.
    block_texts = []
    for path_num, status, blines in neg_blocks:
        while blines and blines[-1].strip() == '':
            blines.pop()
        block_texts.append('\n'.join(blines))

    with open(out_path, 'w') as fh:
        if block_texts:
            fh.write('\n\n'.join(block_texts) + '\n')

    # Single-line statistics sent to stdout (used for scoring).
    sys.stdout.write(
        'TOTAL={} NEG={} WORST_SLACK={} WORST_ENDPOINT={}\n'.format(
            total,
            len(neg_blocks),
            worst_slack_str if worst_slack_str is not None else '',
            worst_endpoint if worst_endpoint is not None else ''))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))