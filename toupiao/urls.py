#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls import patterns
from toupiao.views import  savesubjectoption, showsubjectoption, showTouPiao, toupiaoPage, toupiaoResult, endnewslist,toupiaoerror, toupiaoExcel, initUser


urlpatterns = patterns('toupiao',

                       (r'^savesubjectoption/$', savesubjectoption),
                       (r'^showsubjectoption/$', showsubjectoption),
                       (r'^showTouPiao/$', showTouPiao),
                       (r'^toupiaoPage/$', toupiaoPage),
                       (r'^toupiaoResult/$', toupiaoResult),
                       (r'^endnewslist/$', endnewslist),
                       (r'^error/$', toupiaoerror),
                       (r'^repassword/$', repassword),
                       (r'^toupiaoExcel/$', toupiaoExcel),
                       (r'^initUser/$', initUser),



                       )