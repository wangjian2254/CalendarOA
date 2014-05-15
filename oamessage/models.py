#coding=utf-8
#author:u'王健'
#Date: 14-5-14
#Time: 下午9:10
__author__ = u'王健'

from django.contrib.auth.models import User
from django.db import models


class OAMessage(models.Model):
    '''
    站内短消息
    '''
    f = models.ForeignKey(User, related_name='from_user', verbose_name=u'发起人')
    t = models.ManyToManyField(User, related_name='to_user', verbose_name=u'接收人', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name=u'标题', null=True, blank=True)
    desc = models.TextField(verbose_name=u'内容', null=True, blank=True)
    createtime = models.DateTimeField(auto_created=True, verbose_name=u'创建日期')
    flag = models.BooleanField(default=True, verbose_name=u'是否草稿')
    fatherMessage = models.ForeignKey('OAMessage', verbose_name=u'父级信息', null=True, blank=True)

    def send(self):
        if self.flag:
            return (False, u'草稿不可以发送')
        elif self.t.count() == 0:
            return (False, u'没有指定接收人')
        else:
            for user in self.t.all():
                receiveMessage = ReceiveMessage()
                receiveMessage.message = self
                receiveMessage.user = user
                receiveMessage.is_read = False
                receiveMessage.save()
            return (True, u'发送成功')


class ReceiveMessage(models.Model):
    message = models.ForeignKey(OAMessage)
    user = models.ForeignKey(User, verbose_name=u'接收人')
    is_read = models.BooleanField(default=False, verbose_name=u'是否已读')

