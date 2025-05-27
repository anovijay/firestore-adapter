#!/bin/bash

set -e

# User Configuration
PROJECT_ID="rhea-459720"
SERVICE_ACCOUNT_NAME="rhea-sa"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# 1. Create the service account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name "Service Account for Rhea Cloud Run deployment"

# 2. Grant Cloud Run Admin role (can deploy Cloud Run services)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.admin"

# 3. Grant Cloud Build Editor role (can build and push images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

# 4. Grant Service Account User role (allows using service account with Cloud Run)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# 5. Grant Storage Admin role (needed for pushing to Artifact Registry/Container Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.admin"

# 6. (Optional) Create and download a key file for CI/CD
echo "Do you want to create a service account key (for use in CI/CD)? (y/n)"
read create_key
if [[ "$create_key" == "y" ]]; then
    gcloud iam service-accounts keys create ./rhea-sa-key.json \
        --iam-account=$SERVICE_ACCOUNT_EMAIL
    echo "Service account key saved to ./rhea-sa-key.json"
else
    echo "Skipping key creation."
fi

echo "Service account $SERVICE_ACCOUNT_EMAIL is ready and granted required roles."
