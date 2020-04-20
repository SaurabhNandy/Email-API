from flask import Flask, request, jsonify
import smtplib, ssl, email, imaplib
from smtplib import SMTPAuthenticationError 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_ssl_host = 'smtp.gmail.com'
imap_host = 'imap.gmail.com'
smtp_ssl_port = 465
context = ssl.create_default_context()

app = Flask(__name__)


def authService(sender_email, password, host_type='smtp'):
    if host_type=='smtp':
        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port, context=context)
        try:
            status = server.login(sender_email, password)
            if status[0]==235:
                status = "Accepted"
        except SMTPAuthenticationError:
            status = "Incorrect Username or Password"
    else:
        server = imaplib.IMAP4_SSL(imap_host)
        try:
            status = server.login(sender_email, password) 
            if status[0]=='OK':
                status = "Accepted"
        except imaplib.error:
            status = "Incorrect Username or Password"
    return status, server


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/mail-server/authenticate', methods=["POST"])
def authenticateMail():
    data = request.get_json()
    sender_email = data['sender_email']
    password = data['password']
    status, server = authService(sender_email, password)
    return str(status)


@app.route('/mail-server/send', methods=["POST"])
def sendMail():
    data = request.get_json()
    sender_email = data['sender_email']
    password = data['password']
    receiver_email = data['receiver_email']
    status, server = authService(sender_email, password)
    if status=="Accepted":
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        if "cc" in data:
            message["Cc"] = data['cc']
        if "subject" in data:
            message["Subject"] = data['subject']
        if "body" in data:
            message.attach(MIMEText(data["body"]["content"], data["body"]["type"]))
        try:
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            status = "Mail sent"
        except:
            status = "Error in sending mail"
    return str(status)
    

@app.route('/mail-server/receive', methods=["POST"])
def receiveMail():
    data = request.get_json()
    sender_email = data['sender_email']
    password = data['password']
    status, server = authService(sender_email, password, 'imap')
    response = {"status": status} 
    if status=="Accepted":
        server.select(data['label'])
        if data['next_mail_id']:
            next_mail_id = data['next_mail_id']
        else:
            mail_ids = server.search(None, 'ALL')
            next_mail_id = int(mail_ids[1][0].split()[-1])
        
        result = []
        for id in range(next_mail_id, max(0, next_mail_id-int(data['count'])),-1):
            status, data = server.fetch(str(id), '(RFC822)')
            if type(data[0]) is tuple:
                message = email.message_from_bytes(data[0][1])
                from_ = message['from'].split('<')
                if len(from_)==1:
                    From_id = from_[0].replace('>','')
                    From = From_id
                    if From_id==sender_email:
                        From = 'me'
                else:
                    From = from_[0].replace('"','')
                    From_id = from_[1].replace('>','')

                mail={"id":id, "From":From, "From_id": From_id, "To":message['to'], "Subject":message['subject'], "Date":message['date']}
                if message.is_multipart():
                    content = ''
                    attachment = []
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            content += part.get_payload()
                        if part.get_content_type() == 'multipart/alternative':
                            for p in part.get_payload():
                                if p.get_content_type() == 'text/plain':
                                    content += p.get_payload()
                        if part.get('Content-Disposition') and part.get('Content-Disposition').startswith('attachment'):
                            filename = part.get_filename()
                            typ = part.get_content_type()
                            attachment.append({"filename": filename, "type": typ, "file":part.get_payload()})
                    mail["Attachments"] = attachment
                else:
                    content = message.get_payload()
                mail["Content"] = content
                result.append(mail)
        response["next_mail_id"] = id-1
        response["result"] = result
    return jsonify(response)
    
    
if __name__ == '__main__':
   app.run('localhost', 5000, debug = True)
