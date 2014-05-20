#coding=utf-8
#author:u'王健'
#Date: 14-5-15
#Time: 下午8:43
import datetime
from kaoshi.models import Paper
from util.jsonresult import getResult

__author__ = u'王健'


def getAllPaper(request):
    '''
    获取所有试卷
    '''
    paperlist = []

    is_pub = request.REQUEST.get('is_pub', '')
    is_user = request.REQUEST.get('is_user', '')
    is_replay = request.REQUEST.get('is_replay', '')

    title = request.REQUEST.get('title', '')
    kinds = request.REQUEST.getlist('kinds', [])
    # start = request.REQUEST.get('startdate', None)
    # end = request.REQUEST.get('enddate', None)
    # if start and end:
    #     start = datetime.datetime.strptime(start, "%Y/%m/%d")
    #     end = datetime.datetime.strptime(end, "%Y/%m/%d") + datetime.timedelta(days=1)


    limit = int(request.REQUEST.get('limit', '40'))
    start = int(request.REQUEST.get('start', '0'))
    paperquery = Paper.objects.all().order_by('-id')

    if is_pub:
        if is_pub=='true':
            paperquery = paperquery.filter(is_pub=True)
        else:
            paperquery = paperquery.filter(is_pub=False)
    if is_user:
        if is_user == 'true':
            paperquery = paperquery.filter(is_user=True)
        else:
            paperquery = paperquery.filter(is_user=True)
    if is_replay:
        if is_replay == 'true':
            paperquery = paperquery.filter(is_replay=True)
        else:
            paperquery = paperquery.filter(is_replay=True)
    if title:
        paperquery = paperquery.filter(title__icontains = title)

    if kinds:
        paperquery = paperquery.filter(kinds__in=kinds)



    totalnum = paperquery.count()
    for p in paperquery[start:start+limit]:
        paperlist.append({"id":p.pk, 'title':p.title, 'startDate':unicode(p.startDate),'endDate':unicode(p.endDate),
                          'is_user':p.is_user,'is_pub':p.is_pub,'is_replay':p.is_replay})
    return getResult(True, '', {'result':paperlist, 'limit': limit, 'start': start,
                                'total': totalnum})


def updatePaper(request):
    '''
    修改一个试卷
    '''

    return getResult(True, '', None)


def doPaperSubject(request):
    '''
    管理试卷的试题
    '''
    return getResult(True, '', None)


def delPaper(request):
    '''
    删除一个试卷，设置为不公开
    '''
    return getResult(True, '', None)


def getPaper(request):
    '''
    根据 id 获取一张试卷的完整信息，包括题目
    '''
    return getResult(True, '', None)



def getMyPaper(request):
    '''
    type ：need、do 两个值
    need:获取所有需要我做的试卷
    do:获取我做过的所有试卷
    '''
    return getResult(True, '', None)


def answerPaper(request):
    '''
    提交某个试卷的答案，计算结果并返回
    '''
    return getResult(True, '', None)



def copyPaper(request):
    '''
    根据指定试卷，复制一份试卷包括 考题
    '''
    return getResult(True, '', None)

