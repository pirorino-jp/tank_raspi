# -*- coding: utf-8 -*-

import time
import sys
import atexit
import cv2
import logging as log
import datetime as dt
from time import sleep
import threading

class DetectProcess(threading.Thread):
  def __init__(self, org_frame, faces):
    super(DetectProcess, self).__init__()
    self.org_frame = org_frame
    self.faces = faces
    self.ratio = 3
    # 顔検出に使う特徴量ファイルの指定
    self.cascPath = '/usr/share/opencv/haarcascades/haarcascade_frontalface_alt_tree.xml'
    self.faceCascade = cv2.CascadeClassifier(self.cascPath)

    #スレッドの作成と開始
    self.thread = threading.Thread(target = self.target)
    self.thread.start()

  def target(self):
    shape = self.org_frame.shape

    # 処理高速化のために画像サイズを小さくする（後述:詳細1）

    # print("ratio:"+str(self.ratio))
    frame = cv2.resize(self.org_frame, (int(shape[1]/self.ratio),int(shape[0]/self.ratio)))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 顔の検出
    detectedFaces = self.faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        # 画像サイズの小さくしたので走査するwindowも同様の割合で小さくする（後述:詳細1）
        minSize=(int(30/self.ratio), int(30/self.ratio))
    )
    self.faces[:] = detectedFaces

class image_detect:
  '''
  Videocaptureと認識を行うためのクラス。
  '''
  def __init__( self ):

    # ログの出力
    log.basicConfig(filename='webcam.log',level=log.INFO)

    # もろもろ初期化
    self.video_capture = cv2.VideoCapture(0)
    # self.anterior = 0
    self.shot_dense = 0.7
    self.considerable_frames = 7
    self.prev_faces = []
    self.prev_shot = None
    # 画像サイズを小さくするための割合を設定（後述:詳細1）
    self.ratio = 3
    self.count = 0
    self.deco_pattern = 0
    self.faces = []
    self.framecount = 10
    cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Video',480,320)
    cv2.moveWindow('Video',50,50)
    # self.org_frame = org_frame
    # self.faces = faces
    print('video capture instanciated')

    #スレッドの作成と開始
    self.stop_event = threading.Event() #停止させるかのフラグ
    self.thread = threading.Thread(target = self.target)
    self.thread.start()

  def target(self):
    print('capture started')
    while not self.stop_event.is_set():
        # 動画の読み込みに失敗した場合
        # print('image_detect.py video_capture:'+str(self.ratio))
        if not self.video_capture.isOpened():
            print('Unable to load camera.')
            sleep(20)
            break
    
        # 動画の読み込みに成功した場合
        # 読み込んだ動画を1フレームづつ読み込む
        ret, org_frame = self.video_capture.read()
        cv2.imshow('Video', org_frame)
        # cv2.waitKey(0)

        # フレームカウントずつ顔認識を行う
        if self.count == self.framecount:
            thread = DetectProcess(org_frame, self.faces)
            thread.start()
            self.count = 0
    
            print(self.prev_faces, self.prev_shot)
    
            # 顔が検出されるたびに連続で撮影されないための工夫（後述:詳細2）
            # prev_shot is None -> 初回のデータ格納   seconds>3 -> 顔検出不感タイム の指定（2週目以降の処理）
            if self.prev_shot is None or (dt.datetime.now() - prev_shot).seconds > 3:
                self.prev_faces.append(len(self.faces))
                if len(self.prev_faces) > self.considerable_frames:
                    drops = len(self.prev_faces) - self.considerable_frames
                    # prev_facesのリストの先頭からdrops分だけ要素を削除したlist を返す（05を超えた要素で古いものから削除していく）
                    # prev_facesは常に05の要素数を保つ
                    self.prev_faces = self.prev_faces[drops:]
                # その05の要素数のうち、0以上の数が全要素数(=05)のどれくらいの割合を占めるかチェック
                dense = sum([1 for i in self.prev_faces if i > 0]) / float(len(self.prev_faces))
    
                # prev_facesに05よりも多くの要素が格納されようとしたとき
                if len(self.prev_faces) >= self.considerable_frames and dense >= self.shot_dense:
                    # subprocess.call("aplay cheese.wav", shell=True)
                    print('shot:',str(dt.datetime.now()))
                    save_fig_name = '{}.jpg'.format(dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
                    save_fig_full = '/home/pi/raspi_tank/save_fig/{}'.format(save_fig_name)
                    # 保存
                    cv2.imwrite(save_fig_full,org_frame) # ファイル保存
    
                    # thread = FileUpload(save_fig_name,save_fig_full)
                    # thread.start()
    
                    self.prev_faces = []
                    self.prev_shot = dt.datetime.now()
                    cv2.destroyWindow('shot_image')
    
                    cv2.namedWindow('shot_image', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('shot_image',640,480)
                    cv2.moveWindow('shot_image',100,600)
                    cv2.imshow('shot_image', org_frame)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()
        else:
            self.count += 1
    
        # 顔検出領域を四角で囲む
        for (x, y, w, h) in self.faces:
            x_ = x*self.ratio
            y_ = y*self.ratio
            x_w_ = (x+w)*self.ratio
            y_h_ = (y+h)*self.ratio
            cv2.rectangle(org_frame, (x_, y_), (x_w_, y_h_), (0, 255, 0), 2)

        # 接続しているモニターにリアルタイムで画像を描写する（カメラで撮っている動画を表示する）

        # print('refresh Video')
        cv2.imshow('Video', org_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    def stop(self):
        """スレッドを停止させる"""
        org_frame.release()
        cv2.destroyAllWindows()
        self.stop_event.set()
        self.thread.join()    #スレッドが停止するのを待つ

if __name__ == "__main__":

    pass

