# -*- coding:utf-8 -*-
import os
import sys

def kill_process(port_num):
    '''
    author : PAN YANG
    kill the process that use the port which python configuration going to use
    parameter: port_num to use
    '''
    ret = os.popen("/usr/sbin/lsof -i:{port}".format(port = port_num))
    str_list = ret.read()
    ret_list = str_list.split()
    if 'python'in ret_list and (len(ret_list)>ret_list.index('python')) :
        if ret_list[ret_list.index('python')+1].isdigit():
            pid = ret_list[ret_list.index('python')+1]
            os.system("kill -9 {process_pid}".format(process_pid = pid))


def port_to_kill(argv):
    for arg in argv:
        if arg.isdigit():
            kill_process(arg)

if __name__ == '__main__':
    port_to_kill(sys.argv)