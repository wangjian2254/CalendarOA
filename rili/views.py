#coding=utf-8
# Create your views here.
import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from rili.models import Schedule, REPEAT_TYPE, Group
from util.jsonresult import getResult
from util.loginrequired import client_login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

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

    menuxml = '''
        <?xml version='1.0' encoding='utf-8'?>
                <root>
                    <menu mod='myMenu1' label='日程管理'>

                        <menuitem label='日程管理' mod='calendar'></menuitem>


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

        return getResult(True, u'登录成功')
    else:
        return getResult(False, u'用户名密码错误')


def regUser(request):
    result = saveUser(request)
    if result.get('success'):
        auth_login(request, User.objects.get(pk=result.get('result').get('pk')))

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return getResult(True, '', None)
    else:
        return getResult(False, '注册失败', None)


def saveUser(request):
    id = request.REQUEST.get('id', '')
    if id:
        user = User.objects.get(pk=id)
    else:
        user = User()
        user.set_password('111111')
        user.username = request.REQUEST.get('username', '')
        if not user.username or User.objects.filter(username=user.username).count() > 0:
            return getResult(False, u'用户名已经存在', None)
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
    return getResult(True, '', {'username': user.username, 'truename': user.first_name, 'ismanager': user.is_staff,
                                'isaction': user.is_active, 'id': user.pk})


def allmanager(request):
    uq = User.objects.filter(is_staff=True).filter(is_active=True)
    l = []
    for u in uq:
        l.append({'username': u.username, 'truename': u.first_name, 'ismanager': u.is_staff, 'isaction': u.is_active,
                  'id': u.pk})

    return getResult(True, '', l)

@client_login_required
def currentUser(request):

    return getResult(True, '', {'username': request.user.username, 'truename': request.user.first_name,
                                    'ismanager': request.user.is_staff, 'isaction': request.user.is_active,
                                    'id': request.user.pk})



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

    '''
    date = request.REQUEST.get('date', '')
    if date:
        user = request.user
        groupquery = Group.objects.filter(Q(author=user)|Q(users=user))
        date = datetime.datetime.strptime(date, "%Y%m%d")
        result = []
        for schedule in Schedule.objects.filter(Q(author=user)|Q(users=user)|Q(group__in=groupquery)).filter(
                        Q(startdate__lte=date,enddate__gte=date) | Q(startdate__lte=date,enddate=None)):
            if not (not (schedule.repeat_type == REPEAT_TYPE[0][0]) and not (
                            schedule.repeat_type == REPEAT_TYPE[1][0] and str(
                            date.weekday()) in schedule.repeat_date.split(
                            ',') ) and not (
                    schedule.repeat_type == REPEAT_TYPE[2][0] and str(date.day) in schedule.repeat_date.split(','))) \
                    or (schedule.repeat_type == REPEAT_TYPE[3][0] and date.strftime(
                            '%m%d') == schedule.startdate.strftime('%m%d')):
                s = {'id': schedule.pk, 'title': schedule.title, 'desc': schedule.desc, 'group':schedule.group_id,
                     'startdate': schedule.startdate.strftime('%Y%m%d'), 'is_all_day': schedule.is_all_day,
                     'time_start': schedule.time_start.strftime('%H:%M'),
                     'time_end': schedule.time_start.strftime('%H:%M'), 'repeat_type': schedule.repeat_type,
                     'repeat_date': schedule.repeat_date.split(','), 'color': schedule.color,
                     'users': [{'username': u.username, 'nickname': u.first_name} for u in schedule.users.all()]}
                if schedule.enddate:
                    s['enddate'] = schedule.enddate.strftime('%Y%m%d')
                result.append(s)
        return getResult(True, '', result)
    else:
        return getResult(False, '', None)

@client_login_required
def updateSchedule(request):
    id = request.REQUEST.get('id','')
    title = request.REQUEST.get('title','')
    desc = request.REQUEST.get('desc','')
    startdate = request.REQUEST.get('startdate','')
    enddate = request.REQUEST.get('enddate','')
    is_all_day = request.REQUEST.get('is_all_day','')
    time_start = request.REQUEST.get('time_start','')
    time_end = request.REQUEST.get('time_end','')
    repeat_type = request.REQUEST.get('repeat_type','')
    repeat_date = request.REQUEST.getlist('repeat_date','')
    color = request.REQUEST.get('color','')
    groupid = request.REQUEST.get('groupid','')
    users = request.REQUEST.getlist('users','')
    if not title or not startdate or not repeat_type or not repeat_date or not groupid:
        return getResult(False,u'请完善信息',None)
    if id:
        schedule = Schedule.objects.get(pk=id)
    else:
        schedule = Schedule()
    schedule.title = title
    schedule.desc = desc
    schedule.startdate = datetime.datetime.strptime(startdate,"%Y%m%d")
    if enddate:
        schedule.enddate = datetime.datetime.strptime(enddate,"%Y%m%d")
    else:
        schedule.enddate = None
    if is_all_day.lower() == 'true':
        schedule.is_all_day = True
    else:
        schedule.is_all_day = False
    if time_start:
        schedule.time_start = datetime.datetime.strptime(time_start,'%H:%M')
    else:
        schedule.time_start = None

    if time_end:
        schedule.time_end = datetime.datetime.strptime(time_end,'%H:%M')
    else:
        schedule.time_end = None

    schedule.repeat_type = repeat_type
    schedule.repeat_date = ','.join(repeat_date)
    schedule.color = color
    schedule.users = User.objects.filter(username__in=users)
    schedule.group = Group.objects.get(pk= groupid)
    schedule.save()
    return getResult(True,u'保存成功',schedule.pk)




