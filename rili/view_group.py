#coding=utf-8
#author:u'王健'
#Date: 14-3-28
#Time: 上午6:43
from django.contrib.auth.models import User
from django.db.models import Q
from rili.models import Group
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'



@client_login_required
def getMyGroup(request):
    user = request.user

    groupquery = Group.objects.filter(Q(author=user) | Q(users=user)).order_by('id')
    l = []
    for group in groupquery:
        l.append({'id': group.pk, 'name': group.name, 'author': group.author_id, 'color': group.color,
                  'userlist': [{'username': u.username, 'nickname': u.first_name} for u in group.users.all()]})
    if len(l) == 0:
        g = Group()
        g.author = user
        g.color = 0xeaeaea
        g.flag = 'default'
        g.name = u'%s的日程' % user.first_name
        g.save()
    return getResult(True, '', l)

@client_login_required
def updateGroup(request):
    id = request.REQUEST.get('id','')
    name = request.REQUEST.get('name','')
    color = request.REQUEST.get('color','')
    join = request.REQUEST.getlist('joins')

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
        group.save()

    return getResult(True,'创建成功',)



@client_login_required
def joinGroup(request):
    id = request.REQUEST.get('id','')
    username = request.REQUEST.get('username','')
    do = request.REQUEST.get('do','')
    if id:
        group = Group.objects.get(pk=id)
        if do =='join':
            if username!=group.author.username and 0==group.users.filter(username=username).count():
                group.users.add(User.objects.get(username=username))
                group.save()
        elif do == 'out':
            if username!=group.author.username and 1==group.users.filter(username=username).count():
                group.users.remove(User.objects.get(username=username))
                group.save()
        else:
            return getResult(False,u'操作不正确',id)
        return getResult(True,u'完成操作',id)
    else:
        return getResult(False,u'操作不正确',id)