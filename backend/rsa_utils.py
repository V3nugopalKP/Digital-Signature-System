import random
import hashlib

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def modinv(a, m):
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('No modular inverse')
    return x % m

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_keys():
    p = random.choice([i for i in range(200, 500) if is_prime(i)])
    q = random.choice([i for i in range(200, 500) if is_prime(i) and i != p])
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if gcd(e, phi) != 1:
        e = 3
    d = modinv(e, phi)
    return (e, n), (d, n)

def hash_file(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    return int(h, 16)

def sign_file(filepath, private_key):
    d, n = private_key
    hash_val = hash_file(filepath)
    return pow(hash_val % n, d, n)

def verify_file(filepath, signature, public_key):
    e, n = public_key
    hash_val = hash_file(filepath)
    return (pow(signature, e, n) == hash_val % n)
