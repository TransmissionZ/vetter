from bs4 import BeautifulSoup as soup
import requests


class gsmnet():
    price = 0
    def __init__(self, url):
        self.url = url
        print("Grabbing value")

    def scrap(self):
        print("called")
        count = 0
        while True:
            count += 1
            if count == 3:
                return 0.0
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('div', class_='prices')('div')[-1].text.strip()
                print(p)
                n = p.find(' ')
                p = p[:n]
                return float(p)
            except Exception as e:
                print(e)
                continue

class sepmobile():
    price = 0
    def __init__(self, url):
        self.url = url
        print("Grabbing value")

    def scrap(self):
        count = 0
        while True:
            count += 1
            if count == 3:
                return 0.0
            data = {'login_username':'doctor_gsm', 'login_password':'klf118'}
            try:
                with requests.Session() as s:
                    login = 'https://sepmobile.ro/login/in'
                    response = s.post(login, data=data)
                    print(response.status_code)
                    response = s.get(self.url)
                if response.status_code != 200:
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('span', class_='eroare').text.strip()
                p = p.replace(',', '.')
                return float(p)
            except:
                continue