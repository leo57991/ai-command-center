import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime, timezone, timedelta

def fetch_google_news(keyword, limit=3):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    print(f"Fetching: {keyword}")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('./channel/item')
        
        news_list = []
        for item in items[:limit]:
            title_text = item.find('title').text if item.find('title') is not None else "未命名的標題"
            # Remove publisher suffix from title if it exists (e.g. " - Yahoo奇摩新聞")
            if " - " in title_text:
                title_text = title_text.rsplit(" - ", 1)[0]
                
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
            try:
                # Format: Wed, 27 Mar 2026 09:30:00 GMT
                dt = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %Z')
                # Google News RSS usually returns GMT. Let's force it to UTC and convert to UTC+8 (Taipei)
                dt = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
                time_str = dt.strftime('%m/%d %H:%M')
            except Exception:
                time_str = pubDate[:16] # Fallback string slicing
                
            description_node = item.find('description')
            summary = ""
            if description_node is not None and description_node.text:
                # Strip HTML tags
                clean_text = re.sub('<[^<]+>', '', description_node.text).strip()
                # Remove the title itself if it appears at the beginning of the description
                clean_text = clean_text.replace(title_text, '').strip()
                if clean_text:
                     summary = clean_text[:60] + "..." if len(clean_text) > 60 else clean_text
                     
            if not summary:
                summary = "點擊以查看完整新聞"

            link_text = item.find('link').text if item.find('link') is not None else "#"

            news_list.append({
                "time": time_str,
                "title": title_text,
                "summary": summary,
                "link": link_text
            })
        return news_list
    except Exception as e:
        print(f"Error fetching {keyword}: {e}")
        return []

def main():
    # Setup categories and keywords
    categories = {
        "finance": "台股 OR 財經 OR 股市",
        "langtech": "生成式 AI OR 語言模型 OR 科技職涯",
        "migration": "英國留學 OR PSW簽證 OR 留學"
    }
    
    # Taiwan Time = UTC+8
    tz_tw = timezone(timedelta(hours=8))
    last_sync = datetime.now(tz_tw).strftime("%Y/%m/%d %H:%M")
    
    data = {
        "lastSync": last_sync,
        "finance": fetch_google_news(categories["finance"], 4),
        "langtech": fetch_google_news(categories["langtech"], 4),
        "migration": fetch_google_news(categories["migration"], 4)
    }
    
    output_file = "news_briefing.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully updated {output_file} at {last_sync}")

if __name__ == "__main__":
    main()
