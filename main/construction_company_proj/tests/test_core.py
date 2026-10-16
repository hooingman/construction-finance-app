from pathlib import Path
import pandas as pd
import pytest
from core import load_financials, predict_margin, comparison

DATA = Path(__file__).resolve().parents[1] / "data/financials.csv"

def sample():
    return pd.DataFrame({"corp_name":["A"]*4, "year":[2021,2022,2023,2024], "operating_margin":[.01,.02,.03,9.0], "fs_type":["CFS"]*4})

def test_prediction_excludes_future():
    result = predict_margin(sample(), "A", 2023)
    assert result["value"] == pytest.approx(.02)
    assert result["target_year"] == 2024
    assert result["history"].year.tolist() == [2021,2022,2023]

@pytest.mark.parametrize("mode", ["gap", "missing", "unknown"])
def test_prediction_requires_three_valid_consecutive_years(mode):
    df = sample()
    if mode == "gap": df = df[df.year != 2022]
    if mode == "missing": df.loc[df.year == 2022, "operating_margin"] = float("nan")
    assert not predict_margin(df, "unknown" if mode == "unknown" else "A", 2023)["ok"]

def test_real_data_and_missing_values():
    df = load_financials(DATA)
    assert len(df) == 379
    assert df.corp_name.nunique() == 35
    assert df.loc[(df.corp_name == "KD") & (df.year == 2023), "revenue"].iloc[0] == pytest.approx(179411200000, rel=.001)
    view = comparison(df, ["현대건설", "GS건설"], 2024)
    assert view.index.tolist() == ["현대건설", "GS건설"]
    assert len(view) == 2

@pytest.mark.parametrize("names", [[], ["현대건설"], ["a","b","c","d"]])
def test_comparison_validates_count(names):
    with pytest.raises(ValueError): comparison(load_financials(DATA), names, 2024)

def test_duplicate_data_rejected(tmp_path):
    df = load_financials(DATA)
    path = tmp_path / "duplicates.csv"
    pd.concat([df, df.iloc[:1]]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="중복"): load_financials(path)

def test_missing_schema_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"year":[2024]}).to_csv(path,index=False)
    with pytest.raises(ValueError, match="필수 열"): load_financials(path)


def test_source_ratios_reconcile():
    df = load_financials(DATA)
    for metric, num, den in [("operating_margin","operating_profit","revenue"),("debt_ratio","liabilities","equity"),("current_ratio","current_assets","current_liabilities")]:
        assert df[metric].notna().all()
        assert df[metric].tolist() == pytest.approx((df[num]/df[den]).tolist())

def test_missing_values_are_not_zero(tmp_path):
    df = load_financials(DATA)
    df.loc[0, "revenue"] = float("nan")
    path = tmp_path / "missing.csv"
    df.to_csv(path,index=False)
    assert pd.isna(load_financials(path).loc[0,"revenue"])


def test_mean_rejects_mixed_statement_basis():
    df=sample()
    df.loc[df.year==2022,"fs_type"]="OFS"
    assert not predict_margin(df,"A",2023)["ok"]
