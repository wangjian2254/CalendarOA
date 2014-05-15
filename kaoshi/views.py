#coding=utf-8
# Create your views here.
import json
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from kaoshi.models import Sheet, Option





#
# def toupiaoExcel(request):
#     subjectid = request.REQUEST.get('subjectid')
#     optionid = request.REQUEST.get('optionid')
#     subject = Subject.objects.get(pk=subjectid)
#     if subject.isNoName:
#         return HttpResponse(u'匿名投票不可导出')
#     filename=u'%s'%subject.title
#     if optionid:
#         option = Option.objects.get(pk=optionid)
#         if option.subject.pk!=subject.pk:
#             raise Http404
#         filename+=u'——%s'%option.content
#
#     response = HttpResponse(mimetype=u'application/ms-excel')
#     filenames = u'%s.xls'%filename
#     response['Content-Disposition'] = (u'attachment;filename=%s' % filenames).encode('utf-8')
#     import xlwt
#     from xlwt import Font, Alignment
#
#     style1 = xlwt.XFStyle()
#     font1 = Font()
#     font1.height = 260
#     font1.name = u'仿宋'
#     style1.font = font1
#     algn = Alignment()
#     algn.horz = Alignment.HORZ_LEFT
#     style1.alignment = algn
#     style1.font = font1
#     style0 = xlwt.XFStyle()
#     algn0 = Alignment()
#     algn0.horz = Alignment.HORZ_CENTER
#     font = Font()
#     font.height = 220
#     font.bold = False
#     font.name = u'仿宋'
#     style0.alignment = algn0
#     style0.font = font
#     wb = xlwt.Workbook()
#     ws = wb.add_sheet(u"人员名单", cell_overwrite_ok=True)
#     ws.header_str = filename
#     ws.footer_str =''
#     rownum = 0
#     num=1
#     query=Sheet.objects.filter(subject=subject)
#     if optionid:
#         query=query.filter(options=option)
#         ws.write_merge(rownum,rownum,0,0,u'序号',style0)
#         ws.write_merge(rownum,rownum,1,1,u'部门',style0)
#         ws.write_merge(rownum,rownum,2,2,u'人员',style0)
#         rownum+=1
#         for toupiao in query:
#             ws.write_merge(rownum,rownum,0,0,num,style0)
#             ws.write_merge(rownum,rownum,1,1,unicode(getattr(toupiao.user.person,'depate',u'无')),style0)
#             ws.write_merge(rownum,rownum,2,2,toupiao.user.person.truename,style0)
#             rownum+=1
#             num+=1
#     else:
#         for opt in Option.objects.filter(subject=subject):
#             ws.write_merge(rownum,rownum,0,2,u'选项：%s'%opt.content,style1)
#             rownum+=1
#             ws.write_merge(rownum,rownum,0,0,u'序号',style0)
#             ws.write_merge(rownum,rownum,1,1,u'部门',style0)
#             ws.write_merge(rownum,rownum,2,2,u'人员',style0)
#             rownum+=1
#             for toupiao in query.filter(options=opt):
#                 ws.write_merge(rownum,rownum,0,0,num,style0)
#                 ws.write_merge(rownum,rownum,1,1,unicode(getattr(toupiao.user.person,'depate',u'无')),style0)
#                 ws.write_merge(rownum,rownum,2,2,toupiao.user.person.truename,style0)
#                 rownum+=1
#                 num+=1
#     width=256*10
#     ws.col(0).width = width
#     ws.col(1).width = width*3
#     ws.col(2).width = width*2
#     wb.save(response)
#     return response
