#!/usr/bin/env python
# ENCRYPTLISTWIN.PY - encryption for lists - windows version
# author: vvn [ vvn @ notworth . it ]
# latest version will be available here:
# https://github.com/eudemonics/email2file.git

import base64, hashlib, getpass, os, random, re, sys
if (os.name == 'posix') or (sys.platform == 'darwin' or 'linux' or 'linux2'):
   os.system('python encryptlist.py')
   sys.exit()

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter

global encfile
global encpass

BLOCK_SIZE = 16
PADDING = '&'
CRYPT_MODE = AES.MODE_CBC
rounds = 1121
keysize = 16
saltlen = random.randint(16,42)
salt = os.urandom(saltlen)

def intro():
   print('''
###############################################
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####    ENCRYPTLIST.PY FOR EMAIL2FILE    #####
#####                                     #####
#######           VERSION 0.1           #######
#########           by: vvn           #########
###########                         ###########
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
#####            RELEASE DATE:            #####
#####           APRIL 23, 2015            #####
#####                                     #####
############# #  # #  # #  # #  # #############
###############################################
''')

def encryption(encpass, fn, encfile):

   while not os.path.exists(fn):
      fn = raw_input("invalid path. please check file name and enter again --> ")

   secretpadlen = BLOCK_SIZE - (len(encpass) % BLOCK_SIZE)
   secret = encpass + (PADDING * secretpadlen)
   
   if os.path.isfile("secret.key"):
      cryptfile = open("secret.key", 'r')
      bcryptkey = cryptfile.readline()
      cryptkey = base64.b64decode(bcryptkey)
      print('\nUsing previously generated encryption key stored as secret.key..\n')
   else:
      for i in range(0,rounds):
         cryptkey = hashlib.sha256(encpass+salt).digest()
      cryptkey = cryptkey[:keysize]
      bcryptkey = base64.b64encode(cryptkey)
      cryptfile = open("secret.key", 'wb+')
      cryptfile.write(bcryptkey)
      print('\nEncryption key saved to file as secret.key. You will need this to decrypt the string later.\n')
   
   cryptfile.close()
   
   print('\nyour raw encryption key: ')
   print(cryptkey)
   print('your base64 encoded key: %s' % bcryptkey)
   current = os.getcwd()
   
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
   print("\nencrypted strings written to %s \n") % encfile
   ef.close()
   pf.close()

def decryption(encpass, encfile, newfile):
   
   while not os.path.exists(encfile):
      encfile = raw_input("invalid path. please check file name and enter again --> ")

   AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
   cryptfile = open("secret.key", 'r+')
   cryptkey = cryptfile.readline()
   #cryptkey = filter(None, a)
   cryptfile.close()
   secretpadlen = BLOCK_SIZE - (len(encpass) % BLOCK_SIZE)
   secret = encpass + (PADDING * secretpadlen)
   
   cipher = AES.new(cryptkey, CRYPT_MODE, secret)
   
   ef = open(encfile, "r+")
   pf = open(newfile, "wb+")
   for line in ef.readlines():
      decoded = AES_Dec(cipher, line)
      pf.write(decoded)
   pf.close()
   ef.close()
   print("\ndecrypted lines written to %s \n") % newfile

def gen_list():
   selection = raw_input("enter 1 to encrypt or 2 to decrypt a password list --> ")
   while not re.search(r'^[12]$', selection):
      selection = raw_input("invalid selection. enter 1 to encrypt or 2 to decrypt --> ")
   
   if selection == '1':
      origfile = raw_input("please copy password list file to script directory and enter filename --> ")
      while not os.path.exists(origfile):
         origfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
      encpass = getpass.getpass("enter the secret passphrase --> ")
      encpass2 = getpass.getpass("confirm the secret passphrase --> ")
      while not encpass == encpass2:
         print("the passphrases entered did not match.")
         encpass = getpass.getpass("enter the secret passphrase --> ")
         encpass2 = getpass.getpass("confirm the secret passphrase --> ")
         
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
   else:
      encfile = raw_input("please enter filename of encrypted password list --> ")
      while not os.path.exists(encfile):
         encfile = raw_input("cannot find the file specified. please check path and enter correct filename --> ")
      encpass = getpass.getpass("enter the secret passphrase --> ")
      newfile = raw_input("enter filename to save new decrypted entries --> ")
      while not re.match(r'^[\w\-. ]+$', newfile):
         newfile = raw_input("invalid format. please enter a valid filename --> ")
      print("\ndecrypting each entry in password file %s..") % encfile 
      decryption(encpass, encfile, newfile)
      
   def exitmenu():
   exitsel = raw_input("enter 1 to run encryption script again. enter 2 to run email2file script. enter 3 to print encoded/decoded data. to exit, enter 4 --> ")

   while not re.search(r'^[1-4]$', exitsel):
      exitsel = raw_input("invalid entry. enter 1 to run encryption script again, 2 to run email2file script, 3 to show encoded/decoded data, or 4 to exit --> ")

   if exitsel == '1':
      gen_list()

   elif exitsel == '2':
      os.system('icacls email2file.py /grant Everyone:F')
      os.system('python email2file.py')
      sys.exit()

   elif exitsel == '3':
      AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
      cryptfile = open("secret.key", 'r+')
      a = cryptfile.readlines()
      key = filter(None, a)
      for line in a:
         key = filter(None, line)
      cryptfile.close()
      cryptkey = key
      secretpadlen = BLOCK_SIZE - (len(encpass) % BLOCK_SIZE)
      secret = encpass + (PADDING * secretpadlen)
      cipher = AES.new(cryptkey, CRYPT_MODE, secret)
      print("------------------------------------------------------------")
      ef = open(encfile, "r+")
      for line in ef.readlines():
         decoded = AES_Dec(cipher, line)
         print("encrypted: %s" % line)
         print("decrypted: %s" % decoded)
         print("------------------------------------------------------------")
      ef.close()
      exitmenu()

   else:
      print("goodbye!")
      sys.exit()
   
gen_list()

print("exiting program..")
   
sys.exit()
