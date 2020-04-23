# Copyright (c) 2020 by xfangfang. All Rights Reserved.


import pigpio
import time
import threading

class Motor():
    '''
        L1 L2 R1 R2 为控制电机的GPIO端口
        INIT 为端口修正值，为两位二进制 为1说明要反转对应侧
        修正后前进时：L1 R1 为高电平端 L2 R2 为低电平端
    '''
    def __init__(self, L1, L2, R1, R2, INIT):
        self.left_control_1 = L1
        self.left_control_2 = L2
        self.right_control_1 = R1
        self.right_control_2 = R2
        self.init = INIT
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("pi gpio not connected")
            exit()
        if self.init & 2:
            self.left_control_1 = L2
            self.left_control_2 = L1
        if self.init & 1:
            self.right_control_1 = R2
            self.right_control_2 = R1

        self.v = 0;
        self.h = 0;

        self.pi.set_PWM_frequency(self.left_control_1, 50)
        self.pi.set_PWM_frequency(self.left_control_2, 50)
        self.pi.set_PWM_frequency(self.right_control_1, 50)
        self.pi.set_PWM_frequency(self.right_control_2, 50)
        self.pi.set_PWM_range(self.left_control_1, 50)
        self.pi.set_PWM_range(self.left_control_2, 50)
        self.pi.set_PWM_range(self.right_control_1, 50)
        self.pi.set_PWM_range(self.right_control_2, 50)

        self.stop()

        self.move_running = False
        self.move_stop_event = threading.Event()
        self.startMoveThread()

    def startMoveThread(self):
        def run():
            while self.move_running:
                self.move_stop_event.wait()
                self.setVH(self.v, self.h)
        if not self.move_running:
            self.move_running = True
            self.MoveThread = threading.Thread(target=run, args=())
            self.MoveThread.start()


    def setVH(self, v, h):
        v = v - 50
        h = h - 50
        h = h/2
        if v > 0:
            if h < 0:
                newl = v + h
                if newl < 0 : newl = 0
                self.pi.set_PWM_dutycycle(self.left_control_1, newl)
                self.pi.set_PWM_dutycycle(self.right_control_1, v)
            else:
                newr = v - h
                if newr < 0 : newr = 0
                self.pi.set_PWM_dutycycle(self.left_control_1, v)
                self.pi.set_PWM_dutycycle(self.right_control_1, newr)

            self.pi.set_PWM_dutycycle(self.left_control_2, 0)
            self.pi.set_PWM_dutycycle(self.right_control_2, 0)
        else:
            if h < 0:
                newl = -v + h
                if newl < 0 : newl = 0
                self.pi.set_PWM_dutycycle(self.left_control_2, newl)
                self.pi.set_PWM_dutycycle(self.right_control_2, -v)
            else:
                newr = -v - h
                if newr < 0 : newr = 0
                self.pi.set_PWM_dutycycle(self.left_control_2, -v)
                self.pi.set_PWM_dutycycle(self.right_control_2, newr)


            self.pi.set_PWM_dutycycle(self.left_control_1, 0)
            self.pi.set_PWM_dutycycle(self.right_control_1, 0)


    def killMoveThread(self):
        self.update(0,0)
        time.sleep(0.01)
        self.move_running = False
        self.MoveThread.join()
        self.stopMove()

    def stopMove(self):
        self.move_stop_event.clear()
        time.sleep(0.02)
        self.stop()

    def update(self, v, h):
        """
        v : 速度
        h : 水平
        """
        if not self.move_stop_event.isSet():
            self.move_stop_event.set()

        if v >= 0 and v <= 100:
            self.v = v
        if h >= 0 and h <= 100:
            self.h = h


    def stop(self):
        self.pi.set_PWM_dutycycle(self.left_control_1, 0)
        self.pi.set_PWM_dutycycle(self.left_control_2, 0)
        self.pi.set_PWM_dutycycle(self.right_control_1, 0)
        self.pi.set_PWM_dutycycle(self.right_control_2, 0)

if __name__ == '__main__':
    motor = Motor(L1,L2,R1,R2,INIT)
