#!/usr/bin/env python
# ENCODELIST.PY - base64 encoding for lists integrated with EMAIL2FILE
# *** BASE64 IS NOT A SECURE ALGORITHM FOR PROTECTING YOUR DATA ***
# for enhanced security and greater protection of your sensitive data,
# please use ENCRYPTLIST.PY (also included with this program)
# author: vvn [ vvn @ notworth . it ]
# latest version will be available here:
# https://github.com/eudemonics/email2file.git

import base64, os, sys, re

global encfile

print('''
###############################################
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####     ENCODELIST.PY FOR EMAIL2FILE    #####
#####                                     #####
#######           VERSION 0.1           #######
#########  by: vvn [vvn@notworth.it]  #########
###########                         ###########
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####            RELEASE DATE:            #####
#####           APRIL 24, 2015            #####
#####                                     #####
############# #  # #  # #  # #  # #############
###############################################
''')

def encode_pass(fn, newfile):

   while not os.path.exists(fn):
      fn = raw_input("invalid path. please check file name and enter again --> ")

   pf = open(fn, "r+w")
   bf = open(newfile, "wb+")

   for line in pf.readlines():
      enctxt = base64.b64encode(line)
      bf.write(enctxt)
      bf.write("\n")

   print("base64-encoded lines written to %s") % newfile
   bf.close()
   pf.close()

def decode_pass(fn, newfile):
   
   while not os.path.exists(fn):
      fn = raw_input("invalid path. please check file name and enter again --> ")

   encfile = open(fn, "r+")
   decfile = open(newfile, "wb+")
   for line in encfile.readlines():
      dectext = base64.b64decode(line)
      decfile.write(dectext)
      decfile.write("\n")
   decfile.close()
   
   print("base-64 decoded lines written to %s") % newfile

def gen_list():
   selection = raw_input("enter 1 to encode or 2 to decode a password list --> ")
   while not re.search(r'^[12]$', selection):
      selection = raw_input("invalid selection. enter 1 to encode or 2 to decode --> ")
   
   if selection == '1':
      origfile = raw_input("please copy password list file to script directory and enter filename --> ")
      while not os.path.exists(origfile):
         origfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
      encfile = raw_input("please enter filename to save new encoded list --> ")
      while not re.match(r'^[\w\-. ]+$', encfile):
         encfile = raw_input("invalid format. please enter a valid filename --> ")
      print("encoding each entry in password file..")
      encode_pass(origfile, encfile)
      delsel = raw_input("securely delete the original unencoded password file?\n ***YOU WILL NOT BE ABLE TO RECOVER THE FILE BECAUSE IT WILL BE REWRITTEN*** \nY/N --> ")
      while not re.match(r'^[nNyY]$', delsel):
         delsel = raw_input("invalid selection. enter Y to securely delete or N to keep original unencoded file --> ")
      if delsel.lower() == 'y':
         try:
            if os.path.isfile(origfile):
               f = open(origfile, "wb")
               f.write("*"*os.path.getsize(origfile))
               f.close()
               os.system('srm -m %s' % origfile)
               if os.path.isfile(origfile):
                  os.unlink(origfile)
                  os.remove(origfile)
               print('file %s securely removed successfully.' % origfile)
            else:
               print('file %s not found. nothing to delete.' % origfile)
         except OSError, e: 
            print ("Error: %s - %s." % (e.filename,e.strerror))
      else:
         if os.path.isfile(origfile):
            print('%s may contain sensitive data. it is advised to securely delete it.' % origfile)
   else:
      encfile = raw_input("please enter filename of encoded password list --> ")
      while not os.path.exists(encfile):
         encfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
      newfile = raw_input("please enter filename to save new decoded entries --> ")
      while not re.match(r'^[\w\-. ]+$', newfile):
         newfile = raw_input("invalid format. please enter a valid filename --> ")
      print("decoding each entry in password file %s..") % encfile 
      encode_pass(encfile, newfile)
   def exitmenu():
      exitsel = raw_input("enter 1 to run script again. \nenter 2 to run encryptlist.py script for extra security. \nenter 3 to run email2file script. \nenter 4 to print encoded/decoded data. \nto exit, enter 5 --> ")

      while not re.search(r'^[1-5]$', exitsel):
         exitsel = raw_input("invalid entry. enter 1 to run script again, 2 to run encryptlist.py, 3 to run email2file script, 4 to show encoded/decoded data, or 5 to exit --> ")
   
      if exitsel == '1':
         gen_list()
         exitmenu()
      
      elif exitsel == '2':
         os.system('chmod +x encryptlist.py')
         os.system('python encryptlist.py')
         sys.exit()
   
      elif exitsel == '3':
         os.system('chmod +x email2file.py')
         os.system('./email2file.py')
         sys.exit()
   
      elif exitsel == '4':
         ef = open(encfile, "r+")
         for n in ef.readlines():
            print("encoded: %s" % n)
            dectext = base64.b64decode(n)
            print("decoded: %s" % dectext)
         ef.close()
         exitmenu()

      else:
         print("goodbye!")
   exitmenu()

print('''


***** BASE64 ENCODING IS NOT A SECURE METHOD *****   
         FOR STORING YOUR SENSITIVE DATA.

for increased protection, you have the option to
secure your word list using 256-bit AES encryption. 
you may do this by entering \'python encryptlist.py\'
into a terminal under the same working directory.
 
 

to continue with base64 encoding, enter 1.''')

selscript = raw_input("to switch to encryptlist.py instead, enter 2. --> ")

while not re.match(r'^[12]$', selscript):
   selscript = raw_input("invalid selection. to continue with base64 encoding, enter 1. \nto run encryption module instead, enter 2. --> ")
   
if selscript == '1':
   gen_list()
   
else:
   os.system('python encryptlist.py')
   sys.exit()

print("exiting program..")
   
sys.exit()
