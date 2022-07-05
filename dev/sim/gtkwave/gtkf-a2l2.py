#!/usr/bin/python3
# gtkwave transaction filter

# interpret a2l2 (req) interface
# needs:
#   track multiple outstanding and out-of-order;
#   update to show active tag list (credits), etc.
#
# select the signals; F4; name it; format->binary; format->transaction filter; select the signals and create group

import sys
import tempfile
import subprocess

fi = sys.stdin
fo = sys.stdout
fe = sys.stderr

debug = False

def dbg(m):
   if debug:
      fe.write(m + '\n')
      fe.flush()

filterName = 'A2L2 Decode'
transColor = 'DarkRed'

colors = {
   #'default':'DeepSkyBlue',
   'default':'black',
   'data':'DarkGray',
   'bctr':'DarkOrange'
}

sigs = [None] * 30
sigNames = {
   'ac_an_req' : None,
   'ac_an_req_ra[22:63]' : 'RA',
   'ac_an_req_thread[0:2]' : 'T',
   'ac_an_req_ttype[0:5]' : 'TT',
   'ac_an_req_tag[0:5]' : 'Tag',
   'ac_an_req_wimg_w' : 'W',
   'ac_an_req_wimg_i' : 'I',
   'ac_an_req_wimg_m' : 'M',
   'ac_an_req_wimg_g' : 'G',
}
sigTypes = {
   'RA' : ('08X',),
   'T': ('X',),
   'TT' : ('02X',),
   'Tag' : ('02X',),
   'W' : ('nz', 'X'),
   'I' : ('nz', 'X'),
   'M' : ('nz', 'X'),
   'G' : ('nz', 'X'),
}

trans = []
numTrans = 0

class Sig():
   def __init__(self, name):
      self.name = name
      self.values = []
   def addValue(self, t, v):
      self.values.append((t,v))

class Trans():
   def __init__(self):
      self.timeReq = 0
      self.timeDVal = 0
      self.timeLast = 0
      self.props = {}

# the last value of each sig is in this transaction (req=1)
def addTrans(time):
   global numTrans
   t = Trans()
   t.timeReq = time
   for i in range(len(sigs)):
      if sigs[i] == None:
         continue
      t.props[sigs[i].name] = sigs[i].values[-1][1]
   trans.append(t)
   numTrans += 1

def main():

   t  = f'$name {filterName}\n'
   t += '#0\n'

   inDumpVars = False
   startTrans = False
   inTrans = False

   while True:

      l = fi.readline()
      if not l:
         return 0

      dbg(l)

      if l.startswith('#'):         # time
         if startTrans:
            dbg('start trans\n')
            addTrans(varTime)
            startTrans = False
            inTrans = True
         varTime = int(l[1:-1])
      elif inDumpVars:
         if l.startswith('$comment data_end'):
            inDumpVars = False
            if inTrans:
               addTrans(varTime)
               inTrans = False
         elif l.startswith('$'):    # ?
            pass
         else:                      # value will be either 'vec num' or 'bn' (b=bit,n=num)
            if ' ' in l:            # vector
               v = l.split()[0]
               if 'x' in v or 'z' in v:
                  v = '0'           # could mark it and check later
               elif v[0] == 'b':
                  v = hex(int(v[1:], 2))
               elif v[0] == 'x':
                  v = v[1:]
               n = int(l.split()[1])
            else:                   # bit
               v = l[0]
               n = int(l[1:])
            sigs[n-1].addValue(varTime, v)
            dbg(f'sig {n-1} {v}\n')
            if sigs[n-1].name == 'ac_an_req':
               dbg(f'transig: {n-1} {v}\n')
               if v == '1':
                  startTrans = True
                  dbg('about to start trans\n')
            elif sigs[n-1].name == 'an_ac_reld_data_vld':
               if v == '1':
                  trans[-1].timeDVal = varTime
                  trans[-1].timeLast = varTime
                  inTrans = False
      elif l.startswith('$var '):
         tokens = l.split()      # $var wire 3 2 ac_an_req_thread[0:2] $end  3=width 2=index
         n = int(tokens[3]) - 1
         sigs[n] = Sig(tokens[4])
      elif l.startswith('$dumpvars'):
         inDumpVars = True
      else:
         #t += '#' + str(i) + ' ' + l + '\n'
         pass

      if l.startswith('$comment data_end'):
         # a transaction starts every req=1 cycle
         t = ''
         for i in range(len(trans)):
            t += f'#{trans[i].timeReq} ?{transColor}?'
            for p in trans[i].props:
               if p in sigNames and sigNames[p] is not None:
                  n = sigNames[p]
                  if n in sigTypes and sigTypes[n][0] == 'nz':
                     if trans[i].props[p] == '1':
                        t += f'{n}:{int(trans[i].props[p], 16):{sigTypes[n][1]}} '
                  elif n in sigTypes:
                     dbg(f'{trans[i].props[p]}\n')
                     if n == 'T':
                        t += f'{n}{int(trans[i].props[p], 16):{sigTypes[n][0]}} '
                     elif n == 'TT' and trans[i].props[p] == '0x0':
                        t += 'IFETCH '
                     else:
                        t += f'{n}:{int(trans[i].props[p], 16):{sigTypes[n][0]}} '
                  else:
                     t += f'{n}:{trans[i].props[p]} '
            t += '\n'
            t += f'#{trans[i].timeLast}\n'   # may need to wait till next cyc in case req on back-back?
         t += '$finish\n'
         fo.write(f'{t}')
         fo.flush()


if __name__ == '__main__':
	sys.exit(main())

'''
rgb.c from gtkwave

static struct wave_rgb_color colors[] = {
WAVE_RGB_COLOR("alice blue", 240, 248, 255),
WAVE_RGB_COLOR("AliceBlue", 240, 248, 255),
WAVE_RGB_COLOR("antique white", 250, 235, 215),
WAVE_RGB_COLOR("AntiqueWhite", 250, 235, 215),
WAVE_RGB_COLOR("AntiqueWhite1", 255, 239, 219),
WAVE_RGB_COLOR("AntiqueWhite2", 238, 223, 204),
WAVE_RGB_COLOR("AntiqueWhite3", 205, 192, 176),
WAVE_RGB_COLOR("AntiqueWhite4", 139, 131, 120),
WAVE_RGB_COLOR("aquamarine", 127, 255, 212),
WAVE_RGB_COLOR("aquamarine1", 127, 255, 212),
WAVE_RGB_COLOR("aquamarine2", 118, 238, 198),
WAVE_RGB_COLOR("aquamarine3", 102, 205, 170),
WAVE_RGB_COLOR("aquamarine4", 69, 139, 116),
WAVE_RGB_COLOR("azure", 240, 255, 255),
WAVE_RGB_COLOR("azure1", 240, 255, 255),
WAVE_RGB_COLOR("azure2", 224, 238, 238),
WAVE_RGB_COLOR("azure3", 193, 205, 205),
WAVE_RGB_COLOR("azure4", 131, 139, 139),
WAVE_RGB_COLOR("beige", 245, 245, 220),
WAVE_RGB_COLOR("bisque", 255, 228, 196),
WAVE_RGB_COLOR("bisque1", 255, 228, 196),
WAVE_RGB_COLOR("bisque2", 238, 213, 183),
WAVE_RGB_COLOR("bisque3", 205, 183, 158),
WAVE_RGB_COLOR("bisque4", 139, 125, 107),
WAVE_RGB_COLOR("black", 0, 0, 0),
WAVE_RGB_COLOR("blanched almond", 255, 235, 205),
WAVE_RGB_COLOR("BlanchedAlmond", 255, 235, 205),
WAVE_RGB_COLOR("blue", 0, 0, 255),
WAVE_RGB_COLOR("blue violet", 138, 43, 226),
WAVE_RGB_COLOR("blue1", 0, 0, 255),
WAVE_RGB_COLOR("blue2", 0, 0, 238),
WAVE_RGB_COLOR("blue3", 0, 0, 205),
WAVE_RGB_COLOR("blue4", 0, 0, 139),
WAVE_RGB_COLOR("BlueViolet", 138, 43, 226),
WAVE_RGB_COLOR("brown", 165, 42, 42),
WAVE_RGB_COLOR("brown1", 255, 64, 64),
WAVE_RGB_COLOR("brown2", 238, 59, 59),
WAVE_RGB_COLOR("brown3", 205, 51, 51),
WAVE_RGB_COLOR("brown4", 139, 35, 35),
WAVE_RGB_COLOR("burlywood", 222, 184, 135),
WAVE_RGB_COLOR("burlywood1", 255, 211, 155),
WAVE_RGB_COLOR("burlywood2", 238, 197, 145),
WAVE_RGB_COLOR("burlywood3", 205, 170, 125),
WAVE_RGB_COLOR("burlywood4", 139, 115, 85),
WAVE_RGB_COLOR("cadet blue", 95, 158, 160),
WAVE_RGB_COLOR("CadetBlue", 95, 158, 160),
WAVE_RGB_COLOR("CadetBlue1", 152, 245, 255),
WAVE_RGB_COLOR("CadetBlue2", 142, 229, 238),
WAVE_RGB_COLOR("CadetBlue3", 122, 197, 205),
WAVE_RGB_COLOR("CadetBlue4", 83, 134, 139),
WAVE_RGB_COLOR("chartreuse", 127, 255, 0),
WAVE_RGB_COLOR("chartreuse1", 127, 255, 0),
WAVE_RGB_COLOR("chartreuse2", 118, 238, 0),
WAVE_RGB_COLOR("chartreuse3", 102, 205, 0),
WAVE_RGB_COLOR("chartreuse4", 69, 139, 0),
WAVE_RGB_COLOR("chocolate", 210, 105, 30),
WAVE_RGB_COLOR("chocolate1", 255, 127, 36),
WAVE_RGB_COLOR("chocolate2", 238, 118, 33),
WAVE_RGB_COLOR("chocolate3", 205, 102, 29),
WAVE_RGB_COLOR("chocolate4", 139, 69, 19),
WAVE_RGB_COLOR("coral", 255, 127, 80),
WAVE_RGB_COLOR("coral1", 255, 114, 86),
WAVE_RGB_COLOR("coral2", 238, 106, 80),
WAVE_RGB_COLOR("coral3", 205, 91, 69),
WAVE_RGB_COLOR("coral4", 139, 62, 47),
WAVE_RGB_COLOR("cornflower blue", 100, 149, 237),
WAVE_RGB_COLOR("CornflowerBlue", 100, 149, 237),
WAVE_RGB_COLOR("cornsilk", 255, 248, 220),
WAVE_RGB_COLOR("cornsilk1", 255, 248, 220),
WAVE_RGB_COLOR("cornsilk2", 238, 232, 205),
WAVE_RGB_COLOR("cornsilk3", 205, 200, 177),
WAVE_RGB_COLOR("cornsilk4", 139, 136, 120),
WAVE_RGB_COLOR("cyan", 0, 255, 255),
WAVE_RGB_COLOR("cyan1", 0, 255, 255),
WAVE_RGB_COLOR("cyan2", 0, 238, 238),
WAVE_RGB_COLOR("cyan3", 0, 205, 205),
WAVE_RGB_COLOR("cyan4", 0, 139, 139),
WAVE_RGB_COLOR("dark blue", 0, 0, 139),
WAVE_RGB_COLOR("dark cyan", 0, 139, 139),
WAVE_RGB_COLOR("dark goldenrod", 184, 134, 11),
WAVE_RGB_COLOR("dark gray", 169, 169, 169),
WAVE_RGB_COLOR("dark green", 0, 100, 0),
WAVE_RGB_COLOR("dark grey", 169, 169, 169),
WAVE_RGB_COLOR("dark khaki", 189, 183, 107),
WAVE_RGB_COLOR("dark magenta", 139, 0, 139),
WAVE_RGB_COLOR("dark olive green", 85, 107, 47),
WAVE_RGB_COLOR("dark orange", 255, 140, 0),
WAVE_RGB_COLOR("dark orchid", 153, 50, 204),
WAVE_RGB_COLOR("dark red", 139, 0, 0),
WAVE_RGB_COLOR("dark salmon", 233, 150, 122),
WAVE_RGB_COLOR("dark sea green", 143, 188, 143),
WAVE_RGB_COLOR("dark slate blue", 72, 61, 139),
WAVE_RGB_COLOR("dark slate gray", 47, 79, 79),
WAVE_RGB_COLOR("dark slate grey", 47, 79, 79),
WAVE_RGB_COLOR("dark turquoise", 0, 206, 209),
WAVE_RGB_COLOR("dark violet", 148, 0, 211),
WAVE_RGB_COLOR("DarkBlue", 0, 0, 139),
WAVE_RGB_COLOR("DarkCyan", 0, 139, 139),
WAVE_RGB_COLOR("DarkGoldenrod", 184, 134, 11),
WAVE_RGB_COLOR("DarkGoldenrod1", 255, 185, 15),
WAVE_RGB_COLOR("DarkGoldenrod2", 238, 173, 14),
WAVE_RGB_COLOR("DarkGoldenrod3", 205, 149, 12),
WAVE_RGB_COLOR("DarkGoldenrod4", 139, 101, 8),
WAVE_RGB_COLOR("DarkGray", 169, 169, 169),
WAVE_RGB_COLOR("DarkGreen", 0, 100, 0),
WAVE_RGB_COLOR("DarkGrey", 169, 169, 169),
WAVE_RGB_COLOR("DarkKhaki", 189, 183, 107),
WAVE_RGB_COLOR("DarkMagenta", 139, 0, 139),
WAVE_RGB_COLOR("DarkOliveGreen", 85, 107, 47),
WAVE_RGB_COLOR("DarkOliveGreen1", 202, 255, 112),
WAVE_RGB_COLOR("DarkOliveGreen2", 188, 238, 104),
WAVE_RGB_COLOR("DarkOliveGreen3", 162, 205, 90),
WAVE_RGB_COLOR("DarkOliveGreen4", 110, 139, 61),
WAVE_RGB_COLOR("DarkOrange", 255, 140, 0),
WAVE_RGB_COLOR("DarkOrange1", 255, 127, 0),
WAVE_RGB_COLOR("DarkOrange2", 238, 118, 0),
WAVE_RGB_COLOR("DarkOrange3", 205, 102, 0),
WAVE_RGB_COLOR("DarkOrange4", 139, 69, 0),
WAVE_RGB_COLOR("DarkOrchid", 153, 50, 204),
WAVE_RGB_COLOR("DarkOrchid1", 191, 62, 255),
WAVE_RGB_COLOR("DarkOrchid2", 178, 58, 238),
WAVE_RGB_COLOR("DarkOrchid3", 154, 50, 205),
WAVE_RGB_COLOR("DarkOrchid4", 104, 34, 139),
WAVE_RGB_COLOR("DarkRed", 139, 0, 0),
WAVE_RGB_COLOR("DarkSalmon", 233, 150, 122),
WAVE_RGB_COLOR("DarkSeaGreen", 143, 188, 143),
WAVE_RGB_COLOR("DarkSeaGreen1", 193, 255, 193),
WAVE_RGB_COLOR("DarkSeaGreen2", 180, 238, 180),
WAVE_RGB_COLOR("DarkSeaGreen3", 155, 205, 155),
WAVE_RGB_COLOR("DarkSeaGreen4", 105, 139, 105),
WAVE_RGB_COLOR("DarkSlateBlue", 72, 61, 139),
WAVE_RGB_COLOR("DarkSlateGray", 47, 79, 79),
WAVE_RGB_COLOR("DarkSlateGray1", 151, 255, 255),
WAVE_RGB_COLOR("DarkSlateGray2", 141, 238, 238),
WAVE_RGB_COLOR("DarkSlateGray3", 121, 205, 205),
WAVE_RGB_COLOR("DarkSlateGray4", 82, 139, 139),
WAVE_RGB_COLOR("DarkSlateGrey", 47, 79, 79),
WAVE_RGB_COLOR("DarkTurquoise", 0, 206, 209),
WAVE_RGB_COLOR("DarkViolet", 148, 0, 211),
WAVE_RGB_COLOR("deep pink", 255, 20, 147),
WAVE_RGB_COLOR("deep sky blue", 0, 191, 255),
WAVE_RGB_COLOR("DeepPink", 255, 20, 147),
WAVE_RGB_COLOR("DeepPink1", 255, 20, 147),
WAVE_RGB_COLOR("DeepPink2", 238, 18, 137),
WAVE_RGB_COLOR("DeepPink3", 205, 16, 118),
WAVE_RGB_COLOR("DeepPink4", 139, 10, 80),
WAVE_RGB_COLOR("DeepSkyBlue", 0, 191, 255),
WAVE_RGB_COLOR("DeepSkyBlue1", 0, 191, 255),
WAVE_RGB_COLOR("DeepSkyBlue2", 0, 178, 238),
WAVE_RGB_COLOR("DeepSkyBlue3", 0, 154, 205),
WAVE_RGB_COLOR("DeepSkyBlue4", 0, 104, 139),
WAVE_RGB_COLOR("dim gray", 105, 105, 105),
WAVE_RGB_COLOR("dim grey", 105, 105, 105),
WAVE_RGB_COLOR("DimGray", 105, 105, 105),
WAVE_RGB_COLOR("DimGrey", 105, 105, 105),
WAVE_RGB_COLOR("dodger blue", 30, 144, 255),
WAVE_RGB_COLOR("DodgerBlue", 30, 144, 255),
WAVE_RGB_COLOR("DodgerBlue1", 30, 144, 255),
WAVE_RGB_COLOR("DodgerBlue2", 28, 134, 238),
WAVE_RGB_COLOR("DodgerBlue3", 24, 116, 205),
WAVE_RGB_COLOR("DodgerBlue4", 16, 78, 139),
WAVE_RGB_COLOR("firebrick", 178, 34, 34),
WAVE_RGB_COLOR("firebrick1", 255, 48, 48),
WAVE_RGB_COLOR("firebrick2", 238, 44, 44),
WAVE_RGB_COLOR("firebrick3", 205, 38, 38),
WAVE_RGB_COLOR("firebrick4", 139, 26, 26),
WAVE_RGB_COLOR("floral white", 255, 250, 240),
WAVE_RGB_COLOR("FloralWhite", 255, 250, 240),
WAVE_RGB_COLOR("forest green", 34, 139, 34),
WAVE_RGB_COLOR("ForestGreen", 34, 139, 34),
WAVE_RGB_COLOR("gainsboro", 220, 220, 220),
WAVE_RGB_COLOR("ghost white", 248, 248, 255),
WAVE_RGB_COLOR("GhostWhite", 248, 248, 255),
WAVE_RGB_COLOR("gold", 255, 215, 0),
WAVE_RGB_COLOR("gold1", 255, 215, 0),
WAVE_RGB_COLOR("gold2", 238, 201, 0),
WAVE_RGB_COLOR("gold3", 205, 173, 0),
WAVE_RGB_COLOR("gold4", 139, 117, 0),
WAVE_RGB_COLOR("goldenrod", 218, 165, 32),
WAVE_RGB_COLOR("goldenrod1", 255, 193, 37),
WAVE_RGB_COLOR("goldenrod2", 238, 180, 34),
WAVE_RGB_COLOR("goldenrod3", 205, 155, 29),
WAVE_RGB_COLOR("goldenrod4", 139, 105, 20),
WAVE_RGB_COLOR("gray", 190, 190, 190),
WAVE_RGB_COLOR("gray0", 0, 0, 0),
WAVE_RGB_COLOR("gray1", 3, 3, 3),
WAVE_RGB_COLOR("gray10", 26, 26, 26),
WAVE_RGB_COLOR("gray100", 255, 255, 255),
WAVE_RGB_COLOR("gray11", 28, 28, 28),
WAVE_RGB_COLOR("gray12", 31, 31, 31),
WAVE_RGB_COLOR("gray13", 33, 33, 33),
WAVE_RGB_COLOR("gray14", 36, 36, 36),
WAVE_RGB_COLOR("gray15", 38, 38, 38),
WAVE_RGB_COLOR("gray16", 41, 41, 41),
WAVE_RGB_COLOR("gray17", 43, 43, 43),
WAVE_RGB_COLOR("gray18", 46, 46, 46),
WAVE_RGB_COLOR("gray19", 48, 48, 48),
WAVE_RGB_COLOR("gray2", 5, 5, 5),
WAVE_RGB_COLOR("gray20", 51, 51, 51),
WAVE_RGB_COLOR("gray21", 54, 54, 54),
WAVE_RGB_COLOR("gray22", 56, 56, 56),
WAVE_RGB_COLOR("gray23", 59, 59, 59),
WAVE_RGB_COLOR("gray24", 61, 61, 61),
WAVE_RGB_COLOR("gray25", 64, 64, 64),
WAVE_RGB_COLOR("gray26", 66, 66, 66),
WAVE_RGB_COLOR("gray27", 69, 69, 69),
WAVE_RGB_COLOR("gray28", 71, 71, 71),
WAVE_RGB_COLOR("gray29", 74, 74, 74),
WAVE_RGB_COLOR("gray3", 8, 8, 8),
WAVE_RGB_COLOR("gray30", 77, 77, 77),
WAVE_RGB_COLOR("gray31", 79, 79, 79),
WAVE_RGB_COLOR("gray32", 82, 82, 82),
WAVE_RGB_COLOR("gray33", 84, 84, 84),
WAVE_RGB_COLOR("gray34", 87, 87, 87),
WAVE_RGB_COLOR("gray35", 89, 89, 89),
WAVE_RGB_COLOR("gray36", 92, 92, 92),
WAVE_RGB_COLOR("gray37", 94, 94, 94),
WAVE_RGB_COLOR("gray38", 97, 97, 97),
WAVE_RGB_COLOR("gray39", 99, 99, 99),
WAVE_RGB_COLOR("gray4", 10, 10, 10),
WAVE_RGB_COLOR("gray40", 102, 102, 102),
WAVE_RGB_COLOR("gray41", 105, 105, 105),
WAVE_RGB_COLOR("gray42", 107, 107, 107),
WAVE_RGB_COLOR("gray43", 110, 110, 110),
WAVE_RGB_COLOR("gray44", 112, 112, 112),
WAVE_RGB_COLOR("gray45", 115, 115, 115),
WAVE_RGB_COLOR("gray46", 117, 117, 117),
WAVE_RGB_COLOR("gray47", 120, 120, 120),
WAVE_RGB_COLOR("gray48", 122, 122, 122),
WAVE_RGB_COLOR("gray49", 125, 125, 125),
WAVE_RGB_COLOR("gray5", 13, 13, 13),
WAVE_RGB_COLOR("gray50", 127, 127, 127),
WAVE_RGB_COLOR("gray51", 130, 130, 130),
WAVE_RGB_COLOR("gray52", 133, 133, 133),
WAVE_RGB_COLOR("gray53", 135, 135, 135),
WAVE_RGB_COLOR("gray54", 138, 138, 138),
WAVE_RGB_COLOR("gray55", 140, 140, 140),
WAVE_RGB_COLOR("gray56", 143, 143, 143),
WAVE_RGB_COLOR("gray57", 145, 145, 145),
WAVE_RGB_COLOR("gray58", 148, 148, 148),
WAVE_RGB_COLOR("gray59", 150, 150, 150),
WAVE_RGB_COLOR("gray6", 15, 15, 15),
WAVE_RGB_COLOR("gray60", 153, 153, 153),
WAVE_RGB_COLOR("gray61", 156, 156, 156),
WAVE_RGB_COLOR("gray62", 158, 158, 158),
WAVE_RGB_COLOR("gray63", 161, 161, 161),
WAVE_RGB_COLOR("gray64", 163, 163, 163),
WAVE_RGB_COLOR("gray65", 166, 166, 166),
WAVE_RGB_COLOR("gray66", 168, 168, 168),
WAVE_RGB_COLOR("gray67", 171, 171, 171),
WAVE_RGB_COLOR("gray68", 173, 173, 173),
WAVE_RGB_COLOR("gray69", 176, 176, 176),
WAVE_RGB_COLOR("gray7", 18, 18, 18),
WAVE_RGB_COLOR("gray70", 179, 179, 179),
WAVE_RGB_COLOR("gray71", 181, 181, 181),
WAVE_RGB_COLOR("gray72", 184, 184, 184),
WAVE_RGB_COLOR("gray73", 186, 186, 186),
WAVE_RGB_COLOR("gray74", 189, 189, 189),
WAVE_RGB_COLOR("gray75", 191, 191, 191),
WAVE_RGB_COLOR("gray76", 194, 194, 194),
WAVE_RGB_COLOR("gray77", 196, 196, 196),
WAVE_RGB_COLOR("gray78", 199, 199, 199),
WAVE_RGB_COLOR("gray79", 201, 201, 201),
WAVE_RGB_COLOR("gray8", 20, 20, 20),
WAVE_RGB_COLOR("gray80", 204, 204, 204),
WAVE_RGB_COLOR("gray81", 207, 207, 207),
WAVE_RGB_COLOR("gray82", 209, 209, 209),
WAVE_RGB_COLOR("gray83", 212, 212, 212),
WAVE_RGB_COLOR("gray84", 214, 214, 214),
WAVE_RGB_COLOR("gray85", 217, 217, 217),
WAVE_RGB_COLOR("gray86", 219, 219, 219),
WAVE_RGB_COLOR("gray87", 222, 222, 222),
WAVE_RGB_COLOR("gray88", 224, 224, 224),
WAVE_RGB_COLOR("gray89", 227, 227, 227),
WAVE_RGB_COLOR("gray9", 23, 23, 23),
WAVE_RGB_COLOR("gray90", 229, 229, 229),
WAVE_RGB_COLOR("gray91", 232, 232, 232),
WAVE_RGB_COLOR("gray92", 235, 235, 235),
WAVE_RGB_COLOR("gray93", 237, 237, 237),
WAVE_RGB_COLOR("gray94", 240, 240, 240),
WAVE_RGB_COLOR("gray95", 242, 242, 242),
WAVE_RGB_COLOR("gray96", 245, 245, 245),
WAVE_RGB_COLOR("gray97", 247, 247, 247),
WAVE_RGB_COLOR("gray98", 250, 250, 250),
WAVE_RGB_COLOR("gray99", 252, 252, 252),
WAVE_RGB_COLOR("green", 0, 255, 0),
WAVE_RGB_COLOR("green yellow", 173, 255, 47),
WAVE_RGB_COLOR("green1", 0, 255, 0),
WAVE_RGB_COLOR("green2", 0, 238, 0),
WAVE_RGB_COLOR("green3", 0, 205, 0),
WAVE_RGB_COLOR("green4", 0, 139, 0),
WAVE_RGB_COLOR("GreenYellow", 173, 255, 47),
WAVE_RGB_COLOR("grey", 190, 190, 190),
WAVE_RGB_COLOR("grey0", 0, 0, 0),
WAVE_RGB_COLOR("grey1", 3, 3, 3),
WAVE_RGB_COLOR("grey10", 26, 26, 26),
WAVE_RGB_COLOR("grey100", 255, 255, 255),
WAVE_RGB_COLOR("grey11", 28, 28, 28),
WAVE_RGB_COLOR("grey12", 31, 31, 31),
WAVE_RGB_COLOR("grey13", 33, 33, 33),
WAVE_RGB_COLOR("grey14", 36, 36, 36),
WAVE_RGB_COLOR("grey15", 38, 38, 38),
WAVE_RGB_COLOR("grey16", 41, 41, 41),
WAVE_RGB_COLOR("grey17", 43, 43, 43),
WAVE_RGB_COLOR("grey18", 46, 46, 46),
WAVE_RGB_COLOR("grey19", 48, 48, 48),
WAVE_RGB_COLOR("grey2", 5, 5, 5),
WAVE_RGB_COLOR("grey20", 51, 51, 51),
WAVE_RGB_COLOR("grey21", 54, 54, 54),
WAVE_RGB_COLOR("grey22", 56, 56, 56),
WAVE_RGB_COLOR("grey23", 59, 59, 59),
WAVE_RGB_COLOR("grey24", 61, 61, 61),
WAVE_RGB_COLOR("grey25", 64, 64, 64),
WAVE_RGB_COLOR("grey26", 66, 66, 66),
WAVE_RGB_COLOR("grey27", 69, 69, 69),
WAVE_RGB_COLOR("grey28", 71, 71, 71),
WAVE_RGB_COLOR("grey29", 74, 74, 74),
WAVE_RGB_COLOR("grey3", 8, 8, 8),
WAVE_RGB_COLOR("grey30", 77, 77, 77),
WAVE_RGB_COLOR("grey31", 79, 79, 79),
WAVE_RGB_COLOR("grey32", 82, 82, 82),
WAVE_RGB_COLOR("grey33", 84, 84, 84),
WAVE_RGB_COLOR("grey34", 87, 87, 87),
WAVE_RGB_COLOR("grey35", 89, 89, 89),
WAVE_RGB_COLOR("grey36", 92, 92, 92),
WAVE_RGB_COLOR("grey37", 94, 94, 94),
WAVE_RGB_COLOR("grey38", 97, 97, 97),
WAVE_RGB_COLOR("grey39", 99, 99, 99),
WAVE_RGB_COLOR("grey4", 10, 10, 10),
WAVE_RGB_COLOR("grey40", 102, 102, 102),
WAVE_RGB_COLOR("grey41", 105, 105, 105),
WAVE_RGB_COLOR("grey42", 107, 107, 107),
WAVE_RGB_COLOR("grey43", 110, 110, 110),
WAVE_RGB_COLOR("grey44", 112, 112, 112),
WAVE_RGB_COLOR("grey45", 115, 115, 115),
WAVE_RGB_COLOR("grey46", 117, 117, 117),
WAVE_RGB_COLOR("grey47", 120, 120, 120),
WAVE_RGB_COLOR("grey48", 122, 122, 122),
WAVE_RGB_COLOR("grey49", 125, 125, 125),
WAVE_RGB_COLOR("grey5", 13, 13, 13),
WAVE_RGB_COLOR("grey50", 127, 127, 127),
WAVE_RGB_COLOR("grey51", 130, 130, 130),
WAVE_RGB_COLOR("grey52", 133, 133, 133),
WAVE_RGB_COLOR("grey53", 135, 135, 135),
WAVE_RGB_COLOR("grey54", 138, 138, 138),
WAVE_RGB_COLOR("grey55", 140, 140, 140),
WAVE_RGB_COLOR("grey56", 143, 143, 143),
WAVE_RGB_COLOR("grey57", 145, 145, 145),
WAVE_RGB_COLOR("grey58", 148, 148, 148),
WAVE_RGB_COLOR("grey59", 150, 150, 150),
WAVE_RGB_COLOR("grey6", 15, 15, 15),
WAVE_RGB_COLOR("grey60", 153, 153, 153),
WAVE_RGB_COLOR("grey61", 156, 156, 156),
WAVE_RGB_COLOR("grey62", 158, 158, 158),
WAVE_RGB_COLOR("grey63", 161, 161, 161),
WAVE_RGB_COLOR("grey64", 163, 163, 163),
WAVE_RGB_COLOR("grey65", 166, 166, 166),
WAVE_RGB_COLOR("grey66", 168, 168, 168),
WAVE_RGB_COLOR("grey67", 171, 171, 171),
WAVE_RGB_COLOR("grey68", 173, 173, 173),
WAVE_RGB_COLOR("grey69", 176, 176, 176),
WAVE_RGB_COLOR("grey7", 18, 18, 18),
WAVE_RGB_COLOR("grey70", 179, 179, 179),
WAVE_RGB_COLOR("grey71", 181, 181, 181),
WAVE_RGB_COLOR("grey72", 184, 184, 184),
WAVE_RGB_COLOR("grey73", 186, 186, 186),
WAVE_RGB_COLOR("grey74", 189, 189, 189),
WAVE_RGB_COLOR("grey75", 191, 191, 191),
WAVE_RGB_COLOR("grey76", 194, 194, 194),
WAVE_RGB_COLOR("grey77", 196, 196, 196),
WAVE_RGB_COLOR("grey78", 199, 199, 199),
WAVE_RGB_COLOR("grey79", 201, 201, 201),
WAVE_RGB_COLOR("grey8", 20, 20, 20),
WAVE_RGB_COLOR("grey80", 204, 204, 204),
WAVE_RGB_COLOR("grey81", 207, 207, 207),
WAVE_RGB_COLOR("grey82", 209, 209, 209),
WAVE_RGB_COLOR("grey83", 212, 212, 212),
WAVE_RGB_COLOR("grey84", 214, 214, 214),
WAVE_RGB_COLOR("grey85", 217, 217, 217),
WAVE_RGB_COLOR("grey86", 219, 219, 219),
WAVE_RGB_COLOR("grey87", 222, 222, 222),
WAVE_RGB_COLOR("grey88", 224, 224, 224),
WAVE_RGB_COLOR("grey89", 227, 227, 227),
WAVE_RGB_COLOR("grey9", 23, 23, 23),
WAVE_RGB_COLOR("grey90", 229, 229, 229),
WAVE_RGB_COLOR("grey91", 232, 232, 232),
WAVE_RGB_COLOR("grey92", 235, 235, 235),
WAVE_RGB_COLOR("grey93", 237, 237, 237),
WAVE_RGB_COLOR("grey94", 240, 240, 240),
WAVE_RGB_COLOR("grey95", 242, 242, 242),
WAVE_RGB_COLOR("grey96", 245, 245, 245),
WAVE_RGB_COLOR("grey97", 247, 247, 247),
WAVE_RGB_COLOR("grey98", 250, 250, 250),
WAVE_RGB_COLOR("grey99", 252, 252, 252),
WAVE_RGB_COLOR("honeydew", 240, 255, 240),
WAVE_RGB_COLOR("honeydew1", 240, 255, 240),
WAVE_RGB_COLOR("honeydew2", 224, 238, 224),
WAVE_RGB_COLOR("honeydew3", 193, 205, 193),
WAVE_RGB_COLOR("honeydew4", 131, 139, 131),
WAVE_RGB_COLOR("hot pink", 255, 105, 180),
WAVE_RGB_COLOR("HotPink", 255, 105, 180),
WAVE_RGB_COLOR("HotPink1", 255, 110, 180),
WAVE_RGB_COLOR("HotPink2", 238, 106, 167),
WAVE_RGB_COLOR("HotPink3", 205, 96, 144),
WAVE_RGB_COLOR("HotPink4", 139, 58, 98),
WAVE_RGB_COLOR("indian red", 205, 92, 92),
WAVE_RGB_COLOR("IndianRed", 205, 92, 92),
WAVE_RGB_COLOR("IndianRed1", 255, 106, 106),
WAVE_RGB_COLOR("IndianRed2", 238, 99, 99),
WAVE_RGB_COLOR("IndianRed3", 205, 85, 85),
WAVE_RGB_COLOR("IndianRed4", 139, 58, 58),
WAVE_RGB_COLOR("ivory", 255, 255, 240),
WAVE_RGB_COLOR("ivory1", 255, 255, 240),
WAVE_RGB_COLOR("ivory2", 238, 238, 224),
WAVE_RGB_COLOR("ivory3", 205, 205, 193),
WAVE_RGB_COLOR("ivory4", 139, 139, 131),
WAVE_RGB_COLOR("khaki", 240, 230, 140),
WAVE_RGB_COLOR("khaki1", 255, 246, 143),
WAVE_RGB_COLOR("khaki2", 238, 230, 133),
WAVE_RGB_COLOR("khaki3", 205, 198, 115),
WAVE_RGB_COLOR("khaki4", 139, 134, 78),
WAVE_RGB_COLOR("lavender", 230, 230, 250),
WAVE_RGB_COLOR("lavender blush", 255, 240, 245),
WAVE_RGB_COLOR("LavenderBlush", 255, 240, 245),
WAVE_RGB_COLOR("LavenderBlush1", 255, 240, 245),
WAVE_RGB_COLOR("LavenderBlush2", 238, 224, 229),
WAVE_RGB_COLOR("LavenderBlush3", 205, 193, 197),
WAVE_RGB_COLOR("LavenderBlush4", 139, 131, 134),
WAVE_RGB_COLOR("lawn green", 124, 252, 0),
WAVE_RGB_COLOR("LawnGreen", 124, 252, 0),
WAVE_RGB_COLOR("lemon chiffon", 255, 250, 205),
WAVE_RGB_COLOR("LemonChiffon", 255, 250, 205),
WAVE_RGB_COLOR("LemonChiffon1", 255, 250, 205),
WAVE_RGB_COLOR("LemonChiffon2", 238, 233, 191),
WAVE_RGB_COLOR("LemonChiffon3", 205, 201, 165),
WAVE_RGB_COLOR("LemonChiffon4", 139, 137, 112),
WAVE_RGB_COLOR("light blue", 173, 216, 230),
WAVE_RGB_COLOR("light coral", 240, 128, 128),
WAVE_RGB_COLOR("light cyan", 224, 255, 255),
WAVE_RGB_COLOR("light goldenrod", 238, 221, 130),
WAVE_RGB_COLOR("light goldenrod yellow", 250, 250, 210),
WAVE_RGB_COLOR("light gray", 211, 211, 211),
WAVE_RGB_COLOR("light green", 144, 238, 144),
WAVE_RGB_COLOR("light grey", 211, 211, 211),
WAVE_RGB_COLOR("light pink", 255, 182, 193),
WAVE_RGB_COLOR("light salmon", 255, 160, 122),
WAVE_RGB_COLOR("light sea green", 32, 178, 170),
WAVE_RGB_COLOR("light sky blue", 135, 206, 250),
WAVE_RGB_COLOR("light slate blue", 132, 112, 255),
WAVE_RGB_COLOR("light slate gray", 119, 136, 153),
WAVE_RGB_COLOR("light slate grey", 119, 136, 153),
WAVE_RGB_COLOR("light steel blue", 176, 196, 222),
WAVE_RGB_COLOR("light yellow", 255, 255, 224),
WAVE_RGB_COLOR("LightBlue", 173, 216, 230),
WAVE_RGB_COLOR("LightBlue1", 191, 239, 255),
WAVE_RGB_COLOR("LightBlue2", 178, 223, 238),
WAVE_RGB_COLOR("LightBlue3", 154, 192, 205),
WAVE_RGB_COLOR("LightBlue4", 104, 131, 139),
WAVE_RGB_COLOR("LightCoral", 240, 128, 128),
WAVE_RGB_COLOR("LightCyan", 224, 255, 255),
WAVE_RGB_COLOR("LightCyan1", 224, 255, 255),
WAVE_RGB_COLOR("LightCyan2", 209, 238, 238),
WAVE_RGB_COLOR("LightCyan3", 180, 205, 205),
WAVE_RGB_COLOR("LightCyan4", 122, 139, 139),
WAVE_RGB_COLOR("LightGoldenrod", 238, 221, 130),
WAVE_RGB_COLOR("LightGoldenrod1", 255, 236, 139),
WAVE_RGB_COLOR("LightGoldenrod2", 238, 220, 130),
WAVE_RGB_COLOR("LightGoldenrod3", 205, 190, 112),
WAVE_RGB_COLOR("LightGoldenrod4", 139, 129, 76),
WAVE_RGB_COLOR("LightGoldenrodYellow", 250, 250, 210),
WAVE_RGB_COLOR("LightGray", 211, 211, 211),
WAVE_RGB_COLOR("LightGreen", 144, 238, 144),
WAVE_RGB_COLOR("LightGrey", 211, 211, 211),
WAVE_RGB_COLOR("LightPink", 255, 182, 193),
WAVE_RGB_COLOR("LightPink1", 255, 174, 185),
WAVE_RGB_COLOR("LightPink2", 238, 162, 173),
WAVE_RGB_COLOR("LightPink3", 205, 140, 149),
WAVE_RGB_COLOR("LightPink4", 139, 95, 101),
WAVE_RGB_COLOR("LightSalmon", 255, 160, 122),
WAVE_RGB_COLOR("LightSalmon1", 255, 160, 122),
WAVE_RGB_COLOR("LightSalmon2", 238, 149, 114),
WAVE_RGB_COLOR("LightSalmon3", 205, 129, 98),
WAVE_RGB_COLOR("LightSalmon4", 139, 87, 66),
WAVE_RGB_COLOR("LightSeaGreen", 32, 178, 170),
WAVE_RGB_COLOR("LightSkyBlue", 135, 206, 250),
WAVE_RGB_COLOR("LightSkyBlue1", 176, 226, 255),
WAVE_RGB_COLOR("LightSkyBlue2", 164, 211, 238),
WAVE_RGB_COLOR("LightSkyBlue3", 141, 182, 205),
WAVE_RGB_COLOR("LightSkyBlue4", 96, 123, 139),
WAVE_RGB_COLOR("LightSlateBlue", 132, 112, 255),
WAVE_RGB_COLOR("LightSlateGray", 119, 136, 153),
WAVE_RGB_COLOR("LightSlateGrey", 119, 136, 153),
WAVE_RGB_COLOR("LightSteelBlue", 176, 196, 222),
WAVE_RGB_COLOR("LightSteelBlue1", 202, 225, 255),
WAVE_RGB_COLOR("LightSteelBlue2", 188, 210, 238),
WAVE_RGB_COLOR("LightSteelBlue3", 162, 181, 205),
WAVE_RGB_COLOR("LightSteelBlue4", 110, 123, 139),
WAVE_RGB_COLOR("LightYellow", 255, 255, 224),
WAVE_RGB_COLOR("LightYellow1", 255, 255, 224),
WAVE_RGB_COLOR("LightYellow2", 238, 238, 209),
WAVE_RGB_COLOR("LightYellow3", 205, 205, 180),
WAVE_RGB_COLOR("LightYellow4", 139, 139, 122),
WAVE_RGB_COLOR("lime green", 50, 205, 50),
WAVE_RGB_COLOR("LimeGreen", 50, 205, 50),
WAVE_RGB_COLOR("linen", 250, 240, 230),
WAVE_RGB_COLOR("magenta", 255, 0, 255),
WAVE_RGB_COLOR("magenta1", 255, 0, 255),
WAVE_RGB_COLOR("magenta2", 238, 0, 238),
WAVE_RGB_COLOR("magenta3", 205, 0, 205),
WAVE_RGB_COLOR("magenta4", 139, 0, 139),
WAVE_RGB_COLOR("maroon", 176, 48, 96),
WAVE_RGB_COLOR("maroon1", 255, 52, 179),
WAVE_RGB_COLOR("maroon2", 238, 48, 167),
WAVE_RGB_COLOR("maroon3", 205, 41, 144),
WAVE_RGB_COLOR("maroon4", 139, 28, 98),
WAVE_RGB_COLOR("medium aquamarine", 102, 205, 170),
WAVE_RGB_COLOR("medium blue", 0, 0, 205),
WAVE_RGB_COLOR("medium orchid", 186, 85, 211),
WAVE_RGB_COLOR("medium purple", 147, 112, 219),
WAVE_RGB_COLOR("medium sea green", 60, 179, 113),
WAVE_RGB_COLOR("medium slate blue", 123, 104, 238),
WAVE_RGB_COLOR("medium spring green", 0, 250, 154),
WAVE_RGB_COLOR("medium turquoise", 72, 209, 204),
WAVE_RGB_COLOR("medium violet red", 199, 21, 133),
WAVE_RGB_COLOR("MediumAquamarine", 102, 205, 170),
WAVE_RGB_COLOR("MediumBlue", 0, 0, 205),
WAVE_RGB_COLOR("MediumOrchid", 186, 85, 211),
WAVE_RGB_COLOR("MediumOrchid1", 224, 102, 255),
WAVE_RGB_COLOR("MediumOrchid2", 209, 95, 238),
WAVE_RGB_COLOR("MediumOrchid3", 180, 82, 205),
WAVE_RGB_COLOR("MediumOrchid4", 122, 55, 139),
WAVE_RGB_COLOR("MediumPurple", 147, 112, 219),
WAVE_RGB_COLOR("MediumPurple1", 171, 130, 255),
WAVE_RGB_COLOR("MediumPurple2", 159, 121, 238),
WAVE_RGB_COLOR("MediumPurple3", 137, 104, 205),
WAVE_RGB_COLOR("MediumPurple4", 93, 71, 139),
WAVE_RGB_COLOR("MediumSeaGreen", 60, 179, 113),
WAVE_RGB_COLOR("MediumSlateBlue", 123, 104, 238),
WAVE_RGB_COLOR("MediumSpringGreen", 0, 250, 154),
WAVE_RGB_COLOR("MediumTurquoise", 72, 209, 204),
WAVE_RGB_COLOR("MediumVioletRed", 199, 21, 133),
WAVE_RGB_COLOR("midnight blue", 25, 25, 112),
WAVE_RGB_COLOR("MidnightBlue", 25, 25, 112),
WAVE_RGB_COLOR("mint cream", 245, 255, 250),
WAVE_RGB_COLOR("MintCream", 245, 255, 250),
WAVE_RGB_COLOR("misty rose", 255, 228, 225),
WAVE_RGB_COLOR("MistyRose", 255, 228, 225),
WAVE_RGB_COLOR("MistyRose1", 255, 228, 225),
WAVE_RGB_COLOR("MistyRose2", 238, 213, 210),
WAVE_RGB_COLOR("MistyRose3", 205, 183, 181),
WAVE_RGB_COLOR("MistyRose4", 139, 125, 123),
WAVE_RGB_COLOR("moccasin", 255, 228, 181),
WAVE_RGB_COLOR("navajo white", 255, 222, 173),
WAVE_RGB_COLOR("NavajoWhite", 255, 222, 173),
WAVE_RGB_COLOR("NavajoWhite1", 255, 222, 173),
WAVE_RGB_COLOR("NavajoWhite2", 238, 207, 161),
WAVE_RGB_COLOR("NavajoWhite3", 205, 179, 139),
WAVE_RGB_COLOR("NavajoWhite4", 139, 121, 94),
WAVE_RGB_COLOR("navy", 0, 0, 128),
WAVE_RGB_COLOR("navy blue", 0, 0, 128),
WAVE_RGB_COLOR("NavyBlue", 0, 0, 128),
WAVE_RGB_COLOR("old lace", 253, 245, 230),
WAVE_RGB_COLOR("OldLace", 253, 245, 230),
WAVE_RGB_COLOR("olive drab", 107, 142, 35),
WAVE_RGB_COLOR("OliveDrab", 107, 142, 35),
WAVE_RGB_COLOR("OliveDrab1", 192, 255, 62),
WAVE_RGB_COLOR("OliveDrab2", 179, 238, 58),
WAVE_RGB_COLOR("OliveDrab3", 154, 205, 50),
WAVE_RGB_COLOR("OliveDrab4", 105, 139, 34),
WAVE_RGB_COLOR("orange", 255, 165, 0),
WAVE_RGB_COLOR("orange red", 255, 69, 0),
WAVE_RGB_COLOR("orange1", 255, 165, 0),
WAVE_RGB_COLOR("orange2", 238, 154, 0),
WAVE_RGB_COLOR("orange3", 205, 133, 0),
WAVE_RGB_COLOR("orange4", 139, 90, 0),
WAVE_RGB_COLOR("OrangeRed", 255, 69, 0),
WAVE_RGB_COLOR("OrangeRed1", 255, 69, 0),
WAVE_RGB_COLOR("OrangeRed2", 238, 64, 0),
WAVE_RGB_COLOR("OrangeRed3", 205, 55, 0),
WAVE_RGB_COLOR("OrangeRed4", 139, 37, 0),
WAVE_RGB_COLOR("orchid", 218, 112, 214),
WAVE_RGB_COLOR("orchid1", 255, 131, 250),
WAVE_RGB_COLOR("orchid2", 238, 122, 233),
WAVE_RGB_COLOR("orchid3", 205, 105, 201),
WAVE_RGB_COLOR("orchid4", 139, 71, 137),
WAVE_RGB_COLOR("pale goldenrod", 238, 232, 170),
WAVE_RGB_COLOR("pale green", 152, 251, 152),
WAVE_RGB_COLOR("pale turquoise", 175, 238, 238),
WAVE_RGB_COLOR("pale violet red", 219, 112, 147),
WAVE_RGB_COLOR("PaleGoldenrod", 238, 232, 170),
WAVE_RGB_COLOR("PaleGreen", 152, 251, 152),
WAVE_RGB_COLOR("PaleGreen1", 154, 255, 154),
WAVE_RGB_COLOR("PaleGreen2", 144, 238, 144),
WAVE_RGB_COLOR("PaleGreen3", 124, 205, 124),
WAVE_RGB_COLOR("PaleGreen4", 84, 139, 84),
WAVE_RGB_COLOR("PaleTurquoise", 175, 238, 238),
WAVE_RGB_COLOR("PaleTurquoise1", 187, 255, 255),
WAVE_RGB_COLOR("PaleTurquoise2", 174, 238, 238),
WAVE_RGB_COLOR("PaleTurquoise3", 150, 205, 205),
WAVE_RGB_COLOR("PaleTurquoise4", 102, 139, 139),
WAVE_RGB_COLOR("PaleVioletRed", 219, 112, 147),
WAVE_RGB_COLOR("PaleVioletRed1", 255, 130, 171),
WAVE_RGB_COLOR("PaleVioletRed2", 238, 121, 159),
WAVE_RGB_COLOR("PaleVioletRed3", 205, 104, 137),
WAVE_RGB_COLOR("PaleVioletRed4", 139, 71, 93),
WAVE_RGB_COLOR("papaya whip", 255, 239, 213),
WAVE_RGB_COLOR("PapayaWhip", 255, 239, 213),
WAVE_RGB_COLOR("peach puff", 255, 218, 185),
WAVE_RGB_COLOR("PeachPuff", 255, 218, 185),
WAVE_RGB_COLOR("PeachPuff1", 255, 218, 185),
WAVE_RGB_COLOR("PeachPuff2", 238, 203, 173),
WAVE_RGB_COLOR("PeachPuff3", 205, 175, 149),
WAVE_RGB_COLOR("PeachPuff4", 139, 119, 101),
WAVE_RGB_COLOR("peru", 205, 133, 63),
WAVE_RGB_COLOR("pink", 255, 192, 203),
WAVE_RGB_COLOR("pink1", 255, 181, 197),
WAVE_RGB_COLOR("pink2", 238, 169, 184),
WAVE_RGB_COLOR("pink3", 205, 145, 158),
WAVE_RGB_COLOR("pink4", 139, 99, 108),
WAVE_RGB_COLOR("plum", 221, 160, 221),
WAVE_RGB_COLOR("plum1", 255, 187, 255),
WAVE_RGB_COLOR("plum2", 238, 174, 238),
WAVE_RGB_COLOR("plum3", 205, 150, 205),
WAVE_RGB_COLOR("plum4", 139, 102, 139),
WAVE_RGB_COLOR("powder blue", 176, 224, 230),
WAVE_RGB_COLOR("PowderBlue", 176, 224, 230),
WAVE_RGB_COLOR("purple", 160, 32, 240),
WAVE_RGB_COLOR("purple1", 155, 48, 255),
WAVE_RGB_COLOR("purple2", 145, 44, 238),
WAVE_RGB_COLOR("purple3", 125, 38, 205),
WAVE_RGB_COLOR("purple4", 85, 26, 139),
WAVE_RGB_COLOR("red", 255, 0, 0),
WAVE_RGB_COLOR("red1", 255, 0, 0),
WAVE_RGB_COLOR("red2", 238, 0, 0),
WAVE_RGB_COLOR("red3", 205, 0, 0),
WAVE_RGB_COLOR("red4", 139, 0, 0),
WAVE_RGB_COLOR("rosy brown", 188, 143, 143),
WAVE_RGB_COLOR("RosyBrown", 188, 143, 143),
WAVE_RGB_COLOR("RosyBrown1", 255, 193, 193),
WAVE_RGB_COLOR("RosyBrown2", 238, 180, 180),
WAVE_RGB_COLOR("RosyBrown3", 205, 155, 155),
WAVE_RGB_COLOR("RosyBrown4", 139, 105, 105),
WAVE_RGB_COLOR("royal blue", 65, 105, 225),
WAVE_RGB_COLOR("RoyalBlue", 65, 105, 225),
WAVE_RGB_COLOR("RoyalBlue1", 72, 118, 255),
WAVE_RGB_COLOR("RoyalBlue2", 67, 110, 238),
WAVE_RGB_COLOR("RoyalBlue3", 58, 95, 205),
WAVE_RGB_COLOR("RoyalBlue4", 39, 64, 139),
WAVE_RGB_COLOR("saddle brown", 139, 69, 19),
WAVE_RGB_COLOR("SaddleBrown", 139, 69, 19),
WAVE_RGB_COLOR("salmon", 250, 128, 114),
WAVE_RGB_COLOR("salmon1", 255, 140, 105),
WAVE_RGB_COLOR("salmon2", 238, 130, 98),
WAVE_RGB_COLOR("salmon3", 205, 112, 84),
WAVE_RGB_COLOR("salmon4", 139, 76, 57),
WAVE_RGB_COLOR("sandy brown", 244, 164, 96),
WAVE_RGB_COLOR("SandyBrown", 244, 164, 96),
WAVE_RGB_COLOR("sea green", 46, 139, 87),
WAVE_RGB_COLOR("SeaGreen", 46, 139, 87),
WAVE_RGB_COLOR("SeaGreen1", 84, 255, 159),
WAVE_RGB_COLOR("SeaGreen2", 78, 238, 148),
WAVE_RGB_COLOR("SeaGreen3", 67, 205, 128),
WAVE_RGB_COLOR("SeaGreen4", 46, 139, 87),
WAVE_RGB_COLOR("seashell", 255, 245, 238),
WAVE_RGB_COLOR("seashell1", 255, 245, 238),
WAVE_RGB_COLOR("seashell2", 238, 229, 222),
WAVE_RGB_COLOR("seashell3", 205, 197, 191),
WAVE_RGB_COLOR("seashell4", 139, 134, 130),
WAVE_RGB_COLOR("sienna", 160, 82, 45),
WAVE_RGB_COLOR("sienna1", 255, 130, 71),
WAVE_RGB_COLOR("sienna2", 238, 121, 66),
WAVE_RGB_COLOR("sienna3", 205, 104, 57),
WAVE_RGB_COLOR("sienna4", 139, 71, 38),
WAVE_RGB_COLOR("sky blue", 135, 206, 235),
WAVE_RGB_COLOR("SkyBlue", 135, 206, 235),
WAVE_RGB_COLOR("SkyBlue1", 135, 206, 255),
WAVE_RGB_COLOR("SkyBlue2", 126, 192, 238),
WAVE_RGB_COLOR("SkyBlue3", 108, 166, 205),
WAVE_RGB_COLOR("SkyBlue4", 74, 112, 139),
WAVE_RGB_COLOR("slate blue", 106, 90, 205),
WAVE_RGB_COLOR("slate gray", 112, 128, 144),
WAVE_RGB_COLOR("slate grey", 112, 128, 144),
WAVE_RGB_COLOR("SlateBlue", 106, 90, 205),
WAVE_RGB_COLOR("SlateBlue1", 131, 111, 255),
WAVE_RGB_COLOR("SlateBlue2", 122, 103, 238),
WAVE_RGB_COLOR("SlateBlue3", 105, 89, 205),
WAVE_RGB_COLOR("SlateBlue4", 71, 60, 139),
WAVE_RGB_COLOR("SlateGray", 112, 128, 144),
WAVE_RGB_COLOR("SlateGray1", 198, 226, 255),
WAVE_RGB_COLOR("SlateGray2", 185, 211, 238),
WAVE_RGB_COLOR("SlateGray3", 159, 182, 205),
WAVE_RGB_COLOR("SlateGray4", 108, 123, 139),
WAVE_RGB_COLOR("SlateGrey", 112, 128, 144),
WAVE_RGB_COLOR("snow", 255, 250, 250),
WAVE_RGB_COLOR("snow1", 255, 250, 250),
WAVE_RGB_COLOR("snow2", 238, 233, 233),
WAVE_RGB_COLOR("snow3", 205, 201, 201),
WAVE_RGB_COLOR("snow4", 139, 137, 137),
WAVE_RGB_COLOR("spring green", 0, 255, 127),
WAVE_RGB_COLOR("SpringGreen", 0, 255, 127),
WAVE_RGB_COLOR("SpringGreen1", 0, 255, 127),
WAVE_RGB_COLOR("SpringGreen2", 0, 238, 118),
WAVE_RGB_COLOR("SpringGreen3", 0, 205, 102),
WAVE_RGB_COLOR("SpringGreen4", 0, 139, 69),
WAVE_RGB_COLOR("steel blue", 70, 130, 180),
WAVE_RGB_COLOR("SteelBlue", 70, 130, 180),
WAVE_RGB_COLOR("SteelBlue1", 99, 184, 255),
WAVE_RGB_COLOR("SteelBlue2", 92, 172, 238),
WAVE_RGB_COLOR("SteelBlue3", 79, 148, 205),
WAVE_RGB_COLOR("SteelBlue4", 54, 100, 139),
WAVE_RGB_COLOR("tan", 210, 180, 140),
WAVE_RGB_COLOR("tan1", 255, 165, 79),
WAVE_RGB_COLOR("tan2", 238, 154, 73),
WAVE_RGB_COLOR("tan3", 205, 133, 63),
WAVE_RGB_COLOR("tan4", 139, 90, 43),
WAVE_RGB_COLOR("thistle", 216, 191, 216),
WAVE_RGB_COLOR("thistle1", 255, 225, 255),
WAVE_RGB_COLOR("thistle2", 238, 210, 238),
WAVE_RGB_COLOR("thistle3", 205, 181, 205),
WAVE_RGB_COLOR("thistle4", 139, 123, 139),
WAVE_RGB_COLOR("tomato", 255, 99, 71),
WAVE_RGB_COLOR("tomato1", 255, 99, 71),
WAVE_RGB_COLOR("tomato2", 238, 92, 66),
WAVE_RGB_COLOR("tomato3", 205, 79, 57),
WAVE_RGB_COLOR("tomato4", 139, 54, 38),
WAVE_RGB_COLOR("turquoise", 64, 224, 208),
WAVE_RGB_COLOR("turquoise1", 0, 245, 255),
WAVE_RGB_COLOR("turquoise2", 0, 229, 238),
WAVE_RGB_COLOR("turquoise3", 0, 197, 205),
WAVE_RGB_COLOR("turquoise4", 0, 134, 139),
WAVE_RGB_COLOR("violet", 238, 130, 238),
WAVE_RGB_COLOR("violet red", 208, 32, 144),
WAVE_RGB_COLOR("VioletRed", 208, 32, 144),
WAVE_RGB_COLOR("VioletRed1", 255, 62, 150),
WAVE_RGB_COLOR("VioletRed2", 238, 58, 140),
WAVE_RGB_COLOR("VioletRed3", 205, 50, 120),
WAVE_RGB_COLOR("VioletRed4", 139, 34, 82),
WAVE_RGB_COLOR("wheat", 245, 222, 179),
WAVE_RGB_COLOR("wheat1", 255, 231, 186),
WAVE_RGB_COLOR("wheat2", 238, 216, 174),
WAVE_RGB_COLOR("wheat3", 205, 186, 150),
WAVE_RGB_COLOR("wheat4", 139, 126, 102),
WAVE_RGB_COLOR("white", 255, 255, 255),
WAVE_RGB_COLOR("white smoke", 245, 245, 245),
WAVE_RGB_COLOR("WhiteSmoke", 245, 245, 245),
WAVE_RGB_COLOR("yellow", 255, 255, 0),
WAVE_RGB_COLOR("yellow green", 154, 205, 50),
WAVE_RGB_COLOR("yellow1", 255, 255, 0),
WAVE_RGB_COLOR("yellow2", 238, 238, 0),
WAVE_RGB_COLOR("yellow3", 205, 205, 0),
WAVE_RGB_COLOR("yellow4", 139, 139, 0),
WAVE_RGB_COLOR("YellowGreen", 154, 205, 50),
};
'''