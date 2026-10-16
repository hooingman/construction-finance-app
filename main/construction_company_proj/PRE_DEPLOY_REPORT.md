# 배포 전 검증 결과 — 2026-10-16

## 완료

- MUST 기능 3개를 유지하고 추가 기능 없이 검증했다.
- 저장된 RAW 전체 78,714행에서 앱 원천 계정 2,274건을 검증했다. 기존 full_ml의 88개 셀을 복구/재계산했다.
- 379개 기업·연도에서 원천 계정과 주요 비율에 잔여 결측이 없다. 큰 음수는 원본 근거를 확인해 유지했다.
- ml_large의 매출액·영업이익·영업이익률과 값 불일치 0건, 해당 파일의 부채비율 결측 2건 복구.
- Python 3.12 개발 환경과 /tmp의 새 가상환경에서 각각 pytest 15개 통과. pip check 통과.
- 실제 Chromium으로 홈·재무현황·기업비교·예측·자료 부족·오래된 결과 숨김 검증.
- 데스크톱 화면 캡처와 모바일 홈 화면 캡처, 백업 영상 생성.
- SPEC·README·AI_LOG·SCENARIO·Render 설정 준비 문서 작성.
- .venv·비밀값 파일·생성 영상은 Git 제외 대상으로 설정했다.

## 산출물

- data/VALIDATION_REPORT.md: 원본 대조 범위·결과·한계
- data/account_evidence.csv: 기업·연도·계정별 원본 근거
- data/data_changes.csv: 기존 full_ml 대비 변경 내역
- artifacts/BROWSER_REPORT.md: 실제 브라우저 검증 범위
- artifacts/01_home.png ~ 06_mobile_home.png: 화면 캡처
- artifacts/demo.webm: 실제 시연 흐름 백업 영상 (로컬 파일, Git 제외)
- requirements-verified.txt: 새 환경의 검증된 전체 패키지 버전
- DEPLOYMENT.md: 다음 배포 단계에 입력할 설정

## 남은 사항

실제 사람의 동료 리뷰와 타이머 발표 리허설은 SCENARIO.md로 진행한다. 정정 공시 재조회는 이번 저장 RAW 대조에 포함하지 않았다. Render의 실제 Linux 환경 빌드·외부 접속은 배포 후 확인 대상이다. 현재 호스트와 다른 OS/아키텍처를 검증한 것은 아니다.

Git 커밋은 앱 관련 경로만 대상으로 하고, 기존 week1~3 삭제 변경은 포함하지 않는다. 실제 배포와 원격 push는 수행하지 않는다.
