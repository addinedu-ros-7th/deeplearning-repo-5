import cv2
import numpy as np
import mediapipe as mp
import time
from tensorflow.keras.models import load_model
from collections import deque
from PIL import Image, ImageDraw, ImageFont
import pymysql
import pyttsx3


class LandmarkExtractor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )

    def extract_landmarks(self, results, image_width, image_height):
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            self.extracted_landmarks = []

            # Mediapipe 랜드마크 매핑 (사용자 정의 순서에 맞게 재배치)
            mediapipe_mapping = {
                'Nose': self.mp_pose.PoseLandmark.NOSE,
                'Left Eye': self.mp_pose.PoseLandmark.LEFT_EYE,
                'Right Eye': self.mp_pose.PoseLandmark.RIGHT_EYE,
                'Left Ear': self.mp_pose.PoseLandmark.LEFT_EAR,
                'Right Ear': self.mp_pose.PoseLandmark.RIGHT_EAR,
                'Left Shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER,
                'Right Shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
                'Left Elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW,
                'Right Elbow': self.mp_pose.PoseLandmark.RIGHT_ELBOW,
                'Left Wrist': self.mp_pose.PoseLandmark.LEFT_WRIST,
                'Right Wrist': self.mp_pose.PoseLandmark.RIGHT_WRIST,
                'Left Hip': self.mp_pose.PoseLandmark.LEFT_HIP,
                'Right Hip': self.mp_pose.PoseLandmark.RIGHT_HIP,
                'Left Knee': self.mp_pose.PoseLandmark.LEFT_KNEE,
                'Right Knee': self.mp_pose.PoseLandmark.RIGHT_KNEE,
                'Left Ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE,
                'Right Ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE,
                'Neck': None,  # Neck은 계산 후 추가
                'Left Palm': self.mp_pose.PoseLandmark.LEFT_INDEX,
                'Right Palm': self.mp_pose.PoseLandmark.RIGHT_INDEX,
                'Back': None,  # Back은 계산 후 추가
                'Waist': None,  # Waist는 계산 후 추가
                'Left Foot': self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
                'Right Foot': self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
            }

            # Hip Center 계산
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            hip_x = (left_hip.x + right_hip.x) / 2
            hip_y = (left_hip.y + right_hip.y) / 2

            # Waist 계산 (기준점)
            waist_x = hip_x
            waist_y = hip_y

            # Shoulder Center 계산
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2


            # Neck 계산
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
            neck_x = (shoulder_center_x + nose.x) / 2
            neck_y = (0.6 * shoulder_center_y + 0.4 * nose.y)

            # Back 계산 (어깨 중심과 Waist의 중간)
            back_x = (shoulder_center_x + waist_x) / 2
            back_y = (shoulder_center_y + waist_y) / 2

            # 유효한 랜드마크 좌표 추출
            for name, mp_index in mediapipe_mapping.items():
                if name in ['Neck', 'Back', 'Waist']:
                    # Neck, Back, Waist는 계산 후 추가
                    if name == 'Neck':
                        pixel_x = int(neck_x * image_width)
                        pixel_y = int(neck_y * image_height)
                    elif name == 'Back':
                        pixel_x = int(back_x * image_width)
                        pixel_y = int(back_y * image_height)
                    elif name == 'Waist':
                        pixel_x = int(waist_x * image_width)
                        pixel_y = int(waist_y * image_height)
                        self.extracted_landmarks.append([0, 0])  # Waist는 기준점
                        continue
                    relative_x = pixel_x - (waist_x * image_width)
                    relative_y = pixel_y - (waist_y * image_height)
                    self.extracted_landmarks.append([relative_x, relative_y])
                else:
                    # Mediapipe 랜드마크 추출
                    landmark = landmarks[mp_index]
                    if landmark.visibility > 0.5:
                        pixel_x = int(landmark.x * image_width)
                        pixel_y = int(landmark.y * image_height)
                        relative_x = pixel_x - (waist_x * image_width)
                        relative_y = pixel_y - (waist_y * image_height)
                        self.extracted_landmarks.append([relative_x, relative_y])
                    else:
                        self.extracted_landmarks.append([0, 0])  # 감지되지 않은 랜드마크는 기본값

            return np.array(self.extracted_landmarks)
        
        else:
            return np.array([])

    def release_resources(self):
        self.pose.close()

class PoseAnalyzer:

    def __init__(self, db_manager=None):
        self.db_manager = db_manager  # DB 매니저를 인스턴스 변수로 저장
        self.last_feedback = []
        self.last_feedback_time = 0  # 피드백이 마지막으로 갱신된 시간
        self.feedback_duration = 2  # 피드백 유지 시간 (초)

        # 운동별 카운트 상태
        self.exercise_counts = {  # 운동별 카운트 초기화
            'Dips': 0,
            'Pullup': 0,
            'Pushup': 0,
            'Squat': 0,
            'Deadlift': 0,
            'Side Lateral Raise': 0,
            'Curl': 0,
        }

        self.previous_exercise_counts = {exercise: 0 for exercise in self.exercise_counts}

        self.last_exercise_state = {  # 운동 상태를 추적 (예: up/down)
            'Dips': 'up',
            'Pullup': 'down',
            'Pushup': 'up',
            'Squat': 'up',
            'Deadlift': 'up',
            'Side Lateral Raise': 'down',
            'Curl': 'down',
        }       

    def get_new_counts(self):
        # 증가분 계산
        new_counts = {
            exercise: self.exercise_counts[exercise] - self.previous_exercise_counts[exercise]
            for exercise in self.exercise_counts
        }
        # 이전 상태 업데이트
        self.previous_exercise_counts = self.exercise_counts.copy()
        return new_counts  

    def count_exercise(self, landmarks, detected_class):
        if detected_class == "Pullup":
            # 팔꿈치 각도로 Pullup 동작 완료 감지
            left_elbow_angle = self.calculate_angle(
                landmarks[5], landmarks[7], landmarks[9]
            )
            right_elbow_angle = self.calculate_angle(
                landmarks[6], landmarks[8], landmarks[10]
            )

            # 상태 전환 로직
            if left_elbow_angle < 110 and right_elbow_angle < 110:  # 팔꿈치를 충분히 굽혔을 때
                if self.last_exercise_state["Pullup"] == "down":
                    self.last_exercise_state["Pullup"] = "up"
                    print("Pullup: State changed to UP")
            elif left_elbow_angle > 140 and right_elbow_angle > 140:  # 팔꿈치를 폈을 때
                if self.last_exercise_state["Pullup"] == "up":
                    self.exercise_counts["Pullup"] += 1
                    self.last_exercise_state["Pullup"] = "down"
                    print("Pullup: State changed to DOWN")

        elif detected_class == "Squat":
            # 무릎 각도로 Squat 동작 완료 감지
            left_knee_angle = self.calculate_angle(
                landmarks[11], landmarks[13], landmarks[15]
            )
            right_knee_angle = self.calculate_angle(
                landmarks[12], landmarks[14], landmarks[16]
            )

            # 동작 상태 감지 (무릎이 충분히 굽혀졌을 때)
            if left_knee_angle < 100 and right_knee_angle < 100:  # 내려간 상태
                if self.last_exercise_state["Squat"] == "up":
                    self.last_exercise_state["Squat"] = "down"
            elif left_knee_angle > 160 and right_knee_angle > 160:  # 올라온 상태
                if self.last_exercise_state["Squat"] == "down":
                    self.exercise_counts["Squat"] += 1
                    self.last_exercise_state["Squat"] = "up"

        # 다른 운동도 유사한 방식으로 추가 가능

        return self.exercise_counts

    
    @staticmethod
    def calculate_angle(a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        # 벡터 계산
        ba = a - b
        bc = c - b

        # 내적과 벡터 크기를 이용한 코사인 값 계산
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.degrees(np.arccos(cosine_angle))
        return angle

    def provide_feedback(self, landmarks, last_class_name):

        feedback = []
        
        # 공통: 목 각도 계산 (waist - back - neck)
        right_neck_angle = self.calculate_angle(
            landmarks[0],  # Nose
            landmarks[17],   # Neck
            landmarks[6]   # Right_Shoulder
        )

        left_neck_angle = self.calculate_angle(
            landmarks[0],  # Nose
            landmarks[17],   # Neck
            landmarks[5]   # Left_Shoulder
        )        
           
        # 공통: 허리 각도 계산 (neck - back - waist)
        back_angle = self.calculate_angle(
            landmarks[17],  # Neck
            landmarks[20],  # Back
            landmarks[21]   # Waist
        )

        # Neck 좌우 균형 확인
        neck_balance_diff = abs(left_neck_angle - right_neck_angle)
        
        # 피드백 조건
        if neck_balance_diff > 20:
            feedback.append("Maintain neck balance. Adjust your posture.")  # 목 균형을 유지하세요.
         
        # 허리 각도 피드백
        if back_angle < 165 or back_angle > 185:
            feedback.append("Keep your back straight.")  # 허리를 곧게 펴세요.

        if last_class_name == "Pullup":
            # 팔꿈치 각도 계산
            left_elbow_angle = self.calculate_angle(
                landmarks[7],  # 왼쪽 어깨
                landmarks[8],  # 왼쪽 팔꿈치
                landmarks[9]   # 왼쪽 손목
            )
            right_elbow_angle = self.calculate_angle(
                landmarks[6],  # 오른쪽 어깨
                landmarks[10],  # 오른쪽 팔꿈치
                landmarks[19]  # 오른쪽 손목
            )

            # 피드백 생성
            if left_elbow_angle > 160 or right_elbow_angle > 160:
                feedback.append("Bend your elbows more.")  # 팔꿈치를 더 굽히세요.
            if left_elbow_angle < 90 or right_elbow_angle < 90:
                feedback.append("Your elbows are bent too much.")  # 팔꿈치를 너무 많이 굽혔습니다.

        elif last_class_name == "Squat":
            # 무릎 각도 계산
            left_knee_angle = self.calculate_angle(
                landmarks[11],  # 왼쪽 엉덩이
                landmarks[13],  # 왼쪽 무릎
                landmarks[15]   # 왼쪽 발목
            )
            right_knee_angle = self.calculate_angle(
                landmarks[12],  # 오른쪽 엉덩이
                landmarks[14],  # 오른쪽 무릎
                landmarks[16]   # 오른쪽 발목
            )

            # 피드백 생성
            if left_knee_angle < 70 or right_knee_angle < 70:
                feedback.append("Your knees are bent too much.")  # 무릎이 너무 많이 굽혀졌습니다.

        elif last_class_name == "Deadlift":
            # 무릎 각도 계산
            left_knee_angle = self.calculate_angle(
                landmarks[11],  # 왼쪽 엉덩이
                landmarks[13],  # 왼쪽 무릎
                landmarks[15]   # 왼쪽 발목
            )
            right_knee_angle = self.calculate_angle(
                landmarks[12],  # 오른쪽 엉덩이
                landmarks[14],  # 오른쪽 무릎
                landmarks[16]   # 오른쪽 발목
            )

            # 피드백 생성
            if left_knee_angle > 90 or right_knee_angle > 90:
                feedback.append("Do not bend your knees too much.")  # 무릎을 너무 많이 굽히지 마세요.

        elif last_class_name == "Pushup":
            # 팔꿈치 각도 계산
            left_elbow_angle = self.calculate_angle(
                landmarks[5],  # 왼쪽 어깨
                landmarks[7],  # 왼쪽 팔꿈치
                landmarks[9]   # 왼쪽 손목
            )
            right_elbow_angle = self.calculate_angle(
                landmarks[6],  # 오른쪽 어깨
                landmarks[8],  # 오른쪽 팔꿈치
                landmarks[10]  # 오른쪽 손목
            )

            # 피드백 생성
            if left_elbow_angle < 90 or right_elbow_angle < 90:
                feedback.append("Your elbows are bent too much.")  # 팔꿈치가 너무 많이 굽혀졌습니다.

        elif last_class_name == "Dips":
            # 팔꿈치 각도 계산
            left_elbow_angle = self.calculate_angle(
                landmarks[7],  # 왼쪽 어깨
                landmarks[8],  # 왼쪽 팔꿈치
                landmarks[9]   # 왼쪽 손목
            )
            right_elbow_angle = self.calculate_angle(
                landmarks[6],  # 오른쪽 어깨
                landmarks[10],  # 오른쪽 팔꿈치
                landmarks[19]  # 오른쪽 손목
            )

            # 피드백 생성
            if left_elbow_angle > 120 or right_elbow_angle > 120:
                feedback.append("Lower yourself further.")  # 몸을 더 낮추세요.
            if left_elbow_angle < 70 or right_elbow_angle < 70:
                feedback.append("Do not go too low.")  # 너무 낮추지 마세요.

        elif last_class_name == "Side Lateral Raise":
            # 팔 각도 계산
            left_shoulder_angle = self.calculate_angle(
                landmarks[11],  # 왼쪽 엉덩이
                landmarks[5],   # 왼쪽 어깨
                landmarks[7]    # 왼쪽 팔꿈치
            )
            right_shoulder_angle = self.calculate_angle(
                landmarks[12],  # 오른쪽 엉덩이
                landmarks[6],   # 오른쪽 어깨
                landmarks[8]    # 오른쪽 팔꿈치
            )

            # 피드백 생성
            if left_shoulder_angle < 80 or right_shoulder_angle < 80:
                feedback.append("Lift your arms higher.")  # 팔을 더 높이 들어올리세요.
            if left_shoulder_angle > 120 or right_shoulder_angle > 120:
                feedback.append("Do not lift your arms too high.")  # 팔을 너무 높이 들지 마세요.

        elif last_class_name == "Curl":
            # 팔꿈치 각도 계산
            left_elbow_angle = self.calculate_angle(
                landmarks[7],  # 왼쪽 어깨
                landmarks[8],  # 왼쪽 팔꿈치
                landmarks[9]   # 왼쪽 손목
            )
            right_elbow_angle = self.calculate_angle(
                landmarks[6],  # 오른쪽 어깨
                landmarks[10],  # 오른쪽 팔꿈치
                landmarks[19]  # 오른쪽 손목
            )

            # 피드백 생성
            if left_elbow_angle > 160 or right_elbow_angle > 160:
                feedback.append("Lower the weights more.")  # 팔을 더 내리세요.
            if left_elbow_angle < 30 or right_elbow_angle < 30:
                feedback.append("Do not curl your arms too much.")  # 팔을 너무 많이 굽히지 마세요.

        return feedback
    
    def get_feedback(self, landmarks, detected_class):
        current_time = time.time()

        # 새로운 피드백 생성
        if detected_class and (current_time - self.last_feedback_time > self.feedback_duration):
            self.last_feedback = self.provide_feedback(landmarks, detected_class)
            self.last_feedback_time = current_time

        # 이전 피드백 유지
        return self.last_feedback    


class PoseClassifier:
    def __init__(self, model_path, class_names, sequence_length=16):
        self.model = load_model(model_path)
        self.class_names = class_names
        self.sequence_length = sequence_length
        self.sequence = deque(maxlen=self.sequence_length)

        self.state = 'idle'  # 상태: idle / active
        self.last_movement_time = time.time()
        self.last_prediction_time = 0
        self.movement_threshold = 10  # 움직임 감지 임계값
        self.inactivity_timeout = 5  # 초 단위

        # 마지막 예측 클래스 및 피드백
        self.last_detected_class = None
        self.last_feedback = []

    def detect_movement(self, landmarks):
        if len(self.sequence) < 2:
            return False

        prev_frame = np.array(self.sequence[-2])
        curr_frame = np.array(landmarks)

        movement = np.linalg.norm(curr_frame - prev_frame, axis=1)
        mean_movement = np.mean(movement)

        return mean_movement > (self.movement_threshold / 2)
    
    def predict_class(self):
        input_data = np.array(self.sequence).reshape(1, self.sequence_length, 24, 2)
        prediction = self.model.predict(input_data)
        confidence = np.max(prediction)
        predicted_class = self.class_names[np.argmax(prediction)]

        return predicted_class if confidence > 0.6 else None

    def process_sequence(self, landmarks):
        self.sequence.append(landmarks)
        current_time = time.time()

        # 상태: idle -> active
        if self.state == 'idle' and self.detect_movement(landmarks):
            self.state = 'active'
            self.last_movement_time = current_time
            print("State changed to ACTIVE")

        # 상태: active -> idle (inactivity timeout)
        if self.state == 'active':
            if self.detect_movement(landmarks):
                self.last_movement_time = current_time

            if current_time - self.last_movement_time > self.inactivity_timeout:
                self.state = 'idle'
                self.sequence.clear()
                self.last_detected_class = None
                self.last_feedback = []
                print("State changed to IDLE")
                return None

            # 예측 수행
            if len(self.sequence) == self.sequence_length and current_time - self.last_prediction_time > 2.5:
                self.last_prediction_time = current_time
                predicted_class = self.predict_class()

                if predicted_class:
                    self.last_detected_class = predicted_class
                return self.last_detected_class

        return self.last_detected_class


class PoseVisualization:
    def __init__(self, image_width, image_height):
        self.image_width = image_width
        self.image_height = image_height

    def draw_results(self, frame, extracted_landmarks, hip_x, hip_y, detected_class, state, feedback, exercise_counts):

        if extracted_landmarks is None or len(extracted_landmarks) == 0:
        # 랜드마크가 없으면 원본 프레임 그대로 반환
            return frame
        
        # OpenCV 이미지를 Pillow 이미지로 변환
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)

        # 폰트 설정
        font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
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
            start_x = int((hip_x * self.image_width) + start_coord[0])
            start_y = int((hip_y * self.image_height) + start_coord[1])
            end_x = int((hip_x * self.image_width) + end_coord[0])
            end_y = int((hip_y * self.image_height) + end_coord[1])

            draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 255, 0), width=3)

        # 피드백 관련 점들 연결 (빨간색 선)
        for conn in red_connections:
            start_idx, end_idx = conn
            start_coord = extracted_landmarks[start_idx]
            end_coord = extracted_landmarks[end_idx]

            # 예외 처리: (0, 0) 좌표는 건너뛰지만, Waist(21번)는 예외적으로 포함
            if (np.array_equal(start_coord, [0, 0]) and start_idx != 21) or (np.array_equal(end_coord, [0, 0]) and end_idx != 21):
                continue

            start_x = int((hip_x * self.image_width) + start_coord[0])
            start_y = int((hip_y * self.image_height) + start_coord[1])
            end_x = int((hip_x * self.image_width) + end_coord[0])
            end_y = int((hip_y * self.image_height) + end_coord[1])

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
                abs_x = int((hip_x * self.image_width) + x)
                abs_y = int((hip_y * self.image_height) + y)

                # 피드백 관련 점은 빨간색
                dot_color = (255, 0, 0) if idx in highlighted_indices else (0, 255, 0)
                draw.ellipse((abs_x - 5, abs_y - 5, abs_x + 5, abs_y + 5), fill=dot_color)


        # 피드백 메시지 표시
        y_offset = 150
        for message in feedback:
            draw.text((10, y_offset), message, font=font, fill=(255, 255, 0))
            y_offset += 40

        # 운동별 카운트 표시
        y_offset = 300
        for exercise, count in exercise_counts.items():
            if count > 0:  # 카운트가 0보다 큰 경우에만 표시
                draw.text((10, y_offset), f"{exercise}: {count}", font=font, fill=(255, 255, 255))  # 흰색 텍스트
                y_offset += 30


        # 다시 OpenCV로 변환
        frame = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        return frame


class DatabaseManager:
    def __init__(self, host, user, password, database, charset='utf8mb4'):
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset=charset,  # 추가
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def get_exercise_id(self, exercise_name):
        sql = "SELECT exercise_id FROM exercise_list WHERE exercise_name = %s"
        self.cursor.execute(sql, (exercise_name,))
        result = self.cursor.fetchone()
        return result['exercise_id'] if result else None

    def insert_exercise_time_log(self, user_id):
        sql = """
        INSERT INTO exercise_time_log (user_id, performed_at)
        VALUES (%s, NOW())
        """
        self.cursor.execute(sql, (user_id,))
        self.connection.commit()
        return self.cursor.lastrowid  # 생성된 exercise_time_id 반환

    def insert_exercise_record(self, exercise_time_id, exercise_id, exercise_cnt):
        sql = """
        INSERT INTO exercise_record (exercise_time_id, exercise_id, exercise_cnt)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (exercise_time_id, exercise_id, exercise_cnt))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


class PoseTrackingApp:
    def __init__(self, model_path, class_names, user_id):
        self.db_manager = DatabaseManager(
            host='database-1.cbcw28i2we7h.us-east-2.rds.amazonaws.com',
            user='kj',
            password='1234',
            database='nahonlab',
            charset='utf8mb4'
        )
        self.landmark_extractor = LandmarkExtractor()
        self.pose_classifier = PoseClassifier(model_path, class_names)
        self.pose_analyzer = None  # PoseAnalyzer를 나중에 초기화
        self.pose_visualizer = None
        self.last_feedback = []
        self.user_id = user_id  # 사용자 ID 저장
        self.exercise_time_id = None  # 운동 세션 ID
        self.exercise_counts = {  # 운동별 카운트 초기화
            'Dips': 0,
            'Pullup': 0,
            'Pushup': 0,
            'Squat': 0,
            'Deadlift': 0,
            'Side Lateral Raise': 0,
            'Curl': 0,
        }

        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty('rate', 150)  # 음성 속도 설정
        self.last_feedback_time = time.time()
        self.feedback_cooldown = 3.0  # 피드백 간 최소 간격(초)
        self.last_spoken_feedback = set()  # 마지막으로 출력된 피드백 저장        

    def start_session(self):
        # 운동 세션 시작 시 exercise_time_log에 저장
        self.exercise_time_id = self.db_manager.insert_exercise_time_log(self.user_id)
        self.pose_analyzer = PoseAnalyzer(self.db_manager)  # DB 매니저 전달
        print(f"Exercise session started with ID: {self.exercise_time_id}")

    def save_exercise_records(self):
        # 운동 기록을 한꺼번에 저장
        print("Saving all exercise records to the database...")
        for exercise_name, count in self.pose_analyzer.exercise_counts.items():
            if count > 0:  # 카운트가 0보다 큰 경우에만 저장
                exercise_id = self.db_manager.get_exercise_id(exercise_name)
                if exercise_id:
                    print(f"Saving exercise: {exercise_name}, ID: {exercise_id}, Count: {count}")
                    self.db_manager.insert_exercise_record(
                        self.exercise_time_id,
                        exercise_id,
                        count
                    )
                else:
                    print(f"Exercise ID not found for: {exercise_name}")

    def speak_feedback(self, feedback):
        """
        피드백 메시지를 음성으로 출력
        """
        current_time = time.time()
        
        # 현재 피드백을 set으로 변환하여 비교
        current_feedback_set = set(feedback)
        
        # 이전에 출력되지 않은 새로운 피드백만 필터링
        new_feedback = current_feedback_set - self.last_spoken_feedback
        
        # 충분한 시간이 지났고 새로운 피드백이 있는 경우에만 출력
        if new_feedback and (current_time - self.last_feedback_time) >= self.feedback_cooldown:
            print("Speaking new feedback:", new_feedback)  # 디버깅용
            
            for message in new_feedback:
                try:
                    self.speech_engine.say(message)
                    self.speech_engine.runAndWait()
                except Exception as e:
                    print(f"Speech error: {e}")
                    continue
            
            self.last_feedback_time = current_time
            self.last_spoken_feedback = current_feedback_set

    def run(self):
        self.start_session()  # 세션 시작
        video_path = "../video/squart1.webm"
        cap = cv2.VideoCapture(video_path)
        print("웹캠 시작... 종료하려면 'q'를 누르세요.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (500, 800))
            image_height, image_width, _ = frame.shape

            if self.pose_visualizer is None:
                self.pose_visualizer = PoseVisualization(image_width, image_height)

            # Mediapipe로 랜드마크 추출
            results = self.landmark_extractor.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hip_x, hip_y = 0, 0
            detected_class = None

            landmarks = np.array([])  # 초기화

            if results.pose_landmarks:
                # 랜드마크 추출 및 중심점 계산
                landmarks = self.landmark_extractor.extract_landmarks(results, image_width, image_height)

                left_hip = results.pose_landmarks.landmark[self.landmark_extractor.mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = results.pose_landmarks.landmark[self.landmark_extractor.mp_pose.PoseLandmark.RIGHT_HIP]
                hip_x = (left_hip.x + right_hip.x) / 2
                hip_y = (left_hip.y + right_hip.y) / 2

                # PoseClassifier로 상태 및 예측 수행
                if landmarks.size > 0:
                    detected_class = self.pose_classifier.process_sequence(landmarks)

                    # 예측된 클래스에 대한 피드백 생성
                    if detected_class:
                        # 운동 카운트 업데이트
                        exercise_counts = self.pose_analyzer.count_exercise(landmarks, detected_class)
                        self.last_feedback = self.pose_analyzer.get_feedback(landmarks, detected_class)

                        current_feedback = self.pose_analyzer.get_feedback(landmarks, detected_class)
                        
                        # 피드백이 있을 경우에만 음성 출력 처리
                        if current_feedback:
                            self.speak_feedback(current_feedback)

                        # 운동별 카운트 출력
                        print(f"Exercise Counts: {exercise_counts}")

            # 결과 시각화
            frame = self.pose_visualizer.draw_results(
                frame, landmarks, hip_x, hip_y, 
                detected_class or self.pose_classifier.last_detected_class,  # 마지막 클래스 유지
                self.pose_classifier.state, 
                self.last_feedback if detected_class else [],  # idle 상태에서는 피드백 초기화
                self.pose_analyzer.exercise_counts  # 운동별 카운트 전달
            )

            cv2.imshow('Pose Classification', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.landmark_extractor.release_resources()
        self.save_exercise_records()  # 종료 시 운동 기록 저장
        self.db_manager.close()


def main():
    MODEL_PATH = '/home/hyun/dev_ws/MLDL_project/source/Exercise/pose_classification_model_gru_v11.h5'
    CLASS_NAMES = [
        'Dips', 'Pullup', 'Pushup', 'Squat', 
        'Deadlift', 'Side Lateral Raise', 'Curl'
    ]
    USER_ID = 18  # 사용자의 user_id 설정
    app = PoseTrackingApp(MODEL_PATH, CLASS_NAMES, USER_ID)
    app.run()

if __name__ == "__main__":
    main()

