# Copyright (c) 2020 by xfangfang. All Rights Reserved.

import pigpio
import time
import threading


class Servo():
    def __init__(self, pin_h, pin_v):
        self.horizontal_angle = 90
        self.vertical_angle = 90
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("pi gpio not connected")
            exit()
        self._pin_h = pin_h
        self._pin_v = pin_v
        self.vertical_stop_event = threading.Event()
        self.horizontal_stop_event = threading.Event()

        self.freemove_running = False
        self.freemove_stop_event = threading.Event()
        self.startFreeMoveThread()

    def test(self):
        self.set_horizontal_angle(90)
        self.set_vertical_angle(90)
        time.sleep(0.02)
        for i in range(90,181,1):
            self.set_horizontal_angle(i)
            self.set_vertical_angle(i)
            time.sleep(0.01)
        for i in range(180,89,-1):
            self.set_horizontal_angle(i)
            self.set_vertical_angle(i)
            time.sleep(0.01)
        self.stop()

    def vertical(self, up):
        def run(up):
            self.vertical_stop_event.clear()
            if up:
                while self.vertical_angle <= 180:
                    if self.vertical_stop_event.isSet():
                        break;
                    self.set_vertical_angle(self.vertical_angle + 0.5)
                    time.sleep(0.01)
            else:
                while self.vertical_angle >= 0:
                    if self.vertical_stop_event.isSet():
                        break;
                    self.set_vertical_angle(self.vertical_angle - 0.5)
                    time.sleep(0.01)
            self.stopVertical()
            self.vertical_stop_event.clear()

        threading.Thread(target=run, args=(up,)).start()

    def horizontal(self, left):
        def run(left):
            self.horizontal_stop_event.clear()
            if left:
                while self.horizontal_angle >= 0:
                    if self.horizontal_stop_event.isSet():
                        break;
                    self.set_horizontal_angle(self.horizontal_angle - 0.5)
                    time.sleep(0.01)
            else:
                while self.horizontal_angle <= 180:
                    if self.horizontal_stop_event.isSet():
                        break;
                    self.set_horizontal_angle(self.horizontal_angle + 0.5)
                    time.sleep(0.01)
            self.stopHorizontal()
            self.horizontal_stop_event.clear()

        threading.Thread(target=run, args=(left,)).start()

    def set_horizontal_angle(self, angle):
        if angle >= 0 and angle <= 180:
            self.horizontal_angle = angle
            self.pi.set_servo_pulsewidth(self._pin_h,
                                         self._angle_to_pulsewidth(angle))
    def set_vertical_angle(self, angle):
        if angle >= 0 and angle <= 180:
            self.vertical_angle = angle
            self.pi.set_servo_pulsewidth(self._pin_v,
                                         self._angle_to_pulsewidth(angle))

    def stopVerticalMove(self):
        self.vertical_stop_event.set()
        time.sleep(0.01)

    def stopVertical(self):
        self.pi.set_servo_pulsewidth(self._pin_v, 0)

    def stopHorizontal(self):
        self.pi.set_servo_pulsewidth(self._pin_h, 0)

    def stopHorizontalMove(self):
        self.horizontal_stop_event.set()
        time.sleep(0.01)

    def stop(self):
        self.pi.set_servo_pulsewidth(self._pin_v, 0)
        self.pi.set_servo_pulsewidth(self._pin_h, 0)

    def startFreeMoveThread(self):
        def run():
            while self.freemove_running:
                self.freemove_stop_event.wait()
                self.set_vertical_angle(self.vertical_angle)
                self.set_horizontal_angle(self.horizontal_angle)
        if not self.freemove_running:
            self.freemove_running = True
            self.freeMoveThread = threading.Thread(target=run, args=())
            self.freeMoveThread.start()

    def stopFreeMove(self):
        self.freemove_stop_event.clear()
        self.stop()

    def killFreeMoveThread(self):
        self.updateFreeMove(50,50)
        time.sleep(0.01)
        self.freemove_running = False
        self.freeMoveThread.join()
        self.stopFreeMove()

    def updateFreeMove(self, x, y):
        if not self.freemove_stop_event.isSet():
            self.freemove_stop_event.set()

        self.set_horizontal_angle(x*1.8)
        self.set_vertical_angle(y*1.8)

    def _angle_to_pulsewidth(self,angle):
        return 500 + angle*100.0/9

if __name__ == '__main__':

    servo = Servo(14,15)
    servo.test()


    servo.stop()
