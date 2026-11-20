// invx1.v - Simple inverter netlist for AutoCell flow
module invx1 (Y, A);
    output Y;
    input A;

    wire vdd, vss;

    pmos_planar_lvt p1 (.Y(Y), .A(A), .vdd(vdd), .vss(vss));
    nmos_planar_lvt n1 (.Y(Y), .A(A), .vdd(vdd), .vss(vss));
endmodule
