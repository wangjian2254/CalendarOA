#coding=utf-8
# Create your views here.
import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from rili.models import Schedule,  Group,  Person
from rili.szht_amb import regAMB
from rili.warningtools import  dateisright, dateinrange
from util.jsonresult import getResult
from util.loginrequired import client_login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction



def index(request):
    if request.method != 'GET':
        r='''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
  <response>
    <href>/</href>
    <propstat>
      <prop>
        <resourcetype>
          <C:calendar />
          <collection />
        </resourcetype>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
    <propstat>
      <prop>
        <current-user-principal>
          <unauthenticated />
        </current-user-principal>
        <principal-URL>
          <unauthenticated />
        </principal-URL>
      </prop>
      <status>HTTP/1.1 404 Not Found</status>
    </propstat>
  </response>
</multistatus>
        '''
        h= HttpResponse(r)
        h.status_code = 207
        return h
#
#         with open('%s/index.txt'%MEDIA_ROOT,'w') as f:
#             f.write(request.body)
#         r='''<D:multistatus xmlns:CS="http://calendarserver.org/ns/" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:">
#  <D:response>
#   <D:href>/calendar/dav/wangjian/user/</D:href>
#   <D:propstat>
#    <D:prop>
#     <D:displayname>wangjian</D:displayname>
#     <CS:dropbox-home-URL xmlns:ns4="http://apple.com/ns/ical/">/calendar/dav/wangjian/user/</CS:dropbox-home-URL>
#     <CS:notification-URL xmlns:ns4="http://apple.com/ns/ical/">/calendar/dav/wangjian/user/</CS:notification-URL>
#     <C:calendar-home-set xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>/calendar/r/dav/calendar/wangjian/</D:href>
#     </C:calendar-home-set>
#     <C:calendar-user-address-set xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>mailto:wangjian</D:href>
#     </C:calendar-user-address-set>
#     <C:schedule-inbox-URL xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>/calendar/r/dav/calendar/wangjian/inbox/</D:href>
#     </C:schedule-inbox-URL>
#     <C:schedule-outbox-URL xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>/calendar/r/dav/calendar/wangjian/outbox/</D:href>
#     </C:schedule-outbox-URL>
#     <D:principal-collection-set xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>/calendar/r/dav/users/</D:href>
#     </D:principal-collection-set>
#     <D:principal-URL xmlns:ns4="http://apple.com/ns/ical/">
#      <D:href>/calendar/dav/wangjian/user/</D:href>
#     </D:principal-URL>
#    </D:prop>
#    <D:status>HTTP/1.1 200 OK</D:status>
#   </D:propstat>
#   <D:propstat>
#    <D:prop>
#     <B:allow ed-calendar-component-set xmlns:A="DAV:" xmlns:B="http://calendarserver.org/ns/"/>
#     <A:current-user-principal xmlns:A="DAV:"/>
#     <B:email-address-set xmlns:A="DAV:" xmlns:B="http://calendarserver.org/ns/"/>
#     <A:resource-id xmlns:A="DAV:"/>
#    </D:prop>
#    <D:status>HTTP/1.1 404 Not Found</D:status>
#   </D:propstat>
#  </D:response>
# </D:multistatus>
#         '''
#         return HttpResponse(r)
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
                    <menu mod='myMenu1' label='日程管理'>

                        <menuitem label='日程管理' mod='calendar'></menuitem>
                    </menu>
                    <menu mod='myMenu1' label='消息管理'>

                        <menuitem label='站内消息' mod='message'></menuitem>
                    </menu>
                </root>
        '''

    return HttpResponse(menuxml)


def logout(request):
    auth_logout(request)
    return getResult(True, '')


def login(request):
    username = request.REQUEST.get('username')
    if username:
        userlist = User.objects.filter(username=username)[:1]
        if len(userlist) > 0:
            user = userlist[0]
            if not user.is_active:
                return getResult(False, u'用户已经停止使用。')
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():


        # Okay, security checks complete. Log the user in.
        auth_login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        return getResult(True, u'登录成功',request.session.keys())
    else:
        return getResult(False, u'用户名密码错误',request.session.session_key,500)




def remotelogin(request):
    username = request.REQUEST.get('username')
    if username:
        userlist = User.objects.filter(username=username)[:1]
        if len(userlist) > 0:
            user = userlist[0]
            if not user.is_active:
                return getResult(False, u'用户已经停止使用。')
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():


        # Okay, security checks complete. Log the user in.
        auth_login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        return getResult(True, u'登录成功')
    else:
        raise Http404


def regUser(request):
    result = saveUserFun(request)
    if result.get('success'):
        form = AuthenticationForm(data=request.POST)
        form.is_valid()
        auth_login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return getResult(True, '注册成功', None)
    else:
        return getResult(False, result.get('message'), None)


def saveUser(request):
    result = saveUserFun(request)
    return getResult(True, '修改成功', result.get('result'))


@transaction.commit_on_success
def saveUserFun(request):
    id = request.REQUEST.get('id', '')
    if id:
        user = User.objects.get(pk=id)
    else:
        user = User()
        user.set_password('111111')
        user.username = request.REQUEST.get('username', '')
        user.first_name = request.REQUEST.get('truename', u'游客')
        if not user.username or User.objects.filter(username=user.username).count() > 0:
            return {'success': True, 'message': u'用户名已经存在', 'result': None}
        user.save()
        if 0 == Group.objects.filter(author=user).count():
            g = Group()
            g.author = user
            g.flag = 'default'
            g.color = 0xeaeaea
            g.name = u'%s的日程' % request.REQUEST.get('truename', user.username)
            g.save()
    is_active = request.REQUEST.get('isaction', '')
    if is_active:
        if is_active == 'true':
            user.is_active = True
        else:
            user.is_active = False
    is_staff = request.REQUEST.get('ismanager', '')
    if is_staff:
        if is_staff == 'true':
            user.is_staff = True
        else:
            user.is_staff = False
    user.first_name = request.REQUEST.get('truename', u'游客')
    if request.REQUEST.has_key('password'):
        user.set_password(request.REQUEST.get('password'))
    user.save()
    email = request.REQUEST.get('email', '')
    if email:
        try:
            user.email = email
            user.save()
        except:
            pass
    if not hasattr(user, 'person'):
        person = Person()
        person.user = user
    else:
        person = user.person

    person.rtxnum = request.REQUEST.get('rtx', '')
    person.telphone = request.REQUEST.get('sms', '')
    person.zentao_account = request.REQUEST.get('zentao_account', '')
    person.zentao_password = request.REQUEST.get('zentao_password', '')
    person.save()
    regAMB(person)
    return {'success': True, 'message': '',
            'result': {'username': user.username, 'truename': user.first_name, 'ismanager': user.is_staff,
                       'isaction': user.is_active, 'id': user.pk}}


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
    if schedule.time_start:
        s['time_start'] = schedule.time_start.strftime('%H%M')
    if schedule.time_end:
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
@transaction.commit_on_success
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
        schedule.time_start = datetime.datetime.strptime(time_start, '%H%M')
    else:
        schedule.time_start = None

    if time_end:
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
@transaction.commit_on_success
def delSchedule(request):
    id = request.REQUEST.get('id', '')
    schedule = Schedule.objects.get(pk=id)
    schedule.delete()
    return getResult(True, u'删除成功', id)





