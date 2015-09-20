# email2file
### a script to automate login to one or many IMAP accounts, and download all email messages and attachments to file.
#### supports single account or lists of multiple emails and passwords, with built-in optional AES 256-bit encryption
and base64 encoding for password lists.  

#### email output is saved to **email-output** folder in script directory.

#### log files are stored to **logs** folder in script directory.

LICENSE AGREEMENT & DISCLAIMER

copyright, copyleft (C) 2014-2015  vvn [ lost @ nobody . ninja ]

    This program is FREE software: you can redistribute it and/or modify
    it as you wish. Copying and distribution of this file, with or without 
    modification, are permitted in any medium without royalty provided the 
    copyright notice and this notice are preserved. This program is offered 
    AS-IS, WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    For more information, please refer to the "LICENSE AND NOTICE" file that should
    accompany all official download releases of this program.
    
**to download using git:**

    git clone https://github.com/eudemonics/email2file.git email2file
    cd email2file
    chmod +x email2file.py
    ./email2file.py

**to encrypt text files:**

    chmod +x encryptlist.py
    ./encryptlist.py
