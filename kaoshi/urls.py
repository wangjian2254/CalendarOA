#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls import patterns


urlpatterns = patterns('kaoshi',

                       (r'^updateKind/$', 'view_kinds.updateKind'),
                       (r'^kindList/$', 'view_kinds.getAllKind'),
                       (r'^kindDel/$', 'view_kinds.delKind'),

                       (r'^updatePaperKind/$', 'view_paperkinds.updatePaperKind'),
                       (r'^paperKindList/$', 'view_paperkinds.getAllPaperKind'),
                       (r'^paperKindDel/$', 'view_paperkinds.delPaperKind'),

                       (r'^updateSubject/$', 'view_kinds.updateKind'),
                       (r'^subjectList/$', 'view_kinds.updateKind'),
                       (r'^subjectDel/$', 'view_kinds.updateKind'),
                       (r'^subjectDoOption/$', 'view_kinds.updateKind'),

                       (r'^updateOption/$', 'view_kinds.updateKind'),
                       (r'^optionList/$', 'view_kinds.updateKind'),
                       (r'^optionDel/$', 'view_kinds.updateKind'),

                       (r'^updatePaper/$', 'view_kinds.updateKind'),
                       (r'^getPaper/$', 'view_kinds.updateKind'),
                       (r'^answerPaper/$', 'view_kinds.updateKind'),
                       (r'^paperDoSubject/$', 'view_kinds.updateKind'),
                       (r'^paperList/$', 'view_kinds.updateKind'),
                       (r'^paperDel/$', 'view_kinds.updateKind'),
                       (r'^paperCopy/$', 'view_kinds.updateKind'),

                       (r'^toupiaoExcel/$', 'view_kinds.updateKind'),



                       )