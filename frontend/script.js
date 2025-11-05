// ================== BACKEND CONFIG ==================
const isLocal = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost";
const BACKEND_URL = isLocal
  ? "http://127.0.0.1:5000" // Local testing
  : "https://digital-signature-backend-zrld.onrender.com"; // Render backend


// ================== GENERATE KEYS ==================
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


// ================== SIGN FILE (Auto Download) ==================
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
      // Construct full download URL if missing base
      const downloadLink = data.download_url.startsWith("http")
        ? data.download_url
        : `${BACKEND_URL}${data.download_url}`;

      // ✅ Trigger auto download
      const link = document.createElement("a");
      link.href = downloadLink;
      link.download = data.signed_file;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // ✅ Display signing info
      document.getElementById("signOutput").innerHTML = `
        ✅ <b>File Signed Successfully!</b><br><br>
        <b>Signer:</b> ${data.user}<br>
        <b>Timestamp:</b> ${data.timestamp}<br>
        <b>File Hash (SHA-256):</b> ${data.file_hash}<br>
        <b>Signature:</b> ${data.signature}<br><br>
        <i>The signed file has been automatically downloaded to your system.</i>
      `;
    } else {
      document.getElementById("signOutput").innerText = "❌ Signing failed.";
    }
  } catch (err) {
    console.error(err);
    alert("Error signing file. Check backend connection.");
  }
});


// ================== VERIFY FILE ==================
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


// ================== SECTION NAVIGATION ==================
const signSection = document.getElementById("sign-section");
const verifySection = document.getElementById("verify-section");
const visualSection = document.getElementById("visual-section");

document.getElementById("nav-sign").addEventListener("click", () => {
  signSection.classList.remove("hidden");
  verifySection.classList.add("hidden");
  visualSection.classList.add("hidden");
  clearOutputs();
});

document.getElementById("nav-verify").addEventListener("click", () => {
  verifySection.classList.remove("hidden");
  signSection.classList.add("hidden");
  visualSection.classList.add("hidden");
  clearOutputs();
});

document.getElementById("nav-visual").addEventListener("click", () => {
  visualSection.classList.remove("hidden");
  signSection.classList.add("hidden");
  verifySection.classList.add("hidden");
  clearOutputs();
});

function clearOutputs() {
  document.getElementById("signOutput").innerHTML = "";
  document.getElementById("verifyOutput").innerHTML = "";
}


// ================== VISUALIZATION ANIMATION ==================
document.getElementById("startVisualizationBtn").addEventListener("click", async () => {
  const steps = [
    "🔑 <b>Step 1: Generate Keys</b><br>RSA creates a Public & Private key pair.",
    "🧮 <b>Step 2: Hash File</b><br>The file is converted into a unique SHA-256 fingerprint.",
    "✍️ <b>Step 3: Sign Hash</b><br>The hash is encrypted using the Private Key to produce a signature.",
    "📎 <b>Step 4: Embed Signature</b><br>The signature, timestamp, and user details are embedded in the file.",
    "🧾 <b>Step 5: Verify File</b><br>The hash is recalculated and compared with the decrypted signature.",
    "✅ <b>Result:</b> If both match → File is Authentic. Otherwise → Tampered!"
  ];

  const box = document.getElementById("visualSteps");
  box.innerHTML = "";
  for (let step of steps) {
    const p = document.createElement("p");
    p.innerHTML = step;
    box.appendChild(p);
    await new Promise(r => setTimeout(r, 1000));
  }
});
