// simple verilator top
// uses a2owb with sim mem interface

#define TRACING

#include <cstddef>
#include <iostream>
#include <iomanip>

#include "verilated.h"
#include "Vc.h"

#ifdef TRACING
#include "verilated_vcd_c.h"
VerilatedVcdC *t;
#else
unsigned int t = 0;
#endif

/*
#include "uart/uartsim.h"
*/

Vc* m;

vluint64_t main_time = 0;     // in units of timeprecision used in verilog or --timescale-override
// what is it?  it changed to 941621251 after calling loadmem()

double sc_time_stamp() {      // $time in verilog
   return main_time;
}

const int resetCycle = 10;
const int threadRunCycle = 200;
const int runCycles = 1000;
const int hbCycles = 500;
const int threads = 1;  // needs a more realistic a2l2 data return to work in smt

int mem[16384][4];      // 16K QW

void loadmem(void) {
   int adr;
   mem[0x0000/4] = 0x48000400;
   adr = 0x400/4;

   mem[adr++] = threads == 1 ? 0x38200001 : 0x38200003;
   mem[adr++] = 0x7C366BA6;
   mem[adr++] = 0x7C366BA6;
   mem[adr++] = 0x7C3E6AA6;
   mem[adr++] = 0x4C00012C;
   mem[adr++] = 0x2C010000;
   mem[adr++] = 0x38200660;
   mem[adr++] = 0x41820008;
   mem[adr++] = 0x38210100;
   mem[adr++] = 0x7C2903A6;
   mem[adr++] = 0x4E800420;

}

// nclk = (clk,reset,clk2x,clk4x,-,-)

int main(int argc, char **argv) {
   using namespace std;

   loadmem();

   cout << setfill('0');

   Verilated::commandArgs(argc, argv);
   m = new Vc;

#ifdef TRACING
      Verilated::traceEverOn(true);
      t = new VerilatedVcdC;
      m->trace(t, 99);
      t->open("wtf.vcd");
      cout << "Tracing enabled." << endl;
#endif

   bool resetDone = false;
   unsigned int threadStop = 0x3;

   unsigned int tick = 0;
   unsigned int cycle = 1;
   unsigned int readPending = 0;
   unsigned int readAddr = 0;
   unsigned int readTag = 0;
   unsigned int readTID = 0;
   unsigned int countReads = 0;

   m->nclk = 0x3C;   // run 2x,4x = 1x
   cout << setw(8) << cycle << "Resetting..." << endl;

   m->an_ac_pm_thread_stop = threadStop;
   cout << setw(8) << cycle << "Thread stop=" << threadStop << endl;

   // can skip 4x with new gpr array
   // 1x=4/4 2x=2/2 4x=1/1
   //   1 1 1    7
   //   1 1 0    6
   //   1 0 1    5
   //   1 0 0    4
   //   0 1 1    3
   //   0 1 0    2
   //   0 0 1    1
   //   0 0 0    0
   // (insert reset)
   //const int clocks[8] = {11, 0, 11, 0, 11, 0, 11, 0}; // 2x,4x == 1x
   //const int clocks[8] = {11, 10, 9, 8, 3, 2, 1, 0};     // 1x, 2x, 4x
   //const int ticks1x = 8;
   const int clocks[4] = {10, 8, 2, 0};     // 1x, 2x
   const int ticks1x = 4;

   while (!Verilated::gotFinish()) {

      if (!resetDone && (cycle > resetCycle)) {
         m->nclk &= 0x2F;
         cout << setw(8) << cycle << "Releasing reset." << endl;
         resetDone = true;
      }

      if (threadStop && (cycle > threadRunCycle)) {
         threadStop = 0x0;
         m->an_ac_pm_thread_stop = threadStop;
         cout << setw(8) << cycle << "Thread stop=" << threadStop << endl;
      }

      m->nclk = (m->nclk & 0x10) | (clocks[tick % 8] << 2);
      tick++;
      m->eval();

      // bus is 1x clock
      if ((tick % ticks1x) == 0) {

         /*
            cout << setw(8) << cycle << " an_ac_rsp: data="<< hex << uppercase << setw(8) << m->an_ac_reld_data[3]
               << hex << uppercase << setw(8) << m->an_ac_reld_data[2]
               << hex << uppercase << setw(8) << m->an_ac_reld_data[1]
               << hex << uppercase << setw(8) << m->an_ac_reld_data[0]
               << dec << nouppercase << endl;
         */

      }

      // finish clock stuff
      if ((tick % ticks1x) == 0) {
         cycle++;
         if ((cycle % hbCycles) == 0) {
            cout << setw(8) << cycle << " ...tick..." << endl;
         }
      }
      #ifdef TRACING
      t->dump(tick);
      t->flush();
      #endif

      // check for fails

      // hit limit
      if (cycle > runCycles) {
         break;
      }

   }

#ifdef TRACING
   t->close();
#endif
   m->final();

   exit(EXIT_SUCCESS);

}