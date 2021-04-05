`include "fpga_edge.v"
`include "tile_8x8.v"

module fpga_core(clk, scan_clk, fpga_in, fpga_out,
 clb_scan_in, clb_scan_out, clb_scan_en, conn_scan_in, conn_scan_out, conn_scan_en, reset);

    input clk, scan_clk, clb_scan_in, clb_scan_en, conn_scan_in, conn_scan_en, reset;
    output clb_scan_out, conn_scan_out;
    input[9:0] fpga_in;
    output [9:0] fpga_out;

    wire[31:0] edge_right_arry_left, array_left_edge_right, edge_top_array_bottom, array_bottom_edge_top;
    wire[7:0] clb_out_sb_in, left_cb_right_clb, bottom_cb_top_clb;

    wire conn_scan_conn;

    // fpga_in and fpga_out are mapped inversely to follow the pin order
    fpga_edge inst_edge(
        .right_in(array_left_edge_right), 
        .right_out(edge_right_arry_left), 
        .top_in(array_bottom_edge_top), 
        .top_out(edge_top_array_bottom), 
        .right_sb_in(clb_out_sb_in), 
        .right_clb_in(left_cb_right_clb), 
        .top_clb_in(bottom_cb_top_clb),
        .scan_clk(scan_clk), 
        .conn_scan_en(conn_scan_en), 
        .conn_scan_in(conn_scan_in), 
        .conn_scan_out(conn_scan_conn), 
        .fpga_in({fpga_in[0], fpga_in[1], fpga_in[2], fpga_in[3], fpga_in[4], fpga_in[5], fpga_in[6], fpga_in[7], fpga_in[8], fpga_in[9]}), 
        .fpga_out({fpga_out[0], fpga_out[1], fpga_out[2], fpga_out[3], fpga_out[4], fpga_out[5], fpga_out[6], fpga_out[7], fpga_out[8], fpga_out[9]})
    );

    tile_8x8 inst_tile_8x8 (
        .clk(clk), 
        .scan_clk(scan_clk), 
        .clb_scan_in(clb_scan_in), 
        .clb_scan_out(clb_scan_out), 
        .clb_scan_en(clb_scan_en), 
        .conn_scan_in(conn_scan_conn), 
        .conn_scan_out(conn_scan_out), 
        .conn_scan_en(conn_scan_en),
        .left_in(edge_right_arry_left), 
        .right_in(), 
        .top_in(), 
        .bottom_in(edge_top_array_bottom), 
        .left_out(array_left_edge_right), 
        .right_out(), 
        .top_out(), 
        .bottom_out(array_bottom_edge_top), 
	    .left_clb_out(clb_out_sb_in), 
        .left_clb_in(left_cb_right_clb), 
        .bottom_clb_in(bottom_cb_top_clb),
        .right_sb_in(), 
	    .top_cb_out(), 
        .right_cb_out(),
        .reset(reset)
    );
    
`ifdef COCOTB_SIM
	initial begin
  		$dumpfile ("fpga_core.vcd");
 	 	$dumpvars (0, fpga_core);
  		#1;
	end
`endif
endmodule
