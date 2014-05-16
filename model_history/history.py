#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'
from django.contrib.auth.models import User

import threadlocals
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION
from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.db import models
from django.contrib.admin.models import DELETION
from django.db.models import signals
from django.db.models.base import ModelBase
import datetime

def prepare_fields(instance):
    output = {}
    class_fields = instance.__class__._meta.fields
    instance._history_fields = {}
    all = dict([(f.name, f) for f in class_fields])
    for field_name in instance._history['fields']:
        if all.has_key(field_name):
            modelfield = all[field_name]
            value = getattr(instance, modelfield.attname)
            if value is None: value = ''
            output[field_name] = unicode(value)
    return output

def add_signals(cls):
    def post_delete(instance, **_kwargs):
        if instance._history.get('model', False):
            instance._create_log_entry(DELETION)

    def pre_save(instance, **_kwargs):
        if instance._history.get('fields', []):
            if instance.pk is None:
                instance._history_fields = {}
                for field_name in instance._history['fields']:
                    instance._history_fields[field_name] = ''
            else:
                try:
                    db_instance = instance.__class__.objects.get(pk=instance.pk)
                except instance.__class__.DoesNotExist:
                    db_instance = instance
                instance._history_fields = prepare_fields(db_instance)
        if instance._history.get('model', False):
            if instance.pk == None:
                instance._history_action = ADDITION
            else:
                instance._history_action = CHANGE

    def post_save(instance, **_kwargs):
        if instance._history.get('fields', []):
            pre_fields = instance._history_fields
            post_fields = prepare_fields(instance)
            for name, after in post_fields.iteritems():
                #print 'looking if', name, 'changed...'
                before = pre_fields[name]
                if before != after:
                    # field has been changed
                    #print 'changed', name, 'from', before, 'to', after
                    instance._create_field_log_entry(name, after)
            #print 'checking done.'

        if instance._history.get('model', False):
            instance._create_log_entry(instance._history_action)

    signals.pre_save.connect(pre_save, sender=cls, weak=False)
    signals.post_save.connect(post_save, sender=cls, weak=False)
    signals.post_delete.connect(post_delete, sender=cls, weak=False)

class ModelWithHistoryBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        Model = ModelBase.__new__(cls, name, bases, attrs)
        history = getattr(Model, 'History', None)
        if history:
            history = history.__dict__
            if not 'model' in history:
                history['model'] = False
            if not 'fields' in history:
                history['fields'] = []
        else:
            #raise "Please add History subclass to your model"
            history = {
                'model': False,
                'fields': []
            }
        Model._history = history
        add_signals(Model)
        return Model

class ModelWithHistory(models.Model):
    __metaclass__ = ModelWithHistoryBase
    class Meta:
        abstract = True

    def _create_log_entry(self, action):
        if threadlocals.get_current_user().is_anonymous():
            user = User.objects.get(username='guest')
        else:
            user = threadlocals.get_current_user()
        history = LogEntry(user=user, object_id = self.pk, action_flag = action,
                            content_type = ContentType.objects.get_for_model(self))
        try:
            history.object_repr = unicode(self)
        except Exception:
            history.object_repr = "(unknown)"
        history.save()

    def _create_field_log_entry(self, name, value):
        if threadlocals.get_current_user().is_anonymous():
            user = User.objects.get(username='guest')
        else:
            user = threadlocals.get_current_user()
        from models import AttributeLogEntry
        history = AttributeLogEntry(user=user, object_id = self.pk, field_name=name, field_value = value,
                            content_type = ContentType.objects.get_for_model(self))
        # try:
        #     history.object_repr = repr(self)
        # except Exception:
        #     history.object_repr = "(unknown)"
        history.save()

    def get_history(self):
        content_type = ContentType.objects.get_for_model(self)
        return LogEntry.objects.filter(object_id=self.pk, content_type=content_type)

    def has_history(self):
        return bool(self.__class__._history.get('model', False))

    def last_edited_at(self):
        history = list(self.get_history()[:1])
        if not history:
            return datetime.datetime(2000, 1, 1, 0, 0, 0)
        else:
            return history[0].action_time

    def last_edited_by(self):
        history = list(self.get_history()[:1])
        if not history:
            return User.objects.get(pk=1)
        else:
            return history[0].user