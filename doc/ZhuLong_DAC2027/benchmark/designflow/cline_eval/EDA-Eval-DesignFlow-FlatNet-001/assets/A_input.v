// A_input.v — hierarchical CDL/Verilog netlist (visible A)
// top_A -> ICV_WRAP_X (2-level: leaves) and ICV_WRAP_P -> ICV_WRAP_Q (3-level: leaves)
// contains: `\`-escape nets, VDD/VSS PG, bus bit-selects

module top_A ( CLK , RST_N , DIN , DOUT , VDD , VSS ) ;
  input CLK ;
  input RST_N ;
  input [7:0] DIN ;
  output [7:0] DOUT ;
  input VDD ;
  input VSS ;
  wire \cpu_pwdata[7] ;
  wire [7:0] midbus ;
  ICV_WRAP_X X0 ( .CLK(CLK) , .RST(RST_N) , .A(DIN[0]) , .Y(\cpu_pwdata[7]) , .VDD(VDD) , .VSS(VSS) ) ;
  ICV_WRAP_P X1 ( .A(\cpu_pwdata[7]) , .Y(midbus[0]) , .VDD(VDD) , .VSS(VSS) ) ;
  ICV_WRAP_R X2 ( .A(midbus[0]) , .Y(DOUT[0]) , .VDD(VDD) , .VSS(VSS) ) ;
endmodule

module ICV_WRAP_X ( CLK , RST , A , Y , VDD , VSS ) ;
  input CLK ;
  input RST ;
  input A ;
  output Y ;
  input VDD ;
  input VSS ;
  LEAF_INV  X5 ( .A(CLK) , .Z(Y) , .VDD(VDD) , .VSS(VSS) ) ;
  LEAF_BUF  X4 ( .A(RST) , .Z(A) , .VDD(VDD) , .VSS(VSS) ) ;
endmodule

module ICV_WRAP_P ( A , Y , VDD , VSS ) ;
  input A ;
  output Y ;
  input VDD ;
  input VSS ;
  ICV_WRAP_Q X8 ( .A(A) , .Y(Y) , .VDD(VDD) , .VSS(VSS) ) ;
endmodule

module ICV_WRAP_Q ( A , Y , VDD , VSS ) ;
  input A ;
  output Y ;
  input VDD ;
  input VSS ;
  LEAF_INV  X9 ( .A(A) , .Z(Y) , .VDD(VDD) , .VSS(VSS) ) ;
  LEAF_NAND X10 ( .A(A) , .B(A) , .Z(Y) , .VDD(VDD) , .VSS(VSS) ) ;
endmodule

module ICV_WRAP_R ( A , Y , VDD , VSS ) ;
  input A ;
  output Y ;
  input VDD ;
  input VSS ;
  LEAF_NOR X7 ( .A(A) , .B(A) , .Z(Y) , .VDD(VDD) , .VSS(VSS) ) ;
endmodule

module LEAF_INV ( A , Z , VDD , VSS ) ;
  input A ;
  output Z ;
  input VDD ;
  input VSS ;
  not ( Z , A ) ;
endmodule

module LEAF_BUF ( A , Z , VDD , VSS ) ;
  input A ;
  output Z ;
  input VDD ;
  input VSS ;
  buf ( Z , A ) ;
endmodule

module LEAF_NAND ( A , B , Z , VDD , VSS ) ;
  input A ;
  input B ;
  output Z ;
  input VDD ;
  input VSS ;
  nand ( Z , A , B ) ;
endmodule

module LEAF_NOR ( A , B , Z , VDD , VSS ) ;
  input A ;
  input B ;
  output Z ;
  input VDD ;
  input VSS ;
  nor ( Z , A , B ) ;
endmodule
