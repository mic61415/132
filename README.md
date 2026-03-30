import os
import requests
import time
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright

# 1. 從雲端環境變數讀取機密資料（避免帳密外洩）
USERNAME = os.getenv("MY_USERNAME")
PASSWORD = os.getenv("MY_PASSWORD")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram_message(text):
    """將結果發送到 Telegram"""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("⚠️ 未設定 Telegram Token 或 Chat ID，無法發送訊息。")
        return
        
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    requests.post(url, json=payload)

def fetch_and_report():
    """執行一次抓取任務"""
    print(f"\n{'='*60}")
    print(f"開始執行定時任務 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 啟動自動化瀏覽器
    with sync_playwright() as p:
        try:
            print("啟動瀏覽器...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print("新頁面創建完成")

            # 前往登入頁面
            print("前往登入頁面...")
            page.set_default_timeout(120000)
            try:
                page.goto("https://eporter.skh.org.tw/eBTSController/frmLogin.aspx", timeout=120000)
            except:
                print("⚠️ 頁面加載超時，但繼續嘗試...")
                pass
            page.wait_for_timeout(3000)
            print("頁面加載完成")

            # 填寫登入表單
            print("填寫登入表單...")
            page.fill("input[name='txtUName']", USERNAME)
            page.fill("input[name='txtPwd']", PASSWORD)
            page.click("input[name='butLogin']")
            
            page.wait_for_load_state('networkidle')
            print("登入完成，進入儀表板")

            # 等待並抓取清床任務表格
            print("等待數據表格出現...")
            try:
                page.wait_for_selector("#gvBedStatus", timeout=10000)
                page.wait_for_timeout(2000)
                
                rows = page.locator("#gvBedStatus tr:not(.gvBedStatusHead)").all()
                print(f"表格載入完畢，共找到 {len(rows)} 筆資料列")
                
                data_list = []
                for row in rows:
                    cols = row.locator("td").all_inner_texts()
                    if len(cols) >= 3:
                        # cols[0]是病房, cols[1]是病床, cols[2]是已過時間
                        room_name = cols[0]
                        bed_name = cols[1]
                        time_passed = cols[2]
                        
                        # 只抓取包含「病房」名稱的項目
                        if "病房" in room_name or "9F" in room_name or "8F" in room_name or "7F" in room_name or "6F" in room_name or "5F" in room_name or "2F" in room_name:
                            data_list.append(f"🏥 {room_name} | 🛏️ {bed_name} | ⏱️ {time_passed}")

                # 組合訊息並回報
                if data_list:
                    data_str = "\n".join(data_list)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    message = f"【清床系統定時回報】\n時間: {timestamp}\n目前待處理的任務：\n\n{data_str}"
                else:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    message = f"【清床系統定時回報】\n時間: {timestamp}\n目前系統中沒有待處理的清床任務。🎉"

                print("準備發送的訊息內容：\n", message)

            except Exception as e:
                raise Exception(f"數據表格抓取失敗：{e}")

            print("發送 Telegram 消息...")
            send_telegram_message(message)
            print("消息發送完成")

        except Exception as e:
            print(f"❌ 錯誤：{e}")
            error_msg = f"【清床系統錯誤通報】\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n抓取失敗，錯誤訊息：\n{e}"
            send_telegram_message(error_msg)
        finally:
            print("關閉瀏覽器...")
            browser.close()
            print("任務完成")

def main():
    print("清床系統 - Telegram 定時通知服務")
    print(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("設定: 每半小時執行一次任務")
    print("\n首次執行...")
    
    # 立即執行一次
    fetch_and_report()
    
    # 設定定時任務：每 30 分鐘執行一次
    schedule.every(30).minutes.do(fetch_and_report)
    
    print("\n等待定時任務觸發...(按 Ctrl+C 停止服務)")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # 每 1 秒檢查一次是否需要執行任務
    except KeyboardInterrupt:
        print("\n服務已停止")

def main_single():
    """單次執行模式（用於 GitHub Actions）"""
    print("清床系統 - 單次執行模式")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    fetch_and_report()

if __name__ == "__main__":
    import sys
    
    # 根據環境變數或命令行參數決定運行模式
    # 在本地運行時使用連續模式 (每 30 分鐘執行)
    # 在 GitHub Actions 運行時使用單次模式
    
    if os.getenv("GITHUB_ACTIONS") == "true" or len(sys.argv) > 1 and sys.argv[1] == "single":
        # GitHub Actions 單次執行模式
        main_single()
    else:
        # 本地連續執行模式
        main()
    main()
