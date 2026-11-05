// hl22_porting_test_chip_v1_postsyn.v  (head excerpt, 60 lines)
module hl22_porting_test_chip_v1 ( TMOut, TMReady, GroupSelect0, GroupSelect1,
    GroupSelect2, GroupSelect3, ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1,
    CtrlEn, clk, rst_n );
    input TMOut, TMReady, GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3;
    input ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn;
    input clk, rst_n;
    wire n1, n2, n3, n4, n5, n6, n7, n8, n9, n10;
    INVD2BWP40P140LVT U1 ( .I(D0), .ZN(n1) );
    INVD2BWP40P140LVT U2 ( .I(D1), .ZN(n2) );
    INVD4BWP40P140LVT U3 ( .I(n1), .ZN(n3) );
    ND2D1BWP40P140LVT U4 ( .A1(n2), .A2(n3), .ZN(n4) );
    ND2D1BWP40P140LVT U5 ( .A1(n4), .A2(D2), .ZN(n5) );
    INVD2BWP40P140LVT U6 ( .I(n5), .ZN(n6) );
    INVD2BWP40P140LVT U7 ( .I(D3), .ZN(n7) );
    ND2D1BWP40P140LVT U8 ( .A1(n6), .A2(n7), .ZN(n8) );
    INVD2BWP40P140LVT U9 ( .I(n8), .ZN(n9) );
    INVD2BWP40P140LVT U10 ( .I(D4), .ZN(n10) );
    ND2D1BWP40P140LVT U11 ( .A1(n9), .A2(n10), .ZN(TMOut) );
    INVD2BWP40P140LVT U12 ( .I(D5), .ZN(TMReady) );
    ND2D1BWP40P140LVT U13 ( .A1(GroupSelect0), .A2(GroupSelect1), .ZN(n11) );
    ND2D1BWP40P140LVT U14 ( .A1(GroupSelect2), .A2(GroupSelect3), .ZN(n12) );
    ND2D1BWP40P140LVT U15 ( .A1(n11), .A2(n12), .ZN(ClearFreqDiv) );
    INVD2BWP40P140LVT U16 ( .I(SelByFreq0), .ZN(n13) );
    ND2D1BWP40P140LVT U17 ( .A1(ModeSel0), .A2(ModeSel1), .ZN(n14) );
    ND2D1BWP40P140LVT U18 ( .A1(n13), .A2(n14), .ZN(CtrlEn) );
endmodule
