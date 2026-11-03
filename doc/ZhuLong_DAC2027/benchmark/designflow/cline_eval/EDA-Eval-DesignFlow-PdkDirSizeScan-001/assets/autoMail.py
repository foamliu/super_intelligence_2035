#!/bin/env python3.7
#####################################
#  Author: Bill.Chen
#  CreateTime: 2019-10-21
#####################################

import os,sys,json

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart   import MIMEMultipart
from email.mime.application import MIMEApplication
from soa import *

def autoMail(input):
  try:
    if isinstance(input,str) and os.path.isfile(input):
       Text,subject,receivers,filePath = soaParseJS.read(input,"Text","subject","receivers","filePath")
    if isinstance(input,dict):
       Text,subject,receivers,filePath = input["Text"],input["subject"],input["receivers"],input["filePath"]

    from_addr = "design.cad@cxmt.com"
    password  = "********"
    msgFrom   = "AutoFlow.Bill"
    smtp      = "10.128.246.58"

    msg = MIMEMultipart()
    puretext = MIMEText(Text)
    msg['From']     = from_addr
    msg['To']       = ",".join(receivers)
    msg['Subject']  = subject
    msg.attach(puretext)

    if not isinstance(filePath,list):
       filePath = [filePath]

    for file in filePath:
        if file :
           xlsxpart = MIMEApplication(open(file,'rb').read())
           xName = file.split("/")[-1]
           xlsxpart.add_header('Content-Disposition','attachment',filename=xName)
           msg.attach(xlsxpart)

    s = smtplib.SMTP(smtp,25)
    s.ehlo(smtp)
    s.login(from_addr,password)
    result = s.sendmail(from_addr,receivers,msg.as_string())
  except Exception as e :
    print("\n[ERROR]--in send mail:\n%s" %e)


if __name__ == "__main__" :
  inputPath = "input.js"
  argvs = sys.argv
  if len(argvs) >=2 :
     inputPath = argvs[1]
  autoMail(inputPath)
