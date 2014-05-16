#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.models import User
from django.contrib.auth import models as django_user
__author__ = u'王健'

from django.db.models import signals

def addGuestUser(**kwargs):
    if User.objects.filter(username='guest').count()==0:
        u=User()
        u.username = 'guest'
        u.first_name = u'系统'
        u.set_password('')
        u.is_active=False
        u.is_superuser=False
        u.is_staff=False
        u.save()


signals.post_syncdb.connect(addGuestUser,sender=django_user,dispatch_uid='model_history.create_systemuser')