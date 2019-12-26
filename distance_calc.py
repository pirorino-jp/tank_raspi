import sys
import logging as logger
import datetime as dt
import time
import threading
import spidev
import RPi.GPIO as GPIO

# GP2Y0A21YKOF
# open SPI device 0.0
spi = spidev.SpiDev()
spi.open(0, 0)

# analogInPin = A0 # アナログ入力ピン（定数） SVP(ADC0) GPIO36 に刺す
Vcc = 5.0        # 電源電圧（定数）
# ad               # AD値（変数）
distarray = [0 for i in range(10)]     # 距離（平均算出用変数配列）
# dist             # 距離（変数）
# counter = 0      # 距離測定モジュール用
    
class distance_calc:
    def __init__(self):
        self.stop_event = threading.Event() #停止させるかのフラグ
        #スレッドの作成と開始
        self.thread = threading.Thread(target = self.target)
        self.thread.start()

    def target(self):
        counter = 0      # 距離測定用カウンター
        arrayindex = 0   # 平均距離算出用配列index
        while not self.stop_event.is_set():
            i = 0
            j = 0
            counter = counter + 1
            # distance
            if counter > 50000:
                # print("dist counter:"+str(counter))
                resp = spi.xfer2([0x68, 0x00])
                value = (resp[0] * 256 + resp[1]) & 0x3ff
                volt = value * Vcc / 1023
                if volt > 0:
                    dist = ( 18.679 / volt ) -4.774
                else:
                    dist = 0
                if arrayindex > 8:
                    # calcurate avarage distance
                    distarray[9] = dist
                    print("distarray:"+str(distarray[0])+":"+str(distarray[1])+":"+str(distarray[2])+":"+str(distarray[3])+":"+str(distarray[4])+":"+str(distarray[5])+":"+str(distarray[6])+":"+str(distarray[7])+":"+str(distarray[8])+":"+str(distarray[9])+":")
                    dist = (distarray[0]+distarray[1]+distarray[2]+distarray[3]+distarray[4]+distarray[5]+distarray[6]+distarray[7]+distarray[8]+distarray[9])/10
                    # print("average:"+str(dist))

                    # bubble sort
                    for i in range(len(distarray)):
                        for j in range(len(distarray)-1, i, -1):
                            if distarray[j] < distarray[j-1]:
                                distarray[j],distarray[j-1] = distarray[j-1],distarray[j]
                    dist = distarray[5]
                    # print("median:"+str(dist))
                    distmessage = "Distance:"+str(dist)+"cm"
                    print("Distance:"+str(dist)+"cm")
                    arrayindex = 0
                else:
                    distarray[arrayindex] = dist
                    arrayindex = arrayindex + 1
                    # print("arrayindex:"+str(arrayindex))
                counter = 0

    def stop(self):
        """スレッドを停止させる"""
        self.stop_event.set()
        self.thread.join()    #スレッドが停止するのを待つ


if __name__ == "__main__":

    pass
