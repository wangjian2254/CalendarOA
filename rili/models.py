#coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
# Create your models here.

REPEAT_TYPE = (('daily', u'每天的'), ('weekly', u'每周的'), ('monthly', u'每月的'), ('yearly', u'每年的'))

class Person(models.Model):
    user = models.OneToOneField(User,verbose_name=u'账户')
    telphone = models.CharField(max_length=15, db_index=True, null=True, blank=True, verbose_name=u'手机号码')
    rtxnum = models.CharField(max_length=30, db_index=True, null=True, blank=True, verbose_name=u'腾讯通账号')

class Contacts(models.Model):
    user = models.OneToOneField(User,verbose_name=u'通信录隶属')
    users = models.ManyToManyField(User,related_name=u'contacts_list',verbose_name=u'通信录列表')


class Group(models.Model):
    '''
    日程分组
    '''
    name = models.CharField(max_length=30, verbose_name=u'分组名称')
    flag = models.CharField(max_length=10,verbose_name=u'标示',help_text=u'default :默认分组，custom: 用户自建，system:系统自建')
    color = models.IntegerField(verbose_name=u'html颜色值')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    users = models.ManyToManyField(User, related_name=u'group_sharedusers', verbose_name=u'分享用户')


class Schedule(models.Model):
    '''
    日程
    '''

    title = models.CharField(max_length=200, verbose_name=u'日程名称')
    desc = models.CharField(max_length=4000, verbose_name=u'备注')
    startdate = models.DateTimeField(default=datetime.now, db_index=True, verbose_name=u'开始日期', help_text=u'如果每年重复，开始日期，就是重复的日子')
    enddate = models.DateTimeField(default=datetime.now, db_index=True, null=True, blank=True, verbose_name=u'结束日期', help_text=u'为空，则永远重复')
    is_all_day = models.BooleanField(default=False, verbose_name=u'是否全天任务', help_text=u'全天任务不需要不需要开始时间')
    time_start = models.TimeField(verbose_name=u'开始时间', null=True, blank=True)
    time_end = models.TimeField(verbose_name=u'结束时间', null=True, blank=True)
    repeat_type = models.CharField(choices=REPEAT_TYPE,default=REPEAT_TYPE[0][0], max_length=10, verbose_name=u'重复方式')
    repeat_date = models.CommaSeparatedIntegerField(max_length=200,null=True, blank=True, verbose_name=u'重复时间',
                                                    help_text=u'这是一个逗号分隔的数字字符串，如：‘1,2,3’,如果重复方式为周，数字代表星期数 星期一：0，星期日：6，如果重复方式为月，数字代表日子，1号：1,31号：31')
    color = models.IntegerField( verbose_name=u'html颜色值',help_text=u'颜色不同可以区分缓急，可以作为日程的小分组')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    users = models.ManyToManyField(User, related_name=u'schedule_sharedusers', verbose_name=u'参与用户')
    group = models.ForeignKey(Group,verbose_name=u'隶属分组')






class Task(models.Model):
    '''
    任务
    '''
    title = models.CharField(max_length=200,verbose_name=u'任务名称')
    desc = models.CharField(max_length=4000, verbose_name=u'备注')
    startdate = models.DateField(default=datetime.now, db_index=True, verbose_name=u'创建日期')
    enddate = models.DateField(default=datetime.now, db_index=True, verbose_name=u'截止日期')
    status = models.BooleanField(default=False, db_index=True,verbose_name=u'完成状态')
    color = models.IntegerField( verbose_name=u'html颜色值',help_text=u'颜色不同可以区分缓急，可以作为日程的小分组')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    users = models.ManyToManyField(User, related_name=u'task_sharedusers', verbose_name=u'参与用户')


class RiLiWarning(models.Model):
    '''
    提醒，为日程或任务 创建的提醒
    '''
    TYPE = (('Schedule',u'日程'),('Task',u'任务'))
    WARN_TYPE = (('email',u'电子邮件'),('sms',u'短信'),('rtx',u'腾讯通'))
    type = models.CharField(choices=TYPE,default=TYPE[0][0], db_index=True,max_length=10,verbose_name=u'提醒来源')
    fatherid = models.IntegerField( db_index=True,verbose_name=u'提醒来源的主键')
    warning_type = models.CharField(choices=WARN_TYPE,default=WARN_TYPE[0][0], db_index=True,max_length=10,verbose_name=u'提醒方式')
    timenum = models.IntegerField(verbose_name=u'提前提醒量',help_text=u'提前多少分钟提醒')
    time = models.DateTimeField(verbose_name=u'提醒时间', db_index=True,blank=True,null=True)
    is_repeat = models.BooleanField(default=True, db_index=True,verbose_name=u'是否计算下一次提醒',help_text=u'一次提醒后是否计算下一次提醒时间')
    is_ok = models.BooleanField(default=False, db_index=True, verbose_name=u'是否提醒过')


class UrlCheck(models.Model):
    '''
    有些通过url连接 进行操作的功能，如：邀请某个人加入的超链接，这些超链接，为了防止被仿冒，增加了校验数据库，对url 和 参数进行提前存储
    '''
    flag = models.CharField(max_length=50,verbose_name=u'唯一uuid')
    param = models.TextField(verbose_name=u'参数序列化',help_text=u'校验参数是否被仿冒')
    url = models.CharField(max_length=300,verbose_name=u'url序列化',help_text=u'校验url是否被仿冒')
    is_used = models.BooleanField(default=False,verbose_name=u'是否使用过')
    timeout = models.DateTimeField(verbose_name=u'过期时间',help_text=u'过期后不可再用',null=True,blank=True)

class RiLiMessage(models.Model):
    '''
    站内短消息
    '''
    f = models.ForeignKey(User,related_name='from_user',verbose_name=u'发起人')
    t = models.ManyToManyField(User,related_name='to_user',verbose_name=u'接收人')
    title = models.CharField(max_length=200,verbose_name=u'标题', null=True, blank=True)
    desc = models.TextField(verbose_name=u'内容', null=True, blank=True)
    createtime = models.DateTimeField(auto_created=True,verbose_name=u'创建日期')
    flag = models.BooleanField(default=True,verbose_name=u'是否草稿')
    fatherid = models.ForeignKey('RiLiMessage',verbose_name=u'父级信息')

class ReceiveMessage(models.Model):
    message = models.ForeignKey(RiLiMessage)
    user = models.ForeignKey(User,verbose_name=u'接收人')
    is_read = models.BooleanField(default=False,verbose_name=u'是否已读')