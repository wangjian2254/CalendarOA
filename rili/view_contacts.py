#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rili.models import Contacts
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


@client_login_required
def getContacts(request):
    if not hasattr(request.user,'contacts'):
        return getResult(True,'',[])
    l = []
    for u in request.user.contacts.users.all():
        l.append({'username': u.username, 'nickname': u.first_name, 'email':u.email, 'rtx':u.person.rtxnum, 'sms': u.person.telphone})
    return getResult(True, '',l)

@client_login_required
@transaction.commit_on_success
def joinContacts(request):
    usernamelist = request.REQUEST.getlist('usernames')
    do = request.REQUEST.get('do','')
    if hasattr(request.user,'contacts'):
        contact = request.user.contacts
    else:
        contact = Contacts()
        contact.user = request.user
        contact.save()
    if do =='join':
            contact.users.add(*User.objects.filter(username__in=usernamelist))
    elif do == 'out':
            contact.users.remove(*User.objects.filter(username__in=usernamelist))
    return getResult(True, '修改成功',True)



@client_login_required
def findUser(request):
    key = request.REQUEST.get('key','')
    l = []
    userquery = User.objects.filter(is_active=True).filter(Q(username__icontains=key)|Q(email__icontains=key)|Q(first_name__icontains=key)|Q(last_name__icontains=key)|Q(person__rtxnum__icontains=key)|Q(person__telphone__icontains=key))
    for user in userquery:
        l.append({'username': user.username, 'nickname': user.first_name, 'text':'%s:%s'%(user.username,user.first_name)})
    return getResult(True, '',l)
