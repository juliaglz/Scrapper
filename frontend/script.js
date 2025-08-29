const BACKEND_URL = "https://scrapper-nq37.onrender.com";
const recordBtn = document.getElementById("record-btn");
const instructionInput = document.getElementById("instruction");

let mediaRecorder;
let audioChunks = [];

// --- Función de grabación y transcripción ---
recordBtn.addEventListener("click", async () => {
  try {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      // Pedir permiso y empezar a grabar
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", async () => {
        const audioBlob = new Blob(audioChunks);
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm"); // enviar como WebM

        try {
          const res = await fetch(`${BACKEND_URL}/stt`, { method: "POST", body: formData });
          if (!res.ok) throw new Error(`STT error: ${res.status}`);
          const data = await res.json();

          // Reemplazar texto en input con transcripción
          instructionInput.value = data.text || "";

        } catch (err) {
          console.error("No se pudo transcribir el audio", err);
          alert("No se pudo transcribir el audio");
        }
      });

      mediaRecorder.start();
      recordBtn.textContent = "⏹ Detener";

    } else if (mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      recordBtn.textContent = "🎤 Voz";
    }

  } catch (err) {
    console.error("Error accediendo al micrófono:", err);
    alert("No se pudo acceder al micrófono");
  }
});

// --- Formulario de scraping ---
document.getElementById("scrape-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const url = document.getElementById("url").value.trim();
  const instruction = instructionInput.value.trim();

  document.getElementById("output-data").textContent = "⏳ Running scraper...";
  document.getElementById("output-code").textContent = "⏳ Waiting for code...";

  try {
    const res = await fetch(`${BACKEND_URL}/scrape`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, instruction })
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);

    const { data, code } = await res.json();
    document.getElementById("output-data").textContent = JSON.stringify(data, null, 2);
    document.getElementById("output-code").textContent = code;

  } catch (err) {
    document.getElementById("output-data").textContent = `❌ Error: ${err.message}`;
    document.getElementById("output-code").textContent = "";
  }
});
