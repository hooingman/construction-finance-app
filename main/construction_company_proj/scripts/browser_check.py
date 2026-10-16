"""실제 Chromium으로 시연 흐름을 확인하고 화면·백업 영상을 저장합니다."""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
BASE = "http://127.0.0.1:18518"

def main():
    """서버를 기동하고 화면 검증 뒤 반드시 종료합니다."""
    OUT.mkdir(exist_ok=True)
    env = {**os.environ, "STREAMLIT_BROWSER_GATHER_USAGE_STATS":"false"}
    log = (OUT/"server.log").open("w")
    proc = subprocess.Popen([sys.executable,"-m","streamlit","run",str(ROOT/"app.py"),"--server.headless=true","--server.port=18518","--server.address=127.0.0.1"],cwd="/tmp",env=env,stdout=log,stderr=log)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(BASE+"/_stcore/health",timeout=1).close()
                break
            except OSError: time.sleep(.1)
        else: raise RuntimeError("서버가 시작되지 않았습니다.")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,args=["--no-sandbox"])
            context = browser.new_context(viewport={"width":1440,"height":1000},record_video_dir=str(OUT/"videos"),record_video_size={"width":1440,"height":1000})
            page = context.new_page()
            page.set_default_timeout(10000)
            errors=[]
            page.on("pageerror",lambda e: errors.append(str(e)))
            page.goto(BASE)
            expect(page.get_by_role("heading",name="🏗️ 건설기업 재무분석")).to_be_visible()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT/"01_home.png"),full_page=True)
            page.wait_for_timeout(10000)
            page.get_by_role("link",name="1. 재무현황",exact=False).click()
            expect(page.get_by_role("heading",name="기업 재무현황")).to_be_visible()
            def choose(label, value):
                """현재 선택을 확인한 후 필요한 경우에만 검색·선택합니다."""
                control = page.get_by_role("combobox", name=label, exact=True)
                expect(control).to_be_visible()
                if control.input_value() != value:
                    control.click()
                    control.fill(value)
                    page.get_by_role("option", name=value, exact=True).click()
                    expect(control).to_have_value(value)
                page.wait_for_timeout(500)
            choose("기업", "현대건설")
            choose("조회 연도", "2024")
            expect(page.get_by_text("2024년 재무제표 구분:",exact=False)).to_be_visible()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT/"02_overview.png"),full_page=True)
            page.wait_for_timeout(15000)
            page.get_by_role("link",name="기업비교",exact=False).click()
            expect(page.get_by_role("heading",name="기업 간 재무지표 비교")).to_be_visible()
            choose("공통 비교 연도", "2024")
            expect(page.locator('[data-testid="stDataFrame"]')).to_have_count(4)
            expect(page.locator('[data-testid="stDataFrame"]').first).to_be_visible()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT/"03_comparison.png"),full_page=True)
            page.wait_for_timeout(15000)
            page.get_by_role("link",name="영업이익률예측",exact=False).click()
            expect(page.get_by_role("heading",name="차년도 영업이익률 예측")).to_be_visible()
            choose("예측할 기업", "현대건설")
            choose("기준 연도", "2024")
            page.get_by_role("button",name="예상 영업이익률 계산").click()
            expect(page.locator('[data-testid="stMetric"]')).to_be_visible()
            expect(page.get_by_text("현대건설 · 2025년 예상 영업이익률",exact=True)).to_be_visible()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT/"04_prediction.png"),full_page=True)
            page.wait_for_timeout(15000)
            choose("기준 연도", "2015")
            expect(page.locator('[data-testid="stMetric"]')).to_have_count(0)
            page.get_by_role("button",name="예상 영업이익률 계산").click()
            expect(page.get_by_text("회귀 학습에 필요한 과거 자료가 부족합니다. 기준 연도를 늦춰 주세요.")).to_be_visible()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT/"05_missing_history.png"),full_page=True)
            page.wait_for_timeout(10000)
            expect(page.locator('[data-testid="stException"]')).to_have_count(0)
            video = page.video
            context.close()
            video.save_as(str(OUT/"demo.webm"))
            mobile = browser.new_context(viewport={"width":390,"height":844},is_mobile=True,device_scale_factor=1)
            mp = mobile.new_page();mp.goto(BASE)
            expect(mp.get_by_role("heading",name="🏗️ 건설기업 재무분석")).to_be_visible()
            expect(mp.locator('[data-testid="stMetric"]')).to_have_count(3)
            mp.wait_for_timeout(1500)
            mp.screenshot(path=str(OUT/"06_mobile_home.png"),full_page=True)
            assert not errors, errors
            mobile.close();browser.close()
        (OUT/"BROWSER_REPORT.md").write_text("# 실제 브라우저 검증\n\nChromium 데스크톱(1440×1000)에서 홈 → 현대건설 2024 상세 조회 → 수익성·안정성·성장성·현금흐름 비교표 4개 → Ridge 회귀 2025 예상값 → 2015 기준 학습 자료 부족 안내를 확인했습니다. 선택 변경 시 오래된 결과가 숨겨지는 것을 확인했습니다. JS pageerror 0건, 마지막 화면 Streamlit 예외 0건. 모바일(390×844)은 홈 표시만 확인했습니다. 모든 모바일 화면 검증이나 실제 동료 리뷰를 의미하지 않습니다.\n\n화면 캡처 6개와 demo.webm 백업 영상을 저장했습니다.\n")
        print("browser check passed; screenshots and demo.webm saved")
    finally:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill();proc.wait()
        log.close()

if __name__ == "__main__": main()
