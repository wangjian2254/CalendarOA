#coding=utf-8
#author:u'王健'
#Date: 14-3-28
#Time: 上午6:43
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rili.models import Group, RiLiWarning, Schedule
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'

def groupTodict(group):
    return {'id': group.pk, 'name': group.name, 'author': group.author.username, 'color': group.color,
                  'userlist': [{'username': u.username, 'nickname': u.first_name} for u in group.users.all()], 'observerlist':[{'username': u.username, 'nickname': u.first_name} for u in group.observers.all()]}


@client_login_required
def getMyGroup(request):
    u = request.user
    l = []
    for group in u.group_sharedobservers.all():
        g = groupTodict(group)
        g['pem'] ='look'
        l.append(g)
    for group in u.group_sharedusers.all():
        g = groupTodict(group)
        g['pem'] ='join'
        l.append(g)
    for group in u.group_set.all():
        g = groupTodict(group)
        g['pem'] ='create'
        l.append(g)

    if len(l) == 0:
        g = Group()
        g.author = u
        g.color = 0xeaeaea
        g.flag = 'default'
        g.name = u'%s的日程' % u.first_name
        g.save()
    return getResult(True, '', l)

@client_login_required
@transaction.commit_on_success
def updateGroup(request):
    id = request.REQUEST.get('id','')
    name = request.REQUEST.get('name','')
    color = request.REQUEST.get('color','')
    join = request.REQUEST.getlist('joins')
    observers = request.REQUEST.getlist('observers')

    if id:
        group = Group.objects.get(pk=id)
    else:
        group = Group()
    group.name = name
    group.author = request.user
    group.color = int(color)
    group.flag = 'custom'
    group.save()

    if join:
        group.users = User.objects.filter(username__in=join)
        group.observers = User.objects.filter(username__in=observers)
        group.users.save()
        group.users.save()

    return getResult(True,'保存成功',group.pk)



@client_login_required
@transaction.commit_on_success
def joinGroup(request):
    id = request.REQUEST.get('id','')
    username = request.REQUEST.get('username','')
    do = request.REQUEST.get('do','')
    usertype = request.REQUEST.get('type','join')
    if id:
        group = Group.objects.get(pk=id)
        if do =='join':
            if usertype=='join' and  username!=group.author.username and 0==group.users.filter(username=username).count():
                group.users.add(User.objects.get(username=username))
                group.observers.remove(User.objects.get(username=username))
                group.users.save()
                group.observers.save()
            if usertype=='observer' and  username!=group.author.username and 0==group.observers.filter(username=username).count():
                group.observers.add(User.objects.get(username=username))
                group.users.remove(User.objects.get(username=username))
                group.users.save()
                group.observers.save()
        elif do == 'out':
            if username!=group.author.username and (1==group.users.filter(username=username).count() or 1==group.observers.filter(username=username).count()):
                group.users.remove(User.objects.get(username=username))
                group.observers.remove(User.objects.get(username=username))
                group.users.save()
                group.observers.save()
        else:
            return getResult(False,u'操作不正确',id)
        return getResult(True,u'完成操作',id)
    else:
        return getResult(False,u'操作不正确',id)

@client_login_required
@transaction.commit_on_success
def delGroup(request):
    id = request.REQUEST.get('id','')

    if id:
        group = Group.objects.get(pk=id)

        if group.author.username==request.user.username:
            RiLiWarning.objects.filter(type='Schedule',fatherid__in=Schedule.objects.filter(group=group)).delete()
            Schedule.objects.filter(group=group).delete()
            group.delete()
        else:
            return getResult(False,u'不具有删除权限',id)
        return getResult(True,u'完成操作',id)
    else:
        return getResult(False,u'操作不正确',id)