# 132

## Web Scraper with Telegram Notification

This project contains a Python script that automates web scraping using Playwright, logs into a website, extracts data, and sends the results via Telegram.

### Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```
   playwright install
   ```

3. Set environment variables (see .env.example for template):
   - `MY_USERNAME`: Your login username
   - `MY_PASSWORD`: Your login password
   - `TG_BOT_TOKEN`: Your Telegram bot token (current: 8774257757:AAFW97ijqY13TzuXVNJuh7zKKAe-ypfpfj8)
   - `TG_CHAT_ID`: Your Telegram chat ID (current: 6642001425)

### Usage

Run the script locally:
```
python scraper.py
```

### GitHub Actions Setup

This repository includes a GitHub Actions workflow for automated daily execution.

1. In your GitHub repository, go to Settings > Secrets and variables > Actions.
2. Add the following secrets:
   - `MY_USERNAME`
   - `MY_PASSWORD`
   - `TG_BOT_TOKEN` (use: 8774257757:AAFW97ijqY13TzuXVNJuh7zKKAe-ypfpfj8)
   - `TG_CHAT_ID` (use: 6642001425)

3. The workflow will run daily at 00:00 UTC (08:00 Taiwan time) automatically.
4. You can also trigger it manually from the Actions tab.

### Notes

- The script uses headless browser mode for cloud execution.
- The login URL has been updated to https://eporter.skh.org.tw/eBTSController/frmLogin.aspx.
- Selectors have been updated based on typical ASP.NET login forms: `input[name='UserName']`, `input[name='Password']`, `input[type='submit']`.
- If these selectors don't work, inspect the page source and update them accordingly.
- Update the data selector (currently `.target-data-class`) to match the actual element containing the data to scrape.