from __future__ import print_function
import email, getpass, imaplib, re, sys, os, os.path, datetime

print('''
\033[33m
--------------------------------
------- \033[36m\033[1mEMAIL2FILE v 1.2\033[33m\033[22m -------
-------- \033[35m author : vvn \033[33m --------
--------------------------------
\n
\033[0m
''')

count = 0

emailaddr = raw_input('please enter email --> ')
emailpass = getpass.getpass('please enter password --> ')

atdomain = re.search("@.*", emailaddr).group()
emaildomain = atdomain.translate(None, "@")

#VALIDATE EMAIL USING REGEX
match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

if match:
   count = 0
   print('\033[32memail is valid\033[0m')
   print('checking for gmail')

else:
   count = 1
   print('\033[31minvalid email address')
   print('bad attempts: \033[33m' + str(count) + '\033[0m')
      
   if count > 0 and count < 4:         
      emailaddr = raw_input('enter email again --> ')
      match2 = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
      if match2:
         print('\033[32m email is valid \033[0m')
         emailpass = getpass.getpass('enter password --> ')
         print('checking for gmail')

      else:
         count = 2
         print('\033[31m invalid email address \033[0m')
         print('bad attempts: \033[33m' + str(count) + '\033[0m')
         emailaddr = raw_input('enter email again --> ')
         match3 = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

         if match3:               
            print('\033[32m email is valid \033[0m')
            emailpass = getpass.getpass('enter password --> ')
            print('checking for gmail')

         else:
            count = 3
            print('\033[31m invalid email address \033[0m')
            print('bad attempts: ' + str(count))

            if count > 3:
               print('\033[31m too many bad attempts \033[0m')
               print('aborting..')
               
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
 
         if part.get_content_type() == 'text/html':
            html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
   
         if part.get_content_maintype() == 'multipart':
            continue
            
         if part.get('Content-Disposition') is None:
            continue
            
         filename = part.get_filename()
         
         if bool(filename):
        
            rootdir = 'output'
            user_savename = emailaddr.rstrip(atdomain)
            subdir = user_savename+"_"+emaildomain
        
            detach_dir = os.path.join(rootdir, subdir)
            
            if not os.path.exists(detach_dir):
               os.makedirs(detach_dir)
        
            att_path = os.path.join(detach_dir, 'attachments', filename)
            
            if 'attachments' not in os.listdir(detach_dir):
               os.makedirs(detach_dir, 'attachments')
         
            att = True

            if not os.path.isfile(att_path):
               attfile = open(att_path, 'wb')
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
   emaildomain = atdomain.translate(None, "@")
   
   imap_server = 'imap.' + emaildomain
   imap_port = 993
   
   server = imaplib.IMAP4_SSL(imap_server, imap_port)

   loginstatus, logindata = server.login(emailaddr, emailpass)
   
   attempts = 1
   
   while loginstatus != 'OK' and attempts < 5:
               
      emailaddr = raw_input('login failure. please enter email again --> ')
      emailpass = getpass.getpass('please enter password --> ')
      
      matchcred = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)
      
      if matchcred:
                  
         loginstatus, logindata = server.login(emailaddr, emailpass)
         
      else:
         
         print('\033[31m invalid email format \033[0m')
                  
      attempts = attempts + 1
   
   if loginstatus == 'OK':
   
      select_info = server.select('INBOX')

      status, unseen = server.search(None, 'UNSEEN')
      
      print("%d UNREAD MESSAGES" % len(unseen))

      print()
                                            
      typ, listdata = server.list()
         
      print('Response code:', typ)
      print('FOLDERS: ')
      print( listdata )
      
      print('\033[32m login successful, fetching emails.. \033[0m')
         
      # server.list()
         
      server.select()

      result, msgs = server.search(None, 'ALL')
         
      ids = msgs[0]
      id_list = ids.split()
      
      print(id_list)
      
      print('\n')
   
      print('-----------------------------------------------------------\n')
         
      rootdir = 'output'
      
      printdate = str(datetime.date.today())

      prev_file_name = emailaddr+"-"+printdate+"-listpreview.txt"
      prev_complete_name = os.path.join(rootdir, prev_file_name)
      
      prevfile = open(prev_complete_name, 'a')
         
      for email_uid in id_list:

         result, rawdata = server.fetch(email_uid, '(RFC822)')

         rawbody = rawdata[0][1]
         
         m = email.message_from_string(rawbody)
            
         body = decode_email(rawbody)
         
         msgfrom = m['From']
         
         user_save = emailaddr.rstrip(atdomain)
      
         subdir =  user_save + "_" + emaildomain
         save_path = os.path.join(rootdir, subdir)
         
         if not os.path.exists(save_path):
            os.makedirs(save_path)
            
         mbody = email.message_from_string(rawbody)
         
         if mbody.is_multipart():
         
            ext = ".txt"
         
            for mpart in mbody.get_payload():
            
               if re.search('text', mpart.get_content_type()):
                  ext = ".txt"
                  isattach = False
                  
                  if mpart.get_content_type() == 'text/html':
                     ext = ".htm"
                     isattach = False
                  
               else:
                  file_name = mpart.get_filename()
                  isattach = True
                  
         if isattach is False:
            file_name = user_save + "-" + msgfrom[:25] + "-" + email_uid + ext
        
         if file_name is None:
            file_name = user_save + "-" + msgfrom[:25] + "-" + email_uid + ext
        
         complete_name = os.path.join(save_path, file_name)

         if os.path.isfile(complete_name):
         
            print('\033[33m' + complete_name + '\033[34m already exists, skipping.. \033[0m \n')
            
         else:
            
            if isattach is True:
               bodyfile = open(complete_name, 'wb')
               # bodyfile.seek(0)
               bodyfile.write(body)
               bodyfile.close()
               
            else:
               bodyfile = open(complete_name, 'w')
               bodyfile.write(msgfrom)
               bodyfile.write('\n\n')
               bodyfile.write('Decoded:\n\n')
               bodyfile.write(str(body))
               bodyfile.write('\n\nRaw Data:\n\n')
               bodyfile.write(rawbody)
      
            print('\033[36m\033[1mraw message data saved to new file: \033[35m' + complete_name + '\033[0m\n')
            
         typ, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
         print('\033[32m' + typ + '\033[0m')
         print("\n")
         print(data[0][1])
         print("\n \n")
         msgpreview = data[0][1]
                  
         for fm in data[1]:
     
            if(len(fm)>1):
               metadata = self.parseMetadata(fm[0])
               headers = self.parseHeaders(fm[1])
         
               prevfile.write(metadata)
               prevfile.write("\n")
               prevfile.write(headers)
               prevfile.write("\n")
                     
         prevfile.write(msgpreview)
         prevfile.write("\n")
      
      prevfile.close()
      
      print('list of message previews saved as: \033[31m'+prev_complete_name+'\033[0m \n')
      
      print('-----------------------------------------------------------\n')   
    
      print('\033[32m inbox contents successfully saved to file. YAY! \033[0m')
         
      print('logging out..')

      server.logout()
      
      print('logout successful. exiting..')
               
   else:
        
      print('too many logon failures. unable to log onto IMAP server.')
            
if 'gmail.com' in emailaddr:

   print('\033[32mGMAIL address found\033[0m')
   print('attempting logon')

   # connecting to IMAP
   server = imaplib.IMAP4_SSL ('imap.gmail.com')

   while True:

      try:
         loginstatus, logindata = server.login(emailaddr, emailpass)
         if loginstatus == 'OK':
            print('\033[32mlogin successful, fetching emails..\033[0m')

      except:
         pass
         print('error: login failure')
         emailaddr = raw_input('please enter email again --> ')
         matchcred = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

         if matchcred:
            emailpass = getpass.getpass('enter password --> ')
            print('attempting logon again')

         else:
            print('invalid email address')
            emailaddr = raw_input('please enter email again --> ')
            matchcred = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', emailaddr)

      else:
         break
     
   server.list()

   # CHOOSE INBOX OR ALL MAIL BY COMMENTING AND UNCOMMENTING BELOW
   server.select('inbox') # connect to inbox
   #server.select('[Gmail]/All Mail') # connect to all mail folder

   result, uids = server.uid('SEARCH', None, "ALL")

   # search and return unique IDs (UIDs)

   for email_uid in uids[0].split():

      result, data = server.uid('FETCH', email_uid, '(RFC822)')

      body = data[0][1] # raw text of entire email

      rootdir = 'output'
      user_savename = emailaddr.rstrip("@gmail.com")
      subdir = user_savename+"_gmail.com"
      save_path = os.path.join(rootdir, subdir)
         
      if not os.path.exists(save_path):
         os.makedirs(save_path)
            
      mbody = email.message_from_string(body)
      
      msgfrom = mbody['From']
         
      if mbody.is_multipart():
         
         ext = ".txt"
         
         for mpart in mbody.get_payload():
         
            if mpart.get_content_type() == 'text/html':
               ext = ".htm"
            
            else:
               ext = ".txt"
         
      file_name = user_savename+"-"+msgfrom[:25]+"-"+email_uid+ext
            
      complete_name = os.path.join(save_path, file_name)

      if os.path.isfile(complete_name):
         print(complete_name + ' already exists, skipping..')
         continue

      else:
         file = open(complete_name, 'w')
         file.write(body)
         file.close()
      
         print('raw message data saved to new file: \033[31m' + complete_name + '\033[0m')

#############
   # TO FETCH MULTIPLE EMAILS AT ONCE

   #result, uids = server.uid('SEARCH', None, "ALL")

   #fetch_ids = ','.join(uids[0].split())
   ##convert to comma separated list

   #result, data = server.uid('FETCH', fetch_ids, '(RFC822)')
   ##return all emails

   #body = data[0][1]
   #print body

   print('\033[32m inbox contents successfully saved to file. YAY! \033[0m')

   print('logging out..')

   server.logout()

   print('logout successful. exiting..')

else:
   print('trying IMAP connection to server: \033[34mimap.' + emaildomain + '\033[0m' )

   getimap(emailaddr, emailpass)

#############

#############
   # TO GET LATEST EMAIL BY UID

   #latest_email_uid = items[0].split()[-1]

   #result, data = server.uid('FETCH', latest_email_uid, '(RFC822)')
   ##fetch email body (RFC822) for latest UID

   #body = data[0][1] # raw text of entire email
   #print body
#############

#############
   # TO SEARCH LATEST SEQUENTIAL ID INSTEAD OF UNIQUE ID

   #result, sids = mail.search(None, "ALL") 
   #ids = sids[0] # sids is a list
   #id_list = ids.split() # ids is a space separated string 
   #latest_email_id = id_list[-1] # get the latest

   #result, data = mail.fetch(latest_email_id, "(RFC822)")
   ## fetch the email body (RFC822) for the given ID
 
   #body = data[0][1] # raw text of entire email
#############

sys.exit()