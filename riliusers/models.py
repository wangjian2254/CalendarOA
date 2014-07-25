# coding=utf-8
# Date:2014/7/25
# Email:wangjian2254@gmail.com
from time import timezone
import warnings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, SiteProfileNotAvailable
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.db import models
from django.utils.translation import ugettext_lazy as _
from CalendarOA import settings
from model_history.history import ModelWithHistory
from riliusers.threadlocalsperson import get_current_org

__author__ = u'王健'


class LiYuUser(AbstractBaseUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """

    email = models.EmailField(_('email address'), unique=True, blank=True, verbose_name=u'账号', help_text=u'电子邮箱就是账号')
    email_active = models.BooleanField(default=False, verbose_name=u'邮箱是否激活')
    tel = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=30, blank=True)
    icon = models.ImageField(blank=True, verbose_name=u'默认头像')
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = BaseUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return unicode(self.email)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        warnings.warn("The use of AUTH_PROFILE_MODULE to define user profiles has been deprecated.",
                      DeprecationWarning, stacklevel=2)
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings

            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable(
                    'You need to set AUTH_PROFILE_MODULE in your project '
                    'settings')
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
            except ValueError:
                raise SiteProfileNotAvailable(
                    'app_label and model_name should be separated by a dot in '
                    'the AUTH_PROFILE_MODULE setting')
            try:
                model = models.get_model(app_label, model_name)
                if model is None:
                    raise SiteProfileNotAvailable(
                        'Unable to load the profile model, check '
                        'AUTH_PROFILE_MODULE in your project settings')
                self._profile_cache = model._default_manager.using(
                    self._state.db).get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache


class OtherWebsiteUserInfo(models.Model):
    name = models.CharField(max_length=20, verbose_name=u'第三方网站名称')
    flag = models.CharField(max_length=10, verbose_name=u'第三方网站标记')


class BandInfo(ModelWithHistory):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'账户')
    webinfo = models.ForeignKey(OtherWebsiteUserInfo, verbose_name=u'第三方关联网站', help_text=u'第三方关联的网站')
    web_username = models.CharField(max_length=100, verbose_name=u'第三方网站账号')
    data = models.CharField(max_length=300, verbose_name=u'第三方网站授权信息', help_text=u'json数据')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=u'截止日期', help_text=u'授权截止日期')

    def __unicode__(self):
        return unicode(self.user)

    class History:
        model = True
        fields = ('user', 'webinfo', 'web_username', 'end_date')

    class Meta():
        verbose_name = u'第三方网站授权'


class Industry(models.Model):
    name = models.CharField(max_length=20,verbose_name=u'行业')

class Organization(ModelWithHistory):
    name = models.CharField(max_length=200, blank=True,  verbose_name=u'组织简称', help_text=u'公司或者组织的名称')
    total_name = models.CharField(max_length=200, blank=True,  verbose_name=u'组织全称', help_text=u'公司或者组织的名称')
    flag = models.CharField(max_length=50, blank=True, unique=True,  verbose_name=u'邀请码', help_text=u'邀请其他用户加入本组织')
    icon = models.ImageField(verbose_name=u'头像', blank=True, help_text=u'组织头像')
    type = models.IntegerField(default=1, verbose_name=u'组织类型', help_text=u'1:免费 2：付费 ')
    industry = models.ForeignKey(Industry, blank=True, verbose_name=u'行业类型', help_text=u'行业类型 ')
    free_balance = models.IntegerField(default=0, verbose_name=u'免费可使用额度', help_text=u'网站活动中赠送的')
    balance = models.IntegerField(default=0, verbose_name=u'可使用额度', help_text=u'用户余额')
    managers = models.ManyToManyField('Person', related_name='org_managers', verbose_name=u'组织管理员')
    is_active = models.BooleanField(default=True,verbose_name=u'是否可用')
    update_timeline = models.IntegerField(default=0,verbose_name=u'组织资料修改时间线')
    def __unicode__(self):
        return unicode(self.totalName)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_name = self.name
            self.is_active = True
            self.update_timeline = 0
            import uuid
            self.flag = str(uuid.uuid4())
        self.update_timeline+=1
        super(Organization, self).save(*args, **kwargs)

    def updatetimeline(self):
        self.save(update_fields=['update_timeline'])

    class History:
        model = True
        fields = ('name', 'total_name', 'icon', 'managers')

    class Meta():
        verbose_name = u'组织或公司信息'


class Person(ModelWithHistory):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=u'账户')
    org = models.ForeignKey(Organization, verbose_name=u'隶属组织', help_text=u'隶属组织或公司')
    name = models.CharField(max_length=10, verbose_name=u'名字', help_text=u'组织内名称')
    is_active = models.BooleanField(default=True, verbose_name=u'是否在职')
    last_join = models.DateTimeField(verbose_name=u'最后一次登录', blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
        self.org.updatetimeline()

    class History:
        model = True
        fields = ('user', 'name', 'is_active', 'last_join')

    class Meta():
        unique_together = [('user', 'org')]
        verbose_name = u'个人信息'


class Department(ModelWithHistory):
    name = models.CharField(max_length=20, verbose_name=u'部门名称', help_text=u'部门名称')
    icon = models.ImageField(verbose_name=u'部门头像', blank=True, help_text=u'部门的头像')
    managers = models.ManyToManyField(Person, related_name='dep_managers', verbose_name=u'负责人',
                                      help_text=u'部门负责人,有权任免其他人和有权任免子部门')
    members = models.ManyToManyField(Person, related_name='dep_members', verbose_name=u'成员', help_text=u'部门成员')
    father = models.ForeignKey('Department', blank=True, null=True, verbose_name=u'父级部门')
    flag = models.CharField(default='custom', verbose_name=u'分组标签', help_text=u'组织中必须存在的分组（根组（root）、未分组（free）），所有新加入的、无隶属的人或项目都归属未分组')
    org = models.ForeignKey(Organization, verbose_name=u'隶属组织', help_text=u'隶属组织或公司')

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        if not self.pk and not self.org:
            self.org = get_current_org()
        super(Department, self).save(*args, **kwargs)
        self.org.updatetimeline()

    class History:
        model = True
        fields = ('name', 'members', 'icon', 'father', 'managers')

    class Meta():
        verbose_name = u'部门信息'


class Contacts(ModelWithHistory):
    user = models.OneToOneField(Person, verbose_name=u'通信录隶属')
    users = models.ManyToManyField(Person, related_name=u'contacts_list', verbose_name=u'常用联系人列表')


    def __unicode__(self):
        return unicode(self.user)

    class History:
        model = True
        fields = ('user', 'users')

        @staticmethod
        def users_change_message(users):
            return [u.first_name for u in users]

    class Meta():
        verbose_name = u'常用联系人'



