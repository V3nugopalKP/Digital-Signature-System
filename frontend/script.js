const BACKEND_URL = "https://digital-signature-backend-zrld.onrender.com"; // your deployed backend

// ========== Generate Keys ==========
document.getElementById("generateKeysBtn").addEventListener("click", async () => {
    try {
        const res = await fetch(`${BACKEND_URL}/generate_keys`);
        const data = await res.json();
        document.getElementById("keysOutput").innerText =
            `✅ Keys generated successfully!\n\nPublic Key: ${JSON.stringify(data.public_key)}\nPrivate Key: ${JSON.stringify(data.private_key)}`;
    } catch (err) {
        console.error(err);
        alert("Failed to generate keys. Please check if backend is active.");
    }
});


// ========== Sign File (with username + timestamp) ==========
document.getElementById("signBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("signFileInput");
    const username = document.getElementById("usernameInput")?.value?.trim() || "Anonymous";
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file to sign!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user", username);

    try {
        const res = await fetch(`${BACKEND_URL}/sign_file`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();

        if (data.message) {
            document.getElementById("signOutput").innerHTML = `
                ✅ <b>File Signed Successfully!</b><br><br>
                <b>Signer:</b> ${data.user}<br>
                <b>Timestamp:</b> ${data.timestamp}<br>
                <b>File Hash (SHA-256):</b> ${data.file_hash}<br>
                <b>Signature:</b> ${data.signature}<br><br>
                <i>The signed file now contains embedded signature metadata.</i>
            `;
        } else {
            document.getElementById("signOutput").innerText = "❌ Signing failed.";
        }
    } catch (err) {
        console.error(err);
        alert("Error signing file. Check backend connection.");
    }
});


// ========== Verify File ==========
document.getElementById("verifyBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("verifyFileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload the signed file to verify!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${BACKEND_URL}/verify_file`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();

        if (data.verified) {
            document.getElementById("verifyOutput").innerHTML = `
                ✅ <b>Signature Verified Successfully!</b><br><br>
                <b>Signer:</b> ${data.user}<br>
                <b>Timestamp:</b> ${data.timestamp}<br>
                <b>File Hash:</b> ${data.file_hash}<br>
                <b>Status:</b> Authentic ✅<br>
            `;
        } else {
            document.getElementById("verifyOutput").innerHTML = `
                ❌ <b>Signature Verification Failed!</b><br>
                Reason: ${data.message || "File may be tampered or unsigned."}
            `;
        }
    } catch (err) {
        console.error(err);
        alert("Verification failed. Please ensure backend is active.");
    }
});
