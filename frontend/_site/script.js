document.getElementById("scrape-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const url = document.getElementById("url").value.trim();
  const instruction = document.getElementById("instruction").value.trim();

  document.getElementById("output-data").textContent = "⏳ Running scraper...";
  document.getElementById("output-code").textContent = "⏳ Waiting for code...";

  try {
    const res = await fetch("http://localhost:8000/scrape", {
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
