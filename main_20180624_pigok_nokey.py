# coding:utf-8
# end of loop()
import cv2
import sys
import logging as logger
import datetime as dt
import time
from time import sleep
# import subprocess
import threading
import requests

import RPi.GPIO as GPIO
# import socket
# import spidev
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

import queue
import atexit

# customized function
import sg90p
# import distance_calc
import image_detect
import dcmotor

# sudo pip install git+https://github.com/Pithikos/python-websocket-server
# pip3 install spidev
# pip3 install tornado
# # raspi-config で spiを有効化

# ピン番号の割り当て方式を「GPIO番号」に設定
GPIO.setmode(GPIO.BOARD)
# GPIO.setwarnings(False)

# GPIO.cleanup()

# LED
 
ledPin1 = 13 # white LED
GPIO.setup(ledPin1,GPIO.OUT)

ledPin2 = 15 # yellow LED
GPIO.setup(ledPin2,GPIO.OUT)

# 周波数
clock = 50


# DCモーター
dcMotorPin1 = 8 # pin no,DC pin 26 motor to motor driver 9
dcMotorPin2 = 10 # pin no,DC pin 27 motor to motor driver 10
dcMotorPin3 = 16 # pin no,DC pin 33 motor to motor driver 11
dcMotorPin4 = 18 # pin no,DC pin 32 motor to motor driver 12
input_pwm = 50  # 

GPIO.setup(dcMotorPin1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin4, GPIO.OUT, initial=GPIO.LOW)

p1 = GPIO.PWM(dcMotorPin1, clock)
p2 = GPIO.PWM(dcMotorPin2, clock)
p3 = GPIO.PWM(dcMotorPin3, clock)
p4 = GPIO.PWM(dcMotorPin4, clock)

# 実際は0.5ms-2.4msの間で制御する。
# パルス全体は50Hzなので20msの幅があるから、
# 2.5% - 12.0%のDuty Cycleで制御する。
# 対応する角度は-90度-90度なので、
# Duty Cycleで2.5を指定したら-90度に軸が移動する

# p1.start(0)
# p2.start(0)
# p3.start(0)
# p4.start(0)

# 6v + to motor driver 1
# motor 1,2,3,4 to motor driver 2,3,4,5
# motor driver 7 to 5v ,6 to gnd,8 to gnd

# GP2Y0A21YKOF
# open SPI device 0.0
# spi = spidev.SpiDev()
# spi.open(0, 0)

# analogInPin = A0 # アナログ入力ピン（定数） SVP(ADC0) GPIO36 に刺す
# Vcc = 5.0        # 電源電圧（定数）
# ad               # AD値（変数）
# distarray = [0 for i in range(10)]     # 距離（平均算出用変数配列）
# dist             # 距離（変数）
# counter = 0      # 距離測定モジュール用
# arrayindex = 0   # 平均距離算出用配列index
# i = 0            # ソート用
# j = 0            # ソート用

localPort = 10000
host = '192.168.2.103'    # IPアドレス(ゲートウェイも兼ねる)
# host = '192.168.2.100'    # IPアドレス(ゲートウェイも兼ねる)

# this is line ca
ca = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDVDCCAjygAwIBAgIDAjRWMA0GCSqGSIb3DQEBBQUAMEIxCzAJBgNVBAYTAlVT\n" \
"MRYwFAYDVQQKEw1HZW9UcnVzdCBJbmMuMRswGQYDVQQDExJHZW9UcnVzdCBHbG9i\n" \
"YWwgQ0EwHhcNMDIwNTIxMDQwMDAwWhcNMjIwNTIxMDQwMDAwWjBCMQswCQYDVQQG\n" \
"EwJVUzEWMBQGA1UEChMNR2VvVHJ1c3QgSW5jLjEbMBkGA1UEAxMSR2VvVHJ1c3Qg\n" \
"R2xvYmFsIENBMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2swYYzD9\n" \
"9BcjGlZ+W988bDjkcbd4kdS8odhM+KhDtgPpTSEHCIjaWC9mOSm9BXiLnTjoBbdq\n" \

# -- caなので割愛 --

"tQWVYrmm3ok9Nns4d0iXrKYgjy6myQzCsplFAMfOEVEiIuCl6rYVSAlk6l5PdPcF\n" \
"PseKUgzbFbS9bZvlxrFUaKnjaZC2mqUPuLk/IH2uSrW4nOQdtqvmlKXBx4Ot2/Un\n" \
"hw4EbNX/3aBd7YdStysVAq45pmp06drE57xNNB6pXE0zX5IJL4hmXXeXxx12E6nV\n" \
"5fEWCRE11azbJHFwLJhWC9kXtNHjUStedejV0NxPNO3CBWaAocvmMw==\n" \
"-----END CERTIFICATE-----\n"

def start_servo(servo_no,value):
    print("start servo:"+servo_no+":"+str(value))
    print("before s1:currentdirection:"+str(s1.currentdirection()))
    print("before s2:currentdirection:"+str(s2.currentdirection()))

    if servo_no == "s1":
      print("servo s1 move from "+str(s1.currentdirection())+": end")
      if ((s1.currentdirection() + value) <= -100):
        direction = -100
      elif ((s1.currentdirection() + value) >= 100):
        direction = 100
      else:
        direction = s1.currentdirection() + value
      s1.setdirection( direction )

    elif servo_no == "s2":
      if ((s2.currentdirection() + value) <= -100):
        direction = -100
      elif ((s2.currentdirection() + value) >= 100):
        direction = 100
      else:
        direction = s2.currentdirection() + value
      s2.setdirection( direction )

    print("after s1:currentdirection:"+str(s1.currentdirection()))
    print("after s2:currentdirection:"+str(s2.currentdirection()))

# listen for incoming clients
def tank_order(msg):
    val = int(msg)
    # val == 119

    print("web socket message received:"+str(val)) 

    # white on
    if val == 119:
        print("val=119 led white on selected")
        GPIO.output(ledPin1, True)
        time.sleep(2)
        GPIO.output(ledPin1, False)

    # yellow on
    if val == 121:
        GPIO.output(ledPin2, True)
        time.sleep(2)
        GPIO.output(ledPin2, False)

    # move servo motor1 up
    if val == 114:
        print("val=114 servo s1 up selected")
        th_me = threading.Thread(target=start_servo, name="start_servo", args=("s1",20))
        th_me.start()

    # move servo motor1 up
    if val == 115:
        print("val=115 servo s1 up selected")
        th_me = threading.Thread(target=start_servo, name="start_servo", args=("s1",-20))
        th_me.start()
    # move servo motor2 up
    if val == 116:
        print("val=116 servo s2 up selected")
        th_me = threading.Thread(target=start_servo, name="start_servo", args=("s2",20))
        th_me.start()

    # move servo motor2 down
    if val == 117:
        print("val=117 servo s2 down selected")
        th_me = threading.Thread(target=start_servo, name="start_servo", args=("s2",-20))
        th_me.start()
    # move dc motor
    if val == 50:
        myqueue.put("forward,50")
        print("val=50 DCmotor forward end")

    if val == 52:
        myqueue.put("right,50")
        print("val=52 DCmotor right end")

    if val == 54:
        myqueue.put("left,50")
        print("val=54 left end")

    if val == 56:
        myqueue.put("backward,50")
        print("val=56 DCmotor backward end")

    if val == 53:
        myqueue.put("brake,50")
        print("val=53 DCmotor brake end")

    if val == 108:
        print("[HTTP] begin...\n")
        # configure traged server and url

        payload = {'message': distmessage} # 通知させたいメッセージ
        headers = {'Authorization': 'Bearer キーなので割愛'} # 発行したトークン
        r = requests.post('https://notify-api.line.me/api/notify', data=payload, headers=headers)

        # http.begin("https:#notify-api.line.me/api/notify/", ca) #Specify destination for HTTP request
        # print("[HTTP] POST...\n")
        # start connection and send HTTP header
        # http.addHeader("Content-Type", "application/x-www-form-urlencoded") #Specify content-type header
        # http.addHeader("Authorization", "Bearer キーなので割愛") #access token
        # httpResponseCode = http.POST("message=distance="+str(dist)+"cm") #Send the actual POST request
        # httpCode will be negative on error
        # if httpResponseCode>0:
        #     response = http.getstr()  #Get the response to the request
        #     print("Normal:"+str(httpResponseCode)+":"+response) #Print request answer
        # else 
        #     print("Error on sending POST:"+str(httpResponseCode))
        # http.end()
    
    # if val == 200:
    #     # for measuring distance
    #     th_dist.start()

    # if val == 201:
    #     # for measuring distance
    #     th_dist.stop()

    if val == 202:
        print("stop message received")
        GPIO.cleanup()
        # for stop websocket
        tornado.ioloop.IOLoop.instance().stop()
        # th_image.stop()
        sys.exit()

    print("packet process end")

class MyHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("connection opened")
        self.write_message("connection opened.")

    def on_close(self):
        print("connection closed")

    def on_message(self,message):
        print("Message arrived: {}".format(message))
        tank_order(message)
        self.write_message("message received. : " + message)

if __name__ == "__main__":

    print("setup start...")

    # サーボモーター
    # servo motor1
    motorPin1 = 18 # GPIO no,左からbrown=GND red=5v orange=IO18
    s1 = sg90p.sg90p(motorPin1,620,2470)

    # servo motor2
    motorPin2 = 20 # GPIO no,左からbrown=GND red=5v orange=IO20
    s2 = sg90p.sg90p(motorPin2,720,2500)

    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/",MyHandler)])
    server = tornado.httpserver.HTTPServer(app)
    server.listen(10000)

    # for measuring distance
    # th_dist = distance_calc.distance_calc()

    # for image recognition
    # ################### stop image detection
    # th_image = image_detect.image_detect()
    # ################### stop image detection

    # for motor drivenition
    # print("dcmotor start.")
    myqueue = queue.Queue()
    th_drive = dcmotor.dcmotor(myqueue)

    print("setup ready.")

    tornado.ioloop.IOLoop.instance().start()

    # PWM を停止
    p1.stop()
    p2.stop()
    p3.stop()
    p4.stop()

    # GPIO を解放
    GPIO.cleanup()
