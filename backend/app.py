from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Indicators Backend",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ⚠️ In production, restrict this to your exact Firebase domain (e.g., https://your-site.web.app).
ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.web.app",
    "https://*.firebaseapp.com",
    "*",  # <-- Development convenience only. Replace with explicit origins later.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.get("/api/weather")
def weather():
    # Example: Your Python code does the work
    import random
    from datetime import datetime
    
    # Simulate calling a weather API
    temperature = random.randint(15, 30)
    conditions = ["Sunny", "Cloudy", "Rainy", "Windy"]
    condition = random.choice(conditions)
    
    # Your calculations
    feels_like = temperature + random.randint(-3, 3)
    humidity = random.randint(40, 80)
    
    # Return processed data to frontend
    return {
        "temperature": f"{temperature}°C",
        "condition": condition,
        "feels_like": f"{feels_like}°C",
        "humidity": f"{humidity}%",
        "timestamp": datetime.now().strftime("%H:%M")
    }
