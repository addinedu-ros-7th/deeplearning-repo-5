from importlib.metadata import requires

# from PyQt5.QtGui.QIcon import pixmap
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import os
import sys
import socket
import numpy as np
import time
import base64
import cv2
from yt_dlp import YoutubeDL
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

def Go2Home():
    SunnyMainWindow().show()

server_address = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
server_port = 8080  # 포트 번호

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

#["request000"]
def requestTCP(messages, img=np.zeros((28, 28, 3)), iscamera=False):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    if not iscamera:
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return response
    else:
        resize_frame = cv2.resize(img, dsize=(640, 640), interpolation=cv2.INTER_AREA)

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
        data = np.array(imgencode)
        stringData = base64.b64encode(data)
        length = str(len(stringData))

        # messages should be ["SendImage"]
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
        time.sleep(0.03)
        client_socket.sendall(length.encode('utf-8').ljust(64))
        client_socket.send(stringData)

        response = client_socket.recv(1024).decode('utf-8')
        client_socket.close()
        return response

current_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(current_dir, 'main.ui')
main = uic.loadUiType(ui_file_path)[0]

class SunnyMainWindow(QMainWindow, main):
    def __init__(self):
        super(SunnyMainWindow, self).__init__()
        self.cap = None
        self.setupUi(self)

        self.btn_home.setStyleSheet("""
            QPushButton {
                border-image: url('src/home.png');
                background-repeat: no-repeat;
                background-position: center;
                border: none; /* Remove border if not needed */
            }
        """)
        self.btn_camera.setStyleSheet("""
                    QPushButton {
                        border-image: url('src/VideoStabilization.png');
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none; /* Remove border if not needed */
                    }
                """)
        self.btn_profile.setStyleSheet("""
                    QPushButton {
                        border-image: url('src/User.jpg');
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none; /* Remove border if not needed */
                    }
                """)
        self.lb_logo.setStyleSheet("""
                    QLabel {
                        border-image: url('src/logo.jpg');
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none; /* Remove border if not needed */
                    }
                """)

        # 광고 영상은 바로 시작

        self.cap = cv2.VideoCapture(os.path.join(current_dir, 'src/ad_frame.mp4'))
        self.ad_timer = QTimer()
        self.ad_timer.start(30)  # Start the webcam timer
        self.ad_timer.timeout.connect(self.ad_frame)  # ㅊall update_frame function every time when timer is expired


        # function to run when button cilicked

        self.webcam_timer = QTimer()
        self.webcam_timer.timeout.connect(self.update_webcam_frame)  # ㅊall update_frame function every time when timer is expired

        self.btn_cardio.clicked.connect(self.start_webcam)
        self.btn_weighlifting.clicked.connect(self.start_webcam)
        self.btn_camera.clicked.connect(self.food_camera)
        # self.btn_home.clicked.connect(self.Go2Home)

        self.is_cardio_activate = False
        self.is_weightlifting_activate = False
        # self.is_profile_activate = False

    def start_webcam(self):
        self.cap = cv2.VideoCapture(0)
        self.webcam_timer.start(30)

    def update_webcam_frame(self):
        self.is_webcam_activate = True

        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (353, 563))
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        super().closeEvent(event)

    # def requestTCP(self):
    #     server_address = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
    #     server_port = 8080
    #
    #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     client_socket.connect((server_address, server_port))
    #
    #     # message 생성
    #     messages = []
    #     messages.append("Hello")  # KEY
    #     messages.append("My")
    #     messages.append("name")
    #     messages.append("is")
    #     messages.append("Donggyun")
    #
    #     client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
    #     response = client_socket.recv(1024).decode('utf-8')
    #     client_socket.close()
    #     print(response)

    def ad_frame(self):
        if not self.cap.isOpened():
            print("Video file not found or cannot be opened.")
            return

        ret, frame = self.cap.read()

        if not ret: # 다시 읽기
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (353, 563))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))
        QTimer.singleShot(15000, self.ad_frame)

    def food_camera(self):
        self.food_camera_window = SunnyFoodCamera()
        self.food_camera_window.show()

current_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(current_dir, 'food_camera.ui')
food_camera_window = uic.loadUiType(ui_file_path)[0]

class SunnyFoodCamera(QMainWindow, food_camera_window):
    def __init__(self):
        super(SunnyFoodCamera, self).__init__()
        self.cap = None
        self.setupUi(self)

        self.btn_home.setStyleSheet("""
                    QPushButton {
                        border-image: url('src/home.png');
                        background-repeat: no-repeat;
                        background-position: center;
                        border: none; /* Remove border if not needed */
                    }
                """)
        self.btn_camera.setStyleSheet("""
                            QPushButton {
                                border-image: url('src/VideoStabilization.png');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; /* Remove border if not needed */
                            }
                        """)
        self.btn_profile.setStyleSheet("""
                            QPushButton {
                                border-image: url('src/User.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; /* Remove border if not needed */
                            }
                        """)
        self.lb_logo.setStyleSheet("""
                            QLabel {
                                border-image: url('src/logo.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; /* Remove border if not needed */
                            }
                        """)
        self.btn_camera_shutter.setStyleSheet("""
                            QPushButton {
                                border-image: url('src/Aperture.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; /* Remove border if not needed */
                            }
                        """)

        self.btn_file.setStyleSheet("""
                                    QPushButton {
                                        border-image: url('src/Add_image.png');
                                        background-repeat: no-repeat;
                                        background-position: center;
                                        border: none; /* Remove border if not needed */
                                    }
                                """)
        # self.btn_home.clicked.connect(self.Go2Home)

        self.cap = cv2.VideoCapture(0)
        self.webcam_timer = QTimer()
        self.webcam_timer.start(30)
        self.webcam_timer.timeout.connect(self.webcam_frame)  # ㅊall update_frame function every time when timer is expired

        self.btn_camera_shutter.clicked.connect(self.take_photo)


    def webcam_frame(self):
        self.is_webcam_activate = True
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (393, 781))
        self.current_frame = frame
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    def take_photo(self):
        self.lb_shutter_effect.setStyleSheet("background-color: white;")
        QTimer.singleShot(200, lambda: self.lb_shutter_effect.setStyleSheet(""))

        # cv2.imwrite('sunny_food_photo2TCP.jpg', self.current_frame) # 저장 필요없음? MongoDB 사용

        messages = []
        messages.append("RequestDietAnalyze")
        re=requestTCP(messages, img=self.current_frame, iscamera=True)
        print(re)

if __name__ == '__main__':
    App = QApplication(sys.argv)
    myWindow = SunnyMainWindow()
    myWindow.show()
    sys.exit(App.exec())


#------------------