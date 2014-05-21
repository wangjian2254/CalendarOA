#coding=utf-8
#author:u'王健'
#Date: 14-5-21
#Time: 上午7:56
from django.forms import ModelForm

__author__ = u'王健'


class CustomModelForm(ModelForm):
    def json_error(self,s='\n'):
        msg = []
        for k in self.errors.keys():
            label = self.fields.get(k).label
            error = u"、".join(self.errors.get(k))
            msg.append(u'%s : %s'%(label,error))
        return s.join(msg)
  