#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
__author__ = u'王健'

from django.core.serializers import deserialize, serialize
from django.db.models.query import QuerySet
from django.db import models
from django.utils import simplejson
import json
from django.http import HttpResponse
from django.core.cache import cache





def getErrorFormResult(form):
    msg = form.json_error()
    return getResult(False, msg, None)


def getCacheResult(cache_name):
    cache_result = cache.get(cache_name)
    if cache_result:
        return HttpResponse(cache_result)
    else:
        return

def getResult(success,message,result=None,status_code=200,cachename=None):
    '''
    200 正常返回 code
    201 用户名已经具有
    202 需要验证邮箱
    400 组织余额不足，需要充值后继续使用
    401 用户禁止使用
    402 用户离开了当前组织
    403 需要先选择当前的组织
    404 登录过期，需要重新登录
    '''
    map={'success':success,'message':message, 'status_code':status_code}
    if result:
        map['result']=result
    jsonstr=json.dumps(map)
    if cachename:
        cache.set(cachename,jsonstr,3600*24*31)
    return HttpResponse(jsonstr)


class MyEncoder(simplejson.JSONEncoder):
    """ 继承自simplejson的编码基类，用于处理复杂类型的编码
    """
    @staticmethod
    def default( obj):
        if isinstance(obj,QuerySet):
            l = []
            for o in MyEncoder.obj2json(obj):
                o.update(o['fields'])
                o['id'] = o['pk']
                del o['fields']
                l.append(o)
            return l
        if isinstance(obj,models.Model):
            o = MyEncoder.obj2json(obj)
            o.update(o['fields'])
            o['id'] = o['pk']
            del o['fields']
            return o
        if hasattr(obj, 'isoformat'):
            #处理日期类型
            return obj.isoformat()
        return None

    @staticmethod
    def obj2json(obj):
        if isinstance(obj,QuerySet):
            """ Queryset实例
            直接使用Django内置的序列化工具进行序列化
            但是如果直接返回serialize('json',obj)
            则在simplejson序列化时会被从当成字符串处理
            则会多出前后的双引号
            因此这里先获得序列化后的对象
            然后再用simplejson反序列化一次
            得到一个标准的字典（dict）对象
            """
            return simplejson.loads(serialize('json',obj))
        if isinstance(obj,models.Model):
            """
            如果传入的是单个对象，区别于QuerySet的就是
            Django不支持序列化单个对象
            因此，首先用单个对象来构造一个只有一个对象的数组
            这是就可以看做是QuerySet对象
            然后此时再用Django来进行序列化
            就如同处理QuerySet一样
            但是由于序列化QuerySet会被'[]'所包围
            因此使用string[1:-1]来去除
            由于序列化QuerySet而带入的'[]'
            """
            return simplejson.loads(serialize('json',[obj])[1:-1])
        if hasattr(obj, 'isoformat'):
            #处理日期类型
            return obj.isoformat()
        return None

def jsonBack(json):
     """    进行Json字符串的反序列化
         一般来说，从网络得回的POST（或者GET）
         参数中所包含json数据
         例如，用POST传过来的参数中有一个key value键值对为
         request.POST['update']
         = "[{pk:1,name:'changename'},{pk:2,name:'changename2'}]"
         要将这个value进行反序列化
         则可以使用Django内置的序列化与反序列化
         但是问题在于
         传回的有可能是代表单个对象的json字符串
         如：
         request.POST['update'] = "{pk:1,name:'changename'}"
         这是，由于Django无法处理单个对象
         因此要做适当的处理
         将其模拟成一个数组，也就是用'[]'进行包围
         再进行反序列化
     """
     if json[0] == '[':
         return deserialize('json',json)
     else:
         return deserialize('json','[' + json +']')

def getJson(**args):
     """    使用MyEncoder这个自定义的规则类来序列化对象
     """
     result = dict(args)
     return simplejson.dumps(result,cls=MyEncoder)
