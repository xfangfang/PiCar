
# Abstract

以超低延迟控制和监控的树莓派视频小车。经测试，树莓派3b+：在局域网中可以达到平均20ms操作延迟；640*480、30 FPS 下180ms视频延迟。



# Hardware

### 清单

树莓派3b（or other pi with camera and 40pin gpio）、两个舵机、两个电机、一个L298n电机驱动版

### GPIO接线

左轮电机：L1 = 12，L2 = 16
右轮电机：R1 = 20，R2 = 21
水平舵机：PIN_SERVO_H = 14
垂直舵机：PIN_SERVO_V = 15

# How to run the server

sudo apt-get install pigpio python3-pigpio

pip3 install cherrypy ws4py


pigpiod


cd /home/pi

clone https://github.com/xfangfang/PiCar.git

cd /home/pi/PiCar/server

python3 server.py



# Run on boot

sudo nano /etc/rc.local

add line `sudo pigpiod` before `exit 0`


cd /home/pi/PiCar/server

sudo ln -s `pwd`/car.service /etc/systemd/system/car.service

sudo systemctl enable car.service

sudo systemctl start car.service

# How to use

访问 http://your-raspberry-pi-ip:6082 可以查看实时视频画面。

使用client构建的客户端代码即可在ios或android设备上使用


# Server code organization

| file                              | introduction                                                 |
| --------------------------------- | ------------------------------------------------------------ |
| var.py                            | 可以调整gpio引脚、视频的样式和帧数等内容                     |
| server.py                         | cherrypy（python的一个http服务端）的启动代码                 |
| plugins.py                        | 将自定义的服务（舵机、电机和摄像头）发布在cherrypy上，这样就可以优雅地通过websocket与硬件交互（发布订阅模式） |
| servo.py    motor.py    camera.py | 分别代表：舵机、电机和摄像头（与底层硬件交互，通过修改这三个文件可以将本程序移植到其他非树莓派设备上） |



# Best practices

Using frp for internet connection.


# Bugs

- There is something wrong when a websocket client unexpectedly going down.(It truns other websocket clients to be unavailable for 10 seconds)



# Reference
这两个使用了相同的实现思路，不过均为nodejs项目：

https://github.com/pimterry/raspivid-stream

https://github.com/131/h264-live-player

关于 PiCamera 如何传输视频流：

https://picamera.readthedocs.io/en/release-1.13/api_camera.html#picamera.PiCamera.start_recording

关于cherrypy 与 ws4py：

https://docs.cherrypy.org/en/latest/advanced.html#websocket-support

https://github.com/Lawouach/WebSocket-for-Python/blob/961c07ce16ce4eedc34ca1fdacd29442870feccc/ws4py/server/cherrypyserver.py#L286

https://github.com/Lawouach/WebSocket-for-Python/blob/961c07ce16ce4eedc34ca1fdacd29442870feccc/ws4py/manager.py#L196
