
import requests
import time
import uuid

from backend.common.config import (
    ENVIRONMENT_API_KEY,
    HOSPITAL_API_KEY
)

ENVIRONMENT_URL = "http://127.0.0.1:8001"
HOSPITAL_URL = "http://127.0.0.1:8002"



def get_environment_classifications():
    """Récupère le paquet de classifications signé par Environment."""

    response = requests.get(
        f"{ENVIRONMENT_URL}/api/v1/classifications",
        params={
            "contract_id": "CONTRACT-51AEF4B6A103",
            "consumer_id": "UNIVERSITY-LAB",
            "purpose": "research"
        },
        headers={"X-API-Key": ENVIRONMENT_API_KEY},
        timeout=5
    )

    response.raise_for_status()

    return response.json()



def send_classifications_to_hospital(environment_data):
    """
    Transmet à Hospital le paquet signé par Environment,
    sans modifier son contenu.
    """

    print("[OK] Paquet signé reçu depuis Environment.")
    print("[OK] Signature HMAC générée par Environment.")
    print("[OK] Le laboratoire ne modifie pas le paquet.")

    response = requests.post(
        f"{HOSPITAL_URL}/api/v1/aggregate",
        headers={"X-API-Key": HOSPITAL_API_KEY},
        json={
            "contract_id": environment_data["contract_id"],
            "consumer_id": environment_data["consumer_id"],
            "classifications": environment_data["classifications"],
            "timestamp": environment_data["timestamp"],
            "nonce": environment_data["nonce"],
            "signature": environment_data["signature"]
        },
        timeout=5
    )

    response.raise_for_status()

    return response.json()



def display_results(results):
    """Affiche les résultats agrégés."""

    print("\n" + "=" * 55)
    print("       FEDERAIR - FEDERATED ANALYSIS")
    print("=" * 55)

    print("\nOrganisation :", results["organization"])
    print("Règle :", results["privacy_rule"])

    print("\n--- RÉSULTATS DE L'ANALYSE ---")

    for category, values in results["results"].items():
        print(f"\nCatégorie : {category}")
        print("Statut :", values["status"])
        print("Nombre de jours :", values["days"])

        if "average_admissions" in values:
            print(
                "Moyenne des admissions :",
                values["average_admissions"]
            )

    print("\n" + "=" * 55)
    print("       ANALYSE TERMINÉE")
    print("=" * 55)


def main():
    try:
        print("[1/3] Connexion à l'Environment Node...")

        environment_data = get_environment_classifications()
        print(
            "[OK] Classifications reçues :",
            environment_data["total"]
        )

        print("[2/3] Transmission sécurisée à l'Hospital Node...")

        results = send_classifications_to_hospital(
            environment_data
        )

        print("[OK] Signature vérifiée et agrégation autorisée.")

        print("[3/3] Affichage des résultats...")

        display_results(results)

    except requests.HTTPError as error:
        print("\n[ERREUR HTTP] La requête a été refusée.")
        print(error.response.status_code)
        print(error.response.text)

    except requests.RequestException as error:
        print("\n[ERREUR] Communication avec une API impossible.")
        print(error)


if __name__ == "__main__":
    main()
