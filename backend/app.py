from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, datetime
from rsa_utils import generate_keys, sign_file, verify_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
SIGNED_FOLDER = "signed_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

# Home route
@app.route("/")
def home():
    return jsonify({"message": "Digital Signature Backend (Advanced) is running!"})


# 🧩 Generate Keys
@app.route("/generate_keys", methods=["GET"])
def generate_keys_route():
    public_key, private_key = generate_keys()
    with open("keys.json", "w") as f:
        json.dump({"public_key": public_key, "private_key": private_key}, f)
    return jsonify({"public_key": public_key, "private_key": private_key})


# ✍️ Sign File (with username + timestamp embedded)
@app.route("/sign_file", methods=["POST"])
def sign_file_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    user = request.form.get("user", "Anonymous")  # user name from frontend
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Load private key
    with open("keys.json", "r") as f:
        keys = json.load(f)
    private_key = keys["private_key"]

    # Sign file -> returns signature + hash
    signature, file_hash = sign_file(file_path, private_key)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create metadata block to embed
    signature_block = (
        "\n\n---DIGITAL SIGNATURE DATA---\n"
        f"User: {user}\n"
        f"Timestamp: {timestamp}\n"
        f"File Hash: {file_hash}\n"
        f"Signature: {signature}\n"
        f"Public Key: {keys['public_key']}\n"
        "---END SIGNATURE DATA---\n"
    )

    # Embed the signature block at end of file
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    signed_content = content + signature_block

    signed_path = os.path.join(SIGNED_FOLDER, file.filename)
    with open(signed_path, "w", encoding="utf-8") as f:
        f.write(signed_content)

    return jsonify({
        "message": "File signed successfully!",
        "signed_file": file.filename,
        "user": user,
        "timestamp": timestamp,
        "signature": signature,
        "file_hash": file_hash
    })


# ✅ Verify File (read embedded signature info)
@app.route("/verify_file", methods=["POST"])
def verify_file_route():
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Extract embedded signature block
    if "---DIGITAL SIGNATURE DATA---" not in content:
        return jsonify({"verified": False, "message": "❌ No embedded signature found."})

    original_content, metadata_block = content.split("---DIGITAL SIGNATURE DATA---", 1)
    metadata_lines = metadata_block.splitlines()

    # Parse metadata
    meta = {}
    for line in metadata_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()

    try:
        signature = int(meta["Signature"])
        file_hash = meta["File Hash"]
        user = meta.get("User", "Unknown")
        timestamp = meta.get("Timestamp", "Unknown")
        public_key = json.loads(meta["Public Key"].replace("'", '"'))
    except Exception as e:
        return jsonify({"verified": False, "message": f"Metadata error: {str(e)}"})

    # Write only original content temporarily for verification
    temp_original_path = os.path.join(UPLOAD_FOLDER, f"temp_{file.filename}")
    with open(temp_original_path, "w", encoding="utf-8") as f:
        f.write(original_content)

    valid = verify_file(temp_original_path, signature, public_key)
    os.remove(temp_original_path)

    return jsonify({
        "verified": valid,
        "message": "✅ File is Authentic" if valid else "❌ Signature Invalid or Tampered",
        "user": user,
        "timestamp": timestamp,
        "file_hash": file_hash
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
