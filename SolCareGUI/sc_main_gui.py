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
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
import hashlib
import select
import mysql.connector

Current_User_ID = 0

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# # AI Server
# AI_SERVER = 1
# AI_ADDR = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
# AI_PORT = 8081       # 포트 번호

# AI_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AI_client_socket.connect((AI_ADDR, AI_PORT))

# webcam_request_cnt = 0

# # Main Server
# MAIN_SERVER = 0
# MAIN_ADDR = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
# MAIN_PORT = 8083       # 포트 번호
# def requestTCP(messages, img=np.zeros((28, 28, 3)), iscamera=False, reciver=MAIN_SERVER):
#     if reciver == MAIN_SERVER:
#         addr = MAIN_ADDR
#         port = MAIN_PORT
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client_socket.connect((addr, port))

#     elif reciver == AI_SERVER:
#         addr = MAIN_ADDR
#         port = MAIN_PORT
#         client_socket = AI_client_socket

#     if not iscamera:
#         client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#     else:
#         resize_frame = cv2.resize(img, dsize=(320, 320), interpolation=cv2.INTER_AREA)
#         encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
#         _, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
#         data = np.array(imgencode)
#         stringData = base64.b64encode(data)
#         length = str(len(stringData))
#         # messages should be ["SendImage"]
#         client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#         time.sleep(0.03)
#         client_socket.sendall(length.encode('utf-8').ljust(64))
#         client_socket.send(stringData)

#     ready = select.select([client_socket], [], [], 2)
#     response = "Error"
#     if ready[0]:
#         response = client_socket.recv(1024).decode('utf-8')
#         if reciver == MAIN_SERVER:
#             client_socket.close()
#     return response

# def sendTCP(messages, img=np.zeros((28, 28, 3)), iscamera=False, reciver=MAIN_SERVER):
#     if reciver == MAIN_SERVER:
#         addr = MAIN_ADDR
#         port = MAIN_PORT
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client_socket.connect((addr, port))

#     elif reciver == AI_SERVER:
#         addr = MAIN_ADDR
#         port = MAIN_PORT
#         client_socket = AI_client_socket

#     if not iscamera:
#         client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#     else:
#         resize_frame = cv2.resize(img, dsize=(320, 320), interpolation=cv2.INTER_AREA)
#         encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
#         _, imgencode = cv2.imencode('.jpg', resize_frame, encode_param)
#         data = np.array(imgencode)
#         stringData = base64.b64encode(data)
#         length = str(len(stringData))
#         # messages should be ["SendImage"]
#         client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#         time.sleep(0.03)
#         client_socket.sendall(length.encode('utf-8').ljust(64))
#         client_socket.send(stringData)

#     if reciver == MAIN_SERVER:
#         client_socket.close()

current_dir = os.path.dirname(os.path.abspath(__file__))
login = uic.loadUiType(os.path.join(current_dir, 'login.ui'))[0]
profile = uic.loadUiType(os.path.join(current_dir, 'profile.ui'))[0]
createaccount = uic.loadUiType(os.path.join(current_dir, 'createaccount.ui'))[0]
main = uic.loadUiType(os.path.join(current_dir, 'main.ui'))[0]
food_camera = uic.loadUiType(os.path.join(current_dir, 'food_camera.ui'))[0]
analytics = uic.loadUiType(os.path.join(current_dir, 'analytics.ui'))[0]
security = uic.loadUiType(os.path.join(current_dir, 'security.ui'))[0]
analytics1 = uic.loadUiType(os.path.join(current_dir, 'analytics1.ui'))[0]

class ControlTower:
    def __init__(self):
        self.current_window = None  
    def showwindow(self, windowtoopen):
        if self.current_window:
            self.current_window.hide()
        
        self.current_window = windowtoopen(self)
        self.current_window.show()

class SunnyLoginWindow(QMainWindow, login):
    def __init__(self, control):
        super(SunnyLoginWindow, self).__init__()
        self.control = control
        self.setupUi(self)

        self.lb_logo.setStyleSheet("""
                            QLabel {
                                border-image: url('SolCareGUI/img/logo.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; 
                            }
                        """)

        self.le_UserID.addAction(QIcon('SolCareGUI/img/UserID.png'), QLineEdit.ActionPosition.LeadingPosition)
        self.le_UserPassword.addAction(QIcon('SolCareGUI/img/UserPassword.png'), QLineEdit.ActionPosition.LeadingPosition)


        # self.btn_login.clicked.connect(self.SendUserInfo)
        self.btn_login.clicked.connect(lambda: self.control.showwindow(SunnyMainWindow))

        self.btn_create.clicked.connect(lambda: self.control.showwindow(SunnyCreateAccountWindow))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 동균님에게 전달
    def CheckUserInfo(self, user_info):
        global Current_User_ID
        db = mysql.connector.connect(
            host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
            user="ks",
            password="1234",
            database="nahonlab"
        )
        input_username = user_info[0]
        input_password = user_info[1]
        password_hash = hashlib.sha256(input_password.encode("utf-8")).hexdigest()
        print(password_hash)

        cursor = db.cursor()
        query = """
        SELECT user_id, nickname, pw FROM user_signup
        WHERE nickname = %s AND pw = %s
        """
        cursor.execute(query, (input_username, password_hash))

        result = cursor.fetchone()

        if result:
            Current_User_ID = result[0]
            print(Current_User_ID)
            return True # or 0 send TCP
        else:
            return False # or 1send TCP

        cursor.close()
        db.close()

    def SendUserInfo(self):
        user_info = []
        user_id = self.le_UserID.text()
        user_password = self.le_UserPassword.text()
        user_info.append(user_id)
        user_info.append(user_password)

        print(user_info)
        
        access_result = self.CheckUserInfo(user_info)

        # requestTCP(user_id) # send User ID 
        # requestTCP(user_password) # send User PW

        if access_result == True:
            QMessageBox.warning(self, 'Log In Success',"Log In Success")
            self.control.showwindow(SunnyMainWindow)
        else:
            QMessageBox.warning(self, 'Warning',"User Info Not Exist Please SIGH UP!!!")

class SunnyCreateAccountWindow(QMainWindow, createaccount):
    def __init__(self, control):
        super(SunnyCreateAccountWindow, self).__init__()
        self.control = control
        self.setupUi(self)

        self.lb_logo.setStyleSheet("""
                            QLabel {
                                border-image: url('SolCareGUI/img/logo.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; 
                            }
                        """)
        self.le_NewUserID.addAction(QIcon('SolCareGUI/img/UserID.png'), QLineEdit.ActionPosition.LeadingPosition)
        self.le_NewUserPassword.addAction(QIcon('SolCareGUI/img/UserPassword.png'), QLineEdit.ActionPosition.LeadingPosition)

        self.btn_create.clicked.connect(self.RegisterUser)
        self.btn_cancle.clicked.connect(lambda: self.control.showwindow(SunnyLoginWindow))
        self.cb_NewUserSex.addItems(['남자', '여자'])

    def RegisterUser(self):
        user_login_info = []
        new_user_info = []

        new_user_id = self.le_NewUserID.text()
        new_user_password = self.le_NewUserPassword.text()
        new_user_password_hashed = hashlib.sha256(new_user_password.encode("utf-8")).hexdigest()

        user_login_info.append(new_user_id)
        user_login_info.append(new_user_password_hashed)
        
        new_user_name = self.le_NewUserName.text()
        new_user_sex = self.cb_NewUserSex.currentText()
        new_user_birthday = self.de_NewUserBirthday.text()
        new_user_phone = self.le_NewUserPhone.text()
        new_user_emer_phone = self.le_NewUserEmerPhone.text()

        new_user_info.append(new_user_name)
        new_user_info.append(new_user_sex)
        new_user_info.append(new_user_birthday)
        new_user_info.append(new_user_phone)
        new_user_info.append(new_user_emer_phone)

        db = mysql.connector.connect(
            host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
            user="ks",
            password="1234",
            database="nahonlab"
        )
        cursor = db.cursor()
        
        query = "SELECT nickname FROM user_signup WHERE nickname = %s"
        cursor.execute(query, (user_login_info[0],))
        
        result = cursor.fetchone()   

        if result:
            nickname_status =  False  # 있으면 안됨
        else:
            nickname_status = True

        if nickname_status == True:
            insert_signup_query = """
            INSERT INTO user_signup (nickname, pw)
            VALUES (%s, %s)
            """
            cursor.execute(insert_signup_query, (user_login_info[0], user_login_info[1]))

            user_id = cursor.lastrowid

            insert_user_info_query = """
            INSERT INTO user_info ( name, sex, birthday, phone, emergency_contact)
            VALUES ( %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_user_info_query, ( new_user_info[0], new_user_info[1], new_user_info[2], new_user_info[3], new_user_info[4]))

            db.commit() 
            cursor.close() 
            db.close()  
        else:
            QMessageBox.warning(self, 'Warning',"Please Use Different ID")


        # requestTCP(user_id) # send User ID 



    
    def RegisterDB(self):
        nickname_available = self.CheckNickname(self.user_login_info)

class SunnyMainWindow(QMainWindow, main):
    def __init__(self, control):
        super(SunnyMainWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)

        # Navigation bar Design Setup
        self.btn_home.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/home.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_camera.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/VideoStabilization.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_profile.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/User.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.lb_webcam.setStyleSheet("""
                QLabel {
                    border-radius: 15px
                }
                """)
        # Ad video
        self.cap = cv2.VideoCapture('SolCareGUI/img/ad_frame.mp4')
        self.ad_timer = QTimer()
        self.ad_timer.start(30)  #No trigger, JUST PLAY !!
        self.ad_timer.timeout.connect(self.ad_frame)  # ㅊall update_frame function every time when timer is expired


        # auto function to run when button clicked (timeout!!)
        self.webcam_gui_timer = QTimer()
        self.webcam_gui_timer.timeout.connect(self.update_webcam_frame_gui)  # ㅊall update_frame function every time when timer is expired

        self.webcam_tcp_timer = QTimer()
        # self.webcam_tcp_timer.timeout.connect(self.send_webcam_frame_tcp)


        self.btn_cardio.clicked.connect(self.start_webcam)
        self.btn_weighlifting.clicked.connect(self.start_webcam)

        #Page Move
        self.btn_home.clicked.connect(lambda: (self.closeCam(), self.control.showwindow(SunnyMainWindow)))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))


        self.is_cardio_activate = False
        self.is_weightlifting_activate = False
        # self.is_profile_activate = False


    # def update_webcam_frame(self):
    #     global webcam_request_cnt

    #     self.is_webcam_activate = True

    #     ret, frame = self.cap.read()
    #     if ret:
    #         rgb_frame = cv2.resize(frame, (353, 563))
    #         rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2RGB)
    #         h, w, ch = rgb_frame.shape
    #         bytes_per_line = ch * w
    #         qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

    #         self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    #         messages = ["RequestExResult"]
    #         # re=requestTCP(messages, img=frame, iscamera=True, reciver=AI_SERVER)
    #         try:
    #             re = requestTCP(messages=messages, img=frame, iscamera=True, reciver=AI_SERVER)
    #         except Exception as e:
    #             print(e)
    #             re = "Error"
    #         print(re)
    #         webcam_request_cnt = 0

    def start_webcam(self):
        mobilecamIP = 0
        self.cap = cv2.VideoCapture(mobilecamIP)
        self.webcam_gui_timer.start(33) 
        self.webcam_tcp_timer.start(100)  

    def update_webcam_frame_gui(self):
        ret, frame = self.cap.read()
        if ret:
            frame_resized = cv2.resize(frame, (353, 563))
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    # def send_webcam_frame_tcp(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         messages = ["RequestExResult"]
    #         try:
    #             response = requestTCP(messages=messages, img=frame, iscamera=True, reciver=AI_SERVER)
    #             print(response)
    #         except Exception as e:
    #             print(f"TCP Error: {e}")   
            
    def closeCam(self):
        if  self.cap.isOpened():
            self.cap.release()  
            self.webcam_gui_timer.stop() 
            self.webcam_tcp_timer.stop() 
    def ad_frame(self):
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

class SunnyFoodCameraWindow(QMainWindow, food_camera):
    def __init__(self, control):
        super(SunnyFoodCameraWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Navigation bar Design Setup
        self.btn_home.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/home.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_camera.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/VideoStabilization.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_profile.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/User.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.btn_camera_shutter.setStyleSheet("""
                            QPushButton {
                                border-image: url('SolCareGUI/img/Aperture.jpg');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; 
                            }
                        """)
        self.btn_file.setStyleSheet("""
                                    QPushButton {
                                        border-image: url('SolCareGUI/img/Add_image.png');
                                        background-repeat: no-repeat;
                                        background-position: center;
                                        border: none; 
                                    }
                                """)
        
        mobilecamIP = 0
        self.cap = cv2.VideoCapture(mobilecamIP)

        self.webcam_timer = QTimer()
        self.webcam_timer.start(33)
        self.webcam_timer.timeout.connect(self.webcam_frame)  # ㅊall update_frame function every time when timer is expired

        self.btn_camera_shutter.clicked.connect(self.take_photo)

        self.btn_home.clicked.connect(lambda: self.control.showwindow(SunnyMainWindow))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))


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

        # cv2.imwrite('sunny_food_photo2TCP.jpg', self.current_frame) # 저장 필요없음?

        messages = ["RequestDietAnalyze"]
        re=requestTCP(messages, img=self.current_frame, iscamera=True)
        print(re)

class SunnyProfileWindow(QMainWindow, profile):
    def __init__(self, control):
        super(SunnyProfileWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)

        # Navigation bar Design Setup
        self.btn_home.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/home.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_camera.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/VideoStabilization.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.btn_profile.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/User.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.lb_menu.setStyleSheet("""
                            QLabel {
                                border-image: url('SolCareGUI/img/profile_menu.png');
                                background-repeat: no-repeat;
                                background-position: center;
                                border: none; 
                            }
                        """)
        
        self.btn_security.setStyleSheet("""
                            QPushButton {
                                border-image: url(SolCareGUI/img/Siren.png);
                                border: 1px solid #2E7D32;
                                border-radius: 5px; 
                                padding: 5px;
                                }
                            """)         
        
        self.btn_home.clicked.connect(lambda: self.control.showwindow(SunnyMainWindow))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

        self.btn_MY.clicked.connect(lambda: self.control.showwindow(SunnyAnalyticsWindow))
        self.btn_security.clicked.connect(lambda: self.control.showwindow(SunnySecurityWindow))

class SunnyAnalyticsWindow(QMainWindow, analytics):
    def __init__(self, control):
        super(SunnyAnalyticsWindow, self).__init__()
        self.control = control
        self.setupUi(self)  
        print(Current_User_ID)
        self.User_Name = self.GetCurrentUser_Name(Current_User_ID)
        self.lb_User_Name.setText(f"{self.User_Name}님 분석")

        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

    def GetCurrentUser_Name(self, Current_User_ID):
        db = mysql.connector.connect(
        host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
        user="ks",
        password="1234",
        database="nahonlab"
        )
        cursor = db.cursor()
        query = """
        SELECT name
        FROM user_info
        WHERE user_id = %s
        """
        cursor.execute(query, (Current_User_ID,))
        user_name = cursor.fetchone()
        return user_name
    
class SunnySecurityWindow(QMainWindow, security):
    def __init__(self, control):
        super(SunnySecurityWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Navigation bar Design Setup
        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

        
        mobilecamIP = 0
        self.cap = cv2.VideoCapture(mobilecamIP)

        self.webcam_timer = QTimer()
        self.webcam_timer.start(33)
        self.webcam_timer.timeout.connect(self.webcam_frame)  # ㅊall update_frame function every time when timer is expired


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

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window_controll = ControlTower()
    window_controll.showwindow(SunnyLoginWindow)
    sys.exit(App.exec())


