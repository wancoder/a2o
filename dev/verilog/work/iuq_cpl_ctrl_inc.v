// © IBM Corp. 2020
// Licensed under the Apache License, Version 2.0 (the "License"), as modified by
// the terms below; you may not use the files in this repository except in
// compliance with the License as modified.
// You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
//
// Modified Terms:
//
//    1) For the purpose of the patent license granted to you in Section 3 of the
//    License, the "Work" hereby includes implementations of the work of authorship
//    in physical form.
//
//    2) Notwithstanding any terms to the contrary in the License, any licenses
//    necessary for implementation of the Work that are available from OpenPOWER
//    via the Power ISA End User License Agreement (EULA) are explicitly excluded
//    hereunder, and may be obtained from OpenPOWER under the terms and conditions
//    of the EULA.
//
// Unless required by applicable law or agreed to in writing, the reference design
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
// for the specific language governing permissions and limitations under the License.
//
// Additional rights, including the ability to physically implement a softcore that
// is compliant with the required sections of the Power ISA Specification, are
// available at no cost under the terms of the OpenPOWER Power ISA EULA, which can be
// obtained (along with the Power ISA) here: https://openpowerfoundation.org.

`timescale 1 ns / 1 ns

//  Description:  Saturating Incrementer
//
//*****************************************************************************

module iuq_cpl_ctrl_inc(
   inc,
   i,
   o
);
`include "tri_a2o.vh"
   parameter         SIZE = 7;
   parameter         WRAP = 40;
   input [0:1]       inc;
   input [0:SIZE-1]  i;

   output [0:SIZE-1] o;

      wire [1:SIZE]     a;
      wire [1:SIZE]     b;
      wire [1:SIZE]     rslt;
      wire              rollover;
      wire              rollover_m1;
      wire              inc_1;
      wire              inc_2;
      wire [0:1]        wrap_sel;

      // Increment by 1 or 2.
      // Go back to zero at WRAP
      // Flip bit zero when a rollover occurs
      // eg 0...39, 64..103

      assign a = {i[1:SIZE - 1], inc[1]};
      assign b = {1'b0, inc[0], inc[1]};
      assign rslt = a + b;

      assign rollover = i[1:SIZE - 1] == WRAP;
      assign rollover_m1 = i[1:SIZE - 1] == WRAP - 1;

      assign inc_1 = inc[0] ^ inc[1];
      assign inc_2 = inc[0] & inc[1];

      assign wrap_sel[0] = (rollover & inc_1) | (rollover_m1 & inc_2);
      assign wrap_sel[1] = rollover & inc_2;

      assign o[0] = i[0] ^ |(wrap_sel);

      assign o[1:SIZE - 1] = (wrap_sel[0:1] == 2'b10) ? 0 :
                             (wrap_sel[0:1] == 2'b01) ? 1 :
                             rslt[1:SIZE - 1];

endmodule
