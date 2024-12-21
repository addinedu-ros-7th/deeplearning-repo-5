![image](https://github.com/user-attachments/assets/035e085e-c6a9-4e67-be6d-4700480d66dd)
# 솔로를 위한 인공지능 헬스케어 서비스 : Solcare AI Service

# 1. 프로젝트 소개
## 주제
- 운동, 식단, 위험 상황 관리를 통합하여 개인의 건강을 AI로 관리하는 서비스 개발

## 주제 선정 배경
- 1인 가구의 증가
- 직접 기록해야 하는 기존 서비스의 불편함
- 운동, 식단, 위험 상관 관리 통합 서비스의 부재

## User Requirements
| **구분**       | **기능**                                | **설명**                                                                                 |
|:----------------:|---------------------------------------|-----------------------------------------------------------------------------------------|
| **운동**       | 운동/휴식 상태 인식 기능                | - 운동, 휴식 상태 인식<br>- 휴식 시간 알림                                                  |
|                | 운동 인식 기능                          | - 딥스, 풀업, 푸쉬업, 스쿼트, 데드리프트, 사이드 레터럴 레이즈, 컬                          |
|                | 운동 자세 피드백 기능                   | - 텍스트로 피드백<br>- 음성으로 피드백<br>- 교정 부위 빨간색으로 시각화하여 피드백                 |
|                | 운동 횟수 측정 기능                     | - 운동 종류별 횟수 알림<br>- 운동 종류별 횟수 자동 기록                                      |
| **식단**       | 음식 영양 성분 및 칼로리 계산 기능       | - 사용자가 업로드한 식단 사진을 분석하여 자동으로 영양성분 및 칼로리를 계산하고 제공 및 저장             |
| **위험 상황**  | 위험 상황 인지 및 대처 기능              | - 위험 상황 감지(낙상)<br>- 위험 상황 감지 시 긴급 연락처로 경고 출력<br>- 낙상 감지 영상 저장 기능<br>- 실제 상황일 경우 119 긴급 호출 기능 |
| **사용자 등록** | 사용자 등록 기능                        | - 이름, 성별, 생년월일, 전화번호, 긴급 연락처 설정<br>- 키, 체중, 체지방률, 골격근량 설정             |
| **목표 설정**  | 사용자 목표 설정 기능                    | - 목표 몸무게, 체지방률, 골격근량, 시작일, 종료일 설정                                      |
| **기록 확인**  | 사용자 기록 확인 기능                    | - 사용자가 설정한 기간의 운동 기록 확인<br>- 사용자가 설정한 기간의 식단 기록 확인<br>- 사용자가 설정한 기간의 체성분 기록 확인 |
| **추천**  | 사용자 맞춤 식단 및 운동 추천 기능        | - 사용자의 체성분 기록, 목표, 운동량을 바탕으로 목표 탄수화물, 단백질, 지방량과 그에 맞는 식단 추천 제공<br>- 사용자의 체성분 기록, 식단을 바탕으로 운동 루틴 추천 |
| **예측** | 사용자 체성분 예측 기능                 | - 사용자의 누적된 운동, 식단 기록, 체성분을 분석하여 미래 체성분(몸무게, 체지방률, 골격근량) 예측 제공 |

## 기술 스택
| **구분**            | **상세**                                                                                   |
|---------------------|-------------------------------------------------------------------------------------------|
| **개발 언어**     | ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)        |
| **개발 환경**     | ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange?logo=ubuntu&logoColor=white) ![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-orange?logo=amazonaws&logoColor=white)  ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white) |
| **UI**           | ![PyQt](https://img.shields.io/badge/PYQT5-green?logo=qt&logoColor=white)                   |
| **DBMS**         | ![MySQL](https://img.shields.io/badge/MySQL-5.7-blue?logo=mysql&logoColor=white)            |
| **AI/DL**        | ![TensorFlow](https://img.shields.io/badge/TensorFlow-orange?logo=tensorflow&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-red?logo=pytorch&logoColor=white) ![YOLO](https://img.shields.io/badge/YOLO-yellow?logo=googlecolab&logoColor=white) ![Mediapipe](https://img.shields.io/badge/Mediapipe-brightgreen?logo=mediapipe&logoColor=white) |
| **협업 도구**     | ![Jira](https://img.shields.io/badge/Jira-blue?logo=jira&logoColor=white) ![Confluence](https://img.shields.io/badge/Confluence-blue?logo=confluence&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-purple?logo=slack&logoColor=white) |
| **소스 버전 관리** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)                   |


## 팀원 및 역할

| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **조성현**  | • 위험 상황 관리 기능 개발 <br/> • DB 구성 및 Jira, Confluence, Github 관리                            |
| **김재현**  | • 운동 인식 및 피드백 기능 개발 <br/> • 사용자 맞춤 식단 및 운동 추천 기능 개발 <br/> • 사용자 체성분 예측 기능 개발            |
| **함동균**  | • 시스템 통합(Server) <br/> • 음식 분류 및 양 측정 기능 개발                                          |
| **김선웅**  | • GUI 개발 <br/> · 회원가입, • 사용자 건강 목표 설정 기능 개발 <br/> • 사용자 기록 확인 기능 개발 |
| **문세희**  | • Data Labeling <br/> • 데이터 수집 및 기술 조사                                                    |


### 2.프로젝트 설계
#### 2-1. 기능리스트</br>

#### 2-2. 시스템 구성도</br>

#### 2-3. 데이터 베이스</br>
![image](https://github.com/user-attachments/assets/831ba3ec-e54a-4dec-982d-b7453a00e328)</br>

#### 2-4. GUI 화면 구성도</br>

#### 2-5. 시퀀스 다이어그램</br>



### 3.기능 구현
#### 3-1. </br>



최근 1인 가구가 점차 늘어나는 경향에 따라 1인 관리 서비스가 많이 보편화되는 상황입니다.</br></br>
그러나 기존의 개인 식단 케어 서비스는 사용자가 직접 입력해야 하는 번거로움이 있으며, 개인 운동 케어 서비스는 혼자 운동하는 사람들이 정확한 자세를 잡기에 피드백이 부족한 점이 있습니다.
또한 1인 가구에서 일어나는 낙상사고와 같은 위험 상황은 홀로 대처하기 힘들며, 자칫 잘못하면 매우 위험한 상황까지 이를수 있습니다.</br></br>
이러한 점에서 저희 NahonLab 팀은 Deep Learning(LSTM, GRU, Yolov8) 모델 기반의 1인 관리 서비스를 제공함으로써, 혼자서도 운동, 식단, 건강 관리 가능한 서비스를 제안하고자 합니다. </br>













