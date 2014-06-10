#coding=utf-8
#author:u'王健'
#Date: 14-5-15
#Time: 下午8:43
from django.db.models import Q
from kaoshi.forms import SubjectForm
from kaoshi.models import Subject, Option, Kind
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


@client_login_required
def updateSubject(request):
    pk = request.REQUEST.get('id', '')
    if pk:
        kindForm = SubjectForm(request.POST, instance = Subject.objects.get(pk=pk))
    else:
        kindForm = SubjectForm(request.POST)

    if not kindForm.is_valid():
        msg = kindForm.json_error()
        return getResult(False,msg,None)
    if not kindForm.instance.accuracy:
        kindForm.instance.accuracy=0.0
    kind = kindForm.save()
    for i in range(20):
        id = request.REQUEST.get("option_id_%s"%i,None)
        content = request.REQUEST.get("option_content_%s"%i,None)
        is_right = request.REQUEST.get("option_is_right_%s"%i,None)
        if id or content or is_right:
            if is_right=='true':
                is_right=True
            else:
                is_right = False
            if id:
                option = Option.objects.get(pk=id)
            else:
                option = Option()
            option.content = content
            option.is_right = is_right
            option.subject = kind
            option.save()


    return getResult(True,u'保存试题信息成功', kind.pk)

@client_login_required
def getSubjectByKind(request):
    kind = request.REQUEST.get('kind',None)
    if kind:
        sl = []
        for subject in Subject.objects.filter(Q(kinds__in=Kind.objects.filter(name__icontains=kind))|Q(title__icontains=kind)):
            sl.append({'id':subject.pk, 'title':subject.title, 'bz':subject.bz,'accuracy':subject.accuracy})
        return getResult(True,'', sl)
    else:
        return getResult(False,u'请提供关键字',None)

@client_login_required
def getSubjectAll(request):
    limit = int(request.REQUEST.get('limit', '40'))
    start = int(request.REQUEST.get('start', '0'))
    sl = []
    subjectquery = Subject.objects.all().order_by('-id')
    totalnum = subjectquery.count()
    for subject in subjectquery[start:start+limit]:
        sl.append({'id':subject.pk, 'title':subject.title, 'bz':subject.bz,'accuracy':subject.accuracy})
    return getResult(True,'', {'result':sl, 'limit': limit, 'start': start, 'total': totalnum})



@client_login_required
def getSubjectById(request):
    id = request.REQUEST.get('id', '')
    if id:
        kind = Subject.objects.get(pk=id)
        k = {'id':kind.pk,'title':kind.title, 'kinds':[k.pk for k in kind.kinds.all()], 'bz':kind.bz, 'accuracy':kind.accuracy}
        k['options']=[]
        for o in Option.objects.filter(subject=kind):
            k['options'].append({'id':o.pk,'content':o.content,'is_right':o.is_right})



        return getResult(True, u'获取考题成功', k)
    else:
        return  getResult(False, u'考题不存在', None)


@client_login_required
def delSubject(request):
    id = request.REQUEST.get('id', '')
    if id:
        kind = Subject.objects.get(pk=id)
        kind.delete()
    else:
        return  getResult(False, u'考题不存在', None)

    return getResult(True, u'考题删除成功', id)


@client_login_required
def delOption(request):
    id = request.REQUEST.get('id', '')
    if id:
        kind = Option.objects.get(pk=id)
        kind.delete()
    else:
        getResult(False, u'选项不存在', None)

    return getResult(True,u'选项删除成功', id)