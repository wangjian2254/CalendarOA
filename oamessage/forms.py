#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.forms import ModelForm
from oamessage.models import OAMessage

__author__ = u'王健'



class MessageForm(ModelForm):
        class Meta:
                model = OAMessage
                fields = ('t', 'title', 'desc', 'flag', 'fatherMessage')

