// Simple dashboard that automatically loads message from backend

const BACKEND_URL = "https://indicators-dashboard-he1e.onrender.com";

async function loadDashboardMessage() {
  const messageElement = document.getElementById("dashboard-message");
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/hello`);
    const data = await response.json();
    messageElement.textContent = data.message;
  } catch (error) {
    messageElement.textContent = "Erreur de connexion au serveur";
  }
}

// Load the message when the page loads
document.addEventListener("DOMContentLoaded", loadDashboardMessage);
