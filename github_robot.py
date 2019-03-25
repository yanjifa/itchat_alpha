#!/usr/bin/env python3
#coding:utf-8
import itchat, time, os, urllib, json
from itchat.content import TEXT
from http.server import HTTPServer, BaseHTTPRequestHandler

host = ("0.0.0.0", 8888)

class Resquest(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        try:
            datas = self.rfile.read(int(self.headers['content-length']))
            datas = json.loads(datas.decode())
            print(datas)
            print(datas["commits"])
            # print(datas["pusher"]["name"])
            # print(datas["pusher"]["email"])
            self.wfile.write(json.dumps("ok", ensure_ascii=False).encode())
            text = datas["pusher"]["name"] + " pushed branch at " + datas["repository"]["name"] + "\n"
            for commit in datas["commits"]:
                text = text + str(commit) + "\n"
            # text = text + datas["pusher"]["email"] + "\n"
            print(text)

        except Exception as e:
            print('Error:', e)
        finally:
            print()


def after_login():
    server = HTTPServer(host, Resquest)
    # itchat.send("Starting server, listen at: " + host[0] + ":" + str(host[1]), toUserName ='filehelper')
    server.serve_forever()

@itchat.msg_register(TEXT)
def text_reply(msg):
    # 当消息是由自己发出的时候
    if msg.ToUserName == 'filehelper':
        print("from_me:" + msg.Text)


if __name__ == '__main__':
    after_login()
    # itchat.auto_login(enableCmdQR=2, loginCallback=after_login)
    # itchat.run()
