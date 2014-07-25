#coding=utf-8
#author:u'王健'
#Date: 14-5-21
#Time: 上午8:00
from django import forms
from util.CustomForm import CustomModelForm

__author__ = u'王健'


#
# class PaperForm(CustomModelForm):
#     right_ztdm = forms.CharField(required=False)
#     flag = forms.CharField(required=False)
#     is_pub = forms.BooleanField()
#     guan = forms.ModelChoiceField(required=False,queryset=Guan.objects.all())
#     class Meta:
#         model = Paper
#         fields = ('title','flag', 'content','is_pub','right_ztdm','guan','time')

class OrganizationForm(CustomModelForm):
    right_ztdm = forms.CharField(required=False)
    flag = forms.CharField(required=False)
    is_pub = forms.BooleanField()
    guan = forms.ModelChoiceField(required=False,queryset=Guan.objects.all())
    class Meta:
        model = Organization
        fields = ('name','totalName', 'icon','type','balance','managers','time')
