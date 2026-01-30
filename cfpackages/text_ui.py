from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from typing import List, Optional, Tuple
import questionary


languages = {
    "zh": [
        "请选择",
        "空格: 选择/取消  方向键: 移动  Enter: 确认选择",
        "未选择",
        "按 Enter 确认选择  按 ESC 返回修改",
        "(使用箭头选择)"
    ],
    "en": [
        "Please choose:",
        "Space: Select/Unselect  Arrow: Move  Enter: Confirm",
        "Not selected",
        "Press Enter to confirm selection  Press ESC to back",
        "(use arrow keys to choose)"
    ]
}
language = languages["zh"]


def checkbox_selection(options: list, title: Optional[str] = language[0]) -> list:
    selected = [False] * len(options)
    pointer = 0
    show_options = True
    kb = KeyBindings()

    @kb.add('down')
    def move_down(event) -> None:
        nonlocal pointer
        if show_options:
            pointer = (pointer + 1) % len(options)

    @kb.add('up')
    def move_up(event) -> None:
        nonlocal pointer
        if show_options:
            pointer = (pointer - 1) % len(options)

    @kb.add('space')
    def toggle_selection(event) -> None:
        if show_options:
            selected[pointer] = not selected[pointer]

    @kb.add('enter')
    def accept(event) -> None:
        nonlocal show_options
        if show_options:
            show_options = False
        else:
            event.app.exit()

    @kb.add('escape')
    def back_to_selection(event) -> None:
        nonlocal show_options
        if not show_options:
            show_options = True

    def get_text() -> List[Tuple[str, str]]:
        selected_items = [options[i][1] for i in range(len(options)) if selected[i]]
        if show_options:
            result = []
            result.append(('', f"{title}:\n"))

            for i, (key, text) in enumerate(options):
                if selected[i]:
                    style = '#ffff00'
                else:
                    style = ''

                if i == pointer:
                    style += ' reverse'

                result.append((style, f"  {text}\n"))

            result.append(('\n', language[1]))
            return result
        else:
            selected_text = ", ".join(selected_items) if selected_items else language[2]
            return [
                ('', f"{title}: {selected_text}\n"),
                ('', language[3])
            ]

    control = FormattedTextControl(get_text)
    layout = Layout(Window(content=control))
    style = Style.from_dict({
        'reverse': 'reverse',
    })
    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=False
    )
    app.run()
    return [options[i][0] for i in range(len(options)) if selected[i]]


def radio_selection(options: list, title: Optional[str] = language[0]) -> str:
    data = {}
    for option in options:
        data[option[1]] = option[0]
    result = questionary.select(title, list(data.keys()), instruction=language[4]).ask()
    return data[result]


# Usage:
# cfpackages.text_ui.radio_selection([("a", "input: a"), ("b", "input: b")])
# cfpackages.text_ui.checkbox_selection([("a", "input: a"), ("b", "input: b")])
