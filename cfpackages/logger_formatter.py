from colorama import init, Fore, Style, Back
import logging
import re
import sys
import threading

_colorama_initialized = False
_logger_lock = threading.Lock()


class ColoredFormatter(logging.Formatter):
    """给日志加颜色的 Formatter：按级别着色，并高亮时间戳与 logger 名。"""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE + Style.BRIGHT,
        logging.INFO: Fore.GREEN + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Back.WHITE + Style.BRIGHT,
    }

    TEXT_PART_COLORS = {
        'asctime': Fore.CYAN,
        'name': Fore.MAGENTA,
        'filename': Fore.WHITE,
        'module': Fore.WHITE,
        'funcName': Fore.WHITE,
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        # 不接收 defaults 参数：它是 Python 3.10 才加入的，项目要求兼容 3.9
        super().__init__(fmt, datefmt, style)

    @staticmethod
    def _colorize_first(message: str, text: str, color: str) -> str:
        """把消息中第一次独立出现的 `text` 着色，避免误替换正文中相同的子串。"""
        if not text:
            return message
        match = re.search(r'(?<!\w)' + re.escape(text) + r'(?!\w)', message)
        if match is None:
            return message
        colored = f"{color}{text}{Style.RESET_ALL}"
        return message[:match.start()] + colored + message[match.end():]

    def format(self, record):
        message = super().format(record)

        level_color = self.LEVEL_COLORS.get(record.levelno, '')
        message = message.replace(
            f"[{record.levelname}]",
            f"{level_color}[{record.levelname}]{Style.RESET_ALL}",
        )

        time_str = self.formatTime(record, self.datefmt)
        message = self._colorize_first(
            message, time_str, self.TEXT_PART_COLORS.get('asctime', ''))

        message = self._colorize_first(
            message, record.name, self.TEXT_PART_COLORS.get('name', ''))

        return message


def _ensure_colorama() -> None:
    global _colorama_initialized
    if not _colorama_initialized:
        init(autoreset=True)
        _colorama_initialized = True


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """获取带彩色格式的 logger。

    已存在 handler 的 logger（包括已由用户自行配置过的）原样返回，
    不覆盖其 level 与格式。
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
    with _logger_lock:
        # 二次检查：防止多线程并发首次调用时重复创建 handler
        if logger.hasHandlers():
            return logger
        _ensure_colorama()
        logger.setLevel(level)
        logger.propagate = False  # 避免消息同时被 root logger 重复打印
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = ColoredFormatter(
            fmt="%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
