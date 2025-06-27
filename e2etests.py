import os
import requests
import random
import string
from google.cloud import secretmanager
from google.api_core import exceptions

# --- Configuration ---
# IMPORTANT: Your local environment must be authenticated.
# Run `gcloud auth application-default login` if you have issues.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "rhea-461313")

def get_secret(secret_name: str, project_id: str) -> str | None:
    """
    Retrieves the latest version of a secret from Google Cloud Secret Manager.
    Returns the secret string or None if an error occurs (e.g., permission denied).
    """
    try:
        print(f"Attempting to fetch secret: {secret_name}...")
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=secret_path)
        payload = response.payload.data.decode("UTF-8")
        print(f"✅ Successfully fetched secret: {secret_name}")
        return payload
    except exceptions.PermissionDenied:
        print(f"❌ PERMISSION DENIED: Could not access secret '{secret_name}'.")
        print("   Please ensure your account has the 'Secret Manager Secret Accessor' role.")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while fetching secret '{secret_name}': {e}")
        return None

def generate_random_id(length=8):
    """Generates a random string for unique document IDs."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def main():
    """
    Runs the end-to-end test against the deployed service.
    """
    print("--- Step 1: Fetching Configuration from Secret Manager ---")
    
    try:
        base_url = get_secret("fs-adapter-url", GCP_PROJECT_ID)
        api_keys_str = get_secret("fs-adapter-api-key", GCP_PROJECT_ID)

        # Exit gracefully if secrets could not be fetched
        if not base_url or not api_keys_str:
            print("\n❌ Critical configuration missing. Halting E2E test.")
            return

        api_key = api_keys_str.split(',')[0].strip()

        print("\n--- Configuration Summary ---")
        print(f"Base URL: {base_url}")
        print(f"API Key:  {api_key}")
        
        # --- Start of Lifecycle Test ---
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        collection = "e2e-live-test"
        doc_id = f"test-{generate_random_id()}"
        
        print(f"\nUsing Collection: {collection}")
        print(f"Using Document ID: {doc_id}")
        
        # Step 2: Create a new document
        print("\n--- Step 2: Creating Document ---")
        create_data = {"name": "Live E2E Test", "status": "initial"}
        create_url = f"{base_url}/documents/{collection}"
        response = requests.post(create_url, headers=headers, json=create_data, params={"doc_id": doc_id})
        response.raise_for_status()
        print(f"✅ Document created (Status: {response.status_code})")

        # Step 3: Retrieve the document to verify creation
        print("\n--- Step 3: Verifying Document Creation ---")
        get_url = f"{base_url}/documents/{collection}/{doc_id}"
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        retrieved_data = response.json()['data']
        assert retrieved_data['name'] == create_data['name'], "Verification failed: Name does not match"
        print("✅ Document retrieved and its content is correct.")

        # Step 4: Update the document
        print("\n--- Step 4: Updating Document ---")
        update_data = {"status": "updated"}
        response = requests.put(get_url, headers=headers, json=update_data)
        response.raise_for_status()
        print(f"✅ Document updated (Status: {response.status_code})")
        
        # Step 5: Verify the update
        print("\n--- Step 5: Verifying Document Update ---")
        response = requests.get(get_url, headers=headers)
        response.raise_for_status()
        retrieved_data = response.json()['data']
        assert retrieved_data['status'] == "updated", "Verification failed: Status was not updated"
        print("✅ Document retrieved and update is confirmed.")

        # Step 6: Delete the document
        print("\n--- Step 6: Deleting Document ---")
        response = requests.delete(get_url, headers=headers)
        response.raise_for_status()
        print(f"✅ Document deleted (Status: {response.status_code})")

        # Step 7: Verify deletion (should fail with 404)
        print("\n--- Step 7: Verifying Deletion ---")
        response = requests.get(get_url, headers=headers)
        assert response.status_code == 404, f"Verification failed: Expected 404 but got {response.status_code}"
        print("✅ Document confirmed deleted (received 404 Not Found).")
        
        print("\n🎉 End-to-end test completed successfully! 🎉")

    except requests.exceptions.HTTPError as err:
        print(f"\n❌ HTTP ERROR: {err.response.status_code} - {err.response.text}")
    except Exception as e:
        print(f"\n❌ E2E test failed: {e}")


if __name__ == "__main__":
    main() 