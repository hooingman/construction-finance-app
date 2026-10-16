"""재무자료 검증과 규칙 기반 예측 계산."""
from pathlib import Path
import pandas as pd

RATIOS = {"operating_margin": "영업이익률(%)", "debt_ratio": "부채비율(%)", "current_ratio": "유동비율(%)"}
GROUPS = {
    "수익성": {"operating_margin":"영업이익률(%)", "net_margin":"순이익률(%)", "roa":"ROA(%)", "roe":"ROE(%)"},
    "안정성": {"debt_ratio":"부채비율(%)", "current_ratio":"유동비율(%)", "equity_ratio":"자기자본비율(%)"},
    "성장성": {"revenue_growth":"매출액 증가율(%)", "assets_growth":"자산 증가율(%)", "margin_change":"영업이익률 변화(%p)"},
    "현금흐름": {"operating_cash_flow":"영업활동현금흐름(억 원)", "investing_cash_flow":"투자활동현금흐름(억 원)", "financing_cash_flow":"재무활동현금흐름(억 원)", "ocf_to_revenue":"매출액 대비 영업현금흐름(%)"},
}
AMOUNTS = {"revenue":"매출액", "operating_profit":"영업이익", "net_income":"당기순이익", "assets":"자산총계", "liabilities":"부채총계", "equity":"자본총계"}
LABELS = {**{k:v+"(억 원)" for k,v in AMOUNTS.items()}, **{k:v for group in GROUPS.values() for k,v in group.items()}}
REQUIRED = ["corp_name", "year", "fs_type", *AMOUNTS, *[k for group in GROUPS.values() for k in group if k not in ["revenue_growth", "assets_growth", "margin_change"]]]

def load_financials(path):
    """필수 열·기업 연도 중복을 확인하고 숫자와 결측을 정리합니다."""
    df = pd.read_csv(Path(path), dtype={"stock_code": str, "corp_code": str})
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError("필수 열이 없습니다: " + ", ".join(sorted(missing)))
    if df.empty or df[["corp_name", "year", "fs_type"]].isna().any().any():
        raise ValueError("기업·연도·재무제표 구분을 확인해 주세요.")
    years = pd.to_numeric(df["year"], errors="coerce")
    if years.isna().any() or (years % 1 != 0).any():
        raise ValueError("연도는 정수여야 합니다.")
    df["year"] = years.astype(int)
    if df.duplicated(["corp_name", "year"]).any():
        raise ValueError("기업·연도 중복 자료가 있습니다.")
    for col in [c for c in df.columns if c not in ["corp_name", "year", "fs_type", "stock_code", "corp_code"]]:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace([float("inf"), -float("inf")], float("nan"))
    df = df.sort_values(["corp_name", "year"]).reset_index(drop=True)
    previous = df.groupby("corp_name").shift(1)
    consecutive = df.year.eq(previous.year + 1) & df.fs_type.eq(previous.fs_type)
    for field in ["revenue", "assets"]:
        if field in df:
            df[field+"_growth"] = (df[field] / previous[field] - 1).where(consecutive & previous[field].gt(0))
    df["margin_change"] = (df.operating_margin - previous.operating_margin).where(consecutive)
    return df

def predict_margin(df, company, year):
    """기준 연도까지 연속된 3개년의 평균으로 다음 해를 예상합니다."""
    years = list(range(int(year) - 2, int(year) + 1))
    history = df.loc[(df.corp_name == company) & df.year.isin(years), ["year", "operating_margin", "fs_type"]].sort_values("year")
    if history.year.tolist() != years or history.operating_margin.isna().any():
        return {"ok": False, "message": "연속된 최근 3개년 영업이익률 자료가 모두 필요합니다."}
    if history.fs_type.nunique() != 1:
        return {"ok": False, "message": "최근 3년의 연결·별도 재무제표 기준이 달라 평균을 계산하지 않습니다."}
    return {"ok": True, "company": company, "base_year": int(year), "target_year": int(year) + 1,
            "value": float(history.operating_margin.mean()), "history": history.copy()}

def comparison(df, companies, year):
    """선택 기업의 동일 연도 자료를 정렬하고 없는 자료도 유지합니다."""
    if not 2 <= len(set(companies)) <= 3:
        raise ValueError("기업을 2~3개 선택해 주세요.")
    view = df.loc[(df.corp_name.isin(companies)) & (df.year == year)].set_index("corp_name")
    return view.reindex(companies)[["fs_type", *[c for c in LABELS if c in view.columns]]]
