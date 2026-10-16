import streamlit as st
from ui import get_data

st.set_page_config(page_title="건설기업 재무분석", page_icon="🏗️", layout="wide")
st.title("🏗️ 건설기업 재무분석")
st.write("보유 건설기업의 재무상태를 비교하고 다음 해 수익성을 가늠해 보세요.")
st.info("건설업종 종목 2~3개를 보유하고, 실적 발표 전에 다음 해 수익성을 살펴보려는 개인 투자자를 위한 서비스입니다.")
df = get_data()
a,b,c = st.columns(3)
a.metric("기업 수", f"{df.corp_name.nunique()}개")
b.metric("수록 기간", f"{df.year.min()}~{df.year.max()}")
c.metric("기업·연도 자료", f"{len(df)}행")
st.page_link("pages/1_재무현황.py", label="1. 재무현황 — 주요 지표와 영업이익률 추이", icon="📈")
st.page_link("pages/2_기업비교.py", label="2. 기업 비교 — 수익성·안정성·성장성·현금흐름 비교", icon="📊")
st.page_link("pages/3_영업이익률예측.py", label="3. 영업이익률 예측 — 회귀 모델과 최근 3년 평균 예상값", icon="🔎")
st.caption("출처: OpenDART 수집 CSV · Ridge 회귀와 최근 3년 평균을 비교합니다. 누락값은 0으로 대체하지 않습니다.")
