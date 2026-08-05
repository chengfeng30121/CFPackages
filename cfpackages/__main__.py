"""cfpackages 命令行入口: python -m cfpackages"""
from . import __version__, _check_update, _compare_version, _fetch_latest_version
from . import http_utils, text_ui

_MENU = [
    ("检查更新", "check_update"),
    ("生成 Headers（交互式输入）", "gen_headers"),
    ("退出", "exit"),
]


def _do_check_update() -> None:
    """检查更新并打印结果，同时写入检查时间缓存。"""
    print(f"当前版本: cfpackages {__version__}")
    latest = _fetch_latest_version()
    if latest is None:
        print("检查失败：无法获取最新版本（请检查网络连接）")
        return
    if _compare_version(__version__, latest):
        print(f"发现新版本: cfpackages {__version__} -> {latest}")
        print("运行 `pip install cfpackages --upgrade` 即可更新")
    else:
        print(f"已是最新版本: cfpackages {latest}")
    _check_update()  # 写入检查时间缓存，避免下次导入时再触发后台检查


def main() -> None:
    while True:
        choice = text_ui.single_select(_MENU, title="cfpackages 工具菜单")
        if choice == "check_update":
            _do_check_update()
        elif choice == "gen_headers":
            http_utils.get_headers_from_user_input(print_headers=True)
        else:
            break


if __name__ == "__main__":
    main()
