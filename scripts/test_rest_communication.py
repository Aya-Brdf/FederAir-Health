
import requests

ENVIRONMENT_URL = "http://127.0.0.1:8001"
HOSPITAL_URL = "http://127.0.0.1:8002"

ENVIRONMENT_KEY = "environment-local-key-2026"
HOSPITAL_KEY = "hospital-local-key-2026"


def check_node(name, url):
    try:
        response = requests.get(
            f"{url}/health",
            timeout=3
        )
        response.raise_for_status()

        print(f"[ONLINE] {name}")

    except requests.RequestException as error:
        print(f"[OFFLINE] {name}: {error}")


def retrieve_data(name, url, api_key):
    print(f"\n--- {name} ---")

    try:
        response = requests.get(
            f"{url}/api/v1/" +
            ("measurements" if name == "ENVIRONMENT" else "admissions"),
            headers={"X-API-Key": api_key},
            timeout=5
        )

        response.raise_for_status()
        result = response.json()

        print("Organization:", result["organization"])
        print("Records received:", result["total"])

        for record in result["data"]:
            print(record)

    except requests.RequestException as error:
        print("Communication error:", error)


def main():
    print("=" * 55)
    print("       FEDERAIR - FEDERATED COMMUNICATION")
    print("=" * 55)

    check_node("ENVIRONMENT NODE", ENVIRONMENT_URL)
    check_node("HOSPITAL NODE", HOSPITAL_URL)

    retrieve_data(
        "ENVIRONMENT",
        ENVIRONMENT_URL,
        ENVIRONMENT_KEY
    )

    retrieve_data(
        "HOSPITAL",
        HOSPITAL_URL,
        HOSPITAL_KEY
    )


if __name__ == "__main__":
    main()
