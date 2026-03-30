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
    print("啟動腳本...")
    # 啟動自動化瀏覽器
    with sync_playwright() as p:
        print("啟動瀏覽器...")
        browser = p.chromium.launch(headless=True) # headless=True 代表在雲端背景默默執行
        page = browser.new_page()
        print("新頁面創建完成")

        try:
            # 2. 前往目標網頁的登入畫面
            print("前往登入頁面...")
            page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx")
            page.wait_for_load_state('networkidle')  # 等待頁面加載完成
            print("頁面加載完成")
            page.screenshot(path="login_page.png")  # 截圖登入頁面

            # 檢查輸入框
            inputs = page.query_selector_all("input")
            print(f"找到 {len(inputs)} 個輸入框")
            for i, inp in enumerate(inputs):
                name = inp.get_attribute("name") or "無名稱"
                id_ = inp.get_attribute("id") or "無ID"
                type_ = inp.get_attribute("type") or "無類型"
                print(f"輸入框 {i}: name='{name}', id='{id_}', type='{type_}'")

            # 3. 尋找輸入框並自動填寫帳號密碼，接著點擊登入
            print("填寫登入表單...")
            page.fill("input[name='txtUName']", USERNAME)
            page.fill("input[name='txtPwd']", PASSWORD)
            page.click("input[name='butLogin']")
            page.wait_for_load_state('networkidle')  # 等待登入完成
            print("登入完成")
            page.screenshot(path="after_login.png")  # 截圖登入後頁面

            # 4. 等待登入完成，並抓取目標資訊（需替換為目標網頁的實際元素名稱）
            print("等待數據元素...")
            try:
                page.wait_for_selector(".target-data-class", timeout=10000)  # 10 秒超時
                data = page.inner_text(".target-data-class")
                print(f"抓取到數據：{data}")
            except Exception as e:
                raise Exception(f"數據選擇器未找到：{e}")

            # 5. 組合訊息並回報
            message = f"【系統自動回報】\n今日抓取到的最新數據為：\n{data}"
            print("發送 Telegram 消息...")
            send_telegram_message(message)
            print("消息發送完成")

        except Exception as e:
            print(f"錯誤：{e}")
            send_telegram_message(f"抓取失敗，錯誤訊息：{e}")
        finally:
            print("關閉瀏覽器...")
            browser.close()
            print("腳本結束")

if __name__ == "__main__":
    main()