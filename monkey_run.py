#! /usr/bin/env python
# coding=utf-8

import os
import time
import re

###################################################################
# Please change the packageName and logdir before run this script
packageName = "*****"
logdir = r"******"
###################################################################

cmd0 = "adb shell cat /system/build.prop > %sphone.txt" % (logdir)
os.system(cmd0)

f = r"%sphone.txt" % (logdir)
def getPhoneInfo(phone):
    f = open(phone, 'r')
    lines = f.readlines()
    for line in lines:
        line = line.split("=")
        if line[0] == 'ro.build.version.release':
            version = line[1]
        if line[0] == 'ro.product.brand':
            brand = line[1]

    return version, brand

version, brand = getPhoneInfo(f)
print version,brand
os.remove(f)

# clear the log
os.popen("adb logcat -c")

print "wait"
time.sleep(2)

nowTime = time.strftime("%y-%m-%d-%H_%M_%S", time.localtime(time.time()))
monkeyLog = logdir + nowTime + "-monkey.log"
print monkeyLog

# start do monkey
######################################################
# Here modify the cmd to achieve better coverage
######################################################
#cmd = "adb shell monkey -p %s -s 500 --throttle 10 --ignore-crashes --ignore-timeouts --monitor-native-crashes --pct-appswitch 30 --pct-majornav 20 --pct-nav 20 --pct-touch 20 --pct-motion 10 -v -v -v 10000 >> %s" % (packageName,monkeyLog)

cmd = "adb shell monkey -p %s -s 500 --throttle 10 --ignore-crashes --ignore-timeouts --monitor-native-crashes --pct-appswitch 30 --pct-majornav 20 --pct-nav 20 --pct-touch 20 --pct-motion 10 -v -v -v 1000 >> %s" % (packageName,monkeyLog)

os.popen(cmd)

# take screencap
os.popen("adb shell screencap -p /sdcard/monkey_run.png")
cmd1 = "adb pull /sdcard/monkey_run.png %s" % (logdir)
os.popen(cmd1)

pngfile = logdir + "monkey_run.png"
if os.path.exists(pngfile):
    print "file exists..."
else:
    print "file not exists..."

newname = logdir + "/" + nowTime + r"monkey_png"
os.rename(pngfile, newname)

#  export log
logcatname = logdir + nowTime + r"logcat.log"
cmd2 = "adb logcat -d > %s" % (logcatname)
os.popen(cmd2)

# export trace
tracefilename = logdir + nowTime + r"trace.txt"
cmd3 = "adb shell cat /data/anr/traces.txt > %s" % (tracefilename)
os.popen(cmd3)

###########################################################################
# analyze log file to seek error
###########################################################################
NullPointer="java.lang.NullPointerException"
IllegalState="java.lang.IllegalStateException"
IllegalArgument="java.lang.IllegalArgumentException"
ArrayIndexOutOfBounds="java.lang.ArrayIndexOutOfBoundsException"
RuntimeException="java.lang.RuntimeException"
SecurityException="java.lang.SecurityException"

def geterror():
    f = open(logcatname,"r")
    lines = f.readlines()

    errfile="%s/error.txt" % (logdir)
    if (os.path.exists(errfile)):
        os.remove(errfile)
    fr = open(errfile,"a")
    fr.write(version)
    fr.write("\n")
    fr.write(brand)
    fr.write("\n")
    fr.write(nowTime)
    fr.write("\n")

    count = 0
    for line in lines:
        if (re.findall(NullPointer,line) or re.findall(IllegalArgument,line) or re.findall(IllegalState,line) or re.findall(ArrayIndexOutOfBounds,line) or re.findall(SecurityException,line)):

            tag = "error: %d------------------------------------------------------------\n" % (count+1)
            print tag
            fr.write(tag) 
            index = lines.index(line)
            count = count + 1
            for var in range(index, index+30):
                print lines[var]
                fr.write(lines[var])

    f.close()
    fr.close()
    return count
errornum = geterror()
print "Found %d exceptions!" % (errornum)

#################################################################
# send email
##################################################################
import smtplib
from email.mime.text import MIMEText

def sendmail(receiver, title, body):
    sender = "******"
    host = "smtp.163.com"
    port = 25
    pwd = "******"

    message = MIMEText(body, 'plain', 'utf-8')
    message['from'] = sender
    message['to'] = receiver
    message['subject'] = title
    try:
        s = smtplib.SMTP()
        s.connect(host, port)
        s.login(sender, pwd)
        s.sendmail(sender, receiver, message.as_string())
        s.close()
        print "Email has been sent to your email !"
    except Exception, e:
        #print str(e)
        print "Send failed ..."

if errornum > 0 :
    email = raw_input("Please leave your email , we will send the report to you : ")
    nowTime = time.strftime("%y-%m-%d %H:%M:%S", time.localtime(time.time()))
    title = 'Error Report From Monkey Server %s' % (str(nowTime))
    errfile = "%s/error.txt" % (logdir)
    f = open(errfile, 'r')
    body = f.read()
    sendmail(email, title,body)
    f.close()





