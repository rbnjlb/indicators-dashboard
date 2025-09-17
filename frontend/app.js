// Dashboard that loads data from backend

const BACKEND_URL = "https://indicators-dashboard-he1e.onrender.com";

async function loadDashboardData() {
  const messageElement = document.getElementById("dashboard-message");
  
  try {
    // Load the main message
    const helloResponse = await fetch(`${BACKEND_URL}/api/hello`);
    const helloData = await helloResponse.json();
    
    // Load weather data (your Python calculations)
    const weatherResponse = await fetch(`${BACKEND_URL}/api/weather`);
    
    if (!weatherResponse.ok) {
      throw new Error(`Weather API error: ${weatherResponse.status}`);
    }
    
    const weatherData = await weatherResponse.json();
    
    // Display everything
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
