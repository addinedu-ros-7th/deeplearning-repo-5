import cv2
import time
import numpy as np
import threading
import mysql.connector as con
import mediapipe as mp
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta, timezone

import socket

# 실시간 HomeCam 실행
fall_detected_start_time = None
capture_count = 0  # 캡처 횟수

# 경고음 상태 변수
warning_sound_active = False

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

# Mediapipe 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=4, circle_radius=2, color=(0, 0, 255))
line_drawing_spec = mp_drawing.DrawingSpec(thickness=4, color=(0, 255, 0))

print("모델을 불러옵니다")
# 모델 설정
# TODO: insert your path
model = load_model("Your path")
print("불러옴")
sequence_length = 10
pose_data = []

# HomeCam 설정
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라가 열리지 않았습니다.")

# TODO: insert your path
image_save_path = "Your path"

# Default emergency_contact
emergency_contact = "119!! 119!!!!"

#["request000"]
def requestTCP(messages):
    addr = "192.168.0.48"  # 서버의 IP 주소 또는 도메인 이름
    port = 8083       # 포트 번호

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((addr, port))
    client_socket.send(f"{'&&'.join(messages)}".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    client_socket.close()
    return response


# 캡처 이미지 저장 함수
def save_falling_image(frame, count):
    timestamp = int(time.time())
    save_img_path = f"{image_save_path}/falling_{timestamp}_{count}.jpg"
    cv2.imwrite(save_img_path, frame)
    return save_img_path  # 이미지 경로 반환


if __name__ == "__main__":
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)

        if result.pose_landmarks is not None:
            mp_drawing.draw_landmarks(
                frame,
                result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=line_drawing_spec
            )

            # Pose sequence 추출
            landmarks = result.pose_landmarks.landmark
            pose_sequence = [coord for landmark in landmarks for coord in (landmark.x, landmark.y)]
            pose_data.append(pose_sequence)

        # 시퀀스가 지정된 길이만큼 차면 모델에 입력
        if len(pose_data) >= sequence_length:
            input_data = np.array(pose_data[-sequence_length:]).reshape(1, sequence_length, -1)
            pose_prediction = model.predict(input_data, verbose=False)

            if pose_prediction[0][0] > 0.5:
                status = "Falling"
                cv2.putText(frame, "FALL DETECTED!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (0, 0, 255), 4, cv2.LINE_AA)

                # 낙상이 감지된 시간 및 이미지 경로 DB 저장
                if fall_detected_start_time is None:
                    fall_detected_start_time = datetime.now(KST)
                    capture_count = 0  # 캡처 횟수 초기화

                # 1초 간격으로 최대 5장의 이미지 저장
                if (datetime.now(KST) - fall_detected_start_time).seconds >= capture_count:
                    if capture_count < 5:
                        capture_count += 1
                        fall_detected_image_path = save_falling_image(frame, capture_count)

                        messages = ["RequestSaveEmvegencyLog"]
                        messages.append(str(fall_detected_image_path))
                        print(messages)
                        response = requestTCP(messages)
                        # response == ACK(수신 양호 신호)

                # emergency_contact 번호 출력 (10초 동안)
                if (datetime.now(KST) - fall_detected_start_time).seconds >= 10:
                    cv2.putText(frame, f'Emergency Calling... "{emergency_contact}"', (50, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX,
                                0.85, (0, 153, 255), 4, cv2.LINE_AA)

            else:
                status = "Normal"
                cv2.putText(frame, "Normal", (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                            2, (0, 255, 0), 4, cv2.LINE_AA)

                # 정상 상태가 감지되면 경고음 중단 및 초기화
                warning_sound_active = False
                fall_detected_start_time = None
                capture_count = 0

        cv2.imshow("Pose Estimation", frame)

        if emergency_contact == "119!! 119!!!!":
            response = requestTCP(["RequestUserEmergencyContact"])
            if response != "NAK":
                print(response)
                parts = response.split("&&")
                if parts[0] == "RequestUserEmergencyContact":
                    emergency_contact = parts[1]

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 프로그램 종료 시 경고음 중단
    warning_sound_active = False
    cap.release()
    cv2.destroyAllWindows()
