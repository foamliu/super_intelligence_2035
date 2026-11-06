#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-NetlistCellReplace-001 (schematic_netlist, A-faithful, B-grade synthesized).
A-faithful prompt = U#0 verbatim from trace 1791956671337_q3r6q (e0039602@10.129.8.136).
Task: replace unknown cells in a Verilog netlist (cross-coupled RS NAND latch my_nand2+my_nand3)
with simlib_base.sv physical cells (+ & merge for pure logic, power/bulk pins connected),
print replaced lines, verify truth table with hold state.
16 conditions a-p.
"""
import json, os, zipfile, io, hashlib, shutil, subprocess, sys, re, textwrap, struct

CASE = "EDA-Eval-DesignFlow-NetlistCellReplace-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = BENCH + "/assets/" + CASE
REF = BENCH + "/reference/" + CASE
NEG = REF + "/negative"
for d in (AST, AST+"/hidden", REF, NEG):
    os.makedirs(d, exist_ok=True)

PROMPT = '''请修改 netlist 文件。其中有些模块用到的 cell
在 simlib_base.sv 中不存在，无法直接读取，请结合 simlib_base.sv 把它们替换掉。

约束如下（务必严格遵守）：

1. 优先复用 simlib_base.sv 中【自带电源/衬底引脚】的物理单元积木

2. 分工规则（这是重点）：
   - 凡是有“延时/时序/驱动强度”等物理效应的部分，必须用库内物理单元实现，
     并把 vcc_/vss_/vbulkp_/vbulkn_ 等电源与衬底脚真实接进这些物理单元；
   - 凡是对输出没有延时、没有物理影响的纯逻辑输入合并，一律直接用
     位与 &（或 |、^ 等）逻辑表达式在这个物理单元的前端拼接完成，
     不要再把它们拆成单独的晶体管堆或单独的门级模块。

3. 不要下面这两种做法：
   - 不要用纯行为/无电源脚的 UDP 原语来形成单纯的逻辑电路，
     因为它无法承接 vcc/vss/bulk，电源腿会变成悬空摆设；
   - 尽量不要把每个 NAND 输入都做成独立的 pp/nn 晶体管串并联堆，除非没有模块可以实现对应功能
     那既啰嗦又违背第2条“无延时输入用 &”的规则。

4. 每个被替换的 cell，先用真值表和器件原理分析，再用 simlib_base.sv 里的
   物理单元 + & 组合式地复原出逻辑功能，并保持时序/保持行为一致。

5. 改写时保留原 cell 的所有参数与连接关系（电源脚、衬底脚、端口名都要保留）。

6. 输出要求：
   - 在对话窗口打印每处被替换的原始行和替换后的行；
   - 无须实际改写 netlist 文件；
   - 最后用真值表穷举（含保持态/上一值）验证替换前后等价。
'''

TASK_BRIEF = '''交付：Python 脚本 replace_cells.py，CLI: `replace_cells.py <netlist> <simlib>`。
stdout 先打印替换后完整网表（`// BEGIN_NET` / `// END_NET` 包裹），再打印替换前后对照行（`// REPLACEMENT` 标注），最后打印真值表验证结果（含保持态）。打包 outputs/submit.zip。
'''

# ---- parameterized netlist/simlib generator ----
def gen_netlist(mod_name, cell2, cell3, S_name, R0_name, R1_name,
                vcc, vss, vbp, vbn, fb_wire="nq", fb_wire2="nr", extra_comment=""):
    """Generate a Verilog netlist with a cross-coupled RS NAND latch.
    cell2 (my_nand2X): Y = ~(A & B)  -- set branch (S + feedback)
    cell3 (my_nand3X): Y = ~(A & B & C)  -- reset branch (R0, R1 + feedback)
    """
    return f'''// Verilog netlist for cell "{mod_name}" view "schematic"
// Language Version: 2001
`timescale 10ps/10ps
{extra_comment}

module {mod_name} (Y, {S_name}, {R0_name}, {R1_name}, {vcc}, {vbn}, {vbp}, {vss});

    output Y;
    input {S_name};
    input {R0_name};
    input {R1_name};
    inout {vcc};
    inout {vbn};
    inout {vbp};
    inout {vss};

    wire {fb_wire};
    wire {fb_wire2};

    {cell2} g_set (.Y({fb_wire}), .A({S_name}), .B({fb_wire2}));
    {cell3} g_rst (.Y({fb_wire2}), .A({R0_name}), .B({R1_name}), .C({fb_wire}));

    assign Y = {fb_wire};

endmodule

module {cell2} (Y, A, B);
    output Y;
    input A;
    input B;
    assign Y = ~(A & B);
endmodule

module {cell3} (Y, A, B, C);
    output Y;
    input A;
    input B;
    input C;
    assign Y = ~(A & B & C);
endmodule
'''

def gen_simlib(latch_name, nand2p_name, nand3p_name, invp_name,
               vcc_p, vss_p, vbp_p, vbn_p, extra_cells=True):
    """Generate simlib_base.sv with physical cells (power pins) + latch primitive."""
    s = f'''`timescale 1ps/1ps
// simlib_base.sv -- physical cells with power/bulk pins + sequential primitives

`celldefine
module {nand2p_name} (Y, A, B, {vcc_p}, {vss_p}, {vbp_p}, {vbn_p});
    output Y;
    input A;
    input B;
    inout {vcc_p};
    inout {vss_p};
    inout {vbp_p};
    inout {vbn_p};
    assign Y = ~(A & B);
endmodule
`endcelldefine

`celldefine
module {nand3p_name} (Y, A, B, C, {vcc_p}, {vss_p}, {vbp_p}, {vbn_p});
    output Y;
    input A;
    input B;
    input C;
    inout {vcc_p};
    inout {vss_p};
    inout {vbp_p};
    inout {vbn_p};
    assign Y = ~(A & B & C);
endmodule
`endcelldefine

`celldefine
module {invp_name} (Y, A, {vcc_p}, {vss_p}, {vbp_p}, {vbn_p});
    output Y;
    input A;
    inout {vcc_p};
    inout {vss_p};
    inout {vbp_p};
    inout {vbn_p};
    assign Y = ~A;
endmodule
`endcelldefine

`celldefine
primitive {latch_name} (q, a, b);
    output q;
    input a, b;
    reg q;
    table
    // a b : q : q+
       0 ? : ? : 1 ;
       1 1 : ? : - ;
       1 0 : ? : 0 ;
       1 x : 0 : 0 ;
       1 x : 1 : x ;
       1 x : x : x ;
       x 1 : 1 : 1 ;
       x 1 : 0 : x ;
       x 1 : x : x ;
       x 0 : ? : x ;
    endtable
endprimitive
`endcelldefine
'''
    if extra_cells:
        s += f'''
`celldefine
module nor2p (Y, A, B, {vcc_p}, {vss_p}, {vbp_p}, {vbn_p});
    output Y; input A; input B;
    inout {vcc_p}; inout {vss_p}; inout {vbp_p}; inout {vbn_p};
    assign Y = ~(A | B);
endmodule
`endcelldefine

`celldefine
module oai21p (Y, A, B, C, {vcc_p}, {vss_p}, {vbp_p}, {vbn_p});
    output Y; input A; input B; input C;
    inout {vcc_p}; inout {vss_p}; inout {vbp_p}; inout {vbn_p};
    assign Y = ~((A & B) | C);
endmodule
`endcelldefine
'''
    return s

# A assets
netA = gen_netlist("LatchTopA", "my_nand2A", "my_nand3A", "SetA", "RstA0", "RstA1",
                   "vdda", "gnda", "vbpa", "vbna")
simA = gen_simlib("nandrslatchA", "nand2pA", "nand3pA", "invpA", "vcc_", "vss_", "vbulkp_", "vbulkn_")

# B (hidden) -- different names, same paradigm, anti-hardcode
netB = gen_netlist("RSLatch_B", "NA2_B", "NA3_B", "Sb", "Rb0", "Rb1",
                   "pvdd", "pgnd", "psub", "nsub")
simB = gen_simlib("rslatch_B", "ND2P_B", "ND3P_B", "IVP_B", "vpwr", "vgnd", "vpsub", "vnsub")

# B2 (hidden) -- even more different (different R names, different power, fewer extra cells)
netB2 = gen_netlist("LatchX_C2", "XN2_C", "XN3_C", "SetC", "RzC0", "RzC1",
                    "VDDC", "VSSC", "VBPC", "VBNC")
simB2 = gen_simlib("latch_C2", "N2P_C", "N3P_C", "IV_C", "pwr", "gnd", "psub", "nsub", extra_cells=False)

# write A assets
with open(AST+"/prompt.txt","w") as f: f.write(PROMPT)
with open(AST+"/task_brief.md","w") as f: f.write(TASK_BRIEF)
with open(AST+"/netlist.v","w") as f: f.write(netA)
with open(AST+"/simlib_base.sv","w") as f: f.write(simA)
with open(AST+"/hidden/hidden_netlist_B.v","w") as f: f.write(netB)
with open(AST+"/hidden/hidden_simlib_B.sv","w") as f: f.write(simB)
with open(AST+"/hidden/hidden_netlist_B2.v","w") as f: f.write(netB2)
with open(AST+"/hidden/hidden_simlib_B2.sv","w") as f: f.write(simB2)
manifest = {"hidden_inputs": ["hidden_netlist_B.v","hidden_simlib_B.sv",
           "hidden_netlist_B2.v","hidden_simlib_B2.sv"],
           "note": "B/B2 replace A assets at judge time; check runs only on B/B2"}
with open(AST+"/hidden/hidden_manifest.json","w") as f: json.dump(manifest,f,indent=2)

print("Assets written to", AST)
print("A netlist cells: my_nand2A, my_nand3A (NOT in simA)")
print("B netlist cells: NA2_B, NA3_B (NOT in simB)")
print("B2 netlist cells: XN2_C, XN3_C (NOT in simB2)")
