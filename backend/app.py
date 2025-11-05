from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, datetime
from rsa_utils import generate_keys, sign_file, verify_file
from zoneinfo import ZoneInfo  # for IST timezone (Python 3.9+)

app = Flask(__name__)
CORS(app)

# ===== Folder Setup =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
SIGNED_FOLDER = os.path.join(BASE_DIR, "signed_files")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

# ===== Home Route =====
@app.route("/")
def home():
    return jsonify({"message": "Digital Signature Backend (Advanced) is running!"})


# ===== Generate RSA Keys =====
@app.route("/generate_keys", methods=["GET"])
def generate_keys_route():
    public_key, private_key = generate_keys()
    with open(os.path.join(BASE_DIR, "keys.json"), "w") as f:
        json.dump({"public_key": public_key, "private_key": private_key}, f)
    return jsonify({"public_key": public_key, "private_key": private_key})


# ===== Sign File =====
@app.route("/sign_file", methods=["POST"])
def sign_file_route():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    user = request.form.get("user", "Anonymous")

    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    signed_path = os.path.join(SIGNED_FOLDER, file.filename)
    file.save(upload_path)

    # Load private key
    with open(os.path.join(BASE_DIR, "keys.json"), "r") as f:
        keys = json.load(f)
    private_key = keys["private_key"]

    # Create signature and file hash
    signature, file_hash = sign_file(upload_path, private_key)

    # ✅ Generate correct IST timestamp
    ist = ZoneInfo("Asia/Kolkata")
    timestamp = datetime.datetime.now(ist).strftime("%d-%b-%Y %I:%M:%S %p %Z")

    # Create signature metadata block
    signature_block = (
        f"\n\n---DIGITAL SIGNATURE DATA---\n"
        f"User: {user}\n"
        f"Timestamp: {timestamp}\n"
        f"File Hash: {file_hash}\n"
        f"Signature: {signature}\n"
        f"Public Key: {keys['public_key']}\n"
        f"---END SIGNATURE DATA---\n"
    ).encode("utf-8")

    # Write signed file (binary safe)
    with open(upload_path, "rb") as f:
        original_data = f.read()
    with open(signed_path, "wb") as f:
        f.write(original_data)
        f.write(signature_block)

    print(f"✅ Signed file saved at: {signed_path}")

    # ✅ Create absolute download link (works both locally and on Render)
    if "render" in request.host or "onrender.com" in request.host:
        base_url = f"https://{request.host}"
    else:
        base_url = f"http://{request.host}"

    download_url = f"{base_url}/download_signed/{file.filename}"

    return jsonify({
        "message": "File signed successfully!",
        "signed_file": file.filename,
        "download_url": download_url,
        "user": user,
        "timestamp": timestamp,
        "signature": signature,
        "file_hash": file_hash
    })


# ===== Download Signed File =====
@app.route("/download_signed/<filename>")
def download_signed(filename):
    return send_from_directory(SIGNED_FOLDER, filename, as_attachment=True)


# ===== Verify File (Binary Safe) =====
@app.route("/verify_file", methods=["POST"])
def verify_file_route():
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]
    upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(upload_path)

    # ✅ Read as binary to preserve exact bytes
    with open(upload_path, "rb") as f:
        file_bytes = f.read()

    try:
        content_str = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return jsonify({"verified": False, "message": "File decoding error."})

    if "---DIGITAL SIGNATURE DATA---" not in content_str:
        return jsonify({"verified": False, "message": "❌ No embedded signature found."})

    # Extract original content & metadata
    original_content_str, metadata_block = content_str.split("---DIGITAL SIGNATURE DATA---", 1)
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

    # ✅ Recreate only the original bytes before metadata
    metadata_index = file_bytes.find(b"---DIGITAL SIGNATURE DATA---")
    original_bytes = file_bytes[:metadata_index]

    # Save temporary file for verification
    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(original_bytes)

    valid = verify_file(temp_path, signature, public_key)
    os.remove(temp_path)

    return jsonify({
        "verified": valid,
        "message": "✅ File is Authentic" if valid else "❌ Signature Invalid or Tampered",
        "user": user,
        "timestamp": timestamp,
        "file_hash": file_hash
    })


# ===== Run Flask App =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
