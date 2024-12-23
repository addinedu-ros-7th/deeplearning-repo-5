![image](https://github.com/user-attachments/assets/035e085e-c6a9-4e67-be6d-4700480d66dd)
# 솔로를 위한 인공지능 헬스케어 서비스

# 1. 프로젝트 소개
## 1-1. 목표
- 운동, 식단, 위험 상황 관리를 통합하여 개인의 건강을 AI로 관리하는 서비스 개발

## 1-2. 주제 선정 배경
- 1인 가구의 증가
- 기존 서비스는 운동, 식단 기록을 사용자가 직접 작성해야 함
- 운동, 식단, 위험 요소를 통합 관리하는 서비스의 부재

## 1-3. User Requirements
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

## 1-4. 팀원 및 역할
| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **조성현**<br/>**(팀장)**  | • 위험 상황 관리 기능 개발 <br/> • DB 구성 및 Jira, Confluence, Github 관리                            |
| **김재현**  | • 운동 인식 및 피드백 기능 개발 <br/> • 사용자 맞춤 식단 및 운동 추천 기능 개발 <br/> • 사용자 체성분 예측 기능 개발            |
| **함동균**  | • 시스템 통합(Server) <br/> • 음식 분류 및 양 측정 기능 개발                                          |
| **김선웅**  | • GUI 개발 <br/> · 회원가입, • 사용자 건강 목표 설정 기능 개발 <br/> • 사용자 기록 확인 기능 개발 |
| **문세희**  | • Data Labeling <br/> • 데이터 수집 및 기술 조사                                                    |

## 1-5. 활용 기술
| **구분**            | **상세**                                                                                   |
|---------------------|-------------------------------------------------------------------------------------------|
| **개발 언어**     | ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)        |
| **개발 환경**     | ![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange?logo=ubuntu&logoColor=white) ![Amazon RDS](https://img.shields.io/badge/Amazon%20RDS-orange?logo=amazonaws&logoColor=white)  ![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white) |
| **UI**           | ![PyQt](https://img.shields.io/badge/PYQT5-green?logo=qt&logoColor=white)                   |
| **DBMS**         | ![MySQL](https://img.shields.io/badge/MySQL-5.7-blue?logo=mysql&logoColor=white)            |
| **AI/DL**        | ![TensorFlow](https://img.shields.io/badge/TensorFlow-orange?logo=tensorflow&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-red?logo=pytorch&logoColor=white) ![YOLO](https://img.shields.io/badge/YOLO-yellow?logo=googlecolab&logoColor=white) ![Mediapipe](https://img.shields.io/badge/Mediapipe-brightgreen?logo=mediapipe&logoColor=white) |
| **협업 도구**     | ![Jira](https://img.shields.io/badge/Jira-blue?logo=jira&logoColor=white) ![Confluence](https://img.shields.io/badge/Confluence-blue?logo=confluence&logoColor=white) ![Slack](https://img.shields.io/badge/Slack-purple?logo=slack&logoColor=white) |
| **소스 버전 관리** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)                   |

# 2.설계
## 2-1. Main Functions
![image](https://github.com/user-attachments/assets/ac47e508-e241-46de-be41-355b5fb416bf)

## 2-2. System Architecture
![image](https://github.com/user-attachments/assets/e0d874b7-46b2-4341-a7ce-8efe42a4988a)

## 2-3. ERD
![image](https://github.com/user-attachments/assets/831ba3ec-e54a-4dec-982d-b7453a00e328)</br>

## 2-4. Sequence Diagram
![image](https://github.com/user-attachments/assets/8f55f1a4-486c-410f-9acb-d89ada9927ce)

## 2-5. User Scenario
![image](https://github.com/user-attachments/assets/a1c8eb59-2350-4f8b-814c-7ac822af44c5)

## 2-6. 화면 구성도</br>




# 3. 기능
## 3-1. 회원 가입

## 3-2. 식단 관리

## 3-3. 운동 인식 및 피드백

## 3-4. 위험 상황 관리

## 3-5. 사용자 기록 확인 / 운동 및 식단 추천 / 체성분 예측 기능




# 4. 주요 기술

## 4-1. 회원 관리

## 4-2. 음식

## 4-3. 운동

## 4-4. 위험 상황

## 4-5. 사용자 맞춤 음식 추천 기능

## 4-6. 사용자 맞춤 운동 추천 기능

## 4-7. 사용자 체성분 예측 추천 기능

# 5. 결론

## 5-1. 통합 테스트 결과

## 5-2. 통합 영상

## 5-3. 프로젝트 후기 및 고찰











