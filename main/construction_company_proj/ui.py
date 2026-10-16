"""공통 데이터 로드와 표시 도우미."""
from pathlib import Path
import pandas as pd
import streamlit as st
from core import load_financials

DATA_PATH = Path(__file__).resolve().parent / "data" / "financials.csv"

@st.cache_data
def cached_data(path, modified):
    """파일이 변경되면 캐시를 갱신하여 CSV를 읽습니다."""
    return load_financials(path)

def get_data():
    """자료 오류를 사용자에게 안내하고 화면 실행을 중단합니다."""
    try:
        return cached_data(str(DATA_PATH), DATA_PATH.stat().st_mtime_ns)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        st.warning(f"재무자료를 불러올 수 없습니다: {exc}")
        st.stop()

def companies(df):
    """기업명을 정렬하여 반환합니다."""
    return sorted(df.corp_name.unique())

def format_value(value, percent=False):
    """결측값과 비율의 표시 형식을 통일합니다."""
    if pd.isna(value):
        return "자료 없음"
    return f"{value * 100:,.2f}%" if percent else f"{value / 100000000:,.1f}억 원"

def basis_note(view):
    """연결·별도 재무제표가 혼재하는 경우 안내합니다."""
    types = set(view.fs_type.dropna())
    st.caption("CFS: 연결재무제표 · OFS: 별도재무제표. 비율은 원본 소수 값을 백분율로 표시합니다.")
    if len(types) > 1:
        st.info("연결·별도 재무제표가 섞여 있습니다. 비교 범위가 다를 수 있으므로 재무제표 구분을 함께 확인해 주세요.")


def display_series(series, field):
    """금액은 억 원, 비율과 변화폭은 백분율 단위로 맞춥니다."""
    scale = 1 / 100000000 if field in ["revenue", "operating_profit", "net_income", "assets", "liabilities", "equity", "operating_cash_flow", "investing_cash_flow", "financing_cash_flow"] else 100
    return series * scale


def financial_table(frame, index_label="지표", highlight_column=None, hide_index=False):
    """숫자 형식을 유지하며 교차 행 배경·음수·선택 연도를 일관되게 표시합니다."""
    table = frame.copy()
    table.columns = table.columns.map(str)
    numeric = table.select_dtypes(include="number").columns.tolist()
    styled = table.style.format("{:,.2f}", subset=numeric, na_rep="자료 없음")
    def row_style(row):
        """교차 행과 선택한 연도를 배경으로 구분합니다."""
        position = table.index.get_loc(row.name)
        background = "#F4F7FB" if position % 2 else "#FFFFFF"
        return [f"background-color: {'#E8F0FE' if str(col) == str(highlight_column) else background}; color: #243247;" for col in table.columns]
    styled = styled.apply(row_style, axis=1)
    if numeric:
        styled = styled.map(lambda value: "color: #B42338; font-weight: 600" if pd.notna(value) and value < 0 else "", subset=numeric)
    table.index.name = index_label
    configs = {"_index": st.column_config.TextColumn(index_label, width="medium", pinned=True)}
    for col in numeric:
        configs[col] = st.column_config.NumberColumn(col, width="medium")
    st.dataframe(styled, width="stretch", height=min(600, 40 + 38 * len(table)), row_height=38,
                 hide_index=hide_index, column_config=configs)
