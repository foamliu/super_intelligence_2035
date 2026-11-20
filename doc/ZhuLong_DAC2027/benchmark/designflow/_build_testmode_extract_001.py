# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-TestModeExtract-001 (schematic_netlist, B-synthesized L1).

Trace: 1791973347667_tx5s5 (e04201 / hfeg0pkn002 / mc46)
User intent (U#10): "根据netlist文件，提取test mode的功能，主要包含test mode作用机理，test mode调整大小"
Assistant produced: scan_testmode.py scanning Verilog netlist for test-mode identifiers,
classifying (test/str/size), extracting module defs.

Facet: gen_testmode_report.py --netlist <v> --outdir <dir> -> report.md + modules.json
16 conditions a-p.
"""
import os, json, zipfile, subprocess, sys, shutil, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-TestModeExtract-001"
AST = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)
HID = os.path.join(AST, "hidden")
for d in (AST, REF, HID):
    os.makedirs(d, exist_ok=True)

# ---------------- Verilog netlists ----------------
NETLIST_A = """// Verilog netlist - DDR5 DRAM top, test-mode extraction target (A)
module SCmosCkeRstCtrl(clk, rst_n, testmode, testmodeN, cke, cke_out);
  input clk, rst_n, testmode, testmodeN;
  input cke;
  output cke_out;
  wire sel_n;
  AOI22 u_sel(.a(testmode), .b(clk), .c(testmodeN), .d(rst_n), .y(sel_n));
  testmode_buf u_buf(.in(cke), .out(cke_out));
endmodule

module testmode_buf(in, out);
  input in;
  output out;
  wire out;
  assign out = in;
endmodule

module DL_4PGenTestMode(clk, testmode, pgen_out);
  input clk, testmode;
  output [3:0] pgen_out;
  wire [3:0] pgen_out;
  INV u0(.a(testmode), .y(pgen_out[0]));
  INV u1(.a(clk), .y(pgen_out[1]));
  assign pgen_out[2] = testmode ? 1'bx : 1'b0;
  assign pgen_out[3] = clk;
endmodule

module T_CMLeft_L1(clk, VwlpRDBITestModeEn, rd_data);
  input clk, VwlpRDBITestModeEn;
  output rd_data;
  wire sel;
  AOI22 u_mux(.a(VwlpRDBITestModeEn), .b(clk), .c(~VwlpRDBITestModeEn), .d(clk), .y(sel));
  assign rd_data = sel;
endmodule

module str_pad_driver(in, out, str_mode);
  input in, str_mode;
  output out;
  wire out;
  assign out = in;
endmodule

module size_ctrl(a, b, y);
  input a, b;
  output y;
  wire y;
  assign y = a & b;
endmodule

module plain_filler(a, y);
  input a;
  output y;
  wire y;
  assign y = a;
endmodule
"""

NETLIST_B = """// Verilog netlist - LPDDR4 PHY, test-mode extraction target (hidden B)
module TmRstCtrl(clk, rst_n, tm_en, tm_en_n, rst_out);
  input clk, rst_n, tm_en, tm_en_n;
  output rst_out;
  wire sel;
  NAND2 u_g(.a(tm_en), .b(clk), .y(sel));
  TmBuf u_b(.in(rst_n), .out(rst_out));
endmodule

module TmBuf(in, out);
  input in;
  output out;
  wire out;
  assign out = in;
endmodule

module DL_PGenTm(clk, tm_en, pgen);
  input clk, tm_en;
  output [2:0] pgen;
  wire [2:0] pgen;
  INV u0(.a(tm_en), .y(pgen[0]));
  INV u1(.a(clk), .y(pgen[1]));
  assign pgen[2] = tm_en;
endmodule

module T_ColRight_L2(clk, VwlTm_en, sense_out);
  input clk, VwlTm_en;
  output sense_out;
  wire mux_sel;
  NAND2 u_m(.a(VwlTm_en), .b(clk), .y(mux_sel));
  assign sense_out = mux_sel;
endmodule

module str_clk_buf(in, out, str_sel);
  input in, str_sel;
  output out;
  wire out;
  assign out = in;
endmodule

module size_div(a, b, q);
  input a, b;
  output q;
  wire q;
  assign q = a ^ b;
endmodule

module filler_plain(x, y);
  input x;
  output y;
  wire y;
  assign y = x;
endmodule
"""

# B2: single test-mode module, shallow, different style (test_mode with underscore)
NETLIST_B2 = """// Verilog netlist - simple serializer, single test_mode module (hidden B2)
module SerDesTopTx(clk, test_mode, data_in, tx_p);
  input clk, test_mode;
  input [1:0] data_in;
  output tx_p;
  wire tx_p;
  assign tx_p = test_mode ? ~data_in[0] : data_in[1];
endmodule

module plain_buf(a, y);
  input a;
  output y;
  wire y;
  assign y = a;
endmodule
"""

with open(os.path.join(AST, "netlist_A.v"), "w") as f:
    f.write(NETLIST_A)
with open(os.path.join(HID, "netlist_B.v"), "w") as f:
    f.write(NETLIST_B)
with open(os.path.join(HID, "netlist_B2.v"), "w") as f:
    f.write(NETLIST_B2)

# hidden_manifest.json
with open(os.path.join(HID, "hidden_manifest.json"), "w") as f:
    json.dump({"B": "netlist_B.v", "B2": "netlist_B2.v",
               "note": "hidden inputs not visible to SUT; check.py runs only on these"}, f, indent=2)

# task_brief.md (<=3 lines, interface only, no "what to do")
with open(os.path.join(AST, "task_brief.md"), "w") as f:
    f.write(
        "交付接口：生成器 `gen_testmode_report.py`，读 `--netlist <verilog.v> --outdir <dir>`，"
        "在 `<dir>/report.md` + `<dir>/modules.json` 写出 test mode 分析报告与结构化清单。\n"
        "提交：把 `gen_testmode_report.py` 打包成 `outputs/submit.zip`。\n"
        "判定：独立进程在 hidden netlist_B/netlist_B2 上真跑生成器，校验模块清单 + 标识符分类 + 模块定义抽取 + 跨输入 + 确定性。\n"
    )

# prompt.txt (real scenario, trace-faithful U#10 + context, A netlist referenced)
with open(os.path.join(AST, "prompt.txt"), "w") as f:
    f.write(
        "下面是一个 DDR5 DRAM 顶层 Verilog 网表（assets/netlist_A.v），是 Cadence 导出的仿真网表。"
        "要从这份网表里**提取 test mode 的功能**，主要包含两块：\n"
        "  ① test mode 的**作用机理**（哪些模块带 testmode 端口 / test mode 使能信号，它们内部用什么选择器或逻辑把 test mode 切进来）；\n"
        "  ② test mode 的**调整大小**（drive strength / size 调整相关的标识符）。\n\n"
        "背景：这是 DV（design verification）流程里的一步——网表很大（百万行级），直接人工 grep 不现实，"
        "需要一个脚本自动扫出所有 test-mode 相关的模块、把它们内部的 test/str/size 标识符分类计数、"
        "再把带 test mode 的模块的完整定义抽出来，方便后续做 test mode 功能审查与覆盖。"
        "真实流程在 .75 上对 `/rundata/.../netlist` 跑 python 扫描脚本，这里改成「读 Verilog 网表文本 → "
        "扫 test mode 标识符 + 分类计数 + 抽模块定义 → 写报告 + 清单」的离线复刻。\n\n"
        "交付：写一个生成器 `gen_testmode_report.py`，读 `--netlist <verilog.v> --outdir <dir>`，在 `<dir>` 下产出：\n\n"
        "1. `modules.json` —— 结构化清单，顶层键：\n"
        "   - `netlist`：输入网表文件名（basename）\n"
        "   - `test_modules`：带 test-mode 标识符的模块列表，每项 `{name, match_count, first_line}`，"
        "`match_count` 是该模块体内 test 类标识符出现次数，`first_line` 是该模块 `module` 关键字所在行号（1-based）\n"
        "   - `identifiers`：`{\"test\": [...], \"str\": [...], \"size\": [...]}`，三类标识符去重排序后的列表。"
        "分类规则：对每个模块体内的所有标识符 token（`[A-Za-z_][A-Za-z0-9_]*`），"
        "`test` 类 = 含子串 \"test\" 或 \"testmode\" 或 \"tm_en\"（大小写不敏感）；"
        "`str` 类 = 含子串 \"str\"；`size` 类 = 含子串 \"size\" 或 \"siz\"。一个 token 可同属多类。\n"
        "   - `module_defs`：dict，键 = test_modules 的模块名，值 = 该模块完整原文（从 `module <name>` 行到 `endmodule` 行，含两端）\n"
        "   - `summary`：`{n_modules, n_test_modules, n_test_ids, n_str_ids, n_size_ids}`（模块总数 / test 模块数 / 三类标识符去重计数）\n"
        "2. `report.md` —— 人类可读报告，含三个二级标题节：`## Test Mode Modules`、`## Identifier Classification`、`## Module Definitions`，"
        "分别列出 test 模块表、标识符分类计数、各模块定义片段。\n\n"
        "解析要求：\n"
        "- `module <name>(<ports>);` 起头、`endmodule` 结尾；模块名取 `module` 后第一个 token\n"
        "- 标识符 token 用 `re.findall(r'[A-Za-z_][A-Za-z0-9_]*', body)` 抽，分类按上面的子串规则\n"
        "- `match_count` = 该模块体内命中 `test` 类的 token 出现总次数（含重复）\n"
        "- `first_line` = 模块 `module` 关键字所在行号（整个文件 1-based）\n\n"
        "hidden 输入会换一个完全不同的网表（不同模块名 / 不同 test mode 信号名 / 不同 str/size 标识符 / 不同模块数），"
        "以及一个**只有单个 test mode 模块、很浅**的网表，所以不要硬编码 `SCmosCkeRstCtrl` / `DL_4PGenTestMode` / "
        "`VwlpRDBITestModeEn` / `testmode` 等 A 的任何细节。\n\n"
        "把 `gen_testmode_report.py` 打包进 `outputs/submit.zip` 提交。\n"
    )

# ---------------- Reference generator ----------------
REF_GEN = r'''# -*- coding: utf-8 -*-
"""Reference generator for TestModeExtract-001: scan Verilog netlist for test-mode
identifiers, classify (test/str/size), extract module definitions, emit report."""
import re, os, sys, json, argparse

MODULE_RE = re.compile(r'^\s*module\s+(\w+)\s*\(', re.IGNORECASE)
TOKEN_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')

def classify(token):
    t = token.lower()
 cats = []
    if 'test' in t or 'testmode' in t or 'tm_en' in t:
        cats.append('test')
    if 'str' in t:
        cats.append('str')
    if 'size' in t or 'siz' in t:
        cats.append('size')
    return cats

def parse_netlist(text):
    lines = text.splitlines()
    modules = []  # list of {name, start, end, body}
    i = 0
    n = len(lines)
    while i < n:
        m = MODULE_RE.match(lines[i])
        if m:
            name = m.group(1)
            start = i
            j = i
            depth = 0
            while j < n:
                if re.match(r'^\s*module\s+\w+', lines[j], re.IGNORECASE):
                    depth += 1
                if re.match(r'^\s*endmodule\b', lines[j], re.IGNORECASE):
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            end = j
            body = "\n".join(lines[start:end+1])
            modules.append({'name': name, 'start': start, 'end': end, 'body': body})
            i = end + 1
        else:
            i += 1
    return modules

def analyze(text):
    modules = parse_netlist(text)
    test_ids, str_ids, size_ids = set(), set(), set()
    test_modules = []
    module_defs = {}
    for mod in modules:
        body = mod['body']
        toks = TOKEN_RE.findall(body)
        test_count = 0
        for tk in toks:
            cats = classify(tk)
            if 'test' in cats:
                test_count += 1
                test_ids.add(tk)
            if 'str' in cats:
                str_ids.add(tk)
            if 'size' in cats:
                size_ids.add(tk)
        if test_count > 0:
            test_modules.append({'name': mod['name'],
                                 'match_count': test_count,
                                 'first_line': mod['start'] + 1})
            module_defs[mod['name']] = mod['body']
    summary = {'n_modules': len(modules),
               'n_test_modules': len(test_modules),
               'n_test_ids': len(test_ids),
               'n_str_ids': len(str_ids),
               'n_size_ids': len(size_ids)}
    return {'test_modules': test_modules,
            'identifiers': {'test': sorted(test_ids), 'str': sorted(str_ids), 'size': sorted(size_ids)},
            'module_defs': module_defs,
            'summary': summary}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--netlist', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args()
    with open(args.netlist, errors='replace') as f:
        text = f.read()
    res = analyze(text)
    os.makedirs(args.outdir, exist_ok=True)
    out = {'netlist': os.path.basename(args.netlist)}
    out.update(res)
    with open(os.path.join(args.outdir, 'modules.json'), 'w') as f:
        json.dump(out, f, indent=2)
    # report.md
    r = []
    r.append('# Test Mode Extraction Report')
    r.append('')
    r.append('Source netlist: `%s`' % out['netlist'])
    r.append('')
    r.append('## Test Mode Modules')
    r.append('')
    r.append('| Module | test matches | first line |')
    r.append('|--------|-------------:|-----------:|')
    for tm in res['test_modules']:
        r.append('| `%s` | %d | %d |' % (tm['name'], tm['match_count'], tm['first_line']))
    r.append('')
    r.append('## Identifier Classification')
    r.append('')
    ids = res['identifiers']
    r.append('- test: %d identifiers' % len(ids['test']))
    r.append('- str: %d identifiers' % len(ids['str']))
    r.append('- size: %d identifiers' % len(ids['size']))
    r.append('')
    r.append('## Module Definitions')
    r.append('')
    for name, body in res['module_defs'].items():
        r.append('### %s' % name)
        r.append('```verilog')
        r.append(body)
        r.append('```')
        r.append('')
    with open(os.path.join(args.outdir, 'report.md'), 'w') as f:
        f.write("\n".join(r))

if __name__ == '__main__':
    main()
'''
# fix the typo (cats = [] indentation)
REF_GEN = REF_GEN.replace(" cats = []", "    cats = []")
with open(os.path.join(REF, "gen_testmode_report_ref.py"), "w") as f:
    f.write(REF_GEN)

print("wrote assets + ref gen")
# quick sanity: run ref on A
import importlib.util
spec = importlib.util.spec_from_file_location("refgen", os.path.join(REF, "gen_testmode_report_ref.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
resA = mod.analyze(NETLIST_A)
print("A test_modules:", [m['name'] for m in resA['test_modules']])
print("A identifiers:", {k: len(v) for k,v in resA['identifiers'].items()})
print("A summary:", resA['summary'])
resB = mod.analyze(NETLIST_B)
print("B test_modules:", [m['name'] for m in resB['test_modules']])
print("B identifiers:", {k: len(v) for k,v in resB['identifiers'].items()})
print("B summary:", resB['summary'])
resB2 = mod.analyze(NETLIST_B2)
print("B2 test_modules:", [m['name'] for m in resB2['test_modules']])
print("B2 summary:", resB2['summary'])
