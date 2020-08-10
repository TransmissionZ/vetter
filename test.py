import django
import requests
import json
import time

if __name__ == '__main__':
    start = time.time()
    url = 'http://dev.thenx.net/rest/V1/thenx/prfeed/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 7h5om9dna1pljz1mkbwqr4pzxcih1m79',
    }
    r = requests.get(url, headers=headers)
    with open('products.txt', 'w') as f:
        f.write(str(r.json()))
    a = json.loads(r.json())
    end = time.time()
    print(end - start)
    print(len(a))
    urls = [x['url'] for x in a]
    print(max(urls))
    print(len(max(urls)))

    for p in a:
        print(p['name'], p['brand'], p['supplier'])
        print(p['cat'])
        p1 = json.loads(p['cat'])
        print(p1)
        print(p1[0])
        print(p['cat'])
        print(p['cat'])