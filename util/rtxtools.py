#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import urllib
from CalendarOA import settings
from CalendarOA.settings import RTX_HOST, RTX_PORT
import threading
__author__ = u'王健'


hosturl = '%s:%s/' % (RTX_HOST, RTX_PORT)

api = {'sendnotify': '%ssendnotify.cgi' % hosturl, 'getstatus': '%sgetstatus.php' % hosturl,
       'getimage': '%sgetimage.cgi' % hosturl}

class RTXThread(threading.Thread):

    def __init__(self, usernamelist, msg, title, delaytime):

        self.usernamelist = usernamelist

        self.msg = msg

        self.title = title

        self.delaytime = delaytime



        threading.Thread.__init__(self)

    def run (self):
        for username in self.usernamelist:
            s = urllib.urlencode({'receiver': username, 'msg': self.msg, 'title': self.title, 'delaytime': self.delaytime})
            html = urllib.urlopen(api.get('sendnotify'), s).read()
            if settings.DEBUG:
                print html

def send_rtxmsg(usernamelist,msg,title,delaytime=120000):
    RTXThread(usernamelist,msg,title,delaytime).start()