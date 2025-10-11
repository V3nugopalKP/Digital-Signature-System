from rsa import generate_keys, sign, verify
from hashing import hash_file
import os

def main():
    print("=== Digital Signature System ===")
    
    # Generate keys
    public_key, private_key = generate_keys()
    print("Public Key:", public_key)
    print("Private Key:", private_key)
    
    # Select file
    file_path = input("Enter file path to sign (e.g., test_files/example.pdf): ")
    if not os.path.exists(file_path):
        print("File does not exist!")
        return
    
    # Hash the file
    file_hash = hash_file(file_path)
    print("SHA-256 hash of file:", file_hash)
    
    # Sign the hash
    signature = sign(file_hash, private_key)
    print("Signature:", signature)
    
    # Verify signature
    verified_hash = verify(signature, public_key)
    if verified_hash == file_hash:
        print("Verification Successful: File is authentic")
    else:
        print("Verification Failed: File has been tampered")

if __name__ == "__main__":
    main()
