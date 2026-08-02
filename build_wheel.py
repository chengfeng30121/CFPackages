################################################################################

try:
    from cfpackages.logger_formatter import get_logger
    logger = get_logger(__name__)
except ImportError:
    class logger:
        """简易日志类"""
        def __getattr__(self, name):
            return lambda *args, **kwargs: print(f"[{name.upper()}]", *args, **kwargs)

try:
    import build
except ImportError:
    print("请先安装 `build` 包: pip install build")
    exit(1)
try:
    import twine
except ImportError:
    print("请先安装 `twine` 包: pip install twine")
    exit(1)

import subprocess
import shutil
import sys


def _run(cmd: list) -> None:
    """运行子命令，失败时非零退出。"""
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(f"命令执行失败: {' '.join(cmd)} (退出码 {result.returncode})")


def build_package():
    """构建安装包"""
    print("正在构建安装包...")
    _run([sys.executable, "-m", "build"])


def clean_build():
    """清理构建产物"""
    print("正在清理构建目录...")
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("cfpackages.egg-info", ignore_errors=True)
    shutil.rmtree("cfpackages/__pycache__", ignore_errors=True)


def upload_package():
    """上传到 PyPI"""
    print("正在上传到 PyPI...")
    _run([sys.executable, "-m", "twine", "upload", "dist/*"])


def upload_test_package():
    """上传到 Test PyPI"""
    print("正在上传到 Test PyPI...")
    _run([sys.executable, "-m", "twine", "upload", "--repository", "testpypi", "dist/*"])


################################################################################

import questionary

if __name__ == "__main__":
    result = questionary.select("选择要执行的操作", [
        "全部执行（测试环境）",
        "全部执行（生产环境）",
        "构建安装包",
        "清理构建产物",
        "上传到 PyPI",
        "上传到 Test PyPI",
    ]).ask()

    if result == "全部执行（测试环境）":
        clean_build()
        build_package()
        # upload_package()
        upload_test_package()
        clean_build()
    elif result == "全部执行（生产环境）":
        clean_build()
        build_package()
        upload_package()
        # upload_test_package()
        clean_build()
    elif result == "构建安装包":
        build_package()
    elif result == "清理构建产物":
        clean_build()
    elif result == "上传到 PyPI":
        upload_package()
    elif result == "上传到 Test PyPI":
        upload_test_package()
    else:
        logger.info("用户取消了操作。")
    logger.info("全部完成！")
