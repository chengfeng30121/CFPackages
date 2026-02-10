from typing import Optional, Literal
import json
import requests
import time


# Headers Keys
special_keys = ["WWW-Authenticate", "ETag", "Expect-CT", "TE", "SourceMap", "Accept-CH", "Critical-CH",
                "Content-DPR", "DPR", "ECT", "RTT", "DNT", "Sec-GPC", "NEL", "Sec-CH-UA", "Sec-CH-UA-Arch",
                "Sec-CH-UA-Bitness", "Sec-CH-UA-Form-Factor", "Sec-CH-UA-Full-Version", "Sec-CH-UA-Full-Version-List", 
                "Sec-CH-UA-Mobile", "Sec-CH-UA-Model", "Sec-CH-UA-Platform", "Sec-CH-UA-Platform-Version", 
                "Sec-CH-UA-WoW64"] # From https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Headers
# logger = get_logger()
class logger: # Warning: you should replace this with your own logger.
              # Replace by monkey patching.
    def __getattr__(self, name):
        print(name)


def format_key(key: str, exclude_keys: Optional[list] = []):
    exclude_keys.extend(special_keys)
    for ekey in exclude_keys:
        if ekey.lower() == key.lower(): return ekey
    for i in key.split('-'):
        key = key.replace(i, i.capitalize())
    return key


def generate_headers(raw_text: str, exclude_keys: Optional[list] = []):
    try:
        return json.loads(raw_text)
    except Exception as e:
        headers = {}
        mode = None
    temp = []
    for line in raw_text.split('\n'):
        if mode is None:
            if ":" in line:
                mode = True
            else:
                mode = False
        if mode:
            words = line.split(':')
            key = words[0]
            value = ':'.join(words[1:])
            if not key.strip() or not value.strip(): continue
            headers[format_key(key.strip(), exclude_keys)] = value.strip()
        else:
            match len(temp):
                case 0:
                    temp.append(line.strip())
                case 1:
                    headers[format_key(temp[0], exclude_keys)] = line
                    temp = []
                case _:
                    temp = []
    return headers


def get_headers_from_user_input():
    raw_text = ""
    while True:
        raw_input = input("Please input your headers: ")
        if raw_input.strip():
            raw_text += raw_input + "\n"
        else:
            break
    headers = generate_headers(raw_text)
    print(headers)
    return headers


def request(method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
            url: str, **kwargs) -> requests.models.Response:
    retry = kwargs.get('retry', 0)
    try:
        return requests.request(method, url, **kwargs)
    except:
        if retry >= 3:
            raise Exception(f'Can\'t to request, please check your network connection.')
        logger.error(f'Network error, retrying {retry+1}/3. Waiting for 3 seconds...')
        time.sleep(3)
        return request(method, url, **kwargs, retry=retry+1)


def get(url: str, params: Optional[dict] = None, **kwargs) -> requests.models.Response:
    return request("GET", url, params=params, **kwargs)


def post(url: str, data: Optional[dict] = None, json: Optional[dict] = None, **kwargs) -> requests.models.Response:
    return request("POST", url, data=data, json=json, **kwargs)

