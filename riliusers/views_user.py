# coding=utf-8
# Date:2014/7/25
# Email:wangjian2254@gmail.com
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404
from riliusers.forms import OrganizationForm
from riliusers.models import Organization, Person, Department
from util.jsonresult import getResult, getCacheResult, getErrorFormResult
from util.loginrequired import client_login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache
# UserModel = get_user_model()
# UserModel.objects.all()

__author__ = u'王健'


def logout(request):
    auth_logout(request)
    return getResult(True, '')


def login(request):
    username = request.REQUEST.get('username')
    if username:
        userlist = get_user_model().objects.filter(username=username)[:1]
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
        org_num = request.user.person_set.filter(is_action=True).count()
        if org_num == 1:
            request.session['person'] = request.user.paper_set.filter(is_action=True)[0]
            request.session['org'] = request.session['person'].org
        if not request.user.email_active:
            return getResult(True, u'登录成功,请完成邮箱验证', None, 202)
        return getResult(True, u'登录成功', None)
    else:
        return getResult(False, u'用户名密码错误', request.session.session_key, 500)





@client_login_required
def selectedOrg(request):
    orgid = request.REQUEST.get('orgid')
    org = Organization.objects.get(pk=orgid)
    person = Person.objects.get(user=request.user, org=org)
    if person.is_active:
        request.session['person'] = person
        request.session['org'] = org
        return getResult(True, u'登录成功', {'personid':person.pk, 'org':org.pk})
    return getResult(False, u'您已经离开了 %s, 无法继续工作。'%org.name, None)


def createOrganization(request, person=None):
    '''
    创建组织（组织、根部门、未分组部门、员工信息）
    '''
    if not person:
        person = Person()
        person.user = request.user
        person.name = request.user.name
    orgform = OrganizationForm(request.POST)
    if not orgform.is_valid():
        return getErrorFormResult(orgform)
    org = orgform.save()
    person.org = org
    person.save()
    org.managers.add(person)

    department = Department()
    department.name = org.name
    department.flag = 'root'
    department.icon = org.icon
    department.org = org
    department.save()
    department.managers.add(person)

    free_depart = Department()
    free_depart.name = u'未分组'
    free_depart.flag = 'free'
    free_depart.icon = org.icon
    free_depart.org = org
    free_depart.father = department
    free_depart.save()


@client_login_required
@transaction.atomic()
def regOrganization(request):
    '''
    已登录用户创建组织
    '''
    createOrganization(request)


@transaction.atomic()
def regUser(request):
    '''
    注册新用户
    '''
    flag = request.REQUEST.has_key('flag')
    user = get_user_model()()
    if request.REQUEST.has_key('password'):
        user.set_password(request.REQUEST.get('password'))
    user.username = request.REQUEST.get('username', '')
    user.name = request.REQUEST.get('truename', u'游客')
    if not user.username or get_user_model().objects.filter(username=user.username).count() > 0:
        return getResult(True, u'邮箱已经存在', None, 201)
        # {'success': True, 'message': u'用户名已经存在', 'result': None}
    user.save()

    person = Person()
    person.user = user
    person.name = user.name
    if flag:
        orgquery = Organization.objects.filter(flag=flag)
        if orgquery.count() > 0:
            org = orgquery[0]
            person.org = org
            person.save()
            department = Department.objects.get(org=org, flag='free')
            department.members.add(person)
    else:
        createOrganization(request, person)

    return getResult(True, u'注册成功', {'username': user.get_username(), 'truename': user.name, 'id': user.pk})


@client_login_required
@transaction.atomic()
def addOrganization(request):
    '''
    加入组织
    '''
    flag = request.REQUEST.has_key('flag')
    user = request.user
    person = Person()
    person.user = user
    person.name = user.name
    if flag:
        orgquery = Organization.objects.filter(flag=flag)
        if orgquery.count() > 0:
            org = orgquery[0]
            person.org = org
            person.save()
            department = Department.objects.get(org=org, flag='free')
            department.members.add(person)
            return getResult(True, u'成功加入：%s' % org.name)
        else:
            return getResult(False, u'邀请链接已经失效，请联系（组织/公司）管理员，重新获得邀请。')
    return getResult(False, u'邀请链接已经失效，请联系（组织/公司）管理员，重新获得邀请。')


