// Frontend script to call the backend /api/hello

function normalizeBaseUrl(url) {
  if (!url) return "";
  // Trim trailing slash
  return url.replace(/\/+$/, "");
}

document.getElementById("pingBtn").addEventListener("click", async () => {
  const input = document.getElementById("backendUrl");
  const base = normalizeBaseUrl(input.value.trim() || window.location.origin);

  const output = document.getElementById("output");
  output.textContent = `GET ${base}/api/hello …`;

  try {
    const res = await fetch(`${base}/api/hello`, {
      method: "GET",
      headers: { "Accept": "application/json" }
    });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = `Request failed: ${err}`;
  }
});
