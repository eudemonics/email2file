#!/usr/bin/env python
#
##### EMAIL2FILE v1.3 BETA - UNTESTED! because i am tired and lazy.
##### AUTHOR: vvn
##### VERSION RELEASE: november 27, 2014
##### save email lists in plain text format in script directory with one address per line.
##### you can also include the password, if known. just use "email@addy.com, password" instead.
##### if there are only a few email addresses, you can easily generate the file:
##### open a terminal window to the script directory, then enter:
##### echo "your@email.com" >> emails.txt
##### repeat that command for each email you want to use, then enter "emails.txt" for the filename
##### word lists should be one word per line or you'll probably get some kind of format error.
##### TO RUN SCRIPT, open terminal to script directory and enter "python email2file.py"
##### works best on OSX and probably linux systems, but you can try it on windows.
##### i even tried to remove all the ANSI codes for you windows users, so you'd better use it!
##### each inbox message is saved as a txt file in its respective account's directory within the 'output' subdirectory
##### attachments saved either in user folder or user's 'attachments' subfolder
##### questions? bugs? suggestions? contact vvn at: vvn@notworth.it
##### source code for stable releases should be available on my pastebin:
##### http://pastebin.com/u/eudemonics
##### or on github: http://github.com/eudemonics/email2file
##### git clone https://github.com/eudemonics/email2file.git email2file
##################################################
##################################################
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
import email, base64, getpass, imaplib
import re, sys, os, os.path, datetime, socket, time, logging

colorintro = '''
\033[34m=====================================\033[33m
----------\033[36m EMAIL2FILE v1.3 \033[33m----------
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
---------- EMAIL2FILE v1.3 ----------
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
global server

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
with one email address per line, with optional password
after a comma (example@domain.com, password)
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
   efmatch = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
   if efmatch:
      if usecolor == 'color':
         validmail = '\033[32m\nemail is valid: %s \033[0m\n\n' % emailaddr
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
      server = imaplib.IMAP4_SSL(imap_server)
      
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
         
   except server.error as e:
      pass
      print('IMAP SOCKET ERROR: %s' % str(e))
      logging.error('IMAPLIB ERROR: %s' % server.error)
      checkresp = 'ERROR'
   
   except server.timeout:
      pass
      print('Socket timeout')
      logging.error('ERROR: Socket timeout')
      checkresp = 'TIMEOUT'
         
   return checkresp
# END OF FUNCTION checklogin()
   
# FUNCTION TO CHECK FOR EMAIL FORMAT ERRORS BEFORE SUBMITTING TO SERVER
def checkformat(emailaddr):

   # START WHILE LOOP TO CHECK EMAIL FORMAT FOR ERRORS BEFORE ATTEMPTING LOGIN
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)      
   while not match:
      emailformat = 'bad'
      if usecolor == 'color':
         print('\033[31m invalid email format \033[0m\n')
      else:
         print('invalid email format')
      emailaddr = raw_input('please enter email again --> ')
      emailpass = getpass.getpass('please enter password --> ')
   emailformat = 'good'
   return(emailformat)
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
        
            rootdir = 'output'
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
               print('Response code: \n\n\033[32m', typ)
               print('\033[0m\nFOLDERS:\n\n\033[33m', listdata)
               print('\033[34m\n\nlogin successful, fetching emails.. \033[0m\n\n')
            
            else:
            
               print("%d UNREAD MESSAGES" % len(unseen))
               print()
               print('Response code: \n\n', typ)
               print('\nFOLDERS:\n\n', listdata)
               print('\n\nlogin successful, fetching emails.. \n\n')
              
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
         
            rootdir = 'output'
      
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
         
                  print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n\n')
            
               else:
            
                  if type(body) is str or type(body) is buffer and isattach is True:
                     print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n\n')
                     bodyfile = open(complete_name, 'wb+')
                     # bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()
               
                  else:
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.write("SENDER: \n")
                     bodyfile.write(msgfrom)
                     bodyfile.write('\n\n')
                     # bodyfile.write('Decoded:\n\n')
                     bodyfile.write(str(body))
                     bodyfile.write('\n\nRAW MESSAGE DATA:\n\n')
                     bodyfile.write(rawbody)
                     bodyfile.write('\n\n')
                     bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
                     bodyfile.write('\n\n')
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
                  
               print(data[0][1] + '\n\n')
               msgpreview = data[0][1]
               
               if not os.path.isfile(prev_complete_name):
                  prevfile = open(prev_complete_name, 'wb+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n\n')
               #   prevfile.close()
                  
               with open(prev_complete_name, 'a+b') as prevfile:   
                  prevfile.write(email_uid)
                  prevfile.write("\n\n")
                  prevfile.write(msgpreview)
                  prevfile.write("\n\n")
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
         print('IMAP SOCKET ERROR: %s' % str(e))
         logging.error('IMAPLIB ERROR: %s' % server.error)
         checkresp = 'ERROR'
         
         if usecolor == 'color':
            print('\033[35mfailed connecting to IMAP server.\033[0m\n')
            print('\033[31merror: \033[33m' + str(e) + '\033[0m\n\n')

         else:
         
            print('failed connecting to IMAP server.\n')
            print('error: ' + str(e) + '\n\n')
       
         if qtyemail == '1':

            attempts = attempts - 1
            emailaddr = raw_input('please enter email again --> ')
            emailpass = getpass.getpass('please enter password --> ')
      
            matchaddy = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
               
            while not matchaddy and attempts > 1:
               print('\033[31m invalid email format \033[0m\n')
               attempts = attempts - 1
            
            getimap(emailaddr, emailpass, sslcon)
            continue
                  
   if attempts is 0:
      print('too many logon failures. unable to log onto IMAP server. quitting..')
      sys.exit()

# FUNCTION FOR IMAP CONNECTION USING MULTIPLE ADDRESSES
def getimapmulti(emailaddr, emailpass, sslcon, loginresp):
         
   if 'OK' not in loginresp:
   
      atdomain = re.search("@.*", emailaddr).group()
      emaildomain = atdomain[1:]
   
      imap_server = 'imap.' + emaildomain
      imap_port = 993
   
      if 'no' in sslcon:
         imap_port = 143
   
         if 'gmail.com' in emaildomain:
            imap_port = 587
      
      if 'yes' in sslcon:
         server = imaplib.IMAP4_SSL(imap_server)
      
      else:
         server = imaplib.IMAP4(imap_server, imap_port)
         
      loginstatus, logindata = server.login(emailaddr, emailpass)
      
   while True:
      try:
         select_info = server.select('INBOX')
         status, unseen = server.search(None, 'UNSEEN')
         
         typ, listdata = server.list()
         
         countunseen = len(unseen)

         if usecolor == 'color':
   
            print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))
            print()
            print('Response code: \n\n\033[32m', typ)
            print('\033[0m\nFOLDERS:\n\n\033[33m', listdata)
            print('\033[34m\n\nlogin successful, fetching emails.. \033[0m\n\n')
   
         else:
   
            print("%d UNREAD MESSAGES" % len(unseen))
            print()
            print('Response code: \n\n', typ)
            print('\nFOLDERS:\n\n', listdata)
            print('\n\nlogin successful, fetching emails.. \n\n')
            
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
      
            rootdir = 'output'
   
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
               
                     print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n\n')
         
                  else:
               
                     print(complete_name + 'already exists, skipping.. \n\n')
                  
               else:
         
                  if type(body) is str or type(body) is buffer and isattach is True:
               
                     if usecolor == 'color':
                        print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n\n')
                 
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
                     bodyfile.write('\n\n')
                     # bodyfile.write('Decoded:\n\n')
                     bodyfile.write(str(body))
                     bodyfile.write('\n\nRAW MESSAGE DATA:\n\n')
                     bodyfile.write(rawbody)
                     bodyfile.write('\n\n')
                     bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
                     bodyfile.write('\n\n')
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
               
               print(data[0][1] + '\n\n')
               msgpreview = data[0][1]
         
               if not os.path.isfile(prev_complete_name):
                  prevfile = open(prev_complete_name, 'wb+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n\n')
               #   prevfile.close()
            
               with open(prev_complete_name, 'a+b') as prevfile:   
                  prevfile.write(email_uid)
                  prevfile.write("\n\n")
                  prevfile.write(msgpreview)
                  prevfile.write("\n\n")
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
            print('logout successful. exiting application..\n')
            logging.info('INFO: logout successful for %s. exiting application.' % emailaddr)
            break
            
      except server.timeout:
         pass
         print('Socket timeout')
         logging.error('ERROR: Socket timeout')
         checkresp = 'TIMEOUT'
         continue
               
      except server.error as e:

         pass
   
         if usecolor == 'color':
            print('\033[35mfailed connecting to IMAP server.\033[0m\n')
            print('\033[31merror: \033[33m' + str(e) + '\033[0m\n\n')
         else:
            print('failed connecting to IMAP server.\n')
            print('error: ' + str(e) + '\n\n')
 
         if qtyemail == '1':        

            emailaddr = raw_input('please enter email again --> ')
            emailpass = getpass.getpass('please enter password --> ')
            checkformat(emailaddr)
            
         continue
      
if qtyemail == '2':
   emaillistfile = raw_input('please copy the email list file to the script directory, then enter filename --> ')
   while not os.path.isfile(emaillistfile):
      emaillistfile = raw_input('the file path specified does not exist or is not accessible. please check the file and enter again --> ')
      
   if usewordlist.lower() == 'y':
      pwlistfile = raw_input('please copy word list file to the script directory, then enter the filename --> ')
      
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')
      
      ef = open(emaillistfile, "r")
      for line in ef.readlines():
   
         if re.search(r'^[\,]$', line):

            line = line.strip()
            linevals = line.split(",")

            lnemail = linevals[0]
            lnpass = linevals[1]
            print('using email address: ' + lnemail)
            loginok = checklogin(lnemail, lnpass, sslcon)
         
            if 'OK' not in loginok:
               print('login failure. skipping to next entry in list...')
               continue
            else:
                  break
         
         else:
      
            print('using email address: ' + line)
            lnemaile = line.strip()
            pf = open(pwlistfile, "r")

            for lnpass in pf.readlines():

               loginok = checklogin(lnemail, lnpass, sslcon)

               if 'OK' not in loginok:
                  print('login failure. trying next entry...')
                  continue
    
               else:
                  break
      
         getimapmulti(lnemail, lnpass, sslcon, 'OK')
  
   else:

      ef = open(emaillistfile, "r")
      for line in ef.readlines():
         lnemail = line
         print('using email address: ' + lnemail)
         lnpass = getpass.getpass('please enter password for above account --> ')
         loginok = checklogin(lnemail, lnpass, sslcon)
         print(loginok)
         time.sleep(2)
      
         while 'OK' not in loginok:
            lnpass = getpass.getpass('login failure. please check password and enter again --> ')
            loginok = checklogin(lnemail, lnpass, sslcon)
            print(loginok)
            time.sleep(2)
            if 'OK' in loginok:
               break
            else:
               print('login failure. trying next entry..')
               continue
            
         getimapmulti(lnemail, lnpass, sslcon, 'OK')

# SINGLE EMAIL ADDRESS
else:

   emailaddr = raw_input('please enter email address --> ')
   
   #VALIDATE EMAIL USING REGEX
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

   if match:
      if usecolor == 'color':
         print('\033[32m\nemail is valid\033[0m\n\n')
      
      else:
         print('email is valid\n\n')
         
   else:
      tries = 5

      while not match and tries > 0:

         if usecolor == 'color':
            print('\033[31minvalid email format\033[0m\n')
            print('bad attempts: \033[33m' + str(6 - tries) + '\033[0m\n')
            print('\033[36myou have ' + str(tries) + ' attempts remaining.\033[0m\n\n')
         
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
            print('\n\033[32m email is valid \033[0m\n\n')
         else:
            print('email is valid\n\n')
   
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
    
      for line in pf.readlines():
    
         emailpass = line
         logging.info('INFO: checking login authentication for %s' % emailaddr)
         loginok = checklogin(emailaddr, emailpass, sslcon)
         loginok = str(loginok)
       
         if 'OK' not in loginok:
            logging.info('INFO: bad password. skipping to next line.')
            continue
          
         else:
            logging.info('INFO: LOGIN to %s successful' % emailaddr)
            server.select()
            server.search(None, 'INBOX')
            getimapmulti(emailaddr, emailpass, sslcon, 'OK')
            break
         
   else:
   
      emailpass = getpass.getpass('please enter password --> ')
      getimap(emailaddr, emailpass, sslcon)
   
sys.exit()