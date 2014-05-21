#coding=utf-8
#author:u'王健'
#Date: 14-5-21
#Time: 上午8:00
from kaoshi.models import Kind, PaperKind, Paper
from util.CustomForm import CustomModelForm

__author__ = u'王健'



class KindForm(CustomModelForm):
    class Meta:
        model = Kind
        fields = ('name', 'father_kind')


class PaperKindForm(CustomModelForm):
    class Meta:
        model = PaperKind
        fields = ('name', 'father_kind')


class PaperForm(CustomModelForm):
    class Meta:
        model = Paper
        fields = ('title', 'content','kinds','subjects','startDate','endDate','joins','is_user','is_pub','is_replay')