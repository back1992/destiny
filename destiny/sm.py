# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText


def sm(title, body, *args):
    host = 'smtp.163.com'  # 设置发件服务器地址
    port = 25  # 设置发件服务器端口号。注意，这里有SSL和非SSL两种形式
    sender = '13261871395@163.com'  # 设置发件邮箱，一定要自己注册的邮箱
    pwd = 'Joomla8'  # 设置发件邮箱的密码，等会登陆会用到

    msg = MIMEText(body, 'html')
    msg['subject'] = title
    msg['from'] = sender
    msg['to'] = "linmukong@iCloud.com"
    receiver = args
    if not receiver:
        receiver = '13261871395@163.com'

    s = smtplib.SMTP(host, port)
    s.login(sender, pwd)
    s.sendmail(sender, receiver, msg.as_string())

    print('The mail named %s to %s is sended successly.' % (title, sender,))
