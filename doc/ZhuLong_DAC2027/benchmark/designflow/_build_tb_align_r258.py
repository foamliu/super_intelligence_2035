#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-TbAlignReport-001 (digital, A-faithful, r258).

Trace: 1793069875156_c6xow / lorikx / hfeg0pkn001 / mc158 / digital.
USER#0 (verbatim): "请阅读rtl/文件夹内的修改记录markdown文件，以及最新的.v文件，
                    调整一下testbench，符合最新的修改要求"
Real product: tb_sp_sram.v adjusted v9.5 -> v9.6 (G1 rule: CRSxE edge no longer
clears storage array; only Q=X output pulse; array content preserved).

Deliverable = analyze_tb_alignment.py : a GENERIC script that reads
(modification_note.md, new_rtl.v, baseline_tb.v) per a manifest config and
emits a structured JSON report characterizing the CR-edge behavior change and
the testbench checks that need alignment. Judge runs the candidate script on
hidden B (relabeled variant) and B' (structurally-different variant); a correct
solution derives every field from the input files and contains NO A-specific
literals.
"""
import json, os, shutil, subprocess, sys, zipfile, hashlib, re, py_compile

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-TbAlignReport-001"
REF = os.path.join(REPO, "reference", CID)
AST = os.path.join(REPO, "assets", CID)
for d in [REF, AST, os.path.join(AST, "hidden"), os.path.join(REF, "negative")]:
    os.makedirs(d, exist_ok=True)

USER0 = ('<user_input mode="act">请阅读rtl/文件夹内的修改记录markdown文件，'
         '以及最新的.v文件，调整一下testbench，符合最新的修改要求</user_input>')

# ============================ A inputs (faithful, compact) ===================
# G1 golden rule, CRSLE/CRSRE (left/right CR enable), sram_sp, tb v9.5 -> v9.6.

A_NOTE = """# SRAM 行为模型列冗余(CR)语义对齐 - 迁移指南 (G1 黄金规则)

> 自包含文档。本模型 = 1-port SRAM 行为模型 `sram_sp`（Verilog, VCS 仿真）。
> CR 引脚：`CRSLE/CRSLA`（左半）、`CRSRE/CRSRA`（右半）= 使能 + 缺陷组地址。

## 0. 结论速览（G1 黄金规则，以 REF 为准）

1. CRSxE（repair store）脉冲**不破坏阵列内容** - 只重新配置列映射；
2. CR 操作周期 Q 输出 X（输出扰动脉冲，持续到下一次正常读清除）；
3. repair-ON 写：数据按移位映射写入，缺陷组物理列强制写 X；
4. repair-OFF 读：直访物理列，缺陷组列自然读出 X；
5. 比对与错误记录必须用 4-state logic，X 不得折叠成 0。

## 1. 旧行为（需迁移走的缺陷语义）

- CRSLE/CRSRE 任意有效边沿 -> 清空整个存储阵列（逐地址写 X）；
- 下一拍 sram_op_exec 消费 pending 时再次 mem_init(1'bx)；
- TB 据此写检查："mem=X after CRSxE"、"mem not X after CRSxE" 等。

## 2. 新行为（G1 黄金规则）

- CRSLE/CRSRE 边沿 -> **仅产生 Q=X 输出扰动脉冲**（持续到下次正常读）；
- 阵列内容逐位保持，**不再清空**；
- pending 吸收机制保留；x/z hazard 分支保留。

## 3. TB 迁移要求（golden rule G1）

- 移除所有"mem=X / mem not X after CRSxE"类检查（依赖旧行为，新 RTL 下必然 FAIL）；
- 新增三类 G1 检查任务：阵列快照、Q=X 脉冲检查、阵列逐位保持检查；
- 影响测试：14b、14b_cd、Test 17 H3；
- 版本号 v9.5 -> v9.6，更新 changelog。
"""

A_RTL = """// sram_sp.v  (G1 fixed behavior)
// 1-port SRAM behavior model with column redundancy (CR).
module sram_sp #(parameter DW=8, parameter AW=10) (
    input wire clk, input wire rst_n,
    input wire CRSLE, input wire [1:0] CRSLA,   // left CR enable / group addr
    input wire CRSRE, input wire [1:0] CRSRA,   // right CR enable / group addr
    input wire wen, input wire ren,
    input wire [AW-1:0] addr, input wire [DW-1:0] din,
    output reg [DW-1:0] Q
);
    reg [DW-1:0] mem [0:(1<<AW)-1];
    reg cr_corrupt_pending;
    reg Q_force_x;

    // G1 golden rule: CRSxE edge produces Q=X pulse, array content preserved.
    // (NO mem clear on edge -- the old mem_init(1'bx) on edge was removed.)
    always @(posedge clk) begin
        if (!rst_n) begin
            cr_corrupt_pending <= 1'b0;
            Q_force_x <= 1'b0;
        end else begin
            // CRSLE / CRSRE rising edge: pulse Q=X, keep array intact
            if ((CRSLE && !crsle_buf) || (CRSRE && !crsre_buf)) begin
                Q_force_x <= 1'b1;       // Q=X output corruption pulse
                cr_corrupt_pending <= 1'b1;
                // array NOT cleared -- mem[*] keeps its value (G1)
            end
            // normal read clears the X pulse
            if (ren && !Q_force_x) Q_force_x <= 1'b0;
        end
    end

    // read path: Q=X during CR corrupt pulse, else mem[addr]
    always @(*) begin
        if (Q_force_x) Q = {DW{1'bx}};
        else           Q = mem[addr];
    end
endmodule
"""

A_TB_BASELINE = """// tb_sram_sp.sv  (baseline v9.5 - depends on OLD CR-clear behavior)
// Version: 9.5
// Changelog (v9.5): initial CR-clear-aware checks.
`timescale 1ns/1ps
module tb_sram_sp;
    reg clk, rst_n, CRSLE, CRSRE, wen, ren;
    reg [1:0] CRSLA, CRSRA;
    reg [9:0] addr;
    reg [7:0] din;
    wire [7:0] Q;

    sram_sp dut(.clk(clk),.rst_n(rst_n),.CRSLE(CRSLE),.CRSLA(CRSLA),
                .CRSRE(CRSRE),.CRSRA(CRSRA),.wen(wen),.ren(ren),
                .addr(addr),.din(din),.Q(Q));

    task check_mem; input [9:0] a; begin
        if (dut.mem[a] !== 8'h00) $display("FAIL mem[%0d]", a);
    end endtask

    // OLD checks that depend on CRSxE clearing the array (must be removed per G1)
    // Test 14b
    initial begin
        // CRSLE rise: OLD expects array cleared to X
        if (dut.mem[addr] === 8'hxx) $display("PASS mem=X after CRSLE rise");
        else                          $display("FAIL mem not X after CRSLE rise");
        // CRSLE disable variant
        if (dut.mem[addr] === 8'hxx) $display("PASS mem=X after CRSLE?");
        else                          $display("FAIL mem not X after CRSLE?");
        // CRSRE rise
        if (dut.mem[addr] === 8'hxx) $display("PASS mem=X after CRSRE rise");
        else                          $display("FAIL mem not X after CRSRE rise");
        // CRSRE disable variant
        if (dut.mem[addr] === 8'hxx) $display("PASS mem=X after CRSRE?");
        else                          $display("FAIL mem not X after CRSRE?");
        // Test 17 H3: OLD expects array cleared after CRSxA
        if (dut.mem[addr] === 8'hxx) $display("PASS H3: mem=X after CRSxA=x");
        else                          $display("FAIL H3: mem not X after CRSxA=x");
    end
endmodule
"""

# Gold report for A (the facts a correct analyzer derives from A's inputs)
A_GOLD = {
    "design_name": "sram_sp",
    "tb_name": "tb_sram_sp",
    "version_old": "9.5",
    "note_rule": "G1",
    "cr_signals": ["CRSLE", "CRSRE"],
    "old_check_count": 5,
    "old_check_labels": [
        "mem=X after CRSLE rise", "mem not X after CRSLE rise",
        "mem=X after CRSRE rise", "mem not X after CRSRE rise",
        "H3: mem not X after CRSxA=x",
    ],
    "rtl_clears_mem_on_cr_edge": False,
    "rtl_qx_pulse_on_cr_edge": True,
    "needs_alignment": True,
    "summary": ("CRSxE edges no longer clear storage array; Q=X output pulse, "
                "array content preserved; testbench mem=X/not-X-after-CRSxE checks "
                "must be removed and replaced with Q=X pulse + array-unchanged checks."),
}

# ===================== B = relabelled A (anti-hardcode) ======================
# consistent relabel across note + rtl + baseline_tb; same structure/booleans.
REMAP = [
    ("CRSLE", "CRSENL"),
    ("CRSRE", "CRSENR"),
    ("CRSLA", "CRANL"),
    ("CRSRA", "CRANR"),
    ("G1", "G3"),
    ("9.5", "8.5"),
    ("v9.5", "v8.5"),
    ("sram_sp", "sram_sp"),     # keep module name (cross-checked)
    ("tb_sram_sp", "tb_sram_sp"),
]

def relabel(s, m=REMAP):
    for a, b in m:
        s = s.replace(a, b)
    return s

B_NOTE = relabel(A_NOTE)
B_RTL = relabel(A_RTL)
B_TB = relabel(A_TB_BASELINE)
B_GOLD = {
    "design_name": "sram_sp",
    "tb_name": "tb_sram_sp",
    "version_old": "8.5",
    "note_rule": "G3",
    "cr_signals": ["CRSENL", "CRSENR"],
    "old_check_count": 5,
    "old_check_labels": [
        "mem=X after CRSENL rise", "mem not X after CRSENL rise",
        "mem=X after CRSENR rise", "mem not X after CRSENR rise",
        "H3: mem not X after CRSxA=x",
    ],
    "rtl_clears_mem_on_cr_edge": False,
    "rtl_qx_pulse_on_cr_edge": True,
    "needs_alignment": True,
    "summary": ("CRSxE edges no longer clear storage array; Q=X output pulse, "
                "array content preserved."),
}

# ===================== B' = structurally different (cross-input guard) =======
# Scenario: RTL STILL clears mem on CR edge (no fix) -> needs_alignment False,
# old_check_count 0 (TB already aligned to clearing behavior).
BP_NOTE = """# SRAM 行为模型 CR 语义记录 (G7 - 已对齐, 无需迁移)

> 本模型 = 1-port SRAM `sram_sp`。CR 引脚 CRSLE/CRSRE。
> G7 规则：CRSxE 边沿清空存储阵列（保持旧行为，已确认正确，无需迁移）。
> TB 已据此行为编写检查，当前 RTL 与 TB 语义一致，无需要对齐项。
"""
BP_RTL = """// sram_sp.v  (G7 - clears array on CR edge, OLD behavior retained)
module sram_sp #(parameter DW=8, parameter AW=10) (
    input wire clk, input wire rst_n,
    input wire CRSLE, input wire [1:0] CRSLA,
    input wire CRSRE, input wire [1:0] CRSRA,
    input wire wen, input wire ren,
    input wire [AW-1:0] addr, input wire [DW-1:0] din,
    output reg [DW-1:0] Q
);
    reg [DW-1:0] mem [0:(1<<AW)-1];
    always @(posedge clk) begin
        if (!rst_n) begin end
        else begin
            // CRSLE/CRSRE edge: CLEAR whole array (OLD behavior, G7 retained)
            if (CRSLE || CRSRE) begin
                // mem_init: clear array to X on CR edge
                for (integer i = 0; i < (1<<AW); i = i+1) mem_init(mem[i]);
            end
            if (ren) Q = mem[addr];
        end
    end
    task mem_init; inout [7:0] m; begin m = 8'hxx; end endtask
endmodule
"""
BP_TB = """// tb_sram_sp.sv (v7.2 - aligned to G7 clearing behavior)
// Version: 7.2
`timescale 1ns/1ps
module tb_sram_sp;
    reg clk, rst_n, CRSLE, CRSRE, wen, ren;
    reg [9:0] addr; reg [7:0] din; wire [7:0] Q;
    sram_sp dut(.clk(clk),.rst_n(rst_n),.CRSLE(CRSLE),.CRSRE(CRSRE),
                .wen(wen),.ren(ren),.addr(addr),.din(din),.Q(Q));
    initial begin
        // no mem=X-after-CRSxE checks here -- TB expects clearing, aligned
        if (dut.mem[addr] === 8'hxx) $display("PASS cleared after CRSxE");
    end
endmodule
"""
BP_GOLD = {
    "design_name": "sram_sp",
    "tb_name": "tb_sram_sp",
    "version_old": "7.2",
    "note_rule": "G7",
    "cr_signals": ["CRSLE", "CRSRE"],
    "old_check_count": 0,
    "old_check_labels": [],
    "rtl_clears_mem_on_cr_edge": True,
    "rtl_qx_pulse_on_cr_edge": False,
    "needs_alignment": False,
    "summary": "RTL retains CR-edge array clear (G7); TB already aligned; no migration needed.",
}

# ============================ write A assets =================================
def w(path, content):
    with open(path, "w") as f:
        f.write(content)

w(os.path.join(AST, "prompt.txt"), USER0 + "\n")
w(os.path.join(AST, "task_brief.md"),
  "交付接口：submit.zip 内含 analyze_tb_alignment.py（Python3 脚本，无第三方依赖）。\n"
  "脚本读取同目录 manifest.json（指向 modification_note.md / new_rtl.v / baseline_tb.v），"
  "在 stdout 输出结构化 JSON 报告并 exit 0。\n")
w(os.path.join(AST, "modification_note.md"), A_NOTE)
w(os.path.join(AST, "new_rtl.v"), A_RTL)
w(os.path.join(AST, "baseline_tb.v"), A_TB_BASELINE)
w(os.path.join(AST, "config_a.json"), json.dumps({
    "manifest": {"modification_note": "modification_note.md",
                 "new_rtl": "new_rtl.v",
                 "baseline_tb": "baseline_tb.v"},
}, ensure_ascii=False, indent=2))

# hidden B / B'
w(os.path.join(AST, "hidden", "B_modification_note.md"), B_NOTE)
w(os.path.join(AST, "hidden", "B_new_rtl.v"), B_RTL)
w(os.path.join(AST, "hidden", "B_baseline_tb.v"), B_TB)
w(os.path.join(AST, "hidden", "Bp_modification_note.md"), BP_NOTE)
w(os.path.join(AST, "hidden", "Bp_new_rtl.v"), BP_RTL)
w(os.path.join(AST, "hidden", "Bp_baseline_tb.v"), BP_TB)
w(os.path.join(AST, "hidden", "hidden_manifest.json"), json.dumps({
    "B": {"files": ["B_modification_note.md", "B_new_rtl.v", "B_baseline_tb.v"],
          "manifest": {"modification_note": "B_modification_note.md",
                       "new_rtl": "B_new_rtl.v",
                       "baseline_tb": "B_baseline_tb.v"},
          "expected": B_GOLD},
    "Bp": {"files": ["Bp_modification_note.md", "Bp_new_rtl.v", "Bp_baseline_tb.v"],
           "manifest": {"modification_note": "Bp_modification_note.md",
                        "new_rtl": "Bp_new_rtl.v",
                        "baseline_tb": "Bp_baseline_tb.v"},
           "expected": BP_GOLD},
}, ensure_ascii=False, indent=2))

print("assets written:", CID)
print("A_GOLD old_check_count=", A_GOLD["old_check_count"],
      "B cr_signals=", B_GOLD["cr_signals"],
      "Bp clears=", BP_GOLD["rtl_clears_mem_on_cr_edge"])
