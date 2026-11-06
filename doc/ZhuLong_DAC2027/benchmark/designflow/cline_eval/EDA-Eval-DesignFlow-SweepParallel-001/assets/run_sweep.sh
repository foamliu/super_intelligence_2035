#!/bin/bash

queue=fqueue3_analog
cpu_core=4

netlist=IsmOscTestSweep.sp
run_dir=superon_sweep_$(date +%Y%m%d_%H%M%S)

mkdir -p "$run_dir"

module unload primesim
module load prime/2023.12-SP4

bsub -q "$queue" "cd $PWD/$run_dir && finesim ../$netlist -np $cpu_core > run.log 2>&1"

echo "Output directory: $run_dir"
