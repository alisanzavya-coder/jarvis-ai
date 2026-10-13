from flask import Flask, request, jsonify, send_from_directory
import os, requests, xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__, static_folder='.')

@app.get('/')
def home():
    return send_from_directory('.', 'index.html')

@app.get('/api/health')
def health():
    return jsonify(ok=True, ai_configured=bool(os.getenv('AI_API_KEY')))

@app.post('/api/chat')
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip()
    key = (data.get('api_key') or os.getenv('AI_API_KEY') or '').strip()
    base = (data.get('base_url') or os.getenv('AI_BASE_URL') or 'https://api.openai.com/v1').strip().rstrip('/')
    model = (data.get('model') or os.getenv('AI_MODEL') or 'gpt-4o-mini').strip()
    if not message:
        return jsonify(error='پیام خالی است.'), 400
    if not key:
        return jsonify(error='کلید API وارد نشده است. در تنظیمات اتصال یک کلید معتبر وارد کن.'), 400
    # Accept only HTTP(S) API endpoints. The API key is sent only to this endpoint's configured provider.
    if not base.startswith(('https://','http://')):
        return jsonify(error='نشانی API باید با http:// یا https:// شروع شود.'), 400
    try:
        resp = requests.post(base + '/chat/completions',
            headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
            json={'model':model,'messages':[
                {'role':'system','content':'تو JARVIS، دستیار فارسی‌زبان، دقیق و مودب هستی. پاسخ‌ها را به فارسی و روشن بده. اگر درباره خبر روز سؤال شد و داده زنده نداری، ادعای دسترسی زنده نکن.'},
                {'role':'user','content':message}], 'temperature':0.5},
            timeout=60)
        if not resp.ok:
            return jsonify(error=f'ارائه‌دهنده API خطا داد ({resp.status_code}): '+resp.text[:500]), 502
        result=resp.json()
        reply=result['choices'][0]['message']['content']
        return jsonify(reply=reply)
    except requests.RequestException as e:
        return jsonify(error='اتصال به سرویس هوش مصنوعی ناموفق بود: '+str(e)), 502
    except (KeyError, IndexError, ValueError):
        return jsonify(error='پاسخ سرویس در قالب مورد انتظار نبود.'), 502

@app.get('/api/news')
def news():
    query=(request.args.get('q') or 'اخبار امروز').strip()[:160]
    url='https://news.google.com/rss/search?q='+quote_plus(query)+'&hl=fa&gl=IR&ceid=IR:fa'
    try:
        resp=requests.get(url, timeout=20, headers={'User-Agent':'JARVISNews/1.0'})
        resp.raise_for_status()
        root=ET.fromstring(resp.content)
        items=[]
        for item in root.findall('./channel/item')[:12]:
            title=item.findtext('title') or ''
            link=item.findtext('link') or ''
            pub=item.findtext('pubDate') or ''
            source=item.findtext('source') or 'Google News'
            items.append({'title':title,'link':link,'published':pub,'source':source})
        return jsonify(items=items, query=query)
    except Exception as e:
        return jsonify(error='دریافت اخبار از Google News ناموفق بود: '+str(e)), 502

if __name__ == '__main__':
    print('\\nJARVIS 3D running at http://127.0.0.1:8765')
    print('Keep this window open while using JARVIS. Press Ctrl+C to stop.\\n')
    app.run(host='127.0.0.1', port=8765, debug=False)
