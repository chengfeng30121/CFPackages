from . import file_utils, http_utils, logger_formatter, text_ui
from importlib.metadata import version, PackageNotFoundError
from typing import Optional
import os
import re
import sys
import tempfile
import threading
import time

__all__ = ["file_utils", "http_utils", "logger_formatter", "text_ui", "__version__"]

if sys.platform == "win32":
    from . import win_utils
    __all__.append("win_utils")
else:
    from . import unix_utils
    __all__.append("unix_utils")

try:
    __version__ = version("cfpackages")
except PackageNotFoundError:
    __version__ = "-1"

_CHECK_INTERVAL = 60 * 60 * 24  # 24 小时检查一次
_CACHE_FILE = os.path.join(tempfile.gettempdir(), "cfpackages_last_check_update")
_PACKAGE_NAME = "cfpackages"
# 更新检查源：默认国内镜像（清华/中科大），PyPI 官方作为备选。
# 三者均支持 PEP 691 JSON simple API（带 Accept 头返回 JSON 而非 HTML）。
_UPDATE_SOURCES = (
    "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/{pkg}/",
    "https://mirrors.ustc.edu.cn/pypi/simple/{pkg}/",
    "https://pypi.org/simple/{pkg}/",
)
_ACCEPT_SIMPLE_JSON = "application/vnd.pypi.simple.v1+json"


def _check_update_allowed() -> bool:
    """纯本地判断：本次导入是否需要触发更新检查。绝不联网、绝不抛异常。"""
    if __version__ == "-1":
        return False  # 非 pip 安装（源码直接运行），不检查
    env = os.environ.get("cfpackages.check_update", "").lower()
    if env in ("0", "false", "no", "off"):
        return False  # 显式关闭
    if env == "1":
        return True  # 显式强制检查
    try:
        with open(_CACHE_FILE, encoding="utf-8") as f:
            last = int(f.read().strip())
        return int(time.time()) - last > _CHECK_INTERVAL
    except (OSError, ValueError, TypeError):
        return True  # 无缓存 / 缓存损坏 → 检查一次


def _compare_version(current: str, latest: str):
    """比较版本号。返回 True=需要更新 / False=已最新 / None=无法比较。"""
    if "-" in current:
        return None  # 预发布版本不提示
    try:
        cur = [int(i) for i in current.split(".")]
        new = [int(i) for i in latest.split(".")]
    except ValueError:
        return None
    cur += [0] * (len(new) - len(cur))
    new += [0] * (len(cur) - len(new))
    return cur < new


def _max_version(versions) -> Optional[str]:
    """取版本号列表中的最大值。"""
    best = None
    for version in versions:
        if best is None or _compare_version(best, version) is True:
            best = version
    return best


def _http_get(url: str, accept: Optional[str] = None) -> Optional[str]:
    """GET 请求，返回响应体文本；非 200 或异常返回 None。"""
    import http.client
    from urllib.parse import urlsplit

    parts = urlsplit(url)
    path = parts.path + (f"?{parts.query}" if parts.query else "")
    headers = {"User-Agent": "cfpackages-update-check"}
    if accept:
        headers["Accept"] = accept
    conn = http.client.HTTPSConnection(parts.hostname, timeout=3)
    try:
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        if resp.status != 200:
            return None
        return resp.read().decode("utf-8", errors="replace")
    finally:
        conn.close()


def _versions_from_simple_json(text: str) -> list:
    """从 PEP 691 JSON simple index 中提取所有正式版本号（不含预发布）。"""
    import json

    data = json.loads(text)
    versions = data.get("versions")
    if versions:  # api-version >= 1.1
        return [v for v in versions if re.fullmatch(r"[\d.]+", v)]
    # api-version 1.0：只能从文件名中提取
    versions = []
    for f in data.get("files", []):
        filename = f.get("filename", "")
        stem = filename[:-7] if filename.endswith(".tar.gz") else filename[:-4]
        version = stem[len(_PACKAGE_NAME) + 1:].split("-")[0]
        if re.fullmatch(r"[\d.]+", version):
            versions.append(version)
    return versions


def _fetch_latest_version() -> Optional[str]:
    """依次尝试各更新源，返回最新版本号；全部失败返回 None。"""
    for url_template in _UPDATE_SOURCES:
        try:
            text = _http_get(
                url_template.format(pkg=_PACKAGE_NAME), accept=_ACCEPT_SIMPLE_JSON)
            if text is None:
                continue
            latest = _max_version(_versions_from_simple_json(text))
            if latest is not None:
                return latest
        except Exception:
            continue
    return None


def _check_update() -> None:
    """后台线程入口：检查是否有新版本，所有异常静默吞掉。"""
    logger = logger_formatter.get_logger("cfpackages.update")
    try:
        latest = _fetch_latest_version()
        if latest is not None and _compare_version(__version__, latest):
            logger.warning(
                f"发现新版本: cfpackages {__version__} -> {latest} "
                "(运行 `pip install cfpackages --upgrade` 更新)"
            )
    except Exception:
        pass
    try:
        # 原子写入缓存，避免多进程竞争产生半截文件
        tmp = _CACHE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(str(int(time.time())))
        os.replace(tmp, _CACHE_FILE)
    except OSError:
        pass


if _check_update_allowed():
    threading.Thread(target=_check_update, daemon=True).start()
