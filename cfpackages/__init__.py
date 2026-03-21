from . import file_utils, http_utils, logger_formatter, text_ui
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import os
import sys
import time

__all__ = ["file_utils", "http_utils", "logger_formatter", "text_ui", "__version__", "__check_update__"]

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

def judge_check_update():
    if __version__ == "-1":
        return False
    elif os.environ.get("cfpackages.check_update", "true").lower() == "false":
        return False
    last_check_update = Path(__file__).parent / "last_check_update"
    if not last_check_update.exists():
        return True
    last_time = last_check_update.read_text()
    if int(time.time()) - int(last_time) > 60*10:
        return True
    if os.environ.get("cfpackages.check_update", "a") in ["0", "1"]:
        return bool(os.environ.get("cfpackages.check_update", "1"))
    return False


def _check_update():
    import http.client
    import json
    logger = logger_formatter.get_logger("cfpackages.update")

    def compare_version(version): 
        """Compare two version strings and return if need to update.
        True: Need to update
        False: Already up to date
        None: Development / Pre-release / Self-compiled version
        """
        if __version__ == "-1": 
            return None
        if "-" in __version__:  
            return None
        try:
            current_version = [int(i) for i in __version__.split(".")]
            latest_version = [int(i) for i in version.split(".")]
        except ValueError: 
            return None
        max_len = max(len(current_version), len(latest_version))
        current_version.extend([0] * (max_len - len(current_version)))
        latest_version.extend([0] * (max_len - len(latest_version)))
        for i in range(max_len):
            if current_version[i] < latest_version[i]:
                return True
            elif current_version[i] > latest_version[i]:
                return False
        return False

    connection = http.client.HTTPSConnection("pypi.org")
    try:
        connection.request("GET", "/pypi/cfpackages/json")
        response = connection.getresponse()
        if response.status != 200:
            logger.warning(f"Can't to get package info, Status Code: {response.status}")
            logger.warning(f"NOTE: If you don't want to check for updates, please set `__check_update__` to False.")
            return None
        data = json.loads(response.read().decode('utf-8'))
        str_version = data['info']['version']
        if compare_version(str_version):
            logger.warning(f"New version of cfpackages available: {str_version}")
            logger.warning(f"Please update to the latest version to get the latest features and bug fixes.")
            logger.warning(f"You can update by running `pip install cfpackages --upgrade`")
            return
        try: Path(__file__).parent.joinpath("last_check_update").write_text(str(int(time.time())))
        except: pass
    except json.JSONDecodeError as e:
        logger.warning(f"Can't to decode response info, Error Message: {e}")
        logger.warning(f"NOTE: If you don't want to check for updates, please set `__check_update__` to False.")
        return None
    except Exception as e:
        logger.warning(f"Somethings went wrong: {e}")
        logger.warning(f"NOTE: If you don't want to check for updates, please set `__check_update__` to False.")
        return None
    finally:
        connection.close()


if judge_check_update():
    _check_update()
