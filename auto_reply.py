#!/usr/bin/env python3
#coding:utf-8
import itchat
from itchat.content import *
import xlrd
import time

autoReply = True
group_reply = False
show_log = False
workbook = xlrd.open_workbook('conf/reply.xls')
table_p = workbook.sheet_by_name(u'personal')
table_g = workbook.sheet_by_name(u'group')
all_rooms = []
g_rooms = []
key_words = []
#初始化关键字表
ncols = table_p.ncols
conf_key_word = table_p.col_values(3)
for i in range(1,len(conf_key_word)):
    tb = conf_key_word[i].split(',')
    for n in range(0, len(tb)):
        dic = {'word':tb[n], 'id':i}
        key_words.insert(0,dic)


def print_t(str):
    time_s = time.strftime('%Y-%m-%d %H:%M:%S ',time.localtime(time.time()))
    if show_log:
        print(time_s+str)

def get_replay_by_id(index):
    global table_p
    nrows = table_p.nrows
    if (index != 0 and index <= nrows - 1):
        conf = table_p.row_values(index)
        if conf and conf[5] == 1:
            # print_t('@%s@%s' % (conf[1],conf[2]))
            return '@%s@%s' % (conf[1],conf[2])
        else:
            return False

def get_replay_id_by_msg(msg):
    global key_words
    for i in range(0, len(key_words)):
        if msg.find(key_words[i]['word']) != -1:
            return key_words[i]['id']
    return 0

def get_group(index):
    global table_g
    global all_rooms
    nrows = table_g.nrows
    if index != 0 and index <= nrows - 1:
        conf = table_g.row_values(index)
        if len(all_rooms) == 0:
            all_rooms = itchat.get_chatrooms(update=True)
        room = []
        for i in range(len(all_rooms)):
            # print_t(all_rooms[i].NickName)
            for n in range(1,len(conf)):
                if str(conf[n]) == all_rooms[i].NickName:
                    room.insert(0,all_rooms[i])
                    break
        return room
    else:
        return []

@itchat.msg_register([TEXT,PICTURE])
def text_reply(msg):
    global autoReply
    global table_p
    global group_reply
    global g_rooms
    # 当消息是由自己发出的时候
    if msg.FromUserName == myUserName:
        # 简单GM功能
        print_t(msg.fromUserName + ':' + msg.Text)
        if msg.Text == '/开启回复':
            autoReply = True
            itchat.send('自动回复已开启', toUserName='filehelper')

        if msg.Text == '/关闭回复':
            autoReply = False
            itchat.send('自动回复已关闭',toUserName='filehelper')

        if msg.Text == '/配置':
            itchat.send('@fil@%s' % 'conf/reply.xls', toUserName='filehelper')

        if msg.Text == '/帮助':
            itchat.send('/帮助  显示帮助信息\n\n/配置  下载服务端配置文件\n\n群发:x\nx为纯数字,下一条消息将被转发到配置的群分组\n\n/开启回复  开启自动回复\n\n/关闭回复  关闭自动回复',toUserName='filehelper')

        if group_reply == True:
            if msg.Text == "/取消群发":
                itchat.send('已退出群发状态',toUserName='filehelper')
                group_reply = False
            else: 
                for i in range(len(g_rooms)):
                    print_t(msg.Text + ':' + g_rooms[i].NickName)
                    itchat.send(msg.Text, toUserName=g_rooms[i].UserName)
                    time.sleep(1)
                itchat.send('群发结束',toUserName='filehelper')
                group_reply = False
        else:
            if msg.Text.split(':')[0] == '群发':
                if group_reply == False:
                    group_reply = True
                    names = '下条消息将发往以下%d个群组\n'
                    index = 0
                    try:
                        index = int(msg.Text.split(':')[1])
                    except:
                        print_t('群发命令参数有误')
                    rooms = get_group(index)
                    g_rooms = rooms
                    for i in range(len(rooms)):
                        names = names + rooms[i].NickName + '\n'
                    names = names%(len(rooms))
                    if len(rooms) == 0:
                        group_reply = False
                    print_t(names)
                    itchat.send(names, toUserName='filehelper')
                else:
                    itchat.send('正在群发中,请稍后再试', toUserName='filehelper')

    else:
        if autoReply == True:
            index = 0 
            try:
                index = int(msg.Text)
            except:
                print_t("输入类型不可转换为int型")
            reply_str = get_replay_by_id(index)
            if reply_str:
                return reply_str
            else:
                id_t = get_replay_id_by_msg(msg.Text)
                print_t('关键字索引为:'+ str(id_t))
                reply_str = get_replay_by_id(id_t)
                if reply_str:
                    return reply_str
                # else:
                #     # 配置第一行为默认回复消息
                #     return get_replay_by_id(1)
        else:
            print_t('自动回复已关闭')

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    # 自动同意加好友，并回复一条消息
    global table_p
    msg.user.verify()
    conf = table_p.row_values(1)
    if conf:
        msg.user.send(get_replay_by_id(1))
    else:
        msg.user.send('你好,很高兴认识你!')

if __name__ == '__main__':
    itchat.auto_login()
    # 获取自己的UserName
    myUserName = itchat.get_friends(update=True)[0]['UserName']
    itchat.run()
