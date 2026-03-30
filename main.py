import os
import requests
from playwright.sync_api import sync_playwright

# 1. 從雲端環境變數讀取機密資料（避免帳密外洩）
USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    """將結果發送到 Telegram"""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    requests.post(url, json=payload)

def main():
    # 啟動自動化瀏覽器
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # headless=True 代表在雲端背景默默執行
        page = browser.new_page()

        try:
            # 2. 前往目標網頁的登入畫面
            page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx")

            # 3. 尋找輸入框並自動填寫帳號密碼，接著點擊登入
            page.fill("input[name='UserName']", USERNAME)
            page.fill("input[name='Password']", PASSWORD)
            page.click("input[type='submit']")

            # 4. 等待登入完成，並抓取目標資訊（需替換為目標網頁的實際元素名稱）
            try:
                page.wait_for_selector(".target-data-class", timeout=10000)  # 10 秒超時
                data = page.inner_text(".target-data-class")
            except Exception as e:
                raise Exception(f"數據選擇器未找到：{e}")

            # 5. 組合訊息並回報
            message = f"【系統自動回報】\n今日抓取到的最新數據為：\n{data}"
            send_telegram_message(message)

        except Exception as e:
            send_telegram_message(f"抓取失敗，錯誤訊息：{e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()