#!/usr/bin/env python
##### ANOTHER CRYPTO LIBRARY VERSION 0.1
##### by vvn [ eudemonics on github ]
##### release date: JANUARY 3, 2015
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2014  vvn <vvn@notworth.it>
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
###############################################
###############################################
############# #  # #  # #  # #  # #############
#####                                     #####
##### CRYPTO LIBRARY WITH RANDOMIZED SALT #####
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
#####           JANUARY 3, 2015           #####
#####                                     #####
############# #  # #  # #  # #  # #############
###############################################
###############################################


import hashlib, os, base64, random, getpass, sys
from Crypto.Cipher import AES

saltlen = random.randint(16,42)
rounds = 1121
blocksize = 16
keysize = 32
cryptmode = AES.MODE_CBC

def AESencrypt(passwd, cleartext, encodetype):
     
   salt = os.urandom(saltlen)
   iv = os.urandom(blocksize)

   padlen = 32 - (len(cleartext) % 16)
   paddedcleartext = cleartext + chr(padlen) * padlen
   cryptkey = passwd
   for i in range(0,rounds):
      cryptkey = hashlib.sha256(cryptkey+salt).digest()
   cryptkey = cryptkey[:keysize]
   cipherspec = AES.new(cryptkey, cryptmode, iv)
   ciphertext = cipherspec.encrypt(paddedcleartext)
   ciphertext = ciphertext + iv + salt
   if encodetype == 'base64':
      return base64.b64encode(ciphertext)
   elif encodetype == 'hex':
      return ciphertext.encode("hex")
   elif encodetype == 'utf8':
      return ciphertext.encode("utf8")
   else:
      invalid = 'ERROR: invalid encode type'
      return invalid
 
def AESdecrypt(passwd, ciphertext, encodetype):

   if encodetype == 'base64':
      ciphertextdec = base64.b64decode(ciphertext)
      
   elif encodetype == 'utf8':
      ciphertextdec = ciphertext.decode("utf8")   
      
   else:
      ciphertextdec = ciphertext.decode("hex")
   
   startiv = len(ciphertextdec)-blocksize-saltlen
   startSalt = len(ciphertextdec)-saltlen
   data, iv, salt = ciphertextdec[:startiv], ciphertextdec[startiv:startSalt], ciphertextdec[startSalt:]
   derivedKey = passwd
   for i in range(0, rounds):
      derivedKey = hashlib.sha256(derivedKey+salt).digest()
   derivedKey = derivedKey[:keysize]
   cipherSpec = AES.new(derivedKey, cryptmode, iv)
   plaintextWithPadding = cipherSpec.decrypt(data)
   paddingLength = ord(plaintextWithPadding[-1])
   plaintext = plaintextWithPadding[:-paddingLength]
   return plaintext

userstr = raw_input("enter string to encrypt --> ")

a = AESencrypt("password", userstr, "base64")

cryptfile = open("_crypt.txt", 'wb+')
cryptfile.write(a)
cryptfile.close()

decryptfile = open("_crypt.txt", "r")
for line in decryptfile.readlines():
   print AESdecrypt("password", line, "base64")
   
sys.exit()

