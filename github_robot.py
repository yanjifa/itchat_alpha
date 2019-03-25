#!/usr/bin/env python3
#coding:utf-8
import itchat, time, os, urllib, json
from itchat.content import TEXT
from http.server import HTTPServer, BaseHTTPRequestHandler

host = ("0.0.0.0", 8888)
rooms = []

class Resquest(BaseHTTPRequestHandler):
    def do_POST(self):
        global rooms
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            datas = self.rfile.read(int(self.headers['content-length']))
            datas = json.loads(datas.decode(encoding='UTF-8',errors='strict'))
            self.wfile.write(json.dumps("ok", ensure_ascii=False).encode('utf-8'))
            branch = datas["ref"].split("/")[-1]
            text = datas["pusher"]["name"] + " pushed branch " + branch + " at repository " + datas["repository"]["name"] + "\n"
            for commit in datas["commits"]:
                commit["id"] = commit["id"][0:7]
                msg = "%(url)s\n %(message)s \n" % commit
                text = text + msg

            for room in rooms:
                print("send to" + room["NickName"])
                itchat.send(text, toUserName = room["UserName"])
            print(text)
        except Exception as e:
            print('Error:', e)
        finally:
            print()

def need_notify(room):
    return room["NickName"] == "测试1群"

def after_login():
    global rooms
    rooms = itchat.get_chatrooms(update=True)
    rooms = list(filter(need_notify, rooms))
    server = HTTPServer(host, Resquest)
    itchat.send("Starting server", toUserName ='filehelper')
    server.serve_forever()

@itchat.msg_register(TEXT)
def text_reply(msg):
    # 当消息是由自己发出的时候
    if msg.ToUserName == 'filehelper':
        print("from_me:" + msg.Text)


if __name__ == '__main__':
    itchat.auto_login(enableCmdQR=2, loginCallback=after_login)
    itchat.run()
