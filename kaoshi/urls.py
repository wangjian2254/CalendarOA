#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls import patterns


urlpatterns = patterns('kaoshi',

                       (r'^updateKind', 'view_kind.updateKind'),
                       (r'^getAllKind', 'view_kind.getAllKind'),
                       (r'^delKind', 'view_kind.delKind'),

                       (r'^updatePaperKind', 'view_paperkinds.updatePaperKind'),
                       (r'^getAllPaperKind', 'view_paperkinds.getAllPaperKind'),
                       (r'^delPaperKind', 'view_paperkinds.delPaperKind'),

                       (r'^updateSubject', 'view_subject.updateSubject'),
                       (r'^getSubjectByKind', 'view_subject.getSubjectByKind'),
                       (r'^getSubjectAll', 'view_subject.getSubjectAll'),
                       (r'^getSubjectById', 'view_subject.getSubjectById'),
                       (r'^delSubject', 'view_subject.delSubject'),
                       (r'^delOption', 'view_subject.delOption'),

                       (r'^updatePaper', 'view_paper.updatePaper'),
                       (r'^getPaper', 'view_paper.getPaper'),
                       (r'^getMyPaper', 'view_paper.getMyPaper'),
                       (r'^answerPaper', 'view_paper.answerPaper'),
                       (r'^doPaperSubject', 'view_paper.doPaperSubject'),
                       (r'^getAllPaper', 'view_paper.getAllPaper'),
                       (r'^delPaper', 'view_paper.delPaper'),
                       (r'^copyPaper', 'view_paper.copyPaper'),




                       )