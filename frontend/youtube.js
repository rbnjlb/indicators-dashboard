const LOCAL_HOSTNAMES = new Set(["localhost", "127.0.0.1", "0.0.0.0"]);
const BACKEND_URL = LOCAL_HOSTNAMES.has(window.location.hostname)
  ? "http://localhost:8000"
  : "https://indicators-dashboard-he1e.onrender.com";

function setStatus(message, type = "info") {
  const statusEl = document.getElementById("download-status");
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.dataset.status = type;
}

function renderResult(data) {
  const resultEl = document.getElementById("download-result");
  if (!resultEl) return;

  if (!data) {
    resultEl.innerHTML = "";
    return;
  }

  const downloadHref = data.download_url.startsWith("http")
    ? data.download_url
    : `${BACKEND_URL}${data.download_url}`;

  resultEl.innerHTML = `
    <div class="download-card">
      <h3>Download ready</h3>
      <p>
        <span class="result-label">Video ID:</span>
        <code>${data.video_id}</code>
      </p>
      <a class="result-link" href="${downloadHref}" download>
        ⬇️ Download ${data.filename}
      </a>
    </div>
  `;
}

async function handleSubmit(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const urlInput = document.getElementById("video-url");
  if (!urlInput) return;

  const url = urlInput.value.trim();
  if (!url) {
    setStatus("Please enter a valid YouTube URL.", "error");
    return;
  }

  setStatus("Processing… this can take a minute for long videos.", "pending");
  renderResult(null);

  try {
    const response = await fetch(`${BACKEND_URL}/api/youtube/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      const message = error.detail || "Download failed";
      throw new Error(message);
    }

    const data = await response.json();
    setStatus("Success! Your video is ready.", "success");
    renderResult(data);
  } catch (err) {
    console.error("YouTube download failed", err);
    setStatus(err.message || "Something went wrong.", "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("download-form");
  if (form) {
    form.addEventListener("submit", handleSubmit);
  }
});
