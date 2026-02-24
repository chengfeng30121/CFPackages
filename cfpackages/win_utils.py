from typing import Optional
import sys


if sys.platform != "win32":
    raise ImportError("This module only works on Windows")


def is_admin() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        import win32comext.shell.shell
        return win32comext.shell.shell.IsUserAnAdmin()
    finally:
        return False


def get_admin(raise_admin: Optional[bool] = True, exit_after: Optional[bool] = True) -> None:
    if is_admin():
        if raise_admin:
            raise PermissionError("You're already an admin!")
    try:
        import ctypes
        arg = sys.argv.copy()
        if (not sys.argv[0].endswith('.py') or getattr(sys, "frozen", False)) and arg[0] == sys.executable:
            del arg[0]
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(arg), None, 1)
        if exit_after:
            sys.exit()
    except:
        import win32comext.shell.shell
        arg = sys.argv.copy()
        if (not sys.argv[0].endswith('.py') or getattr(sys, "frozen", False)) and arg[0] == sys.executable:
            del arg[0]
        win32comext.shell.shell.ShellExecuteW(None, "runas", sys.executable, " ".join(arg), None, 1)
        if exit_after:
            sys.exit()
