#!/usr/bin/env python3
#coding:utf-8
import itchat,xlrd,time,random
from itchat.content import *
from threading import Thread

def print_t(string):
    # 记录日志到文件
    time_s = time.strftime('%Y-%m-%d %H:%M:%S ',time.localtime(time.time()))
    if show_log:
        f = open('wechat.log','a+')
        print('{0} {1}'.format(time_s, string), file = f)

def get_replay_by_id(index):
    nrows = table_p.nrows
    if (index != 0 and index <= nrows - 1):
        conf = table_p.row_values(index)
        if conf and conf[5] == 1:
            return '@%s@%s' % (conf[1],conf[2])
        else:
            return False

def get_replay_id_by_msg(msg):
    for i in range(0, len(key_words)):
        if msg.find(key_words[i]['word']) != -1:
            return key_words[i]['id']
    return 0

def get_group(index):
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

def replay_group_thread(text):
    global group_reply
    global group_replying
    for i in range(len(g_rooms)):
        print_t('正在发送至群:'+g_rooms[i].NickName)
        itchat.send(text, toUserName=g_rooms[i].UserName)
        # 发一条随机延时2-10秒，群发容易被封号
        time.sleep(random.randint(2,10))
    itchat.send('群发结束,已退出群发状态',toUserName='filehelper')
    group_reply = False
    group_replying = False

@itchat.msg_register(TEXT)
def text_reply(msg):
    global auto_reply
    global group_reply
    global group_replying
    global g_rooms
    # 当消息是由自己发出的时候
    if msg.ToUserName == 'filehelper':
        # 简单GM功能
        print_t("from_me:" + msg.Text)
        cmd_dic={
                    '/开启回复':'自动回复已开启',
                    '/关闭回复':'自动回复已关闭',
                    '/配置':'@fil@conf/reply.xls',
                    '/帮助':'/帮助  显示帮助信息\n\n/配置  下载服务端配置文件\n\n群发:x\nx为纯数字,下一条消息将被转发到配置的群分组\n\n/开启回复  开启自动回复\n\n/关闭回复  关闭自动回复',
                }
        try:
            cmd_dic[msg.Text]
            if msg.Text == '/开启回复':
                auto_reply = True
            if msg.Text == '/关闭回复':
                auto_reply = False
            itchat.send(cmd_dic[msg.Text], toUserName='filehelper')
        except:
            if group_reply == True:
                if msg.Text == "/取消群发":
                    group_reply = False
                    itchat.send('已退出群发状态',toUserName='filehelper')
                else:
                    if group_replying == False:
                        group_replying = True
                        thread=Thread(target=replay_group_thread,args=(msg.Text,))
                        thread.start()
                    else:
                        itchat.send('正在群发中,请等待群发结束', toUserName='filehelper')
            else:
                if msg.Text.split(':')[0] == '群发':
                    if group_reply == False:
                        group_reply = True
                        names = '下条消息将发往以下%d个群组，请慎重使用此功能，有被封号风险\n'
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
        if auto_reply == True:
            index = 0 
            try:
                index = int(msg.Text)
            except:
                print_t("输入类型不可转换为int型")
            reply_str = get_replay_by_id(index)
            if reply_str:
                return reply_str
            else:
                index = get_replay_id_by_msg(msg.Text)
                print_t('关键字索引为:'+ str(index))
                reply_str = get_replay_by_id(index)
                if reply_str:
                    return reply_str
        else:
            print_t('自动回复已关闭')

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    # 自动同意加好友，并回复一条消息
    msg.user.verify()
    conf = table_p.row_values(1)
    time.sleep(2)
    if conf:
        msg.user.send(get_replay_by_id(1))
    else:
        msg.user.send('你好,很高兴认识你!')

if __name__ == '__main__':
    # 设置参数
    auto_reply = True
    group_reply = False
    group_replying = False
    show_log = True
    # 配置表
    workbook = xlrd.open_workbook(u'conf/reply.xls')
    table_p = workbook.sheet_by_name(u'personal')
    table_g = workbook.sheet_by_name(u'group')
    #记录所有群组
    all_rooms = []
    #记录要转发消息的群组
    g_rooms = []
    #初始化关键字表-----------------------
    key_words = []
    ncols = table_p.ncols
    conf_key_word = table_p.col_values(3)
    for i in range(1,len(conf_key_word)):
        tb = conf_key_word[i].split(',')
        for n in range(0, len(tb)):
            dic = {'word':tb[n], 'id':i}
            key_words.insert(0,dic)
    #-------------------------------------
    itchat.auto_login()
    itchat.run()
