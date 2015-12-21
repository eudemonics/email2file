#!/usr/bin/env python
# ENCRYPTLIST.PY version 0.3 - encryption for lists, extension for email2file
# author: vvn [ v @ vvn . ninja ]
# version release date: Dec 21, 2015
# latest version will be available here:
# https://github.com/eudemonics/email2file.git
#####
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2015  vvn <v @ vvn . ninja>
##### 
##### This program is FREE software: you can use it, redistribute it and/or modify
##### it as you wish. Copying and distribution of this file, with or without modification,
##### are permitted in any medium without royalty provided the copyright
##### notice and this notice are preserved. This program is offered AS-IS,
##### WITHOUT ANY WARRANTY; without even the implied warranty of
##### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##### GNU General Public License for more details.
##### 
##### For more information, please refer to the "LICENSE AND NOTICE" file that should
##### accompany all official download releases of this program. 
#####

import base64, hashlib, getpass, os, random, re, sys
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
from ansilist import ac

colorintro = ac.BLKBGBLUE + '''
###############################################
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
'''
colorintro += '#####    ' + ac.REDBGWHITEBOLD + 'ENCRYPTLIST.PY FOR EMAIL2FILE' + ac.CLEAR + ac.BLKBGBLUE + '    #####\n'
colorintro += '#####                                     #####\n'
colorintro += '#######           ' + ac.BLKBGPINKBOLD + 'VERSION 0.3' + ac.CLEAR + ac.BLKBGBLUE + '           #######\n'
colorintro += '#########           ' + ac.BLKBGAQUABOLD + 'by: vvn' + ac.CLEAR + ac.BLKBGBLUE + '           #########'
colorintro += '''
###########                         ###########
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
'''
colorintro += '#####            ' + ac.CLEAR + ac.BLKBGGREYBOLD + 'RELEASE DATE:' + ac.CLEAR + ac.BLKBGBLUE + '            #####\n'
colorintro += '#####            ' + ac.BLKBGYELLOWBOLD + 'DEC 20, 2015' + ac.CLEAR + ac.BLKBGBLUE + '             #####'
colorintro += '''
#####                                     #####
############# #  # #  # #  # #  # #############
###############################################
''' + ac.CLEAR

cleanintro = '''
###############################################
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####    ENCRYPTLIST.PY FOR EMAIL2FILE    #####
#####                                     #####
#######           VERSION 0.3           #######
#########           by: vvn           #########
###########                         ###########
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####            RELEASE DATE:            #####
#####            DEC 20, 2015             #####
#####                                     #####
############# #  # #  # #  # #  # #############
###############################################
'''

if os.name == 'nt' or sys.platform == 'win32':
   try:
      import colorama
      colorama.init()
      usecolor = "color"
   except:
      pass
      try:
         os.system('pip install colorama')
         import colorama
         colorama.init()
         usecolor = "color"
      except:
         pass
         try:
            import tendo.ansiterm
            usecolor = "color"
         
         except:
            usecolor = "clean"
            pass

else:
   usecolor = "color"

global encfile
global encpass

# BLOCK_SIZE: block size in bytes for cipher object. this can be 16, 24, or 32.
# 32 bytes = 256 bits, 24 bytes = 192 bits, 16 bytes = 128 bits
BLOCK_SIZE = 32
# PADDING: any character used to stretch out a value to a multiple of BLOCK_SIZE
PADDING = '&'
CRYPT_MODE = AES.MODE_CBC
rounds = 1337
keysize = 32
saltlen = random.randint(16,42)
salt = os.urandom(saltlen)

def encryption(encpass, fn, encfile):

   current = os.getcwd()

   while not os.path.exists(fn):
      fn = raw_input("invalid path. please check file name and enter again --> ")

   secretpadlen = 16 - (len(encpass) % 16)
   secret = encpass + (PADDING * secretpadlen)
   
   if os.path.isfile("secret.key"):
      cryptfile = open("secret.key", 'r')
      bcryptkey = cryptfile.readline()
      cryptkey = base64.b64decode(bcryptkey)
      print(ac.GREENBOLD + '\nUsing previously generated encryption key stored as ' + ac.ORANGE + 'secret.key.\n' + ac.CLEAR)
   else:
      for i in range(0,rounds):
         cryptkey = hashlib.sha256(encpass+salt).digest()
      cryptkey = cryptkey[:keysize]
      bcryptkey = base64.b64encode(cryptkey)
      cryptfile = open("secret.key", 'wb+')
      cryptfile.write(bcryptkey)
      if usecolor == "color":
         print(ac.GREENBOLD + '\nYour encryption key has been saved to the current directory (' + ac.BLKBGGREYBOLD + current + ac.CLEAR + ac.GREENBOLD + ') as ' + ac.ORANGE + 'secret.key' + ac.GREENBOLD + '. \nYou should copy this file to another location to ensure you have a backup of it.\n' + ac.PINKBOLD + 'You will need the key to decrypt the file later.\n' + ac.CLEAR)
      else:
         print('\nYour encryption key has been saved to the current directory (%s) as \'secret.key\'. \nYou should copy this file to another location to ensure you have a backup of it. \nYou will need the ky to decrypt the file later.\n' % current)
   cryptfile.close()
   os.system('chmod 0640 secret.key')
   print('\nyour raw encryption key: %s \n' % cryptkey)
   print('\nyour base64 encoded key: %s \n' % bcryptkey)
   
   pad = lambda a: a + (BLOCK_SIZE - len(a) % BLOCK_SIZE) * PADDING
   AES_Enc = lambda c, a: base64.b64encode(c.encrypt(pad(a)))
   cipher = AES.new(cryptkey, CRYPT_MODE, secret)
   
   pf = open(fn, "r+")
   ef = open(encfile, "wb+")
   for line in pf.readlines():
      encoded = AES_Enc(cipher, line)
      print('Encrypted string: %s' % encoded)
      ef.write(encoded)
      ef.write("\n")
   print("\nencrypted strings written to: " + ac.AQUABOLD + " %s \n" + ac.CLEAR) % encfile
   ef.close()
   pf.close()

def decryption(encpass, encfile, newfile):
   
   while not os.path.exists(encfile):
      encfile = raw_input("invalid path. please check file name and enter again --> ")

   AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
   cryptfile = open("secret.key", 'r+')
   a = cryptfile.readline()
   cryptkey = base64.b64decode(a)
   cryptfile.close()
   secretpadlen = 16 - (len(encpass) % 16)
   secret = encpass + (PADDING * secretpadlen)
   
   cipher = AES.new(cryptkey, CRYPT_MODE, secret)
   
   ef = open(encfile, "r+")
   pf = open(newfile, "wb+")
   for line in ef.readlines():
      decoded = AES_Dec(cipher, line)
      pf.write(decoded)
   pf.close()
   ef.close()
   print("\ndecrypted lines written to: " + ac.PINK + " %s \n" + ac.CLEAR) % newfile
   
def encryptlist():
   origfile = raw_input("please copy password list file to script directory and enter filename --> ")
   while not os.path.exists(origfile):
      origfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
   encpass = getpass.getpass("enter the secret passphrase --> ")
   while len(encpass) > 16:
      encpass = getpass.getpass("the passphrase you have entered exceeds the 128-bit length. please enter a different passphrase of 16 characters or less --> ")
   encpass2 = getpass.getpass("confirm the secret passphrase --> ")
   while not encpass == encpass2:
      print("the passphrases entered did not match.")
      encpass = getpass.getpass("enter the secret passphrase --> ")
      encpass2 = getpass.getpass("confirm the secret passphrase --> ")
   
   print("\n*** PLEASE REMEMBER YOUR PASSPHRASE OR KEEP A RECORD OF IT IN A SECURE LOCATION. THE PROGRAM IS UNABLE TO RECOVER OR VERIFY YOUR PASSPHRASE. ***\n")
      
   encfile = raw_input("enter filename to save new encrypted list --> ")
   while not re.match(r'^[\w\-. ]+$', encfile):
      encfile = raw_input("invalid format. please enter a valid filename --> ")
   print("encrypting each entry in password file..\n")
   encryption(encpass, origfile, encfile)
   delsel = raw_input("delete the original unencrypted password file? Y/N --> ")
   while not re.match(r'^[nNyY]$', delsel):
      delsel = raw_input("invalid selection. enter Y to delete or N to keep original unencoded file --> ")
   if delsel.lower() == 'y':
      try:
         os.remove(origfile)
         if os.path.isfile(origfile):
            os.unlink(origfile)
         print('%s deleted successfully.\n' % origfile)
      except OSError, e: 
         print ("Error: %s - %s." % (e.filename,e.strerror))
   else:
      if os.path.isfile(origfile):
         print('\n*** %s contains sensitive data. please delete it manually ASAP. ***\n' % origfile)
   return encfile
         
def decryptlist():
   encfile = raw_input("please enter filename of encrypted password list --> ")
   while not os.path.exists(encfile):
      encfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
   encpass = getpass.getpass("enter the secret passphrase --> ")
   newfile = raw_input("enter filename to save new decrypted entries --> ")
   while not re.match(r'^[\w\-. ]+$', newfile):
      newfile = raw_input("invalid format. please enter a valid filename --> ")
   print("\ndecrypting each entry in password file %s..") % encfile 
   decryption(encpass, encfile, newfile)
   return newfile

def gen_list():
   selection = raw_input("enter 1 to encrypt or 2 to decrypt a password list --> ")
   while not re.search(r'^[12]$', selection):
      selection = raw_input("invalid selection. enter 1 to encrypt or 2 to decrypt --> ")
   
   if selection == '1':
      encryptlist()
   
   else:
      decryptlist()
         
def exitmenu():
   exitsel = raw_input("enter 1 to run encryption script again. enter 2 to run email2file script. enter 3 to print encoded/decoded data. to exit, enter 4 --> ")

   while not re.search(r'^[1-4]$', exitsel):
      exitsel = raw_input("invalid entry. enter 1 to run encryption script again, 2 to run email2file script, 3 to show encoded/decoded data, or 4 to exit --> ")

   if exitsel == '1':
      gen_list()

   elif exitsel == '2':
      import email2file

   elif exitsel == '3':
      AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
      cryptfile = open("secret.key", 'r+')
      a = cryptfile.readline()
      cryptkey = base64.b64decode(a)
      cryptfile.close()
      secretpadlen = 16 - (len(encpass) % 16)
      secret = encpass + (PADDING * secretpadlen)
      cipher = AES.new(cryptkey, CRYPT_MODE, secret)
      print(ac.BLUE + "------------------------------------------------------------" + ac.CLEAR)
      ef = open(encfile, "r+")
      for line in ef.readlines():
         decoded = AES_Dec(cipher, line)
         print(ac.WHITE + "encrypted: " + ac.ORANGE + line + ac.CLEAR)
         print(ac.WHITE + "decrypted: " + ac.GREEN + decoded + ac.CLEAR)
         print(ac.BLUE + "------------------------------------------------------------" + ac.CLEAR)
      ef.close()
      exitmenu()

   else:
      print(ac.AQUA + "goodbye!" + ac.CLEAR)
      sys.exit()
   
   sys.exit()
   
if __name__ == '__main__':
   if usecolor == 'color':
      print(colorintro)
   else:
      print(cleanintro)
   gen_list()   
   exitmenu()

   print("exiting program..")

   sys.exit()