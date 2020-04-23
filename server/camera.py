# Copyright (c) 2020 by xfangfang. All Rights Reserved.

import io
import time
import cherrypy
import picamera
from threading import Thread

from var import *


class CameraOutput(object):



    def __init__(self):
        self.stream = io.BytesIO()
        self.HEADER_FRAME = None
        self.IDR_FRAME = None

    def write(self, buf):
        # h264视频每帧的开始字节
        if buf.startswith(b'\x00\x00\x00\x01'):
            # 通过websocket广播此帧
            self.stream.seek(0)
            cherrypy.engine.publish('websocket-video-broadcast', self.stream.read())
            self.stream.seek(0)
            self.stream.truncate()

            # 储存关键帧（用于初始连接时提升视频加载速度）
            frame_type = buf[4] & 31
            if frame_type == 7:
                self.HEADER_FRAME = buf
            elif frame_type == 5:
                self.IDR_FRAME = buf

        self.stream.write(buf)

    def flush(self):
        logger.info('camera output end.')

class Camera(Thread):

    def __init__(self):
        super(Camera, self).__init__()
        logger.info("init camera")
        camera = picamera.PiCamera()
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMERATE
        camera.vflip = VFLIP
        camera.hflip = HFLIP
        self.camera = camera
        self.output = CameraOutput()
        self.stop_thread = False
        time.sleep(1)

    def run(self):
        # 详情见  https://picamera.readthedocs.io/en/release-1.13/api_camera.html#picamera.PiCamera.start_recording
        self.camera.start_recording(self.output,
                               format='h264',
                               profile='baseline',
                               intra_period = 30
                              )
        try:
            while not self.stop_thread:
                self.camera.wait_recording(1)
        except Exception:
            pass
        finally:
            logger.info('Stopping recording')
            self.camera.stop_recording()

    def stop(self):
        self.stop_thread = True
