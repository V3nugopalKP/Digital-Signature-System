from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib, os, json
from rsa_utils import generate_keys, sign_file, verify_file

app = Flask(__name__)
CORS(app)  # <-- allow frontend fetch
UPLOAD_FOLDER = "uploads"
SIGNATURE_FOLDER = "signatures"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNATURE_FOLDER, exist_ok=True)

@app.route("/generate_keys", methods=["GET"])
def generate_keys_route():
    public_key, private_key = generate_keys()
    with open("keys.json", "w") as f:
        json.dump({"public_key": public_key, "private_key": private_key}, f)
    return jsonify({"public_key": public_key, "private_key": private_key})

@app.route("/sign_file", methods=["POST"])
def sign_file_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    with open("keys.json", "r") as f:
        keys = json.load(f)
    signature = sign_file(filepath, keys["private_key"])
    sig_path = os.path.join(SIGNATURE_FOLDER, file.filename + ".sig")
    with open(sig_path, "w") as f:
        f.write(str(signature))
    return jsonify({"signature": signature})

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
    with open("keys.json", "r") as f:
        keys = json.load(f)
    with open(sig_path, "r") as f:
        signature = int(f.read().strip())
    valid = verify_file(file_path, signature, keys["public_key"])
    return jsonify({"verified": valid})

if __name__ == "__main__":
    app.run(debug=True)
