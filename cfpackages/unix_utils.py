from typing import Optional
import sys
import os


if sys.platform == "win32":
    raise ImportError("This module only works on Unix like systems")


def is_admin() -> bool:
    return os.getuid() == 0


def get_admin(raise_admin: Optional[bool] = True) -> None:
    if is_admin():
        if raise_admin:
            raise PermissionError("You're already an admin!")
    arg = sys.argv.copy()
    if (not sys.argv[0].endswith('.py') or getattr(sys, "frozen", False)) and arg[0] != sys.executable:
        arg.insert(0, sys.executable)
    os.execvp("sudo", ["sudo"] + arg)
