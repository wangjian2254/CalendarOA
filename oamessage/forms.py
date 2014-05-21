#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django import forms
from django.contrib.auth.models import User
from oamessage.models import OAMessage
from util.CustomForm import CustomModelForm

__author__ = u'王健'




class MessageForm(CustomModelForm):
    t = forms.ModelMultipleChoiceField(User.objects, label=u'接收人',error_messages={'invalid_pk_value':u'%s 不是正确的接收人。'})

    class Meta:
        model = OAMessage
        fields = ('t', 'title', 'desc', 'flag', 'fatherMessage')

