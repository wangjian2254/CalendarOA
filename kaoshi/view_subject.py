#coding=utf-8
#author:u'王健'
#Date: 14-5-15
#Time: 下午8:43
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


@client_login_required
def updateSubject(request):
    return getResult(True, '', None)

@client_login_required
def getSubjectByKind(request):
    return getResult(True,'', None)


@client_login_required
def delSubject(request):
    return getResult(True,'', None)


@client_login_required
def doSubjectOption(request):
    return getResult(True,'', None)