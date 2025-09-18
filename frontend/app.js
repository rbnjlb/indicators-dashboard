// Dashboard that loads data from backend

const BACKEND_URL = "https://indicators-dashboard-he1e.onrender.com";

async function loadDashboardData() {
  const messageElement = document.getElementById("dashboard-message");

  if (!messageElement) {
    console.error("Missing dashboard message element");
    return;
  }

  try {
    let weatherMarkup = `
      <div style="font-size: 16px; color: #a0a8c0;">
        ⏳ Weather data coming soon... (JAMAIS)
        <br>
      </div>
    `;

    // Try to load weather data (your Python calculations)
    try {
      const weatherResponse = await fetch(`${BACKEND_URL}/api/weather`);

      if (weatherResponse.ok) {
        const weatherData = await weatherResponse.json();

        weatherMarkup = `
          <div style="font-size: 18px; color: #a0a8c0;">
            🌡️ ${weatherData.temperature} (feels like ${weatherData.feels_like})<br>
            ☁️ ${weatherData.condition}<br>
            💧 Humidity: ${weatherData.humidity}<br>
            🕐 Updated: ${weatherData.timestamp}
          </div>
        `;
      }
    } catch (weatherError) {
      console.warn("Weather data unavailable:", weatherError);
    }

    // Display everything with or without weather
    messageElement.innerHTML = `
      <div style="margin-bottom: 20px;">
        <strong>Indicators are on the way!</strong>
        <br>
      </div>
      ${weatherMarkup}
    `;
  } catch (error) {
    console.error("Error:", error);
    messageElement.innerHTML = `
      <div style="color: #ff6b6b;">
        ❌ Erreur: ${error.message}<br>
        <small>Vérifiez la console pour plus de détails</small>
      </div>
    `;
  }
}

// Load data when the page loads
document.addEventListener("DOMContentLoaded", loadDashboardData);
