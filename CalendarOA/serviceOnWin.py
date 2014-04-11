#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'
import win32serviceutil
import win32service
import win32event

class PythonService(win32serviceutil.ServiceFramework):
    """
    Usage: 'PythonService.py [options] install|update|remove|start [...]|stop|restart [...]|debug [...]'
    Options for 'install' and 'update' commands only:
     --username domain\username : The Username the service is to run under
     --password password : The password for the username
     --startup [manual|auto|disabled|delayed] : How the service starts, default = manual
     --interactive : Allow the service to interact with the desktop.
     --perfmonini file: .ini file to use for registering performance monitor data
     --perfmondll file: .dll file to use when querying the service for
       performance data, default = perfmondata.dll
    Options for 'start' and 'stop' commands only:
     --wait seconds: Wait for the service to actually start or stop.
                     If you specify --wait with the 'stop' option, the service
                     and all dependent services will be stopped, each waiting
                     the specified period.
    """
    #服务名
    _svc_name_ = "CalendarOAService"
    #服务显示名称
    _svc_display_name_ = "Calendar OA Service"
    #服务描述
    _svc_description_ = "Calendar OA Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        # self.logger = self._getLogger()
        self.isAlive = True

    # def _getLogger(self):
    #     import logging
    #     import os
    #     import inspect
    #
    #     logger = logging.getLogger('[CalendarOAService]')
    #
    #     this_file = inspect.getfile(inspect.currentframe())
    #     dirpath = os.path.abspath(os.path.dirname(this_file))
    #     handler = logging.FileHandler(os.path.join(dirpath, "service.log"))
    #
    #     formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    #     handler.setFormatter(formatter)
    #
    #     logger.addHandler(handler)
    #     logger.setLevel(logging.INFO)
    #
    #     return logger

    def SvcDoRun(self):
        import time, urllib
        import os
        import inspect
        # from CalendarOA.settings import APP_HOST
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        APP_HOST='http://127.0.0.1:8190'
        for line in open('%s/settings.py'%dirpath,'r'):
            if line.find('APP_HOST')==0:
                APP_HOST=line.split("'")[1]
        # self.logger.error("start……")
        num = 0
        # APP_HOST ='http://192.168.101.18:8190'
        while self.isAlive:
            try:
                urllib.urlopen('%s/ca/warningTask'%APP_HOST).read()
                if num%10==0:
                    urllib.urlopen('%s/ca/zentaoTask'%APP_HOST).read()
                    urllib.urlopen('%s/ca/zentaoStatusTask'%APP_HOST).read()
                    urllib.urlopen('%s/ca/zentaoStatusBug'%APP_HOST).read()
                time.sleep(50)
            except Exception,e:
                # self.logger.error("%s"%e)
                time.sleep(60*3)
        # 等待服务被停止
        #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def SvcStop(self):
        # 先告诉SCM停止这个过程
        # self.logger.error("stop……")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # 设置事件
        win32event.SetEvent(self.hWaitStop)
        self.isAlive = False

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(PythonService)