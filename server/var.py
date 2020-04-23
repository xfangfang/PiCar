# Copyright (c) 2020 by xfangfang. All Rights Reserved.

import logging
from ws4py import configure_logger

logger = configure_logger(stdout=True, level=logging.INFO, filepath='car.log')

# 电机GPIO引脚
L1 = 12
L2 = 16
R1 = 20
R2 = 21
## 二进制数用来翻转电机 当电机接线接反时无需重新接线 修改此值即可
INIT = int('01',2)

# 两个舵机端口号
# 水平舵机
PIN_SERVO_H = 14
# 垂直舵机
PIN_SERVO_V = 15

# 服务端口号
PORT = 6082

# 视频设置
WIDTH = 640
HEIGHT = 480
# FPS
FRAMERATE = 30
# 是否翻转视频
VFLIP = False
HFLIP = False
