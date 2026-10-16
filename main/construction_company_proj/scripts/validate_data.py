"""저장된 DART RAW에서 앱 지표를 재구성하고 계정별 근거를 남깁니다."""
import argparse
import hashlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    "assets": ("Assets", ["자산총계"]),
    "net_income": ("ProfitLoss", ["당기순이익", "당기순이익(손실)", "당기순손익"]),
    "operating_cash_flow": ("CashFlowsFromUsedInOperatingActivities", ["영업활동현금흐름", "영업활동으로 인한 현금흐름", "영업활동으로부터의 현금흐름"]),
    "investing_cash_flow": ("CashFlowsFromUsedInInvestingActivities", ["투자활동현금흐름", "투자활동으로 인한 현금흐름"]),
    "financing_cash_flow": ("CashFlowsFromUsedInFinancingActivities", ["재무활동현금흐름", "재무활동으로 인한 현금흐름"]),
    "revenue": ("Revenue", ["매출액", "수익(매출액)", "영업수익", "매출", "수익", "수익 합계"]),
    "operating_profit": ("dart_OperatingIncomeLoss", ["영업이익", "영업이익(손실)", "영업손익", "영업손실"]),
    "equity": ("Equity", ["자본총계"]),
    "liabilities": ("Liabilities", ["부채총계"]),
    "current_assets": ("CurrentAssets", ["유동자산", "유동자산 합계"]),
    "current_liabilities": ("CurrentLiabilities", ["유동부채", "유동부채 합계"]),
}

def extract(group, field):
    """재무제표 종류·통화를 제한하고 표준 ID 우선으로 계정을 선택합니다."""
    suffix, aliases = FIELDS[field]
    section = ["CF"] if field.endswith("cash_flow") else (["IS", "CIS"] if field in ["revenue", "operating_profit", "net_income"] else ["BS"])
    valid = group[group.sj_div.isin(section) & group.currency.eq("KRW") & group.account_detail.fillna("-").eq("-")].copy()
    valid["number"] = pd.to_numeric(valid.thstrm_amount.astype(str).str.replace(",", "", regex=False), errors="coerce")
    ids = [suffix] if suffix.startswith("dart_") else ["ifrs_"+suffix,"ifrs-full_"+suffix]
    match = valid[valid.account_id.isin(ids)].dropna(subset=["number"])
    method = "account_id"
    if match.empty:
        match = valid[valid.account_nm.str.replace(" ", "", regex=False).isin([x.replace(" ", "") for x in aliases])].dropna(subset=["number"])
        method = "account_nm"
    if match.empty:
        return float("nan"), {"status":"missing"}
    if match.number.nunique() > 1:
        return float("nan"), {"status":"conflict", "values":str(match.number.tolist())}
    row = match.iloc[0]
    return float(row.number), {"status":"matched", "method":method, "account_id":row.account_id,
        "account_nm":row.account_nm,"sj_div":row.sj_div,"rcept_no":row.rcept_no,"amount":row.number}

def build(raw_path, previous_path, output):
    """모든 기업 연도의 근거·변경내역·보고서와 최소 앱 데이터셋을 생성합니다."""
    raw = pd.read_csv(raw_path, dtype=str)
    old = pd.read_csv(previous_path)
    rows, evidence = [], []
    for (company, year, basis), group in raw.groupby(["corp_name","bsns_year","fs_type_used"], sort=True):
        row = {"corp_name":company,"year":int(year),"fs_type":basis}
        for field in FIELDS:
            row[field], proof = extract(group, field)
            evidence.append({**{k:row[k] for k in ["corp_name","year","fs_type"]},"field":field, **proof})
        for metric, numerator, denominator in [("operating_margin","operating_profit","revenue"),("debt_ratio","liabilities","equity"),("current_ratio","current_assets","current_liabilities"),("roa","net_income","assets"),("roe","net_income","equity"),("net_margin","net_income","revenue"),("ocf_to_revenue","operating_cash_flow","revenue"),("equity_ratio","equity","assets")]:
            den = row[denominator]
            row[metric] = row[numerator] / den if pd.notna(den) and den != 0 else float("nan")
        rows.append(row)
    data = pd.DataFrame(rows).sort_values(["corp_name","year"])
    if data.duplicated(["corp_name","year"]).any():
        raise ValueError("동일 기업·연도에 여러 재무제표 기준이 있습니다.")
    changes = []
    merged = data.merge(old, on=["corp_name","year"],suffixes=("_new","_old"),validate="one_to_one")
    for field in [*FIELDS,"operating_margin","debt_ratio","current_ratio"]:
        for _, row in merged.iterrows():
            if field+"_old" not in row.index: continue
            a,b = row[field+"_old"],row[field+"_new"]
            if (pd.isna(a) and pd.isna(b)) or (pd.notna(a) and pd.notna(b) and abs(a-b) <= max(abs(a),abs(b),1)*1e-10): continue
            changes.append({"corp_name":row.corp_name,"year":row.year,"field":field,"old":a,"new":b})
    output.mkdir(parents=True, exist_ok=True)
    data.to_csv(output/"financials.csv",index=False)
    pd.DataFrame(evidence).to_csv(output/"account_evidence.csv",index=False)
    pd.DataFrame(changes,columns=["corp_name","year","field","old","new"]).to_csv(output/"data_changes.csv",index=False)
    counts = pd.DataFrame(evidence).status.value_counts().to_dict()
    report = ["# 데이터 검증 보고서", "", "검증 범위: 저장된 OpenDART RAW와 앱 지표의 일치 여부. 현재 DART 공시를 재조회한 검증은 아니다.",
        "",f"- RAW SHA256: `{hashlib.sha256(raw_path.read_bytes()).hexdigest()}`",f"- RAW: {len(raw):,}행",f"- 앱: {len(data)}행, {data.corp_name.nunique()}개 기업, {data.year.min()}~{data.year.max()}년",f"- 계정 추출 결과: {counts}",f"- 기존 full_ml 대비 변경: {len(changes)}개 셀", "", "## 검증 방식", "", "BS(재무상태표)와 IS/CIS(손익)를 구분하고 KRW·총계 계정만 사용했다. 표준 account_id를 우선하고 계정명은 보조로 사용했다. 서로 다른 값이 충돌하면 결측으로 남겼다. 비율은 추출한 원천 값으로 재계산했다.", "", "## 잔여 결측", ""]
    for field in [*FIELDS,"operating_margin","debt_ratio","current_ratio"]:
        report.append(f"- {field}: {data[field].isna().sum()}개")
    report += ["", "## 큰 음수 영업이익률", "", "아래 값은 저장된 RAW의 매출액과 영업이익으로 재계산한 값이다. 임의로 삭제하거나 보정하지 않았다.", ""]
    for _,row in data[data.operating_margin < -1].iterrows(): report.append(f"- {row.corp_name} {row.year}: {row.operating_margin*100:.2f}% (매출액 {row.revenue:,.0f}원, 영업이익 {row.operating_profit:,.0f}원)")
    report += ["", "## 확인 사례", "", "현대건설·GS건설 및 KD·범양건영·신세계건설을 포함한 모든 기업·연도의 계정 근거는 account_evidence.csv에 있다. KD의 '수익 합계', 범양건영의 번호가 붙은 계정명, 신세계건설의 '영업손실'처럼 이름으로만 추출할 때 누락되던 항목을 표준 ID로 복구했다.", "", "## 한계", "", "정정 공시·수집 시점·회사 범위 적절성은 별도 검토 대상이다. 연결/별도 혼재는 보존하고 화면에서 안내한다. 이 결과는 저장된 RAW에 대한 재현 가능한 대조 결과다."]
    (output/"VALIDATION_REPORT.md").write_text("\n".join(report)+"\n")
    print("rows",len(data),"status",counts,"changes",len(changes))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw",type=Path,required=True)
    parser.add_argument("--previous",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=ROOT/"data")
    args=parser.parse_args()
    build(args.raw,args.previous,args.output)
