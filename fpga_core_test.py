import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer
from cocotb.binary import BinaryValue
from helper import int_list_to_bitstream
from helper import bin_list_to_int_little_endian
from helper import int_to_bin_list_little_endian
import os

@cocotb.test()
async def test_fpga_core(dut):
	clock = Clock(dut.scan_clk, 10000, units="ps")
	cocotb.fork(clock.start())

	# 2 * 2 fpga
	# built for primary fpga functional test because bitstream generator is pending complete
	# bitstream used in this testbench is hand-translated from VTR result

	# io info:
	# io_0: C, io_1: B, io_2: A, io_3: D
	# C = A | B, D = A & B
	tile_2_A_port = 0
	tile_3_A_port = 0
	tile_2_B_port = 2
	tile_3_B_port = 2

	# The Environmental Variable BITSTREAM_DIR is set in the vtr_wholeflow.sh
	# Loading Routing Configuration Bitstream
	import re
	f = open(os.getenv('BITSTREAM_DIR')+"/testMini.route.bitstream", "r")
	routing = f.read()
	routing = re.split("\n", routing)
	routing = [int(i) for i in routing if len(i) > 0]
	f.close()
	conn_bitstream = int_list_to_bitstream(routing, 2)
	conn_scan_size = len(conn_bitstream)
	
	conn_bitstream_check = conn_bitstream.copy()
	conn_bitstream += conn_bitstream_check
  	
	# Loading CLB Configuration Bitstream
	# The Environmental Variable BITSTREAM_DIR is set in the vtr_wholeflow.sh
	f = open(os.getenv('BITSTREAM_DIR')+"/testMini.clb.bitstream", "r")
	lut_bitstream = f.read()
	lut_bitstream = [int(i) for i in lut_bitstream]
	f.close()
	lut_scan_size = len(lut_bitstream)
	
	lut_bitstream_check = lut_bitstream.copy()
	lut_bitstream += lut_bitstream_check
	
	# print("lut bitstream:")
	# print(lut_bitstream)
	# print("conn bitstream:")
	# print(conn_bitstream)
	
	#first scan 
	dut.clb_scan_en <= 1
	for i in range(lut_scan_size):
		dut.clb_scan_in <= lut_bitstream.pop(-1)
		await RisingEdge(dut.scan_clk)
	dut.clb_scan_en <= 0
	
	
	dut.conn_scan_en <= 1
	for i in range(conn_scan_size):
		dut.conn_scan_in <= conn_bitstream.pop(-1)
		await RisingEdge(dut.scan_clk)
	dut.conn_scan_en <= 0
	
	#repeated scan and check
	clb_scan_out = []
	dut.clb_scan_en <= 1
	for i in range(lut_scan_size):
		dut.clb_scan_in <= lut_bitstream.pop(-1)
		await RisingEdge(dut.scan_clk)
		clb_scan_out.append(dut.clb_scan_out.value)
	dut.clb_scan_en <= 0
	
	if(lut_bitstream_check == clb_scan_out[::-1]):
		print('clb bitstream valid')
	else:
		print('clb bitstream invalid')
		
	conn_scan_out = []
	dut.conn_scan_en <= 1
	for i in range(conn_scan_size):
		dut.conn_scan_in <= conn_bitstream.pop(-1)
		await RisingEdge(dut.scan_clk)
		conn_scan_out.append(dut.conn_scan_out.value)
	dut.conn_scan_en <= 0
	
	if(conn_bitstream_check == conn_scan_out[::-1]):
		print('conn bitstream valid')
	else:
		print('conn bitstream invalid')

	await Timer(100, units='ps')

	test_in_A = random.randint(0, 1)
	test_in_B = random.randint(0, 1)

	# dut.fpga_in[0] <= 0
	# B
	dut.fpga_in[2] <= test_in_B
	# A
	dut.fpga_in[1] <= test_in_A
	# dut.fpga_in[3] <= 0
	
	print("TOng CORE TESTTT")
	
	await Timer(100, units='ps')

	result_C = dut.fpga_out[3]
	result_D = dut.fpga_out[0]
	await Timer(200, units='ps')
	print("FPGA input:")
	print(dut.fpga_in.value)
	print("FPGA output:")
	print(dut.fpga_out.value)

	assert result_C == test_in_A | test_in_B, "port 0 (C) mismatch"
	assert result_D == test_in_A & test_in_B, "port 3 (D) mismatch"


