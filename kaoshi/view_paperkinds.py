#coding=utf-8
#author:u'王健'
#Date: 14-5-15
#Time: 下午8:43
from kaoshi.models import  PaperKind
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


@client_login_required
def getAllPaperKind(request):
    kindlist = []
    kindidlist = []
    kinddict = {}
    for kind in PaperKind.objects.all().order_by('id'):
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
    return getResult(True, u'获取考卷分类成功', kindlist)

@client_login_required
def updatePaperKind(request):
    id = request.REQUEST.get('id', '')
    name = request.REQUEST.get('name', '')
    kindid = request.REQUEST.get('fatherid', '')
    if not name:
        return getResult(False,u'分类名称不能为空',None)
    if id:
        kind = PaperKind.objects.get(pk=id)
    else:
        kind = PaperKind()
    kind.name = name.strip()
    if kindid:
        kind.father_kind = PaperKind.objects.get(pk=kindid)
    kind.save()
    return getResult(True,u'保存分类信息成功', kind.pk)


@client_login_required
def delPaperKind(request):
    id = request.REQUEST.get('id', '')
    if id:
        kind = PaperKind.objects.get(pk=id)
        kind.delete()
    else:
        getResult(False, u'分类不存在', None)

    return getResult(True,'', id)