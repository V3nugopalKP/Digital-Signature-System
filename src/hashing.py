import hashlib

def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return int(sha256.hexdigest(), 16)  # convert hex digest to int
