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

import signal
import sys

# SolCareGUI 수신 소켓 설정
host0 = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
port0 = 8083       # 포트 번호
server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket0.bind((host0, port0))
server_socket0.listen()
userListen_thread_flag = True

# SolCaAIService 송신 소켓 설정
host1 = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
port1 = 8082       # 포트 번호
# server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket0.bind((host0, port0))
# server_socket0.listen()
# userListen_thread_flag = True

remote = mysql.connector.connect(
    host = "database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
    port =3306,
    user = "h",
    password = "1234",
    database = "nahonlab"
)
cur = remote.cursor()

def signal_handler(signal, frame):
    global userListen_thread_flag
    print('You pressed Ctrl+C!')
    print("Server End Final")
    userListen_thread_flag = False
    server_socket0.close()
    remote.close()

    cv2.waitKey(50)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

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

#["request000"]
def requestTCP(messages, img=np.zeros((28, 28, 3)), iscamera=False):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host1, port1))

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
    
def TCPListenerFromUser(server_socket, set_time):
    global userListen_thread_flag
    print("hello thread")

    cnt = 0
    socketList = [server_socket]
    while userListen_thread_flag:
        
        if not set_time == -1:
            cnt += 1
            print("cnt:", cnt, "/", set_time)
            if cnt >= set_time:
                print("end thread by cnt")
                userListen_thread_flag = False
                break

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
                        if parts[0] == "RequestDietAnalyze":
                            print("model 가즈아!!")
                            decimg = recImage(sock)

                            # TODO requestTCP(decimg, isImg = True)

                            messages = []
                            messages.append(str(parts[0]))
                            response = requestTCP(messages, decimg, iscamera = True)
                            print(response)

                            sock.send(response.encode('utf-8'))

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
                    sock.close()
                    socketList.remove(sock)

    print("Server End")
    server_socket.close()
    # cv2.destroyAllWindows()


if __name__=="__main__":
    userListenTread = threading.Thread(target=TCPListenerFromUser, 
                                             args=(server_socket0, -1))
    userListenTread.start()
    userListenTread.join()
