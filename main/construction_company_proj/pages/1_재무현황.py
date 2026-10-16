import streamlit as st
from core import GROUPS, AMOUNTS, LABELS
from ui import get_data, companies, format_value, basis_note, display_series, financial_table

st.set_page_config(page_title="재무현황", layout="wide")
st.title("기업 재무현황")
df = get_data()
names = companies(df)
company = st.selectbox("기업", names, index=names.index("현대건설") if "현대건설" in names else 0)
history = df[df.corp_name == company].sort_values("year")
year = st.selectbox("조회 연도", sorted(history.year.unique(), reverse=True))
row = history[history.year == year].iloc[0]
st.caption(f"{year}년 재무제표 구분: {row.fs_type}")
st.subheader("주요 재무 규모")
columns = st.columns(3)
for i, (field, label) in enumerate(AMOUNTS.items()):
    columns[i % 3].metric(label, format_value(row[field]), border=True)
for title, fields in GROUPS.items():
    st.subheader(title)
    cols = st.columns(min(4, len(fields)))
    for i, (field, label) in enumerate(fields.items()):
        value = display_series(row[[field]], field).iloc[0]
        cols[i % len(cols)].metric(label, "자료 없음" if value != value else f"{value:,.2f}", border=True)
st.caption("ROA=당기순이익/기말자산, ROE=당기순이익/기말자본. 성장률은 동일 재무제표 기준의 연속된 전년 대비이며, 전년 분모가 0 이하이면 표시하지 않습니다.")
if row.equity <= 0:
    st.warning("자본이 0 이하입니다. ROE와 부채비율의 부호를 일반적인 우열로 해석하지 마세요.")
st.subheader("연도별 지표 추이")
metric = st.selectbox("추이 지표", list(LABELS), index=list(LABELS).index("operating_margin"), format_func=LABELS.get)
chart = display_series(history.set_index("year")[[metric]], metric).rename(columns=LABELS)
if chart.dropna().empty:
    st.warning("선택 지표의 추이 자료가 없습니다.")
else:
    st.line_chart(chart, x_label="연도", y_label=LABELS[metric])
st.subheader("연도별 상세 재무정보")
st.caption("지표는 세로로, 연도는 가로로 정리했습니다. 파란 열은 선택한 조회 연도이며, 붉은 숫자는 음수입니다.")
sections = {"재무 규모": {k: LABELS[k] for k in AMOUNTS}, **GROUPS}
tabs = st.tabs(list(sections))
for tab, (title, fields) in zip(tabs, sections.items()):
    with tab:
        table = history.set_index("year")[list(fields)].copy().sort_index(ascending=False)
        for field in table: table[field] = display_series(table[field], field)
        table = table.rename(columns=LABELS).T
        table.columns = table.columns.map(str)
        financial_table(table, highlight_column=str(year))
basis_note(history)
