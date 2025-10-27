"""Script para verificar o ultimo processamento."""
import requests

try:
    response = requests.get("http://localhost:8000/health")
    data = response.json()
    print("Status do servidor:", data.get("status"))
    print("\nServicos:")
    for key, val in data.get("services", {}).items():
        print(f"  {key}: {val}")
except Exception as e:
    print(f"Erro: {e}")
