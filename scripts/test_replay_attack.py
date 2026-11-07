
import requests

from backend.common.config import (
    ENVIRONMENT_API_KEY,
    HOSPITAL_API_KEY
)

ENVIRONMENT_URL = "http://127.0.0.1:8001"
HOSPITAL_URL = "http://127.0.0.1:8002"

CONTRACT_ID = "CONTRACT-39977320EAE4"
CONSUMER_ID = "UNIVERSITY-LAB"


def main():

    print("=" * 55)
    print("       FEDERAIR - REPLAY ATTACK TEST")
    print("=" * 55)

    # 1. Récupérer un paquet signé depuis Environment
    print("\n[1] Récupération du paquet signé...")

    response = requests.get(
        f"{ENVIRONMENT_URL}/api/v1/classifications",
        params={
            "contract_id": CONTRACT_ID,
            "consumer_id": CONSUMER_ID,
            "purpose": "research"
        },
        headers={"X-API-Key": ENVIRONMENT_API_KEY},
        timeout=10
    )

    response.raise_for_status()
    environment_data = response.json()

    print("[OK] Paquet signé reçu.")

    # 2. Préparer le paquet sans le modifier
    payload = {
        "contract_id": environment_data["contract_id"],
        "consumer_id": environment_data["consumer_id"],
        "classifications": environment_data["classifications"],
        "timestamp": environment_data["timestamp"],
        "nonce": environment_data["nonce"],
        "signature": environment_data["signature"],
        "epsilon": 1.0
    }

    headers = {"X-API-Key": HOSPITAL_API_KEY}

    # 3. Première transmission
    print("\n[2] Première transmission...")

    first_response = requests.post(
        f"{HOSPITAL_URL}/api/v1/aggregate",
        headers=headers,
        json=payload,
        timeout=10
    )

    print("HTTP Status:", first_response.status_code)
    print("Réponse:", first_response.text)

    # 4. Réutilisation exacte du même paquet
    print("\n[3] Deuxième transmission du même paquet...")

    second_response = requests.post(
        f"{HOSPITAL_URL}/api/v1/aggregate",
        headers=headers,
        json=payload,
        timeout=10
    )

    print("HTTP Status:", second_response.status_code)
    print("Réponse:", second_response.text)

    # 5. Vérifier les résultats
    if (
        first_response.status_code == 200
        and second_response.status_code == 409
    ):
        print("\n[PASS] Première requête acceptée.")
        print("[PASS] Deuxième requête rejetée.")
        print("[PASS] Attaque par rejeu détectée.")

    else:
        print("\n[FAIL] Résultat inattendu.")


if __name__ == "__main__":
    main()
