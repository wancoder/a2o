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

//*****************************************************************************
//  Description:  XU Population Count - Byte Phase
//
//*****************************************************************************

module tri_st_popcnt_byte(
   b0,
   y,
   vdd,
   gnd
);
   input [0:7]  b0;
   output [0:3] y;
   inout        vdd;
   inout        gnd;

   wire [0:2]   s0;
   wire [0:3]   c1;
   wire [0:0]   s1;
   wire [0:1]   c2;

   // Level 0

   tri_csa32 csa_l0_0(
      .vd(vdd),
      .gd(gnd),
      .a(b0[0]),
      .b(b0[1]),
      .c(b0[2]),
      .sum(s0[0]),
      .car(c1[0])
   );


   tri_csa32 csa_l0_1(
      .vd(vdd),
      .gd(gnd),
      .a(b0[3]),
      .b(b0[4]),
      .c(b0[5]),
      .sum(s0[1]),
      .car(c1[1])
   );


   tri_csa22 csa_l0_2(
      .a(b0[6]),
      .b(b0[7]),
      .sum(s0[2]),
      .car(c1[2])
   );


   tri_csa32 csa_l0_3(
      .vd(vdd),
      .gd(gnd),
      .a(s0[0]),
      .b(s0[1]),
      .c(s0[2]),
      .sum(y[3]),
      .car(c1[3])
   );

   // Level 1

   tri_csa32 csa_l1_0(
      .vd(vdd),
      .gd(gnd),
      .a(c1[0]),
      .b(c1[1]),
      .c(c1[2]),
      .sum(s1[0]),
      .car(c2[0])
   );


   tri_csa22 csa_l1_1(
      .a(c1[3]),
      .b(s1[0]),
      .sum(y[2]),
      .car(c2[1])
   );

   // Level 2/3

   tri_csa22 csa_l2_0(
      .a(c2[0]),
      .b(c2[1]),
      .sum(y[1]),
      .car(y[0])
   );


endmodule
