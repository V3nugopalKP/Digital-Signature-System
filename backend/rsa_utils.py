import random
import hashlib

# --------------------------------------------
# 🔢 Mathematical Helper Functions
# --------------------------------------------

def gcd(a, b):
    """Compute GCD using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def modinv(a, m):
    """Compute Modular Inverse using Extended Euclidean algorithm."""
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception("No modular inverse exists")
    return x % m


def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# --------------------------------------------
# 🔐 RSA Key Generation
# --------------------------------------------

def generate_keys():
    """Generate public and private RSA keys."""
    p = random.choice([i for i in range(200, 500) if is_prime(i)])
    q = random.choice([i for i in range(200, 500) if is_prime(i) and i != p])
    n = p * q
    phi = (p - 1) * (q - 1)

    # Common choice for e
    e = 65537
    if gcd(e, phi) != 1:
        e = 3

    d = modinv(e, phi)
    return (e, n), (d, n)


# --------------------------------------------
# 🔢 Hashing Function
# --------------------------------------------

def hash_file(filepath):
    """
    Hash file contents using SHA-256.
    Returns both hex digest (for display) and integer (for math).
    """
    with open(filepath, "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    return h, int(h, 16)


# --------------------------------------------
# ✍️ Signing and Verification Functions
# --------------------------------------------

def sign_file(filepath, private_key):
    """
    Generate a digital signature for the file.
    - Compute file hash (SHA-256)
    - Compute signature = (hash^d mod n)
    Returns (signature, hash_hex)
    """
    d, n = private_key
    hash_hex, hash_val = hash_file(filepath)
    signature = pow(hash_val % n, d, n)
    return signature, hash_hex


def verify_file(filepath, signature, public_key):
    """
    Verify the authenticity of a file using the public key.
    - Recalculate hash
    - Decrypt signature using (sig^e mod n)
    - Compare both values
    Returns True if authentic, else False.
    """
    e, n = public_key
    hash_hex, hash_val = hash_file(filepath)
    verified = pow(signature, e, n)
    return (verified == hash_val % n)
