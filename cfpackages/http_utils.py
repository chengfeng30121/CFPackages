from typing import Optional, Literal, Mapping
import json
import logging
import time
import requests

logger = logging.getLogger(__name__)

# 大小写敏感、需要原样保留的 HTTP 响应头
# 来源: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Headers
PRESERVE_CASE_KEYS = frozenset([
    "WWW-Authenticate", "ETag", "Expect-CT", "TE", "SourceMap", "Accept-CH",
    "Critical-CH", "Content-DPR", "DPR", "ECT", "RTT", "DNT", "Sec-GPC",
    "NEL", "Sec-CH-UA", "Sec-CH-UA-Arch", "Sec-CH-UA-Bitness",
    "Sec-CH-UA-Form-Factor", "Sec-CH-UA-Full-Version",
    "Sec-CH-UA-Full-Version-List", "Sec-CH-UA-Mobile", "Sec-CH-UA-Model",
    "Sec-CH-UA-Platform", "Sec-CH-UA-Platform-Version", "Sec-CH-UA-WoW64",
])

# 值为带引号列表、不能剥引号的键
QUOTED_VALUE_KEYS = frozenset(("sec-ch-ua", "sec-ch-ua-platform"))


def format_key(key: str, preserve_case: Optional[set] = None) -> str:
    """将 header 键格式化为首字母大写，如 `content-type` → `Content-Type`。

    `preserve_case` 中的键（不区分大小写匹配）保持原样返回。
    """
    key_lower = key.lower()
    for ekey in PRESERVE_CASE_KEYS:
        if ekey.lower() == key_lower:
            return ekey
    if preserve_case:
        for ekey in preserve_case:
            if ekey.lower() == key_lower:
                return ekey
    return "-".join(part.capitalize() for part in key.split("-"))


def generate_headers(raw_text: str, preserve_case: Optional[set] = None) -> dict:
    """从粘贴的文本解析 headers。

    支持三种输入格式：
    1. 完整 JSON 对象
    2. 缺少花括号的 JSON 片段
    3. 普通文本，同时支持两种行格式（可混用）：
       - 每行一个 `Key: value`（浏览器开发者工具复制的格式）
       - 每两行一组：key 行（无冒号）+ value 行
       （value 行里即使带冒号，如 `Wed, 5 Aug 2026 21:30:51 +0800`，也不会被误拆）
    """
    raw_text = raw_text.strip()
    if not raw_text:
        return {}

    # 1) 直接是 JSON
    try:
        return json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        pass

    # 2) 缺少花括号的 JSON 片段
    try:
        candidate = raw_text
        if not candidate.startswith("{"):
            candidate = "{" + candidate
        if not candidate.endswith("}"):
            candidate = candidate + "}"
        return json.loads(candidate)
    except (json.JSONDecodeError, TypeError):
        pass

    # 3) 逐行解析：`Key: value` 或两行式（key 行 + value 行）
    def _unquote(value: str, key: str) -> str:
        if (key.lower() not in QUOTED_VALUE_KEYS
                and len(value) >= 2
                and value.startswith('"') and value.endswith('"')):
            return value[1:-1]
        return value

    headers = {}
    pending_key = None
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if pending_key is not None:
            # 两行式的 value 行：可能带冒号（如 `Wed, 5 Aug 2026 21:30:51 +0800`），
            # 只要前面还有未配对的 key 行，就整行作为 value，不拆冒号
            headers[format_key(pending_key, preserve_case)] = _unquote(line, pending_key)
            pending_key = None
        elif ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().strip('"')
            value = value.strip()
            if key and value:
                headers[format_key(key, preserve_case)] = _unquote(value, key)
        else:
            # 无冒号：作为 key 等待下一行作为 value（两行式）
            pending_key = line
    return headers


def get_headers_from_user_input(print_headers: bool = True) -> dict:
    """交互式输入 headers：支持 `Key: value` 或 `Key` 换行 `value` 两行式，空行结束。"""
    print("请粘贴你的 headers（支持 `Key: value` 每行，或 `Key` 换行 `value` 两行式），空行结束输入:")
    lines = []
    while True:
        line = input()
        if line.strip():
            lines.append(line)
        else:
            break
    headers = generate_headers("\n".join(lines))
    if print_headers:
        print(headers)
    return headers


def request(method: Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"],
            url: str, retry: int = 3, delay: float = 3.0, **kwargs) -> requests.Response:
    """发起请求，网络失败时最多自动重试 `retry` 次（默认 3 次，与 0.1.5 及更早版本一致）。

    传 `retry=0` 可禁用重试。重试间隔固定为 `delay` 秒。
    重试耗尽后抛 ConnectionError。
    """
    for attempt in range(retry + 1):
        try:
            return requests.request(method, url, **kwargs)
        except requests.RequestException as e:
            if attempt == retry:
                raise ConnectionError(
                    f"请求失败（已尝试 {retry + 1} 次），请检查网络连接。"
                ) from e
            logger.error(
                f"网络错误，正在重试 {attempt + 1}/{retry}，"
                f"等待 {delay} 秒..."
            )
            time.sleep(delay)


def get(url: str, params: Optional[Mapping] = None, **kwargs) -> requests.Response:
    return request("GET", url, params=params, **kwargs)


def post(url: str, data: Optional[Mapping] = None,
         json: Optional[Mapping] = None, **kwargs) -> requests.Response:
    return request("POST", url, data=data, json=json, **kwargs)
