#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.forms import ModelForm
from rili.models import RiLiMessage, Schedule

__author__ = u'王健'



class MessageForm(ModelForm):
        class Meta:
                model = RiLiMessage
                fields = ('t', 'title', 'desc', 'fatherMessage')

