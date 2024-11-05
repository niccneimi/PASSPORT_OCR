import requests

def san(text):
    burp0_url = "https://speller.yandex.net:443/services/spellservice.json/checkText?sid=c3524e0c.672a2a0c.a19cc90e.74722d74657874&srv=tr-text&yu=1287804781727899070&yum=1727899071221811984"
    burp0_headers = {"Sec-Ch-Ua-Platform": "\"Linux\"", "Accept-Language": "en-US,en;q=0.9", "Sec-Ch-Ua": "\"Chromium\";v=\"129\", \"Not=A?Brand\";v=\"8\"", "Content-Type": "application/x-www-form-urlencoded", "Sec-Ch-Ua-Mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36", "Accept": "*/*", "Origin": "https://translate.yandex.ru", "Sec-Fetch-Site": "cross-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://translate.yandex.ru/?source_lang=en&target_lang=ru&text=%D0%B2%D0%BB%D0%B0%D0%B4%D1%81%D0%BB%D0%B0%D0%B2", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=1, i"}
    burp0_data = {"text": text, "lang": "en", "options": "516"}
    r = requests.post(burp0_url, headers=burp0_headers, data=burp0_data)
    try:
        return r.json()[0]['s'][1]
    except:
        return None