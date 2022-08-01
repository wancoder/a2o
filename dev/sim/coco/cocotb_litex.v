
`include "tri_a2o.vh"

`timescale 1ns/1ps

module cocotb (

    input                                                  clk_1x,
    input                                                  clk_2x,
    input                                                  rst,

    input                                                  timerInterrupt,
    input                                                  externalInterrupt,
    input                                                  softwareInterrupt,
    input                                                  externalInterruptS,

    output                                                 wb_stb,
    output                                                 wb_cyc,
    output [31:0]                                          wb_adr,
    output                                                 wb_we,
    output [3:0]                                           wb_sel,
    output [31:0]                                          wb_datw,
    input                                                  wb_ack,
    input  [31:0]                                          wb_datr

);

a2owb c0 (
      .clk_1x(clk_1x),
      .clk_2x(clk_2x),
      .rst(rst),

      .timerInterrupt(timerInterrupt),
      .externalInterrupt(externalInterrupt),
      .softwareInterrupt(softwareInterrupt),
      .externalInterruptS(externalInterruptS),

      .wb_stb(wb_stb),
      .wb_cyc(wb_cyc),
      .wb_adr(wb_adr),
      .wb_we(wb_we),
      .wb_ack(wb_ack),
      .wb_sel(wb_sel),
      .wb_datr(wb_datr),
      .wb_datw(wb_datw)
   );

initial begin
  $dumpfile ("a2olitex.vcd");
  // you can do it by levels and also by module so could prune down
  $dumpvars;
  // need to explicitly specify arrays for icarus
  // guess not: $dumpvars cannot dump a vpiMemory
  //$dumpvars(0, c0.iuq0.iuq_slice_top0.slice0.iuq_ibuf0.buffer_data_q);
  #1;
end

endmodule