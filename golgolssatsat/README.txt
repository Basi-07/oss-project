프로젝트 명: 골골샅샅 (여행 기록 지도 애플리케이션)
1. 프로젝트 개요
전국 228개 시군구를 여행하며 자신만의 지도를 사진으로 채워나가는 개인용 여행 기록 웹 애플리케이션입니다. Flask 기반의 백엔드와 순수 HTML, CSS, JavaScript로 구성된 프론트엔드로 개발되었습니다.

주요 기능
회원가입 및 로그인: 개인별 여행 기록을 관리합니다.

여행 기록: 특정 지역에 대한 사진, 방문 날짜, 메모, 태그를 저장하고 수정할 수 있습니다.

대한민국 전도 시각화: 기록을 남긴 지역이 대한민국 전도 위에 업로드한 사진으로 표시됩니다.

여행 통계: 전체 진행률, 도/광역시별 방문 분포, 월별 여행 기록을 차트로 시각화하여 제공합니다.

룰렛 추천: 아직 방문하지 않은 지역 중 한 곳을 무작위로 추천받을 수 있습니다.

개인화 설정: 다크 모드, 선호하는 길찾기 앱(카카오맵/네이버지도)을 선택하고 저장하는 기능을 제공합니다.

2. 사전 준비 사항
본 프로젝트를 실행하기 위해서는 아래의 소프트웨어가 설치되어 있어야 합니다.

Python 3.x 버전: Python 공식 홈페이지에서 설치할 수 있습니다.

pip: Python 설치 시 함께 설치되는 패키지 관리자입니다.

3. 설치 및 실행 방법
3.1. 필요한 라이브러리 설치
프로젝트 실행에 필요한 Python 라이브러리는 Flask 하나입니다. 아래 명령어를 터미널(Windows의 경우 명령 프롬프트 또는 PowerShell)에 입력하여 설치합니다.

pip install Flask

3.2. 프로젝트 실행
터미널을 열고, 제출된 프로젝트의 backend 폴더로 이동합니다.

# 예시: cd C:\Users\YourName\Desktop\GOLGOLSSATSAT\backend
cd 경로/GOLGOLSSATSAT/backend

아래 명령어를 입력하여 Flask 애플리케이션을 실행합니다.

python app.py

실행 후 터미널에 다음과 같은 메시지가 나타나면 정상적으로 서버가 구동된 것입니다.

 * Running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/) (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: ...

웹 브라우저를 열고 주소창에 아래 주소를 입력하여 접속합니다.

http://127.0.0.1:5000