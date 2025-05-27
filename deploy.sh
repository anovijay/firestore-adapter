#!/bin/bash

set -e

# ---- USER CONFIG ----
PROJECT_ID="rhea-459720"
REGION="us-central1"
SERVICE_NAME="firestore-adapter"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"
PORT=8080
SERVICE_ACCOUNT_EMAIL="mailservice-sa@rhea-459720.iam.gserviceaccount.com"
SA_KEY_PATH="rhea-459720-a00877ca58da.json"  # <-- Replace with the real path!
# ---------------------

# 1. Authenticate with the service account
echo "Authenticating with service account..."
export GOOGLE_APPLICATION_CREDENTIALS="$SA_KEY_PATH"
gcloud auth activate-service-account $SERVICE_ACCOUNT_EMAIL --key-file=$GOOGLE_APPLICATION_CREDENTIALS

# 2. Set the project and region
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 3. Build and push the Docker image
gcloud builds submit --tag $IMAGE

# 4. Deploy to Cloud Run (using the same service account for the service)
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --service-account $SERVICE_ACCOUNT_EMAIL \
  --allow-unauthenticated \
  --port $PORT

echo "✅ Deployment complete!"
