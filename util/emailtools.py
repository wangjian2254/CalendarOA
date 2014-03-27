#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'
from django.core.mail import EmailMultiAlternatives

from django.template import loader

from CalendarOA.settings import EMAIL_HOST_EMAIL

import threading

from_email = EMAIL_HOST_EMAIL

class EmailThread(threading.Thread):

    def __init__(self, subject, body, from_email, recipient_list, fail_silently, html):

        self.subject = subject

        self.body = body

        self.recipient_list = recipient_list

        self.from_email = from_email

        self.fail_silently = fail_silently

        self.html = html

        threading.Thread.__init__(self)

    def run (self):

        msg = EmailMultiAlternatives(self.subject, self.body, self.from_email, self.recipient_list)

        if self.html:

            msg.attach_alternative(self.body,self.html)

            msg.send(self.fail_silently)

def send_mail(subject, body,  recipient_list, fail_silently=False, html=None, *args, **kwargs):

    EmailThread(subject, body, from_email, recipient_list, fail_silently, html).start()

def test_mail(request):

    subject = u'邮件主题'

    to_mail_list = ['abc@gmail.com','test@qq.com']

    body = loader.render_to_string('mail_template.html',

    {'email':None,'date':'2014', }

    )

    send_mail(subject,body,from_email,to_mail_list,html="text/html")

    return "ok"

