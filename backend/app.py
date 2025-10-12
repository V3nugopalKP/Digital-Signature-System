from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json
from rsa_utils import generate_keys, sign_file, verify_file

app = Flask(__name__)
CORS(app)  # allow frontend to call backend

UPLOAD_FOLDER = "uploads"
SIGNATURE_FOLDER = "signatures"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNATURE_FOLDER, exist_ok=True)

# Home route
@app.route("/")
def home():
    return jsonify({"message": "Digital Signature Backend is running!"})

# Generate keys
@app.route("/generate_keys", methods=["GET"])
def generate_keys_route():
    public_key, private_key = generate_keys()
    with open("keys.json", "w") as f:
        json.dump({"public_key": public_key, "private_key": private_key}, f)
    return jsonify({"public_key": public_key, "private_key": private_key})

# Sign file
@app.route("/sign_file", methods=["POST"])
def sign_file_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load keys
    with open("keys.json", "r") as f:
        keys = json.load(f)

    # Sign the file
    signature = sign_file(filepath, keys["private_key"])

    # Save signature
    sig_path = os.path.join(SIGNATURE_FOLDER, file.filename + ".sig")
    with open(sig_path, "w") as f:
        f.write(str(signature))

    # Provide download URL for .sig
    download_url = f"/download_signature/{file.filename}.sig"

    return jsonify({
        "signature": signature,
        "download_url": download_url
    })

# Download signature
@app.route("/download_signature/<filename>")
def download_signature(filename):
    return send_from_directory(SIGNATURE_FOLDER, filename)

# Verify file
@app.route("/verify_file", methods=["POST"])
def verify_file_route():
    if "file" not in request.files or "signature" not in request.files:
        return jsonify({"error": "Both file and signature are required"}), 400

    file = request.files["file"]
    sig_file = request.files["signature"]

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    sig_path = os.path.join(SIGNATURE_FOLDER, sig_file.filename)

    file.save(file_path)
    sig_file.save(sig_path)

    # Load keys
    with open("keys.json", "r") as f:
        keys = json.load(f)

    with open(sig_path, "r") as f:
        signature = int(f.read().strip())

    valid = verify_file(file_path, signature, keys["public_key"])
    return jsonify({"verified": valid})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
