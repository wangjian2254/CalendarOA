#coding=utf-8
# Create your views here.
import datetime
import threading
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from rili.models import Schedule,    Person
from rili.szht_amb import regAMB
from rili.warningtools import  dateisright, dateinrange
from util.jsonresult import getResult
from util.loginrequired import client_login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

c = threading.RLock()

def index(request):
    url = 'http://' + request.META['HTTP_HOST'] + '/static/swf/'
    return render_to_response('index.html', {'url': url, 'p': datetime.datetime.now()})


def menu(request):
    '''
     <menuitem label='分类管理' mod='taxkind'></menuitem>
				    <menuitem label='报表管理' mod='bbedit'></menuitem>

				    <menuitem label='知识库编辑' mod='knowledgeedit'></menuitem>
				    <menuitem label='知识库查询' mod='knowledgequery'></menuitem>
    '''
    #

    menuxml = '''
        <?xml version='1.0' encoding='utf-8'?>
                <root>
                    <menu mod='myMenu1' label='分组和通信录'>
                        <menuitem label='常用联系人' mod='contact'></menuitem>
                        <menuitem label='分组管理' mod='group'></menuitem>
                    </menu>
                    <menu mod='myMenu1' label='考试'>
                        <menuitem label='试题分类管理' mod='subjectkind'></menuitem>
                        <menuitem label='试卷分类管理' mod='paperkind'></menuitem>
                        <menuitem label='试卷管理' mod='paper'></menuitem>
                        <menuitem label='题库管理' mod='subject'></menuitem>
                        <menuitem label='我的考试' mod='mypaper'></menuitem>
                    </menu>
                    <menu mod='myMenu1' label='日程'>
                        <menuitem label='日程管理' mod='calendar'></menuitem>
                    </menu>
                    <menu mod='myMenu1' label='消息'>
                        <menuitem label='站内消息' mod='message'></menuitem>
                    </menu>
                    <menu mod='myMenu1' label='系统'>
                        <menuitem label='日志' mod='log'></menuitem>
                    </menu>
                </root>
        '''

    return HttpResponse(menuxml)

def allmanager(request):
    uq = User.objects.filter(is_staff=True).filter(is_active=True)
    l = []
    for u in uq:
        l.append({'username': u.username, 'truename': u.first_name, 'ismanager': u.is_staff, 'isaction': u.is_active,
                  'id': u.pk})

    return getResult(True, '', l)


@client_login_required
def getContacts(request):
    return getResult(True, '',
                     [{'username': u.username, 'nickname': u.first_name} for u in request.user.contacts_list.all()])


@client_login_required
def currentUser(request):
    user = {'username': request.user.username, 'nickname': request.user.first_name, 'email':request.user.email, 'zentao_account':request.user.person.zentao_account, 'zentao_password':request.user.person.zentao_password,
                                'ismanager': request.user.is_staff, 'isaction': request.user.is_active, 'rtx':'','sms':'',
                                'id': request.user.pk}
    if hasattr(request.user,'person'):
        user['rtx'] = request.user.person.rtxnum
        user['sms'] = request.user.person.telphone

    return getResult(True, '', user)


def scheduleToDict(schedule):
    s = {'id': schedule.pk, 'title': schedule.title, 'desc': schedule.desc, 'type':'schedule',
                             'group': schedule.group_id, 'author':schedule.author.username, 'authornickname':schedule.author.first_name,
                             'startdate': schedule.startdate.strftime('%Y%m%d'), 'is_all_day': schedule.is_all_day,
                             'repeat_type': schedule.repeat_type, 'zentaourl':schedule.getZentaoUrl(),
                             'repeat_date': schedule.repeat_date.split(','), 'color': schedule.color,
                             'users': [{'username': u.username, 'nickname': u.first_name} for u in
                                       schedule.users.all()]}
    if schedule.enddate:
        s['enddate'] = schedule.enddate.strftime('%Y%m%d')
    if schedule.time_start != None:
        s['time_start'] = schedule.time_start.strftime('%H%M')
    if schedule.time_end != None:
        s['time_end'] = schedule.time_end.strftime('%H%M')

    s['warningkind']=schedule.warning_type.split(',')
    s['warningtime']=schedule.warning_time.split(',')
    return s

@client_login_required
def getScheduleByDate(request):
    '''
    date 的格式为 yyyymmdd
    如果没有则返回空
    if schedule.repeat_type == REPEAT_TYPE[0][0] or (
                            schedule.repeat_type == REPEAT_TYPE[1][0] and str(date.weekday()) in schedule.repeat_date.split(
                            ',') ) \
                    or ( schedule.repeat_type == REPEAT_TYPE[2][0] and str(date.day) in schedule.repeat_date.split(',')) \
                    or (schedule.repeat_type == REPEAT_TYPE[3][0] and date.strftime(
                            '%m%d') == schedule.startdate.strftime('%m%d')):

    if schedule.startdate <= date <=schedule.enddate or (schedule.startdate<=date and schedule.enddate == None):
                    if schedule.repeat_type == REPEAT_TYPE[0][0] or (schedule.repeat_type == REPEAT_TYPE[1][0] and str(date.weekday()) in schedule.repeat_date.split(',') ) or ( schedule.repeat_type == REPEAT_TYPE[2][0] and str(date.day) in schedule.repeat_date.split(',')) or (schedule.repeat_type == REPEAT_TYPE[3][0] and date.strftime('%m%d') == schedule.startdate.strftime('%m%d')):


    '''
    startdatestr = request.REQUEST.get('startdate', '')
    enddatestr = request.REQUEST.get('enddate', '')
    if startdatestr and enddatestr:
        user = request.user
        groupquery = Group.objects.filter(Q(author=user) | Q(users=user) | Q(observers=user))
        with c:
            startdate = datetime.datetime.strptime(startdatestr, "%Y%m%d")
            enddate = datetime.datetime.strptime(enddatestr, "%Y%m%d")

        result = {}
        scheduledict = {}
        schedulepkset = set()
        for schedule in Schedule.objects.filter(Q(author=user) | Q(users=user) | Q(group__in=groupquery)).filter(
                                                Q(startdate__lte=startdate, enddate__gte=enddate) | Q(
                                                startdate__lte=startdate, enddate__gte=startdate) | Q(
                                        startdate__gte=startdate, enddate__lte=enddate) | Q(startdate__lte=enddate,
                                                                                            enddate__gte=enddate) | Q(
                        startdate__lte=enddate, enddate=None)).order_by('time_start'):
            if schedule.pk in schedulepkset:
                continue
            schedulepkset.add(schedule.pk)
            with c:
                date = datetime.datetime.strptime(startdatestr, "%Y%m%d")
            while date <= enddate:
                if not result.has_key(date.strftime("%Y%m%d")):
                    result[date.strftime("%Y%m%d")] = []
                if dateinrange(date,schedule) and dateisright(date,schedule):
                    if not scheduledict.has_key('%s' % schedule.pk):
                        s=scheduleToDict(schedule)
                        scheduledict['%s' % schedule.pk] = s
                    result[date.strftime("%Y%m%d")].append(str(schedule.pk))
                date += datetime.timedelta(days=1)
        return getResult(True, '', {"schedulemap":scheduledict,'schedulelist':result})
    else:
        return getResult(False, '', None)



@client_login_required
def updateSchedule(request):
    id = request.REQUEST.get('id', '')
    title = request.REQUEST.get('title', '')
    desc = request.REQUEST.get('desc', '')
    startdate = request.REQUEST.get('startdate', '')
    enddate = request.REQUEST.get('enddate', '')
    is_all_day = request.REQUEST.get('is_all_day', '')
    time_start = request.REQUEST.get('time_start', '')
    time_end = request.REQUEST.get('time_end', '')
    repeat_type = request.REQUEST.get('repeat_type', '')
    repeat_date = request.REQUEST.getlist('repeat_date')
    color = request.REQUEST.get('color', '')
    groupid = request.REQUEST.get('groupid', '')
    users = request.REQUEST.getlist('users')

    warning_email = request.REQUEST.get('warning_email', '')
    warning_sms = request.REQUEST.get('warning_sms', '')
    warning_rtx = request.REQUEST.get('warning_rtx', '')
    wl = []
    if warning_email.lower() == 'true':
        wl.append('email')
    if warning_rtx.lower() == 'true':
        wl.append('rtx')
    if warning_sms.lower() == 'true':
        wl.append('sms')

    warning_time1 = request.REQUEST.get('warning_time1', '')
    warning_time2 = request.REQUEST.get('warning_time2', '')
    wtl = [warning_time1, warning_time2]

    if not title or not startdate or not repeat_type or not groupid:
        return getResult(False, u'请完善信息', None)
    if id:
        schedule = Schedule.objects.get(pk=id)
    else:
        schedule = Schedule()
    schedule.title = title
    schedule.desc = desc
    with c:
        schedule.startdate = datetime.datetime.strptime(startdate, "%Y%m%d")
        if enddate:
            schedule.enddate = datetime.datetime.strptime(enddate, "%Y%m%d")
        else:
            schedule.enddate = None
    if is_all_day.lower() == 'true':
        schedule.is_all_day = True
    else:
        schedule.is_all_day = False
    if time_start:
        with c:
            schedule.time_start = datetime.datetime.strptime(time_start, '%H%M')
    else:
        schedule.time_start = None

    if time_end:
        with c:
            schedule.time_end = datetime.datetime.strptime(time_end, '%H%M')
    else:
        schedule.time_end = None
    schedule.warning_time=''
    schedule.warning_type=''
    schedule.repeat_type = repeat_type
    schedule.repeat_date = ','.join(repeat_date)
    schedule.color = int(color)
    if not schedule.author_id:
        schedule.author = request.user
    if schedule.author_id  == request.user.pk:
        schedule.group = Group.objects.get(pk=groupid)
    schedule.save()
    schedule.users = User.objects.filter(username__in=users)
    schedule.save()
    schedule.warning_type = ','.join(wl)
    schedule.warning_time = ','.join(wtl)
    schedule.save()

    #
    # for wt in wl:
    #     for w in wtl:
    #         if w:
    #             rw = RiLiWarning()
    #             rw.fatherid = schedule.pk
    #             rw.type = 'Schedule'
    #             rw.warning_type = wt
    #             rw.timenum = int(w)
    #             rw.is_repeat = True
    #             rw.is_ok = True
    #             rw.save()
    # schedule.save()
    return getResult(True, u'保存成功', scheduleToDict(schedule))


@client_login_required
def delSchedule(request):
    id = request.REQUEST.get('id', '')
    schedule = Schedule.objects.get(pk=id)
    schedule.delete()
    return getResult(True, u'删除成功', id)





