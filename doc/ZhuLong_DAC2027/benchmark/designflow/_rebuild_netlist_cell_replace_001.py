#!/usr/bin/env python3
"""Rebuild NetlistCellReplace-001: consistent functional ports (S,R0,R1,Y),
variable power/cell/module names for anti-hardcoding.
"""
import json, os
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

def gen_netlist(mod, c2, c3, vcc, vss, vbp, vbn):
    return f'''// Verilog netlist for cell "{mod}" view "schematic"
`timescale 10ps/10ps
module {mod} (Y, S, R0, R1, {vcc}, {vbn}, {vbp}, {vss});
    output Y;
    input S;
    input R0;
    input R1;
    inout {vcc};
    inout {vbn};
    inout {vbp};
    inout {vss};
    wire nq;
    wire nr;
    {c2} g_set (.Y(nq), .A(S), .B(nr));
    {c3} g_rst (.Y(nr), .A(R0), .B(R1), .C(nq));
    assign Y = nq;
endmodule
module {c2} (Y, A, B);
    output Y; input A; input B;
    assign Y = ~(A & B);
endmodule
module {c3} (Y, A, B, C);
    output Y; input A; input B; input C;
    assign Y = ~(A & B & C);
endmodule
'''

def gen_simlib(latch, n2p, n3p, invp, vp, vs, vpp, vpn, extra=True):
    s = f'''`timescale 1ps/1ps
`celldefine
module {n2p} (Y, A, B, {vp}, {vs}, {vpp}, {vpn});
    output Y; input A; input B;
    inout {vp}; inout {vs}; inout {vpp}; inout {vpn};
    assign Y = ~(A & B);
endmodule
`endcelldefine
`celldefine
module {n3p} (Y, A, B, C, {vp}, {vs}, {vpp}, {vpn});
    output Y; input A; input B; input C;
    inout {vp}; inout {vs}; inout {vpp}; inout {vpn};
    assign Y = ~(A & B & C);
endmodule
`endcelldefine
`celldefine
module {invp} (Y, A, {vp}, {vs}, {vpp}, {vpn});
    output Y; input A;
    inout {vp}; inout {vs}; inout {vpp}; inout {vpn};
    assign Y = ~A;
endmodule
`endcelldefine
`celldefine
primitive {latch} (q, a, b);
    output q; input a, b; reg q;
    table
    // a b : q : q+
       0 ? : ? : 1 ;
       1 1 : ? : - ;
       1 0 : ? : 0 ;
    endtable
endprimitive
`endcelldefine
'''
    if extra:
        s += f'''`celldefine
module nor2p (Y, A, B, {vp}, {vs}, {vpp}, {vpn});
    output Y; input A; input B;
    inout {vp}; inout {vs}; inout {vpp}; inout {vpn};
    assign Y = ~(A | B);
endmodule
`endcelldefine
`celldefine
module oai21p (Y, A, B, C, {vp}, {vs}, {vpp}, {vpn});
    output Y; input A; input B; input C;
    inout {vp}; inout {vs}; inout {vpp}; inout {vpn};
    assign Y = ~((A & B) | C);
endmodule
`endcelldefine
'''
    return s

netA = gen_netlist("LatchTopA","my_nand2A","my_nand3A","vdda","gnda","vbpa","vbna")
simA = gen_simlib("nandrslatchA","nand2pA","nand3pA","invpA","vcc_","vss_","vbulkp_","vbulkn_")
netB = gen_netlist("RSLatch_B","NA2_B","NA3_B","pvdd","pgnd","psub","nsub")
simB = gen_simlib("rslatch_B","ND2P_B","ND3P_B","IVP_B","vpwr","vgnd","vpsub","vnsub")
netB2 = gen_netlist("LatchX_C2","XN2_C","XN3_C","VDDC","VSSC","VBPC","VBNC")
simB2 = gen_simlib("latch_C2","N2P_C","N3P_C","IV_C","pwr","gnd","psub","nsub",extra=False)

for fn,content in [("prompt.txt",PROMPT),("task_brief.md",TASK_BRIEF),
    ("netlist.v",netA),("simlib_base.sv",simA),
    ("hidden/hidden_netlist_B.v",netB),("hidden/hidden_simlib_B.sv",simB),
    ("hidden/hidden_netlist_B2.v",netB2),("hidden/hidden_simlib_B2.sv",simB2)]:
    with open(os.path.join(AST,fn),"w") as f: f.write(content)
manifest = {"hidden_inputs":["hidden_netlist_B.v","hidden_simlib_B.sv",
    "hidden_netlist_B2.v","hidden_simlib_B2.sv"],
    "note":"B/B2 replace A at judge time"}
with open(AST+"/hidden/hidden_manifest.json","w") as f: json.dump(manifest,f,indent=2)
print("Assets rebuilt.")
# quick check: verify B netlist cell names NOT in B simlib
import re
b_cells = set(re.findall(r'(\w+)\s+g_\w+\s*\(', netB))
sim_b_mods = set(re.findall(r'module\s+(\w+)', simB)) | set(re.findall(r'primitive\s+(\w+)', simB))
print("B netlist inst cells:", b_cells)
print("B simlib mods:", sim_b_mods)
print("Unknown (not in simlib):", b_cells - sim_b_mods)
