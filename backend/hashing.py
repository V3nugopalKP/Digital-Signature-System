import hashlib

def hash_file(file_data):
    """Takes bytes and returns a SHA-256 hash as integer"""
    file_hash = hashlib.sha256(file_data).hexdigest()
    return int(file_hash, 16)
