import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    try: requests.post(url, json=payload, timeout=15)
    except: pass

def main():
    print("🔬 進入診斷模式...")
    with sync_playwright() as p:
        # 模擬真人瀏覽器，降低被醫院系統阻擋的機率
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        page.set_default_timeout(60000)

        try:
            print("1. 嘗試連線醫院網址...")
            page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx", wait_until="domcontentloaded")
            print(f"目前網頁標題: {page.title()}")

            print("2. 填寫登入資訊...")
            # 確保欄位真的存在才寫
            page.wait_for_selector("input[name='txtUName']")
            page.fill("input[name='txtUName']", USERNAME)
            page.fill("input[name='txtPwd']", PASSWORD)
            
            print("3. 點擊登入按鈕...")
            page.click("input[name='butLogin']")
            
            # 等待跳轉後的頁面標題
            page.wait_for_timeout(5000)
            print(f"登入後的網頁標題: {page.title()}")

            print("4. 尋找表格內容...")
            # 這裡我們換個方式等，看看表格在哪裡
            page.wait_for_selector("#gvBedStatus", timeout=20000)
            
            rows = page.locator("#gvBedStatus tr:not(.gvBedStatusHead)").all()
            data_list = [f"🏥 {row.locator('td').all_inner_texts()[0]} | ⏱️ {row.locator('td').all_inner_texts()[2]}" for row in rows if len(row.locator('td').all_inner_texts()) >= 3]

            message = f"【巡檢成功】\n時間：{datetime.now().strftime('%H:%M')}\n資料筆數：{len(data_list)} 筆"
            send_telegram_message(message)
            print("✅ 成功完成並發送訊息")

        except Exception as e:
            error_msg = f"❌ 診斷失敗！在哪一步斷掉：{str(e)[:200]}"
            print(error_msg)
            send_telegram_message(f"【系統回報】抓取失敗。原因：{str(e)[:50]}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
