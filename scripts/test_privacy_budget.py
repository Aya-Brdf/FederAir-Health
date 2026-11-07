
import requests

from backend.common.config import (
    ENVIRONMENT_API_KEY,
    HOSPITAL_API_KEY
)

ENVIRONMENT_URL = "http://127.0.0.1:8001"
HOSPITAL_URL = "http://127.0.0.1:8002"

# Contrat de test : il doit être actif et autoriser la recherche.
CONTRACT_ID = "CONTRACT-858A55945FE1"


def main():
    print("\n=== TEST DU BUDGET DE CONFIDENTIALITE ===")

    # 1. Récupérer un paquet signé depuis Environment
    print("\n[1/3] Récupération des classifications...")

    response = requests.get(
        f"{ENVIRONMENT_URL}/api/v1/classifications",
        params={
            "contract_id": CONTRACT_ID,
            "consumer_id": "UNIVERSITY-LAB",
            "purpose": "research"
        },
        headers={"X-API-Key": ENVIRONMENT_API_KEY},
        timeout=5
    )

    response.raise_for_status()
    environment_data = response.json()

    print("[OK] Paquet signé reçu.")

    # 2. Envoyer une analyse avec epsilon = 1
    print("\n[2/3] Envoi de la demande d'agrégation...")

    payload = {
        "contract_id": environment_data["contract_id"],
        "consumer_id": environment_data["consumer_id"],
        "classifications": environment_data["classifications"],
        "timestamp": environment_data["timestamp"],
        "nonce": environment_data["nonce"],
        "signature": environment_data["signature"],
        "epsilon": 1.0
    }

    response = requests.post(
        f"{HOSPITAL_URL}/api/v1/aggregate",
        json=payload,
        headers={"X-API-Key": HOSPITAL_API_KEY},
        timeout=5
    )

    # 3. Vérifier le refus attendu
    print("\n[3/3] Vérification du résultat...")

    if response.status_code == 429:
        print("[PASS] Budget épuisé : requête refusée (HTTP 429).")
        print(response.json())

    elif response.status_code == 200:
        print("[ECHEC] La requête a été acceptée.")
        print("Le budget n'était pas encore épuisé.")

    else:
        print("[ERREUR] Réponse inattendue :")
        print("HTTP", response.status_code)
        print(response.text)


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as error:
        print("\n[ERREUR DE COMMUNICATION]")
        print(error)
