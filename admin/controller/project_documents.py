# -*- coding:utf-8 -*-

import base
import os
import re
import fcntl
import commands
import struct
import socket
from api.html import MYHTMLParser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class documents(base.base):
    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)
        self.project_Service = self.importService('project_documents')

    def index(self):

        strMenu = 'project_documents'
        try:
            intPage = int(self.I('page'))
        except ValueError:
            intPage = 1

        # 单页数据条数
        intPageDataNum = 10
        # 分页url
        strPageUrl = '/project/documents?'
        uid = self.current_user.get('id')

        tupData, intRows = self.project_Service.get_documentsPage(intPage, intPageDataNum)
        for idx, item in enumerate(tupData, 1):
            item['idx'] = (intPage - 1) * intPageDataNum + idx
            item['update_time'] = self.formatTime(item.get('update_time'), '%Y-%m-%d')

        self.dicViewData['documentsData'] = tupData
        self.dicViewData['page_html'] = self.page(intPage, intPageDataNum, intRows, strPageUrl)
        self.dicViewData['menu'] = strMenu
        self.display('documents', 'project')

    def follow(self):
        id = self.I('id')
        remark = self.I('follow_remark')
        group_id = self.I('group')
        uid = self.current_user.get('id')
        if group_id:
            group_id = group_id.split(',')

        status = self.project_Service.follow_group(id, group_id, uid, remark)
        self.out(status)

    def load(self):
        sourceData = self.I('documents_load_info')
        file_name = self.I('documents_load_title')+".docx"
        path = self.dicConfig['UPLOAD_PATH'] + "/static/data/"+file_name
        documents_load= MYHTMLParser(path, self.I('documents_load_title'))
        documents_load.complete(sourceData)

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        buf_size = 1024
        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()
        try:
            import os
            os.remove(path)
        except Exception:
            pass
        return False

    def create_display(self):
        self.dicViewData['menu'] = "project_documents"
        self.display('create', 'project')

    def create(self):
        str = self.I('myEditors')
        dicArgs = {
            'content': str,
            'documents_title': self.I('documents_title'),
        }
        self.project_Service.create_documents(dicArgs)
        self.redirect('/project/documents')

    def update_display(self):
        media_id = int(self.I('id'))
        data_dict = self.project_Service.get_documents_detail(media_id)
        self.dicViewData['detail_info'] = data_dict
        self.dicViewData['menu'] = "project_documents"
        self.display('update', 'project')

    def update(self):
        dicArgs = {
            'documents_title': self.I('documents_titleUp'),
            'content': self.I('myEditorsUp'),
            'media_content_id':self.I('id'),
        }
        self.project_Service.update_documents(dicArgs)
        self.redirect('/project/documents')


    def details(self):
        media_id = int(self.I('id'))
        uid = self.current_user.get('id')
        self.dicViewData['menu'] = "project_documents"
        data_dict = self.project_Service.get_documents_detail(media_id)
        data_dict['update_time'] = self.formatTime(data_dict.get('update_time'), '%Y-%m-%d')
        data_dict['create_time'] = self.formatTime(data_dict.get('create_time'), '%Y-%m-%d')
        self.dicViewData['group'] = self.project_Service.check_group(media_id, uid)
        self.dicViewData['detail_info'] = data_dict
        self.dicViewData['groupData'] = self.importService('admin_user').get_group(uid, 3)

        self.display('detail', 'project')


class Ue_ImageUp(base.base):

    def initialize(self):
        config = {'isDataBase': True}
        base.base.initialize(self, config)

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    def index(self):
        reqfile = self.request.files['upfile']
        if len(reqfile)==1:
            filename = reqfile[0]['filename']
            content_type = reqfile[0]['content_type']
            content = reqfile[0]['body']
            fileName_all = self.saveUploadFile(filename,content)
            #返回数据
            return_info = [{
                'url': fileName_all ,                # 保存后的文件名称
                'original': filename,                # 原始文件名
                'type': content_type,
                'state': 'SUCCESS',                  # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
                'size': len(content)
            }]
        else:
            return_info=[{
                "state":u"未找到匹配文件！",
                "list":[],
                "size":0
            }]
        self.out(200, '', return_info)

    def getPort(self):
        ps_stat = ""
        try:
            #获取进程的内存信息
            ps_stat = self.request.host.split(':')
            if ps_stat and len(ps_stat)>1:
                ps_stat = ps_stat[1]
        except Exception,e:
            print "filterList e = ",e
        return ps_stat

    def saveUploadFile(self, fileName, content):
        ueconfig_dir = self.dicConfig['ueconfig_dir']
        myaddrIP = self.get_ip_address('eth1')
        strPort = self.getPort()
        if not strPort:
            strPort = "80"

        fileName_all = ueconfig_dir + '/' + self.md5(fileName)[:8]+'.'+fileName.split('.')[-1] # replaces the windows-style slashes with linux ones.
        fout=file(fileName_all,'w')
        fout.write(content) # writes the uploaded file to the newly created file.
        fout.close() # closes the file, upload complete.
        fileName_http = 'http://' + myaddrIP+ ':'+strPort+'/' + fileName_all
        return fileName_http

