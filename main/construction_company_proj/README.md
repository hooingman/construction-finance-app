# 건설기업 재무분석

Streamlit으로 재무현황 조회, 기업 2~3개 비교, Ridge 회귀 및 최근 3년 평균 기반 차년도 영업이익률 예측을 제공한다.
Python 3.12에서 검증한다. Render 배포 전 로컬 프로토타입이다.

## 설치·실행

프로젝트 폴더에서 다음을 실행한다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

브라우저에서 터미널에 표시된 로컬 주소를 연다. 종료는 Ctrl+C, 재시작은 같은 실행 명령을 사용한다.
운영 실행만 필요하면 requirements.txt를 사용한다.

## 검증

```bash
python -m pytest -q
```

검증 결과: Python 3.12의 개발 환경과 별도 가상환경에서 각각 pytest 15개 통과. pip check도 통과했다. Chromium 검증 결과와 화면 캡처는 artifacts/에 기록한다.

core.py는 계산과 검증, ui.py는 CSV 캐시와 표시, pages/는 화면이다.
데이터는 파일 위치 기준으로 읽으므로 다른 작업 디렉터리에서도 접근할 수 있다.
출처·단위·결측 정책은 data/README.md, 기능과 제외 범위는 SPEC.md에 있다.

## 시연 순서

1. 홈에서 문제와 사용자를 설명한다.
2. 재무현황: 현대건설·2024년 선택, 지표 3개와 추이 확인.
3. 비교: 현대건설·GS건설, 2024년의 지표와 차트 확인.
4. 예측: 현대건설·2024년 기준 → Ridge 회귀의 2025년 예상값과 입력 지표·평가 확인.
5. 기준 연도를 2015년으로 바꾸고 자료 부족 안내 확인.

앱 지표는 저장된 RAW에서 재구성했고, 6개 원천 계정 2,274건을 대조했다. 데이터 검증 보고서는 data/VALIDATION_REPORT.md에 있다. 큰 음수는 RAW와 일치하므로 보존했다. 현재 DART의 정정 공시를 다시 조회하지는 않았다.
예상값은 과거 평균이며 미래 수익성을 보장하지 않는다.

## 검증 재현

저장된 RAW에서 데이터와 근거를 다시 만들려면 저장소 루트에서 실행한다.

```bash
main/construction_company_proj/.venv/bin/python main/construction_company_proj/scripts/validate_data.py --raw dart_test/data/dart_construction_full_raw.csv --previous dart_test/data/dart_construction_full_ml.csv
```

브라우저 검증은 앱 폴더에서 별도 도구를 설치한 뒤 실행한다.

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python scripts/browser_check.py
```

브라우저 스크립트는 임시 로컬 서버를 기동하고 종료한다. 화면 캡처와 WebM 백업 영상은 artifacts/에 저장한다. 영상은 Git에서 제외한다.
검증한 전체 패키지 버전은 requirements-verified.txt에 기록되어 있다. 동일한 Python 3.12에서 이 파일로 설치하면 테스트 환경의 패키지 버전을 재현할 수 있다.

## 배포 전 남은 사람의 확인

동료 리뷰와 발표 리허설은 SCENARIO.md의 확인표를 사용한다.
Render 입력값은 DEPLOYMENT.md에 정리했다. 서비스 생성과 실제 배포는 수행하지 않았다.

## 재무분석·회귀 확장

재무현황에 금액 6개와 수익성·안정성·성장성·현금흐름 지표를 표시하며, 추이 지표를 선택하고 연도별 상세 표를 볼 수 있다. 기업 비교는 같은 네 분류의 표와 분류별 선택 차트를 제공한다.
예측은 Ridge 회귀가 기본이며, 최근 3년 평균도 선택할 수 있다. 시간 경계, 입력 변수, 평가 지표와 한계는 ML_DESIGN.md에 기록했다.
이전 15개 테스트·배포 준비 보고서는 당시 MVP의 기록이다. 최신 확장 검증은 FEATURE_UPDATE_REPORT.md를 참고한다. 이전 시연 영상과 캡처는 새 검증 실행으로 교체한다.
