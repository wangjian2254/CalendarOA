#coding=utf-8
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Kind(models.Model):
    name = models.CharField(max_length=20,verbose_name=u'分类名称')
    father_kind = models.ForeignKey('Kind',null=True,blank=True)


class PaperKind(models.Model):
    name = models.CharField(max_length=20,verbose_name=u'分类名称')
    father_kind = models.ForeignKey('PaperKind',null=True,blank=True)


class Paper(models.Model):
    choices = ((True, u'已发布'), (False, u'未发布'))
    joinchoices = ((True, u'选定人群'), (False, u'所有人'))
    typechoices = (('paper', u'试卷'), ('toupiao', u'投票活动'))

    title = models.CharField(max_length=200,verbose_name=u'标题', help_text=u'一次投票的标题')
    content = models.TextField(verbose_name=u'内容', blank=True, null=True)
    kind = models.ForeignKey(PaperKind)

    startDate = models.DateTimeField(verbose_name=u'开始日期', blank=True, null=True, help_text=u'开始投票日期')
    endDate = models.DateTimeField(verbose_name=u'结束日期', blank=True, null=True, help_text=u'结束投票日期')

    updateDate = models.DateTimeField(verbose_name=u'生成日期', blank=True, null=True, help_text=u'一旦产生投票、考试操作，就不能修改了')

    type = models.CharField(max_length=10,default=typechoices[0],verbose_name=u'类型',help_text=u'投票、试卷标示')

    joins = models.ManyToManyField(User, blank=True, null=True, verbose_name=u'范围', help_text=u'允许操作的人员')
    is_user = models.BooleanField(choices=joinchoices,default=False,verbose_name=u'是否限定人员范围',help_text=u'是否限定特定人群投票')
    is_pub = models.BooleanField(choices=choices, default=True, verbose_name=u'是否发布', help_text=u'将投票发布出去，让用户投票')
    is_anonymous = models.BooleanField(default=False, verbose_name=u'是否匿名', help_text=u'选中为匿名投票，匿名投票无需登录')
    is_replay = models.BooleanField(default=False, verbose_name=u'是否允许评论', help_text=u'选中为匿名投票，是否开启评论功能？')

    def was_published_recently(self):
        if not self.isPub:
            return u'已经关闭'
        if self.startDate > datetime.now():
            return u'未到开始投票时间'
        elif self.startDate < datetime.now() < self.endDate:
            return u'正在投票'
        else:
            return u'投票已经关闭'

class PaperResult(models.Model):
    paper = models.ForeignKey(Paper)
    user = models.ForeignKey(User, verbose_name=u'操作人', help_text=u'参与考试的人员、非匿名投票的人')
    editDate = models.DateTimeField(verbose_name=u'时间')
    accuracy = models.FloatField(verbose_name=u'正确率',help_text=u'试卷正确率')
    result = models.TextField(blank=True, null=True, verbose_name=u'做题结果，json数据')

class Subject(models.Model):
    title = models.CharField(max_length=500, verbose_name=u'题目', help_text=u'选择题题目')
    num = models.IntegerField(default=1, verbose_name=u'可选数量', help_text=u'规定投票时选择选项的数量，多选有效')
    kinds = models.ManyToManyField(Kind,null=True,blank=True,verbose_name=u'分类',help_text=u'题目的分类,多个隶属分类')
    bz = models.CharField(max_length=500,verbose_name=u'备注',help_text=u'正确答案的解释')
    rightnum = models.IntegerField(default=0,verbose_name=u'正确次数')
    wrongnum = models.IntegerField(default=0,verbose_name=u'错误次数')
    accuracy = models.FloatField(verbose_name=u'正确率',help_text=u'总正确率')

    def __unicode__(self):
        return self.title




class Option(models.Model):
    subject = models.ForeignKey(Subject, verbose_name=u'题目', help_text=u'隶属于哪一个题目')
    content = models.CharField(max_length=500, verbose_name=u'选项内容', help_text=u'投票选项')
    is_right = models.BooleanField(default=False, verbose_name=u'正确',help_text=u'是否是正确选项')

    def __unicode__(self):
        return u'选项：%s' % (self.content,)

    class Meta():
        verbose_name = u'选项'
        verbose_name_plural = u'选项列表'


class Sheet(models.Model):
    '''
    投票结果
    '''
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'投票人', help_text=u'匿名情况，无需登录')
    dateTime = models.DateTimeField(auto_created=True, verbose_name=u'投票发生时间')
    subject = models.ForeignKey(Subject, verbose_name=u'投票的主题', help_text=u'针对哪一个主题的投票')
    options = models.ManyToManyField(Option, verbose_name=u'选项', help_text=u'可包含多选，多选时可以多头')

