#!/usr/bin/env python  
#coding:utf-8  
#filename:tcp.py  
'''  
author: shenzhiwei
date:   2016-04-08 09:35:59   
'''  
import socket  
import copy
import sys  
import Queue
from  threading import Thread,Lock,Condition
import time
import random
import subprocess
import string
import hashlib
import traceback
from eventlet import greenthread
import tempfile
import shutil
import sys
 
NORMAL=0  
ERROR=1  
TIMEOUT=5  

SRC_IP={"10.10.10.1":1,"20.20.20.2":1} ##分布在不同的机房
queue = []

condition = Condition()

line = []

class ProducerThread(Thread):

    def __init__(self) :
        super(ProducerThread, self).__init__()  #调用父类的构造函数
    self.ip = ""

    def get_ip(self):
    global line 
        with open("/etc/hosts","r")  as f:
            line=f.readlines()
        return  line[:-1],line[-1].split()[0]

    def run(self):
        global queue,line
        while True:
            condition.acquire()
        line,self.ip = self.get_ip()
            if self.check_tcp(self.ip,port=389):
                queue.append(self.ip)
                print "Produced %s" %(self.ip)
            condition.notify()
            condition.release()
            time.sleep(5)

    def check_tcp(self,ip,port,timeout=TIMEOUT):  
        try:  
            cs=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
            address=(str(ip),int(port))  
            status = cs.connect_ex((address))  
            cs.settimeout(timeout)  
            #this status is returnback from tcpserver  
            if status != NORMAL :  
                print "tcp port %d is wrong " %(port)
                return ERROR
            else:  
                print "tcp port %d is OK "  %(port)
                return NORMAL
        except Exception ,e:  
            print "error:%s" %e  
            return ERROR  

class ConsumerThread(Thread):

    def __init__(self,func):
        super(ConsumerThread, self).__init__() 
        self.cmd=func

    def run(self):
        global queue,line
        while True:
            condition.acquire()
            if not queue:
                print "Nothing in queue, consumer is waiting"
                condition.wait()
                print "Producer added something to queue and notified the consumer"
            try:
                num = queue.pop()
            global SRC_IP
            tmp = copy.copy(SRC_IP)
            tmp.pop(num,"false")
        print "##############"
        print "####",line
        print "##############"
        line.append(str(tmp.keys()[0])+"    ldap.opstack.cc\n")   ### 替换本地解析##
        with open("/etc/hosts","wb") as f:
            for t in line:
                f.write(t)
        line.pop()
                result,code = self.cmd("pkill","-HUP","squid")
        print "#######"
        print "code is %d",code
        print "#######"
                if code:
            print "hard restart ..."
                    self.cmd("/usr/local/squid/sbin/squid","-s")
            except Exception ,e:
                print "Queue is NULL",e 
            condition.release()
            time.sleep(random.random())

    def alert(self):
            pass

def cmd(*cmd,**kwargs):
    delay_on_retry = kwargs.pop('delay_on_retry', True)
    shell = kwargs.pop('shell', False)
    attempts = kwargs.pop('attempts', 1)
    while attempts > 0:
        attempts -= 1
        try:
            _PIPE = subprocess.PIPE
            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE, stderr=_PIPE,
                                   stdout=_PIPE, close_fds=True,
                                   shell=shell)
            result = obj.communicate()
            obj.stdin.close()
            _returncode = obj.returncode
            return result, _returncode
        except:
            if delay_on_retry:
                greenthread.sleep(random.randint(20, 200) / 100.0)
        finally:
            greenthread.sleep(0)

def mainloop():
    [thread.start() for thread in [ ProducerThread(),ConsumerThread(cmd)]] 

if __name__=='__main__':  

    mainloop()


