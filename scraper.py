import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import datetime
import os

# ==========================================
# ⚡️ 在這裡修改你的專屬 3 大主題
# 只要在這裡改字，前端的網頁標題也會跟著自動變動！
# ==========================================
TOPICS = [
    "台股 投資 股市 財經",
    "AI 技術 LLM 生成式",
    "全球 移民 留學 簽證"
]

# 提供給前端顯示的美觀標題名稱 (可隨意改)
DISPLAY_NAMES = [
    "📈 台股投資新聞",
    "🤖 AI 技術更新",
    "✈️ 全球移民與留學"
]

def fetch_google_news(query):
    print(f"Fetching: {query}")
    # Google News RSS URL
    encoded_query = urllib.parse.quote(query.replace(' ', ' OR '))
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = []
        # 取前 5 篇
        for item in root.findall('./channel/item')[:5]:
            title = item.find('title').text if item.find('title') is not None else '無標題'
            link = item.find('link').text if item.find('link') is not None else '#'
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            # 格式化日期，只保留 "DD MMM YYYY HH:MM"
            time_str = pub_date
            if pub_date:
                parts = pub_date.split()
                if len(parts) >= 5:
                    time_str = f"{parts[1]} {parts[2]} {parts[3]} {parts[4][:-3]}"
            
            items.append({
                "title": title,
                "link": link,
                "summary": "",
                "time": time_str
            })
        return items
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        return []

def main():
    # 建立時區 (使用台灣時間 UTC+8)
    tz = datetime.timezone(datetime.timedelta(hours=8))
    now = datetime.datetime.now(tz)
    last_sync = now.strftime('%Y/%m/%d %H:%M')

    data = {
        "lastSync": last_sync,
        "topics": []
    }

    # 依序抓取 3 個領域
    for i in range(3):
        articles = fetch_google_news(TOPICS[i])
        data["topics"].append({
            "title": DISPLAY_NAMES[i],
            "articles": articles
        })

    # 確保輸出路徑正確 (目前跟腳本放在同一目錄)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "news_briefing.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully updated news_briefing.json at {last_sync}")

if __name__ == "__main__":
    main()
