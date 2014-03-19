#coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
# Create your models here.

REPEAT_TYPE=(('daily',u'每天的'),('weekly',u'每周的'),('monthly',u'每月的'),('yearly',u'每年的'))

class Group(models.Model):
    '''
    日程分组
    '''
    name = models.CharField(max_length=30, verbose_name=u'分组名称')
    color = models.CharField(max_length=10,verbose_name=u'html颜色值')
    author = models.ForeignKey(User,verbose_name=u'创建者')
    users = models.ManyToManyField(User,related_name=u'sharedusers', verbose_name=u'分享用户')

class Schedule(models.Model):
    '''
    日程
    '''


    title = models.CharField(max_length=200,verbose_name=u'日程名称')
    desc = models.CharField(max_length=4000,verbose_name=u'备注')
    startdate = models.DateField(default=datetime.now,verbose_name=u'开始日期')
    enddate = models.DateField(default=datetime.now, null=True, blank=True, verbose_name=u'结束日期',help_text=u'为空，则永远重复')
    is_all_day = models.BooleanField(default=False,verbose_name=u'是否全天任务')
    repeat_type = models.CharField(choices=REPEAT_TYPE,max_length=10,verbose_name=u'重复方式')



class Task(models.Model):
    '''
    任务
    '''
    pass