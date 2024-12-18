import cv2
import numpy as np
import mediapipe as mp
import time
from tensorflow.keras.models import load_model
from collections import deque
from PIL import Image, ImageDraw, ImageFont

class LandmarkExtractor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )

    def extract_landmarks(self, results, image_width, image_height):
        """
        Mediapipe 결과에서 24개의 랜드마크 좌표를 추출하고, 엉덩이 중앙을 기준으로 상대좌표로 변환 후 보정
        """
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
    @staticmethod
    def calculate_angle(a, b, c):
        """
        세 점 (A, B, C)을 기준으로 B에 대한 각도를 계산.
        :param a: 점 A (x, y)
        :param b: 점 B (x, y)
        :param c: 점 C (x, y)
        :return: 각도 (degree)
        """
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
        """
        운동 종류와 관절 각도에 따라 피드백 메시지를 생성.
        :param landmarks: 랜드마크 좌표 리스트
        :return: 피드백 메시지 리스트
        """
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
        # 피드백 조건: 좌우 Neck 각도 차이가 30도 이상이고, 특정 조건을 만족할 때
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



class PoseClassifier:
    def __init__(self, model_path, class_names, sequence_length=16):
        self.model = load_model(model_path)
        self.class_names = class_names
        self.sequence_length = sequence_length
        self.sequence = deque(maxlen=self.sequence_length)

        self.state = 'idle'  # 상태: idle / active
        self.last_movement_time = 0
        self.last_prediction_time = 0
        self.movement_threshold = 50  # 움직임 감지 임계값
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
        significant_movement = movement[movement > self.movement_threshold]

        return len(significant_movement) > 5

    def predict_class(self):
        input_data = np.array(self.sequence).reshape(1, self.sequence_length, 24, 2)
        prediction = self.model.predict(input_data)
        confidence = np.max(prediction)
        predicted_class = self.class_names[np.argmax(prediction)]

        return predicted_class if confidence > 0.6 else None

    def process_sequence(self, landmarks):
        """
        상태 관리 및 예측 로직
        """
        self.sequence.append(landmarks)
        current_time = time.time()

        # 상태: idle -> active
        if self.state == 'idle' and self.detect_movement(landmarks):
            self.state = 'active'
            self.last_movement_time = current_time

        # 상태: active -> idle (inactivity timeout)
        if self.state == 'active':
            if self.detect_movement(landmarks):
                self.last_movement_time = current_time

            if current_time - self.last_movement_time > self.inactivity_timeout:
                self.state = 'idle'
                self.sequence.clear()
                self.last_detected_class = None  # idle 상태가 되면 예측값 초기화
                self.last_feedback = []
                return None

            # 예측 수행
            if len(self.sequence) == self.sequence_length and current_time - self.last_prediction_time > 2.5:
                self.last_prediction_time = current_time
                predicted_class = self.predict_class()

                if predicted_class:
                    self.last_detected_class = predicted_class
                return self.last_detected_class  # 마지막 클래스 반환

        return self.last_detected_class  # 상태가 유지될 때 마지막 클래스 반환



class PoseVisualization:
    def __init__(self, image_width, image_height):
        """
        시각화를 위한 초기화
        :param image_width: 이미지 너비
        :param image_height: 이미지 높이
        """
        self.image_width = image_width
        self.image_height = image_height

    def draw_results(self, frame, extracted_landmarks, hip_x, hip_y, detected_class, state, feedback):
        """
        모델 예측 및 상대 좌표 데이터를 기반으로 시각화
        :param frame: OpenCV 형식의 현재 프레임
        :param extracted_landmarks: 상대 좌표 기반 랜드마크 (Waist 기준)
        :param hip_x: 엉덩이 중심 x 좌표 (상대 좌표)
        :param hip_y: 엉덩이 중심 y 좌표 (상대 좌표)
        :param detected_class: 예측된 운동 클래스 이름
        :param state: 현재 운동 상태 (e.g., 'idle', 'active')
        :param feedback: 생성된 피드백 메시지 리스트
        :return: 시각화된 프레임 (OpenCV 형식)
        """

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
            draw.text((10, 50), f"Class: {detected_class}", font=font, fill=(0, 255, 0))
        draw.text((10, 100), f"State: {state}", font=font, fill=(255, 0, 0))

        # 랜드마크 연결 규칙 정의
        landmark_connections = [
            (17, 5), (17, 6), (5, 7), (6, 8), (7, 9), (8, 10), (9, 18), (10, 19),
            (17, 20), (20, 21), (21, 11), (21, 12),
            (11, 13), (12, 14), (13, 15), (14, 16), (15, 22), (16, 23)
        ]

        # 랜드마크 연결 (선 그리기)
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

            if start_x > 0 and start_y > 0 and end_x > 0 and end_y > 0:
                draw.line([(start_x, start_y), (end_x, end_y)], fill=(0, 255, 0), width=3)


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

                if abs_x > 0 and abs_y > 0:
                    draw.ellipse((abs_x - 5, abs_y - 5, abs_x + 5, abs_y + 5), fill=(0, 0, 255))


        # 피드백 메시지 표시
        y_offset = 150
        for message in feedback:
            draw.text((10, y_offset), message, font=font, fill=(255, 0, 0))
            y_offset += 40

        # 다시 OpenCV로 변환
        frame = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        return frame


class PoseTrackingApp:
    def __init__(self, model_path, class_names):
        self.landmark_extractor = LandmarkExtractor()
        self.pose_classifier = PoseClassifier(model_path, class_names)
        self.pose_analyzer = PoseAnalyzer()
        self.pose_visualizer = None
        self.last_feedback = []

    def run(self):
        cap = cv2.VideoCapture(0)
        print("웹캠 시작... 종료하려면 'q'를 누르세요.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (600, 800))
            image_height, image_width, _ = frame.shape

            if self.pose_visualizer is None:
                self.pose_visualizer = PoseVisualization(image_width, image_height)

            # Mediapipe로 랜드마크 추출
            results = self.landmark_extractor.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hip_x, hip_y = 0, 0
            detected_class = None

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
                        self.last_feedback = self.pose_analyzer.provide_feedback(landmarks, detected_class)

            # 결과 시각화
            frame = self.pose_visualizer.draw_results(
                frame, landmarks, hip_x, hip_y, 
                detected_class or self.pose_classifier.last_detected_class,  # 마지막 클래스 유지
                self.pose_classifier.state, 
                self.last_feedback if detected_class else []  # idle 상태에서는 피드백 초기화
            )

            cv2.imshow('Pose Classification', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.landmark_extractor.release_resources()


def main():
    MODEL_PATH = '/home/hyun/dev_ws/MLDL_project/source/Exercise/pose_classification_model_gru_v11.h5'
    CLASS_NAMES = [
        'Dips', 'Pullup', 'Pushup', 'Squat', 
        'Deadlift', 'Side Lateral Raise', 'Curl'
    ]

    app = PoseTrackingApp(MODEL_PATH, CLASS_NAMES)
    app.run()

if __name__ == "__main__":
    main()