const BACKEND_URL = "https://digital-signature-backend.onrender.com";

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
    const file = document.getElementById("signFileInput").files[0];
    if (!file) { alert("Select a file to sign!"); return; }
    const formData = new FormData();
    formData.append("file", file);
    try {
        const res = await fetch(`${BACKEND_URL}/sign_file`, { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById("signOutput").innerText = `File signed successfully!\nSignature: ${data.signature}`;
    } catch (err) { console.error(err); alert("Failed to sign file!"); }
});

// Verify File
document.getElementById("verifyBtn").addEventListener("click", async () => {
    const file = document.getElementById("verifyFileInput").files[0];
    const sig = document.getElementById("verifySigInput").files[0];
    if (!file || !sig) { alert("Select both file and signature!"); return; }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("signature", sig);
    try {
        const res = await fetch(`${BACKEND_URL}/verify_file`, { method: "POST", body: formData });
        const data = await res.json();
        document.getElementById("verifyOutput").innerText = 
            `Verification result: ${data.verified ? "Authentic" : "Tampered"}`;
    } catch (err) { console.error(err); alert("Failed to verify file!"); }
});
