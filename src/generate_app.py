import os
import requests
import json

# OpenRouter API kulcs (helyettesítsd a sajátoddal)
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("API key not found")

# OpenRouter DeepSeek Coder endpoint
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Toolcalling beállítása, hogy csak futtatható React kódot generáljon
TOOLS = [
    {
        "type": "code",
        "format": "javascript",
        "language": "react"
    }
]

# Prompt: React Todo alkalmazás generálása
prompt = "Készíts egy egyszerű React Todo alkalmazást."

# API kérés előkészítése
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-coder",
    "messages": [{"role": "user", "content": prompt}],
    "tools": TOOLS,  # Toolcalling megadása
    "max_tokens": 800  # Limitáljuk a választ
}

# API hívás
response = requests.post(API_URL, headers=headers, json=data)

# Válasz feldolgozása
if response.status_code == 200:
    result = response.json()
    generated_code = result["choices"][0]["message"]["content"]
    
    # A generált kód mentése egy fájlba
    with open("todo_app.txt", "w") as f:
        f.write(generated_code)

    print("✅ React Todo alkalmazás generálva: todo_app.txt")
else:
    print("❌ Hiba történt:", response.text)
