from bs4 import BeautifulSoup as soup
import requests

def login_web(user, pwd, formname, formpass, url, purl):
    data = {formname: user, formpass: pwd, 'SubmitLogin': ''}
    try:
        with requests.Session() as s:
            response = s.post(url, data=data)
            if response.status_code != 200:
                return None
            response = s.get(purl)
        s = soup(response.text, 'html.parser')
        return s
    except Exception as e:
        return None

class gsmnet():
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

            id = 'doctor_gsm'
            pwd = 'klf118'
            s = login_web(id, pwd, 'login_username', 'login_password', 'https://sepmobile.ro/login/in', self.url)
            if s:
                p = s.find('span', class_='eroare').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').strip()
                return float(p)
            else:
                continue

class sunex():
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

            id = 'itool_service@yahoo.com'
            pwd = 'samsung22'
            s = login_web(id, pwd, 'email', 'passwd', 'https://sunex.ro/nou/autentificare', self.url)
            if s:
                p = s.find('span', itemprop='price').text.strip()
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').strip()
                return float(p)
            else:
                continue

class conectshop():
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

            id = 'klf118@yahoo.com'
            pwd = 'rLH-Jq5-e5G-CWF'
            s = login_web(id, pwd, 'email', 'password', 'https://conectshop.ro/index.php?route=account/login', self.url)
            if s:
                p = s.find(itemprop='price').get('content')
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').strip()
                return float(p)
            else:
                continue

class magazingsm():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('span', class_='price').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('Lei', '').strip()
                return float(p)
            except Exception as e:
                print(e)
                continue

class protableta():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('span', class_='price').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                return float(p)
            except Exception as e:
                print(e)
                continue

class powerlaptop():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('em', class_='ProductPrice').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                return float(p)
            except Exception as e:
                print(e)
                continue

class servicepack():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('p', class_='price').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                try:
                    p = float(p)
                except:
                    n = p.find('–')
                    p = float(p[:n].strip())
                return p
            except Exception as e:
                print(e)
                continue

class distrizone():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('span', class_='fPrice').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                n = p.count('.')
                if n == 2:
                    p = p.replace('.', '', 1)

                return float(p)
            except Exception as e:
                print(e)
                continue

class mokagsm():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('span', class_='fPrice').text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                return float(p)
            except Exception as e:
                print(e)
                continue

class inowgsm():
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
            try:
                response = requests.get(self.url)
                if response.status_code != 200:
                    print(response.status_code)
                    continue
                s = soup(response.text, 'html.parser')
                p = s.find('div', class_='price-group')('div')[0].text
                p = p.replace(',', '.').replace('RON', '').replace('LEI', '').replace('lei', '').replace('Lei', '').strip()
                return float(p)
            except Exception as e:
                print(e)
                continue