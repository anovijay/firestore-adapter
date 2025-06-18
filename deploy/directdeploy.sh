#!/bin/bash
set -e

# CONFIGURATION
PROJECT_ID="rhea-461313"
REGION="europe-west1"
SERVICE_NAME="firestore-adapter"
REPO_NAME="firestore-adapter"
IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

# 1. Authenticate Docker for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# 2. Build the Docker image
echo "🐳 Building Docker image..."
docker build --platform=linux/amd64 -t $IMAGE_TAG .

# 3. Push to Artifact Registry
echo "📦 Pushing image to Artifact Registry..."
docker push $IMAGE_TAG

# 4. Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_TAG \
  --region $REGION \
  --platform managed \
  --service-account rhea-app-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --quiet \
  --port 8080 \
  --set-env-vars PROJECT_ID=$PROJECT_ID

echo "✅ Deployment complete!"
