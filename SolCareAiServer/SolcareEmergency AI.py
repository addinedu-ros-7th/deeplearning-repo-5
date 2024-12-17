import cv2
import time
import numpy as np
import threading
from playsound import playsound
import mysql.connector as con
import mediapipe as mp
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta, timezone

# Mediapipe 설정
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=4, circle_radius=2, color=(0, 0, 255))
line_drawing_spec = mp_drawing.DrawingSpec(thickness=4, color=(0, 255, 0))

# 모델 설정
model = load_model("/home/cho/nah/model_with_GRU.h5")
sequence_length = 10
pose_data = []

# HomeCam 설정
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라가 열리지 않았습니다.")

# 경고음 상태 변수
warning_sound_active = False
image_save_path = "/home/cho/nah/fall_cap"

# Mysql 연결 설정
nahonlab_db = {
    "user": "admin",
    "password": "Kj40116972!",
    "host": "database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com",
    "database": "nahonlab"
}

# 데이터베이스 연결
dbcon = con.connect(**nahonlab_db)
cursor = dbcon.cursor(dictionary=True)

# emergency_contact 가져오기
cursor.execute(f"SELECT emergency_contact FROM user_info WHERE user_id = 33")
user_contact_num = cursor.fetchone()
emergency_contact = user_contact_num['emergency_contact'] if user_contact_num else "unknown"

# 캡처 이미지 저장 함수
def save_falling_image(frame, count):
    timestamp = int(time.time())
    save_img_path = f"{image_save_path}/falling_{timestamp}_{count}.jpg"
    cv2.imwrite(save_img_path, frame)
    return save_img_path  # 이미지 경로 반환

# 경고음 재생 함수
def play_warning_sound():
    global warning_sound_active
    while warning_sound_active:
        playsound("/home/cho/nah/warning_sound.mp3")
        time.sleep(1.5)

# 실시간 HomeCam 실행
fall_detected_start_time = None
capture_count = 0  # 캡처 횟수

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))


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
        pose_prediction = model.predict(input_data)

        if pose_prediction[0][0] > 0.5:
            status = "Falling"
            cv2.putText(frame, "FALL DETECTED!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                        2, (0, 0, 255), 4, cv2.LINE_AA)

            if not warning_sound_active:
                warning_sound_active = True
                threading.Thread(target=play_warning_sound, daemon=True).start()

            # 낙상이 감지된 시간 및 이미지 경로 DB 저장
            if fall_detected_start_time is None:
                fall_detected_start_time = datetime.now(KST)
                capture_count = 0  # 캡처 횟수 초기화

            # 1초 간격으로 최대 5장의 이미지 저장
            if (datetime.now(KST) - fall_detected_start_time).seconds >= capture_count:
                if capture_count < 5:
                    capture_count += 1
                    fall_detected_image_path = save_falling_image(frame, capture_count)
                    cursor.execute(
                        "INSERT INTO emergency_log (event_time, event_img) VALUES (%s, %s)",
                        (fall_detected_start_time.strftime('%Y-%m-%d %H:%M'), fall_detected_image_path[9:])
                    )
                    dbcon.commit()  # 데이터베이스에 적용

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

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 프로그램 종료 시 경고음 중단
warning_sound_active = False
cap.release()
cv2.destroyAllWindows()

# 데이터베이스 연결 닫기
cursor.close()
dbcon.close()