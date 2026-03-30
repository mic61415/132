import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# 讀取機密資料
USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

def main():
    print("🚀 啟動強化版巡檢腳本...")
    
    with sync_playwright() as p:
        # 啟動瀏覽器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 把等待上限從 30 秒改成 120 秒 (2 分鐘)
        page.set_default_timeout(120000)

        try:
            print("🔗 正在前往登入網頁 (這步最容易超時，我們多等一下)...")
            # 使用 commit 模式：只要伺服器有回應就開始做，不等圖片全部抓完
            page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx", wait_until="commit")
            
            # 額外手動等待 5 秒確保格子跑出來
            page.wait_for_timeout(5000)

            print("📝 填寫帳號密碼...")
            page.fill("input[name='txtUName']", USERNAME)
            page.fill("input[name='txtPwd']", PASSWORD)
            page.click("input[name='butLogin']")
            
            # 登入後也多等一下
            page.wait_for_timeout(5000)

            print("📊 正在讀取清床表格...")
            # 這裡也給它 30 秒的等待時間找表格
            page.wait_for_selector("#gvBedStatus", timeout=30000)
            
            rows = page.locator("#gvBedStatus tr:not(.gvBedStatusHead)").all()
            
            data_list = []
            for row in rows:
                cols = row.locator("td").all_inner_texts()
                if len(cols) >= 3:
                    data_list.append(f"🏥 {cols[0]} | 🛏️ {cols[1]} | ⏱️ {cols[2]}")

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if data_list:
                data_str = "\n".join(data_list)
                message = f"【清床系統回報】\n時間：{now}\n\n待處理任務：\n{data_str}"
            else:
                message = f"【清床系統回報】\n時間：{now}\n目前沒有待處理任務。🎉"

            print("📤 發送通知...")
            send_telegram_message(message)

        except Exception as e:
            error_msg = f"❌ 執行失敗：{e}"
            print(error_msg)
            # 失敗時也發個簡訊讓你知道
            send_telegram_message(f"【系統通知】巡檢遇到困難：網頁加載太慢或出現錯誤。\n錯誤代碼：{str(e)[:100]}")
        finally:
            browser.close()
            print("🏁 任務結束。")

if __name__ == "__main__":
    main()
