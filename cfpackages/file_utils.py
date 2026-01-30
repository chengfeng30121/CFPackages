
def read_file(path):
    with open(path, 'r', encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(content)

def append_file(path, content):
    with open(path, 'a', encoding="utf-8") as f:
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
