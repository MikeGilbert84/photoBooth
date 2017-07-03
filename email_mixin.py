'''
Created on Feb 25, 2013

@author: robertb
'''

import logging
import os
import threading
import smtplib
import datetime
import mimetypes
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64




class EmailMixin(object):
    '''Email Utility Class'''
    def __init__(self):
        self.today = datetime.date(2017,7,1)

        self.settings = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_secure': 1,
            'smtp_username': 'kika.nina.wedding@gmail.com',
            'smtp_password': 'Pel9t9n123',
            'smtp_split_to': 1,
        }



    def makePart(self, content, mimetype):
        part = MIMEText(str(content))
        part.set_type(mimetype)
        return part
        

    def _email_orig(self, subject, text, attachmentFilePaths, fromaddr, toaddrs, async=False, parts=[]):
        """Emails to multiple recipients are sent individually.
        
           parts are additional multipart/mime components to embed in the email 
           e.g.('content', 'mimetype') 
               ('<strong>Hello World</strong>', 'text/html')
        
        """
        if async is False:
            sendfunc = self._send_email_
        else:
            sendfunc = self._send_email_async_
        
        fromaddr = fromaddr
        
        if parts is None:
            parts = []
        parts = [(text, 'text/plain')] + parts
        
        if isinstance(toaddrs,str):
            msg = MIMEMultipart('alternative')
            msg['From'] = fromaddr
            msg['To'] =  toaddrs
            msg['Subject'] = subject
            for part in parts:
                msg.attach(self.makePart(*part))
            for attachmentFilePath in attachmentFilePaths:
                msg.attach(self._attachment_(attachmentFilePath))
            sendfunc(msg.as_string(), fromaddr, toaddrs)
        else:
            for address in toaddrs:
                if address:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = fromaddr
                    msg['To'] =  address
                    msg['Subject'] = subject
                    for part in parts:
                        msg.attach(self.makePart(*part))
                    for attachmentFilePath in attachmentFilePaths:
                        msg.attach(self._attachment_(attachmentFilePath))
                    sendfunc(msg.as_string(), fromaddr, address)


    def _email_(self, subject, text, attachmentFilePaths, fromaddr, toaddrs,async=False, html=None):
        """
        Generate the core of the email message regarding the parameters.
        The structure of the MIME email may vary, but the general one is as follow::
            multipart/mixed 
             |
             +-- multipart/related 
             |    |
             |    +-- multipart/alternative 
             |    |    |
             |    |    +-- text/plain (text version of the message)
             |    |    +-- text/html  (html version of the message)
             |    |     
             |    +-- image/gif  (where to include embedded contents)
             |
             +-- application/msword (where to add attachments)                
        """


        smtp_split_to = self.settings.get('smtp_split_to')
        attachmentFilePaths = attachmentFilePaths if isinstance(attachmentFilePaths, (list, tuple, set)) else []
        
        if async is False:
            sendfunc = self._send_email_
        else:
            sendfunc = self._send_email_async_

        if isinstance(toaddrs,(str, unicode)):
            toaddrs = toaddrs.split(',')
        
        if smtp_split_to:
            recipients = toaddrs[:]
        else:
            recipients = [toaddrs[:]]
            
        for address in recipients:
            if html:
                if text is None:
                    main_body = MIMEText(html, "html")
                else:
                    main_body = MIMEMultipart("alternative")
                    main_body.attach(MIMEText(text, "plain"))
                    main_body.attach(MIMEText(html, "html"))
            else:
                main_body = MIMEText(text, 'plain') 
            if len(attachmentFilePaths) > 0:
                tmpmsg = main_body
                main_body = MIMEMultipart()
                main_body.attach(tmpmsg)    
            for attachmentFilePath in attachmentFilePaths:
                main_body.attach(self._attachment_(attachmentFilePath))
            main_body['subject'] = subject
            main_body['To'] = ", ".join(address) if isinstance(address, list) else address 
            main_body['From'] = fromaddr
            main_body.preamble = 'This is a multi-part message in MIME format.'
            main_body = main_body.as_string()
            if isinstance(address, list):
                #print("send multiple to {}".format(address))              
                sendfunc(main_body, fromaddr, address, self.settings)
            else:
                #print("send individual {}".format(address))
                sendfunc(main_body, fromaddr, [address], self.settings)
                
     

    def _attachment_(self, attachmentFilePath):
        contentType, encoding = mimetypes.guess_type(attachmentFilePath)
        if contentType is None or encoding is not None:
            contentType = 'application/octet-stream'
        mainType, subType = contentType.split('/', 1)
        file = open(attachmentFilePath, 'rb')
        if mainType == 'text':
            attachment = MIMEText(file.read())
        elif mainType == 'message':
            attachment = email.message_from_file(file)
        elif mainType == 'image':
            attachment = MIMEImage(file.read(),_subType=subType)
        elif mainType == 'audio':
            attachment = MIMEAudio(file.read(),_subType=subType)
        else:
            attachment = MIMEBase(mainType, subType)
            attachment.set_payload(file.read())
            encode_base64(attachment)
        file.close()
        attachment.add_header('Content-Disposition', 'attachment',   filename=os.path.basename(attachmentFilePath))
        return attachment
        

    def _send_email_(self, msg, fromaddr, toaddrs, settings={}):
        smtp_port = settings.get('smtp_port')
        smtp_server = settings.get('smtp_server')
        smtp_secure = settings.get('smtp_server') != 0
        smtp_username = settings.get('smtp_username')
        password = settings.get('smtp_password')
        
        logging.debug(u'connecting to {}:{}'.format(smtp_server, smtp_port))
        try:
            smtp = smtplib.SMTP(smtp_server, smtp_port)
        
            if smtp_secure:
                logging.debug(u'starting ttls')
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
        
            if smtp_username:
                logging.debug(u'logging in as {}'.format(smtp_username))
                smtp.login(smtp_username, password)
            
            logging.debug(u'sending email to {}'.format(toaddrs))
            smtp.sendmail(fromaddr, toaddrs, msg)
            logging.debug(u'closing smtp connection')
            smtp.quit()
        except Exception, e:
            error = u'Error sending mail via to {} {} ({}) : {}'.format(smtp_server, smtp_port, smtp_secure, e)
            raise Exception(error)

    def _send_email_async_(self, msg, fromaddr, toaddrs, settings={}):
        # sending mail can be slow (e.g. 30 second delay artificially introduced in the relay to prevent spamming)
        # this is rather poor fire and forget solution (really the emails should be queued in the db and a separate process
        # sends, with retrying etc.)
        t = threading.Thread(target=self._send_email_, args=(msg, fromaddr, toaddrs, settings))
        t.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    sending_email = EmailMixin()
    toaddrs = ['bill.gilbert@genoa.io']
    fromaddr = 'bill.gilbert@mac.com'
    subject = 'Test Email'
    bodytext = 'none'
    html = "<html><body><h3>Hello world 4</h3></body></html>"
    attachmentFilePaths = [__file__]
    home = os.path.expanduser("~") + '/Desktop'
    the_file_22 = os.path.join(home, 'IMG_1680.JPG')
    sending_email._email_(subject,bodytext,[the_file_22],fromaddr,toaddrs,html=html)




    
    
    