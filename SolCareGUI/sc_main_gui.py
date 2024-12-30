from importlib.metadata import requires
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import os
import sys
import socket
import numpy as np
import pandas as pd
import time
import base64
import cv2
import select

import hashlib
import mysql.connector
import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from io import BytesIO
from decimal import Decimal
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from PIL import Image, ImageDraw, ImageFont


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# AI Server
AI_SERVER = 1
AI_ADDR = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
AI_PORT = 8081       # 포트 번호

AI_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
AI_client_socket.connect((AI_ADDR, AI_PORT))

webcam_request_cnt = 0

# Main Server
MAIN_SERVER = 0
MAIN_ADDR = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
MAIN_PORT = 8083       # 포트 번호

def requestTCP(messages, img=np.zeros((28, 28, 3)), iscamera=False, reciver=MAIN_SERVER, long_time = False):
    if reciver == MAIN_SERVER:
        addr = MAIN_ADDR
        port = MAIN_PORT
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((addr, port))

    elif reciver == AI_SERVER:
        addr = MAIN_ADDR
        port = MAIN_PORT
        client_socket = AI_client_socket

    if not iscamera:
        client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
    else:
        resize_frame = cv2.resize(img, dsize=(320, 320), interpolation=cv2.INTER_AREA)
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

    ready = select.select([client_socket], [], [], 2)
    response = "Error"
    if ready[0] or long_time:
        print(long_time)
        response = client_socket.recv(2048).decode('utf-8')
        if reciver == MAIN_SERVER:
            client_socket.close()
    return response

# Import PyQT Desinger File
current_dir = os.path.dirname(os.path.abspath(__file__))
login = uic.loadUiType(os.path.join(current_dir, 'login.ui'))[0]
profile = uic.loadUiType(os.path.join(current_dir, 'profile.ui'))[0]
createaccount = uic.loadUiType(os.path.join(current_dir, 'createaccount.ui'))[0]
main = uic.loadUiType(os.path.join(current_dir, 'main.ui'))[0]
food_camera = uic.loadUiType(os.path.join(current_dir, 'food_camera.ui'))[0]
analytics = uic.loadUiType(os.path.join(current_dir, 'analytics.ui'))[0]
security = uic.loadUiType(os.path.join(current_dir, 'security.ui'))[0]
excercise = uic.loadUiType(os.path.join(current_dir, 'excercise.ui'))[0]
target = uic.loadUiType(os.path.join(current_dir, 'target.ui'))[0]
bodymetrics = uic.loadUiType(os.path.join(current_dir, 'bodymetrics.ui'))[0]

class ControlTower:
    def __init__(self):
        self.current_window = None  
    def showwindow(self, windowtoopen):
        if self.current_window:
            self.current_window.hide() # close
        
        self.current_window = windowtoopen(self)
        self.current_window.show()

class SunnyLoginWindow(QMainWindow, login):
    def __init__(self, control):
        super(SunnyLoginWindow, self).__init__()
        self.control = control
        self.setupUi(self)
        #  Design
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
        
        # Background video play
        self.cap = cv2.VideoCapture('SolCareGUI/img/ad_frame.mp4')
        self.ad_timer = QTimer()
        self.ad_timer.start(30)
        self.ad_timer.timeout.connect(self.ad_frame)

        # GUI Function
        self.btn_login.clicked.connect(self.SendUserInfo)
        self.btn_create.clicked.connect(lambda: self.control.showwindow(SunnyCreateAccountWindow))

    def SendUserInfo(self):
        global Current_User_ID
        global Current_User_NAME
        user_info = []
        user_id = self.le_UserID.text()
        user_password = self.le_UserPassword.text()
        password_hash = hashlib.sha256(user_password.encode("utf-8")).hexdigest()
        user_info.append(user_id)
        user_info.append(password_hash)

        messages = ["RequestLogin"]
        messages.append(user_id)
        messages.append(password_hash)
        response = requestTCP(messages)
        print(response)
        response = response.split('&&')

        Current_User_ID = response[2]
        Current_User_NAME = response[3]

        if response[1] == 'True':
            QMessageBox.warning(self, 'Log In Success',"Log In Success")
            self.control.showwindow(SunnyMainWindow)
        else:
            QMessageBox.warning(self, 'Warning',"User Info Not Exist Please SIGH UP!!!")

    def ad_frame(self):
        ret, frame = self.cap.read()
        if not ret: # 다시 읽기
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (393, 852))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))
        QTimer.singleShot(15000, self.ad_frame)

class SunnyCreateAccountWindow(QMainWindow, createaccount):
    def __init__(self, control):
        super(SunnyCreateAccountWindow, self).__init__()
        self.control = control
        self.setupUi(self)
        #  Design
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
        
        #  GUI Function
        self.btn_create.clicked.connect(self.RegisterUser)
        self.btn_cancle.clicked.connect(lambda: self.control.showwindow(SunnyLoginWindow))
        self.cb_NewUserSex.addItems(['남성', '여성'])

    def RegisterUser(self):
        new_user_nickname = self.le_NewUserID.text()
        new_user_password = self.le_NewUserPassword.text()
        new_user_password_hashed = hashlib.sha256(new_user_password.encode("utf-8")).hexdigest()
        
        new_user_name = self.le_NewUserName.text()
        new_user_sex = self.cb_NewUserSex.currentText()
        new_user_birthday = self.de_NewUserBirthday.text()
        new_user_phone = self.le_NewUserPhone.text()
        new_user_emer_phone = self.le_NewUserEmerPhone.text()

        messages = ["RequestSignUp"]
        messages.append(new_user_nickname)
        messages.append(new_user_password_hashed)
        messages.append(new_user_name)
        messages.append(new_user_sex)
        messages.append(new_user_birthday)
        messages.append(new_user_phone)
        messages.append(new_user_emer_phone)
        response = requestTCP(messages)

        print(response)

        response = response.split("&&")
        if response[1] == 'True':
            QMessageBox.warning(self, 'Sign Up Success',"Welcome!")
            self.control.showwindow(SunnyTargetWindow)
        else:
            QMessageBox.warning(self, 'Warning',"Please Use Different ID")
    
class SunnyMainWindow(QMainWindow, main):
    def __init__(self, control):
        super(SunnyMainWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)

        # Design
        self.lb_logo.setStyleSheet("""
                                    QLabel {
                                        border-image: url('SolCareGUI/img/logo.jpg');
                                        background-repeat: no-repeat;
                                        background-position: center;
                                        border: none; 
                                        }
                                    """)
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

        # User daily stat
        messages = ["RequestTodayAnalytics"]
        print(Current_User_ID)
        messages.append(Current_User_ID)
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        messages.append(today_date)

        response = requestTCP(messages) # df / pixmap
        response = response.split('&&')

        data = response[1]
        result = eval(data)

        # Visualiztion
        activities = [item[0] for item in result]  
        values = [float(item[2]) for item in result]  
        multipliers = [float(item[3]) for item in result] 
        calories = [Decimal(value) * Decimal(multiplier) for value, multiplier in zip(values, multipliers)]

        total_calories = round(sum(calories),2)
        self.lb_kcal.setText(f"{total_calories}kcal")
        cmap = plt.get_cmap('Blues') 
        fig, ax = plt.subplots()
        ax.pie(values, labels=activities, autopct='%1.1f%%', startangle=90,colors=cmap(np.linspace(0, 1, len(values))), textprops={'fontsize': 18})
        ax.axis('equal') 

        img_stream_pie = BytesIO()
        plt.savefig(img_stream_pie, format='png')
        img_stream_pie.seek(0)

        pixmap_pie = QPixmap()
        pixmap_pie.loadFromData(img_stream_pie.read())
        self.lb_user_today.setPixmap(pixmap_pie)
        self.lb_user_today.setScaledContents(True)

        fig, ax = plt.subplots()
        ax.bar(activities, calories)

        ax.set_xlabel('Exercises')
        ax.set_ylabel('Calories Consumed')
        ax.set_title(f'Total Calories Consumed: {total_calories:.2f} kcal')

        img_stream_bar = BytesIO()
        plt.savefig(img_stream_bar, format='png')
        img_stream_bar.seek(0)

        pixmap_bar = QPixmap()
        pixmap_bar.loadFromData(img_stream_bar.read())
        self.lb_user_kcal_cons.setPixmap(pixmap_bar)
        self.lb_user_kcal_cons.setScaledContents(True)

        # GUI Function
        self.btn_cardio.clicked.connect(lambda: self.control.showwindow(SunnyExcerciseCamWindow))
        self.btn_home.clicked.connect(lambda:  self.control.showwindow(SunnyMainWindow))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

class SunnyExcerciseCamWindow(QMainWindow, excercise):
    def __init__(self, control):
        super(SunnyExcerciseCamWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Design
        self.btn_back.setStyleSheet("""
                            QPushButton {
                                border-image: url(SolCareGUI/img/Back.png);
                                background-color: rgb(255, 255, 255,0);
                                border: 1px solid #2E7D32;
                                border-radius: 5px; 
                                padding: 5px;
                                }
                            """)

        mobilecamIP = 0 # In case of using external cam
        self.cap = cv2.VideoCapture(mobilecamIP)

        self.webcam_tcp_timer = QTimer()
        self.webcam_tcp_timer.timeout.connect(self.send_webcam_frame_tcp)
        self.webcam_tcp_timer.start(100)

        self.btn_back.clicked.connect(lambda: (self.closeCam(), self.control.showwindow(SunnyMainWindow)))

    def send_webcam_frame_tcp(self):
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (480, 640))
        
        if ret:
            h, w, _ = frame.shape
            messages = ["RequestExResult"]
            messages.append('{0:08d}'.format(w))
            messages.append('{0:08d}'.format(h))
            re = requestTCP(messages=messages, img=frame, iscamera=True, reciver=AI_SERVER)

            parts = re.split("&&")

            landmarks = np.array(eval(parts[1]))
            hip_x = eval(parts[2])
            hip_y = eval(parts[3])
            detected_class = parts[4]
            state = parts[5]
            last_feedback = eval(parts[6])
            exercise_counts = eval(parts[7])
            idle_duration = eval(parts[8])

            # print((landmarks), 
            #       (hip_x), 
            #       (hip_y), 
            #       (detected_class), 
            #       (state), 
            #       (last_feedback), 
            #       (exercise_counts), 
            #       (idle_duration))

            # print(type(landmarks), 
            #       type(hip_x), 
            #       type(hip_y), 
            #       type(detected_class), 
            #       type(state), 
            #       type(last_feedback), 
            #       type(exercise_counts), 
            #       type(idle_duration))

            dst = self.draw_results(frame,
                                landmarks, 
                                hip_x, 
                                hip_y, 
                                detected_class, 
                                state, 
                                last_feedback, 
                                exercise_counts, 
                                idle_duration,
                                w,
                                h)
            
            # cv2.imshow('dst', dst)
            frame_resized = cv2.resize(dst, (393, 852))
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    def closeCam(self):
        if  self.cap.isOpened():
            self.cap.release()  
            self.webcam_tcp_timer.stop()

    def draw_results(self, frame, extracted_landmarks, hip_x, hip_y, detected_class, state, feedback, exercise_counts, idle_duration, w, h):
        image_width = w
        image_height = h
        if extracted_landmarks is None or len(extracted_landmarks) == 0:
        # 랜드마크가 없으면 원본 프레임 그대로 반환
            return frame
        
        # OpenCV 이미지를 Pillow 이미지로 변환
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # # 폰트 설정
        font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        font = ImageFont.truetype(font_path, 24)

        # 텍스트 추가 (클래스와 상태 표시)
        if detected_class:
            draw.text((10, 100), f"Class: {detected_class}", font=font, fill=(0, 255, 0))
        # 상태에 따라 색상 변경 (활성화: 녹색, 비활성화: 회색)
        state_color = (0, 255, 0) if state == "active" else (128, 128, 128)
        draw.text((10, 50), f"State: {state.capitalize()}", font=font, fill=state_color)

        # 피드백에 따라 강조할 랜드마크 인덱스 설정
        feedback_mapping = {
            "neck balance": [17],  # 목 점
            "back straight": [17, 20, 21],
            "left_elbow": [7, 8, 9],
            "right_elbow": [6, 10, 19],  # 팔꿈치
            "left_knee": [11, 13, 15],  # 무릎
            "right_knee": [12, 14, 16]  # 무릎
        }

        # 강조할 점 인덱스 추출
        highlighted_indices = set()
        for message in feedback:
            message_lower = message.lower()
            for key, indices in feedback_mapping.items():
                if key in message_lower:
                    highlighted_indices.update(indices)

        # 빨간 점 연결 (highlighted_indices 기반으로 점들 사이의 선 계산)
        red_connections = []
        highlighted_indices = sorted(highlighted_indices)  # 정렬된 인덱스로 처리
        for i in range(len(highlighted_indices) - 1):
            red_connections.append((highlighted_indices[i], highlighted_indices[i + 1]))


        # 랜드마크 연결 규칙 정의
        landmark_connections = [
            (17, 5), (17, 6), (5, 7), (6, 8), (7, 9), (8, 10), (9, 18), (10, 19),
            (17, 20), (20, 21), (21, 11), (21, 12),
            (11, 13), (12, 14), (13, 15), (14, 16), (15, 22), (16, 23)
        ]

        # 랜드마크 연결 (선 그리기)
        for conn in landmark_connections:
            start_idx, end_idx = conn
            start_coord = extracted_landmarks[start_idx]
            end_coord = extracted_landmarks[end_idx]

            # 예외 처리: (0, 0) 좌표는 건너뛰지만, Waist(21번)는 예외적으로 포함
            if (np.array_equal(start_coord, [0, 0]) and start_idx != 21) or (np.array_equal(end_coord, [0, 0]) and end_idx != 21):
                continue

            # 상대 좌표를 절대 좌표로 변환
            start_x = int((hip_x * image_width) + start_coord[0])
            start_y = int((hip_y * image_height) + start_coord[1])
            end_x = int((hip_x * image_width) + end_coord[0])
            end_y = int((hip_y * image_height) + end_coord[1])

            draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 255, 0), width=3)

        # 피드백 관련 점들 연결 (빨간색 선)
        for conn in red_connections:
            start_idx, end_idx = conn
            start_coord = extracted_landmarks[start_idx]
            end_coord = extracted_landmarks[end_idx]

            # 예외 처리: (0, 0) 좌표는 건너뛰지만, Waist(21번)는 예외적으로 포함
            if (np.array_equal(start_coord, [0, 0]) and start_idx != 21) or (np.array_equal(end_coord, [0, 0]) and end_idx != 21):
                continue

            start_x = int((hip_x * image_width) + start_coord[0])
            start_y = int((hip_y * image_height) + start_coord[1])
            end_x = int((hip_x * image_width) + end_coord[0])
            end_y = int((hip_y * image_height) + end_coord[1])

            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 0, 0), width=3)


        # 랜드마크 점 찍기 (얼굴 랜드마크 인덱스 제외)
        excluded_indices = [0, 1, 2, 3, 4]
        for idx, coord in enumerate(extracted_landmarks):
            if idx in excluded_indices:
                continue

            # 예외 처리: (0, 0) 좌표는 건너뛰지만, Waist(21번)는 예외적으로 포함
            if np.array_equal(coord, [0, 0]) and idx != 21:
                continue

            if len(coord) == 2:
                x, y = coord
                abs_x = int((hip_x * image_width) + x)
                abs_y = int((hip_y * image_height) + y)

                # 피드백 관련 점은 빨간색
                dot_color = (255, 0, 0) if idx in highlighted_indices else (0, 255, 0)
                draw.ellipse((abs_x - 5, abs_y - 5, abs_x + 5, abs_y + 5), fill=dot_color)


        # 피드백 메시지 표시
        y_offset = 150
        for message in feedback:
            draw.text((10, y_offset), message, font=font, fill=(255, 255, 0))
            y_offset += 40

        # Idle Duration 출력
        if state == "idle":
            draw.text((10, 150), f"Resting: {idle_duration} seconds", font=font, fill=(255, 255, 0))

        # 운동별 카운트 표시
        y_offset = 300
        for exercise, count in exercise_counts.items():
            if count > 0:  # 카운트가 0보다 큰 경우에만 표시
                draw.text((10, y_offset), f"{exercise}: {count}", font=font, fill=(255, 255, 255))  # 흰색 텍스트
                y_offset += 30


        # 다시 OpenCV로 변환
        frame = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        return frame

class DietAnalyzePopup(QDialog):
    def __init__(self, response_string):
        super().__init__()
        self.setWindowTitle("결과")
        self.setGeometry(655, 350, 300, 250)

        self.features = self.parse_response(response_string)

        self.layout = QVBoxLayout()
        self.input_fields = [] #Lineedit Value

        for feature in self.features:
            feature_name, grams, carb, protein, fat = feature
            self.add_feature_row(feature_name, grams, carb, protein, fat)

        confirm_button = QPushButton("저장")
        confirm_button.clicked.connect(self.save_food_result)
        self.layout.addWidget(confirm_button)

        self.setLayout(self.layout)

    def parse_response(self, response_string):
        parts = response_string.split("&&")
        features = []
        for i in range(1, len(parts), 5): # 4 variables, skip first index 
            if i + 4 < len(parts):
                features.append((parts[i], parts[i + 1], parts[i + 2], parts[i + 3], parts[i + 4]))
        return features

    def add_feature_row(self, feature_name, grams, carb, protein, fat):
        row_layout = QHBoxLayout()

        feature_label = QLabel(feature_name)
        row_layout.addWidget(feature_label)

        grams_edit = QLineEdit(grams)
        row_layout.addWidget(QLabel("Grams:"))
        row_layout.addWidget(grams_edit)

        carb_edit = QLineEdit(str(int(float(carb) * float(grams))))
        row_layout.addWidget(QLabel("탄수화물:"))
        row_layout.addWidget(carb_edit)

        protein_edit = QLineEdit(str(int(float(protein) * float(grams))))
        row_layout.addWidget(QLabel("단백질:"))
        row_layout.addWidget(protein_edit)

        fat_edit = QLineEdit(str(int(float(fat) * float(grams))))
        row_layout.addWidget(QLabel("지방:"))
        row_layout.addWidget(fat_edit)

        self.input_fields.append((feature_name, grams_edit, carb_edit, protein_edit, fat_edit))

        self.layout.addLayout(row_layout)

    def save_food_result(self):
        updated_values = ["SendUpdatedFood"]
        for feature_name, grams_edit, carb_edit, protein_edit, fat_edit in self.input_fields:
            updated_values.append(feature_name)
            updated_values.append(grams_edit.text())
            updated_values.append(carb_edit.text())
            updated_values.append(protein_edit.text())
            updated_values.append(fat_edit.text())
        requestTCP(updated_values)
        self.accept()

class SunnyFoodCameraWindow(QMainWindow, food_camera):
    def __init__(self, control):
        super(SunnyFoodCameraWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Design
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

        self.webcam_gui_timer = QTimer()
        self.webcam_gui_timer.start(1)
        self.webcam_gui_timer.timeout.connect(self.webcam_frame)  
        self.btn_camera_shutter.clicked.connect(self.take_photo)
        # GUI Function
        self.btn_home.clicked.connect(lambda: (self.closeCam(), self.control.showwindow(SunnyMainWindow)))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

    def webcam_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame =frame
            frame_resized = cv2.resize(frame, (393, 852))
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lb_webcam.setPixmap(QPixmap.fromImage(qt_image))

    def closeCam(self):
        if  self.cap.isOpened():
            self.cap.release()  
            self.webcam_gui_timer.stop() 

    def take_photo(self):
         # cam effect
        self.lb_shutter_effect.setStyleSheet("background-color: white;")
        QTimer.singleShot(200, lambda: self.lb_shutter_effect.setStyleSheet(""))

        messages = ["RequestDietAnalyze"]
        response = requestTCP(messages, img=self.frame, iscamera=True)
        food_result = response 
        print(food_result)

        popup = DietAnalyzePopup(food_result)
        if popup.exec_() == QDialog.Accepted: 
            updated_values = []

            total_calories = 0
            total_carb = 0
            total_prot = 0
            total_fat = 0

            carb_percent = 0
            prot_percent = 0
            fat_percent = 0

            for feature, grams, carb, protein, fat in popup.input_fields:
                print(feature, grams, carb, protein, fat)
                grams_value = float(grams.text())
                carb_value = float(carb.text())
                protein_value = float(protein.text())
                fat_value = float(fat.text())
                print(feature, grams_value, carb_value, protein_value, fat_value)
                
                total_calories += (carb_value * 4 + protein_value * 4 + fat_value * 9)
                total_carb += carb_value
                total_prot += protein_value
                total_fat += fat_value

            carb_percent = total_carb * 4 / total_calories
            prot_percent = total_prot * 4 / total_calories
            fat_percent = total_fat * 9 / total_calories
        

                
            updated_values.append({
                "총 칼로리": round(total_calories,2),

                "탄(g)": round(total_carb,2),
                "탄(%)": round(carb_percent,2),

                "단(g)": round(total_prot,2),
                "단(%)": round(prot_percent,2),

                "지(g)": round(total_fat,2),
                "지(%)": round(fat_percent,2),
            })

            s = f"""
                총 칼로리": {round(total_calories,2)}

                탄(g): {round(total_carb,2)}
                탄(%): {round(carb_percent,2)}

                단(g): {round(total_prot,2)}
                단(%): {round(prot_percent,2)}

                지(g): {round(total_fat,2)}
                지(%): {round(fat_percent,2)}
                """
                
            QMessageBox.information(self, 'Calculation Complete', s)

class SunnyProfileWindow(QMainWindow, profile):
    def __init__(self, control):
        super(SunnyProfileWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)

        # Design
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
        # GUI Function
        self.btn_home.clicked.connect(lambda: self.control.showwindow(SunnyMainWindow))
        self.btn_camera.clicked.connect(lambda: self.control.showwindow(SunnyFoodCameraWindow))
        self.btn_profile.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

        self.btn_statistics.clicked.connect(lambda: self.control.showwindow(SunnyAnalyticsWindow))
        self.btn_target.clicked.connect(lambda: self.control.showwindow(SunnyTargetWindow))
        self.btn_bodymetrics.clicked.connect(lambda: self.control.showwindow(SunnyBodyMetricstWindow))

        self.btn_security.clicked.connect(lambda: self.control.showwindow(SunnySecurityWindow))

class SunnyAnalyticsWindow(QMainWindow, analytics):
    def __init__(self, control):
        super(SunnyAnalyticsWindow, self).__init__()
        self.control = control
        self.setupUi(self)
        # Design
        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        self.lb_User_Name.setText(f"{Current_User_NAME}님 분석")
        
        # Date selection
        self.date_from = (datetime.datetime.today() - timedelta(weeks=1)).date()
        self.date_to = datetime.datetime.today().date()
        self.de_from.setDate(self.date_from)
        self.de_to.setDate(self.date_to)
        self.de_from.editingFinished.connect(lambda: self.date_from == self.de_from.date().toString('yyyy-MM-dd'))
        self.de_to.editingFinished.connect(lambda: self.date_to == self.de_to.date().toString('yyyy-MM-dd'))
        # GUI Function
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))
        self.btn_reset.clicked.connect(self.ResetAnalyticsGraph)
        self.btn_mealAI.clicked.connect(self.MealRequest)
        self.btn_exAI.clicked.connect(self.ExerciseRequest)

    def ResetAnalyticsGraph(self):
        self.GetUserAnalyticsGraph(Current_User_ID, self.date_from, self.date_to)
        self.GetKcalGraph(Current_User_ID, self.date_from, self.date_to)
    
    def GetUserAnalyticsGraph(self, Current_User_ID, date_from, date_to):
        print(date_from)
        db = mysql.connector.connect(
            host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
            user="ks",
            password="1234",
            database="nahonlab"
        )

        query = """
        SELECT 
            el.exercise_name,
            DATE(etl.performed_at) AS exercise_date,
            SUM(er.exercise_cnt) AS total_count,
            SUM(er.exercise_set) AS total_set
        FROM 
            exercise_time_log etl
        JOIN 
            exercise_record er ON etl.exercise_time_id = er.exercise_time_id
        JOIN 
            exercise_list el ON er.exercise_id = el.exercise_id
        WHERE 
            etl.user_id = %s
            AND DATE(etl.performed_at) BETWEEN %s AND %s
        GROUP BY 
            exercise_date, el.exercise_name
        ORDER BY 
            exercise_date, el.exercise_name;
        """

        cursor = db.cursor()
        cursor.execute(query, (Current_User_ID, date_from, date_to))
        
        result = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        db.close()

        df = pd.DataFrame(result, columns=columns)

        df['exercise_date'] = pd.to_datetime(df['exercise_date'], format='%m-%d')
        df['total_count'] = pd.to_numeric(df['total_count'], errors='coerce')
        df = df.dropna(subset=['total_count'])
        df['exercise_date'] = df['exercise_date'].dt.date

        pivot_df = df.pivot_table(
            index='exercise_date',
            columns='exercise_name',
            values='total_count',
            aggfunc='sum',
            fill_value=0
        )

        fig, ax = plt.subplots(figsize=(6, 3.5)) 
        pivot_df.plot(kind='bar', stacked=True, ax=ax, colormap='Greys', legend=False) 

        for idx, rect_group in enumerate(ax.containers):
            for rect in rect_group:
                height = rect.get_height()
                if height > 0:
                    x = rect.get_x() + rect.get_width() / 2
                    y = rect.get_y() + height / 2
                    ax.text(
                        x,
                        y,
                        f'{int(height)}',
                        ha='center',
                        va='center',
                        fontsize=10,
                        color='black'
                    )

        ax.set_yticks([])
        ax.set_xticks([])
        plt.xticks(rotation=45, fontsize=10)

        graph_buf = BytesIO()
        fig.savefig(graph_buf, format="png", bbox_inches="tight", dpi=300)
        graph_buf.seek(0)

        graph_pixmap = QPixmap()
        graph_pixmap.loadFromData(graph_buf.getvalue())
        graph_buf.close()

        legend_fig, legend_ax = plt.subplots(figsize=(2, 3.8))
        legend_ax.axis("off")

        legend = legend_ax.legend(*ax.get_legend_handles_labels(), loc='center', frameon=False)
        legend_buf = BytesIO()
        legend_fig.savefig(legend_buf, format="png", bbox_inches="tight", dpi=300)
        legend_buf.seek(0)

        legend_pixmap = QPixmap()
        legend_pixmap.loadFromData(legend_buf.getvalue())
        legend_buf.close()

        graph_pixmap = graph_pixmap.scaled(
            self.lb_use_ex_analytics.width(),
            self.lb_use_ex_analytics.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        legend_pixmap = legend_pixmap.scaled(
            self.lb_use_ex.width(),
            self.lb_use_ex.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.lb_use_ex_analytics.setPixmap(graph_pixmap)
        self.lb_use_ex.setPixmap(legend_pixmap)    

    def GetKcalGraph(self, Current_User_ID, date_from, date_to):

        db = mysql.connector.connect(
            host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
            user="ks",
            password="1234",
            database="nahonlab"
        )

        query = """
            SELECT 
                record_date, 
                weight, 
                fat_percent, 
                muscle_mass, 
                calories_burned, 
                calories_intake
            FROM 
                user_body_metrics
            WHERE 
                user_id = %s 
                AND record_date BETWEEN %s AND %s
            ORDER BY 
                record_date ASC;
            """
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (Current_User_ID, date_from, date_to))
        result = cursor.fetchall()
        cursor.close()
        data = pd.DataFrame(result)

        fig, ax = plt.subplots(figsize=(7, 4))

        for metric in ['calories_burned', 'calories_intake']:
            if metric in data.columns:
                ax.plot(data['record_date'], data[metric] , label=metric)

        ax.set_xlabel('date')
        ax.set_ylabel('kcal')
        ax.legend()
        ax.grid()

        canvas = FigureCanvas(fig)
        buf = BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        kcal_pixmap = QPixmap()
        kcal_pixmap.loadFromData(buf.getvalue())
        buf.close()

        kcal_pixmap = kcal_pixmap.scaled(
            self.lb_use_meal_analytics.width(),
            self.lb_use_meal_analytics.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.lb_use_meal_analytics.setPixmap(kcal_pixmap)
    
    def MealRequest(self):
        msg = ["RequestMealRecommend"]
        msg.append(Current_User_ID)
        response = requestTCP(msg, long_time=True)
        print("hdk", response)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("주인님을 위한 식단 추천입니다")
        msg_box.setText(response)  
        msg_box.setIcon(QMessageBox.Information) 
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def ExerciseRequest(self): 
        msg = ["RequestExerciseRecommend"]
        msg.append(Current_User_ID)
        response = requestTCP(msg)
        print(response)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("주인님을 위한 운동 추천입니다")
        msg_box.setText(response)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

class SunnySecurityWindow(QMainWindow, security):
    def __init__(self, control):
        super(SunnySecurityWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Design
        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        # GUI Function
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))

        # Sec Cam trigger
        mobilecamIP = 0
        self.cap = cv2.VideoCapture(mobilecamIP)
        self.webcam_timer = QTimer()
        self.webcam_timer.start(33)
        self.webcam_timer.timeout.connect(self.webcam_frame) 

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

class SunnyTargetWindow(QMainWindow, target):
    def __init__(self, control):
        super(SunnyTargetWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        # Design
        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)
        
        self.date_today = datetime.datetime.today().date()
        self.de_from.setDate(self.date_today)
        # GUI Function
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))
        self.btn_save.clicked.connect(self.SaveUserTarget)

    def SaveUserTarget(self):

        date_from = self.de_from.date().toString('yyyy-MM-dd')
        date_to = self.de_to.date().toString('yyyy-MM-dd')
        user_weight = self.le_UserWeight.text()
        user_fat = self.le_UserFat.text()
        user_sm = self.le_Usersm.text()

        messeage = ['UserTargetInfo']
        messeage.append(date_from)
        messeage.append(date_to)
        messeage.append(user_weight)
        messeage.append(user_fat)
        messeage.append(user_sm)
        response = requestTCP(messeage)
        response = response.split('&&')
        if response[1] == 'True':
            QMessageBox.information(self, 'Information Saved')
            self.control.showwindow(SunnyProfileWindow)
        else:
            None

class SunnyBodyMetricstWindow(QMainWindow, bodymetrics):
    def __init__(self, control):
        super(SunnyBodyMetricstWindow, self).__init__()
        self.control = control
        self.cap = None
        self.setupUi(self)
        #Design
        self.btn_back.setStyleSheet("""
                                    QPushButton {
                                        border-image: url(SolCareGUI/img/Back.png);
                                        background-color: rgb(255, 255, 255,0);
                                        border: 1px solid #2E7D32;
                                        border-radius: 5px; 
                                        padding: 5px;
                                        }
                                    """)

        # Date Selection
        self.date_from = (datetime.datetime.today() - timedelta(weeks=1)).date()
        self.date_to = datetime.datetime.today().date()
        self.de_from.setDate(self.date_from)
        self.de_to.setDate(self.date_to)
        self.de_from.editingFinished.connect(lambda: self.date_from == self.de_from.date().toString('yyyy-MM-dd'))
        self.de_to.editingFinished.connect(lambda: self.date_to == self.de_to.date().toString('yyyy-MM-dd'))
        # GUI Function
        self.btn_back.clicked.connect(lambda: self.control.showwindow(SunnyProfileWindow))
        self.btn_analytics.clicked.connect(self.GetBodyMetrics)
        self.btn_met.clicked.connect(self.GetBodyMetRecom)

    def GetBodyMetRecom(self):
        msg = ["RequestPredict"]
        msg.append(Current_User_ID)
        response = requestTCP(msg, long_time=True)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("주인님의 체성분 예측입니다")
        msg_box.setText(response)  
        msg_box.setIcon(QMessageBox.Information) 
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def GetBodyMetrics(self):
        from_date = self.de_from.date().toString('yyyy-MM-dd')
        to_date = self.de_to.date().toString('yyyy-MM-dd')

        db = mysql.connector.connect(
            host="database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
            user="ks",
            password="1234",
            database="nahonlab"
        )

        query = """
            SELECT 
                record_date, 
                weight, 
                fat_percent, 
                muscle_mass
            FROM 
                user_body_metrics
            WHERE 
                user_id = %s 
                AND record_date BETWEEN %s AND %s
            ORDER BY 
                record_date ASC;
        """
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (Current_User_ID, from_date, to_date))
        result = cursor.fetchall()
        cursor.close()

        data = pd.DataFrame(result)

        data['record_date'] = pd.to_datetime(data['record_date'])

        fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)

        for metric in ['weight', 'fat_percent', 'muscle_mass']:
            if metric in data.columns:
                ax.plot(data['record_date'], data[metric], label=metric)

        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.legend(loc="upper left")
        ax.grid()

        canvas = FigureCanvas(fig)
        buf = BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        buf.close()

        pixmap = pixmap.scaled(
            self.lb_bodymetrics.width(),
            self.lb_bodymetrics.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.lb_bodymetrics.setPixmap(pixmap)

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window_controll = ControlTower()
    window_controll.showwindow(SunnyLoginWindow)
    sys.exit(App.exec())


