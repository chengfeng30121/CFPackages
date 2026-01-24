from colorama import init, Fore, Style, Back
import logging
import sys


init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.BLUE + Style.BRIGHT,
        logging.INFO: Fore.GREEN + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Back.WHITE + Style.BRIGHT
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
        message = super().format(record)
        
        level_color = self.LEVEL_COLORS.get(record.levelno, '')
        message = message.replace(f"[{record.levelname}]", f"{level_color}[{record.levelname}]{Style.RESET_ALL}")
        
        time_color = self.TEXT_PART_COLORS.get('asctime', '')
        time_str = self.formatTime(record, self.datefmt)
        message = message.replace(time_str, f"{time_color}{time_str}{Style.RESET_ALL}")
        
        name_color = self.TEXT_PART_COLORS.get('name', '')
        message = message.replace(record.name, f"{name_color}{record.name}{Style.RESET_ALL}")
        
        return message

def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        formatter = ColoredFormatter(
            fmt="%(asctime)s %(name)s %(filename)s:%(lineno)d %(funcName)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
