#coding=utf-8
#经过最终思考，考试和投票 还是 在数据库上区分开来。1. 方便全局日志记录 2. 结构清晰方便扩展
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Kind(models.Model):
    '''
    试题的分类，可以理解为标签
    '''
    name = models.CharField(max_length=20,verbose_name=u'分类名称')
    father_kind = models.ForeignKey('Kind',null=True,blank=True)

    def __unicode__(self):
        return self.name

    class History:
        model = True
        fields = ('name', 'father_kind')  # save these fields history to AttributeLogEntry table

    class Meta():
        verbose_name = u'试题分类'


class PaperKind(models.Model):
    '''
    试卷的分类，可以理解为标签
    '''
    name = models.CharField(max_length=20,verbose_name=u'分类名称')
    father_kind = models.ForeignKey('PaperKind',null=True,blank=True)

    def __unicode__(self):
        return self.name

    class History:
        model = True
        fields = ('name', 'father_kind')  # save these fields history to AttributeLogEntry table

    class Meta():
        verbose_name = u'考卷分类'


class Paper(models.Model):
    '''
    试卷，可以指定考试人员范围也可以不指定
    '''
    choices = ((True, u'已发布'), (False, u'未发布'))
    joinchoices = ((True, u'选定人群'), (False, u'所有人'))

    title = models.CharField(max_length=200,verbose_name=u'标题', help_text=u'考卷名字')
    content = models.TextField(verbose_name=u'内容', help_text=u'考卷描述', blank=True, null=True)
    kinds = models.ManyToManyField(PaperKind,null=True,blank=True,verbose_name=u'分类',help_text=u'考卷的分类,多个隶属分类')
    subjects = models.ManyToManyField("Subject",null=True,blank=True,verbose_name=u'试题')

    startDate = models.DateTimeField(verbose_name=u'开始日期', blank=True, null=True, help_text=u'考卷有效日期起')
    endDate = models.DateTimeField(verbose_name=u'结束日期', blank=True, null=True, help_text=u'考卷有效日期止')

    joins = models.ManyToManyField(User, blank=True, null=True, verbose_name=u'范围', help_text=u'指定的答卷人员')
    is_user = models.BooleanField(choices=joinchoices,default=False,verbose_name=u'是否限定人员范围',help_text=u'是否限定特定人群，必考')
    is_pub = models.BooleanField(choices=choices, default=True, verbose_name=u'是否发布', help_text=u'发布后不可修改')
    is_replay = models.BooleanField(default=False, verbose_name=u'是否允许评论', help_text=u'是否开启评论功能？考完的人可以评论试卷')

    def was_published_recently(self):
        if not self.is_pub:
            return u'已经关闭',False
        if self.startDate > datetime.now():
            return u'未到开始投票时间',False
        elif self.startDate < datetime.now() < self.endDate:
            return u'正在投票',True
        else:
            return u'考试已经结束',False


    def __unicode__(self):
        return self.title

    class History:
        model = True
        fields = ('title', 'content','kinds','subjects','startDate','endDate','joins','is_user','is_pub','is_replay')

    class Meta():
        verbose_name = u'试卷'

class PaperResult(models.Model):
    '''
    人员考试的答题结果
    '''
    paper = models.ForeignKey(Paper)
    user = models.ForeignKey(User, verbose_name=u'操作人', help_text=u'参与考试的人员')
    editDate = models.DateTimeField(verbose_name=u'答卷时间')
    accuracy = models.FloatField(default=0.0, verbose_name=u'正确率',help_text=u'试卷正确率')
    result = models.TextField(blank=True, null=True, verbose_name=u'做题结果，json数据')

    def __unicode__(self):
        return u'%s 答题: %s'%(self.user.first_name,self.paper.title)

    class History:
        model = True
        fields = ('paper', 'user','editDate','accuracy')

    class Meta():
        verbose_name = u'答题'

class Subject(models.Model):
    '''
    试题信息，有记录正确次数和错误次数，方便计算试题的正确率，未来可以衡量难度
    '''
    title = models.CharField(max_length=500, verbose_name=u'题目', help_text=u'选择题题目')
    kinds = models.ManyToManyField(Kind,null=True,blank=True,verbose_name=u'分类',help_text=u'题目的分类,多个隶属分类')
    bz = models.CharField(max_length=500,verbose_name=u'备注',help_text=u'正确答案的解释')
    rightnum = models.IntegerField(default=0,verbose_name=u'正确次数')
    wrongnum = models.IntegerField(default=0,verbose_name=u'错误次数')
    accuracy = models.FloatField(verbose_name=u'正确率',help_text=u'总正确率')

    def __unicode__(self):
        return self.title


    class History:
        model = True
        fields = ('title', 'num','kinds','bz')

    class Meta():
        verbose_name = u'题目'




class Option(models.Model):
    '''
    试题的选项
    '''
    subject = models.ForeignKey(Subject, verbose_name=u'题目', help_text=u'隶属于哪一个题目')
    content = models.CharField(max_length=500, verbose_name=u'选项内容', help_text=u'投票选项')
    is_right = models.BooleanField(default=False, verbose_name=u'正确',help_text=u'是否是正确选项')

    def __unicode__(self):
        return self.content

    class Meta():
        verbose_name = u'选项'
        verbose_name_plural = u'选项列表'

    def __unicode__(self):
        return self.title


    class History:
        model = True
        fields = ('subject', 'content','is_right')


#
# class Sheet(models.Model):
#     '''
#     投票结果
#     '''
#     user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'投票人', help_text=u'匿名情况，无需登录')
#     dateTime = models.DateTimeField(auto_created=True, verbose_name=u'投票发生时间')
#     subject = models.ForeignKey(Subject, verbose_name=u'投票的主题', help_text=u'针对哪一个主题的投票')
#     options = models.ManyToManyField(Option, verbose_name=u'选项', help_text=u'可包含多选，多选时可以多头')

