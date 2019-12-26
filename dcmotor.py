# -*- coding: utf-8 -*-
import queue
import sys
import threading
import RPi.GPIO as GPIO
import math

pwm_dict = { "rightmotor_f":0, "rightmotor_b":0, "leftmotor_f":0, "leftmotor_b":0 }
# DCモーター
# 周波数
clock = 50

dcMotorPin1 = 29 # DC pin 26 motor to motor driver 9
dcMotorPin2 = 31 # DC pin 27 motor to motor driver 10
dcMotorPin3 = 33 # DC pin 33 motor to motor driver 11
dcMotorPin4 = 35 # DC pin 32 motor to motor driver 12
    
# ピン番号の割り当て方式を「コネクタのピン番号」に設定
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(dcMotorPin1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dcMotorPin4, GPIO.OUT, initial=GPIO.LOW)

p1 = GPIO.PWM(dcMotorPin1, clock)
p2 = GPIO.PWM(dcMotorPin2, clock)
p3 = GPIO.PWM(dcMotorPin3, clock)
p4 = GPIO.PWM(dcMotorPin4, clock)

p1.start(0)
p2.start(0)
p3.start(0)
p4.start(0)

class dcmotor:

  def __init__( self ,myqueue ):
    #スレッドの作成と開始
    # 自動減速インターバル
    
    print("dcmotor start...")
    self.queue = myqueue
    self.dec_interval = 100
    self.count = 0
    self.thread = threading.Thread(target = self.target)
    self.thread.start()
    
  def target(self):
    # while self.count < 1000:
    while True:
        if self.queue.qsize() == 0:
            """queueにデータが入っていない"""
            pass
        else:
            """queueにデータが入っている"""
            param = self.queue.get().split(',')
            print(str(param))
            print("before:",self.count,pwm_dict)
            if len(param) != 2:
                print("queue message error:"+str(param))
                break
            """急な反転は無視する"""
            if ( param[0] == "forword" and ( pwm_dict["leftmotor_b"] > 0 or pwm_dict["rightmotor_b"] > 0) ):
                pass
            elif ( param[0] == "backword" and ( pwm_dict["leftmotor_f"] > 0 or pwm_dict["rightmotor_f"] > 0) ):
                pass
            else:
                """queueを処理して速度を加算"""
                if param[0] == "forward":
                    """前進"""
                    print("param[0]=forward")
                    if pwm_dict["rightmotor_f"] > pwm_dict["leftmotor_f"]:
                        print("right_f>left_f")
                        pwm_dict["rightmotor_f"] = pwm_dict["rightmotor_f"] + int(param[1])
                        pwm_dict["leftmotor_f"] = pwm_dict["rightmotor_f"]
                    else:
                        print("right_f<=left_f")
                        pwm_dict["leftmotor_f"] = pwm_dict["leftmotor_f"] + int(param[1])
                        pwm_dict["rightmotor_f"] = pwm_dict["leftmotor_f"]
                if param[0] == "left":
                    """左へ"""
                    pwm_dict["rightmotor_f"] = pwm_dict["rightmotor_f"] + int(param[1])
                    if pwm_dict["rightmotor_f"] > 100:
                        pwm_dict["rightmotor_f"] = 100
                    pwm_dict["leftmotor_f"] = pwm_dict["rightmotor_f"] // 2
                if param[0] == "right":
                    """右へ"""
                    pwm_dict["leftmotor_f"] = pwm_dict["leftmotor_f"] + int(param[1])
                    if pwm_dict["leftmotor_f"] > 100:
                        pwm_dict["leftmotor_f"] = 100
                    pwm_dict["rightmotor_f"] = pwm_dict["leftmotor_f"] // 2
                if param[0] == "backward":
                    """後へ"""
                    if ( pwm_dict["rightmotor_f"] == 0 ) and ( pwm_dict["leftmotor_f"] == 0 ):
                        if pwm_dict["rightmotor_b"] > pwm_dict["leftmotor_b"]:
                            pwm_dict["rightmotor_b"] = pwm_dict["rightmotor_b"] + int(param[1])
                            pwm_dict["leftmotor_b"] = pwm_dict["rightmotor_b"]
                        else:
                            pwm_dict["leftmotor_b"] = pwm_dict["leftmotor_b"] + int(param[1])
                            pwm_dict["rightmotor_b"] = pwm_dict["leftmotor_b"]

                """加速が100を越えたら100にする"""
                if pwm_dict["rightmotor_f"] > 100:
                    pwm_dict["rightmotor_f"] = 100
                if pwm_dict["rightmotor_b"] > 100:
                    pwm_dict["rightmotor_b"] = 100
                if pwm_dict["leftmotor_f"] > 100:
                    pwm_dict["leftmotor_f"] = 100
                if pwm_dict["leftmotor_b"] > 100:
                    pwm_dict["leftmotor_b"] = 100
                print("after:",self.count,pwm_dict)

        """定期的に自動減速"""
        if self.count % self.dec_interval == 0:
            if pwm_dict["leftmotor_f"] > 0:
                pwm_dict["leftmotor_f"] = pwm_dict["leftmotor_f"] - 10
                if pwm_dict["leftmotor_f"] < 0:
                    pwm_dict["leftmotor_f"] = 0
            if pwm_dict["leftmotor_b"] > 0:
                pwm_dict["leftmotor_b"] = pwm_dict["leftmotor_b"] - 10
                if pwm_dict["leftmotor_b"] < 0:
                    pwm_dict["leftmotor_b"] = 0
            if pwm_dict["rightmotor_f"] > 0:
                pwm_dict["rightmotor_f"] = pwm_dict["rightmotor_f"] - 10
                if pwm_dict["rightmotor_f"] < 0:
                  pwm_dict["rightmotor_f"] = 0
            if pwm_dict["rightmotor_b"] > 0:
                pwm_dict["rightmotor_b"] = pwm_dict["rightmotor_b"] - 10
                if pwm_dict["rightmotor_b"] < 0:
                    pwm_dict["rightmotor_b"] = 0

        self.count = self.count + 1

        """DCモーターを動かす"""
        p1.ChangeDutyCycle(pwm_dict["rightmotor_f"])
        GPIO.output(dcMotorPin1, math.ceil(int(pwm_dict["rightmotor_f"])))
        p2.ChangeDutyCycle(pwm_dict["rightmotor_b"])
        GPIO.output(dcMotorPin2, math.ceil(int(pwm_dict["rightmotor_b"])))
        p3.ChangeDutyCycle(pwm_dict["leftmotor_f"])
        GPIO.output(dcMotorPin3, math.ceil(int(pwm_dict["leftmotor_f"])))
        p4.ChangeDutyCycle(pwm_dict["leftmotor_b"])
        GPIO.output(dcMotorPin4, math.ceil(int(pwm_dict["leftmotor_b"])))

  def stop(self):
      """スレッドを停止させる"""
      self.stop_event.set()
      self.thread.join()    #スレッドが停止するのを待つ

if __name__ == "__main__":
    pass

