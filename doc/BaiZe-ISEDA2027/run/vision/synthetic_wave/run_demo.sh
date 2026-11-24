#!/bin/bash

set -e

echo "=== Synthetic Waveform Demo ==="

# Step 1: Compile Verilog with Icarus Verilog
echo "1. Compiling Verilog files..."
iverilog -o tb_counter tb_counter.v demo_counter.v

# Step 2: Run simulation to generate VCD
echo "2. Running simulation to generate VCD..."
vvp tb_counter

# Step 3: Export waveform to PNG using GTKWave CLI
echo "3. Exporting waveform to PNG..."
gtkwave -S export_wave.tcl -n counter_wave.vcd

# Step 4: Generate Q&A pair
echo "4. Generating Q&A pair..."
cat > qa_pair.json << 'EOF'
{
  "image": "counter_wave.png",
  "question": "What is the maximum value of the count signal in the waveform?",
  "answer": "15 (0xF)",
  "metadata": {
    "type": "value_reading",
    "signal": "count",
    "range": "4 bits",
    "clock_period_ns": 10
  }
}
EOF

echo "Demo completed successfully!"
echo "Generated files:"
echo "  - counter_wave.vcd: Waveform dump"
echo "  - counter_wave.png: Waveform image"
echo "  - qa_pair.json: Q&A pair for training"
echo ""
echo "Q&A Sample:"
cat qa_pair.json
