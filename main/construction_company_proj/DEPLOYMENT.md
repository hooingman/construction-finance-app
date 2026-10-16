# Render 실행 및 배포

## 준비된 파일

- `main/render.yaml`: Render Blueprint 설정
- `start.sh`: 앱 경로에서 Streamlit을 실행하고 Render의 PORT를 사용
- `requirements.txt`: 앱 실행 패키지
- `data/financials.csv`: 실행용 데이터. dart_test 폴더나 DART API 키는 필요 없음

## Blueprint로 연결

Render에서 New → Blueprint → GitHub 저장소 `hooingman/construction-finance-app`를 선택한다.
Blueprint Path는 **main/render.yaml**로 지정한다. 설정을 확인하고 배포한다.
이 파일을 GitHub에 올리는 것만으로 Render 서비스가 생성되지는 않는다.

## Web Service로 직접 연결

| 설정 | 값 |
|---|---|
| Runtime | Python |
| Branch | main |
| Root Directory | main/construction_company_proj |
| Build Command | python -m pip install -r requirements.txt |
| Start Command | bash start.sh |
| Health Check Path | /_stcore/health |
| PYTHON_VERSION | 3.12.3 |
| OPENBLAS_NUM_THREADS | 1 |
| OMP_NUM_THREADS | 1 |

Static Site가 아닌 Web Service로 생성한다. API 키와 데이터베이스는 필요 없다.
Python 버전은 현재 검증한 버전을 지정했다. 앱 폴더에서 실행하므로 Streamlit 테마도 함께 로드한다.

## 로컬에서 같은 실행 방식 확인

앱 폴더에서 가상환경을 활성화한 뒤 `PORT=10000 bash start.sh`로 실행한다.
인터넷에서 접속 가능한 실제 Render 주소의 확인은 서비스 생성 후 수행한다.
배포 완료 후 홈·상세 조회·기업 비교·회귀 예측과 WebSocket 갱신을 다시 확인한다.

## 업로드 범위

이번 업로드는 main/ 아래 파일만 반영한다. dart_test, 가상환경, 캐시, 비밀값, 생성 영상은 제외한다.
저장소에 이미 있던 수업 자료는 삭제하지 않는다. 원본 RAW 재추출 스크립트는 보관하지만 앱 실행에는 필요 없다.

공식 근거: [Blueprint 설정](https://render.com/docs/blueprint-spec), [Web Service](https://render.com/docs/web-services), [Python 버전](https://render.com/docs/python-version).
