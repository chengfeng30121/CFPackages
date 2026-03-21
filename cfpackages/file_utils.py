
def read_file(path, encoding="utf-8"):
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

def write_file(path, content, encoding="utf-8"):
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)

def append_file(path, content, encoding="utf-8"):
    with open(path, 'a', encoding=encoding) as f:
        f.write(content)

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def write_bytes(path, content):
    with open(path, 'wb') as f:
        f.write(content)

def append_bytes(path, content):
    with open(path, 'ab') as f:
        f.write(content)
