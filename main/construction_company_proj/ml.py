"""연도별 정보 경계를 지키는 회귀 모델입니다."""
import numpy as np
import pandas as pd
from core import LABELS
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

FEATURES = ["operating_margin", "roa", "debt_ratio", "current_ratio", "equity_ratio", "ocf_to_revenue", "revenue_growth", "assets_growth", "margin_change", "log_assets"]

def feature_frame(df):
    """같은 기업·기준의 연속된 다음 연도만 정답으로 연결합니다."""
    data = df.sort_values(["corp_name","year"]).copy()
    data["log_assets"] = np.log1p(data.assets.where(data.assets > 0))
    nxt = data.groupby("corp_name").shift(-1)
    valid = nxt.year.eq(data.year + 1) & nxt.fs_type.eq(data.fs_type)
    data["target"] = nxt.operating_margin.where(valid)
    data["target_year"] = data.year + 1
    # 비교 기준선도 당해 연도까지의 같은 기준·연속 3년만 사용합니다.
    prev = data.groupby("corp_name").shift(1)
    prev2 = data.groupby("corp_name").shift(2)
    eligible = prev.year.eq(data.year-1) & prev2.year.eq(data.year-2) & prev.fs_type.eq(data.fs_type) & prev2.fs_type.eq(data.fs_type)
    data["mean3"] = ((data.operating_margin+prev.operating_margin+prev2.operating_margin)/3).where(eligible)
    return data.replace([np.inf,-np.inf],np.nan)

def new_model():
    """학습 자료로만 결측 보완과 표준화를 학습하는 Ridge 회귀를 만듭니다."""
    return make_pipeline(SimpleImputer(strategy="median",keep_empty_features=True),StandardScaler(),Ridge(alpha=10.0))

def evaluate(data, base_year):
    """2022년까지의 정답으로 학습하고 그 이후 알려진 정답으로 검증합니다."""
    cutoff = min(2022, base_year-2)
    train = data[data.target_year.le(cutoff) & data.target.notna()]
    test = data[data.target_year.gt(cutoff) & data.target_year.le(base_year) & data.target.notna() & data.mean3.notna()]
    if len(train)<60 or len(test)<10: return pd.DataFrame(), None
    model = new_model().fit(train[FEATURES],train.target)
    predictions = {"Ridge 회귀":model.predict(test[FEATURES]),"전년도 값":test.operating_margin,"최근 3년 평균":test.mean3}
    rows=[]
    for name, pred in predictions.items():
        rows.append({"방식":name,"MAE(%p)":mean_absolute_error(test.target,pred)*100,"RMSE(%p)":root_mean_squared_error(test.target,pred)*100,"R²":r2_score(test.target,pred)})
    return pd.DataFrame(rows), {"cutoff":cutoff,"train_count":len(train),"test_count":len(test),"test_start":int(test.target_year.min()),"test_end":int(test.target_year.max())}

def predict_ml(df, company, base_year):
    """기준 연도까지 정답이 알려진 기업·연도만 학습해 차년도를 예측합니다."""
    data = feature_frame(df[df.year.le(base_year)])
    train = data[data.target.notna() & data.target_year.le(base_year)]
    current = data[data.corp_name.eq(company) & data.year.eq(base_year)]
    if len(train)<60 or train.target_year.nunique()<3:
        return {"ok":False,"message":"회귀 학습에 필요한 과거 자료가 부족합니다. 기준 연도를 늦춰 주세요."}
    if current.empty or current[FEATURES].notna().sum(axis=1).iloc[0]<5:
        return {"ok":False,"message":"선택 기업의 예측 입력 자료가 부족합니다."}
    model = new_model().fit(train[FEATURES],train.target)
    value = float(model.predict(current[FEATURES])[0])
    scores, split = evaluate(data,base_year)
    shown = current[FEATURES].copy()
    for field in FEATURES:
        if field != "log_assets": shown[field] *= 100
    shown = shown.rename(columns={**LABELS, "log_assets":"자산 규모(자연로그)"})
    return {"ok":True,"value":value,"target_year":int(base_year)+1,"train_count":len(train),"train_target_end":int(train.target_year.max()),"features":shown.T.rename(columns={current.index[0]:"입력값"}),"scores":scores,"split":split}
