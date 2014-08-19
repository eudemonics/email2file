#!/usr/bin/python
#
##### EMAIL2FILE v1.1
##### download or copy & paste into blank text file and save as "email2file.py"
##### to run, open terminal to script location and enter "python email2file.py"
##### all files are written to unique email user folder within 'output' subdirectory
##### attachments saved either in user folder or user's 'attachments' subfolder
##### questions? bugs? suggestions? contact vvn at:
##### vvn (at) eudemonics (dot) org
 
from __future__ import print_function
import email, base64, getpass, imaplib
import re, sys, os, os.path, datetime, socket

print('''
\033[34m
------------------------------------- \033[33m
----------\033[36m EMAIL2FILE v1.1 \033[33m----------
-----------\033[35m author : vvn \033[33m------------
-------------------------------------
----\033[37m support my work: buy my EP! \033[33m----
---\033[37m http://dreamcorp.bandcamp.com \033[33m---
\033[34m-------------------------------------\n\033[0m
''')

emailaddr = raw_input('please enter email --> ')

#VALIDATE EMAIL USING REGEX
match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

if match:
   print('\033[32m\nemail is valid\033[0m\n\n')
   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]

else:
   tries = 5

   while not match and tries > 0:
   
      print('\033[31minvalid email format\033[0m\n')
      print('bad attempts: \033[33m' + str(6 - tries) + '\033[0m\n')
      print('\033[36myou have ' + str(tries) + ' attempts remaining.\033[0m\n\n')
      emailaddr = raw_input('please enter email again --> ')
      
      match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
      
      if match:
         tries = -1
         break
         
      else:
         tries = tries - 1
        
   if match:
      print('\n\033[32m email is valid \033[0m\n\n')
      atdomain = re.search("@.*", emailaddr).group()
      emaildomain = atdomain[1:]
      
   else:
      print('\033[31munhandled exception. aborting..\033[0m\n')
      sys.exit()
   
   if tries is 0:
      print('\033[31m too many bad attempts using invalid format! \033[0m\n')
      print('aborting..')
      sys.exit()
               
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
               
def getimap(emailaddr, emailpass):

   atdomain = re.search("@.*", emailaddr).group()
   emaildomain = atdomain[1:]
   
   imap_server = 'imap.' + emaildomain
   imap_port = 993
   
   server = imaplib.IMAP4_SSL(imap_server, imap_port)
   attempts = 5

   while True and attempts > 0:

      try:

         loginstatus, logindata = server.login(emailaddr, emailpass)
   
         if loginstatus == 'OK':
   
            select_info = server.select('INBOX')

            status, unseen = server.search(None, 'UNSEEN')
      
            print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))

            print()
                                            
            typ, listdata = server.list()
         
            print('Response code: \n\n\033[32m', typ)
            print('\033[0m\nFOLDERS:\n\n\033[33m', listdata)
      
            print('\033[34m\n\nlogin successful, fetching emails.. \033[0m\n\n')
         
            # server.list()
         
            server.select()

            result, msgs = server.search(None, 'ALL')
         
            ids = msgs[0]
            id_list = ids.split()
      
            print(id_list)
   
            print('\033[37m------------------------------------------------------------\n\033[0m')
         
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
      
                  print('\033[36m\033[1mmessage data saved to new file: \033[35m' + complete_name + '\033[0m\n')
               
               print('\033[37m------------------------------------------------------------\033[0m\n')
            
               resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
               print('\033[35m' + email_uid + '\033[0m\n')
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
                            
            print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')
         
         print('list of message previews saved as: \033[31m'+prev_complete_name+'\033[0m \n')
         
         print('logging out..\n')
            
         server.logout()
            
         print('logout successful. exiting..\n')
         attempts = -1
         break

      except server.error, e:
      
         pass
         print('\033[35mfailed connecting to IMAP server.\033[0m\n')
         print('\033[31merror: \033[33m' + str(e) + '\033[0m\n\n')

         attempts = attempts - 1              

         emailaddr = raw_input('please enter email again --> ')
         emailpass = getpass.getpass('please enter password --> ')
      
         matchaddy = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
      
         while not matchaddy and attempts > 1:
            print('\033[31m invalid email format \033[0m\n')
            attempts = attempts - 1
            
      continue
         
   if attempts is 0:
      print('too many logon failures. unable to log onto IMAP server.')   
      
emailpass = getpass.getpass('please enter password --> ')
            
try:
   print('\ntrying IMAP connection to server: \033[36mimap.' + emaildomain + '\033[0m' )
   getimap(emailaddr, emailpass)
   
except socket.error, e:
   print("Error establishing IMAP connection: ", e)
   sys.exit()
   
sys.exit()