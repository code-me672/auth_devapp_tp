import requests

BASE_URL = "http://127.0.0.1:8000"

# =========================
# BRUTE FORCE TEST
# =========================

for i in range(7):

    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": "josias",
            "password": "SecurePass456!"
        }
    )

    print(f"Tentative {i+1}")
    print(response.status_code)
    print(response.text)
    print("=" * 50)