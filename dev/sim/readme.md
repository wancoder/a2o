# Simulation

Building with cocotb, verilator, icarus...

```
cd coco
```

## cocotb + Icarus

* A2L2 python interface partially implemented
* original boot code makes it to jump to (missing) test
* makegtkw creates netlist

```
make -f Makefile.icarus run
...
  7353.00ns INFO     [00000919] C0: CP 0:00056C 000000000000056C
  7369.00ns INFO     [00000921] C0: CP 0:000570 0000000000000570
  7377.00ns INFO     [00000922] RELD tag=08 48000000480000FC6000000060000000 1of4 crit
  7385.00ns INFO     [00000923] RELD tag=08 60000000600000006000000060000000 2of4
  7393.00ns INFO     [00000924] RELD tag=08 60000000600000006000000060000000 3of4
  7401.00ns INFO     [00000925] RELD tag=08 60000000600000006000000060000000 4of4
  7433.00ns INFO     [00000929] T0 IFETCH 00000640 tag=09 len=6 WIMG:0 reld data:935
  7481.00ns INFO     [00000935] RELD tag=09 60000000600000006000000060000000 1of4 crit
  7481.00ns INFO     [00000935] C0: CP 0:000574 0000000000000574
  7489.00ns INFO     [00000936] RELD tag=09 60000000600000006000000060000000 2of4
  7497.00ns INFO     [00000937] RELD tag=09 60000000600000006000000060000000 3of4
  7505.00ns INFO     [00000938] RELD tag=09 60000000600000006000000060000000 4of4
  7593.00ns INFO     [00000949] C0: CP 0:000578 1:00057C 0000000000000578
  7697.00ns INFO     [00000962] C0: CP 0:000580 0000000000000580
  7793.00ns INFO     [00000974] C0: CP 0:000584 0000000000000584
  7801.00ns INFO     [00000975] T0 IFETCH 00000700 tag=08 len=6 WIMG:0 reld data:981
  7849.00ns INFO     [00000981] RELD tag=08 48000000480000FC6000000060000000 1of4 crit
  7857.00ns INFO     [00000982] RELD tag=08 60000000600000006000000060000000 2of4
  7857.00ns INFO     [00000982] C0: CP 0:000588 1:00058C 0000000000000588
  7865.00ns INFO     [00000983] RELD tag=08 60000000600000006000000060000000 3of4
  7873.00ns INFO     [00000984] RELD tag=08 60000000600000006000000060000000 4of4
  7905.00ns INFO     [00000988] T0 IFETCH 00000740 tag=09 len=6 WIMG:0 reld data:994
  7953.00ns INFO     [00000994] RELD tag=09 60000000600000006000000060000000 1of4 crit
  7961.00ns INFO     [00000995] RELD tag=09 60000000600000006000000060000000 2of4
  7969.00ns INFO     [00000996] RELD tag=09 60000000600000006000000060000000 3of4
  7977.00ns INFO     [00000997] RELD tag=09 60000000600000006000000060000000 4of4
  8001.00ns INFO     [00001000] ...tick...
  8009.00ns INFO     [00001001] T0 IFETCH 100004B0 tag=08 len=6 LE WIMG:0 reld data:1007
  8057.00ns INFO     [00001007] RELD tag=08 00000000000000000000000000000000 1of4
  8065.00ns INFO     [00001008] RELD tag=08 00000000000000000000000000000000 2of4
  8073.00ns INFO     [00001009] RELD tag=08 00000000000000000000000000000000 3of4
  8081.00ns INFO     [00001010] RELD tag=08 00000000000000000000000000000000 4of4 crit
  8113.00ns INFO     [00001014] T0 IFETCH 100004C0 tag=09 len=6 LE WIMG:0 reld data:1020
  8161.00ns INFO     [00001020] RELD tag=09 00000000000000000000000000000000 1of4 crit
  8169.00ns INFO     [00001021] RELD tag=09 00000000000000000000000000000000 2of4
  8177.00ns INFO     [00001022] RELD tag=09 00000000000000000000000000000000 3of4
  8185.00ns INFO     [00001023] RELD tag=09 00000000000000000000000000000000 4of4
  8257.00ns INFO     [00001032] T0 IFETCH 000000E0 tag=08 len=6 WIMG:0 reld data:1038
  8257.00ns INFO     Test stopped by this forked coroutine
  8257.00ns INFO     tb failed
                     Traceback (most recent call last):
                       File "/home/wtf/projects/a2o-opf/dev/sim/coco/A2L2.py", line 405, in A2L2Monitor
                         assert False, (f'{me}: Bad IFetch @={ra:08X}')  #wtf want this to end back in main code for summary
                     AssertionError: A2L2 Monitor: Bad IFetch @=000000E0
  8257.00ns INFO     **************************************************************************************
                     ** TEST                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                     **************************************************************************************
                     ** tb.tb                          FAIL        8257.00         154.07         53.59  **
                     **************************************************************************************
                     ** TESTS=0 PASS=0 FAIL=1 SKIP=0               8257.00         154.09         53.58  **
                     **************************************************************************************


```

## Verilator (can't build with coco so far)


* build and run a few hardcoded ops

```
verilator -cc --exe --trace --Mdir obj_dir --language 1364-2001 -Wno-fatal -Wno-LITENDIAN --error-limit 1  -Iverilog/work -Iverilog/trilib_clk1x -Iverilog/trilib -Iverilog/unisims c.v tb.cpp
make -C obj_dir -f Vc.mk Vc
obj_dir/Vc
Tracing enabled.
00000001Resetting...
00000001Thread stop=3
00000011Releasing reset.
00000201Thread stop=0
00000213 ac_an_req: T0 ra=FFFFFFF0
00000216 an_ac_rsp: data=00000000000000000000000048000002
00000236 ac_an_req: T0 ra=00000000
00000239 an_ac_rsp: data=48000400000000000000000000000000
00000251 ac_an_req: T0 ra=00000400
00000254 an_ac_rsp: data=382000017C366BA67C366BA67C3E6AA6
00000263 ac_an_req: T0 ra=00000410
00000266 an_ac_rsp: data=4C00012C2C0100003820066041820008
00000275 ac_an_req: T0 ra=00000420
00000278 an_ac_rsp: data=382101007C2903A64E80042000000000
00000287 ac_an_req: T0 ra=00000430
00000290 an_ac_rsp: data=00000000000000000000000000000000
00000299 ac_an_req: T0 ra=00000440
00000302 an_ac_rsp: data=00000000000000000000000000000000
00000311 ac_an_req: T0 ra=00000450
00000314 an_ac_rsp: data=00000000000000000000000000000000
00000319 ac_an_req: T0 ra=00000410
00000322 an_ac_rsp: data=4C00012C2C0100003820066041820008
00000331 ac_an_req: T0 ra=00000420
00000334 an_ac_rsp: data=382101007C2903A64E80042000000000
00000344 ac_an_req: T0 ra=00000420
00000347 an_ac_rsp: data=382101007C2903A64E80042000000000
00000356 ac_an_req: T0 ra=00000430
00000359 an_ac_rsp: data=00000000000000000000000000000000
00000369 ac_an_req: T0 ra=00000660
00000372 an_ac_rsp: data=48000040000000000000000000000000
00000384 ac_an_req: T0 ra=000006A0
00000387 an_ac_rsp: data=48000040000000000000000000000000
00000399 ac_an_req: T0 ra=000006E0
00000402 an_ac_rsp: data=48000040000000000000000000000000
00000414 ac_an_req: T0 ra=00000720
00000417 an_ac_rsp: data=48000040000000000000000000000000
00000429 ac_an_req: T0 ra=00000760
00000432 an_ac_rsp: data=48000040000000000000000000000000
00000444 ac_an_req: T0 ra=000007A0
00000447 an_ac_rsp: data=48000040000000000000000000000000
00000459 ac_an_req: T0 ra=000007E0
00000462 an_ac_rsp: data=48000040000000000000000000000000
00000474 ac_an_req: T0 ra=00000820
...
```