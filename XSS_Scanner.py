from urllib3.util.retry import Retry
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import json
from Log import Log
from urllib.parse import urlparse, urljoin


class XSS:
    def __init__(self) -> None:
        self.payload_filename = "payloads.txt"
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

    def session(self, headers, cookie) -> requests.sessions.Session:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers = headers if headers else self.headers
        if cookie:
            session.cookies.update(json.loads(cookie))
        return session

    def base_url(self, url, with_path=False):
        parsed = urlparse(url)
        path = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
        parsed = parsed._replace(path=path)
        parsed = parsed._replace(params='')
        parsed = parsed._replace(query='')
        parsed = parsed._replace(fragment='')
        return parsed.geturl()

    def read_payloads(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()

        lines = list(set([line.strip() for line in lines if line.strip()]))
        Log.info(f"Loaded {len(lines)} payloads!")
        return lines

    def post_form(self):
        soup = BeautifulSoup(self.body, 'html.parser')
        forms = soup.find_all('form')
        for form in forms:
            action = form.get("action")
            if not action:
                action = self.url
            action = urljoin(self.url, action)
            if form.get("method").lower().strip() == "post":
                Log.info(f"Form found! at [bold yellow]{action}")
                inputs = form.find_all(["input", "textarea"])
                data = {}
                for input in inputs:
                    name = input.get("name")
                    value = input.get("value")
                    type = input.get("type")
                    if not name:
                        continue
                    if type == "hidden" or type == "submit":
                        data[name] = value if value else "__PAYLOAD__"
                    else:
                        data[name] = "__PAYLOAD__"
                    Log.info(
                        f"Input name : [bold cyan]{name}[/] => value : [bold cyan]{value if value else '__PAYLOAD__'}[/]")
                Log.info(f"Post data schema : [bold yellow4]{data}")
                for payload in self.payloads:
                    data_payload = {key: val.replace("__PAYLOAD__", payload) for key, val in data.items()}
                    Log.info(f"Post data : [bold yellow4]{data_payload}")
                    response = self.request.post(action, data=data_payload)
                    if response.status_code > 400:
                        Log.warning(
                            f"Connection failed! with status code : {response.status_code}")
                        return
                    # time = datetime.now().strftime('%H_%M_%S')
                    # open(f"report_{time}.html", "w", encoding="utf-8").write(response.text)
                    open(f"report.html", "w", encoding="utf-8").write(response.text)
                    if payload in response.text:
                        Log.high(
                            f"XSS found! Payload: [bold blue_violet]{payload}")

    def main(self, url, proxy, headers, cookie, method=2):
        self.url = url
        self.cookie = cookie
        self.method = method
        self.request = self.session(headers, self.cookie)
        self.response = self.request.get(self.url)
        self.body = self.response.text
        if self.response.status_code > 400:
            Log.warning(
                f"Connection failed! with status code : {self.response.status_code}")
            return
        Log.info(
            f"Connection established! with status code : {self.response.status_code}")
        self.payloads = self.read_payloads(self.payload_filename)

        self.post_form()


if __name__ == '__main__':
    xss = XSS()
    url = "http://testphp.vulnweb.com/"
    xss.main(url, None, None, None, 2)
