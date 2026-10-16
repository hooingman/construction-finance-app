# 데이터 안내

출처: 저장된 OpenDART 원본 `dart_test/data/dart_construction_full_raw.csv`에서 재구성한 `financials.csv`.
수집 코드: `dart_test/collect_dart_data.py`. 이 앱은 실시간 API 호출 없이 CSV를 읽는다.

- 35개 기업, 2015~2025년, 379행·22열. 기업별 수록 기간은 다를 수 있다.
- 선택 이유: MUST 기능의 6개 원천 계정을 RAW에서 추출해 비율 3개를 일관되게 재계산했다.
- RAW 대조 결과는 VALIDATION_REPORT.md, 계정별 근거는 account_evidence.csv, 기존 full_ml 대비 변경은 data_changes.csv를 참고한다. 현재 DART 정정 공시를 재조회한 검증은 아니다.
- 기업·연도 중복은 허용하지 않는다. 숫자 변환 실패와 무한값은 결측 처리한다.
- CFS는 연결, OFS는 별도 재무제표다. 혼재 시 안내하며 합치거나 임의 변환하지 않는다.
- 결측값은 0으로 대체하지 않는다. 큰 음수도 임의 삭제·보정하지 않는다.

| 사용 열 | 의미 | 원본 단위 |
|---|---|---|
| corp_name | 기업명 | 문자열 |
| year | 실적 연도 | 정수 |
| fs_type | 재무제표 구분 | CFS/OFS |
| revenue | 매출액 | 원, 화면은 억 원 |
| operating_margin | 영업이익 / 매출액 | 소수 비율, 화면은 ×100% |
| debt_ratio | 부채 / 자본 | 소수 비율, 화면은 ×100% |
| current_ratio | 유동자산 / 유동부채 | 소수 비율, 화면은 ×100% |

영업이익·자본·부채·유동자산·유동부채 원천 열을 함께 보관한다. 미래 정답 열은 앱 데이터에 포함하지 않는다.
예측은 기준 연도 T의 T-2~T 연속 3개년 영업이익률이 모두 있을 때만 평균을 계산한다.

## 재무분석 확장

RAW에서 assets, net_income, operating_cash_flow, investing_cash_flow, financing_cash_flow를 추가 추출했다. 현금흐름은 CF, 순이익은 IS/CIS, 자산은 BS에서 가져온다. 표준 계정 ID 우선 원칙은 동일하다.
ROA=순이익/기말자산, ROE=순이익/기말자본, 순이익률=순이익/매출액, 자기자본비율=자본/자산, 영업현금흐름비율=영업현금흐름/매출액이다. 원본 단위는 금액은 원, 비율은 소수다.
net_income은 CNT85 2015·상지건설 2018 두 건을 확정하지 못해 결측으로 남겼다. 관련 ROA·ROE도 결측이다.
로딩 시 동일 기업·동일 기준의 연속 전년 대비 revenue_growth·assets_growth·margin_change를 생성한다. 증가율은 전년 분모가 양수일 때만 계산하며 margin_change는 비율 차이로 화면에서 ×100해 %p로 표시한다.
회귀 입력에서 결측은 학습 집합의 중앙값으로만 보완한다. 이는 화면의 결측을 0으로 채우는 것과 구분된다. 미래 정답은 ml.py에서 같은 기업·같은 기준의 실제 다음 해와 연결한다.
