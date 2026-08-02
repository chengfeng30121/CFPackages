from os import PathLike
from typing import Union

FilePath = Union[str, bytes, PathLike]


def read_file(path: FilePath, encoding: str = "utf-8") -> str:
    """读取文本文件全部内容。"""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_file(path: FilePath, content: str, encoding: str = "utf-8") -> None:
    """将文本写入文件（覆盖）。"""
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


def append_file(path: FilePath, content: str, encoding: str = "utf-8") -> None:
    """将文本追加到文件末尾。"""
    with open(path, "a", encoding=encoding) as f:
        f.write(content)


def read_bytes(path: FilePath) -> bytes:
    """读取二进制文件全部内容。"""
    with open(path, "rb") as f:
        return f.read()


def write_bytes(path: FilePath, content: bytes) -> None:
    """将二进制内容写入文件（覆盖）。"""
    with open(path, "wb") as f:
        f.write(content)


def append_bytes(path: FilePath, content: bytes) -> None:
    """将二进制内容追加到文件末尾。"""
    with open(path, "ab") as f:
        f.write(content)
