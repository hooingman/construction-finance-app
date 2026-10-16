import streamlit as st
from core import comparison, GROUPS, LABELS
from ui import get_data, companies, basis_note, display_series, financial_table

st.set_page_config(page_title="기업 비교", layout="wide")
st.title("기업 간 재무지표 비교")
df = get_data()
names = companies(df)
defaults = [c for c in ["현대건설", "GS건설"] if c in names]
selected = st.multiselect("비교할 기업을 2~3개 선택해 주세요", names, default=defaults or names[:2], max_selections=3)
if len(selected) < 2:
    st.warning("비교하려면 기업을 2개 이상 선택해 주세요.")
    st.stop()
years = sorted(set.intersection(*[set(df.loc[df.corp_name == c, "year"]) for c in selected]), reverse=True)
if not years:
    st.warning("선택한 기업의 공통 연도가 없습니다.")
    st.stop()
year = st.selectbox("공통 비교 연도", years)
view = comparison(df, selected, year)
st.caption(f"{year}년 동일 연도 비교 · " + " / ".join(f"{company}: {view.loc[company, 'fs_type']}" for company in selected))
st.caption("기업별 수치를 같은 행에서 비교해 보세요. 붉은 숫자는 음수이며, 지표의 좋고 나쁨을 뜻하지 않습니다.")
notes = {
    "수익성": "이익을 얼마나 남겼는지 살펴봅니다. ROA·ROE는 기말 자산·자본 기준입니다.",
    "안정성": "부채 부담과 유동성을 살펴봅니다. 지표마다 해석 방향이 다릅니다.",
    "성장성": "전년 대비 규모와 수익성 변화를 살펴봅니다. 변화폭의 단위는 %p입니다.",
    "현금흐름": "현금의 유입·유출을 살펴봅니다. 금액은 억 원 단위입니다.",
}
for title, fields in GROUPS.items():
    with st.container(border=True):
        st.subheader(title)
        st.caption(notes[title])
        table = view[list(fields)].copy()
        for field in fields: table[field] = display_series(table[field], field)
        financial_table(table.rename(columns=LABELS).T)
st.divider()
category = st.selectbox("차트 분류", list(GROUPS))
fields = GROUPS[category]
metric = st.selectbox("차트 지표", list(fields),format_func=fields.get)
chart = display_series(view[[metric]],metric).dropna().rename(columns=LABELS)
if chart.empty:
    st.warning("선택 지표의 비교 자료가 없습니다.")
else:
    st.bar_chart(chart, y_label=LABELS[metric])
    if len(chart) < len(selected): st.info("자료가 없는 기업은 차트에서 제외했습니다.")
st.caption("성장률: 동일 기준의 연속 전년 대비. ROA·ROE: 기말 자산·자본 기준. 자본이 음수이면 ROE·부채비율 해석에 주의해 주세요.")
basis_note(view)
