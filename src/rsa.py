import random
from math import gcd

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

def generate_prime(start=100, end=300):
    while True:
        p = random.randint(start, end)
        if is_prime(p):
            return p

def modinv(a, m):
    # Extended Euclidean Algorithm
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def generate_keys():
    p = generate_prime()
    q = generate_prime()
    while q == p:
        q = generate_prime()
    n = p * q
    phi = (p-1)*(q-1)
    
    e = 2
    while gcd(e, phi) != 1:
        e += 1
    
    d = modinv(e, phi)
    return (e, n), (d, n)  # public, private

def sign(hash_int, private_key):
    """Sign the hash modulo n"""
    hash_mod = hash_int % private_key[1]
    return pow(hash_mod, private_key[0], private_key[1])

def verify(signature_int, public_key):
    """Return the original hash modulo n"""
    return pow(signature_int, public_key[0], public_key[1])
