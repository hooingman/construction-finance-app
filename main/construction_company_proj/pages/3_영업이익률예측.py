import streamlit as st
from core import predict_margin
from ml import predict_ml
from ui import get_data, companies, format_value, basis_note, financial_table

st.set_page_config(page_title="영업이익률 예측", layout="wide")
st.title("차년도 영업이익률 예측")
st.write("재무지표와 전년 대비 변화로 다음 해 영업이익률을 예상합니다. Ridge는 과적합을 줄이도록 계수 크기를 제한하는 선형 회귀입니다.")
df = get_data()
# 기업을 바꿀 때 해당 기업의 연도 목록을 바로 갱신합니다.
company = st.selectbox("예측할 기업", companies(df))
year = st.selectbox("기준 연도", sorted(df.loc[df.corp_name == company, "year"].unique(), reverse=True))
method = st.radio("예측 방식", ["Ridge 회귀", "최근 3년 평균"], horizontal=True)
with st.form("prediction"):
    st.caption(f"{year}년까지의 자료로 {year+1}년을 예상합니다. 연간 실적이 공시된 후 사용할 수 있는 예측입니다.")
    submitted = st.form_submit_button("예상 영업이익률 계산")
if submitted:
    st.session_state["prediction_result"] = (predict_ml(df, company, int(year)) if method == "Ridge 회귀" else predict_margin(df, company, int(year)))
    st.session_state["prediction_key"] = (company, int(year), method)
result = st.session_state.get("prediction_result")
if result and st.session_state.get("prediction_key") == (company, int(year), method):
    if not result["ok"]:
        st.warning(result["message"])
    else:
        st.metric(f"{company} · {result['target_year']}년 예상 영업이익률", format_value(result["value"], True))
        if method == "Ridge 회귀":
            st.caption(f"학습 {result['train_count']}행 · 학습 정답 마지막 연도 {result['train_target_end']}년 · Ridge alpha=10 고정")
            financial_table(result["features"])
            if not result["scores"].empty:
                st.subheader("과거 연도 분할 검증")
                split = result["split"]
                st.caption(f"정답 연도 {split['cutoff']}년까지 학습({split['train_count']}행), {split['test_start']}~{split['test_end']}년 검증({split['test_count']}행). 모든 방식은 동일 검증 행에서 비교합니다. 예측용 재학습 모델과 검증 모델은 구분됩니다.")
                financial_table(result["scores"].set_index("방식"), index_label="예측 방식")
                scores = result["scores"].set_index("방식")
                if scores.loc["Ridge 회귀", "MAE(%p)"] >= scores.loc[["최근 3년 평균", "전년도 값"], "MAE(%p)"].min():
                    st.warning("현재 회귀 모델보다 MAE가 작은 단순 기준선이 있습니다. 머신러닝 적용이 정확도 향상을 보장하지 않습니다.")
            else:
                st.info("연도 분할 평가에 필요한 과거 정답이 부족합니다.")
            st.caption("원본의 큰 손실을 임의 제거하지 않았습니다. 정정 공시 시점까지 재현한 실시간 투자 백테스트는 아닙니다.")
        else:
            st.caption("최근 3년 평균 기반 예상값 · 머신러닝 모델 결과가 아닙니다.")
        if method == "최근 3년 평균":
            history = result["history"]
            shown = history.copy()
            shown["operating_margin"] = shown.operating_margin * 100
            financial_table(shown.set_index("year").rename(columns={"operating_margin":"영업이익률(%)", "fs_type":"재무제표"}).rename_axis("사용 연도"), index_label="사용 연도")
            st.write("계산: 위 3개년 영업이익률의 합 ÷ 3")
            basis_note(history)
else:
    st.info("기업과 기준 연도를 선택한 뒤 계산 버튼을 눌러 주세요.")
