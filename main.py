import os
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("⚠️ 未設定 Telegram Token 或 Chat ID")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    requests.post(url, json=payload)

def main():
    print("啟動腳本...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("前往登入頁面...")
            page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx")
            page.wait_for_load_state('networkidle')

            print("填寫登入表單...")
            page.fill("input[name='txtUName']", USERNAME)
            page.fill("input[name='txtPwd']", PASSWORD)
            page.click("input[name='butLogin']")
            page.wait_for_load_state('networkidle')

            print("等待數據表格出現...")
            page.wait_for_selector("#gvBedStatus", timeout=10000)
            page.wait_for_timeout(2000) 
            
            rows = page.locator("#gvBedStatus tr:not(.gvBedStatusHead)").all()
            
            data_list = []
            for row in rows:
                cols = row.locator("td").all_inner_texts()
                if len(cols) >= 3:
                    data_list.append(f"🏥 {cols[0]} | 🛏️ {cols[1]} | ⏱️ 已過時間: {cols[2]}")

            if data_list:
                data_str = "\n".join(data_list)
                message = f"【清床系統自動回報】\n目前待處理的任務：\n\n{data_str}"
            else:
                message = "【清床系統自動回報】\n目前系統中沒有待處理的清床任務。🎉"

            send_telegram_message(message)

        except Exception as e:
            send_telegram_message(f"抓取失敗，錯誤訊息：\n{e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
