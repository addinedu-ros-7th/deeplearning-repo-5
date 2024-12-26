![image](https://github.com/user-attachments/assets/035e085e-c6a9-4e67-be6d-4700480d66dd)
# 솔로를 위한 인공지능 헬스케어 서비스

## [통합 영상](https://youtube.com/shorts/AUdVKNk_UV8?si=kb7C2WoPwqL_4VAp)

# 1. 프로젝트 소개
## 1-1. 목표
- 운동, 식단, 위험 상황 관리를 통합하여 개인의 건강을 AI로 관리하는 서비스 개발

## 1-2. 주제 선정 배경
![Screenshot from 2024-12-26 14-09-25](https://github.com/user-attachments/assets/93e342cf-d736-40bb-b5fc-1afbf7224505)
- 1인 가구의 증가 추세
- 사용자가 직접 운동, 식단 기록 해야 하는 기존 서비스의 불편함
- 운동, 식단, 위험 요소를 통합 관리하는 서비스의 부재

최근 발표한 통계청 자료에 의하면 2050년까지 1인 가구가 점차 늘어 전체 인구의 약 40% 비율을 1인가구가 차지할 것으로 예측하였습니다. 또한 2022년 대비 현재 1인 가구 생활비 지출은 2.1% 증가하면서 1인 생활 소비가 증가하고 있는 추세입니다.</br></br>
그래서 최근들어 1인 관리 서비스들이 늘어나고 있지만 기존의 개인 식단 케어 서비스는 사용자가 직접 입력해야 하는 번거로움이 있으며, 개인 운동 케어 서비스는 혼자 운동하는 사람들이 정확한 자세를 잡기에 피드백이 부족한 점이 있습니다.
더 나아가 1인 가구에서 일어나는 낙상사고와 같은 위험 상황은 홀로 대처하기 힘들며, 자칫 잘못하면 매우 위험한 상황까지 이를수 있습니다.</br></br>
이러한 점에서 저희 NahonLab 팀은 Deep Learning(LSTM, GRU, Yolov8) 모델 기반의 1인 AI 서비스를 제공함으로써, 혼자서도 운동, 식단, 건강 관리 가능한 서비스를 제안하고자 합니다. </br>

## 1-3. 팀원 및 역할
| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **조성현**<br/>**(팀장)**  | • 위험 상황 관리 기능 개발 <br/> • DB 구성 및 Jira, Confluence, Github 관리                            |
| **김재현**  | • 운동 동작 인식 및 자세 피드백 기능 개발 <br/> • 사용자 맞춤 식단 및 운동 추천 기능 개발 <br/> • 사용자 체성분 예측 기능 개발            |
| **함동균**  | • 시스템 통합(Server) <br/> • 음식 분류 및 양 측정 기능 개발                                          |
| **김선웅**  | • GUI 개발 <br/> • 사용자 등록, 건강 목표 설정 기능 개발 <br/> • 사용자 통계 확인 기능 개발 |
| **문세희**  | • Data Labeling <br/> • 데이터 수집 및 기술 조사                                                    |

## 1-4. 활용 기술
| **구분**            | **상세**                                                                                   |
|---------------------|-------------------------------------------------------------------------------------------|
| **개발 언어**     | ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)        |
| **개발 환경**     | ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange?logo=ubuntu&logoColor=white) ![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-orange?logo=amazonaws&logoColor=white)  ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white) |
| **UI**           | ![PyQt](https://img.shields.io/badge/PYQT5-green?logo=qt&logoColor=white)                   |
| **DBMS**         | ![MySQL](https://img.shields.io/badge/MySQL-5.7-blue?logo=mysql&logoColor=white)            |
| **AI/DL**        | ![TensorFlow](https://img.shields.io/badge/TensorFlow-orange?logo=tensorflow&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-red?logo=pytorch&logoColor=white) ![YOLO](https://img.shields.io/badge/YOLO-yellow?logo=googlecolab&logoColor=white) ![Mediapipe](https://img.shields.io/badge/Mediapipe-brightgreen?logo=mediapipe&logoColor=white) |
| **협업 도구**     | ![Jira](https://img.shields.io/badge/Jira-blue?logo=jira&logoColor=white) ![Confluence](https://img.shields.io/badge/Confluence-blue?logo=confluence&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-purple?logo=slack&logoColor=white) |
| **소스 버전 관리** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)                   |

# 2. 설계
## 2-1. 주요 기능
![image](https://github.com/user-attachments/assets/496c7d39-755c-4297-ae55-dd8ff5789fd9)

## 2-2. 시스템 구성도
![image](https://github.com/user-attachments/assets/e0d874b7-46b2-4341-a7ce-8efe42a4988a)

## 2-3. ERD
![image](https://github.com/user-attachments/assets/831ba3ec-e54a-4dec-982d-b7453a00e328)</br>

## 2-4. 시퀀스 다이어그램
![image](https://github.com/user-attachments/assets/8f55f1a4-486c-410f-9acb-d89ada9927ce)

## 2-5. 사용자 시나리오
![image](https://github.com/user-attachments/assets/a1c8eb59-2350-4f8b-814c-7ac822af44c5)
 
# 3. 기능
## 3-1. 회원 가입

| **분류**       | **기능**                                | **설명**                                                                                 |
|:----------------:|---------------------------------------|-----------------------------------------------------------------------------------------|
| **사용자 등록** | 사용자 등록 기능                        | • 이름, 성별, 생년월일, 전화번호, 긴급 연락처 설정<br>• 키, 체중, 체지방률, 골격근량 설정             |
| **목표 설정**  | 사용자 목표 설정 기능                    | • 목표 몸무게, 체지방률, 골격근량, 시작일, 종료일 설정                                      |

<img src="https://github.com/user-attachments/assets/4926146c-48c0-405a-9531-8924b227a553" alt="solcare_user_stat_V1" width="300"/>

## 3-2. 식단 관리

| **분류**       | **기능**                                | **설명**                                                                                 |
|:----------------:|---------------------------------------|-----------------------------------------------------------------------------------------|
| **식단**       | 음식 영양 성분 분석 기능       | • 사용자가 업로드한 식단 사진을 분석하여 영양 성분 및 칼로리를 계산하여 제공 및 저장<br>• 음식 양 수정 기능  |

![solcare_user_foodphoto_V2_gif_V4](https://github.com/user-attachments/assets/40569ffa-61b2-4dd4-9bb0-0d11e19232ea)


## 3-3. 운동 인식 및 피드백

| **분류** | **기능**            | **설명**                                                                 |
|:--------------:|---------------------|-------------------------------------------------------------------------|
| **운동**       | 운동/휴식 상태 인식 기능                | • 운동, 휴식 상태 인식<br>• 휴식 시간 알림                                                  |
|                | 운동 동작 인식 기능                     | • 딥스, 풀업, 푸쉬업, 스쿼트, 데드리프트, 사이드 레터럴 레이즈, 컬                          |
|                | 운동 자세 피드백 기능                   | • 텍스트로 피드백<br>• 음성으로 피드백<br>• 교정 부위 빨간색으로 시각화하여 피드백                 |
|                | 운동 횟수 측정 기능                     | • 운동 종류별 횟수 측정<br>• 운동 종류별 횟수 자동 저장                                      |

<img src="https://github.com/user-attachments/assets/d47fa289-09fd-413c-afdd-b2fc737d4cbd" alt="pullup_test_V2" width="300" />
<img src="https://github.com/user-attachments/assets/9d459f2b-5507-47ed-a476-11758c86fa60" alt="pullup_test_V2" width="300" />


## 3-4. 위험 상황 관리

| **분류**       | **기능**                                | **설명**                                                                                 |
|:----------------:|---------------------------------------|-----------------------------------------------------------------------------------------|
| **위험 상황**  | 위험 상황 인지 및 대처 기능              | • 위험 상황 감지(낙상)<br>• 감지 영상 저장<br>• 위험 상황 감지시 비상 연락처로 연락 |

<img src="https://github.com/user-attachments/assets/49be0b5e-cb74-4451-b5d9-3047bc7c39b4" alt="solcare_user_stat_V1" width="300"/>

## 3-5. 통계, 추천, 예측

| **분류** | **기능**            | **설명**                                                                 |
|:--------------:|---------------------|-------------------------------------------------------------------------|
| **통계**    | 식단 통계 확인       | • 사용자가 설정한 기간의 식단 기록 확인                                      |
|              | 운동 통계 확인       | • 사용자가 설정한 기간의 운동 기록 확인                                      |
|              | 체성분 통계 확인       | • 사용자가 설정한 기간의 체성분 기록 확인                                      |
| **추천**         | 식단 추천            | • 식단 추천 버튼을 클릭하면 사용자 맞춤 식단 추천 제공                          |
|              | 운동 추천            | • 운동 추천 버튼을 클릭하면 사용자 맞춤 운동 추천 제공                          |
| **예측**         | 체성분 예측          | • 체성분 예측 버튼을 클릭하면 미래 체성분 예측 제공                            |

<img src="https://github.com/user-attachments/assets/d03357b1-282a-4cf0-bae8-e54f3f0bec55" alt="solcare_user_stat_V1" width="300"/>

# 4. 결론

## 4-1. 통합 테스트 결과
| **기능**       | **설명**                                                                                  | **결과** |
|:---------------------:|--------------------------------------------------------------------------------------------------|:------------:|
| **식단**            | • 촬영한 식단 사진을 분석하여 영양 성분(탄수화물, 단백질, 지방량)과 칼로리를 사용자에게 제공 후 저장                 | pass       |
| **운동**            | • 운동/휴식 상태 감지, 휴식 시간 측정                                                              | pass       |
|                     | • 운동 동작 인식(딥스, 풀업, 푸시업, 스쿼트, 데드리프트, 사이드 레터럴 레이즈, 컬)하여 동작별 횟수 자동 저장           | pass       |
|                     | • 운동 동작별 잘못된 자세에 대한 피드백 (텍스트, 음성, 관절 시각화 제공)                              | pass       |
| **위험 상황**       | • 웹캠에서 낙상 감지 시 보호자의 GUI에 위험 상황 알림                                                | pass       |
|                     | • 비상 연락처에 문자 전송                                                                          | pass       |
| **기록 확인**       | • 오늘의 음식 목표량과 섭취량 확인                                                                 | pass       |
|                     | • 오늘의 운동 목표량과 수행량 확인                                                                 | pass       |
|                     | • 사용자가 설정한 기간의 식단 기록 확인                                                            | pass       |
|                     | • 사용자가 설정한 기간의 운동 기록 확인                                                            | pass       |
|                     | • 사용자가 설정한 기간의 위험 상황 기록 확인                                                       | pass       |
| **추천**            | • 식단 추천 버튼을 클릭하면 사용자 맞춤 식단 추천 제공                                              | pass       |
|                     | • 운동 추천 버튼을 클릭하면 사용자 맞춤 운동 추천 제공                                              | pass       |
| **예측**            | • 체성분 예측 버튼을 클릭하면 미래 체성분 예측 제공                                                | pass       |

## 4-2. 프로젝트 리뷰 및 개선점


# 5. 발표 자료
https://docs.google.com/presentation/d/1dvwK7o6es8Wn-Mrr18u-DYbreAsfyP4J_0AuqXVFU0I/edit?usp=sharing












