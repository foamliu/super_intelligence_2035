# Planar Profile Rules

## Process type
`planar`

## Device sizing
Use `channel_width` device sizing. Device models are `nmos_planar_lvt` / `pmos_planar_lvt`.

## Layer set
Typical planar layers: poly, active, nwell, contact, metal1, via1, metal2, via2, metal3.

## Key constraints
- Layers are declared with `create_layer -name <name> -gds_layer <num> -gds_datatype <num>`.
- Layer functions: poly=gate, active=diffusion, nwell=well, contact=cut, metalN=routing, viaN=cut.
- Via definitions use cut/lower/upper layer names from the declared layer set.
- Design rules use planar-specific values (e.g., min_width_m1=0.06, min_spacing_m1=0.07).
- Placement templates use planar boundary dimensions.
- Routing grids use planar pitches (e.g., 0.20um for metal1/2, 0.30um for metal3).
- Global nets: VDD=[vdd,VDD,vcc], VSS=[vss,VSS,gnd], BODY=[body,VNW,vpw].

## Forbidden
- Do not use finfet-specific parameters (nfin, fin_width) in a planar flow.
- Do not copy finfet layer numbers, rule values, or via enclosures.
