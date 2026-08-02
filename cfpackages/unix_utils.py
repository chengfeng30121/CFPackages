import os
import sys

if sys.platform == "win32":
    raise ImportError("本模块仅支持 Unix 类系统")


def is_admin() -> bool:
    """检测当前进程是否以 root 权限运行。"""
    return os.getuid() == 0


def get_admin(raise_admin: bool = False) -> None:
    """通过 sudo 以 root 身份重新启动当前程序（以 exec 替换本进程）。

    已是 root 时直接返回（`raise_admin=True` 则抛 PermissionError）。
    """
    if is_admin():
        if raise_admin:
            raise PermissionError("当前已是 root 权限！")
        return
    os.execvp("sudo", ["sudo"] + sys.argv)
