# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5 import uic
# import PyQt5
# from PyQt5.QtCore import *

import time
import cv2
import base64
import threading
import socket
import select
import mysql.connector
import numpy as np
from datetime import datetime

from ultralytics import YOLO

print("모델을 불러오는 중입니다...")
test_thread_flag = True
diet_model = YOLO("/home/hdk/ws/project/data/train7/weights/best.pt")

remote = mysql.connector.connect(
    host = "database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
    port =3306,
    user = "h",
    password = "1234",
    database = "nahonlab"
)
cur = remote.cursor()

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def recImage(sock):
    length = recvall(sock, 64)
    length1 = length.decode('utf-8')
    stringData = recvall(sock, int(length1))
    data = np.frombuffer(base64.b64decode(stringData), np.uint8)
    decimg = cv2.imdecode(data, 1)
    return decimg

def test_thread(server_socket, set_time):
    global test_thread_flag
    print("hello thread")

    cnt = 0
    socketList = [server_socket]
    while test_thread_flag:
        cnt += 1
        print("cnt:", cnt, "/", set_time)
        if cnt >= set_time:
            if not set_time == -1:
                print("end thread by cnt")
                test_thread_flag = False
                break

        # 클라이언트 연결 대기
        # print("클라이언트 연결 대기")
        # client_socket, client_address = socket.accept()
        read_socket, write_socket, error_socket = select.select(socketList, [], [], 1)
        for sock in read_socket :
            if sock == server_socket :
                # print("Wait accept")
                client_socket, client_address = sock.accept()
                socketList.append(client_socket)
                # print("Hello,", client_address)

            else :
                try:
                    response = []
                    response.append("NAK")
                    response = "&&".join(response)

                    # print("Wait recive")
                    # 클라이언트로부터 요청 받기
                    data = sock.recv(1024).decode("utf-8")
                    if not data:
                        print("No Data")
                        continue

                    # 요청 파싱
                    # print(data)
                    parts = data.split("&&")
                    # print(parts)

                    if len(parts) != 0:
                        if parts[0] == "Hello":
                            response = []
                            response.append("Hello, ")
                            response.append(str(client_address))
                            response.append("Let's Go")
                            response.append("Home")
                        elif parts[0] == "SendImage":
                            decimg = recImage(sock)

                            response = []
                            response.append("ACK")

                            cv2.imshow("img",decimg)
                            # print(decimg.shape)
                        elif parts[0] == "RequestDietAnalyze":
                            print("model 가즈아!!")
                            decimg = recImage(sock)

                            # 식단 predict
                            results = diet_model(decimg)
                            obj_lsit = [
                                "밥", "김치", "빵", "샐러드", "고등어구이", "닭가슴살", "사과", "바나나", "오렌지", "라면", "삼겹살"
                            ]
                            amount_lsit = [100 for _ in obj_lsit]
                            tmp_list = [False for _ in obj_lsit]

                            boxes = results[0].boxes
                            clss = boxes.cls.cpu().detach().numpy().tolist()
                            xywhs = boxes.xywh.cpu().detach().numpy().tolist()
                            # TODO: amount 추정 코드

                            response = []
                            response.append("ACK")
                            for cls in clss:
                                tmp_list[int(cls)] = True

                            for i, obj in enumerate(obj_lsit):
                                if tmp_list[i]:
                                    response.append(obj)
                                    response.append(str(amount_lsit[i]))

                            plots = results[0].plot()
                            cv2.imshow("plot", plots)
                        elif parts[0] == "ModifyedDietAnalyze":
                            # "modify&&사과&&170&&바나나&&180"
                            # parts[1] = "사과"
                            # parts[2] = "170"
                            objets = parts[1::2]
                            grams = parts[2::2]

                            # TODO: DB 저장
                            pass

                except Exception as e:
                    print(f"오류 발생: {e}")

                finally:
                    # 클라이언트 소켓 닫기
                    # print("클라이언트 연결종료")
                    response = "&&".join(response)
                    sock.send(response.encode("utf-8"))
                    sock.close()
                    socketList.remove(sock)

    print("Server End")
    server_socket.close()
    # cv2.destroyAllWindows()


if __name__=="__main__":
    # 서버 설정
    host0 = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
    port0 = 8080       # 포트 번호
    # 서버 소켓 생성
    server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket0.bind((host0, port0))
    server_socket0.listen()

    server_time = 6
    tcp_controller_thread = threading.Thread(target=test_thread, 
                                             args=(server_socket0,server_time))
    tcp_controller_thread.start()

    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            print("q 입력 종료")
            break

        if not test_thread_flag:
            print("서버 타임 종료")
            break

    test_thread_flag = False
    remote.close()
