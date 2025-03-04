![image](https://github.com/user-attachments/assets/035e085e-c6a9-4e67-be6d-4700480d66dd)
# 솔로를 위한 인공지능 헬스케어 서비스

## 👉 [통합 영상](https://youtu.be/33UZJujoVBs?si=Ll3DOmD68eE4wvqI)

## 👉 [발표 자료](https://docs.google.com/presentation/d/1dvwK7o6es8Wn-Mrr18u-DYbreAsfyP4J_0AuqXVFU0I/edit?usp=sharing)

# 1. 프로젝트 소개
## 1-1. 목표
- 운동, 식단, 위험 상황 관리를 통합하여 개인의 건강을 AI로 관리하는 서비스 개발

## 1-2. 주제 선정 배경
<table align="center">
    <tr>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/77cb9819-889d-4405-a102-508dab830497" alt="1인 가구 증가 추세" width="300"/>
        </td>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/1b72f7fe-e6e0-4e7d-9575-6ada1c015f36" alt="사용자가 직접 입력해야 하는 기존 서비스" width="300"/>
        </td>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/d7168063-9a82-4169-8809-5e12fcabe6ff" alt="운동, 식단, 위험 통합 관리 부재" width="300"/>
        </td>
    </tr>
    <tr>
        <td align="center">
            <p><strong>1인 가구 증가</strong></p>
        </td>
        <td align="center">
            <p><strong>사용자가 직접 기록(기존 서비스)</strong></p>
        </td>
        <td align="center">
            <p><strong>통합 건강 관리 서비스 부재</strong></p>
        </td>
    </tr>
</table>


### 1인 가구 증가
- 혼자서도 식단 관리와 운동을 돕는 헬스케어 서비스 수요 증가
### 기존 서비스의 문제점
- 식단 관리: 사용자가 직접 데이터를 입력해야 하는 번거로움
- 운동 관리: 실시간 자세 피드백 제공의 어려움
- 응급 상황: 혼자 사는 사람들은 낙상 등 사고 발생 시 신속히 대처하기 어려움
### 해결 방안
- 딥러닝 기술을 활용하여 운동, 식단, 건강 관리 기능을 통합한 서비스 개발

## 1-3. 팀원 및 역할
| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **조성현**<br/>**(팀장)**  | • 위험 상황 관리 기능 개발                             |
| **김재현**  | • 운동 동작 인식 및 자세 피드백 기능 개발 <br/> • 사용자 맞춤 식단 및 운동 추천 기능 개발 <br/> • 사용자 체성분 예측 기능 개발            |
| **함동균**  | • 시스템 통합(Server) <br/> • 음식 분류 및 양 측정 기능 개발                                          |
| **김선웅**  | • GUI 개발 <br/> • 사용자 등록, 건강 목표 설정 기능 개발 <br/> • 사용자 통계 확인 기능 개발 |

## 1-4. 활용 기술
| **구분**          | **상세**                                                                                                  |
|:------------------:|---------------------------------------------------------------------------------------------------------|
| **개발환경**       | <img src="https://img.shields.io/badge/Ubuntu 22.04-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/> <img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white"/> |
| **개발언어**       | <img src="https://img.shields.io/badge/Python 3.10-3776AB?style=for-the-badge&logo=Python&logoColor=white"/> |
| **UI**             | <img src="https://img.shields.io/badge/PYQT5-41CD52?style=for-the-badge&logo=cplusplus&logoColor=white"/> <img src="https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white"/> |
| **DBMS**           | <img src="https://img.shields.io/badge/MYSQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/> |
| **AI/DL**          | <img src="https://img.shields.io/badge/Tensorflow-FF6F00?style=for-the-badge&logo=Tensorflow&logoColor=white"/> <img src="https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white"/> <img src="https://img.shields.io/badge/Yolov8-F2E142?style=for-the-badge&logo=elegoo&logoColor=white"/> <img src="https://img.shields.io/badge/Mediapipe-0097A7?style=for-the-badge&logo=mediapipe&logoColor=white"/> |
| **API**            | <img src="https://img.shields.io/badge/KakaoTalk Message API-FFCD00?style=for-the-badge&logo=kakao&logoColor=black"/> <img src="https://img.shields.io/badge/USDA FoodData Central API-8DC63F?style=for-the-badge&logo=leaflet&logoColor=white"/> |
| **협업 도구**      | <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> <img src="https://img.shields.io/badge/confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/>  <img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> |
| **소스 버전 관리** | <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"/> |





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
| **식단**       | 음식 영양 성분 분석 기능       | • 업로드한 식단 사진을 분석하여 영양 성분 및 칼로리를 계산하여 제공<br>• 음식 양 수정 및 저장  |

![solcare_user_food_1_V1](https://github.com/user-attachments/assets/ad7f3650-0871-4ec4-84c3-be8d42829f54)

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

## 4-2. 프로젝트 리뷰 및 개선 방안
### 클래스의 부족으로 인한 분석 한계
- 음식 모델의 클래스가 11개로 부족하여 세분화된 분석이 어려움.
- 위험 상황 모델 또한 낙상/정상 상태만 구별 가능하여 다양한 상황을 처리하기에는 한계.
### 일반 알고리즘을 활용한 대체 구현
- 음식 양 측정, 식단 및 운동 추천, 운동 시 관절의 부정확한 자세 구별 기능도 딥러닝 기술로 구현하고자 함.
- 데이터의 부족으로 이를 대체하기 위해 일반 알고리즘을 적용하여 기능을 구현.
### 개발 환경의 불일치
- TensorFlow 및 PyTorch 기반 모델을 하나의 서버에서 동작시키는 과정에서 라이브러리 간 호환성 문제 발생.
- 이를 해결하기 위해 서버를 분리하여 각 모델의 독립성을 보장하고 환경 충돌 문제를 해결.
### 향후 개선 방안
- Docker와 같은 가상화 도구를 활용해 팀원 간 개발 환경을 통일.
- 실제 서비스 출시를 통해 사용자 데이터를 추가적으로 수집하고, 이를 활용해 딥러닝 기반의 고도화된 서비스로 발전시킬 예정.

