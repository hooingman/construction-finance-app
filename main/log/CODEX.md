# 프로젝트: 이탈 위험 체크 서비스 (Streamlit) — ★ 내 주제로 고쳐 쓴다 (4주차 체크포인트 1 직후)
## 구조
- app.py 홈, pages/ 화면, core.py 로직(streamlit import 금지), data/ CSV
- 데이터 로드는 @st.cache_data, 경로는 app.py 기준 상대 경로
## 코딩 규칙
- Python 3, streamlit, pandas. 새 패키지는 설치하기 전에 먼저 물어볼 것 (설치하면 requirements.txt에도 추가)
- 함수에는 한글 docstring, 화면 문구는 한국어 존댓말
- 빈 결과·잘못된 입력에서 오류 대신 st.warning
- 열 이름은 data/README.md의 목록만 사용 (지어내지 말 것)
## 하지 말 것
- 요청한 파일 외 수정, 전체 재작성, 비밀값 하드코딩
- 이 폴더(~/work/<프로젝트>) 밖의 파일 접근, rm -rf / sudo 실행
## 검증
- core.py 수정 시 python -m pytest -q 를 실행해 결과를 알려 줄 것
- 화면 파일 수정 후에는 "streamlit run app.py 로 확인하라"고 알려 줄 것 (실행은 내가 한다)
