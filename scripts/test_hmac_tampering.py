
import requests

from backend.common.config import (
    ENVIRONMENT_API_KEY,
    HOSPITAL_API_KEY
)

ENVIRONMENT_URL = "http://127.0.0.1:8001"
HOSPITAL_URL = "http://127.0.0.1:8002"

CONTRACT_ID = "CONTRACT-858A55945FE1"
CONSUMER_ID = "UNIVERSITY-LAB"


def main():

    print("=" * 55)
    print("       FEDERAIR - HMAC TAMPERING TEST")
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

    # 2. Préparer le paquet destiné à Hospital
    payload = {
        "contract_id": environment_data["contract_id"],
        "consumer_id": environment_data["consumer_id"],
        "classifications": environment_data["classifications"],
        "timestamp": environment_data["timestamp"],
        "nonce": environment_data["nonce"],
        "signature": environment_data["signature"],
        "epsilon": 1.0
    }

    # 3. Modifier une classification après signature
    print("\n[2] Modification frauduleuse...")

    original = payload["classifications"][0]["category"]

    payload["classifications"][0]["category"] = (
        "LOW" if original == "HIGH" else "HIGH"
    )

    print("Catégorie originale :", original)
    print("Catégorie modifiée :", payload["classifications"][0]["category"])

    # 4. Envoyer le paquet falsifié à Hospital
    print("\n[3] Transmission du paquet falsifié...")

    hospital_response = requests.post(
        f"{HOSPITAL_URL}/api/v1/aggregate",
        headers={"X-API-Key": HOSPITAL_API_KEY},
        json=payload,
        timeout=10
    )

    print("\n--- RÉSULTAT DU TEST ---")
    print("HTTP Status:", hospital_response.status_code)
    print("Réponse:", hospital_response.text)

    # 5. Vérifier le rejet
    if (
        hospital_response.status_code == 403
        and "Invalid HMAC signature" in hospital_response.text
    ):
        print("\n[PASS] Modification détectée.")
        print("[PASS] Signature HMAC invalide.")
        print("[PASS] Paquet falsifié rejeté.")

    else:
        print("\n[FAIL] Résultat inattendu.")


if __name__ == "__main__":
    main()
