# Több tipusú fájlt képes generált néven menteni.

import os
import requests
import json

if not os.path.exists("generated_code"):
    os.makedirs("generated_code")

# OpenRouter API kulcs (helyettesítsd a sajátoddal)
API_KEY = "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"

# OpenRouter DeepSeek Coder endpoint
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Toolcalling beállítása
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_code",
            "description": "Generate raw code for multiple components based on a detailed description. Return a list of codes, filenames, and file extensions, without any additional text or explanations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "The detailed code generated by the AI for a component."
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "The name of the file where the code should be saved, e.g., 'LoginScreen.jsx' or 'main.cpp'."
                                },
                                "file_extension": {
                                    "type": "string",
                                    "description": "The file extension, e.g., '.jsx', '.cpp', '.py'."
                                }
                            },
                            "required": ["code", "filename", "file_extension"]
                        },
                        "description": "A list of components, each containing code, a filename, and a file extension."
                    }
                },
                "required": ["components"]
            }
        }
    }
]

def read_files_from_folder(folder_path):
    files = {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                files[filename] = file.read()
    return files

# Prompt: Kód generálás
prompt = """
Generálj egy react komponenst, ami beolvassa a felhasználó nevét és ezt menti local storage-ba és egy másik komponenst ami ezeket kiírja.
"""
prompt1 = """
Generálj egy egyszerű weboldalt react framworkkel, ami tartalmaz egy menüt, egy címsort és egy bekezdést.
"""

prompt2 = """
Generálj egy javascript adatbázist a képeknek.
"""

files = read_files_from_folder("generated_code").items()
if files:
    prompt += " Kiindulásnak használd az alábbi fáljlokat és add vissza az újakkal együtt:"
    for filename, content in files:
        prompt += f"\n-----------------------------------------------\nA {filename} tartalma:\n\n{content}\n"

# API kérés előkészítése
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "google/gemini-2.0-pro-exp-02-05:free",
    "messages": [{"role": "user", "content": prompt}],
    "tools": tools,  # Toolcalling megadása
    "tool_choice": {"type": "function", "function": {"name": "generate_code"}},  # Explicit eszköz kiválasztása
    "max_tokens": 8000  # Limitáljuk a választ
}

# API hívás
try:
    import logging
    logging.basicConfig(level=logging.INFO)

    logging.info("\n --Promptseparator-- \n".join([x["content"] for x in data["messages"]]))
    response = requests.post(API_URL, headers=headers, json=data, timeout=10)

    # Válasz feldolgozása
    if response.status_code == 200:
        result = response.json()

        if "choices" in result:
            message = result["choices"][0]["message"]

            # Tool calling válasz ellenőrzése
            if "tool_calls" in message:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])

                    if tool_name == "generate_code":
                        components = tool_args.get("components", [])
                        print(f"🛠️ Received {len(components)} components from AI.")

                        for component in components:
                            code = component.get("code")
                            filename = component.get("filename", "component")  # Alapértelmezett fájlnév, ha nincs megadva
                            file_extension = component.get("file_extension", ".txt")  # Alapértelmezett kiterjesztés, ha nincs megadva
                            full_filename = f"{filename}"
                            print(f"📄 Filename: {full_filename}")
                            print("🟢 Code:")
                            print(code)

                            # Kód mentése fájlba
                            os.makedirs("generated_code", exist_ok=True)
                            with open(f"generated_code/{full_filename}", "w", encoding="utf-8") as file:
                                file.write(code)
                                print(f"✅ Code saved to 'generated_code/{full_filename}'.")

            # Ha nincs tool calling, akkor a szöveges választ írjuk ki
            elif "content" in message:
                print("💬 Assistant response:", message["content"])

        else:
            print("❌ Hiba történt (válasz formátuma ismeretlen):", json.dumps(result, indent=2))

    else:
        print("❌ Hiba történt:", response.text)

except requests.Timeout:
    print("❌ Hiba történt: az API hívás túllépte az időkorlátot.")
except requests.RequestException as e:
    print(f"❌ Hiba történt: {e}")

print("👋 Program vége.")
