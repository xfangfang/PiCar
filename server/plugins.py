# Copyright (c) 2020 by xfangfang. All Rights Reserved.


import json
from ws4py.manager import WebSocketManager
from ws4py.compat import py3k
from cherrypy.process import plugins

from camera import Camera, CameraOutput
from servo import Servo
from motor import Motor
from var import *


class MotorPlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        super(MotorPlugin, self).__init__(bus)
        logger.info('Initializing MotorPlugin')
        self.motor = Motor(L1,L2,R1,R2,INIT)

    def start(self):
        self.bus.subscribe('motor-update', self.motor.update)
        self.bus.subscribe('motor-stop', self.motor.stopMove)

    def stop(self):
        logger.info('Stoping MotorPlugin')
        self.bus.unsubscribe('motor-update', self.motor.update)
        self.bus.unsubscribe('motor-stop', self.motor.stopMove)
        self.motor.killMoveThread()

class ServoPlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        super(ServoPlugin, self).__init__(bus)
        logger.info('Initializing ServoPlugin')
        self.servo = Servo(PIN_SERVO_H, PIN_SERVO_V)

    def start(self):
        self.bus.subscribe('servo-test', self.servo.test)
        self.bus.subscribe('servo-updateFreeMove', self.servo.updateFreeMove)
        self.bus.subscribe('servo-stopFreeMove', self.servo.stopFreeMove)

    def stop(self):
        logger.info('Stoping ServoPlugin')
        self.bus.unsubscribe('servo-test', self.servo.test)
        self.bus.unsubscribe('servo-updateFreeMove', self.servo.updateFreeMove)
        self.bus.unsubscribe('servo-stopFreeMove', self.servo.stopFreeMove)
        self.servo.killFreeMoveThread()

# 用于视频连接的websocket客户端管理器
# 前端如果发送文本消息 REQUESTSTREAM 则被定义为请求视频资源
# 这时就会给这个websocket发送视频帧

# TODO: 当视频websocket未正常关闭时，VideoWebsocketManager 广播还会给这个client发送数据
# 因为广播是单线程的所以只有timeout（10s）后才能正常使用

class VideoWebSocketManager(WebSocketManager):
    def broadcast(self, message, binary=False):
        """
        Broadcasts the given message to all registered
        websockets, at the time of the call.
        Broadcast may fail on a given registered peer
        but this is silent as it's not the method's
        purpose to handle websocket's failures.
        """
        with self.lock:
            websockets = self.websockets.copy()
            if py3k:
                ws_iter = iter(websockets.values())
            else:
                ws_iter = websockets.itervalues()

        for ws in ws_iter:
            if not ws.terminated:
                try:
                    ws.send(message, binary)
                except:
                    fd = ws.sock.fileno()
                    with self.lock:
                        self.websockets.pop(fd, None)
                        self.poller.unregister(fd)
                    ws.terminate()


# 视频流广播
class BroadcastPlugin(plugins.SimplePlugin):
    def __init__(self, bus):
        super(BroadcastPlugin, self).__init__(bus)
        logger.info('Initializing camera')

        self.camera = Camera()
        self.manager = VideoWebSocketManager()

    def start(self):
        logger.info('Starting Broadcast Thread')
        self.camera.start()
        self.bus.subscribe('websocket-video-broadcast', self.broadcast)
        self.bus.subscribe('handle-video-websocket', self.handle)
        self.manager.start()

    def stop(self):
        self.bus.unsubscribe('handle-video-websocket', self.handle)
        self.bus.unsubscribe('websocket-video-broadcast', self.broadcast)
        logger.info('Stoping Broadcast Thread')
        self.camera.stop();
        self.camera.join();
        self.manager.stop()
        self.manager.join()


    def handle(self, ws_handler):
        logger.info("get new video client")
        self.manager.add(ws_handler)
        init = json.dumps({
          'action' : "init",
          'width'  : WIDTH,
          'height' : HEIGHT,
        })
        ws_handler.send(init)
        if self.camera.output.HEADER_FRAME:
            logger.info('send header frame')
            ws_handler.send(self.camera.output.HEADER_FRAME, binary=True)
        if self.camera.output.IDR_FRAME:
            logger.info('send idr frame')
            ws_handler.send(self.camera.output.IDR_FRAME, binary=True)

    def broadcast(self, message):
        self.manager.broadcast(message, binary=True)
