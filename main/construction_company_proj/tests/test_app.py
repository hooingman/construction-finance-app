from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

def app(name):
    return AppTest.from_file(str(ROOT / name)).run(timeout=30)

def test_home_and_overview():
    for name in ["app.py", "pages/1_재무현황.py"]:
        at = app(name)
        assert not at.exception
        if name == "app.py":
            assert len(at.metric) == 3
        else:
            labels = {m.label for m in at.metric}
            assert {"ROA(%)", "ROE(%)", "유동비율(%)", "영업활동현금흐름(억 원)", "매출액 증가율(%)"} <= labels

def test_comparison_empty_selection():
    at = app("pages/2_기업비교.py")
    assert not at.exception
    at.multiselect[0].set_value([]).run()
    assert not at.exception
    assert at.warning

def test_prediction_and_stale_result():
    at = app("pages/3_영업이익률예측.py")
    at.selectbox[0].select("현대건설").run()
    at.button[0].click().run()
    assert not at.exception
    assert len(at.metric) == 1
    at.selectbox[1].select(2015).run()
    assert len(at.metric) == 0
    at.button[0].click().run()
    assert at.warning
    assert not at.exception


def test_comparison_categories_and_baseline_mode():
    at = app("pages/2_기업비교.py")
    assert {"수익성", "안정성", "성장성", "현금흐름"} <= {h.value for h in at.subheader}
    at.selectbox[1].select("성장성").run()
    assert not at.exception
    assert "revenue_growth" in at.selectbox[2].options or "매출액 증가율(%)" in at.selectbox[2].options
    at = app("pages/3_영업이익률예측.py")
    at.radio[0].set_value("최근 3년 평균").run()
    at.button[0].click().run()
    assert not at.exception
    assert len(at.metric) == 1
