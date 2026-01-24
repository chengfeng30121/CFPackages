from colorama import init, Fore, Style
import logging
import sys


init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.RED
    }

    TEXT_PART_COLORS = {
        'asctime': Fore.CYAN,
        'name': Fore.MAGENTA,
        'filename': Fore.WHITE,
        'module': Fore.WHITE,
        'funcName': Fore.WHITE
    }

    def __init__(self, fmt=None, datefmt=None, style='%', defaults=None):
        super().__init__(fmt, datefmt, style, defaults)

    def format(self, record):
        raw_msg = super().format(record)
        colored_msg = self._colorize_raw_message(raw_msg, record)
        return colored_msg

    def _colorize_raw_message(self, msg, record):
        levelname = f"[{record.levelname}]"
        if levelname in msg:
            color = self.LEVEL_COLORS.get(record.levelno, Style.RESET_ALL)
            msg = msg.replace(levelname, f"{color}{levelname}{Style.RESET_ALL}")

        time_str = self.formatTime(record, self.datefmt)
        if time_str in msg:
            color = self.TEXT_PART_COLORS.get('asctime', Style.RESET_ALL)
            msg = msg.replace(time_str, f"{color}{time_str}{Style.RESET_ALL}")

        name = record.name
        if name in msg:
            color = self.TEXT_PART_COLORS.get('name', Style.RESET_ALL)
            msg = msg.replace(name, f"{color}{name}{Style.RESET_ALL}")

        for field in ['filename', 'lineno', 'module', 'funcName']:
            if hasattr(record, field):
                original_value = getattr(record, field)
                value_str = str(original_value)
                color = self.TEXT_PART_COLORS.get(field, Style.RESET_ALL)
                if value_str in msg:
                    colored_value = f"{color}{value_str}{Style.RESET_ALL}"
                    msg = msg.replace(value_str, colored_value)

        return msg

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = ColoredFormatter(
        fmt="%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger
