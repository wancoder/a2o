// © IBM Corp. 2022
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

// Transaction limiting
// LOAD_CREDITS=1, STORE_CREDITS=1, XUCR0[52]=1
//
// Experiments with downsizing
// ;tldr most dont work!

`ifndef _tri_a2o_vh_
`define _tri_a2o_vh_

`include "tri.vh"

// Experiments with downsizing

// normal settings
`define LQ_NORMAL
`define DC_32
`define IU_NORMAL           // this one actually works if keep erat bypass
`define RN_CP_NORMAL
`define RV_NORMAL             // needs rtl updates to support changes

`define EXPAND_TLB_TYPE 2    // 0 = erat-only, 1 = tlb logic, 2 = tlb array
//`define EXPAND_TLB_TYPE 0     // doesn't work in sim

// 0: none   1: DP
//`define FLOAT_TYPE 0          // fails with completion x's in sim
`define FLOAT_TYPE 1

/*wtf these are a mess; need to be doc'd and create dependency reqts and legal ranges;
      shrinking values causes lots of bit sel vector problems, and sim fails

      can ic size/ways be easily added?
      can dc ways use parameter?
*/

// ********************************************************************************************************
// Load/Store
`ifdef LQ_NORMAL

`define  LDSTQ_ENTRIES  16
`define  LDSTQ_ENTRIES_ENC  4
`define  STQ_ENTRIES  12
`define  STQ_ENTRIES_ENC  4
`define  STQ_FWD_ENTRIES  4		// number of stq entries that can be forwarded from
`define  LMQ_ENTRIES  8
`define  LMQ_ENTRIES_ENC  3
`define  LGQ_ENTRIES  8
`define  EMQ_ENTRIES  4          // erat miss queue (d-only?)
`define  IUQ_ENTRIES  4 		   // Instruction Fetch Queue Size (lq)
`define  MMQ_ENTRIES  2 		   // MMU Queue Size (lq)

`else

/*
// these values comp/elab and DON'T pass test3 (coco)
// and vivado still gets an elab error:
// ERROR: [Synth 8-524] part-select [0:4] out of range of prefix 'stq3_cmmt_ptr_q' [/data/projects/a2o/dev/build/litex/a2o/verilog/work/lq_stq.v:2171]
// not sure if it's a true requirement or the hardcoded 0:4 can use `STQ_ENTRIES
`define  LDSTQ_ENTRIES  4        // ?order?
`define  LDSTQ_ENTRIES_ENC  2
`define  STQ_ENTRIES  4
`define  STQ_ENTRIES_ENC  2
`define  STQ_FWD_ENTRIES  2		// number of stq entries that can be forwarded from
`define  LMQ_ENTRIES  4
`define  LMQ_ENTRIES_ENC  2
`define  LGQ_ENTRIES  4
*/
// above w/STQ_ENTRIES=5
// these values comp/elab and fail test3 (coco) with cp hang after 8700 cys
`define  LDSTQ_ENTRIES  4        // ?order?
`define  LDSTQ_ENTRIES_ENC  2
`define  STQ_ENTRIES  5
`define  STQ_ENTRIES_ENC  3
`define  STQ_FWD_ENTRIES  2		// number of stq entries that can be forwarded from
`define  LMQ_ENTRIES  4
`define  LMQ_ENTRIES_ENC  2
`define  LGQ_ENTRIES  4
`define  EMQ_ENTRIES  1          // erat miss queue (d-only?)
`define  IUQ_ENTRIES  1 		   // Instruction Fetch Queue Size (lq)
`define  MMQ_ENTRIES  1 		   // MMU Queue Size (lq)

`endif
// ********************************************************************************************************

// ********************************************************************************************************
// DC Size
//wtf modify ways also?

`ifdef DC_32

`define  STQ_DATA_SIZE  64		   // 64 or 128 Bit store data sizes supported
`define  DC_SIZE  15			      // 14 => 16K L1D$, 15 => 32K L1D$
`define  CL_SIZE  6			      // 6 => 64B CLINE, 7 => 128B CLINE

`else

//wtf this gets 8 vector size warnings in iverilog and hangs early in coco test3
`define  STQ_DATA_SIZE  64		   // 64 or 128 Bit store data sizes supported
`define  DC_SIZE  14			      // 14 => 16K L1D$, 15 => 32K L1D$
`define  CL_SIZE  6			      // 6 => 64B CLINE, 7 => 128B CLINE

`endif
// ********************************************************************************************************

// ********************************************************************************************************
// IU
//wtf NO IC SIZE
//  iuq_ic_dir:   parameter                      ways = 4;
//                dir_rd_addr,dir_wr_addr hardcoded 0:6 - but somewhat easy change to use smaller IC?  hold bits to 0 and change lookup

`ifdef IU_NORMAL

`define  INCLUDE_IERAT_BYPASS 1	// 0 => Removes IERAT Bypass logic, 1=> includes (power savings)

`define  IBUFF_DEPTH 16

`define  BUILD_PFETCH 1 		   // 1=> include pfetch in the build, 0=> build without pfetch
`define  PF_IAR_BITS 12	   	   // number of IAR bits used by prefetch
`define  PF_IFAR_WIDTH 12
`define  PFETCH_INITIAL_DEPTH 0	// the initial value for the SPR that determines how many lines to prefetch
`define  PFETCH_Q_SIZE_ENC 3		// number of bits to address queue size (3 => 8 entries, 4 => 16 entries)
`define  PFETCH_Q_SIZE 8		   // number of entries

`else

// compiles and fails after first op executes in coco test3 - IERAT_BYPASS=0
`define  INCLUDE_IERAT_BYPASS  1	// 0 => Removes IERAT Bypass logic, 1=> includes (power savings)

// these work so far!
`define  IBUFF_DEPTH 6           //wtf 4 fails compile in iuq_ibuf equations using -5

`define  BUILD_PFETCH 0  		   // 1=> include pfetch in the build, 0=> build without pfetch
`define  PF_IAR_BITS 12		      // number of IAR bits used by prefetch
`define  PF_IFAR_WIDTH 12
`define  PFETCH_INITIAL_DEPTH 0	// the initial value for the SPR that determines how many lines to prefetch
`define  PFETCH_Q_SIZE_ENC 3		// number of bits to address queue size (3 => 8 entries, 4 => 16 entries)
`define  PFETCH_Q_SIZE 8		   // number of entries

`endif

// ********************************************************************************************************


//********************************************************************************************************
// Rename-Completion
`ifdef RN_CP_NORMAL

`define  CPL_Q_DEPTH  32
`define  CPL_Q_DEPTH_ENC  6

`define  GPR_POOL  64
`define  GPR_POOL_ENC  6
`define  GPR_UCODE_POOL  4
`define  FPR_POOL 64
`define  FPR_POOL_ENC 6
`define  CR_POOL  24
`define  CR_POOL_ENC  5
`define  CR_WIDTH 4
`define  CR_UCODE_POOL  1
`define  BR_POOL_ENC  3
`define  BR_POOL      8
`define  CTR_POOL_ENC  3
`define  CTR_POOL  8
`define  CTR_UCODE_POOL  0
`define  LR_POOL_ENC  3
`define  LR_POOL  8
`define  LR_UCODE_POOL  0
`define  XER_POOL  12
`define  XER_POOL_ENC  4
`define  XER_WIDTH  10
`define  XER_UCODE_POOL  0

`else

`define  CPL_Q_DEPTH 16             // 16/5: ok, 8/4, 4/3: fail
`define  CPL_Q_DEPTH_ENC 5

`define  GPR_POOL  64
`define  GPR_POOL_ENC  6
`define  GPR_UCODE_POOL  4
`define  FPR_POOL 64
`define  FPR_POOL_ENC 6
`define  CR_POOL  24
`define  CR_POOL_ENC  5
`define  CR_WIDTH 4
`define  CR_UCODE_POOL  1
`define  BR_POOL_ENC  3
`define  BR_POOL      8
`define  CTR_POOL_ENC  3
`define  CTR_POOL  8
`define  CTR_UCODE_POOL  0
`define  LR_POOL_ENC  3
`define  LR_POOL  8
`define  LR_UCODE_POOL  0
`define  XER_POOL  12
`define  XER_POOL_ENC  4
`define  XER_WIDTH  10
`define  XER_UCODE_POOL  0

`endif

//********************************************************************************************************
// Reservation Stations

`ifdef RV_NORMAL

`define  RV_FX0_ENTRIES  12
`define  RV_FX0_ENTRIES_ENC  4
`define  RV_FX1_ENTRIES  12
`define  RV_FX1_ENTRIES_ENC  4
`define  RV_LQ_ENTRIES  16
`define  RV_LQ_ENTRIES_ENC  4
`define  RV_AXU0_ENTRIES  12
`define  RV_AXU0_ENTRIES_ENC  4
`define  RV_AXU1_ENTRIES  0
`define  RV_AXU1_ENTRIES_ENC  1
`define  UCODE_ENTRIES  8
`define  UCODE_ENTRIES_ENC  3

`else

//wtf there are hardcoded bit 4's in enc eqs; try not touching the enc widths (the '4' DOES come from a
//    parameter though (q_barf_enc_g) so may just need rewrite, or is dont-care cuz some are always 0).
//    but eqs must be related - changing entry count still fails
`define  RV_FX0_ENTRIES 12
`define  RV_FX0_ENTRIES_ENC 4
`define  RV_FX1_ENTRIES 12
`define  RV_FX1_ENTRIES_ENC 4
`define  RV_LQ_ENTRIES 16
`define  RV_LQ_ENTRIES_ENC 4
`define  RV_AXU0_ENTRIES 12
`define  RV_AXU0_ENTRIES_ENC 4
`define  RV_AXU1_ENTRIES 0
`define  RV_AXU1_ENTRIES_ENC 1
`define  UCODE_ENTRIES 8
`define  UCODE_ENTRIES_ENC 3

`endif

//********************************************************************************************************

/* FXU*/
`define  FXU1_ENABLE  1          //wtf don't see this except in dispatch; must need some other stuff (like if deleting mmu/fpu)

// Use this line for 1 thread.  Comment out for 2 thread design.
`define THREADS1

//`define RESET_VECTOR 32'hFFFFFFFC
`define RESET_VECTOR 32'h00000000

`ifdef THREADS1
    `define  THREADS  1
    `define  THREAD_POOL_ENC  0
    `define  THREADS_POOL_ENC  0
`else
    `define  THREADS  2
    `define  THREAD_POOL_ENC  1
    `define  THREADS_POOL_ENC  1
`endif

`define  LOAD_CREDITS 1
`define  STORE_CREDITS 1
`define  INIT_XUCR0   32'h00000C60  // 52:single-credit LS

`define  REGMODE 6               // 32/64b
`define  EFF_IFAR_ARCH  62
`define  EFF_IFAR_WIDTH  20
`define  EFF_IFAR   20
`define  REAL_IFAR_WIDTH  42

`define  gpr_t  3'b000
`define  cr_t  3'b001
`define  lr_t  3'b010
`define  ctr_t  3'b011
`define  xer_t  3'b100
`define  spr_t  3'b101
`define  axu0_t  3'b110
`define  axu1_t  3'b111

`define  ITAG_SIZE_ENC  7
`define  GPR_WIDTH  64
`define  GPR_WIDTH_ENC 6
`define  AXU_SPARE_ENC  3
`define  TYPE_WIDTH 3
`define  IBUFF_INSTR_WIDTH  70
`define  IBUFF_IFAR_WIDTH  20
`define  FXU0_PIPE_START 1
`define  FXU0_PIPE_END 8
`define  FXU1_PIPE_START 1
`define  FXU1_PIPE_END 5
`define  LQ_LOAD_PIPE_START 4
`define  LQ_LOAD_PIPE_END 8
`define  LQ_REL_PIPE_START 2
`define  LQ_REL_PIPE_END 4

//wtf: change for verilatorsim - didnt help
//`define  INIT_BHT  1			      // 0=> array init time set to 16 clocks, 1=> increased to 512 to init BHT
`define  INIT_BHT  0			      // 0=> array init time set to 16 clocks, 1=> increased to 512 to init BHT
//`define  INIT_IUCR0  16'h0000	   // BP disabled
`define  INIT_IUCR0  16'h00FA	   // BP enabled

`define  INIT_MASK  2'b10
`define  RELQ_INCLUDE  0		   // Reload Queue Included

`define  G_BRANCH_LEN  `EFF_IFAR_WIDTH + 1 + 1 + `EFF_IFAR_WIDTH + 3 + 18 + 1

//wtf: add completion stuff
/*
   assign spr_cpcr0_fx0_cnt = cpcr0_l2[35:39];
   assign spr_cpcr0_fx1_cnt = cpcr0_l2[43:47];
   assign spr_cpcr0_lq_cnt = cpcr0_l2[51:55];
   assign spr_cpcr0_sq_cnt = cpcr0_l2[59:63];
*/
`define INIT_CPCR0                  32'h0C0C100C   // 000a aaaa 000b bbbb 000c cccc 000d dddd   watermarks: a=fx0 b=fx1 c=ls d=sq ---- um p.543 wrong!; was this in vlog: hex 0C0C100C = 202117132
//`define INIT_CPCR0                  32'h01010201     // 1/1/2/1
/*
   assign spr_cpcr1_fu0_cnt = cpcr1_l2[43:47];
   assign spr_cpcr1_fu1_cnt = cpcr1_l2[51:55];
*/
`define INIT_CPCR1                  32'h000C0C00     // 0000 0000 000a aaaa 000b bbbb 0000 0000   credits: a=fx0 b=fx1 c=ls d=sq ---- um p.544 wrong!; was this in vlog: hex 000C0C00 = 789504
//`define INIT_CPCR1                  32'h00010100      // 1/1

// IERAT boot config entry values
`define  IERAT_BCFG_EPN_0TO15      0
`define  IERAT_BCFG_EPN_16TO31     0
`define  IERAT_BCFG_EPN_32TO47     (2 ** 16) - 1   // 1 for 64K, 65535 for 4G
`define  IERAT_BCFG_EPN_48TO51     (2 ** 4) - 1    // 15 for 64K or 4G
`define  IERAT_BCFG_RPN_22TO31     0               // (2 ** 10) - 1  for x3ff
`define  IERAT_BCFG_RPN_32TO47     (2 ** 16) - 1   // 1 for 64K, 8181 for 512M, 65535 for 4G
`define  IERAT_BCFG_RPN_48TO51     (2 ** 4) - 1    // 15 for 64K or 4G
`define  IERAT_BCFG_RPN2_32TO47    0               // 0 to match dd1 hardwired value; (2**16)-1 for same 64K page
`define  IERAT_BCFG_RPN2_48TO51    0               // 0 to match dd1 hardwired value;  (2**4)-2 for adjacent 4K page
`define  IERAT_BCFG_ATTR    0                      // u0-u3, endian

// DERAT boot config entry values
`define  DERAT_BCFG_EPN_0TO15      0
`define  DERAT_BCFG_EPN_16TO31     0
`define  DERAT_BCFG_EPN_32TO47     (2 ** 16) - 1   // 1 for 64K, 65535 for 4G
`define  DERAT_BCFG_EPN_48TO51     (2 ** 4) - 1    // 15 for 64K or 4G
`define  DERAT_BCFG_RPN_22TO31     0               // (2 ** 10) - 1  for x3ff
`define  DERAT_BCFG_RPN_32TO47     (2 ** 16) - 1   // 1 for 64K, 8191 for 512M, 65535 for 4G
`define  DERAT_BCFG_RPN_48TO51     (2 ** 4) - 1    // 15 for 64K or 4G
`define  DERAT_BCFG_RPN2_32TO47    0               // 0 to match dd1 hardwired value; (2**16)-1 for same 64K page
`define  DERAT_BCFG_RPN2_48TO51    0               // 0 to match dd1 hardwired value;  (2**4)-2 for adjacent 4K page
`define  DERAT_BCFG_ATTR    0                      // u0-u3, endian

// Do NOT add any defines below this line
`endif  //_tri_a2o_vh_
