# -*- coding:utf-8 -*-

import base
import fcntl
import struct
import socket

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class ImageUpload(base.base):

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