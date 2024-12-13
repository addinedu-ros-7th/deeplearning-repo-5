import time
import cv2
import base64
import threading
import socket
import select
import numpy as np
from datetime import datetime

import signal
import sys

test_thread_flag = True

print("식단 모델을 불러오는 중입니다...")
from ultralytics import YOLO
diet_model = YOLO("/home/hdk/ws/project/data/train7/weights/best.pt")


# SolCareImgSender 수신 소켓 설정
host0 = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
port0 = 8081       # 포트 번호
server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket0.bind((host0, port0))
server_socket0.listen()
userListen_thread_flag = True

# SolcarMainService 수신 소켓 설정
host1 = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
port1 = 8082       # 포트 번호
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket1.bind((host1, port1))
server_socket1.listen()
mainListen_thread_flag = True

def signal_handler(signal, frame):
    global userListen_thread_flag, mainListen_thread_flag
    print('You pressed Ctrl+C!')
    print("Server End Final") 
    userListen_thread_flag = False
    mainListen_thread_flag = False
    server_socket0.close()
    server_socket1.close()

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

# def sendTCP(messages):
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect((host2, port2))
#     client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#     client_socket.close()

# def requestTCP(messages):
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect((host2, port2))
#     client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
#     response = client_socket.recv(1024).decode('utf-8')
#     client_socket.close()
#     return response

def responseTCP(sock, response):
    sock.send(f"{'&&'.join(response)}".encode('utf-8'))

def TCPListenerFromUser(server_socket, set_time=-1):
    global userListen_thread_flag
    socketList = [server_socket]

    print("User Listner 연결 대기", set_time)
    notConnect = True
    cnt = 0
    while userListen_thread_flag:
        # conut out
        if set_time != -1:
            cnt += 1
            print("cnt:", cnt, "/", set_time)
            if cnt >= set_time:
                print("end thread by cnt")
                userListen_thread_flag = False
                break
        # socket connect
        if notConnect:
            read_socket, write_socket, error_socket = select.select(socketList, [], [], 1)
            for sock in read_socket :
                if sock == server_socket:
                    if sock.fileno() != -1:
                        client_socket, client_address = sock.accept()
                        print("User Listner 연결완료")
                        notConnect = False
        # work
        else:
            try:
                # 클라이언트로부터 요청 받기
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    print("No Data")
                    raise Exception("'NoneType' object has no attribute 'decode'")
                parts = data.split("&&")
                if len(parts) != 0:
                    if parts[0] == "SendImage":
                        decimg = recImage(client_socket)
                        # TODO:
                        # 운동자세 모델 적용 후 MainServer로 데이터 전달...?

                        # results = diet_model(decimg, verbose=False)
                        print("good")

            except Exception as e:
                print(f"오류 발생: {e}")
                if str(e) == "'NoneType' object has no attribute 'decode'":
                    client_socket.close()
                    print("User Listner 연결 대기")
                    notConnect = True
                    continue

                print("알 수 없는 오류")
                break

    print("User Listner End")
    server_socket.close()
    cv2.destroyAllWindows()

def TCPListenerFromMain(server_socket, set_time=-1):
    global mainListen_thread_flag
    socketList = [server_socket]

    print("Main Listner 연결 대기")
    notConnect = True
    cnt = 0
    while mainListen_thread_flag:
        # conut out
        if set_time != -1:
            cnt += 1
            print("cnt:", cnt, "/", set_time)
            if cnt >= set_time:
                print("end thread by cnt")
                mainListen_thread_flag = False
                break
        read_socket, write_socket, error_socket = select.select(socketList, [], [], 1)
        for sock in read_socket :
            if sock == server_socket:
                if sock.fileno() != -1:
                    client_socket, client_address = sock.accept()
                    socketList.append(client_socket)
                    print("Main Listner 연결완료")
            # work
            else:
                try:
                    data = sock.recv(1024).decode("utf-8")
                    if not data:
                        print("No Data")
                        continue
                    parts = data.split("&&")
                    print(parts)

                    if len(parts) != 0:
                        if parts[0] == "RequestDietAnalyze":
                            decimg = recImage(sock)
                            results = diet_model(decimg, verbose=False)

                            obj_lsit = ["밥", "김치", "빵", "샐러드", "고등어구이", "닭가슴살", "사과", "바나나", "오렌지", "라면", "삼겹살"]
                            prev_amount_lsit = [200,27,100,24,200,150,287,208,301,85,10]
                            amount_lsit = [0 for _ in obj_lsit]
                            tmp_list = [False for _ in obj_lsit]

                            boxes = results[0].boxes
                            clss = boxes.cls.cpu().detach().numpy().tolist()
                            xywhs = boxes.xywh.cpu().detach().numpy().tolist()
                            # TODO: amount 추정 코드
                            print(xywhs)

                            response = []
                            response.append("ResponseDietCalorie")
                            for cls in clss:
                                tmp_list[int(cls)] = True
                                amount_lsit[int(cls)] += prev_amount_lsit[int(cls)]

                            for i, obj in enumerate(obj_lsit):
                                if tmp_list[i]:
                                    response.append(str(obj))
                                    response.append(str(amount_lsit[i]))
                            print(response)
                            responseTCP(sock, response)
                except Exception as e:
                        print(f"오류 발생: {e}")
                finally:
                    # 클라이언트 소켓 닫기
                    print("Main Listner 연결 대기")
                    sock.close()
                    socketList.remove(sock)

    print("Main Listner End")
    server_socket.close()
    cv2.destroyAllWindows()

if __name__=="__main__":
    userListenTread = threading.Thread(target=TCPListenerFromUser, 
                                  args=(server_socket0, -1))
    
    mainListenTread = threading.Thread(target=TCPListenerFromMain, 
                                  args=(server_socket1, -1))
    
    userListenTread.start()
    mainListenTread.start()
    userListenTread.join()
    mainListenTread.join()