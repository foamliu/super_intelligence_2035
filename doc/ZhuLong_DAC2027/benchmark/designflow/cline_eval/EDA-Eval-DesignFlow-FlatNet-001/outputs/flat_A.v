module top_A ( CLK , RST_N , DIN_7_ , DIN_6_ , DIN_5_ , DIN_4_ , DIN_3_ , DIN_2_ , DIN_1_ , DIN_0_ , DOUT_7_ , DOUT_6_ , DOUT_5_ , DOUT_4_ , DOUT_3_ , DOUT_2_ , DOUT_1_ , DOUT_0_ ) ;
  input CLK ;
  input RST_N ;
  input DIN_7_ ;
  input DIN_6_ ;
  input DIN_5_ ;
  input DIN_4_ ;
  input DIN_3_ ;
  input DIN_2_ ;
  input DIN_1_ ;
  input DIN_0_ ;
  output DOUT_7_ ;
  output DOUT_6_ ;
  output DOUT_5_ ;
  output DOUT_4_ ;
  output DOUT_3_ ;
  output DOUT_2_ ;
  output DOUT_1_ ;
  output DOUT_0_ ;
  wire cpu_pwdata_7_ ;
  wire midbus_7_ ;
  wire midbus_6_ ;
  wire midbus_5_ ;
  wire midbus_4_ ;
  wire midbus_3_ ;
  wire midbus_2_ ;
  wire midbus_1_ ;
  wire midbus_0_ ;
  LEAF_INV X0_X5 ( .A(CLK) , .Z(cpu_pwdata_7_) ) ;
  LEAF_BUF X0_X4 ( .A(RST_N) , .Z(DIN_0_) ) ;
  LEAF_INV X1_X8_X9 ( .A(cpu_pwdata_7_) , .Z(midbus_0_) ) ;
  LEAF_NAND X1_X8_X10 ( .A(cpu_pwdata_7_) , .B(cpu_pwdata_7_) , .Z(midbus_0_) ) ;
  LEAF_NOR X2_X7 ( .A(midbus_0_) , .B(midbus_0_) , .Z(DOUT_0_) ) ;
endmodule

module LEAF_INV ( A , Z ) ;
  input A ;
  output Z ;
  not ( Z , A ) ;
endmodule

module LEAF_BUF ( A , Z ) ;
  input A ;
  output Z ;
  buf ( Z , A ) ;
endmodule

module LEAF_NAND ( A , B , Z ) ;
  input A ;
  input B ;
  output Z ;
  nand ( Z , A , B ) ;
endmodule

module LEAF_NOR ( A , B , Z ) ;
  input A ;
  input B ;
  output Z ;
  nor ( Z , A , B ) ;
endmodule