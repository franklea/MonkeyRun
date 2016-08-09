import smtplib
from email.mime.text import MIMEText
from email.header import Header

email = raw_input("Please input your email to get the report: ")

def sendmail(receiver, title, body):
    sender = "******"
    host = "smtp.163.com"
    port = 25
    pwd = "********"

    message = MIMEText(body, 'plain', 'utf-8')
    message['from'] = sender
    message['to'] = receiver
    message['subject'] = title
    try:
        s = smtplib.SMTP()
        s.connect(host, port)
        s.login(sender, pwd)
        s.sendmail(sender, receiver, message.as_string())
        s.close()
        print "Email has been sent to your email !"
    except Exception, e:
        print str(e)


title = 'Error Report From Monkey Server'
f = open('test.txt','r')
body = f.read()
f.close()
sendmail(email, title, body)
