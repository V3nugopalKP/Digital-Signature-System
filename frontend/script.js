const BACKEND_URL = "https://digital-signature-backend-zrld.onrender.com"; // deployed backend

// Generate Keys
document.getElementById("generateKeysBtn").addEventListener("click", async () => {
    try {
        const res = await fetch(`${BACKEND_URL}/generate_keys`);
        const data = await res.json();
        document.getElementById("keysOutput").innerText =
            `Keys generated!\nPublic Key: ${JSON.stringify(data.public_key)}\nPrivate Key: ${JSON.stringify(data.private_key)}`;
    } catch (err) {
        console.error(err);
        alert("Failed to generate keys. Is backend running?");
    }
});

// Sign File
document.getElementById("signBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("signFileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file to sign!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${BACKEND_URL}/sign_file`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();

        // Show signature and download link
        document.getElementById("signOutput").innerHTML =
            `File signed successfully!<br>Signature: ${data.signature}<br>` +
            `<a href="${BACKEND_URL}${data.download_url}" download>Download Signature</a>`;
    } catch (err) {
        console.error(err);
        alert("Failed to sign file. Is backend running?");
    }
});

// Verify File
document.getElementById("verifyBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("verifyFileInput");
    const sigInput = document.getElementById("verifySigInput");

    const file = fileInput.files[0];
    const sig = sigInput.files[0];

    if (!file || !sig) {
        alert("Please select both the original file and the signature!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("signature", sig);

    try {
        const res = await fetch(`${BACKEND_URL}/verify_file`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        document.getElementById("verifyOutput").innerText =
            `Verification result: ${data.verified ? "Authentic ✅" : "Tampered ❌"}`;
    } catch (err) {
        console.error(err);
        alert("Failed to verify file. Is backend running?");
    }
});
