source ref_impl.tcl
set a "# Routing report
NET clk segments=4 vias=3 layers=M1,M2,M3 status=routed
NET data segments=2 vias=1 layers=M1,M2 status=routed
NET rst segments=1 vias=0 layers=M1 status=partial
NET vss segments=0 vias=0 layers= status=unrouted
SUMMARY nets_checked=4 routed=2 unrouted=1 missing_vias=0 max_segments=4 max_segment_net=clk"
set r [layout_routing_audit $a]
puts "mismatch=[dict get $r mismatched_summary]"
puts "routed=[dict get $r routed_count] unrouted=[dict get $r unrouted_count] max=[dict get $r max_segments] maxnet=[dict get $r max_segment_net]"
