#!/usr/bin/env python
# ANSILIST.PY - ANSI color library
# author: vvn [ vvn @ notworth . it ]
# latest version will be available here:
# https://github.com/eudemonics/email2file.git

class ac:
     
   CLEAR = '\033[0m'
   BOLD = '\033[1m'
   DARK = '\033[2m'
   UNDERLINE = '\033[4m'
   BLINK = '\033[5m'
   INVERSE = '\033[7m'
   
   BLACK = '\033[30m'
   ORANGE = '\033[31m'
   GREEN = '\033[32m'
   YELLOW = '\033[33m'
   BLUE = '\033[34m'
   PINK = '\033[35m'
   AQUA = '\033[36m'
   WHITE = '\033[37m'
   
   normal = 'm'
   bold = ';1m'
   endbold = ';21m'
   underline = ';4m'
   endunderline = ';24m'
   blink = ';5m'
   endblink = ';25m'
   inverse = ';7m'
   endinverse = ';27m'
         
   BLACKBG = '\033[40m'
   REDBG = '\033[41m'
   GREENBG = '\033[42m'
   YELLOWBG = '\033[43m'
   BLUEBG = '\033[44m'
   PINKBG = '\033[45m'
   AQUABG = '\033[46m'
   WHITEBG = '\033[47m'
   
   GREYBOLD = '\033[30;1m'
   ORANGEBOLD = '\033[31;1m'
   GREENBOLD = '\033[32;1m'
   YELLOWBOLD = '\033[33;1m'
   BLUEBOLD = '\033[34;1m'
   PINKBOLD = '\033[35;1m'
   AQUABOLD = '\033[36;1m'
   WHITEBOLD = '\033[37;1m'
   TEALBOLD = '\033[2;1m'
   BLACKBG = '\033[40m'
   REDBG = '\033[41m'
   GREENBG = '\033[42m'
   YELLOWBG = '\033[43m'
   BLUEBG = '\033[44m'
   PINKBG = '\033[45m'
   AQUABG = '\033[46m'
   WHITEBG = '\033[47m'
   OKGREY = '\033[90m'
   OKORANGE = '\033[91m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   OKBLUE = '\033[94m'
   OKPINK = '\033[95m'
   OKAQUA = '\033[96m'
   OKWHITE = '\033[97m'
   BLKBGORANGE = BLACKBG + '\033[31m'
   BLKBGGREEN = BLACKBG + '\033[32m'
   BLKBGYELLOW = BLACKBG + '\033[33m'
   BLKBGBLUE = BLACKBG + '\033[34m'
   BLKBGPINK = BLACKBG + '\033[35m'
   BLKBGAQUA = BLACKBG + '\033[36m'
   BLKBGWHITE = BLACKBG + '\033[37m'
   BLKBGGREYBOLD = BLACKBG + '\033[30;1m'
   BLKBGORANGEBOLD = BLACKBG + '\033[31;1m'
   BLKBGGREENBOLD = BLACKBG + '\033[32;1m'
   BLKBGYELLOWBOLD = BLACKBG + '\033[33;1m'
   BLKBGBLUEBOLD = BLACKBG + '\033[34;1m'
   BLKBGPINKBOLD = BLACKBG + '\033[35;1m'
   BLKBGAQUABOLD = BLACKBG + '\033[36;1m'
   BLKBGWHITEBOLD = BLACKBG + '\033[37;1m'
   REDBGBLACK = REDBG + '\033[30m'
   REDBGORANGE = REDBG + '\033[31m'
   REDBGGREEN = REDBG + '\033[32m'
   REDBGYELLOW = REDBG + '\033[33m'
   REDBGBLUE = REDBG + '\033[34m'
   REDBGPINK = REDBG + '\033[35m'
   REDBGAQUA = REDBG + '\033[36m'
   REDBGWHITE = REDBG + '\033[37m'
   REDBGGREYBOLD = REDBG + '\033[30;1m'
   REDBGORANGEBOLD = REDBG + '\033[31;1m'
   REDBGGREENBOLD = REDBG + '\033[32;1m'
   REDBGYELLOWBOLD = REDBG + '\033[33;1m'
   REDBGBLUEBOLD = REDBG + '\033[34;1m'
   REDBGPINKBOLD = REDBG + '\033[35;1m'
   REDBGAQUABOLD = REDBG + '\033[36;1m'
   REDBGWHITEBOLD = REDBG + '\033[37;1m'
   GRNBGBLACK = GREENBG + '\033[30m'
   GRNBGORANGE = GREENBG + '\033[31m'
   GRNBGGREEN = GREENBG + '\033[32m'
   GRNBGYELLOW = GREENBG + '\033[33m'
   GRNBGBLUE = GREENBG + '\033[34m'
   GRNBGPINK = GREENBG + '\033[35m'
   GRNBGAQUA = GREENBG + '\033[36m'
   GRNBGWHITE = GREENBG + '\033[37m'
   GRNBGGREYBOLD = GREENBG + '\033[30;1m'
   GRNBGORANGEBOLD = GREENBG + '\033[31;1m'
   GRNBGGREENBOLD = GREENBG + '\033[32;1m'
   GRNBGYELLOWBOLD = GREENBG + '\033[33;1m'
   GRNBGBLUEBOLD = GREENBG + '\033[34;1m'
   GRNBGPINKBOLD = GREENBG + '\033[35;1m'
   GRNBGAQUABOLD = GREENBG + '\033[36;1m'
   GRNBGWHITEBOLD = GREENBG + '\033[37;1m'
   YLWBGBLACK = YELLOWBG + '\033[30m'
   YLWBGORANGE = YELLOWBG + '\033[31m'
   YLWBGGREEN = YELLOWBG + '\033[32m'
   YLWBGYELLOW = YELLOWBG + '\033[33m'
   YLWBGBLUE = YELLOWBG + '\033[34m'
   YLWBGPINK = YELLOWBG + '\033[35m'
   YLWBGAQUA = YELLOWBG + '\033[36m'
   YLWBGWHITE = YELLOWBG + '\033[37m'
   YLWBGGREYBOLD = YELLOWBG + '\033[30;1m'
   YLWBGORANGEBOLD = YELLOWBG + '\033[31;1m'
   YLWBGGREENBOLD = YELLOWBG + '\033[32;1m'
   YLWBGYELLOWBOLD = YELLOWBG + '\033[33;1m'
   YLWBGBLUEBOLD = YELLOWBG + '\033[34;1m'
   YLWBGPINKBOLD = YELLOWBG + '\033[35;1m'
   YLWBGAQUABOLD = YELLOWBG + '\033[36;1m'
   YLWBGWHITEBOLD = YELLOWBG + '\033[37;1m'
   BLUBGBLACK = BLUEBG + '\033[30m'
   BLUBGORANGE = BLUEBG + '\033[31m'
   BLUBGGREEN = BLUEBG + '\033[32m'
   BLUBGYELLOW = BLUEBG + '\033[33m'
   BLUBGBLUE = BLUEBG + '\033[34m'
   BLUBGPINK = BLUEBG + '\033[35m'
   BLUBGAQUA = BLUEBG + '\033[36m'
   BLUBGWHITE = BLUEBG + '\033[37m'
   BLUBGGREYBOLD = BLUEBG + '\033[30;1m'
   BLUBGORANGEBOLD = BLUEBG + '\033[31;1m'
   BLUBGGREENBOLD = BLUEBG + '\033[32;1m'
   BLUBGYELLOWBOLD = BLUEBG + '\033[33;1m'
   BLUBGBLUEBOLD = BLUEBG + '\033[34;1m'
   BLUBGPINKBOLD = BLUEBG + '\033[35;1m'
   BLUBGAQUABOLD = BLUEBG + '\033[36;1m'
   BLUBGWHITEBOLD = BLUEBG + '\033[37;1m'
   PNKBGBLACK = PINKBG + '\033[30m'
   PNKBGORANGE = PINKBG + '\033[31m'
   PNKBGGREEN = PINKBG + '\033[32m'
   PNKBGYELLOW = PINKBG + '\033[33m'
   PNKBGBLUE = PINKBG + '\033[34m'
   PNKBGPINK = PINKBG + '\033[35m'
   PNKBGAQUA = PINKBG + '\033[36m'
   PNKBGWHITE = PINKBG + '\033[37m'
   PNKBGGREYBOLD = PINKBG + '\033[30;1m'
   PNKBGORANGEBOLD = PINKBG + '\033[31;1m'
   PNKBGGREENBOLD = PINKBG + '\033[32;1m'
   PNKBGYELLOWBOLD = PINKBG + '\033[33;1m'
   PNKBGBLUEBOLD = PINKBG + '\033[34;1m'
   PNKBGPINKBOLD = PINKBG + '\033[35;1m'
   PNKBGAQUABOLD = PINKBG + '\033[36;1m'
   PNKBGWHITEBOLD = PINKBG + '\033[37;1m'
   AQUBGBLACK = AQUABG + '\033[30m'
   AQUBGORANGE = AQUABG + '\033[31m'
   AQUBGGREEN = AQUABG + '\033[32m'
   AQUBGYELLOW = AQUABG + '\033[33m'
   AQUBGBLUE = AQUABG + '\033[34m'
   AQUBGPINK = AQUABG + '\033[35m'
   AQUBGAQUA = AQUABG + '\033[36m'
   AQUBGWHITE = AQUABG + '\033[37m'
   AQUBGGREYBOLD = AQUABG + '\033[30;1m'
   AQUBGORANGEBOLD = AQUABG + '\033[31;1m'
   AQUBGGREENBOLD = AQUABG + '\033[32;1m'
   AQUBGYELLOWBOLD = AQUABG + '\033[33;1m'
   AQUBGBLUEBOLD = AQUABG + '\033[34;1m'
   AQUBGPINKBOLD = AQUABG + '\033[35;1m'
   AQUBGAQUABOLD = AQUABG + '\033[36;1m'
   AQUBGWHITEBOLD = AQUABG + '\033[37;1m'
   WHITEBGBLACK = WHITEBG + '\033[30m'
   WHITEBGORANGE = WHITEBG + '\033[31m'
   WHITEBGGREEN = WHITEBG + '\033[32m'
   WHITEBGYELLOW = WHITEBG + '\033[33m'
   WHITEBGBLUE = WHITEBG + '\033[34m'
   WHITEBGPINK = WHITEBG + '\033[35m'
   WHITEBGAQUA = WHITEBG + '\033[36m'
   WHITEBGWHITE = WHITEBG + '\033[37m'
   WHITEBGGREYBOLD = WHITEBG + '\033[30;1m'
   WHITEBGORANGEBOLD = WHITEBG + '\033[31;1m'
   WHITEBGGREENBOLD = WHITEBG + '\033[32;1m'
   WHITEBGYELLOWBOLD = WHITEBG + '\033[33;1m'
   WHITEBGBLUEBOLD = WHITEBG + '\033[34;1m'
   WHITEBGPINKBOLD = WHITEBG + '\033[35;1m'
   WHITEBGAQUABOLD = WHITEBG + '\033[36;1m'
   WHITEBGWHITEBOLD = WHITEBG + '\033[37;1m'
      
class trans():

   fdict = {}
   bdict = {}
   sdict = {}

   fdict['black'] = 30
   fdict['orange'] = 31
   fdict['green'] = 32
   fdict['yellow'] = 33
   fdict['blue'] = 34
   fdict['pink'] = 35
   fdict['aqua'] = 36
   fdict['white'] = 37
   fdict['silver'] = 90

   bdict['black'] = 40
   bdict['red'] = 41
   bdict['green'] = 42
   bdict['yellow'] = 43
   bdict['blue'] = 44
   bdict['pink'] = 45
   bdict['aqua'] = 46
   bdict['white'] = 47

   sdict['bold'] = 1
   sdict['under'] = 4
   sdict['blink'] = 5
   sdict['inverse'] = 7
   sdict['clear'] = 0
   sdict['none'] = 50
   
   def colorize(foreground, background, style, text):
   
      fr = foreground.lower()
      bk = background.lower()
      st = style.lower()
   
      fval = fdict.get(foreground, 50)
      bval = bdict.get(background, 50)
      sval = sdict.get(style, 50)
      
      if sum(fval, bval, sval) == 150:
         str = ''
      
      elif 50 not in {fval, bval, sval}:
         str = '\033[%dm\033[%d;%dm' % (bval, fval, sval)
      
      elif sval == 50:
         if fval == 50:
            str = '\033[%dm' % bval
         elif bval == 50:
            str = '\033[%dm' % fval
         else:
            str = '\033[%dm\033[%dm' % (fval, bval)
      
      elif bval == 50:
         str = '\033[%d;%dm' % (bval, sval)
      
      else:
         str = '\033[%d;%dm' % (fval, sval)
      
      result = str + text + '\033[0m'
      return result