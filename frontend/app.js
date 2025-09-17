// Dashboard that loads data from backend

const BACKEND_URL = "https://indicators-dashboard-he1e.onrender.com";

async function loadDashboardData() {
  const messageElement = document.getElementById("dashboard-message");
  
  try {
    // Load the main message
    const helloResponse = await fetch(`${BACKEND_URL}/api/hello`);
    const helloData = await helloResponse.json();
    
    // Try to load weather data (your Python calculations)
    try {
      const weatherResponse = await fetch(`${BACKEND_URL}/api/weather`);
      
      if (weatherResponse.ok) {
        const weatherData = await weatherResponse.json();
        
        // Display everything with weather
        messageElement.innerHTML = `
          <div style="margin-bottom: 20px;">
            <strong>${helloData.message}</strong>
          </div>
          <div style="font-size: 18px; color: #a0a8c0;">
            🌡️ ${weatherData.temperature} (feels like ${weatherData.feels_like})<br>
            ☁️ ${weatherData.condition}<br>
            💧 Humidity: ${weatherData.humidity}<br>
            🕐 Updated: ${weatherData.timestamp}
          </div>
        `;
      } else {
        // Weather API not available yet, show only main message
        messageElement.innerHTML = `
          <div style="margin-bottom: 20px;">
            <strong>${helloData.message}</strong>
          </div>
          <div style="font-size: 16px; color: #a0a8c0;">
            ⏳ Weather data coming soon... (deploying)
          </div>
        `;
      }
    } catch (weatherError) {
      // Weather API not available yet, show only main message
      messageElement.innerHTML = `
        <div style="margin-bottom: 20px;">
          <strong>${helloData.message}</strong>
        </div>
        <div style="font-size: 16px; color: #a0a8c0;">
          ⏳ Weather data coming soon... (deploying)
        </div>
      `;
    }
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
