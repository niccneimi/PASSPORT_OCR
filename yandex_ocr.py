import requests
def OCR(image_bytes,class_name):
    headers = {
        'Host': 'translate.yandex.net',
        'Accept': '*/*',
        'Origin': 'https://translate.yandex.ru',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://translate.yandex.ru/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Priority': 'u=1, i'
    }
    if class_name == "birthday":
        response = requests.post('https://translate.yandex.net/ocr/v1.1/recognize?srv=tr-image&sid=2d4f7d88.66fda5c0.304282bc.74722d696d616765&lang=ru&rotate=0', headers=headers, files = {'file': ('blob', image_bytes, 'image/png')})
    else:
        response = requests.post('https://translate.yandex.net/ocr/v1.1/recognize?srv=tr-image&sid=2d4f7d88.66fda5c0.304282bc.74722d696d616765&lang=ru&rotate=auto', headers=headers, files = {'file': ('blob', image_bytes, 'image/png')})

    try:
        return(response.json()['data']['blocks'][0]['boxes'][0]['text'])
    except:
        return None