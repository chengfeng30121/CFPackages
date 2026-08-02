from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from typing import List, Optional, Tuple
import warnings
import questionary


def _normalize_options(options: list) -> list:
    """统一为 `(text, key)` 二元组列表：字符串元素以自身作为 text 和 key。"""
    normalized = []
    for opt in options:
        if isinstance(opt, str):
            normalized.append((opt, opt))
        else:
            normalized.append((opt[0], opt[1]))
    return normalized


def multi_select(options: list, title: Optional[str] = None) -> Optional[list]:
    """复选列表选择，返回选中的 key 列表；ESC 取消时返回 None。

    `options` 接受字符串列表（`["选项 a"]`）或 `(text, key)` 二元组列表。
    空格: 选择/取消  方向键: 移动  Enter: 确认  ESC: 取消
    """
    normalized = _normalize_options(options)
    if not normalized:
        return []
    title = title or "请选择"
    keys = [key for _, key in normalized]
    texts = [text for text, _ in normalized]
    selected = [False] * len(normalized)
    pointer = 0
    kb = KeyBindings()

    @kb.add('down')
    def move_down(event) -> None:
        nonlocal pointer
        pointer = (pointer + 1) % len(normalized)

    @kb.add('up')
    def move_up(event) -> None:
        nonlocal pointer
        pointer = (pointer - 1) % len(normalized)

    @kb.add('space')
    def toggle_selection(event) -> None:
        selected[pointer] = not selected[pointer]

    @kb.add('enter')
    def confirm(event) -> None:
        event.app.exit([keys[i] for i in range(len(keys)) if selected[i]])

    @kb.add('escape')
    def cancel(event) -> None:
        event.app.exit(None)

    def get_text() -> List[Tuple[str, str]]:
        result = [('', f"{title}:\n")]
        for i, text in enumerate(texts):
            style = '#ffff00' if selected[i] else ''
            if i == pointer:
                style += ' reverse'
            result.append((style, f"  {text}\n"))
        result.append(('', "空格: 选择/取消  方向键: 移动  Enter: 确认  ESC: 取消\n"))
        return result

    control = FormattedTextControl(get_text)
    layout = Layout(Window(content=control))
    style = Style.from_dict({'reverse': 'reverse'})
    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=False,
    )
    return app.run()


def single_select(options: list, title: Optional[str] = None) -> Optional[str]:
    """单选列表选择，返回选中的 key；ESC 取消时返回 None。

    `options` 接受字符串列表（`["选项 a"]`）或 `(text, key)` 二元组列表。
    """
    normalized = _normalize_options(options)
    if not normalized:
        return None
    title = title or "请选择"
    result = questionary.select(
        title, [text for text, _ in normalized],
        instruction="(使用箭头选择，ESC 取消)").ask()
    if result is None:
        return None
    for text, key in normalized:
        if text == result:
            return key
    return None


def checkbox_selection(options: list, title: Optional[str] = None):
    """已弃用，请改用 multi_select（参数顺序已变更为 `(text, key)`）。"""
    warnings.warn(
        "checkbox_selection 已弃用，请改用 multi_select",
        DeprecationWarning, stacklevel=2)
    flipped = [(text, key) for key, text in options]
    return multi_select(flipped, title)


def radio_selection(options: list, title: Optional[str] = None):
    """已弃用，请改用 single_select（参数顺序已变更为 `(text, key)`）。"""
    warnings.warn(
        "radio_selection 已弃用，请改用 single_select",
        DeprecationWarning, stacklevel=2)
    flipped = [(text, key) for key, text in options]
    return single_select(flipped, title)


# 用法示例:
# cfpackages.text_ui.multi_select(["选项 a", "选项 b"])
# cfpackages.text_ui.multi_select([("选项 a", "a"), ("选项 b", "b")])
# cfpackages.text_ui.single_select(["选项 a", "选项 b"])
# cfpackages.text_ui.single_select([("选项 a", "a"), ("选项 b", "b")])
