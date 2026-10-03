# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


async def uart_receive(dut, clks_per_bit):

    byte = 0

    while dut.uo_out.value[0] == 1:
        await RisingEdge(dut.clk)
    
    await ClockCycles(dut.clk, clks_per_bit // 2)
    
    assert dut.uo_out.value[0] == 0, "start bit not low at mid-bit"

    for i in range(8):
        await ClockCycles(dut.clk, clks_per_bit)
        bit = dut.uo_out.value[0]
        byte |= (int(bit) << i)

    await ClockCycles(dut.clk, clks_per_bit)
    assert dut.uo_out.value[0] == 1, "stop bit not high at mid-bit"

    return byte

async def uart_fake_send(dut, byte, clks_per_bit):
    # Send start bit
    dut.ui_in.value = 0

    await ClockCycles(dut.clk, clks_per_bit)

    for i in range(8):
        bit = (byte >> i) & 1
        dut.ui_in.value = bit
        await ClockCycles(dut.clk, clks_per_bit)

    # Send stop bit
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, clks_per_bit)

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 1
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    # dut.ui_in.value = 20

    rx_task = cocotb.start_soon(uart_receive(dut, 8))

    await uart_fake_send(dut, 50, 8)

    result = await rx_task

    # inputs have been set and reset deasserted

    # await falling edge of serial output for start bit

    # await clocks_per_bit//2 clock cycles and read the serial output value should be equal to 0

    # then await clocks_per_bit clock cycles for bit 0, then again for bit 1, then again for bit 2, and so on till bit 7

    # last await for clocks per bit clock cycles the value should be 1

    # also need to check if the busy signal is high through out this and goes low during the stop bit

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    assert result == 50, f"Expected 50, got {result}"

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
