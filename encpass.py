#!/usr/bin/env python
import base64, os, sys, re

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
   else:
      encfile = raw_input("please enter filename of encoded password list --> ")
      while not os.path.exists(encfile):
         encfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
      newfile = raw_input("please enter filename to save new decoded entries --> ")
      while not re.match(r'^[\w\-. ]+$', newfile):
         newfile = raw_input("invalid format. please enter a valid filename --> ")
      print("decoding each entry in password file %s..") % encfile 
      encode_pass(encfile, newfile)

   exitsel = raw_input("enter 1 to run script again. enter 2 to run email2file script. enter 3 to print encoded/decoded data. to exit, enter 4 --> ")

   while not re.search(r'^[1-4]$', exitsel):
      exitsel = raw_input("invalid entry. enter 1 to run script again, 2 to run email2file script, 3 to show encoded/decoded data, or 4 to exit --> ")
   
   if exitsel == '1':
      gen_list()
   
   elif exitsel == '2':
      os.system('chmod +x email2file.py')
      os.system('./email2file.py')
   
   elif exitsel == '3':
      ef = open(encfile, "r+")
      for n in ef.readlines():
         print("encoded: %s" % n)
         dectext = base64.b64decode(n)
         print("decoded: %s" % dectext)
      ef.close()

   else:
      print("goodbye!")
   
gen_list()

print("exiting program..")
   
sys.exit()
