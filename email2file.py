#!/usr/bin/env python
#
##### EMAIL2FILE v1.5 BETA
##### AUTHOR: vvn < vvn @ notworth dot it >
##### VERSION RELEASE: April 23, 2015
##### save email lists in plain text format in script directory with one address per line.
##### you can also include the password, if known. just use "email@addy.com, password" instead.
##### if there are only a few email addresses, you can easily generate the file:
##### open a terminal window to the script directory, then enter:
##### echo "your@email.com" >> emails.txt
##### repeat that command for each email you want to use, then enter "emails.txt" for the filename
##### word lists should be one word per line or you'll probably get some kind of format error.
##### TO RUN SCRIPT, open terminal to script directory and enter "python email2file.py"
##### PLEASE USE PYTHON 2.7+ AND NOT PYTHON 3 OR YOU WILL GET SYNTAX ERRORS.
##### works best on OSX and linux systems, but you can try it on windows.
##### i even tried to remove all the ANSI codes for you windows users, so you'd better use it!
##### even better, if you are on windows, install the colorama module for python to support ANSI
##### if you have setuptools or pip installed, you can easily get it with "pip install colorama"
##### each inbox message is saved as a txt file in its respective account's directory within the 'email-output' subdirectory of user home directory (or $HOME env path)
##### for example, example@email.com will output to a directory called 'example_email.com'
##### a file of all mail headers fetched from your inbox is also saved in the 'email-output' directory
##### it should be called example@email.com-headerlist-yyyy-mm-dd.txt
##### attachments are saved either in user folder or user's 'attachments' subfolder
##### questions? bugs? suggestions? contact vvn at: vvn@notworth.it
##### source code for stable releases should be available on my pastebin:
##### http://pastebin.com/u/eudemonics
##### or on github: http://github.com/eudemonics/email2file
##### git clone https://github.com/eudemonics/email2file.git email2file
##################################################
##################################################
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2014-2015  vvn < vvn @ notworth . it >
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
##### contact me at:
##### vvn (at) notworth (dot) it
##### there be only about a thousand lines of code after this -->

from __future__ import print_function
import email, base64, getpass, imaplib, ast
import re, sys, os, os.path, datetime, socket, time, traceback, logging

colorintro = '''
\033[34m=====================================\033[33m
----------\033[36m EMAIL2FILE v1.5 \033[33m----------
-------------------------------------
-----------\033[35m author : vvn \033[33m------------
----------\033[32m vvn@notworth.it \033[33m----------
\033[34m=====================================\033[33m
----\033[37m support my work: buy my EP! \033[33m----
---\033[37m http://dreamcorp.bandcamp.com \033[33m---
---\033[37m facebook.com/dreamcorporation \033[33m---
------\033[32m thanks for the support! \033[33m------
\033[34m=====================================\n\033[0m
'''

cleanintro = '''
=====================================
---------- EMAIL2FILE v1.5 ----------
-------------------------------------
----------- author : vvn ------------
---------- vvn@notworth.it ----------
=====================================
---- support my work: buy my EP! ----
--- http://dreamcorp.bandcamp.com ---
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
'''

global usecolor

if os.name == 'nt' or sys.platform == 'win32':
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
print('''SINGLE EMAIL ADDRESS OR LIST OF MULTIPLE EMAIL ADDRESSES?
list of multiple email addresses must be in text format
with one email address per line. PASSWORD LIST with one
password per line in plain text or base64 encoded format
supported. ENCRYPTION MODULE provided in current release
and will be fully implemented in a future release. To
encrypt password list, run \033[33mpython encryptlist.py\033[0m.
***ALSO SUPPORTS EMAIL AND PASSWORD IN A SINGLE FILE:***
one email address and one password per line separated
by a comma (example@domain.com, password)
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

def checklogin(emailaddr, emailpass, sslcon):

   global checkresp
   efmatch = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)
   if efmatch:
      if usecolor == 'color':
         validmail = '\033[32m\nemail is valid: %s \033[0m\n' % emailaddr
      else:
         validmail = 'email is valid: %s ' % emailaddr
      print(validmail)
   else:
      print('invalid email format, skipping..')
      pass

   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]

   imap_server = 'imap.' + emaildomain
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
   logging.info('INFO: attempting to connect to IMAP server to check login credentials for account %s' % emailaddr)

   try:

      loginstatus, logindata = server.login(emailaddr, emailpass)

      if 'OK' in loginstatus:
         print('LOGIN SUCCESSFUL: %s' % emailaddr)
         logging.info('INFO: LOGIN successful for account %s' % emailaddr)
         checkresp = 'OK'

      elif 'AUTHENTICATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'AUTHENFAIL'

      elif 'PRIVACYREQUIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'PRIVACYREQ'

      elif 'UNAVAILABLE' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'UNAVAIL'

      elif 'AUTHORIZATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'AUTHORFAIL'

      elif 'EXPIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'EXPIRED'

      elif 'CONTACTADMIN' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s' % loginstatus
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'ADMINREQ'

      else:
         print('Unable to connect: %s' % emailaddr)
         logging.error('ERROR: %s' % loginstatus)
         checkresp = 'UNKNOWN'
         
   except IOError as e:
      pass
      logging.error('IO ERROR: %s' % str(e))
      checkresp = 'IOERROR'
   
   except socket.error as e:
      pass
      logging.error('SOCKET ERROR: %s' % str(e))
      checkresp = 'SOCKETERROR'

   except server.error as e:
      pass
      logging.error('IMAPLIB ERROR: %s' % str(e))
      checkresp = 'IMAPERROR'

      if 'BAD' in str(e):
         checkresp = 'BAD'
      else:
         checkresp = 'ERROR'

   except socket.timeout as e:
      pass
      print('Socket timeout: %s' % str(e))
      logging.error('ERROR: Socket timeout')
      checkresp = 'TIMEOUT'

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

# FUNCTION TO LOG ONTO IMAP SERVER FOR SINGLE EMAIL ADDRESS
def getimap(emailaddr, emailpass, sslcon):

   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]

   imap_server = 'imap.' + emaildomain
   imap_port = 993
   server = imaplib.IMAP4_SSL(imap_server, imap_port)

   if 'no' in sslcon:
      imap_port = 143

   if 'gmail.com' in atdomain and 'no' in sslcon:
      imap_port = 587

   if 'yes' in sslcon:
      server = imaplib.IMAP4_SSL(imap_server, imap_port)

   else:
      server = imaplib.IMAP4(imap_server, imap_port)

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
               print('\033[0m\nFOLDERS:\n\033[33m', listdata)
               print('\033[34m\nlogin successful, fetching emails.. \033[0m\n')

            else:

               print("%d UNREAD MESSAGES" % len(unseen))
               print()
               print('Response code: \n', typ)
               print('\nFOLDERS:\n', listdata)
               print('\nlogin successful, fetching emails.. \n')

            logging.info('INFO: LOGIN successful for %s.' % emailaddr)
            logging.info('INFO: %d unread messages.' % countunseen)
            logging.info('INFO: fetching all messages...')

            # server.list()

            server.select()

            result, msgs = server.search(None, 'ALL')

            ids = msgs[0]
            id_list = ids.split()

            print(id_list)

            if usecolor == 'color':

               print('\033[37m------------------------------------------------------------\n\033[0m')

            else:

               print('------------------------------------------------------------')


            homedir = os.path.expanduser("~")

            rootdir = os.path.join(homedir, 'email-output')

            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            printdate = str(datetime.date.today())

            prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
            prev_complete_name = os.path.join(rootdir, prev_file_name)

            for email_uid in id_list:

               result, rawdata = server.fetch(email_uid, '(RFC822)')

               rawbody = rawdata[0][1]

               m = email.message_from_string(rawbody)

               msgfrom = m['From'].replace('/', '-')

               body = decode_email(rawbody)

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
                  file_name = user_save + "-" + email_uid + "-" + msgfrom[:35] + ext

               if file_name is None:
                  file_name = user_save + "-" + msgfrom[:35] + "-" + email_uid + ext

               complete_name = os.path.join(save_path, file_name)

               dtnow = datetime.datetime.now()
               dtyr = str(dtnow.year)
               dtmo = str(dtnow.month)
               dtday = str(dtnow.day)
               dthr = str(dtnow.hour)
               dtmin = str(dtnow.minute)

               dtdate = str(dtyr + "-" + dtmo + "-" + dtday)
               dttime = str(dthr + "." + dtmin)

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
                     bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
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

               if not os.path.isfile(prev_complete_name):
                  prevfile = open(prev_complete_name, 'wb+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n')
               #   prevfile.close()

               with open(prev_complete_name, 'a+b') as prevfile:
                  prevfile.write(email_uid)
                  prevfile.write("\n")
                  prevfile.write(msgpreview)
                  prevfile.write("\n")
                  # prevfile.close()

            if usecolor == 'color':

               print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

            else:

               print('inbox contents successfully saved to file. YAY!')

         if usecolor == 'color':

            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')

         else:

            print('list of message previews saved as: ', prev_complete_name)

         print('logging out..\n')

         server.logout()

         print('logout successful. exiting..\n')
         attempts = -1
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

         if qtyemail == '1':

            attempts = attempts - 1
            emailaddr = raw_input('please enter email again --> ')
            emailpass = getpass.getpass('please enter password --> ')

            matchaddy = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)

            while not matchaddy and attempts > 1:
               print('\033[31m invalid email format \033[0m\n')
               attempts = attempts - 1

            getimap(emailaddr, emailpass, sslcon)
            continue

   if attempts is 0:
      print('too many logon failures. unable to log onto IMAP server. quitting..')
      sys.exit()
# END OF FUNCTION getimap(emailaddr, emailpass, sslcon)

# FUNCTION FOR IMAP CONNECTION USING MULTIPLE ADDRESSES
def getimapmulti(emailaddr, emailpass, sslcon):

   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]

   imap_server = 'imap.' + emaildomain
   imap_port = 993

   if 'no' in sslcon:
      imap_port = 143

      if 'gmail.com' in emaildomain:
         imap_port = 587

   server = imaplib.IMAP4_SSL(imap_server, imap_port)

   if 'yes' in sslcon:
      server = imaplib.IMAP4_SSL(imap_server)

   else:
      server = imaplib.IMAP4(imap_server, imap_port)

   loginstatus, logindata = server.login(emailaddr, emailpass)

   attempts = 0

   while attempts <= 20:

      try:
         attempts += 1
         select_info = server.select('INBOX')
         status, unseen = server.search(None, 'UNSEEN')

         typ, listdata = server.list()

         countunseen = len(unseen)

         if usecolor == 'color':

            print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))
            print()
            print('Response code: \n\033[32m', typ)
            print('\033[0m\nFOLDERS:\n\033[33m', listdata)
            print('\033[34m\nlogin successful, fetching emails.. \033[0m\n')

         else:

            print("%d UNREAD MESSAGES" % len(unseen))
            print()
            print('Response code: \n', typ)
            print('\nFOLDERS:\n', listdata)
            print('\nlogin successful, fetching emails.. \n')

         server.select()
         result, msgs = server.search(None, 'ALL')

         ids = msgs[0]
         id_list = ids.split()

         print(id_list)

         if usecolor == 'color':

            print('\033[37m------------------------------------------------------------\n\033[0m')

         else:

            print('------------------------------------------------------------')

         homedir = os.path.expanduser("~")

         rootdir = os.path.join(homedir, 'email-output')

         if not os.path.exists(rootdir):
            os.makedirs(rootdir, 0755)

         printdate = str(datetime.date.today())

         prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
         prev_complete_name = os.path.join(rootdir, prev_file_name)

         for email_uid in id_list:

            result, rawdata = server.fetch(email_uid, '(RFC822)')

            rawbody = rawdata[0][1]

            m = email.message_from_string(rawbody)

            msgfrom = m['From'].replace('/', '-')

            body = decode_email(rawbody)

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
               file_name = user_save + "-" + email_uid + "-" + msgfrom[:25] + ext

            if file_name is None:
               file_name = user_save + "-" + msgfrom[:25] + "-" + email_uid + ext

            complete_name = os.path.join(save_path, file_name)

            dtnow = datetime.datetime.now()
            dtyr = str(dtnow.year)
            dtmo = str(dtnow.month)
            dtday = str(dtnow.day)
            dthr = str(dtnow.hour)
            dtmin = str(dtnow.minute)

            dtdate = str(dtyr + "-" + dtmo + "-" + dtday)
            dttime = str(dthr + "." + dtmin)

            if os.path.isfile(complete_name):

               if usecolor == 'color':

                  print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n')

               else:

                  print(complete_name + 'already exists, skipping.. \n')

            else:

               if type(body) is str or type(body) is buffer and isattach is True:

                  if usecolor == 'color':
                     print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n')

                  else:
                     print('downloading file: ' + str(file_name))

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
                  bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
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

            if not os.path.isfile(prev_complete_name):
               prevfile = open(prev_complete_name, 'wb+')
            #   prevfile.write('Email headers for: ' + emailaddr + '\n')
            #   prevfile.close()

            with open(prev_complete_name, 'a+b') as prevfile:
               prevfile.write(email_uid)
               prevfile.write("\n")
               prevfile.write(msgpreview)
               prevfile.write("\n")
               # prevfile.close()

         if usecolor == 'color':

            print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

         else:

            print('inbox contents successfully saved to file. YAY!')

         if usecolor == 'color':
            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')
         else:
            print('list of message previews saved as: %s' % prev_complete_name)

         logging.info('INFO: inbox contents saved to file with preview file %s' % prev_complete_name)
         print('logging out..\n')
         logging.info('INFO: logging off IMAP server.')
         server.logout()
         if usecolor == 'color':
            print('logout successful for \033[38m%s.\033[0m\n' % emailaddr)
            print('\033[34m------------------------------------------------------------\033[0m\n')
         else:
            print('logout successful for %s.\n' % emailaddr)
            print('------------------------------------------------------------\n')
         logging.info('INFO: logout successful for %s.' % emailaddr)
         checkresp = 'OK'
         attempts = 100
         break
         
      except IOError as e:
         pass
         print("IO SOCKET ERROR: %s" % str(e))
         logging.error('IO SOCKET ERROR: %s' % str(e))
         traceback.print_exc()
         checkresp = 'IOERROR'
         attempts += 1
         
      except socket.error as e:
         pass
         print("SOCKET ERROR: %s" % str(e))
         traceback.print_exc()
         logging.error('SOCKET ERROR: %s' % str(e))
         checkresp = 'SOCKETERROR'
         attempts += 1
      
      except socket.timeout as e:
         pass
         print('Socket timeout: %s, retrying connection..' % str(e))
         time.sleep(5.0)
         checkresp = 'TIMEOUT'
         attempts += 1
      
      except TypeError as e:
         pass
         print("TYPE ERROR: %s" % e)
         logging.error('TYPE ERROR: %s' % e)
         checkresp = 'TYPEERROR'
         attempts += 1

      except server.error as e:
         pass
         logging.error('ERROR: %s' % e)
         checkresp = 'ERROR'
         attempts += 1
         if usecolor == 'color':
            print('\033[35mfailed connecting to IMAP server.\033[0m\n')
            print('\033[31mERROR: \033[33m' + str(e) + '\033[0m\n')
         else:
            print('failed connecting to IMAP server.\n')
            print('ERROR: ' + str(e) + '\n')
            
         if qtyemail == '1':
            while True and attempts <= 20:
               emailaddr = raw_input('please enter email again --> ')
               emailpass = getpass.getpass('please enter password --> ')
               checkformat(emailaddr)
               attempts += 1
               logging.info('INFO: trying again with user-supplied email %s' % emailaddr)
               print('RETRYING with %s..' % emailaddr)
               pass
               
         # start with a socket at 30-second timeout
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         sock.settimeout(30.0)
 
         # check and turn on TCP Keepalive
         x = sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
         if( x == 0):
            print('Socket KEEPALIVE off, turning on')
            x = sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            logging.info('INFO: setsockopt=', x)
         else:
            print('Socket Keepalive already on')
            logging.info('INFO: Socket KEEPALIVE already on')

         try:
            sock.connect(imap_server)
            attempts += 1

         except socket.error:
            pass
            print('Socket connection failed')
            traceback.print_exc()
            time.sleep(5.0)
            attempts += 1
            continue

         print('Socket connection established!')

         while 1:
            try:
               req = sock.recv(6)

            except socket.timeout:
               pass
               print('Socket timeout, retrying connection..')
               time.sleep( 5.0)
               attempts += 1
               continue
               # traceback.print_exc()

            except:
               pass
               traceback.print_exc()
               print('Other Socket error. Trying to recreate socket..')
               attempts += 1
               # break from loop
               break

            print('received ', req)
            continue

         try:
            sock.close()
         except:
            pass
         continue
      
      return checkresp
# END OF FUNCTION getimapmulti(emailaddr, emailpass, sslcon)

# MULTIPLE EMAIL ADDRESSES
if qtyemail == '2':
   emaillistfile = raw_input('please copy the email list file to the script directory, then enter filename --> ')
   while not os.path.isfile(emaillistfile):
      emaillistfile = raw_input('the file path specified does not exist or is not accessible. please check the file and enter again --> ')

   ef = open(emaillistfile, "r")
   emailfile = ef.readlines()
   eflen = len(emailfile)

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
      pwlistfile = raw_input('please copy word list file to the script directory, then enter the filename --> ')

      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')
         
      encryptsel = raw_input('is the word list encrypted using encryptlist.py? enter Y/N --> ')
      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
         
      if encryptsel.lower() == 'y':
         print('*** the encryption module, though fully functional, is still in the process of being integrated with the full email2file program. ***')
         cryptlaunch = raw_input('enter 1 to decrypt your word list using encryptlist.py. enter 2 if you already have the decrypted file. --> ')
         while not re.match(r'^[12]$', cryptlaunch):
            cryptlaunch = raw_input('invalid selection. enter 1 to decrypt your word list. enter 2 if your word list is already decrypted. --> ')
         if cryptlaunch == '1':
            raw_input('press ENTER to launch encryptlist.py...')
            os.system('chmod +x encryptlist.py')
            os.system('python encryptlist.py')

      else:
      
         b64sel = raw_input('is the word list base64-encoded? Y/N --> ')

         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')

         if b64sel.lower() == 'n':
         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. would you like to encrypt or base64-encode your password list? Y/N --> ')

            while not re.search(r'^[yYnN]$', gotoencsel):

               gotoencsel = raw_input('invalid selection. enter Y to run script to encode a password list, or enter N to continue --> ')

            if gotoencsel.lower() == 'y':
               launchsel = raw_input('enter 1 to encrypt your word list using encryptlist.py. enter 2 to base64 encode with encodelist.py. --> ')
               while not re.search(r'^[12]$', launchsel):
                  launchsel = raw_input('invalid selection. enter 1 to encrypt list or 2 to base64 encode list. --> ')
               if launchsel == '1':
                  print("launching encryptlist.py..")
                  os.system('chmod +x encryptlist.py')
                  os.system('python encryptlist.py')
               else:
                  print("launching encodelist.py..")
                  os.system('chmod +x encodelist.py')
                  os.system('python encodelist.py')

         else:
            print('*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' ***')

      lnemail = ''
      lnpass = ''

      if usecolor == 'color':
         print("\n\033[31mEMAIL ADDRESSES IN FILE:\033[0m %s \n" % str(eflen))
      else:
         print("EMAIL ADDRESSES IN FILE: %s \n" % str(eflen))

      efcount = 1
      lenfile = len(emailfile)
      
      for index,line in enumerate(emailfile):
      
         print("PROCESSING EMAIL:\033[36;1m #%s \033[0m" % str(index))
         print("TOTAL EMAIL ADDRESSES:\033[36;1m %s \033[0m\n" % str(lenfile))
         
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
               print('\033[36musing email address: \033[0m' + lnemail)
            
            else:
               print('using email address: ' + lnemail)
               
            loginok = checklogin(lnemail, lnpass, sslcon)

            if 'OK' not in loginok:
               print('login failure. skipping to next entry in list...')
               logging.debug('DEBUG: LOGIN to %s failed' % emailaddr)
               continue
            else:
               logging.info('INFO: LOGIN to %s successful' % emailaddr)
               getimapmulti(lnemail, lnpass, sslcon)

         else:
         
            if usecolor == 'color':
               print('\n\033[34m------------------------------------------------------------\033[0m\n')
               print('\n\033[36musing email address: \033[0m' + line)
            
            else:
               print('------------------------------------------------------------\n')
               print('\nusing email address: ' + line)
               
            lnemail = line.strip()
            pf = open(pwlistfile, "r+")

            wordlist = pf.readlines()
            listlen = len(wordlist)

            tries = 0

            for lnpass in wordlist:

               if b64sel.lower() == 'y':
                  lnpass = base64.b64decode(lnpass)
               lnpass = lnpass.strip()
               lnpass = lnpass.replace("\n","")
               lnpass = str(lnpass)
               loginok = checklogin(lnemail, lnpass, sslcon)
               tries += 1

               if 'OK' not in loginok and tries <= listlen:
                  #print('tried: %s') % str(lnpass)
                  print('login failure. trying next entry...')
                  if usecolor == 'color':
                     print('\033[33mtries: \033[35m' + str(tries) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
                  else:
                     print('tries: ' + str(tries) + ' out of ' + str(listlen))
                  continue

               else:
                  logging.info('INFO: LOGIN to %s successful!' % lnemail)
                  getimapmulti(lnemail, lnpass.strip(), sslcon)
                  tries = 100
                  break

            if tries >= listlen and tries < 100:
               if usecolor == 'color':
                  print('\n\033[35mexhausted all entries in password list.\n\033[0m')
               else:
                  print('\nexhausted all entries in password list.\n')
               continue
         
         efcount += 1
         countdown = countdown - 1
               
         if countdown <= 0:
            print('finished processing all email addresses and passwords.')
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

            loginok = checklogin(lnemail, lnpass, sslcon)
            print(loginok)

            while 'OK' not in loginok:
               lnpass = getpass.getpass('login failure. please check password and enter again --> ')
               loginok = checklogin(lnemail, lnpass, sslcon)
               print(loginok)
               if 'OK' in loginok:
                  break
               else:
                  print('login failure. trying next entry..')
                  continue

            efcount += 1

            logging.info('INFO: LOGIN to %s successful' % lnemail)
            getimapmulti(lnemail, lnpass, sslcon)

      if efcount > eflen:
         print("all emails and passwords have been processed.")
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

         emailaddr = raw_input('please enter email again --> ')

         if match:
            tries = -1
            break

         else:
            tries = tries - 1

      if match:
         if usecolor == 'color':
            print('\n\033[32m email is valid \033[0m')
         else:
            print('email is valid')

      else:
         if usecolor == 'color':
            print('\033[31mERROR: unhandled exception. aborting..\033[0m\n')
         else:
            print('ERROR: unhandled exception. aborting..\n')
         logging.error('ERROR: unhandled exception. aborting program.')
         sys.exit()

      if tries is 0:
         if usecolor == 'color':
            print('\033[31m too many bad attempts using invalid format! \033[0m\n')
         else:
            print('too many bad attempts using invalid format!')

         logging.info('INFO: too many bad attempts using unproperly formatted email string. aborting program.')
         print('aborting..')
         sys.exit()

   if usewordlist.lower == 'y':

      pf = open(pwlistfile, "r")
      words = pf.readlines()
      total = len(words)
      count = 0

      while count <= total:

         for line in words():

            line = line.strip()
            line = line.replace("\n","")
            if b64sel.lower() == 'y':
               line = base64.b64decode(line)
            emailpass = line
            print("checking login authentication for %s" % emailaddr)
            logging.info('INFO: checking login authentication for %s' % emailaddr)
            loginok = checklogin(emailaddr, emailpass, sslcon)
            loginok = str(loginok)
            if usecolor == 'color':
               print("\033[31m result: \033[34m")
               print(loginok)
               print("\033[0m")
            else:
               print("result: %s") % loginok

            # INCREASE COUNTER BY 1
            count += 1
            print("tries: " + str(count) + " out of " + str(total))

            # WRONG PASSWORD
            if 'AUTHEN' in loginok:
               print("Wrong login credentials supplied for %s. Skipping to next password..." % emailaddr)
               logging.info('INFO: invalid password for %s. skipping to next password.' % emailaddr)
               continue

            # PASSWORD NOT CORRECTLY FORMATTED
            elif 'BAD' in loginok:
               emailpass = emailpass.strip()
               print("password format error. trying again..")
               loginok = checklogin(emailaddr, emailpass, sslcon)
               loginok = str(loginok)
               if 'OK' in loginok:
                  logging.info('INFO: LOGIN to %s successful' % emailaddr)
                  getimapmulti(emailaddr, emailpass, sslcon)
                  break
               continue

            else:
               logging.info('INFO: LOGIN to %s successful' % emailaddr)
               getimapmulti(emailaddr, emailpass, sslcon)
               break

   else:

      emailpass = getpass.getpass('please enter password --> ')
      getimap(emailaddr, emailpass, sslcon)

print("exiting program..")
sys.exit()
