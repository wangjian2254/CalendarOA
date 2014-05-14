#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rili.forms import MessageForm
from rili.models import Contacts, OAMessage, ReceiveMessage
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


def getUnReadMessageCount(user):
    num = ReceiveMessage.objects.filter(user=user, is_read=False).count()
    return num


@client_login_required
def getUnReadCount(request):
    num = getUnReadMessageCount(request.user)
    return getResult(True, '', '%s'%num)


@client_login_required
def updateMessage(request):
    try:
        with transaction.commit_on_success():
            pk = request.REQUEST.get('id', '')
            if pk:
                messageForm = MessageForm(request.POST, OAMessage.objects.get(pk=pk))
            else:
                messageForm = MessageForm(request.POST)

            message = messageForm.save(False)
            if not message.f:
                message.f = request.user
            message.save()
            messageForm.save_m2m()
            result, msg = message.send()
            return getResult(True, msg, {'result': result, 'messageid': message.pk})

    except Exception, e:
        return getResult(False, u'发送信息失败', None)


@client_login_required
def flagMessage(request):
    try:
        with transaction.commit_on_success():
            pk = request.REQUEST.get('id', '')
            read = request.REQUEST.get('do', 'false')
            receivemessage = ReceiveMessage.objects.get(pk=pk)
            if read == 'false':
                receivemessage.is_read = False
            else:
                receivemessage.is_read = True
            receivemessage.save()
            return getResult(True, u'操作成功', receivemessage.pk)
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

    totalnum = messagequery.count()
    resultlist = []
    for m in messagequery[start:limit]:
        s = {'id': m.pk, 'mid': m.message_id, 'title': m.message.title, 'mfid': m.message.fatherMessage_id,
             'is_read': m.is_read, 'datetime': m.message.createtime.strftime("%Y/%m/%d %H:%M")}
        resultlist.append(s)
    return getResult(True, u'获取信息成功', {'limit': limit, 'start': start, 'total': totalnum, 'list': resultlist})


def messageToDict(fm):
    result = {'mid': fm.pk, 'flag': fm.flag, 'title': fm.title, 'desc': fm.desc,
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
            fm = m.fatherMessage
            l = []
            for message in OAMessage.objects.filter(fatherMessage=fm).order_by('-id'):
                l.append(messageToDict(message))
            l.append(messageToDict(fm))
            return getResult(True, u'获取信息成功', l)
        else:
            result = messageToDict(m)
            return getResult(True, u'获取信息成功', [result])

    else:
        return getResult(False, u'不能阅读别人的信息', None)





