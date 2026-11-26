// DC netlist fragment: dc_2026-11-02-20.29.45
// test_chip_v1 — PM_VDDI_Inst subtree (VDD_PM netlist-level isolation)
module test_chip_v1 (
    input  VDD,
    input  VSS,
    input  VDD_PM,      // top-level PM sensing supply pin
    // ... 16 top-level pins total
    output [15:0] data_out
);
  // PM array
  PMArrayPart TOPPMBLK (
    .VDD(VDD), .VSS(VSS), .VDD_PM(VDD_PM)
  );

  // PM VDDI matrix — hierarchy port maps module-local VDD_PM to top
  PMVDDIMatrixPart PM_VDDI_Inst (
    .VDD_PM(VDD_PM),   // <-- hierarchy port (NOT .VDD): maps to top-level VDD_PM
    .VDD(VDD),
    .VSS(VSS)
  );

  // Inside PM_VDDI_Inst: 21 x PMVDDIRowPart(PMColBLK_Blk40xx)
  //   each PMVDDIRowPart contains 21 x INVD8(PMRowBLK_Blk40xx)
  //   each INVD8 leaf: .VDD(local VDD_PM), .VSS(VSS)
  //   => 441 leaf INVD8 cells, .VDD connects to module-local VDD_PM net
  //   => top-level GNC searching pin "VDD" finds 0 leaf std-cell pin on VDD_PM
  //
  // (subtree expanded flat for verification)
  PMVDDIRowPart PMColBLK_Blk40xx00 ( .VDD_PM(VDD_PM), .VSS(VSS),
    .row( {PMRowBLK_Blk40xx00, PMRowBLK_Blk40xx01, ... PMRowBLK_Blk40xx20} ) );
  // ... 21 RowParts, each with 21 INVD8 = 441 leaf cells total
endmodule
