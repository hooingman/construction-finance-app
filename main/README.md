# 건설기업 재무분석 서비스

Streamlit 웹 앱으로 기업별 상세 재무정보, 수익성·안정성·성장성·현금흐름 비교, Ridge 회귀 기반 차년도 영업이익률 예측을 제공한다.

- 앱: construction_company_proj/
- 기획·수업 자료: info/
- 수업 AI 활용 기록: log/AI_LOG.md
- Render Blueprint: render.yaml

## 로컬 실행

```bash
cd main/construction_company_proj
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash start.sh
```

기본 포트는 10000이다. 다른 포트는 `PORT=8501 bash start.sh`로 지정한다.

## Render

저장소 연결 후 Web Service로 생성한다.

| 항목 | 값 |
|---|---|
| Root Directory | main/construction_company_proj |
| Build Command | python -m pip install -r requirements.txt |
| Start Command | bash start.sh |
| Python 환경변수 | PYTHON_VERSION=3.12.3 |
| Health Check Path | /_stcore/health |

Blueprint를 사용하면 경로를 `main/render.yaml`로 지정한다. API 키나 dart_test 폴더는 필요 없다.
세부 사항은 construction_company_proj/DEPLOYMENT.md를 참고한다.

## 검증

별도 복사본에서 pytest 20개와 Render용 실행 스크립트의 HTTP health·실제 Chromium 홈 표시를 확인했다. 실제 Render 서비스에서의 외부 접속 검증은 배포 후 진행한다.
