# AutoCell TCL Command Reference

## Technology & Layers

```
tech -process <planar|finfet>
create_layer -name <name> -gds_layer <num> -gds_datatype <num>
```

## Layer Functions

```
set_layer_function -layer <name> -function <gate|diffusion|well|cut|routing|fin>
```

## Via Definitions

```
create_viadef -name <name> -cut <cut_layer> -lower <lower_layer> -upper <upper_layer> \
    -cut_size {<w> <h>} -spacing {<w> <h>} -enclosure {<w> <h>}
```

## Global Nets

```
set_global_net -role <VDD|VSS|BODY> -nets {<alias1> <alias2> ...}
```

## Design Rules

```
create_rule -name <rule_name> -value <float>
```

## Placement

```
# auto mode
set_placer -mode auto -template <template_name>

# replay mode
read_placement -file <json_file>
```

## Routing

```
create_grid -name <grid_name> -layer <layer_name> -direction <horizontal|vertical> -pitch <float>
set_router -grid_map {<layer1> <grid1> <layer2> <grid2> ...} \
    -pin_template <name> -pin_grid <grid_name> \
    -vdd_connector <name> -vss_connector <name>
via -name <inst_name> -viadef <viadef_name>
```

## Flow Control

```
read_netlist -mode <verilog|spice> -file <path>
create_cell -name <cell_name>
generate_layout -cell <cell_name>
write_layout -output <path>
```

## Sourcing

```
source <file.tcl>
```
