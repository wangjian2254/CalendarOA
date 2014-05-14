#coding=utf-8
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Subject(models.Model):
    choices = ((True, u'已发布'), (False, u'未发布'))
    joinchoices = ((True, u'选定人群'), (False, u'所有人'))

    title = models.CharField(max_length=500, verbose_name=u'标题', help_text=u'投票的标题')
    content = models.TextField(verbose_name=u'内容', blank=True, null=True)
    single = models.BooleanField(default=True, verbose_name=u'是否单选', help_text=u'选中为单选')
    num = models.IntegerField(default=1, verbose_name=u'可选数量', help_text=u'规定投票时选择选项的数量，多选有效')
    startDate = models.DateTimeField(verbose_name=u'开始日期', help_text=u'开始投票日期')
    endDate = models.DateTimeField(verbose_name=u'结束日期', help_text=u'结束投票日期')

    joins = models.ManyToManyField(User, blank=True, null=True, verbose_name=u'投票范围', help_text=u'允许投票的人员')
    isUser = models.BooleanField(choices=joinchoices,default=False,verbose_name=u'是否限定投票范围',help_text=u'是否限定特定人群投票')
    isPub = models.BooleanField(choices=choices, default=True, verbose_name=u'是否发布投票', help_text=u'将投票发布出去，让用户投票')
    isNoName = models.BooleanField(default=False, verbose_name=u'是否匿名', help_text=u'选中为匿名投票，匿名投票无需登录')
    isReplay = models.BooleanField(default=False, verbose_name=u'是否允许评论', help_text=u'选中为匿名投票，是否开启评论功能？')

    def __unicode__(self):
        return self.title

    class Meta():
        verbose_name = u'投票'
        verbose_name_plural = u'投票列表'

    def was_published_recently(self):
        if not self.isPub:
            return u'已经关闭'
        if self.startDate > datetime.now():
            return u'未到开始投票时间'
        elif self.startDate < datetime.now() < self.endDate:
            return u'正在投票'
        else:
            return u'投票已经关闭'

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.short_description = u'投票状态'

    date_hierarchy = 'endDate'


class Option(models.Model):
    subject = models.ForeignKey(Subject, verbose_name=u'主题', help_text=u'隶属于哪一个投票')
    content = models.CharField(max_length=500, verbose_name=u'选项内容', help_text=u'投票选项')

    def __unicode__(self):
        return u'选项：%s' % (self.content,)

    class Meta():
        verbose_name = u'选项'
        verbose_name_plural = u'选项列表'


class Toupiao(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'投票人', help_text=u'匿名情况，无需登录')
    dateTime = models.DateTimeField(auto_created=True, verbose_name=u'投票发生时间')
    subject = models.ForeignKey(Subject, verbose_name=u'投票的主题', help_text=u'针对哪一个主题的投票')
    options = models.ManyToManyField(Option, verbose_name=u'选项', help_text=u'可包含多选，多选时可以多头')

