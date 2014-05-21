#coding=utf-8
#author:u'王健'
#Date: 14-5-21
#Time: 上午8:00
from kaoshi.models import Kind
from util.CustomForm import CustomModelForm

__author__ = u'王健'



class KindForm(CustomModelForm):
        class Meta:
                model = Kind
                fields = ('name', 'father_kind')