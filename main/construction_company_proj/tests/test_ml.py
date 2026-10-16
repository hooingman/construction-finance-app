import pandas as pd
import pytest
from pathlib import Path
from core import load_financials
from ml import feature_frame, predict_ml, FEATURES

DATA = Path(__file__).resolve().parents[1]/"data/financials.csv"

def test_future_changes_do_not_change_prediction():
    df=load_financials(DATA)
    a=predict_ml(df,"현대건설",2023)
    df.loc[df.year>2023,"operating_margin"]=999
    b=predict_ml(df,"현대건설",2023)
    assert a["ok"] and a["train_target_end"]<=2023
    assert a["value"] == pytest.approx(b["value"])
    assert not {"target", "next_operating_margin", "profitability_improved"} & set(FEATURES)

def test_gap_and_basis_changes_do_not_create_targets_or_growth(tmp_path):
    df=load_financials(DATA)
    df=df[df.corp_name=="현대건설"].copy()
    df=df[df.year!=2022]
    df.loc[df.year==2024,"fs_type"]="OFS"
    data=feature_frame(df)
    assert data.loc[data.year.isin([2021,2023,2024]),"target"].isna().all()
    path=tmp_path/"gap.csv";df.to_csv(path,index=False)
    loaded=load_financials(path)
    assert loaded.loc[loaded.year.isin([2023,2024]),"revenue_growth"].isna().all()

def test_annual_evaluation_uses_same_rows_and_chronology():
    result=predict_ml(load_financials(DATA),"현대건설",2025)
    assert result["split"]["cutoff"]==2022
    assert result["split"]["test_start"]==2023
    assert result["split"]["test_end"]==2025
    assert len(result["scores"])==3
    assert (result["scores"]["MAE(%p)"]>=0).all()
