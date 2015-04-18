#!/usr/bin/env python
import base64, getpass, re, os, sys
from Crypto.Cipher import AES

# 32 bytes = 256 bits, 16 = 128 bits
# the block size for cipher obj, can be 16 24 or 32. 16 matches 128 bit.
BLOCK_SIZE = 32

# the character used for padding to ensure value is always a multiple of BLOCK_SIZE
PADDING = '&'

def encryption(plaintext):

   pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
   AESEnc = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
   secret = os.urandom(BLOCK_SIZE)
   print('your encryption key: ')
   print(secret)
   cryptfile = open("secret.key", 'wb+')
   cryptfile.write(secret)
   cryptfile.close()
   print('Encryption key saved as secret.key. You will need this to decrypt the string later.')
   cipher = AES.new(secret)
   encoded = AESEnc(cipher, plaintext)
   print('Encrypted string: %s' % encoded)

def decryption(cryptstring):
   
   AESDec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
   encryption = cryptstring
   cryptfile = open("secret.key", 'r+')
   a = cryptfile.readlines()
   key = filter(None, a)
   for line in a:
      key = filter(None, line)
   cryptfile.close()
   cipher = AES.new(key)
   decoded = AESDec(cipher, encryption)
   print('Decrypted string: %s' % decoded)
   
def main():
   sel = raw_input("enter 1 to encrypt, 2 to decrypt, or 3 to exit --> ")
   while not re.match(r'^[1-3]$', sel):
      sel = raw_input("enter 1 to encrypt, 2 to decrypt, or 3 to exit --> ")
   if sel == '1':
      plaintext = raw_input("please enter string to encrypt --> ")
      encryption(plaintext)
   elif sel == '2':
      cryptstring = raw_input("paste string to decrypt --> ")
      decryption(cryptstring)
   else:
      print("exiting.. goodbye!")
      sys.exit()

main()
sys.exit()
