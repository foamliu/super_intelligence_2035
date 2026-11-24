#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""synth_vcd_demo.py -- P4 合成波形数据 minimal demo.

演示「Verilog testbench -> VCD -> 波形 PNG -> 可验证 Q&A」全链路。

由于 .17 无 root 权限安装 iverilog，本 demo 用纯 Python：
  1. 生成 Verilog RTL + testbench 模板（展示 EDA 工具链输入）
  2. 用 Python 模拟仿真器输出标准 IEEE 1364 VCD 文件
  3. 纯 Python VCD 解析器提取信号变化沿
  4. PIL 渲染波形 PNG（带网格，VLM 可数格读数）
  5. 从 VCD 参数直接计算 ground-truth 答案（非 LLM 生成，反作弊）

作者: vision wake#1714 · P4 合成波形数据调研
"""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

VERILOG_COUNTER = """\
// synth_vcd_demo: clock divider + counter
// Compile: iverilog -o sim.vvp tb_counter.v counter.v && vvp sim.vvp
module counter(
    input  wire       clk,
    input  wire       rst_n,
    output reg [3:0]  count,
    output wire       clk_div2
);
    assign clk_div2 = count[0];
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) count <= 4'b0000;
        else        count <= count + 1'b1;
    end
endmodule
"""

VERILOG_TESTBENCH = """\
`timescale 1ns/1ps
module tb_counter;
    reg        clk;  reg        rst_n;
    wire [3:0] count; wire       clk_div2;
    counter dut(.clk(clk),.rst_n(rst_n),.count(count),.clk_div2(clk_div2));
    initial begin
        $dumpfile("counter.vcd"); $dumpvars(0, tb_counter);
        clk=0; rst_n=0; #20 rst_n=1; #500 $finish;
    end
    always #10 clk = ~clk;  // 100MHz, period=20ns
endmodule
"""

# ========================================================================== #
#  2. VCD 生成器（模拟 iverilog + vvp 的 VCD 输出，IEEE 1364 格式）
# ========================================================================== #

def generate_vcd(out_path, clk_period_ns=20, sim_ns=520, rst_release_ns=20,
                 counter_width=4):
    """生成标准 IEEE 1364 VCD 文件，模拟 counter 模块行为。

    返回 dict: 仿真参数（用于后续 GT 答案计算，反作弊）。
    """
    L = []
    L.append("$date\n    Mon Nov 24 14:00:00 2026\n$end")
    L.append("$version\n    synth_vcd_demo v1.0\n$end")
    L.append("$timescale 1ns $end")
    L.append("$scope module tb_counter $end")
    L.append("$var wire 1 ! clk $end")
    L.append('$var wire 1 " rst_n $end')
    L.append("$var wire %d # count[%d:0] $end" % (counter_width, counter_width-1))
    L.append("$var wire 1 $ clk_div2 $end")
    L.append("$upscope $end")
    L.append("$enddefinitions $end")
    L.append("$dumpvars")
    L.append("0!")
    L.append('0"')
    L.append("b" + "0"*counter_width + " #")
    L.append("0$")
    L.append("$end")

    clk_val = 0; rst_val = 0; count_val = 0
    half = clk_period_ns // 2
    for t in range(0, sim_ns + 1, half):
        changes = []
        clk_val = 1 - clk_val
        changes.append("%d!" % clk_val)
        if t >= rst_release_ns and rst_val == 0:
            rst_val = 1; changes.append('1"')
        if clk_val == 1 and rst_val == 1:
            count_val = (count_val + 1) % (2 ** counter_width)
            changes.append("b" + format(count_val, "0{}b".format(counter_width)) + " #")
            changes.append("%d$" % (count_val & 1))
        L.append("#%d" % t)
        L.extend(changes)
    L.append("#%d" % sim_ns)
    L.append("$end")

    with open(out_path, "w") as f:
        f.write("\n".join(L) + "\n")

    return {
        "clk_period_ns": clk_period_ns, "sim_ns": sim_ns,
        "rst_release_ns": rst_release_ns, "counter_width": counter_width,
        "half_period_ns": half, "clk_freq_mhz": 1000.0 / clk_period_ns,
        "total_clk_cycles": sim_ns // clk_period_ns,
        "active_clk_cycles": (sim_ns - rst_release_ns) // clk_period_ns,
        "final_count": count_val,
    }

# ========================================================================== #
#  3. VCD 解析器（纯 Python，无外部依赖）
# ========================================================================== #

def parse_vcd(vcd_path):
    """解析 VCD 文件，返回 {signal_name: [(time, value), ...]}。"""
    signals = {}; timeline = {}; current_time = 0; in_header = True
    with open(vcd_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("$var"):
                parts = line.split()
                vid, name = parts[3], parts[4]
                signals[vid] = name; timeline[vid] = []
            elif line.startswith("$enddefinitions"):
                in_header = False
            elif line.startswith("#"):
                current_time = int(line[1:])
            elif not in_header and not line.startswith("$"):
                if line[0] in ("b", "B"):
                    parts = line.split()
                    val, vid = parts[0][1:], parts[1]
                    if vid in timeline:
                        timeline[vid].append((current_time, val))
                else:
                    val, vid = line[0], line[1:]
                    if vid in timeline:
                        timeline[vid].append((current_time, val))
    result = {}
    for vid, name in signals.items():
        result[name] = timeline.get(vid, [])
    return result

# ========================================================================== #
#  4. 波形 PNG 渲染器（PIL，带网格，VLM 可数格读数）
# ========================================================================== #

def render_waveform_png(signals_timeline, params, out_path,
                        width=640, height=400):
    """渲染数字波形图为 PNG（带网格、信号名、时间轴）。"""
    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    ml, mr, mt, mb = 80, 20, 30, 40
    plot_w = width - ml - mr
    plot_h = height - mt - mb
    sim_ns = params["sim_ns"]
    sig_names = ["clk", "rst_n", "count[3:0]", "clk_div2"]
    sig_keys = ["clk", "rst_n", "count", "clk_div2"]
    n_sigs = len(sig_names)
    track_h = plot_h / n_sigs
    grid_ns = 20
    n_grids = sim_ns // grid_ns
    grid_px = plot_w / max(n_grids, 1)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except Exception:
        font = ImageFont.load_default()

    # Grid lines
    for i in range(n_grids + 1):
        x = ml + i * grid_px
        color = "#e0e0e0" if i % 5 != 0 else "#c0c0c0"
        d.line([(x, mt), (x, height - mb)], fill=color, width=1)
    for i in range(n_sigs + 1):
        y = mt + i * track_h
        d.line([(ml, y), (width - mr, y)], fill="#c0c0c0", width=1)
    for i in range(0, n_grids + 1, 5):
        x = ml + i * grid_px
        d.text((x - 5, height - mb + 5), str(i * grid_ns) + "ns",
               fill="#666666", font=font)

    # Draw each signal
    for si, (sname, skey) in enumerate(zip(sig_names, sig_keys)):
        y_top = mt + si * track_h + 5
        y_mid = mt + si * track_h + track_h / 2
        y_bot = mt + (si + 1) * track_h - 5
        d.text((5, y_mid - 6), sname, fill="#333333", font=font)
        tl = signals_timeline.get(skey, [])
        if not tl:
            continue
        is_bus = (skey == "count")
        prev_val = None; prev_t = 0
        for t, val in tl:
            x = ml + (t / sim_ns) * plot_w
            if is_bus:
                if prev_val is not None:
                    xp = ml + (prev_t / sim_ns) * plot_w
                    d.rectangle([xp, y_top, x, y_bot],
                                outline="#4488cc", fill="#e8f0ff")
                    d.text((xp + 3, y_mid - 6), str(prev_val),
                           fill="#003366", font=font)
                prev_val = val; prev_t = t
            else:
                if prev_val is not None:
                    xp = ml + (prev_t / sim_ns) * plot_w
                    yl = y_top if prev_val == "1" else y_bot
                    d.line([(xp, yl), (x, yl)], fill="#1a1a8a", width=2)
                    yn = y_top if val == "1" else y_bot
                    if yl != yn:
                        d.line([(x, yl), (x, yn)], fill="#1a1a8a", width=2)
                prev_val = val; prev_t = t
        x_end = ml + plot_w
        if is_bus and prev_val is not None:
            xp = ml + (prev_t / sim_ns) * plot_w
            d.rectangle([xp, y_top, x_end, y_bot],
                        outline="#4488cc", fill="#e8f0ff")
            d.text((xp + 3, y_mid - 6), str(prev_val), fill="#003366", font=font)
        elif not is_bus and prev_val is not None:
            xp = ml + (prev_t / sim_ns) * plot_w
            yl = y_top if prev_val == "1" else y_bot
            d.line([(xp, yl), (x_end, yl)], fill="#1a1a8a", width=2)

    d.text((ml, 5), "Synthetic VCD Waveform (counter.v + tb_counter.v)",
           fill="#333333", font=font)
    img.save(out_path)
    return out_path

# ========================================================================== #
#  5. Q&A 生成（ground truth 从 VCD 参数直接计算，反作弊）
# ========================================================================== #

def generate_qa_pairs(params, signals_timeline):
    """从 VCD 仿真参数直接计算 Q&A 对的 ground truth。"""
    qa = []
    qa.append({"id": "q1_clock_freq", "type": "regression",
        "question": "What is the clock frequency in MHz?",
        "gt": str(round(params["clk_freq_mhz"], 1)),
        "gt_num": params["clk_freq_mhz"],
        "verify_method": "freq = 1000 / period_ns"})
    qa.append({"id": "q2_total_cycles", "type": "regression",
        "question": "How many complete clock cycles are shown?",
        "gt": str(params["total_clk_cycles"]),
        "gt_num": float(params["total_clk_cycles"]),
        "verify_method": "total_cycles = sim_ns / clk_period_ns"})
    qa.append({"id": "q3_reset_release", "type": "regression",
        "question": "At what time (ns) does rst_n go high?",
        "gt": str(params["rst_release_ns"]),
        "gt_num": float(params["rst_release_ns"]),
        "verify_method": "directly from testbench parameter"})
    qa.append({"id": "q4_final_count", "type": "word",
        "question": "What is the final value of count (hexadecimal)?",
        "gt": hex(params["final_count"]),
        "verify_method": "final_count = active_cycles mod 2^width"})
    div2_freq = params["clk_freq_mhz"] / 2
    qa.append({"id": "q5_div2_freq", "type": "regression",
        "question": "What is the frequency of clk_div2 in MHz?",
        "gt": str(round(div2_freq, 1)), "gt_num": div2_freq,
        "verify_method": "div2_freq = clk_freq / 2"})
    clk_tl = signals_timeline.get("clk", [])
    rising = sum(1 for t, v in clk_tl if v == "1")
    qa.append({"id": "q6_rising_edges", "type": "regression",
        "question": "How many rising edges of clk are shown?",
        "gt": str(rising), "gt_num": float(rising),
        "verify_method": "count(clk==1) from VCD timeline"})
    return qa

# ========================================================================== #
#  Main
# ========================================================================== #

def main():
    out_dir = os.path.join(HERE, "vcd_demo_output")
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 60)
    print("P4 Synthetic Waveform Data Demo")
    print("=" * 60)

    # Step 1: Write Verilog files
    v_path = os.path.join(out_dir, "counter.v")
    tb_path = os.path.join(out_dir, "tb_counter.v")
    with open(v_path, "w") as f:
        f.write(VERILOG_COUNTER)
    with open(tb_path, "w") as f:
        f.write(VERILOG_TESTBENCH)
    print("[1] Verilog RTL:    %s" % v_path)
    print("[1] Testbench:      %s" % tb_path)
    print("    (iverilog -o sim.vvp tb_counter.v counter.v && vvp sim.vvp)")

    # Step 2: Generate VCD
    vcd_path = os.path.join(out_dir, "counter.vcd")
    params = generate_vcd(vcd_path, 20, 520, 20, 4)
    print("[2] VCD generated:  %s (%d bytes)" % (vcd_path, os.path.getsize(vcd_path)))
    print("    Params: %s" % json.dumps(params))

    # Step 3: Parse VCD
    signals = parse_vcd(vcd_path)
    print("[3] VCD parsed:     %d signals" % len(signals))
    for name, tl in signals.items():
        print("    %s: %d transitions" % (name, len(tl)))

    # Step 4: Render PNG
    png_path = os.path.join(out_dir, "waveform.png")
    render_waveform_png(signals, params, png_path, 640, 400)
    print("[4] PNG rendered:   %s (%d bytes)" % (png_path, os.path.getsize(png_path)))

    # Step 5: Generate Q&A
    qa = generate_qa_pairs(params, signals)
    qa_path = os.path.join(out_dir, "qa_pairs.json")
    with open(qa_path, "w") as f:
        json.dump({"params": params, "qa_pairs": qa,
                   "cheat_check": "all GT from VCD params, not LLM"},
                  f, indent=2, ensure_ascii=False)
    print("[5] Q&A pairs:      %s (%d pairs)" % (qa_path, len(qa)))
    for q in qa:
        print("    %s: GT=%s" % (q["id"], q["gt"]))

    # Summary
    print()
    print("=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    print("  Verilog files : counter.v + tb_counter.v")
    print("  VCD file      : counter.vcd")
    print("  Waveform PNG  : waveform.png")
    print("  Q&A pairs     : %d (all GT from VCD params, cheat_rate=0)" % len(qa))
    print("  Tool chain    : Python VCD gen + parser + PIL renderer")
    print("  EDA equiv     : iverilog + vvp -> VCD -> vcd2image/GTKWave -> PNG")
    print()
    print("Scalability estimate:")
    wtypes = ["clock", "counter", "fifo", "shift_reg", "mux", "decoder",
              "adder", "fsm", "bus", "spi"]
    print("  %d circuit types x 100 param combos x 6 Q&A = %d samples" % (len(wtypes), len(wtypes)*100*6))
    return out_dir


if __name__ == "__main__":
    main()
