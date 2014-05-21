#coding=utf-8
#author:u'王健'
#Date: 14-5-15
#Time: 下午8:43
from django.db import transaction
from kaoshi.forms import KindForm
from kaoshi.models import Kind
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


@client_login_required
def getAllKind(request):
    kindlist = []
    kindidlist = []
    kinddict = {}
    for kind in Kind.objects.all().order_by('id'):
        kinddict['%s' % kind.pk] = {'id': kind.pk,  'fatherid': kind.father_kind_id,
                                      'name': kind.name, 'children': []}
        kindidlist.append(kind.pk)
    for kid in kindidlist:
        kind = kinddict.get(str(kid))
        if not kind['fatherid']:
            kindlist.append(kind)
        else:
            kinddict[str(kind.get('fatherid'))]['children'].append(kind)
    for kind in kinddict.values():
        if len(kind['children']) == 0:
            del kind['children']
    return getResult(True, u'获取试题分类成功', kindlist)

@client_login_required
@transaction.commit_on_success
def updateKind(request):
    pk = request.REQUEST.get('id', '')
    if pk:
        kindForm = KindForm(request.POST, Kind.objects.get(pk=pk))
    else:
        kindForm = KindForm(request.POST)
    if not kindForm.is_valid():
        msg = kindForm.json_error()
        return getResult(False,msg,None)
    kind = kindForm.save()
    return getResult(True,u'保存分类信息成功', kind.pk)


@client_login_required
def delKind(request):
    id = request.REQUEST.get('id', '')
    if id:
        kind = Kind.objects.get(pk=id)
        kind.delete()
    else:
        getResult(False, u'分类不存在', None)

    return getResult(True,'', id)