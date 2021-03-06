# -*- coding:utf-8 -*-

import win32con
import win32api
import win32security
import wmi
import sys
import os

def get_process_privileges(pid):
    try:
        #获取目标进程的句柄
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,pid)
        #打开主进程的令牌
        htok = win32security.OpenProcessToken(hproc,win32con.TOKEN_QUERY)

        #解析已启用权限的列表
        privs = win32security.GetTokenInformation(htok,win32security.TokenPrivileges)
        #迭代每个权限输出其中已经启用的
        priv_list = ""
        for i in privs:
            #检测权限是否已经启用
            if i[1] == 3:
                priv_list += "%s|"%win32security.LookupPrivilegeName(None,i[0])
    except:
        priv_list = "N/A"
    return priv_list

def log_to_file(message):
    fd = open("process_mintor_log.csv",'ab')
    fd.write("%s\r\n"%message)
    fd.close()
    return

#创建一个日志文件的头
log_to_file("Time,User,Executable,CommandLine,PID,Parent,PID,Privileges")
#初始化Wmi借口
c = wmi.WMI()

#创建进程监控器
process_watcher = c.Win32_Process.watch_for("creation")

while True:
    try:
        new_process = process_watcher()
        proc_owner = new_process.GetOwner()
        proc_owner = "%s\\%s"%(proc_owner[0],proc_owner[2])
        create_date =new_process.CreationDate
        executable = new_process.ExecutablePath
        cmdline = new_process.CommandLine
        pid = new_process.ProcessId
        parent_pid = new_process.ParentProcessId
        privileges = get_process_privileges(pid)
        process_log_message ="%s,%s,%s,%s,%s,%s,%s\r"%(create_date,proc_owner,executable,cmdline,pid,parent_pid,privileges)
        print process_log_message
        log_to_file(process_log_message)
    except:
        pass

