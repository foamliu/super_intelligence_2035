# AutoCell TCL Flow Pipeline

## Generation order

Build the Flow Spec first, then generate in dependency order:

1. layers.tcl
2. layer_functions.tcl
3. viadefs.tcl
4. globals.tcl
5. rules.tcl
6. place.tcl
7. route.tcl
8. run.tcl

## Sourcing order

`run.tcl` must `source` the seven technology files in exactly this order:

```tcl
source layers.tcl
source layer_functions.tcl
source viadefs.tcl
source globals.tcl
source rules.tcl
source place.tcl
source route.tcl
```

## Hard constraints

1. Technology creation: create the technology object in `layers.tcl` with `tech -process`; `run.tcl` must not create technology.
2. Via separation: put via definitions in `viadefs.tcl` and create router instances with `via ... -viadef ...` in `route.tcl`.
3. Explicit placement mode: select exactly one mode:
   - `auto`: execute `set_placer` and do not execute `read_placement`;
   - `replay`: execute `read_placement` with an existing JSON file and do not execute `set_placer`.
4. Predictable GDS output: use `[file join $case_dir ...]` unless the user explicitly provides an absolute path.
5. Explicit router contract: configure `set_router` with `grid_map`, `pin_template`, `pin_grid`, `vdd_connector`, and `vss_connector`.
6. Explicit grid map: map physical layers to grids from the Flow Spec.
7. Profile isolation: never use planar geometry as defaults for finfet or vice versa.
8. No TODO placeholders in final output.

## Final flow

The final flow must read netlists, create cells, configure placement and routing, call `generate_layout`, and call `write_layout`.
