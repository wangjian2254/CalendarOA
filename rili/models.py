#coding=utf-8
from django.contrib.admin.models import ADDITION
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
# Create your models here.
from django.db.models.signals import m2m_changed
from model_history.history import ModelWithHistory
from util.rtxtools import send_rtxmsg

timezone = timedelta(hours=23, minutes=59)
USERTEMPLATE = u'"%s : %s"'

REPEAT_TYPE = (('daily', u'每天的'), ('weekly', u'每周的'), ('monthly', u'每月的'), ('yearly', u'每年的'))


def rtxUrl():
    from CalendarOA.settings import APP_HOST

    return u'[日程管理查看|%s]' % APP_HOST


class Person(ModelWithHistory):
    user = models.OneToOneField(User, verbose_name=u'账户')
    telphone = models.CharField(max_length=15, db_index=True, null=True, blank=True, verbose_name=u'手机号码')
    rtxnum = models.CharField(max_length=30, db_index=True, null=True, blank=True, verbose_name=u'腾讯通账号')
    zentao_account = models.CharField(max_length=30, db_index=True, null=True, blank=True,
                                      verbose_name=u'禅道账号')
    zentao_password = models.CharField(max_length=30, db_index=True, null=True, blank=True, verbose_name=u'禅道密码')

    def __unicode__(self):
        return u'%s' % (self.user.first_name,)

    class History:
        model = True  # save model changes into admin's LogEntry table
        fields = ('user', 'telphone', 'rtxnum', 'zentao_account',
                  'zentao_password')  # save these fields history to AttributeLogEntry table

    class Meta():
        verbose_name = u'个人信息'


class Contacts(ModelWithHistory):
    user = models.OneToOneField(User, verbose_name=u'通信录隶属')
    users = models.ManyToManyField(User, related_name=u'contacts_list', verbose_name=u'通信录列表')


    def __unicode__(self):
        return u'%s' % (self.user.first_name,)

    class History:
        model = True
        fields = ('user', 'users')

        @staticmethod
        def users_change_message(users):
            return [USERTEMPLATE % (u.first_name, u.username) for u in users]

    class Meta():
        verbose_name = u'通信录'


class Group(ModelWithHistory):
    '''
    日程分组
    '''
    name = models.CharField(max_length=30, verbose_name=u'分组名称')
    flag = models.CharField(max_length=10, verbose_name=u'标示', help_text=u'default :默认分组，custom: 用户自建，system:系统自建')
    color = models.IntegerField(verbose_name=u'html颜色值')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    users = models.ManyToManyField(User, related_name=u'group_sharedusers', verbose_name=u'分享用户')
    observers = models.ManyToManyField(User, related_name=u'group_sharedobservers', verbose_name=u'观察者用户',
                                       help_text=u'只能看到不能编辑')

    def __unicode__(self):
        return u'%s' % (self.name,)

    class History:
        model = True
        fields = ('name', 'color', 'author', 'users', 'observers')

        @staticmethod
        def users_change_message(users):
            return [USERTEMPLATE % (u.first_name, u.username) for u in users]

        @staticmethod
        def observers_change_message(users):
            return [USERTEMPLATE % (u.first_name, u.username) for u in users]

    class Meta():
        verbose_name = u'日程分组'


class Schedule(ModelWithHistory):
    '''
    日程
    '''

    title = models.CharField(max_length=200, verbose_name=u'日程名称')
    desc = models.CharField(max_length=4000, verbose_name=u'备注')
    startdate = models.DateTimeField(default=datetime.now, db_index=True, verbose_name=u'开始日期',
                                     help_text=u'如果每年重复，开始日期，就是重复的日子')
    enddate = models.DateTimeField(default=datetime.now, db_index=True, null=True, blank=True, verbose_name=u'结束日期',
                                   help_text=u'为空，则永远重复')
    is_all_day = models.BooleanField(default=False, verbose_name=u'是否全天任务', help_text=u'全天任务不需要不需要开始时间')
    time_start = models.TimeField(verbose_name=u'开始时间', null=True, blank=True)
    time_end = models.TimeField(verbose_name=u'结束时间', null=True, blank=True)
    repeat_type = models.CharField(choices=REPEAT_TYPE, default=REPEAT_TYPE[0][0], max_length=10, verbose_name=u'重复方式')
    repeat_date = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True, verbose_name=u'重复时间',
                                                    help_text=u'这是一个逗号分隔的数字字符串，如：‘1,2,3’,如果重复方式为周，数字代表星期数 星期一：0，星期日：6，如果重复方式为月，数字代表日子，1号：1,31号：31')
    color = models.IntegerField(verbose_name=u'html颜色值', help_text=u'颜色不同可以区分缓急，可以作为日程的小分组')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    users = models.ManyToManyField(User, related_name=u'schedule_sharedusers', verbose_name=u'参与用户')
    group = models.ForeignKey(Group, verbose_name=u'隶属分组')
    warning_type = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True, verbose_name=u'提醒类型',
                                                     help_text=u'方式，方式依次排列')
    warning_time = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True, verbose_name=u'提醒时间',
                                                     help_text=u'时间，时间依次排列')

    lastUpdateTime = models.DateTimeField(verbose_name=u'最后修改时间', null=True, blank=True)
    flag = models.CharField(max_length=10, verbose_name=u'禅道类型', null=True, blank=True, help_text=u'任务、需求、bug')
    flagid = models.IntegerField(verbose_name=u'禅道id', null=True, blank=True, help_text=u'主键')

    def __unicode__(self):
        return u'%s' % (self.title,)

    class History:
        model = True
        fields = (
            'title', 'desc', 'startdate', 'enddate', 'is_all_day', 'time_start', 'time_end', 'repeat_type',
            'repeat_date', 'color', 'author', 'users', 'group', 'warning_type', 'warning_time')

        @staticmethod
        def users_change_message(users):
            return [USERTEMPLATE % (u.first_name, u.username) for u in users]

        @staticmethod
        def time_start_change_message(instence, name, oldvalue, value):
            if oldvalue[name][-8:] == value[name][-8:]:
                return None, None
            else:
                return oldvalue[name], value[name]

        @staticmethod
        def time_end_change_message(instence, name, oldvalue, value):
            if oldvalue[name][-8:] == value[name][-8:]:
                return None, None
            else:
                return oldvalue[name], value[name]
        @staticmethod
        def startdate_change_message(instence, name, oldvalue, value):
            o = u''
            v = u''
            if oldvalue[name]:
                o = oldvalue[name][:-9]
            if value[name]:
                v = value[name][:-9]
            return o,v

        @staticmethod
        def enddate_change_message(instence, name, oldvalue, value):
            if instence._history_action == ADDITION:
                o = u''
            else:
                o = u'永远'
            v = u'永远'
            if oldvalue[name]:
                o = oldvalue[name][:-9]
            if value[name]:
                v = value[name][:-9]
            return o,v

        @staticmethod
        def color_change_message(instence, name, oldvalue, value):
            o=''
            v=''
            if oldvalue[name]:
                o = u'#06x'%int(oldvalue[name])
            if value[name]:
                v = u'#06x'%int(value[name])
            return o,v

        @staticmethod
        def repeat_type_change_message(instence, name, oldvalue, value):
            o=''
            for code, n in REPEAT_TYPE:
                if oldvalue[name] == code:
                    o = n
                if value[name] == code:
                    v = n
            return o, v

        @staticmethod
        def warning_type_change_message(instenct, name, oldvalue, value):
            o = []
            v = []
            if oldvalue[name]:
                for t in oldvalue[name].split(','):
                    if t=='rtx':
                        o.append(u'腾讯通')
                    elif t=='email':
                        o.append(u'电子邮件')
                    elif t == 'sms':
                        o.append(u'手机短信')

            if value[name]:
                for t in value[name].split(','):
                    if t=='rtx':
                        v.append(u'腾讯通')
                    elif t=='email':
                        v.append(u'电子邮件')
                    elif t == 'sms':
                        v.append(u'手机短信')
            return u'、'.join(o),u'、'.join(v)

        @staticmethod
        def warning_time_change_message(instence, name, oldvalue, value):
            ov = []
            for mins in oldvalue[name].split(','):
                if not mins:
                    continue
                mins = int(mins)
                if oldvalue['is_all_day'] == 'True':

                    d = 0 - divmod(mins, 24 * 60.0)[0]
                    h, m = divmod(divmod(mins + d * 24 * 60, 24 * 60)[1], 60.0)
                    # m = divmod(mins+d*24*60,60)[1]
                    if d > 0:
                        o = u'提前%d天,%02d:%02d' % (d, h, m)
                    else:
                        o = u'%02d:%02d' % (h, m)
                else:
                    if divmod(mins, 7 * 24 * 60)[1] == 0:
                        o = u'提前%d周' % divmod(mins, 7 * 24 * 60)[0]
                    elif divmod(mins, 24 * 60)[1] == 0:
                        o = u'提前%d天' % divmod(mins, 24 * 60)[0]
                    elif divmod(mins, 60)[1] == 0:
                        o = u'提前%d小时' % divmod(mins, 60)[0]
                    else:
                        o = u'提前%d分钟' % divmod(mins, 60)[1]
                ov.append(o)

            vv = []
            for mins in value[name].split(','):
                if not mins:
                    continue
                mins = int(mins)
                if instence.is_all_day:
                    d = 0 - divmod(mins, 24 * 60.0)[0]
                    h, m = divmod(divmod(mins + d * 24 * 60, 24 * 60)[1], 60.0)
                    # m = divmod(mins+d*24*60,60)[1]
                    if d > 0:
                        v = u'提前%d天,%02d:%02d' % (d, h, m)
                    else:
                        v = u'%02d:%02d' % (h, m)
                else:
                    if divmod(mins, 7 * 24 * 60)[1] == 0:
                        v = u'提前%d周' % divmod(mins, 7 * 24 * 60)[0]
                    elif divmod(mins, 24 * 60)[1] == 0:
                        v = u'提前%d天' % divmod(mins, 24 * 60)[0]
                    elif divmod(mins, 60)[1] == 0:
                        v = u'提前%d小时' % divmod(mins, 60)[0]
                    else:
                        v = u'提前%d分钟' % divmod(mins, 60)[1]
                vv.append(v)
            return u'、'.join(ov), u'、'.join(vv)

        @staticmethod
        def is_all_day_change_message(instence, name, oldvalue, value):

            if oldvalue[name] == 'True':
                o = u'全天'
            else:
                o = u'非全天'
            if value[name] == 'True':
                v = u'全天'
            else:
                v = u'非全天'
            return o, v


    class Meta():
        unique_together = [('flag', 'flagid')]
        verbose_name = u'日程'

    def adjustWarning(self):
        from rili.warningtools import adjustRiLiWarning

        for w in self.warning_time.split(','):
            if w:
                rw = RiLiWarning()
                rw.fatherid = self.pk
                rw.type = 'Schedule'
                rw.timenum = int(w)
                rw.is_repeat = True
                rw.is_ok = True
                rw.save()
        adjustRiLiWarning(self.pk, 'Schedule')

    def save(self, *args, **kwargs):
        if kwargs.has_key('lastUpdateTime'):
            self.lastUpdateTime = kwargs['lastUpdateTime']
            del kwargs['lastUpdateTime']
        else:
            self.lastUpdateTime = datetime.now()
        if self.enddate and hasattr(self.enddate, 'hour') and getattr(self.enddate, 'hour', 0) == 0:
            self.enddate += timezone
        RiLiWarning.objects.filter(type='Schedule', fatherid=self.pk).delete()
        super(Schedule, self).save(*args, **kwargs)
        if self.warning_time and self.warning_type:
            self.adjustWarning()


    def delete(self, *args, **kwargs):
        super(Schedule, self).delete(*args, **kwargs)
        RiLiWarning.objects.filter(type='Schedule', fatherid=self.pk).delete()

    def getZentaoUrl(self):
        if self.flag and self.flagid:
            from CalendarOA.settings import ZENTAO_HOST

            if self.flag == 'Task':
                return '%s/index.php?m=task&f=view&taskID=%s' % (ZENTAO_HOST, self.flagid)
            if self.flag == 'Bug':
                return '%s/index.php?m=bug&f=view&bugID=%s' % (ZENTAO_HOST, self.flagid)

        return None

    def getRTXUrl(self):
        u = u''
        if self.flag and self.flagid:
            u = u'  [禅道查看|%s]' % self.getZentaoUrl()

        return u'%s  %s' % ( rtxUrl(), u)

    def sendRTX(self, rtxnum):
        if rtxnum:
            send_rtxmsg(rtxnum, (u'%s\n%s' % (self.desc, self.getRTXUrl())), self.title)


class Task(ModelWithHistory):
    '''
    任务
    '''
    title = models.CharField(max_length=200, verbose_name=u'任务名称')
    desc = models.CharField(max_length=4000, verbose_name=u'备注')
    startdate = models.DateTimeField(default=datetime.now, db_index=True, verbose_name=u'创建日期')
    enddate = models.DateTimeField(default=datetime.now, db_index=True, null=True, blank=True, verbose_name=u'截止日期')
    status = models.BooleanField(default=False, db_index=True, verbose_name=u'完成状态')
    color = models.IntegerField(verbose_name=u'html颜色值', help_text=u'颜色不同可以区分缓急，可以作为日程的小分组')
    author = models.ForeignKey(User, verbose_name=u'创建者')
    warning_type = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True, verbose_name=u'提醒类型',
                                                     help_text=u'方式，方式依次排列')
    warning_time = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True, verbose_name=u'提醒时间',
                                                     help_text=u'时间，时间依次排列')

    lastUpdateTime = models.DateTimeField(verbose_name=u'最后修改时间', null=True, blank=True)
    flag = models.CharField(max_length=10, verbose_name=u'禅道类型', null=True, blank=True, help_text=u'任务、需求、bug')
    flagid = models.IntegerField(verbose_name=u'禅道id', null=True, blank=True, help_text=u'主键')

    def __unicode__(self):
        return u'%s' % (self.title,)

    class History:
        model = True
        fields = (
            'title', 'desc', 'startdate', 'enddate', 'status',
            'color', 'author', 'warning_type', 'warning_time')



        @staticmethod
        def startdate_change_message(instence, name, oldvalue, value):
            o = u''
            v = u''
            if oldvalue[name]:
                o = oldvalue[name][:-9]
            if value[name]:
                v = value[name][:-9]
            return o,v

        @staticmethod
        def enddate_change_message(instence, name, oldvalue, value):
            if instence._history_action == ADDITION:
                o = u''
            else:
                o = u'永远'
            v = u'永远'
            if oldvalue[name]:
                o = oldvalue[name][:-9]
            if value[name]:
                v = value[name][:-9]
            return o,v

        @staticmethod
        def status_change_message(instence, name, oldvalue, value):

            if oldvalue[name] == 'True':
                o = u'完成'
            else:
                o = u'未完成'
            if value[name] == 'True':
                v = u'完成'
            else:
                v = u'未完成'
            return o, v

        @staticmethod
        def color_change_message(instence, name, oldvalue, value):
            o=''
            v=''
            if oldvalue[name]:
                o = u'#06x'%int(oldvalue[name])
            if value[name]:
                v = u'#06x'%int(value[name])
            return o,v



        @staticmethod
        def warning_type_change_message(instenct, name, oldvalue, value):
            o = []
            v = []
            if oldvalue[name]:
                for t in oldvalue[name].split(','):
                    if t=='rtx':
                        o.append(u'腾讯通')
                    elif t=='email':
                        o.append(u'电子邮件')
                    elif t == 'sms':
                        o.append(u'手机短信')

            if value[name]:
                for t in value[name].split(','):
                    if t=='rtx':
                        v.append(u'腾讯通')
                    elif t=='email':
                        v.append(u'电子邮件')
                    elif t == 'sms':
                        v.append(u'手机短信')
            return u'、'.join(o),u'、'.join(v)

        @staticmethod
        def warning_time_change_message(instence, name, oldvalue, value):
            ov = []
            for mins in oldvalue[name].split(','):
                if not mins:
                    continue
                mins = int(mins)
                if oldvalue['is_all_day'] == 'True':

                    d = 0 - divmod(mins, 24 * 60.0)[0]
                    h, m = divmod(divmod(mins + d * 24 * 60, 24 * 60)[1], 60.0)
                    # m = divmod(mins+d*24*60,60)[1]
                    if d > 0:
                        o = u'提前%d天,%02d:%02d' % (d, h, m)
                    else:
                        o = u'%02d:%02d' % (h, m)
                else:
                    if divmod(mins, 7 * 24 * 60)[1] == 0:
                        o = u'提前%d周' % divmod(mins, 7 * 24 * 60)[0]
                    elif divmod(mins, 24 * 60)[1] == 0:
                        o = u'提前%d天' % divmod(mins, 24 * 60)[0]
                    elif divmod(mins, 60)[1] == 0:
                        o = u'提前%d小时' % divmod(mins, 60)[0]
                    else:
                        o = u'提前%d分钟' % divmod(mins, 60)[1]
                ov.append(o)

            vv = []
            for mins in value[name].split(','):
                if not mins:
                    continue
                mins = int(mins)
                if instence.is_all_day:
                    d = 0 - divmod(mins, 24 * 60.0)[0]
                    h, m = divmod(divmod(mins + d * 24 * 60, 24 * 60)[1], 60.0)
                    # m = divmod(mins+d*24*60,60)[1]
                    if d > 0:
                        v = u'提前%d天,%02d:%02d' % (d, h, m)
                    else:
                        v = u'%02d:%02d' % (h, m)
                else:
                    if divmod(mins, 7 * 24 * 60)[1] == 0:
                        v = u'提前%d周' % divmod(mins, 7 * 24 * 60)[0]
                    elif divmod(mins, 24 * 60)[1] == 0:
                        v = u'提前%d天' % divmod(mins, 24 * 60)[0]
                    elif divmod(mins, 60)[1] == 0:
                        v = u'提前%d小时' % divmod(mins, 60)[0]
                    else:
                        v = u'提前%d分钟' % divmod(mins, 60)[1]
                vv.append(v)
            return u'、'.join(ov), u'、'.join(vv)


    class Meta():
        unique_together = [('flag', 'flagid')]
        verbose_name = u'任务'

    def adjustWarning(self):
        from rili.warningtools import adjustRiLiWarning

        for w in self.warning_time.split(','):
            if w:
                rw = RiLiWarning()
                rw.fatherid = self.pk
                rw.type = 'Task'
                rw.timenum = int(w)
                rw.is_repeat = True
                rw.is_ok = True
                rw.save()
        adjustRiLiWarning(self.pk, 'Task')

    def save(self, *args, **kwargs):
        if kwargs.has_key('lastUpdateTime'):
            self.lastUpdateTime = kwargs['lastUpdateTime']
            del kwargs['lastUpdateTime']
        else:
            self.lastUpdateTime = datetime.now()
        if self.enddate and hasattr(self.enddate, 'hour') and getattr(self.enddate, 'hour', 0) == 0:
            self.enddate += timezone
        super(Task, self).save(*args, **kwargs)
        if self.warning_time and self.warning_type:
            self.adjustWarning()

    def delete(self, *args, **kwargs):
        super(Task, self).delete(*args, **kwargs)
        RiLiWarning.objects.filter(type='Task', fatherid=self.pk).delete()

    def getRTXUrl(self):
        u = u''
        if self.flag and self.flagid:
            u = u'  [禅道查看|%s]' % self.getZentaoUrl()

        return u'%s  %s' % ( rtxUrl(), u)

    def getZentaoUrl(self):
        if self.flag and self.flagid:
            from CalendarOA.settings import ZENTAO_HOST

            if self.flag == 'Task':
                return '%s/index.php?m=task&f=view&taskID=%s' % (ZENTAO_HOST, self.flagid)
            if self.flag == 'Bug':
                return '%s/index.php?m=bug&f=view&bugID=%s' % (ZENTAO_HOST, self.flagid)
        return None

    def sendRTX(self, rtxnum):
        if rtxnum:
            send_rtxmsg(rtxnum, (u'%s\n%s' % (self.desc, self.getRTXUrl())), self.title)


class RiLiWarning(ModelWithHistory):
    '''
    提醒，为日程或任务 创建的提醒
    '''
    TYPE = (('Schedule', u'日程'), ('Task', u'任务'))
    WARN_TYPE = (('email', u'电子邮件'), ('sms', u'短信'), ('rtx', u'腾讯通'))
    type = models.CharField(choices=TYPE, default=TYPE[0][0], db_index=True, max_length=10, verbose_name=u'提醒来源')
    fatherid = models.IntegerField(db_index=True, verbose_name=u'提醒来源的主键')
    timenum = models.IntegerField(verbose_name=u'提前提醒量', help_text=u'提前多少分钟提醒')
    time = models.DateTimeField(verbose_name=u'提醒时间', db_index=True, blank=True, null=True)
    is_repeat = models.BooleanField(default=True, db_index=True, verbose_name=u'是否计算下一次提醒',
                                    help_text=u'一次提醒后是否计算下一次提醒时间')
    is_ok = models.BooleanField(default=False, db_index=True, verbose_name=u'是否提醒过')


class UrlCheck(ModelWithHistory):
    '''
    有些通过url连接 进行操作的功能，如：邀请某个人加入的超链接，这些超链接，为了防止被仿冒，增加了校验数据库，对url 和 参数进行提前存储
    '''
    flag = models.CharField(max_length=50, verbose_name=u'唯一uuid')
    param = models.TextField(verbose_name=u'参数序列化', help_text=u'校验参数是否被仿冒')
    url = models.CharField(max_length=300, verbose_name=u'url序列化', help_text=u'校验url是否被仿冒')
    is_used = models.BooleanField(default=False, verbose_name=u'是否使用过')
    timeout = models.DateTimeField(verbose_name=u'过期时间', help_text=u'过期后不可再用', null=True, blank=True)

