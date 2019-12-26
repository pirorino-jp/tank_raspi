# -*- coding: utf-8 -*-

import pigpio
import time
import sys
import atexit

class sg90p:
  '''
  Servo Motor SG90をpigpioで簡単に使えるようにするためのクラス。
  '''
  direction = 0
  def __init__( self, pin, start_value, end_value ):
    '''
    初期化する。
    pin : GPIO番号。
    direction : 初期の向き。 -100(一番左) から 100(一番右)までの場所を整数値で指定する。
    '''
    print("sg90p.init called")
    self.pi = pigpio.pi()
    self.pin = int( pin )
    atexit.register( self.cleanup )
    self.start_value = int( start_value)
    self.end_value = int( end_value)
    
    self.pi.set_servo_pulsewidth(self.pin,((self.end_value - self.start_value) / 2 ) + self.start_value )

  def stop( self ):
    '''
    単純に停止する
    '''
    self.pi.stop()
 
  def cleanup( self ):
    '''
    最後は正面に戻して終了する
    '''
    print("self.cleanup called")
    self.pi.set_servo_pulsewidth(self.pin,((self.end_value - self.start_value) / 2 ) + self.start_value )
    time.sleep(1.0)
    self.pi.stop()

  def currentdirection( self ):
    '''
    現在のSG90の向きを返す。
    '''
    return self.direction

  def henkan( self, value ):
    '''
    set_servo_pulsewidthに渡すための値を計算する。
    -100から100のfloat値を入力して、値を返す。
    '''
    score = 100 + value

    return ((self.end_value - self.start_value ) / 200 * score ) + self.start_value

  def setdirection( self, direction ):
    '''
    SG90の向きを変える。
    direction : -100 - 100 の整数値
    speed     : 変化量
    '''
    print("set direction:"+str(direction))
    print("pin:" + str(self.pin) + " henkan call:" + str(self.henkan(direction)))
    self.pi.set_servo_pulsewidth( self.pin, self.henkan( direction ) )
    time.sleep(0.5) 
    self.direction = direction

if __name__ == "__main__":
    pass

