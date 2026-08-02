import ctypes
import subprocess
import sys

if sys.platform != "win32":
    raise ImportError("本模块仅支持 Windows")


def is_admin() -> bool:
    """检测当前进程是否以管理员权限运行。"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        try:
            import win32comext.shell.shell as shell
            return bool(shell.IsUserAnAdmin())
        except Exception:
            return False


def _get_launch_args() -> list:
    """返回去掉解释器前缀后的命令行参数。"""
    args = sys.argv.copy()
    if args and args[0] == sys.executable:
        args.pop(0)  # 解释器本身会由 ShellExecuteW 重新指定
    return args


def get_admin(raise_admin: bool = False, exit_after: bool = True) -> None:
    """以管理员身份重新启动当前程序。

    已是管理员时直接返回（`raise_admin=True` 则抛 PermissionError）。
    提权重启后本进程立即退出（`exit_after=True`，默认）。
    """
    if is_admin():
        if raise_admin:
            raise PermissionError("当前已是管理员权限！")
        return
    cmdline = subprocess.list2cmdline(_get_launch_args())
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, cmdline, None, 1)
    if exit_after:
        sys.exit()
