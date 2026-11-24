# GTKWave TCL script to export waveform to PNG
set vcd_file "counter_wave.vcd"
set output_png "counter_wave.png"

# Open VCD file
gtkwave::/Edit/Insert_File $vcd_file

# Add signals
gtkwave::/Edit/Insert_Signal_Recursive tb_counter/clk
gtkwave::/Edit/Insert_Signal_Recursive tb_counter/rst_n
gtkwave::/Edit/Insert_Signal_Recursive tb_counter/count

# Zoom to full view
gtkwave::/View/Zoom/Zoom_Full

# Set waveform style
gtkwave::/View/Show_Grid 1
gtkwave::/View/Time_Unit_From_Simulation 1

# Export to PNG
gtkwave::/File/Export_Graphics $output_png png

# Exit GTKWave
gtkwave::/File/Quit
