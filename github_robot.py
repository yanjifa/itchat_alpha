#!/usr/bin/env python3
#coding:utf-8
import itchat,xlrd,time,random
from itchat.content import TEXT, FRIENDS
from threading import Thread

@itchat.msg_register(TEXT)
def text_reply(msg):
    # 当消息是由自己发出的时候
    if msg.ToUserName == 'filehelper':
        print("from_me:" + msg.Text)

if __name__ == '__main__':
    itchat.auto_login()
    itchat.run()
