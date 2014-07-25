# coding=utf-8
# Date:2014/7/25
# Email:wangjian2254@gmail.com
from riliusers.forms import DepartmentForm
from riliusers.models import Department
from riliusers.threadlocalsperson import get_current_org
from util.jsonresult import getResult, getCacheResult, MyEncoder, getErrorFormResult
from util.loginrequired import client_login_required, client_login_org_required, login_org_is_active_required
from django.db import transaction
from django.core.cache import cache


__author__ = u'王健'


@client_login_required
def getAllOrg(request):
    '''
    获取用户参与的所有组织
    '''
    cache_name = 'allorg_%s' % request.user.pk
    response = getCacheResult(cache_name)
    if response:
        return response
    result = []
    for person in request.user.person_set.all().order_by('-is_active'):
        p = MyEncoder.default(person.org)
        p['person_active'] = person.is_active
        p['pid'] = person.pk
        p['person_name'] = person.name
        result.append(p)

    return getResult(True, None, result, None, cache_name)


@client_login_org_required
def getAllDepart(request):
    '''
    获取组织下所有部门
    '''
    cache_name = 'alldepart_%s' % get_current_org().pk
    response = getCacheResult(cache_name)
    if response:
        return response
    result = []
    for depart in get_current_org().department_set.all():
        d = MyEncoder.default(depart)
        # 外键是如何 序列化的 ？todo

        d['managers'] = MyEncoder.default(depart.managers)
        d['members'] = MyEncoder.default(depart.members)

        result.append(d)

    return getResult(True, None, result, None, cache_name)


@login_org_is_active_required
@transaction.atomic()
def updateDepartment(request):
    pk = request.POST.get('id')
    if pk:
        dfrom = DepartmentForm(request.POST, instance=Department.objects.get(pk=pk))
    else:
        dfrom = DepartmentForm(request.POST)
    if not dfrom.is_valid():
        return getErrorFormResult(dfrom)
    depart = dfrom.save()
    cache.delete('alldepart_%s' % get_current_org().pk)
    d = MyEncoder.default(depart)
    d['managers'] = MyEncoder.default(depart.managers)
    d['members'] = MyEncoder.default(depart.members)
    return getResult(True, u'保存部门信息成功', d)
