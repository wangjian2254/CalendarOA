#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.db import transaction
from oamessage.forms import MessageForm
from models import OAMessage, ReceiveMessage
from util.jsonresult import getResult
from util.loginrequired import client_login_required


__author__ = u'王健'


def getUnReadMessageCount(user):
    '''
    查询未读信息数量，根据用户
    '''
    num = ReceiveMessage.objects.filter(user=user, is_read=False).count()
    return num


@client_login_required
def getUnReadCount(request):
    '''
    查询未读信息数量
    '''
    num = getUnReadMessageCount(request.user)
    return getResult(True, '', '%s'%num)


@client_login_required
def updateMessage(request):
    '''
    修改、新建 信息，是保存为草稿，还是直接发送
    '''
    pk = request.REQUEST.get('id', '')
    if pk:
        messageForm = MessageForm(request.POST, instance = OAMessage.objects.get(pk=pk))
    else:
        messageForm = MessageForm(request.POST)
    if not messageForm.is_valid():
        msg = messageForm.json_error()
        return getResult(False,msg,None)

    message = messageForm.save(False)
    message.f = request.user
    message.save()
    messageForm.save_m2m()
    result, msg = message.send()
    return getResult(True, msg, {'result': result, 'messageid': message.pk})



@client_login_required
def flagMessage(request):
    try:
        with transaction.atomic():
            pk = request.REQUEST.get('id', '')
            read = request.REQUEST.get('do', 'false')
            if read == 'false':
                read = False
            else:
                read = True
            ReceiveMessage.objects.filter(pk=pk).update(is_read=read)
            return getResult(True, u'操作成功', pk)
    except Exception, e:
        return getResult(False, u'操作失败', None)


@client_login_required
def getMessageByUser(request):
    '''
    type 为信息查询条件 all 为按时间倒序，n条； read 为按时间倒序，已读的 n条；unread 为按时间倒序 未读的n条
    '''
    user = request.user
    type = request.REQUEST.get('type', 'all')
    limit = int(request.REQUEST.get('limit', '30'))
    start = int(request.REQUEST.get('start', '0'))

    messagequery = ReceiveMessage.objects.filter(user=user).order_by('-id')
    if type == 'unread':
        messagequery = messagequery.filter(is_read=False)
    elif type == 'read':
        messagequery = messagequery.filter(is_read=True)
    elif type == 'saved':
        messagequery = OAMessage.objects.filter(flag=True,f=request.user).order_by('-id')
        resultlist = []
        for m in messagequery:

            s = {'id': m.pk,'rid':m.pk, 'title': m.title, 'mfid': m.fatherMessage_id, 'authorname':m.f.first_name, 'author':m.f.username,
                  'datetime': m.createtime.strftime("%Y/%m/%d %H:%M"),'flag':m.flag,'desc':m.desc}
            s['to'] = [{'username': u.username, 'nickname': u.first_name} for u in m.t.all()]
            resultlist.append(s)
        return getResult(True, u'获取信息成功', {'limit': limit, 'start': start, 'total': 0, 'list': resultlist})

    totalnum = messagequery.count()
    resultlist = []
    messageids=[]
    msgread={}
    for m in messagequery[start:limit]:

        s = {'id': m.message_id,'rid':m.pk, 'title': m.message.title, 'mfid': m.message.fatherMessage_id, 'authorname':m.message.f.first_name, 'author':m.message.f.username,
             'is_read': m.is_read, 'datetime': m.message.createtime.strftime("%Y/%m/%d %H:%M")}
        resultlist.append(s)
    return getResult(True, u'获取信息成功', {'limit': limit, 'start': start, 'total': totalnum, 'list': resultlist})


def messageToDict(fm):
    result = {'id': fm.pk, 'flag': fm.flag, 'title': fm.title, 'desc': fm.desc, 'fatherMessage_id':fm.fatherMessage_id,
              'datetime': fm.createtime.strftime("%Y/%m/%d %H:%M"), 'author': fm.f.username,
              'authorname': fm.f.first_name}
    result['to'] = [{'username': u.username, 'nickname': u.first_name} for u in fm.t.all()]

    return result


@client_login_required
def getMessageById(request):
    pk = request.REQUEST.get('id')
    if 0 < ReceiveMessage.objects.filter(user=request.user, message=pk).count():
        m = OAMessage.objects.get(pk=pk)
        if m.fatherMessage_id:
            m = m.fatherMessage

        l = []
        l.append(messageToDict(m))
        for message in OAMessage.objects.filter(fatherMessage=m).order_by('id'):
            l.append(messageToDict(message))
        return getResult(True, u'获取信息成功', l)

    else:
        return getResult(False, u'不能阅读别人的信息', None)





