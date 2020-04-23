# Copyright (c) 2020 by xfangfang. All Rights Reserved.

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import os

from var import *
from plugins import BroadcastPlugin, ServoPlugin, MotorPlugin


# http Handler
class HelloWorld(object):
    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler


# websocket Handler
class BroadcastWebSocketHandler(WebSocket):
    def opened(self):
        logger.info("BroadcastWebSocketHandler - opened")
        # 通知客户端连接成功
        self.send("START")

    def closed(self, code, reason="A client left the room without a proper explanation."):
        logger.info("BroadcastWebSocketHandler - closed %d %s"%(code,reason))

    def received_message(self, message):
        messages = message.data.decode().split('-')
        if messages[0] == 'REQUESTSTREAM':
            # 将接受视频流的websocket单独管理 见 VideoWebsocketManager
            cherrypy.engine.publish('handle-video-websocket', self)
        elif messages[0] == 'init':
            # 客户端发出重置舵机请求——舵机摆正
            cherrypy.engine.publish('servo-test')
        elif messages[0] == 'test':
            # 客户端的心跳检测信号 可以用来粗略检测延时大小
            self.send('test')
        elif messages[0] == 's':
            # 客户端发来的舵机移动信号
            x = float(messages[1])
            y = float(messages[2])
            # 0 -  100
            if x == 0  and y ==0:
                cherrypy.engine.publish('servo-stopFreeMove')
            else:
                cherrypy.engine.publish('servo-updateFreeMove', x, y)
        elif messages[0] == 'm':
            # 客户端发来的电机移动信号
            h = float(messages[1])
            v = float(messages[2])
            # 0 -  100
            if h == 0  and v == 0:
                cherrypy.engine.publish('motor-stop')
            else:
                cherrypy.engine.publish('motor-update', v, h)


if __name__ == '__main__':

    # ws4py 基本配置
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    # video broadcast 视频广播
    BroadcastPlugin(cherrypy.engine).subscribe()
    # servo 舵机
    ServoPlugin(cherrypy.engine).subscribe()
    # motor 电机
    MotorPlugin(cherrypy.engine).subscribe()

    cherrypy.config.update({
        'server.socket_host' : '0.0.0.0',
        'server.socket_port' : PORT,
    })

    cherrypy_config = {'/ws': {'tools.websocket.on': True,
                               'tools.websocket.handler_cls': BroadcastWebSocketHandler},
                       '/': {'tools.staticdir.root' : os.getcwd(),
                            'tools.staticdir.index' : "index.html",
                                'tools.staticdir.on' : True,
                                   'tools.staticdir.dir' : "public"}
                      }


    cherrypy.quickstart(HelloWorld(), '', config = cherrypy_config)
