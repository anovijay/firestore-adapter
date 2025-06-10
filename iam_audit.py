import subprocess
import json
from datetime import datetime

PROJECT_ID = "rhea-461313"  # <-- Replace with your actual GCP Project ID
LOG_FILE = f"iam_audit_log_{PROJECT_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

log_data = {
    "project_id": "rhea-461313",
    "timestamp": datetime.utcnow().isoformat(),
    "iam_policy": {},
    "service_accounts": [],
    "external_access": [],
    "custom_roles": [],
    "recommendations": []
}

def run_command(command, expect_json=True):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if expect_json:
            return json.loads(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr.strip()}
    except json.JSONDecodeError:
        return {"error": "Output was not valid JSON", "raw_output": result.stdout.strip()}

print("[*] Starting IAM Audit...")

# 1. IAM Policy
print("-> Fetching IAM Policy")
log_data["iam_policy"] = run_command(
    f"gcloud projects get-iam-policy {PROJECT_ID} --format=json"
)

# 2. Service Accounts
print("-> Listing Service Accounts")
log_data["service_accounts"] = run_command(
    f"gcloud iam service-accounts list --project={PROJECT_ID} --format=json"
)

# 3. External Access
print("-> Checking for External/Public Access")
log_data["external_access"] = run_command(
    f"gcloud projects get-iam-policy {PROJECT_ID} "
    f'--flatten="bindings[].members" '
    f'--filter="bindings.members:allUsers OR bindings.members:allAuthenticatedUsers" '
    f'--format=json'
)

# 4. Custom Roles
print("-> Listing Custom Roles")
log_data["custom_roles"] = run_command(
    f"gcloud iam roles list --project={PROJECT_ID} --format=json"
)

# 5. IAM Policy Recommender (if available)
print("-> Fetching IAM Policy Recommendations")
log_data["recommendations"] = run_command(
    f"gcloud recommender recommendations list "
    f"--project={PROJECT_ID} --location=global "
    f"--recommender=google.iam.policy.Recommender --format=json"
)

# Write to file
with open(LOG_FILE, "w") as f:
    json.dump(log_data, f, indent=2)

print(f"✅ IAM Audit completed.\n📄 Log saved to: {LOG_FILE}")
