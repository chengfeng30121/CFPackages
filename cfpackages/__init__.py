from . import file_utils, http_utils, logger_formatter, text_ui
from importlib.metadata import version, PackageNotFoundError
import os

try:
    __version__ = version("cfpackages")
except PackageNotFoundError:
    __version__ = "-1"

if os.environ.get("cfpackages.check_update", 1).isdigit():
    __check_update__ = bool(int(os.environ.get("cfpackages.check_update", 1)))
elif os.environ.get("cfpackages.check_update", "true").lower() == "false":
    __check_update__ = False
else:
    __check_update__ = True
__all__ = ["file_utils", "http_utils", "logger_formatter", "text_ui", "__version__", "__check_update__"]

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

if __check_update__:
    _check_update()
